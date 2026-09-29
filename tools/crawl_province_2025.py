#!/usr/bin/env python3
"""Read-only Wikipedia API collector for 63+34 INF observation targets. No INF writes."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
from pathlib import Path
import random
import re
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.0'
API = 'https://vi.wikipedia.org/w/api.php'
UA = 'RAW-WIKIPEDIA/0.3 (https://github.com/leanhvu-ktnn/RAW_WIKIPEDIA; contact via repository issues)'
GROUPS = [('before', 'historical_before_reorganization', 63), ('after', 'post_reorganization_baseline', 34)]
PILOT = {('before','Gia Lai'),('before','Bình Định'),('after','Gia Lai'),('before','Hà Nội'),('after','Hà Nội')}

def now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def sha(b): return hashlib.sha256(b).hexdigest()
def encode(x): return (json.dumps(x, ensure_ascii=False, indent=2)+'\n').encode()
def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    with temp.open('wb') as f: f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
def put_json(path, data): atomic(path,encode(data))
def read_json(path): return json.loads(path.read_bytes())
def short(label):
    name=re.sub(r'^(tỉnh|thành phố)\s+', '', unicodedata.normalize('NFC',label), flags=re.I)
    return 'Thành phố Hồ Chí Minh' if name=='Hồ Chí Minh' else name
def check_root(root):
    root=root.resolve()
    if not root.is_relative_to(ROOT) or root==ROOT: raise ValueError('Output must be a package directory inside RAW_WIKIPEDIA')
    return root

def prepare(input_path, root):
    raw=input_path.read_bytes();data=json.loads(raw)
    frozen=root/'input/province-before-after-2025.json'
    if frozen.exists() and frozen.read_bytes()!=raw: raise ValueError('Input changed; use a new package. Frozen input must not be replaced.')
    atomic(frozen,raw)
    subjects={s['inf_id']:s for s in data['subjects']}
    if len(subjects)!=len(data['subjects']): raise ValueError('duplicate observation IDs')
    targets=[]
    for phase,key,count in GROUPS:
        ids=data[key]
        if len(ids)!=count or len(set(ids))!=count: raise ValueError('Unexpected target inventory')
        for index,obs_id in enumerate(ids):
            subject=subjects[obs_id]
            events=[e for e in data['events'] if obs_id in e['predecessor_observation_ids']+e['successor_observation_ids']]
            tid=f"{phase}-{obs_id.split(':',1)[1]}"
            targets.append({'target_id':tid,'target_id_namespace':'RAW staging only; not an INF identity',
                'phase':phase,'input_pointer':f'/{key}/{index}','input_observation_id':obs_id,
                'input_subject':subject,'input_events':events,'label':subject['label'],'search_name':short(subject['label']),
                'temporal_scope':'immediately_before_nq202_legal_effect' if phase=='before' else 'nq202_post_reorganization_baseline_not_crawl_date_current',
                'legal_effective_on_from_input':sorted({e['legal_effective_on'] for e in events}),
                'government_operational_on_from_input':sorted({e['operational_on'] for e in events})})
    stage={'staging_schema_version':'province-observation-0.1.0','collector_version':VERSION,
        'source':{'logical_path':'INF/context/bao-cao/evidence/vietnam-territory-law/province-before-after-2025.json','file':'input/province-before-after-2025.json','sha256':sha(raw),'declared_version':data.get('schema_version',data.get('version')),'version_basis':'content-addressed SHA-256; no version invented','input_document_inf_id':data['inf_id'],'source_pdf':data['source_pdf'],'source_pdf_sha256':data['source_sha256']},
        'contract_gap':'INF–RAW 0.1.0 requires canonical typed entity_ref; this input contains observations, so no entity_type coercion and no INF ID creation.',
        'temporal_note_from_input':data['temporal_note'],'targets':targets}
    put_json(root/'staging.json',stage)
    return stage

def retry_after(value, current=None):
    if not value:return 0.0
    try:return max(0.0,float(value))
    except ValueError:
        return max(0.0,(parsedate_to_datetime(value)- (current or datetime.now(timezone.utc))).total_seconds())

class APIError(RuntimeError): pass
class Client:
    def __init__(self, root, opener=urlopen, sleeper=time.sleep, max_attempts=5):
        self.root=root;self.opener=opener;self.sleep=sleeper;self.max_attempts=max_attempts;self.last=0.0
    def get(self, params):
        params={'format':'json','formatversion':'2','maxlag':5,**params}
        url=API+'?'+urlencode(sorted(params.items()))
        key=sha(url.encode());meta_path=self.root/'requests'/f'{key}.json'
        if meta_path.exists():
            meta=read_json(meta_path);body=(self.root/meta['path']).read_bytes()
            if sha(body)!=meta['sha256']:raise APIError('Cached response checksum mismatch')
            return json.loads(body),meta
        for attempt in range(self.max_attempts):
            wait=max(0,1.0-(time.monotonic()-self.last));self.sleep(wait)
            self.last=time.monotonic();headers={};retry=False
            try:
                with self.opener(Request(url,headers={'User-Agent':UA,'Accept':'application/json','Accept-Encoding':'identity'}),timeout=30) as response:
                    body=response.read();headers=dict(response.headers);status=response.status
                data=json.loads(body)
                if 'error' in data:
                    code=data['error'].get('code');retry=code in ('maxlag','ratelimited','readonly')
                    if not retry:raise APIError('API error: '+json.dumps(data['error'],ensure_ascii=False))
                    error='API '+str(code)
                else:
                    digest=sha(body);path=f'sources/responses/{digest}.json';dest=self.root/path
                    if not dest.exists():atomic(dest,body)
                    meta={'request_url':url,'params':params,'retrieved_at':now(),'http_status':status,'headers':{k:v for k,v in headers.items() if k.lower() in ('date','content-type','content-length','etag','last-modified','retry-after')},'path':path,'sha256':digest,'byte_length':len(body),'media_type':'application/json','representation':'unmodified MediaWiki HTTP response body bytes'}
                    put_json(meta_path,meta)
                    return data,meta
            except HTTPError as exc:
                headers=dict(exc.headers or {});error=f'HTTP {exc.code}';retry=exc.code in (429,500,502,503,504);exc.close()
                if not retry:raise APIError(error) from exc
            except (URLError,TimeoutError,ConnectionError,OSError) as exc:
                error=type(exc).__name__+': '+str(exc);retry=True
            except json.JSONDecodeError as exc:
                raise APIError('Invalid API JSON') from exc
            event={'at':now(),'request_url':url,'attempt':attempt+1,'error':error,'retryable':retry}
            with (self.root/'network-events.jsonl').open('a') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
            if attempt+1==self.max_attempts:raise APIError(error+'; retry exhausted')
            delay=max(retry_after(headers.get('Retry-After',headers.get('retry-after'))),2**attempt+random.uniform(0,0.2))
            if delay>60:raise APIError(error+f'; deferred Retry-After {delay}s')
            self.sleep(delay)
        raise APIError('unreachable retry state')

def disambiguation(page):return 'disambiguation' in page.get('pageprops',{}) or 'định hướng' in page.get('title','')
def discover(client,name):
    titles=[name,f'{name} (tỉnh)',f'{name} (tỉnh cũ)',f'{name} (trước 2025)']
    if name=='Hà Nam': titles.insert(0,'Hà Nam (tỉnh Việt Nam)')
    data,meta=client.get({'action':'query','titles':'|'.join(titles),'redirects':1,'prop':'info|pageprops','inprop':'url','ppprop':'wikibase_item|disambiguation'})
    pages=data.get('query',{}).get('pages',[])
    valid=[p for p in pages if 'missing' not in p and p.get('ns')==0 and not disambiguation(p)]
    # Do not use first search hit. Candidate must be one of the queried province title forms or redirect destination.
    order={t:i for i,t in enumerate(titles)}
    valid.sort(key=lambda p:order.get(p['title'],10))
    unique={p['pageid']:p for p in valid}
    return list(unique.values()),{'searched_titles':titles,'normalized':data.get('query',{}).get('normalized',[]),'redirects':data.get('query',{}).get('redirects',[]),'pages':pages,'response':meta}

def snapshot(client,pageid,cutoff=None):
    params={'action':'query','pageids':pageid,'prop':'revisions','rvprop':'ids|timestamp|content|contentmodel','rvslots':'main','rvlimit':1}
    if cutoff:params.update(rvstart=cutoff,rvdir='older')
    data,meta=client.get(params)
    page=data.get('query',{}).get('pages',[{}])[0]
    revisions=page.get('revisions',[])
    if not revisions:return None
    rev=revisions[0];content=rev.get('slots',{}).get('main',{}).get('content')
    if not isinstance(content,str):raise APIError('Revision content unavailable/suppressed')
    return {'page_id':str(page['pageid']),'resolved_title':page['title'],'revision_id':str(rev['revid']),'revision_timestamp':rev['timestamp'],
            'source_url':'https://vi.wikipedia.org/wiki/'+quote(page['title'].replace(' ','_')),
            'revision_url':'https://vi.wikipedia.org/w/index.php?oldid='+str(rev['revid']),
            'contributors_url':'https://vi.wikipedia.org/w/index.php?title='+quote(page['title'])+'&action=history',
            'selection_cutoff':cutoff,'response':meta,'content':content,'wikitext_sha256':sha(content.encode()),
            'license':'CC-BY-SA-4.0','license_url':'https://creativecommons.org/licenses/by-sa/4.0/','attribution':'Wikipedia tiếng Việt contributors; full revision/history URLs retained'}

def evidence(content,name):
    lines=content.splitlines();out=[];section='lead'
    lead_added=0
    for i,line in enumerate(lines):
        heading=re.match(r'^(={2,6})\s*(.*?)\s*\1\s*$',line)
        if heading:section=heading.group(2)
        categories=[]
        plain=re.sub(r'\[\[([^]|]+)\|([^]]+)\]\]',r'\2',line).replace('[[','').replace(']]','').replace("'''",'')
        if name.casefold() in plain.casefold() and re.search(r'\b(tỉnh|thành phố trực thuộc trung ương)\b',plain,re.I) and not line.startswith(('|','*','#',':','{{')) and lead_added<2:
            categories.append('name_and_territory_type');lead_added+=1
        if re.search(r'202\s*/\s*2025\s*/\s*QH15',line,re.I):categories.append('cited_resolution_202')
        if ('2025' in line or '202/2025' in line) and re.search(r'sáp nhập|sắp xếp|hợp nhất|hợp nhất|thành lập|không.*(sáp nhập|sắp xếp)',plain,re.I):categories.append('reorganization_and_period')
        if re.search(r'trước.*2025|1991.*2025|1975.*2025|tỉnh cũ',plain,re.I) and name.casefold() in plain.casefold():categories.append('historical_period')
        if ('2025' in line) and re.search(r'1 tháng 7|01/07|1/7|12 tháng 6|12/6|12/06',line):categories.append('dates_stated_by_wikipedia')
        if categories:
            out.append({'evidence_id':'line-'+str(i+1),'line_start':i+1,'line_end':i+1,'section':section,'categories':categories,'excerpt_wikitext':line,'plain_for_review':plain,'cited_urls':re.findall(r'https?://[^\s|}<]+',line),
                        'interpretation':'Wikipedia statement, not independently verified legal authority'})
    return out

def persist_snapshot(root,snap):
    base=f"sources/viwiki/{snap['page_id']}/{snap['revision_id']}"
    raw_path=base+'/source.wikitext';p=root/raw_path
    if p.exists() and sha(p.read_bytes())!=snap['wikitext_sha256']:raise ValueError('Immutable revision text changed')
    if not p.exists():atomic(p,snap['content'].encode())
    record={k:v for k,v in snap.items() if k!='content'};record['wikitext_path']=raw_path
    return record

def collect_target(client,target,root):
    name=target['search_name'];candidates,discovery=discover(client,name)
    result={'target_id':target['target_id'],'phase':target['phase'],'input_observation_id':target['input_observation_id'],'label':target['label'],
        'status':'ambiguous','reason':'Nguồn cần xét bằng chứng thời kỳ; không tự canonical hóa INF.','discovery':discovery,'sources':[],
        'wikipedia_claims':[],'unverified_fields':[],'conflicts':[],'collected_at':now(),'collector_version':VERSION}
    if not candidates:
        result.update(status='not_found',reason='Không có bài không-định-hướng trong các title ứng viên; không khẳng định không tồn tại toàn Wikipedia.')
        return result
    # Province candidates only, up to two distinct articles; shared page IDs never merge target records.
    for candidate in candidates[:2]:
        sn=snapshot(client,candidate['pageid'])
        if sn:
            record=persist_snapshot(root,sn);record['qid_from_current_discovery']=candidate.get('pageprops',{}).get('wikibase_item');record['evidence']=evidence(sn['content'],name);record['role']='current_article_historical_evidence';result['sources'].append(record)
        if target['phase'] in ('before','after'):
            cutoff='2025-06-11T23:59:59Z' if target['phase']=='before' else '2025-07-02T23:59:59Z'
            old=snapshot(client,candidate['pageid'],cutoff)
            if old and (not sn or old['revision_id']!=sn['revision_id']):
                record=persist_snapshot(root,old);record['evidence']=evidence(old['content'],name);record['role']='pre_legal_effect_revision_support_only' if target['phase']=='before' else 'post_reorganization_2025_revision_support_only';result['sources'].append(record)
    # Explicit evidence review is required; no semantic success inferred from revision timestamps.
    result['unverified_fields']=['temporal_entity_match_pending_review','legal_effective_date_independent_verification','government_operational_date_independent_verification']
    return result

def run(args):
    root=check_root(args.package);root.mkdir(parents=True,exist_ok=True)
    stage=prepare(args.input,root)
    if args.mode=='prepare':print(json.dumps({'targets':len(stage['targets']),'source_sha256':stage['source']['sha256']},ensure_ascii=False));return
    if args.mode=='all':
        gate=read_json(root/'pilot-validation.json')
        if gate.get('status')!='PASS' or gate.get('input_sha256')!=stage['source']['sha256']:raise ValueError('Pilot gate required before full collection')
    selected=[t for t in stage['targets'] if args.mode=='all' or (t['phase'],t['search_name']) in PILOT]
    if args.target_name:selected=[t for t in selected if t['search_name']==args.target_name]
    if not selected:raise ValueError('No matching targets')
    client=Client(root)
    checkpoint=read_json(root/'checkpoint.json') if (root/'checkpoint.json').exists() else {'staging_schema_version':stage['staging_schema_version'],'input_sha256':stage['source']['sha256'],'results':{}}
    if checkpoint['input_sha256']!=stage['source']['sha256']:raise ValueError('Checkpoint input mismatch')
    for i,target in enumerate(selected,1):
        tid=target['target_id'];old=checkpoint['results'].get(tid)
        if old and not args.refresh_results and (old['status']!='error' or not args.retry_errors):
            print(f"{i}/{len(selected)} cached {target['phase']} {target['label']}",flush=True);continue
        try:result=collect_target(client,target,root)
        except (APIError,OSError,ValueError) as exc:
            result={'target_id':tid,'phase':target['phase'],'input_observation_id':target['input_observation_id'],'label':target['label'],'status':'error','reason':str(exc),'sources':[],'collected_at':now(),'retryable':True}
        checkpoint['results'][tid]=result;put_json(root/'checkpoint.json',checkpoint)
        print(f"{i}/{len(selected)} {result['status']} {target['phase']} {target['label']} sources={len(result['sources'])}",flush=True)
    print('Collected',len(checkpoint['results']),'targets; semantic review and package validation still required.',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--package',type=Path,required=True);p.add_argument('--mode',choices=['prepare','pilot','all'],default='prepare');p.add_argument('--retry-errors',action='store_true');p.add_argument('--refresh-results',action='store_true');p.add_argument('--target-name')
    run(p.parse_args())
if __name__=='__main__':main()
