#!/usr/bin/env python3
"""OKF 0.2 reading derivatives. Originals stay immutable; conversion never asserts truth."""
from pathlib import Path
import hashlib,json,re,subprocess,shutil,os,html,unicodedata
from urllib.parse import urljoin,urlsplit,quote
from html.parser import HTMLParser
from datetime import datetime,timezone
from functools import lru_cache
VERSION='raw-markdown/0.1.2'
# Trần thời gian pandoc. 60 giây không đủ cho HTML cổng bộ có nhiều SVG; không để treo vô hạn.
PANDOC_TIMEOUT_SECONDS=120
SKIP_TAGS=('script','style','noscript','svg','iframe','canvas','object','embed')
def sha(b):return hashlib.sha256(b).hexdigest()
def scalar(x):return json.dumps(x,ensure_ascii=False)
def frontmatter(fields):return '---\n'+'\n'.join(k+': '+scalar(v) for k,v in fields.items())+'\n---\n\n'
def now():return datetime.now(timezone.utc).isoformat()
def confined(root,name):
 p=(root/name).resolve()
 if not p.is_relative_to(root.resolve()):raise ValueError('Markdown path escapes package')
 return p
def put(path,b,mutable=False):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists() and path.read_bytes()==b:return
 if path.exists() and not mutable:raise ValueError('Immutable Markdown artifact conflict')
 temp=path.with_name(path.name+'.tmp');temp.write_bytes(b);os.replace(temp,path)
def pandoc_path():
 for name in [shutil.which('pandoc'),'/opt/homebrew/bin/pandoc','/usr/local/bin/pandoc']:
  if name and Path(name).is_file():return name
 raise RuntimeError('Pandoc missing: Markdown gate cannot pass')
class SafeHTML(HTMLParser):
 """Preserve document text/structure; remove executable content and absolutize links."""
 def __init__(self,base):super().__init__(convert_charrefs=False);self.base=base;self.parts=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in SKIP_TAGS:self.skip+=1;return
  if self.skip:return
  if tag=='base':
   self.base=urljoin(self.base,dict(attrs).get('href',''));return
  clean=[]
  for k,v in attrs:
   if k.lower().startswith('on'):continue
   if k in ('href','src') and v:
    v=urljoin(self.base,v)
    if urlsplit(v).scheme not in ('http','https','mailto','tel'):continue
   clean.append(k if v is None else k+'="'+html.escape(v,quote=True)+'"')
  self.parts.append('<'+tag+(' '+' '.join(clean) if clean else '')+'>')
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_endtag(self,tag):
  if tag in SKIP_TAGS:self.skip=max(0,self.skip-1);return
  if not self.skip:self.parts.append('</'+tag+'>')
 def handle_data(self,data):
  if not self.skip:self.parts.append(data)
 def handle_entityref(self,name):
  if not self.skip:self.parts.append('&'+name+';')
 def handle_charref(self,name):
  if not self.skip:self.parts.append('&#'+name+';')

def html_text_fallback(cleaned_html):
 """Khi pandoc quá giờ: giữ chữ đã đọc, khai báo fallback, không chặn cả request."""
 class TextOnly(HTMLParser):
  def __init__(self):super().__init__();self.parts=[];self.skip=0
  def handle_starttag(self,tag,attrs):
   if tag in SKIP_TAGS:self.skip+=1
   elif not self.skip and tag in ('p','div','h1','h2','h3','li','br','tr'):self.parts.append('\n')
  def handle_endtag(self,tag):
   if tag in SKIP_TAGS and self.skip:self.skip-=1
   elif tag in ('p','h1','h2','h3','li','tr'):self.parts.append('\n')
  def handle_data(self,data):
   if not self.skip:self.parts.append(data)
 parser=TextOnly();parser.feed(cleaned_html)
 lines=[x.strip() for x in ''.join(parser.parts).splitlines() if x.strip()]
 return '\n\n'.join(lines)+('\n' if lines else '')
def pandoc_convert(engine,args,data):
 try:return subprocess.run([engine,*args],input=data,capture_output=True,timeout=PANDOC_TIMEOUT_SECONDS)
 except subprocess.TimeoutExpired:return None
