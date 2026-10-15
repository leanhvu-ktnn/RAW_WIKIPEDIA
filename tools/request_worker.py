#!/usr/bin/env python3
"""Bounded evidence collection from pushed, versioned targets; no canonical decisions."""
from pathlib import Path
import json,re,hashlib,unicodedata
from collections import Counter
from urllib.parse import urlsplit,unquote
from tools.local_exchange import relative,immutable,encode,request,emit,load,digest
from tools.crawl_province_2025 import Client,snapshot,persist_snapshot,disambiguation,put_json,now,APIError
from tools.fetch_official_evidence import Fetcher
from tools.raw_markdown import materialize,materialize_records,frontmatter,validate as validate_markdown
VERSION='bounded-verification/0.1.0'
REGISTRY={'territory':['crawl-wikipedia-diaban'],'organization':['crawl-wikipedia-coquan'],'query':['verify-wikipedia-query']}

def checked_files(root,req):
 root=Path(root).resolve()
 pkg=relative(root,req['package']['path']);manifest=relative(root,str((pkg/'manifest.json').relative_to(root)))
 if digest(manifest.read_bytes())!=req['package']['manifest_sha256']:raise ValueError('Input manifest mismatch')
 m=load(manifest);seen=set();files=[]
 for f in m.get('files',[]):
  p=relative(pkg,f['path'])
  if f['path'] in seen:raise ValueError('Duplicate manifest entry')
  seen.add(f['path']);body=p.read_bytes()
  if digest(body)!=f['sha256'] or len(body)!=f['bytes']:raise ValueError('Input file checksum/length mismatch: '+f['path'])
  files.append((f['path'],body))
 if 'targets.json' not in seen:raise ValueError('Manifest must include targets.json')
 return manifest.read_bytes(),files

def adapt(req,payload):
 ver=payload.get('schema_version');rows=payload.get('targets',[]);out=[]
 if ver=='inf-territory-web-input/1.0':
  byref={t.get('inf_territory_ref',t.get('inf_ref')):t for t in rows}
  if len(byref)!=len(rows):raise ValueError('Duplicate territory refs')
  for item in req['items']:
   refs=item.get('target_refs',[])
   if len(refs)!=1 or refs[0].get('type')!='DiaBan':raise ValueError('Expected one DiaBan target ref')
   t=byref[refs[0]['inf_id']];parent=byref.get(t.get('parent_territory_ref'),{})
   if item['suggested_skill']!='crawl-wikipedia-diaban':raise ValueError('Skill/type mismatch')
   out.append({'item_id':item['item_id'],'kind':'territory','label':t['name'],'reference_date':payload.get('reference_date'),'parent_label':parent.get('name'),'level':t['administrative_level'],'input':t,'wikipedia_candidate_url':t.get('wikipedia_candidate_url'),'official_urls':[t['official_website_candidate_url']] if t.get('official_website_candidate_url') else []})
  if len(out)!=len(rows):raise ValueError('Target coverage mismatch')
 elif ver=='raw-verification-input/1.0':
  byid={t['item_id']:t for t in rows}
  if len(byid)!=len(rows) or set(byid)!={i['item_id'] for i in req['items']}:raise ValueError('Target IDs must match items')
  for item in req['items']:
   t=byid[item['item_id']];kind=t['kind']
   if kind not in REGISTRY or item.get('suggested_skill') not in REGISTRY[kind]:raise ValueError('Unsupported task adapter/skill')
   if not isinstance(t.get('label'),str) or not t['label'].strip():raise ValueError('Target label required')
   if kind=='query' and not t.get('query'):raise ValueError('Structured query required')
   if len(t.get('official_urls',[]))>5:raise ValueError('Max 5 official URLs per target')
   out.append({**t,'input':t})
 else:raise ValueError('Unsupported payload schema: '+str(ver)+'; push supported structured targets, not executable instructions')
 if not out or len(out)>1000:raise ValueError('Supported target count is 1..1000')
 for t in out:
  date=t.get('reference_date')
  if not isinstance(date,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):raise ValueError('reference_date required; never infer current from label')
 return out

