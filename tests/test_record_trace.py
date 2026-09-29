import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools.record_trace import record


class TraceTests(unittest.TestCase):
    def test_evidence_is_preserved_and_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / 'audit.json'
            evidence.write_text('{"status": "observed"}\n')
            out = record(root, 'pilot-001', 'audit', evidence)
            saved = out.read_bytes()
            data = json.loads(saved)
            self.assertEqual(data['evidence_sha256'], hashlib.sha256(evidence.read_bytes()).hexdigest())
            self.assertEqual(data['evidence_raw'], evidence.read_text())
            with self.assertRaises(FileExistsError):
                record(root, 'pilot-001', 'audit', evidence)
            self.assertEqual(out.read_bytes(), saved)

    def test_rejects_escape_and_invalid_input_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / 'bad.json'
            evidence.write_text('not json')
            with self.assertRaises(ValueError):
                record(root, '../escape', 'audit', evidence)
            with self.assertRaises(ValueError):
                record(root, 'valid', 'audit', evidence)
            self.assertFalse((root/'raw/valid.json').exists())
