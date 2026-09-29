from pathlib import Path
import shutil
import tempfile
import unittest
from tools.validate_project import ROOT, validate


class ProjectValidationTests(unittest.TestCase):
    def test_broken_reference_and_corrupt_trace_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ('context', 'skills', 'wiki', 'raw', 'reports'):
                shutil.copytree(ROOT / folder, root / folder)
            for filename in ('SKILLS.md', 'README.md'):
                shutil.copyfile(ROOT / filename, root / filename)
            # Package links are part of the knowledge graph; copy small report anchors.
            for source in (ROOT/'packages').rglob('report.md'):
                dest=root/source.relative_to(ROOT)
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,dest)
            self.assertEqual(validate(root), [])
            with (root/'context/index.md').open('a') as stream:
                stream.write('\n[[context/not-present|Broken]]\n')
            trace = root/'raw/bootstrap-2026-09-29/trace.json'
            trace.write_text('{}')
            errors = validate(root)
            self.assertTrue(any('broken wiki link' in e for e in errors))
            self.assertTrue(any('invalid trace' in e for e in errors))