def clean(name):
 return re.sub(r'\s+mới$','',re.sub(r'^(tỉnh|thành phố|phường|xã|thị trấn)\s+','',unicodedata.normalize('NFC',name),flags=re.I),flags=re.I).strip()

def titles_for(t):
 if t.get('wikipedia_candidate_url'):
  u=urlsplit(t['wikipedia_candidate_url'])
  if u.scheme!='https' or u.netloc!='vi.wikipedia.org' or not u.path.startswith('/wiki/'):raise ValueError('Invalid Wikipedia candidate URL')
  return [unquote(u.path[len('/wiki/'):]).replace('_',' ')]
 n=clean(t['label']);parent=clean(t.get('parent_label') or '')
 if t['kind']=='territory':
  if t.get('level')=='province':return list(dict.fromkeys([n,n+' (tỉnh)',t['label']]))
  kind={'ward':'phường','commune':'xã','township':'thị trấn'}.get(t.get('level'),'địa bàn')
  return list(dict.fromkeys([n+', '+parent,n+' ('+kind+')',n,t['label']]))
 return [t['label']]

def excerpts(content,t):
 out=[];offset=0;name=clean(t['label']).casefold();words=[w for w in re.findall(r'\w+',t.get('query','').casefold()) if len(w)>3]
 for line in content.splitlines(keepends=True):
  plain=line.casefold()
  relevant=name in plain or (t['kind']=='query' and sum(w in plain for w in words)>=min(3,len(words)) and words)
  if relevant and len(out)<24:
   out.append({'character_start':offset,'character_end_exclusive':offset+len(line),'quote':line,'origin':'wikipedia_revision','claim_status':'unreviewed_excerpt','note':'Candidate evidence only; not independent legal confirmation'})
  offset+=len(line)
 return out

