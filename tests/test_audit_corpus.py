import json
from pathlib import Path
import tempfile
import unittest
from tools.audit_corpus import audit, local_path, metadata


class AuditTests(unittest.TestCase):
    def test_preserves_leading_zero_and_unicode(self):
        self.assertEqual(metadata('---\nma_dvhc: "00123"\nwiki_title: "Hải Vân"\n---'),
                         {'ma_dvhc': '00123', 'wiki_title': 'Hải Vân'})

    def test_rejects_unsupported_and_duplicate_fields(self):
        for text in ('---\na: x\na: y\n---', '---\na: |\n text\n---', '---\na: x'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                metadata(text)

    def test_paths_are_confined(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(local_path(root, 'RAW/WIKIPEDIA/DiaBan/a/index.md'), (root / 'DiaBan/a/index.md').resolve())
            for value in ('../outside', '/outside', None, ''):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    local_path(root, value)

    def test_detects_stale_manifest_duplicates_and_bad_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fields = dict(type='wiki_page', wiki_title='Test', wiki_pageid='123', oldid='456',
                          source_url='https://vi.wikipedia.org/wiki/Test', license='CC-BY-SA-4.0',
                          extracted_at='2026-09-29T00:00:00Z', wiki_kind='CoQuan', extract_mode='lead')
            for slug in ('a', 'b'):
                path = root / 'CoQuan' / slug / 'index.md'
                path.parent.mkdir(parents=True)
                path.write_text('---\n' + '\n'.join(k + ': ' + json.dumps(v) for k, v in fields.items()) + '\n---\nBody')
            row = {'status': 'hit', 'wave': 'D', 'path': 'RAW/WIKIPEDIA/CoQuan/missing/index.md'}
            (root / '_catalog.jsonl').write_text(json.dumps(row) + '\n')
            (root / '_manifest_D.json').write_text(json.dumps([row]))
            report = audit(root)
            self.assertEqual(report['pages'], 2)
            self.assertEqual(report['finding_counts']['duplicate_pageid'], 1)
            self.assertEqual(report['finding_counts']['manifest_missing_page'], 1)
            self.assertEqual(report['finding_counts']['catalog_hit_missing_file'], 1)
            self.assertEqual(report['finding_counts']['pages_without_manifest'], 2)
            self.assertNotIn('invalid_id', report['finding_counts'])
            fields['wiki_pageid'] = '-1'
            path.write_text('---\n' + '\n'.join(k + ': ' + json.dumps(v) for k, v in fields.items()) + '\n---\nBody')
            self.assertEqual(audit(root)['finding_counts']['invalid_id'], 1)


if __name__ == '__main__':
    unittest.main()
