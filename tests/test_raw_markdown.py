import unittest,tempfile,json
from pathlib import Path
from tools.raw_markdown import convert,write_source,materialize,validate,sha,journal_view
class MarkdownTests(unittest.TestCase):
 def test_html_structure_relative_links_script_removal_and_footer(self):
  body=b'<h1>Title</h1><p>Hello <b>bold</b><a href="/law">Law</a></p><ul><li>One</li></ul><table><tr><th>A</th><th>B</th></tr><tr><td>01</td><td>02</td></tr></table><script>alert(1)</script><footer>Operator X</footer>'
  text,m=convert(body,'html','https://example.gov.vn/path')
  for part in ['# Title','**bold**','https://example.gov.vn/law','One','| A','01','Operator X']:self.assertIn(part,text)
  self.assertNotIn('alert(1)',text)
 def test_mediawiki_template_and_references_preserved(self):
  body="{{Infobox|code=001}}\n'''Tên''' là [[phường]].<ref>{{Chú thích web|url=https://example.gov.vn/law|title=Tên}}</ref>\n== Lịch sử ==\nNgày 1.".encode()
  text,m=convert(body,'mediawiki','https://vi.wikipedia.org/wiki/Tên')
  for part in ['code=001','Lịch sử','https://vi.wikipedia.org/wiki/','[^raw-ref-1]','https://example.gov.vn/law']:self.assertIn(part,text)
 def test_derivative_hash_and_original_unchanged(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'packages/p';p.mkdir(parents=True);body=b'<h1>A</h1>';s=p/'source.html';s.write_bytes(body)
   r={'item_id':'inf:one','label':'A','status':'ambiguous','reason':'pending','official_sources':[{'response':{'raw_path':'source.html','sha256':sha(body),'requested_url':'https://example.gov.vn','retrieved_at':'2026-09-30T00:00:00Z'}}]}
   materialize(p,[r]);validate(p,[r]);self.assertEqual(s.read_bytes(),body)
   m=r['official_sources'][0]['response'];f=p/m['markdown_path'];f.write_text(f.read_text()+'tampered')
   with self.assertRaisesRegex(ValueError,'Markdown checksum'):validate(p,[r])
 def test_sealed_and_escape_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'checksums.json').write_text('{}')
   with self.assertRaisesRegex(ValueError,'sealed'):write_source(p,'source.html',{},'html')
   (p/'checksums.json').unlink()
   with self.assertRaisesRegex(ValueError,'escapes'):write_source(p,'../outside',{},'html')
 def test_journal_md_does_not_change_contract(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'000000.json';b=json.dumps({'state':'acknowledged','created_at':'2026-09-30'}).encode();p.write_bytes(b);m=journal_view(p);self.assertEqual(p.read_bytes(),b);self.assertIn('okf_version: "0.2"',m.read_text());self.assertEqual(journal_view(p),m)
 def test_complex_table_keeps_cell_text(self):
  text,_=convert(b'<table><tr><th colspan="2">Combined</th></tr><tr><td>A</td><td>B</td></tr></table>','html')
  for x in ['Combined','A','B']:self.assertIn(x,text)
 def test_svg_dropped_before_pandoc_and_text_kept(self):
  body=b'<h1>Bo</h1><p>Noi dung</p><svg><path d="M0 0 L9 9"/></svg><script>alert(1)</script>'
  text,m=convert(body,'html','https://example.gov.vn/')
  self.assertIn('Noi dung',text)
  self.assertNotIn('M0 0',text)
  self.assertNotIn('alert(1)',text)
  self.assertNotIn('pandoc_reader_timeout', ' '.join(m['warnings']))