def mediawiki_verbatim(body,charset,warnings,reason):
 original=body.decode(charset);fence='`'*max(3,max((len(m.group()) for m in re.finditer(r'`+',original)),default=0)+1)
 return '## Nội dung nguồn giữ nguyên do cú pháp chưa hỗ trợ\n\n'+fence+'mediawiki\n'+original+'\n'+fence+'\n',{'warnings':warnings+[reason],'engine':'Pandoc reader failed; lossless fenced source'}

@lru_cache(maxsize=128)
def convert(body,kind,source_url='',charset='utf-8'):
 warnings=[]
 try:text=body.decode(charset)
 except (UnicodeDecodeError,LookupError):text=body.decode('utf-8',errors='replace');warnings.append('decode_replacement_used')
 if kind in ('text','markdown'):return text,{'warnings':warnings,'engine':'UTF-8 text derivative'}
 if kind=='json':return '```json\n'+json.dumps(json.loads(text),ensure_ascii=False,indent=2)+'\n```\n',{'warnings':warnings,'engine':'JSON reading view; original contract preserved'}
 if kind not in ('html','mediawiki'):raise ValueError('Unsupported source conversion: '+kind)
 if kind=='html':
  cleaner=SafeHTML(source_url);cleaner.feed(text);text=''.join(cleaner.parts)
 references=[]
 if kind=='mediawiki':
  def protect_ref(match):
   references.append(match.group(0));return 'RAWREF'+str(len(references))+'TOKEN'
  text=re.sub(r'<ref\b[^>]*?/\s*>|<ref\b[^>]*>.*?</ref\s*>',protect_ref,text,flags=re.I|re.S)
  text=re.sub(r'</?ref\b[^>]*>',protect_ref,text,flags=re.I)
 engine=pandoc_path()
 r=pandoc_convert(engine,['--sandbox','--from='+kind,'--to=json'],text.encode())
 if r is None:
  if kind=='html':
   warnings.append('pandoc_reader_timeout_text_fallback')
   return html_text_fallback(text),{'warnings':warnings,'engine':'text fallback after pandoc timeout '+str(PANDOC_TIMEOUT_SECONDS)+'s'}
  return mediawiki_verbatim(body,charset,warnings,'pandoc_reader_timeout_verbatim')
 if r.returncode:
  if kind=='mediawiki':
   out,meta=mediawiki_verbatim(body,charset,warnings,'mediawiki_reader_fallback_verbatim')
   meta['warnings'].append(r.stderr.decode(errors='replace')[:500]);return out,meta
  raise RuntimeError('Pandoc reader: '+r.stderr.decode(errors='replace')[:600])
 ast=json.loads(r.stdout);raw_count=0
 def walk(x):
  nonlocal raw_count
  if isinstance(x,list):return [walk(v) for v in x]
  if not isinstance(x,dict):return x
  if x.get('t') in ('RawBlock','RawInline'):
   fmt,value=x['c'];raw_count+=1
   # Preserve unexpanded templates/unsupported markup as inert code, never drop it.
   return {'t':'CodeBlock' if x['t']=='RawBlock' else 'Code','c':[['',[fmt],[]],value]}
  if x.get('t') in ('Link','Image') and kind=='mediawiki':
   dest=x['c'][-1][0]
   if not urlsplit(dest).scheme:
    x['c'][-1][0]=urljoin(source_url,dest) if dest.startswith('#') else 'https://vi.wikipedia.org/wiki/'+quote(dest.replace(' ','_'),safe=':#()/%')
  return {k:walk(v) for k,v in x.items()}
 ast=walk(ast)
 r=pandoc_convert(engine,['--sandbox','--from=json','--to=gfm-raw_html','--wrap=none'],json.dumps(ast,ensure_ascii=False).encode())
 if r is None:
  if kind=='html':
   warnings.append('pandoc_writer_timeout_text_fallback')
   return html_text_fallback(text),{'warnings':warnings,'engine':'text fallback after pandoc writer timeout '+str(PANDOC_TIMEOUT_SECONDS)+'s'}
  return mediawiki_verbatim(body,charset,warnings,'pandoc_writer_timeout_verbatim')
 if r.returncode:raise RuntimeError('Pandoc writer: '+r.stderr.decode(errors='replace')[:600])
 if raw_count:warnings.append('unexpanded_markup_preserved_as_code:'+str(raw_count))
 if r.stderr:warnings.append('pandoc_writer:'+r.stderr.decode(errors='replace')[:500])
 rendered=r.stdout.decode()
 for i,reference in enumerate(references,1):
  rendered=rendered.replace('RAWREF'+str(i)+'TOKEN','[^raw-ref-'+str(i)+']')
  fence='`'*max(3,max((len(m.group()) for m in re.finditer(r'`+',reference)),default=0)+1)
  urls=list(dict.fromkeys(re.findall(r'https?://[^\s|}<>\]"\']+',reference)))
  note=(' '.join('[Nguồn](<'+html.unescape(u)+'>)' for u in urls)+'\n\n' if urls else '')+fence+'mediawiki\n'+reference+'\n'+fence
  rendered+='\n[^raw-ref-'+str(i)+']: '+note.replace('\n','\n    ')+'\n'
 if references:warnings.append('reference_markup_preserved_with_footnotes:'+str(len(references)))
 return unicodedata.normalize('NFC',rendered),{'warnings':warnings,'engine':subprocess.run([engine,'--version'],capture_output=True,text=True,timeout=5).stdout.splitlines()[0]}