def collect(client,t,pkg):
 r={'item_id':t['item_id'],'label':t['label'],'kind':t['kind'],'input':t['input'],'reference_date':t['reference_date'],'canonical_id':None,'status':'ambiguous','reason':'Candidate evidence requires entity/time review.','queries':[],'sources':[],'official_sources':[],'unverified_fields':['identity_and_time','claim_truth','current_legal_status'],'started_at':now()}
 try:
  pool={};needs_search=t['kind']=='query'
  if not needs_search:
   titles=titles_for(t);d,m=client.get({'action':'query','titles':'|'.join(titles),'redirects':1,'prop':'info|pageprops','inprop':'url','ppprop':'wikibase_item|disambiguation'})
   q=d.get('query',{});r['queries'].append({'kind':'titles','searched_titles':titles,'normalized':q.get('normalized',[]),'redirects':q.get('redirects',[]),'pages':q.get('pages',[]),'response':m})
   pool={p['pageid']:p for p in q.get('pages',[]) if 'missing' not in p and p.get('ns')==0 and not disambiguation(p)}
   needs_search=not pool
  if needs_search:
   query=t.get('query') or '"'+clean(t['label'])+'" '+(clean(t.get('parent_label') or '') if t['kind']=='territory' else '')
   d,m=client.get({'action':'query','list':'search','srsearch':query,'srnamespace':0,'srlimit':5,'srprop':'snippet'})
   q=d.get('query',{});r['queries'].append({'kind':'search','query':query,'response':m,'results':q.get('search',[]),'continuation':d.get('continue')})
   pool={p['pageid']:p for p in q.get('search',[])}
  r['candidate_pages']=list(pool.values());r['candidate_limit']=2
  # Exact-title candidates precede bare-name candidates; title matches never establish identity.
  for p in list(pool.values())[:2]:
   sn=snapshot(client,p['pageid'],t['reference_date']+'T23:59:59Z')
   if not sn:continue
   s=persist_snapshot(pkg,sn);s['evidence']=excerpts(sn['content'],t);s['role']='candidate_pending_semantic_review'
   s['final_url']=sn['source_url'];s['final_url_note']='API canonical article URL, not observed browser redirect'
   s['related_urls']=list(dict.fromkeys(re.findall(r'https?://[^\s|}<\]"<>]+',sn['content'])))[:100]
   r['sources'].append(s)
  if not pool:
   r['status']='ambiguous' if any(q.get('continuation') for q in r['queries']) else 'not_found'
   r['reason']='No candidate in recorded bounded titles/search; not proof of nonexistence.'
  elif not r['sources']:
   r['status']='ambiguous';r['reason']='Candidates found but no readable revision at requested cutoff.'
  # Only explicitly supplied official URLs are fetched automatically; citation URLs remain leads.
  if t.get('official_urls'):
   fetcher=Fetcher(pkg,timeout=8,max_attempts=1)
   for url in t['official_urls']:
    try:
     m=fetcher.get(url);text=(pkg/m['text_path']).read_text() if m.get('text_path') else ''
     shell=bool(re.search(r'đang tải dữ liệu|vui lòng.*javascript|verify.*human|just a moment|checking your browser',text,re.I))
     operator=[];off=0
     for line in text.splitlines(keepends=True):
      if len(operator)<12 and re.search(r'cơ quan chủ quản|chịu trách nhiệm|ủy ban nhân dân|uỷ ban nhân dân|đơn vị quản lý',line,re.I):operator.append({'character_start':off,'character_end_exclusive':off+len(line),'quote':line,'placeholder_suspected':bool(re.search(r'Nguyễn Văn A|xã X\b|xxx\.gov',line,re.I))})
      off+=len(line)
     r['official_sources'].append({'response':m,'content_status':('loading_or_challenge' if shell else 'needs_content_review') if m['status']=='downloaded' else 'unavailable','claim_status':'unverified','operator_candidate_spans':operator,'origin':'official_live'})
    except (ValueError,OSError) as e:r['official_sources'].append({'url':url,'status':'error','reason':str(e),'claim_status':'unverified'})
 except (APIError,OSError,ValueError) as e:r.update(status='error',reason=type(e).__name__+': '+str(e))
 r['finished_at']=now();return r

def verify_result(pkg,r):
 if r['status'] not in ('ambiguous','not_found','error','found'):raise ValueError('Invalid target status')
 if r['status']=='found':raise ValueError('Automated collector cannot assert semantic found')
 for q in r['queries']:
  m=q['response'];p=relative(pkg,m['path'])
  if digest(p.read_bytes())!=m['sha256']:raise ValueError('Response checksum mismatch')
 for s in r['sources']:
  m=s['response'];p=relative(pkg,m['path'])
  if digest(p.read_bytes())!=m['sha256'] or p.stat().st_size!=m['byte_length']:raise ValueError('Snapshot checksum mismatch')
  p=relative(pkg,s['wikitext_path']);body=p.read_bytes()
  if digest(body)!=s['wikitext_sha256']:raise ValueError('Wikitext checksum mismatch')
  text=body.decode()
  for e in s['evidence']:
   if text[e['character_start']:e['character_end_exclusive']]!=e['quote']:raise ValueError('Evidence span mismatch')
 for s in r.get('official_sources',[]):
  m=s.get('response',{})
  if m.get('raw_path'):
   p=relative(pkg,m['raw_path']);b=p.read_bytes()
   if digest(b)!=m['sha256'] or len(b)!=m['byte_length']:raise ValueError('Official snapshot checksum mismatch')
  if m.get('text_path'):
   p=relative(pkg,m['text_path']);b=p.read_bytes()
   if digest(b)!=m['text_sha256']:raise ValueError('Official derivative checksum mismatch')
   text=b.decode()
   for e in s.get('operator_candidate_spans',[]):
    if text[e['character_start']:e['character_end_exclusive']]!=e['quote']:raise ValueError('Operator span mismatch')

