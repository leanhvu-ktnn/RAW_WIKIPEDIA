#!/usr/bin/env python3
"""Validate and export a staged province-observation package; no INF mutation."""
import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path
try:
    from tools.crawl_province_2025 import read_json,put_json,sha,atomic,now,PILOT
except ModuleNotFoundError:
    from crawl_province_2025 import read_json,put_json,sha,atomic,now,PILOT

def source_key(s):return s['page_id']+'/'+s['revision_id']
def check(condition,message):
    if not condition:raise ValueError(message)
def confined(root,path):
    out=(root/path).resolve();check(out.is_relative_to(root.resolve()),'Path escapes package: '+path);return out

def validate(root, pilot=False, inventory=False):
    stage=read_json(root/'staging.json');checkpoint=read_json(root/'checkpoint.json');reviews=read_json(root/'reviews.json')
    check(sha((root/stage['source']['file']).read_bytes())==stage['source']['sha256'],'Input checksum mismatch')
    check(checkpoint['input_sha256']==stage['source']['sha256'],'Checkpoint input mismatch')
    targets=[t for t in stage['targets'] if not pilot or (t['phase'],t['search_name']) in PILOT]
    check(len(targets)==(5 if pilot else 97),'Target count mismatch')
    check(len({t['target_id'] for t in stage['targets']})==97,'Target dedup incorrectly collapsed episodes')
    if not pilot:check(set(checkpoint['results'])=={t['target_id'] for t in targets},'Results must exactly cover all 97 targets')
    sources={};statuses=Counter();evidence_count=0
    context=read_json(root/'context-sources.json') if (root/'context-sources.json').exists() else []
    for target in targets:
        tid=target['target_id'];result=checkpoint['results'][tid];review=reviews.get(tid,{})
        check(result['input_observation_id']==target['input_observation_id'],'Observation ID changed')
        status=review.get('status',result['status']);statuses[status]+=1
        check(status in ('found','ambiguous','error','not_found'),'Invalid status')
        if result['status']=='error':check(status=='error','Network error converted to semantic result')
        pool={source_key(s):s for s in result['sources']+context}
        for source in result['sources']+context:sources[source_key(source)]=source
        if status=='found':
            check(review.get('reason') and review.get('accepted_evidence'),'Found without explicit evidence review')
            for ref in review['accepted_evidence']:
                s=pool[ref['source_key']];lines=(root/s['wikitext_path']).read_text().splitlines()
                a,b=ref['line_start'],ref['line_end']
                check(1<=a<=b<=len(lines),'Evidence line out of bounds')
                check(ref['excerpt_wikitext']=='\n'.join(lines[a-1:b]),'Reviewed evidence mismatch')
                check(ref['claim_scope'] in ('name_type','historical_extent','reorganization','unchanged_in_2025','legal_date_as_stated','operational_date_as_stated'),'Missing claim scope')
                evidence_count+=1
    for key,s in sources.items():
        body=confined(root,s['response']['path']).read_bytes()
        check(sha(body)==s['response']['sha256'] and len(body)==s['response']['byte_length'],'Response checksum mismatch: '+key)
        data=json.loads(body);page=next((p for p in data['query']['pages'] if str(p.get('pageid'))==s['page_id']),None)
        check(page is not None,'Page ID absent from response')
        rev=next((r for r in page.get('revisions',[]) if str(r['revid'])==s['revision_id']),None)
        check(rev is not None and rev['timestamp']==s['revision_timestamp'],'Revision mismatch')
        content=rev['slots']['main']['content'];stored=confined(root,s['wikitext_path']).read_bytes()
        check(stored==content.encode() and sha(stored)==s['wikitext_sha256'],'Wikitext not faithful to API response')
        check(s['license']=='CC-BY-SA-4.0' and s.get('contributors_url'),'Attribution missing')
        for e in s.get('evidence',[]):
            check(e['excerpt_wikitext']=='\n'.join(content.splitlines()[e['line_start']-1:e['line_end']]),'Extracted evidence mismatch')
    if inventory:
        listing=read_json(root/'checksums.json')
        for record in listing['files']:
            body=confined(root,record['path']).read_bytes()
            check(sha(body)==record['sha256'] and len(body)==record['bytes'],'Package file checksum mismatch: '+record['path'])
        listed={r['path'] for r in listing['files']}
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='checksums.json'}
        check(actual==listed,'Inventory has missing or additional files')
    return {'status':'PASS','scope':'pilot' if pilot else 'full-package','input_sha256':stage['source']['sha256'],'targets':len(targets),'statuses':dict(statuses),'unique_retrieved_pages':len({s['page_id'] for s in sources.values()}),'unique_retrieved_revisions':len(sources),'accepted_evidence_count':evidence_count,'raw_integrity':'verified against original API bytes','identity_scope':'observation staging; no canonical INF identity assertion','validated_at':now()}