def write_source(package,source_path,meta,kind,source_base=None):
 package=Path(package).resolve();base=Path(source_base or package).resolve()
 if (package/'checksums.json').exists():raise ValueError('Output package sealed')
 source=confined(base,source_path);body=source.read_bytes();digest=sha(body)
 expected=meta.get('source_sha256')
 if expected and expected!=digest:raise ValueError('Source checksum mismatch before Markdown conversion')
 url=meta.get('source_url','');text,conversion=convert(body,kind,url,meta.get('charset','utf-8'))
 title=meta.get('title')
 if not title and kind=='html':
  match=re.search(r'<title[^>]*>(.*?)</title>',body.decode('utf-8',errors='replace'),re.I|re.S)
  if match:title=html.unescape(re.sub('<[^>]+>','',match.group(1))).strip()
 title=title or url or source.name
 identity={'source_sha256':digest,'kind':kind,'meta':meta,'source_path':str(source.relative_to(base)),'source_base':os.path.relpath(base,package),'converter':VERSION}
 key=sha(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode());dest=package/'markdown/sources'/f'{key}.md'
 fields={'okf_version':'0.2','type':'source_markdown','title':title,'updated':str(meta.get('retrieved_at') or 'unknown')[:10],'status':'needs_review','representation':'derived_markdown_not_original','source_format':kind,'source_url':url,'source_path':os.path.relpath(source,package),'source_path_base':'package','source_sha256':digest,'retrieved_at':meta.get('retrieved_at'),'converter':VERSION,'conversion_engine':conversion['engine'],'conversion_warnings':conversion['warnings'],'page_id':meta.get('page_id'),'revision_id':meta.get('revision_id'),'revision_timestamp':meta.get('revision_timestamp'),'license':meta.get('license','not_assumed'),'attribution':meta.get('attribution','Source publisher; no ownership/legal inference')}
 note='> Bản Markdown chuyển đổi từ nguồn; không phải bản gốc và không tự xác minh nội dung. '
 if conversion['warnings']:note+='Các template/markup chưa dựng được giữ dưới dạng mã; xem conversion_warnings. '
 content=frontmatter(fields)+note+'\n\n'+text+'\n\n## Liên kết và ghi công\n\n- [Bản nguồn lưu trữ](<'+os.path.relpath(source,dest.parent)+'>)\n'
 if url:content+='- [Nguồn trực tuyến](<'+url+'>)\n'
 if meta.get('revision_url'):content+='- [Revision](<'+meta['revision_url']+'>)\n'
 content+='- Giấy phép: '+str(fields['license'])+'; '+str(fields['attribution'])+'\n'
 put(dest,content.encode())
 return {'markdown_path':str(dest.relative_to(package)),'markdown_sha256':sha(content.encode()),'markdown_source_sha256':digest,'markdown_converter':VERSION,'markdown_status':'converted','conversion_warnings':conversion['warnings']}