def freeze(root,path,pkg):
 req,h=request(root,path);manifest,files=checked_files(root,req)
 immutable(pkg/'input/request.json',path.read_bytes());immutable(pkg/'input/manifest.json',manifest)
 for name,body in files:immutable(relative(pkg/'input',name),body)
 targets=adapt(req,load(pkg/'input/targets.json'))
 # Reuse only locally captured bytes from the explicitly superseded request.
 predecessor=req.get('supersedes_pending_request_id')
 if predecessor:
  if not re.fullmatch(r'inf:[0-9a-f-]{36}',predecessor):raise ValueError('Invalid superseded request ID')
  base=relative(root,'packages/inbox-'+predecessor.split(':')[1]);deps=[]
  if (base/'checksums.json').exists():
   for f in load(base/'checksums.json')['files']:
    if not f['path'].startswith(('sources/','requests/')):continue
    source=relative(base,f['path']);body=source.read_bytes()
    if digest(body)!=f['sha256'] or len(body)!=f['bytes']:raise ValueError('Reuse checksum mismatch')
    immutable(relative(pkg,f['path']),body);deps.append({'path':str(source.relative_to(root)),'sha256':f['sha256'],'bytes':f['bytes']})
  immutable(pkg/'reuse-dependencies.json',encode({'supersedes':predecessor,'files':deps,'note':'HTTP metadata retains original capture time; copied bytes are not claimed as new downloads.'}))
 immutable(pkg/'staging.json',encode({'version':VERSION,'request_sha256':h,'targets':targets,'ontology':'wiki:ObservationTarget / wiki:Match; opaque INF refs, no sameAs or canonical IDs','budgets':{'max_targets':1000,'search_queries_per_target':1,'candidate_revisions_per_target':2,'official_urls_per_target':5}}))
 return req,h,targets

