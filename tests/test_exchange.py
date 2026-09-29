import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from jsonschema import ValidationError
from tools.validate_exchange import ROOT, validate


class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.request_bytes = (ROOT/'context/examples/inf-request-0.1.0.json').read_bytes()
        self.request = json.loads(self.request_bytes)
        self.report = json.loads((ROOT/'context/examples/raw-report-0.1.0.json').read_bytes())

    def test_fixtures(self):
        validate(self.request)
        validate(self.report, self.request_bytes)

    def test_unknown_version_and_inf_write_field_rejected(self):
        for field, value in [('schema_version', '9.0.0'), ('inf_write_path', 'INF/anything')]:
            candidate = copy.deepcopy(self.report)
            candidate[field] = value
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validate(candidate, self.request_bytes)

    def test_reference_and_request_hash_mismatch_rejected(self):
        changed = copy.deepcopy(self.report)
        changed['items'][0]['inf_ref']['entity_id'] = 'wrong-id'
        with self.assertRaisesRegex(ValueError, 'INF reference'):
            validate(changed, self.request_bytes)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            validate(self.report, self.request_bytes + b' ')

    def test_duplicate_and_incomplete_final_report_rejected(self):
        changed = copy.deepcopy(self.report)
        changed['items'].append(copy.deepcopy(changed['items'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate(changed, self.request_bytes)
        req = copy.deepcopy(self.request)
        another = copy.deepcopy(req['items'][0]);another['request_item_id'] = 'second'
        req['items'].append(another)
        raw = json.dumps(req).encode()
        self.report['request_sha256'] = hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError, 'exactly all'):
            validate(self.report, raw)
        self.report['final'] = False
        validate(self.report, raw)

    def test_found_requires_snapshot_and_error_is_not_missing(self):
        item = self.report['items'][0]
        item['status'] = 'found'
        with self.assertRaisesRegex(ValueError, 'selected'):
            validate(self.report, self.request_bytes)
        item['status'] = 'not_found'
        with self.assertRaisesRegex(ValueError, 'searches'):
            validate(self.report, self.request_bytes)

    def test_snapshot_integrity_and_separate_identifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = json.dumps({'query': {'pages': [{'pageid': 11, 'revisions': [{'revid': 22,
                'timestamp': '2026-09-01T00:00:00Z', 'slots': {'main': {'content': 'Original fixture'}}}]}]}}).encode()
            path = root/'sources/viwiki/11/22/response.json'
            path.parent.mkdir(parents=True);path.write_bytes(raw)
            item = self.report['items'][0]
            item['status'] = 'found';item['selected_candidate_id'] = 'candidate-1'
            item['candidates'] = [{'candidate_id': 'candidate-1', 'page': {'wiki_id': 'viwiki', 'page_id': '11', 'title': 'Fixture', 'source_url': 'https://vi.wikipedia.org/wiki/Fixture'},
                'revision': {'revision_id': '22', 'revision_timestamp': '2026-09-01T00:00:00Z', 'revision_url': 'https://vi.wikipedia.org/w/index.php?oldid=22'},
                'artifacts': [{'path': 'sources/viwiki/11/22/response.json', 'sha256': hashlib.sha256(raw).hexdigest(), 'media_type': 'application/json', 'byte_length': len(raw),
                    'retrieved_at': '2026-09-29T00:00:00Z', 'request_url': 'https://vi.wikipedia.org/w/api.php?action=query&revids=22',
                    'representation': 'mediawiki-api-response-bytes', 'license': None}], 'evidence': ['Synthetic unit test only'], 'conflicts': []}]
            validate(self.report, self.request_bytes, root, True)
            original = path.read_bytes();path.write_bytes(original.replace(b'Original', b'Modified'))
            with self.assertRaisesRegex(ValueError, 'checksum'):
                validate(self.report, self.request_bytes, root, True)
            artifact = item['candidates'][0]['artifacts'][0]
            artifact['path'] = 'sources/../INF/record.json'
            with self.assertRaisesRegex(ValueError, 'artifact path'):
                validate(self.report, self.request_bytes)
            artifact['path'] = 'sources/viwiki/11/22/response.json'
            path.write_bytes(original)
            item['candidates'][0]['revision']['revision_id'] = '33'
            with self.assertRaisesRegex(ValueError, 'revision URL'):
                validate(self.report, self.request_bytes, root, True)
