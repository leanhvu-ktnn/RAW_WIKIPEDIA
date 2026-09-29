import io
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from tools.crawl_province_2025 import Client, APIError, prepare, retry_after, evidence, disambiguation, sha

class Response(io.BytesIO):
    status=200
    headers={'Content-Type':'application/json'}

class CrawlTests(unittest.TestCase):
    def test_input_preserves_observations_and_epochs(self):
        source=Path(__file__).resolve().parents[1]/'packages/province-before-after-2025/input/province-before-after-2025.json'
        with tempfile.TemporaryDirectory() as tmp:
            stage=prepare(source,Path(tmp));targets=stage['targets']
            self.assertEqual(len(targets),97)
            self.assertEqual(len({x['target_id'] for x in targets}),97)
            hn=[t for t in targets if t['search_name']=='Hà Nội']
            self.assertEqual(len(hn),2)
            self.assertEqual(hn[0]['input_observation_id'],hn[1]['input_observation_id'])
            self.assertNotEqual(hn[0]['target_id'],hn[1]['target_id'])
            self.assertEqual(stage['source']['declared_version'],None)
    def test_network_error_not_missing(self):
        def fail(*a,**k):raise URLError('fixture network outage')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(APIError):Client(Path(tmp),fail,lambda n:None,2).get({'action':'query'})
    def test_maxlag_and_cache_preserve_original_bytes(self):
        bodies=[b'{"error":{"code":"maxlag"}}',b'{ "query" : {"pages":[]} }']
        def opener(*a,**k):return Response(bodies.pop(0))
        with tempfile.TemporaryDirectory() as tmp:
            client=Client(Path(tmp),opener,lambda n:None)
            data,meta=client.get({'action':'query'})
            self.assertEqual((Path(tmp)/meta['path']).read_bytes(),b'{ "query" : {"pages":[]} }')
            self.assertEqual(client.get({'action':'query'}),(data,meta))
            self.assertEqual(bodies,[])
    def test_429_retry_after_and_403_no_retry(self):
        for code in (429,403):
            calls=[];sleeps=[]
            def opener(*a,**k):
                calls.append(1)
                if len(calls)==1:raise HTTPError('https://vi.wikipedia.org',code,'fixture',{'Retry-After':'7'},io.BytesIO())
                return Response(b'{"query":{"pages":[]}}')
            with tempfile.TemporaryDirectory() as tmp:
                c=Client(Path(tmp),opener,sleeps.append,2)
                if code==403:
                    with self.assertRaises(APIError):c.get({'action':'query'})
                    self.assertEqual(len(calls),1)
                else:
                    c.get({'action':'query'});self.assertIn(7.0,sleeps)
    def test_http_date(self):
        self.assertEqual(retry_after('Tue, 29 Sep 2026 00:00:07 GMT',datetime(2026,9,29,tzinfo=timezone.utc)),7)
    def test_evidence_exact_lines_and_no_date_inference(self):
        content="'''Gia Lai''' là một tỉnh ở Việt Nam.\n== Lịch sử ==\nNgày 12 tháng 6 năm 2025, hợp nhất theo Nghị quyết 202/2025/QH15."
        snippets=evidence(content,'Gia Lai')
        for snippet in snippets:self.assertEqual(snippet['excerpt_wikitext'],content.splitlines()[snippet['line_start']-1])
        self.assertTrue(any('cited_resolution_202' in x['categories'] for x in snippets))
        self.assertTrue(disambiguation({'title':'Bình Định','pageprops':{'disambiguation':''}}))