def run(root,path,progress=lambda **kw:None,client_factory=Client):
 root=Path(root).resolve();path=Path(path).resolve()
 req,h=request(root,path);pkg=relative(root,'packages/inbox-'+req['request_id'].split(':')[1]);pkg.mkdir(parents=True,exist_ok=True)
 if (pkg/'checksums.json').exists():return publish(root,path,pkg)
 req,h,targets=freeze(root,path,pkg)
 pilot=list(dict.fromkeys([0,min(1,len(targets)-1),next((i for i,t in enumerate(targets) if t.get('level')=='commune'),len(targets)-1),min(2,len(targets)-1),min(3,len(targets)-1)]))
 immutable(pkg/'plan.json',encode({'version':VERSION,'request_sha256':h,'pilot_item_ids':[targets[i]['item_id'] for i in pilot],'requires_semantic_review':True,'automatic_found':False}))
 client=client_factory(pkg,max_attempts=2);results={}
 for p in (pkg/'targets').glob('*.json'):
  r=load(p);verify_result(pkg,r);results[r['item_id']]=r
 def perform(t,phase):
  if t['item_id'] in results:return results[t['item_id']]
  progress(phase=phase,completed=len(results),total=len(targets),active_item=t['item_id'])
  r=collect(client,t,pkg);verify_result(pkg,r)
  immutable(pkg/'targets'/(digest(t['item_id'].encode())+'.json'),encode(r));results[t['item_id']]=r
  put_json(pkg/'checkpoint.json',{'request_sha256':h,'updated_at':now(),'completed':len(results),'total':len(targets),'items':{k:v['status'] for k,v in results.items()}})
  progress(phase=phase,completed=len(results),total=len(targets),active_item=None)
  return r
 gate=pkg/'pilot-validation.json'
 if not gate.exists():
  for i in pilot:perform(targets[i],'pilot')
  ok=any(results[targets[i]['item_id']]['sources'] for i in pilot) and all(results[targets[i]['item_id']]['status']!='error' for i in pilot)
  if not ok:raise RuntimeError('Pilot retrieval/integrity gate failed; no bulk crawl. Inspect target errors and request a bounded retry.')
  immutable(gate,encode({'status':'PASS','scope':'retrieval, provenance, conservative no-found outputs; semantic matching remains pending','request_sha256':h,'pilot_items':[targets[i]['item_id'] for i in pilot],'checked_at':now()}))
 if load(gate)['request_sha256']!=h:raise ValueError('Pilot input mismatch')
 for t in targets:perform(t,'collecting')
 ordered=[results[t['item_id']] for t in targets]
 for r in ordered:verify_result(pkg,r)
 materialize(pkg,ordered)
 markdown_validation=validate_markdown(pkg,ordered)
 immutable(pkg/'markdown-validation.json',encode(markdown_validation))
 counts=Counter(r['status'] for r in ordered);pages={s['page_id'] for r in ordered for s in r['sources']};revs={s['revision_id'] for r in ordered for s in r['sources']}
 summary={'request_id':req['request_id'],'request_sha256':h,'state':'partial','counts':{'targets':len(targets),'unique_pages':len(pages),'unique_revisions':len(revs),'statuses':dict(counts)},'semantic_review_pending':True,'results':ordered,'inf_action':'review_only'}
 immutable(pkg/'results.json',encode(summary))
 immutable(pkg/'validation.json',encode({'status':'PASS','scope':'artifact integrity and coverage, not semantic or legal verification','target_count':len(targets),'checked_at':now()}))
 report='# RAW inbox verification\n\nState: partial / review_only.\n\n'+json.dumps(summary['counts'],ensure_ascii=False,indent=2)+'\n\nCollected actual revision bytes and candidate evidence. No canonical identity or claim truth inferred. All ambiguous targets require entity, administrative level, parent territory and reference-date review. Government links extracted from Wikipedia are leads, not independent confirmation. Explicit official URLs, if supplied, retain independent capture provenance.\n\nSee results.json, staging.json, input/, targets/, sources/, validation.json and checksums.json.\n'
 immutable(pkg/'report.md',(frontmatter({'okf_version':'0.2','type':'report','title':'RAW inbox verification','updated':now()[:10],'status':'partial'})+report).encode())
 immutable(pkg/'manifest.json',encode({'version':VERSION,'request_id':req['request_id'],'request_sha256':h,'state':'partial','counts':summary['counts'],'inventory':'checksums.json','dependencies':['input/manifest.json'],'created_at':now()}))
 materialize_records(pkg);validate_markdown(pkg,ordered)
 files=[{'path':str(p.relative_to(pkg)),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(pkg.rglob('*')) if p.is_file() and p.name!='checksums.json']
 immutable(pkg/'checksums.json',encode({'files':files,'immutable_after_report':True}))
 return publish(root,path,pkg)

def publish(root,path,pkg):
 checks=load(pkg/'checksums.json');expected={f['path'] for f in checks['files']}
 actual={str(p.relative_to(pkg)) for p in pkg.rglob('*') if p.is_file() and p.name!='checksums.json'}
 if actual!=expected:raise ValueError('Sealed inventory mismatch')
 for f in checks['files']:
  p=relative(pkg,f['path']);b=p.read_bytes()
  if digest(b)!=f['sha256'] or len(b)!=f['bytes']:raise ValueError('Sealed checksum mismatch')
 d=load(pkg/'results.json');rp=str((pkg/'results.json').relative_to(root));items=[{'item_id':r['item_id'],'outcome':r['status'],'reason':r['reason'],'artifact_paths':[rp]} for r in d['results']]
 req,_=request(root,path);previous=sorted((root/'outbox/inf'/req['request_id'].split(':')[1]).glob('[0-9]*.json'))
 if previous:
  last=load(previous[-1])
  blocked_only=bool(last.get('items')) and all(i.get('outcome')=='blocked' for i in last['items'])
  if last.get('state') in ('completed','partial') and not blocked_only:return previous[-1]
 return emit(root,path,'partial',items,[str(p.relative_to(root)) for p in pkg.rglob('*') if p.is_file()])
