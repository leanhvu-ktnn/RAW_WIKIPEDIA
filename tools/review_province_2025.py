#!/usr/bin/env python3
"""Conservative evidence proposals; does not resolve or write canonical INF identities."""
import argparse
import re
from pathlib import Path
try:
    from tools.crawl_province_2025 import read_json,put_json,short
    from tools.province_package import source_key
except ModuleNotFoundError:
    from crawl_province_2025 import read_json,put_json,short
    from province_package import source_key

def plain(text):
    return re.sub(r'\[\[([^]|]+)\|([^]]+)\]\]',r'\2',text).replace('[[','').replace(']]','').replace("'''",'')
def ref(root,source,start,end,scope):
    lines=(root/source['wikitext_path']).read_text().splitlines()
    return {'source_key':source_key(source),'line_start':start,'line_end':end,'claim_scope':scope,'excerpt_wikitext':'\n'.join(lines[start-1:end])}
def norm(x):return plain(x).casefold().replace('hoà','hòa').replace('thuỷ','thủy').replace('–','-').replace('—','-')

def propose(root,target,result,context,subjects):
    if result['status'] in ('error','not_found'):
        return {'status':result['status'],'reason':result['reason'],'accepted_evidence':[],'unverified_fields':['Wikipedia source not obtained'],'conflicts':[]}
    sources=result['sources'];name=target['search_name'];city=target['label'].casefold().startswith('thành phố')
    primary=None;lead=None;rejected=[]
    ordered=sorted(sources,key=lambda s:0 if s['selection_cutoff'] else 1)
    for s in ordered:
        if s.get('related_event_source'):continue
        lines=(root/s['wikitext_path']).read_text().splitlines()
        for index,line in enumerate(lines[:350]):
            txt=norm(line)
            if not re.match(r'\s*(?:tỉnh |thành phố )?'+re.escape(norm(name))+r'.{0,200}?\blà\b',txt,re.I):continue
            if city and 'thành phố trực thuộc trung ương' not in txt:continue
            if not city and not re.search(r'\blà (?:một )?tỉnh\b',txt,re.I):continue
            if re.search(r'là (?:một )?tỉnh[^.]{0,160}trung quốc',txt):continue
            primary=s;lead=ref(root,s,index+1,index+1,'name_type');break
        if primary:break
    accepted=[lead] if lead else []
    period=[];conflicts=[];unverified=[]
    if target['input_events']:
        event=target['input_events'][0]
        names=[short(subjects[x]['label']) for x in event['predecessor_observation_ids']+event['successor_observation_ids']]
        # Current historical section or pinned 2025 text may support an event; timestamp alone never does.
        event_sources=sorted(sources,key=lambda s:0 if (s['selection_cutoff'] and target['phase']=='after') else 1)
        for s in event_sources:
            lines=(root/s['wikitext_path']).read_text().splitlines()
            for i,line in enumerate(lines):
                if line.startswith('|'):continue
                text=norm(line)
                if not ('2025' in text and re.search(r'sáp nhập|hợp nhất|sắp xếp',text)):continue
                # Include adjacent paragraph lines when a sentence refers to "tỉnh" instead of its name.
                start=max(0,i-2);end=min(len(lines),i+4);block='\n'.join(lines[start:end]);n=norm(block)
                if all(norm(x) in n for x in names) and '202/2025' in n:
                    period=[ref(root,s,start+1,end,'reorganization')];break
            if period:break
        if period:
            conflicts.append('Bằng chứng Wikipedia được lưu nguyên văn; cách nói sáp nhập vào không được dùng để đồng nhất tiền thân với tỉnh mới theo input.')
        else:unverified.append('Chưa tìm được đoạn Wikipedia vừa nêu NQ202/2025 vừa bao phủ các tiền thân/kế thừa trong input.')
    else:
        for s in context:
            lines=(root/s['wikitext_path']).read_text().splitlines()
            heading=next((i for i,l in enumerate(lines) if 'không thực hiện sáp nhập' in l),None)
            if heading is not None:
                match=next((i for i in range(heading+1,min(heading+20,len(lines))) if norm(name) in norm(lines[i])),None)
                if match is not None:
                    period=[ref(root,s,heading+1,match+1,'unchanged_in_2025')];break
        unverified.append('Không tự suy legal_effective_on/operational_on riêng cho địa bàn không sắp xếp; input không có event riêng.')
    if period:accepted+=period
    valid=bool(lead and period)
    if primary and not primary['selection_cutoff']:
        unverified.append('Chưa lấy được revision nền trong năm 2025; chỉ có nguồn hiện tại với lịch sử, cần thẩm tra phạm vi thời kỳ.')
        # A current article is permissible only if it explicitly speaks of the historical period.
        if target['phase']=='before' and not ('cũ' in norm(lead['excerpt_wikitext']) or '2025' in norm(lead['excerpt_wikitext'])):valid=False
    for s in sources:
        if primary and s['page_id']!=primary['page_id']:
            rejected.append({'page_id':s['page_id'],'title':s['resolved_title'],'reason':'Không chọn làm bài nhận diện target: cần kiểm tra khác loại/thời kỳ; vẫn giữ bytes để audit.'})
    unverified.extend(['Không chứng nhận hiện trạng tại ngày crawl.','Chưa kiểm chứng độc lập nội dung pháp lý của các URL Wikipedia dẫn.','Ngày hiệu lực và ngày vận hành chỉ được INF cung cấp/đoạn nguồn nêu; không suy từ revision timestamp.'])
    return {'status':'found' if valid else 'ambiguous','review_method':'conservative content-rule review; not legal authority adjudication',
        'reason':'Có bằng chứng tên/loại và đoạn quan hệ năm 2025; lưu cho INF đối chiếu, không canonical hóa.' if valid else 'Đã lưu nguồn nhưng chưa đủ bằng chứng tên/loại và thời kỳ để chọn cho target.',
        'accepted_evidence':accepted,'primary_source_key':source_key(primary) if primary else None,'conflicts':conflicts,'unverified_fields':unverified,'rejected_candidates':rejected}

def run(root):
    stage=read_json(root/'staging.json');results=read_json(root/'checkpoint.json')['results'];context=read_json(root/'context-sources.json')
    subjects={s['inf_id']:s for s in read_json(root/stage['source']['file'])['subjects']}
    reviews=read_json(root/'reviews.json') if (root/'reviews.json').exists() else {}
    for target in stage['targets']:
        tid=target['target_id']
        if tid in results and target['input_events']:
            ids=set()
            for event in target['input_events']:
                ids.update(event['predecessor_observation_ids']+event['successor_observation_ids'])
            existing={source_key(s) for s in results[tid]['sources']}
            for other in results.values():
                if other['input_observation_id'] not in ids:continue
                for src in list(other['sources']):
                    if source_key(src) not in existing and not src.get('related_event_source'):
                        related=dict(src);related['related_event_source']=True
                        results[tid]['sources'].append(related);existing.add(source_key(src))
        
        if tid not in results:continue
        if reviews.get(tid,{}).get('review_method','').startswith('manual'):continue
        reviews[tid]=propose(root,target,results[tid],context,subjects)
    put_json(root/'reviews.json',reviews)
    checkpoint=read_json(root/'checkpoint.json');checkpoint['results']=results;put_json(root/'checkpoint.json',checkpoint)
    for target in stage['targets']:
        if target['target_id'] in reviews:
            v=reviews[target['target_id']];print(target['phase'],target['label'],v['status'],v.get('primary_source_key','manual'))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);run(p.parse_args().package)