def source_records(data):
 if isinstance(data,dict):
  if 'wikitext_path' in data and 'wikitext_sha256' in data:yield ('mediawiki',data)
  elif data.get('raw_path') and data.get('sha256'):yield ('html' if data['raw_path'].endswith('.html') else 'other',data)
  for key,value in data.items():
   if key not in ('input','input_context','evidence_raw','results_raw'):yield from source_records(value)
 elif isinstance(data,list):
  for v in data:yield from source_records(v)

def metadata(kind,r):
 if kind=='mediawiki':return {'source_url':r.get('source_url',''),'title':r.get('resolved_title'),'source_sha256':r['wikitext_sha256'],'page_id':r.get('page_id'),'revision_id':r.get('revision_id'),'revision_timestamp':r.get('revision_timestamp'),'retrieved_at':r.get('response',{}).get('retrieved_at'),'license':r.get('license','CC-BY-SA-4.0'),'attribution':r.get('attribution','Wikipedia tiếng Việt contributors'),'revision_url':r.get('revision_url')}
 return {'source_url':r.get('final_url',r.get('requested_url','')),'source_sha256':r['sha256'],'retrieved_at':r.get('retrieved_at'),'license':r.get('rights','not_assumed'),'http_status':r.get('http_status')}

def add_record(package,kind,r,base=None):
 if kind=='mediawiki':path=r['wikitext_path']
 elif kind=='html':path=r['raw_path']
 elif kind=='other':
  path=r['raw_path']
  if path.endswith('.pdf'):raise ValueError('PDF Markdown conversion not available; do not publish as normalized')
  kind='text'
 else:return None
 base=Path(base or package).resolve();meta=metadata(kind,r)
 original=confined(base,path)
 if not original.exists():
  # A review overlay can refer to a sibling RAW package; resolve only by exact bytes.
  found=None
  for sibling in sorted(base.parent.iterdir()):
   if not sibling.is_dir() or not sibling.resolve().is_relative_to(base.parent):continue
   candidate=confined(sibling,path)
   if candidate.is_file() and sha(candidate.read_bytes())==meta['source_sha256']:found=sibling;break
  if found is None:raise ValueError('Missing RAW source dependency: '+path)
  base=found
 m=write_source(package,path,meta,kind,base);r.update(m);return m

def target_page(package,r,base=None):
 base=Path(base or package);tid=r.get('item_id',r.get('target_id',''))
 if not tid:return None
 key=sha((base.name+':'+tid).encode());dest=package/'markdown/targets'/f'{key}.md';refs=[]
 for kind,s in source_records(r):
  m=add_record(package,kind,s,base)
  if m:refs.append(m)
 fields={'okf_version':'0.2','type':'verification_target','title':r.get('label',tid),'updated':str(r.get('finished_at',r.get('collected_at','unknown')))[:10],'status':r.get('status','needs_review'),'request_item_id':tid,'canonical_assignment':'not_performed_by_RAW'}
 text=frontmatter(fields)+'# '+str(fields['title'])+'\n\n'+str(r.get('reason','Chưa có kết luận đối sánh.'))+'\n\n## Bản Markdown của nguồn\n\n'
 for m in {x['markdown_path']:x for x in refs}.values():text+='- [Nguồn](<'+os.path.relpath(package/m['markdown_path'],dest.parent)+'>)\n'
 if not refs:text+='Chưa có nội dung nguồn được chuyển đổi; xem trạng thái và lỗi, không suy thành đối tượng không tồn tại.\n'
 text+='\n## Metadata, bằng chứng và trường chưa xác minh\n\n```json\n'+json.dumps(r,ensure_ascii=False,indent=2)+'\n```\n'
 put(dest,text.encode(),mutable=True);return str(dest.relative_to(package))