def export(root):
    stage=read_json(root/'staging.json');results=read_json(root/'checkpoint.json')['results'];reviews=read_json(root/'reviews.json');context=read_json(root/'context-sources.json')
    manifest={'staging_schema_version':stage['staging_schema_version'],'input':stage['source'],'contract_gap':stage['contract_gap'],'inf_action':'review_only','completion_meaning':'all target outcomes and byte integrity, not all legal facts verified','targets':[],'context_sources':context}
    rows=[];status=Counter();all_sources={}
    for t in stage['targets']:
        r=results[t['target_id']];review=reviews.get(t['target_id'],{'status':r['status'],'reason':r['reason'],'accepted_evidence':[],'unverified_fields':['entity_and_period_match'],'conflicts':[]})
        status[review['status']]+=1
        record={'input':t,'raw_result':r,'match_review':review};manifest['targets'].append(record)
        pool={source_key(s):s for s in r['sources']+context};all_sources.update(pool)
        for ev in review.get('accepted_evidence',[]):
            s=pool[ev['source_key']]
            rows.append({'target_id':t['target_id'],'phase':t['phase'],'input_observation_id':t['input_observation_id'],'label':t['label'],'status':review['status'],
                'page_id':s['page_id'],'revision_id':s['revision_id'],'revision_timestamp':s['revision_timestamp'],'title':s['resolved_title'],'revision_url':s['revision_url'],'retrieved_at':s['response']['retrieved_at'],'raw_path':s['response']['path'],'raw_sha256':s['response']['sha256'],'license':s['license'],**ev})
        if not review.get('accepted_evidence'):rows.append({'target_id':t['target_id'],'phase':t['phase'],'input_observation_id':t['input_observation_id'],'label':t['label'],'status':review['status'],'reason':review['reason']})
        title=t['label']+' — '+t['phase']+' NQ202/2025'
        front='---\nokf_version: "0.2"\ntype: evidence_report\ntitle: '+json.dumps(title,ensure_ascii=False)+'\nupdated: "'+now()[:10]+'"\nstatus: '+review['status']+'\n---\n\n# '+title+'\n\n'
        text=front+'## Tham chiếu input (không phải khẳng định của Wikipedia)\n\n'+json.dumps(t,ensure_ascii=False,indent=2).join(['```json\n','\n```\n'])
        text+='\n## Kết quả RAW\n\n'+review['reason']+'\n\nKhông ghi vào INF; ID quan sát, bài và revision được giữ riêng.\n'
        text+='\n## Bằng chứng Wikipedia đã chọn\n'
        for e in review.get('accepted_evidence',[]):
            s=pool[e['source_key']]
            text+='\n### '+e['claim_scope']+'\n\n['+s['resolved_title']+' — revision '+s['revision_id']+']('+s['revision_url']+') · dòng '+str(e['line_start'])+'–'+str(e['line_end'])+' · revision timestamp '+s['revision_timestamp']+'\n\n```wikitext\n'+e['excerpt_wikitext']+'\n```\n'
        text+='\n## Mâu thuẫn và chưa xác minh\n\n'+ '\n'.join('- '+x for x in review.get('conflicts',[])+review.get('unverified_fields',[]))+'\n'
        text+='\n## Nguồn và ghi công\n\nWikipedia tiếng Việt contributors, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Bản gốc và checksum trong manifest; trích đoạn giữ nguyên wikicode, lời nhận xét do RAW biên soạn.\n'
        atomic(root/'targets'/t['target_id']/'index.md',text.encode())
    manifest['counts']={'targets':len(manifest['targets']),'before':63,'after':34,'status':dict(status),'unique_retrieved_pages':len({s['page_id'] for s in all_sources.values()}),'unique_retrieved_revisions':len(all_sources),'selected_pages':len({x['page_id'] for x in rows if 'page_id' in x}),'selected_revisions':len({(x['page_id'],x['revision_id']) for x in rows if 'page_id' in x})}
    put_json(root/'manifest.json',manifest)
    atomic(root/'target-page-revision-evidence.jsonl',b''.join((json.dumps(row,ensure_ascii=False)+'\n').encode() for row in rows))
    fields=['target_id','phase','input_observation_id','label','status','page_id','revision_id','revision_timestamp','title','revision_url','retrieved_at','raw_path','raw_sha256','license','claim_scope','line_start','line_end','excerpt_wikitext','reason']
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows);atomic(root/'target-page-revision-evidence.csv',stream.getvalue().encode('utf-8-sig'))
    return manifest

def inventory(root):
    files=[]
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='checksums.json':
            b=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':sha(b)})
    put_json(root/'checksums.json',{'algorithm':'SHA-256','excludes':['checksums.json'],'files':files})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('--pilot',action='store_true');p.add_argument('--inventory',action='store_true');p.add_argument('--export',action='store_true');args=p.parse_args()
    if args.export:export(args.package)
    print(json.dumps(validate(args.package,args.pilot,args.inventory),ensure_ascii=False,indent=2))
