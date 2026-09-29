import json
from pathlib import Path
import tempfile
import unittest
from tools.crawl_province_2025 import read_json,put_json,sha,short
from tools.province_package import validate
from tools.review_province_2025 import propose

ROOT=Path(__file__).resolve().parents[1]

class PackageTests(unittest.TestCase):
    def fixture(self,root):
        original=ROOT/'packages/province-before-after-2025'
        stage=read_json(original/'staging.json');raw=(original/stage['source']['file']).read_bytes()
        (root/'input').mkdir();(root/stage['source']['file']).write_bytes(raw);put_json(root/'staging.json',stage)
        content="Synthetic test only: province text."
        body=json.dumps({'query':{'pages':[{'pageid':1,'revisions':[{'revid':2,'timestamp':'2025-01-01T00:00:00Z','slots':{'main':{'content':content}}}]}]}}).encode()
        (root/'response.json').write_bytes(body);(root/'text.wikitext').write_text(content)
        s={'page_id':'1','revision_id':'2','revision_timestamp':'2025-01-01T00:00:00Z','response':{'path':'response.json','sha256':sha(body),'byte_length':len(body)},'wikitext_path':'text.wikitext','wikitext_sha256':sha(content.encode()),'license':'CC-BY-SA-4.0','contributors_url':'https://vi.wikipedia.org/w/index.php?action=history'}
        results={};reviews={}
        for t in stage['targets']:
            tid=t['target_id'];results[tid]={'input_observation_id':t['input_observation_id'],'status':'ambiguous','sources':[s]}
            reviews[tid]={'status':'found','reason':'Synthetic integrity test, not a semantic assessment','accepted_evidence':[{'source_key':'1/2','line_start':1,'line_end':1,'claim_scope':'name_type','excerpt_wikitext':content}]}
        put_json(root/'checkpoint.json',{'input_sha256':stage['source']['sha256'],'results':results});put_json(root/'reviews.json',reviews)
        return stage,results,reviews

    def test_shared_page_does_not_collapse_97_targets_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            v=validate(root);self.assertEqual(v['targets'],97);self.assertEqual(v['unique_retrieved_pages'],1)
            (root/'text.wikitext').write_text('Tampered text')
            with self.assertRaisesRegex(ValueError,'evidence mismatch|faithful'):validate(root)

    def test_reference_and_evidence_must_match_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);stage,results,reviews=self.fixture(root)
            first=stage['targets'][0]['target_id'];reviews[first]['accepted_evidence'][0]['excerpt_wikitext']='Fabricated excerpt'
            put_json(root/'reviews.json',reviews)
            with self.assertRaisesRegex(ValueError,'evidence mismatch'):validate(root)

    def test_country_mismatch_cannot_become_found_and_city_name_preserved(self):
        self.assertEqual(short('Thành phố Hồ Chí Minh'),'Thành phố Hồ Chí Minh')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'text.wikitext').write_text("'''Hà Nam''' là một tỉnh của Trung Quốc.")
            target={'label':'tỉnh Hà Nam','search_name':'Hà Nam','phase':'before','input_events':[]}
            result={'status':'ambiguous','sources':[{'page_id':'1','revision_id':'2','selection_cutoff':'2025-06-11T23:59:59Z','wikitext_path':'text.wikitext','resolved_title':'Hà Nam'}]}
            self.assertEqual(propose(root,target,result,[],{})['status'],'ambiguous')