def build_indexes(package):
 package=Path(package);date=now()[:10]
 for directory in [package/'markdown/sources',package/'markdown/targets',package/'markdown']:
  directory.mkdir(parents=True,exist_ok=True)
  files=sorted(p for p in directory.glob('*.md') if p.name!='index.md');links=[]
  for p in files:
   match=re.search(r'^title: (.*)$',p.read_text(),re.M)
   try:label=json.loads(match.group(1)) if match else p.stem
   except ValueError:label=p.stem
   links.append('- ['+str(label).replace('[','\\[').replace(']','\\]')+'](<'+p.name+'>)')
  if directory==package/'markdown':links=['- [Các nguồn](sources/index.md)','- [Các target](targets/index.md)']
  put(directory/'index.md',(frontmatter({'okf_version':'0.2','type':'index','title':'RAW Markdown — '+directory.name,'updated':date,'status':'active'})+'\n'.join(links)+'\n').encode(),mutable=True)
 if not (package/'index.md').exists():put(package/'index.md',(frontmatter({'okf_version':'0.2','type':'index','title':'Gói RAW — bản đọc Markdown','updated':date,'status':'needs_review'})+'- [Đọc dữ liệu Markdown](markdown/index.md)\n').encode())

def materialize(package,results):
 package=Path(package).resolve()
 if (package/'checksums.json').exists():raise ValueError('Cannot backfill sealed package in place')
 for r in results:target_page(package,r)
 build_indexes(package)

def materialize_records(package):
 """Human-readable control views; machine JSON/JSONL stays unchanged."""
 package=Path(package).resolve()
 for p in sorted(package.rglob('*')):
  if not p.is_file() or 'markdown' in p.relative_to(package).parts or p.name=='checksums.json':continue
  if p.suffix not in ('.json','.jsonl'):continue
  write_source(package,str(p.relative_to(package)),{'title':'Metadata — '+str(p.relative_to(package)),'source_sha256':sha(p.read_bytes()),'source_url':'','retrieved_at':None},'json' if p.suffix=='.json' else 'text')
 build_indexes(package)

def journal_view(path):
 path=Path(path);dest=path.with_suffix('.md')
 if dest.exists():return dest
 b=path.read_bytes();d=json.loads(b)
 fields={'okf_version':'0.2','type':'exchange_record','title':'INF–RAW '+str(d.get('state',d.get('message_type','record'))),'updated':str(d.get('created_at','unknown'))[:10],'status':d.get('state','recorded'),'source_path':path.name,'source_sha256':sha(b),'representation':'reading_view_of_original_json'}
 body=frontmatter(fields)+'[Bản ghi máy nguyên bản](<'+path.name+'>)\n\n```json\n'+json.dumps(d,ensure_ascii=False,indent=2)+'\n```\n'
 put(dest,body.encode());return dest

def validate(package,results=None):
 package=Path(package).resolve();errors=[]
 if not (package/'markdown/index.md').exists():errors.append('Missing Markdown reading index')
 for p in (package/'markdown').rglob('*.md'):
  text=p.read_text();match=re.match(r'^---\n(.*?)\n---\n',text,re.S)
  if not match:errors.append('Missing frontmatter: '+str(p));continue
  fields={}
  try:
   for line in match.group(1).splitlines():
    k,v=line.split(': ',1);fields[k]=json.loads(v)
  except (ValueError,TypeError):errors.append('Invalid frontmatter: '+str(p));continue
  if fields.get('okf_version')!='0.2':errors.append('Wrong OKF version')
  for k in ('type','title','updated','status'):
   if not fields.get(k):errors.append('Missing '+k)
  if fields.get('type')=='source_markdown':
   source=(package/fields['source_path']).resolve()
   # Supplemental provenance may reference another RAW package, but never upstream.
   raw_root=package.parent.parent
   if not source.is_relative_to(raw_root.resolve()):errors.append('Source outside RAW')
   elif not source.is_file() or sha(source.read_bytes())!=fields['source_sha256']:errors.append('Source checksum mismatch')
 if results is not None:
  for r in results:
   for kind,s in source_records(r):
    if kind not in ('html','mediawiki','other'):continue
    p=s.get('markdown_path')
    if not p:errors.append('Source missing Markdown: '+str(s.get('raw_path',s.get('wikitext_path'))));continue
    q=confined(package,p)
    if not q.is_file() or sha(q.read_bytes())!=s.get('markdown_sha256'):errors.append('Markdown checksum mismatch')
 if errors:raise ValueError('; '.join(errors[:20]))
 return {'status':'PASS','markdown_files':len(list((package/'markdown').rglob('*.md'))),'profile':'OKF 0.2','converter':VERSION}
