#!/usr/bin/env python3
"""Assemble reports and provenance graph, then validate every package file before completion."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
try:
    from tools.crawl_province_2025 import read_json,put_json,atomic,sha,now
    from tools.province_package import source_key,validate,export,inventory
    from tools.review_province_2025 import plain
except ModuleNotFoundError:
    from crawl_province_2025 import read_json,put_json,atomic,sha,now
    from province_package import source_key,validate,export,inventory
    from review_province_2025 import plain


def enhance_reviews(root):
    stage=read_json(root/'staging.json');cp=read_json(root/'checkpoint.json');reviews=read_json(root/'reviews.json')
    for t in stage['targets']:
        v=reviews[t['target_id']];r=cp['results'][t['target_id']]
        refs=v.get('accepted_evidence',[])
        cited=set();dates=[]
        for e in refs:
            clean=plain(re.sub(r'<ref\b[^>]*>.*?</ref>|<ref[^>]*/>','',e['excerpt_wikitext'],flags=re.S|re.I))
            cited.update(re.findall(r'\b\d{1,4}/\d{4}/QH\d+\b',e['excerpt_wikitext']))
            if '202/2025' in clean and re.search(r'hiệu lực|hoạt động|vận hành',clean,re.I):
                dates.append({'source_key':e['source_key'],'line_start':e['line_start'],'line_end':e['line_end'],'text_as_stated':clean,'verification':'Wikipedia statement only; separate from input legal/operational dates'})
                if re.search(r'hiệu lực.{0,80}(?:1 tháng 7|01/07|1/7)',clean,re.I):
                    note='Đoạn Wikipedia có cách ghi hiệu lực 01/07/2025; input event ghi hiệu lực 12/06/2025 và vận hành 01/07/2025. Cần INF phân xử, không sửa nguồn.'
                    if note not in v['conflicts']:v['conflicts'].append(note)
        v['wikipedia_cited_documents']=sorted(cited)
        v['wikipedia_date_statements']=dates
        if not dates:v['unverified_fields'].append('Chưa có câu Wikipedia được chọn xác nhận rõ hai loại ngày hiệu lực/vận hành riêng biệt.')
        if not cited:v['unverified_fields'].append('Chưa có văn bản NQ202 được bài/trích đoạn đã chọn dẫn trực tiếp; nguồn nghị quyết nằm ở input, không gán cho Wikipedia.')
        # Stable, unique notes on repeated finalize.
        v['unverified_fields']=list(dict.fromkeys(v['unverified_fields']))
        v['conflicts']=list(dict.fromkeys(v['conflicts']))
    put_json(root/'reviews.json',reviews)


def graph_export(root,manifest):
    wiki=Namespace('https://github.com/leanhvu-ktnn/RAW_WIKIPEDIA/ontology#');g=Graph();g.bind('wiki',wiki)
    for row in manifest['targets']:
        t=row['input'];review=row['match_review'];target=URIRef('urn:raw-wikipedia:nq202:'+t['target_id'])
        g.add((target,RDF.type,wiki.ObservationTarget));g.add((target,wiki.inputObservationId,Literal(t['input_observation_id'])));g.add((target,wiki.phase,Literal(t['phase'])));g.add((target,wiki.inputSha256,Literal(manifest['input']['sha256'])))
        for e in review.get('accepted_evidence',[]):
            pid,rid=e['source_key'].split('/');page=URIRef('urn:viwiki:page:'+pid);rev=URIRef('urn:viwiki:revision:'+rid)
            ex=URIRef('urn:raw-wikipedia:excerpt:'+sha((e['source_key']+':'+str(e['line_start'])+':'+str(e['line_end'])).encode()))
            g.add((page,RDF.type,wiki.Page));g.add((page,wiki.pageId,Literal(pid)));g.add((page,wiki.hasRevision,rev));g.add((rev,RDF.type,wiki.Revision));g.add((rev,wiki.oldid,Literal(rid)))
            g.add((target,wiki.supportedBy,ex));g.add((ex,RDF.type,wiki.EvidenceExcerpt));g.add((ex,wiki.excerptRevision,rev));g.add((ex,wiki.lineStart,Literal(e['line_start'],datatype=XSD.positiveInteger)));g.add((ex,wiki.lineEnd,Literal(e['line_end'],datatype=XSD.positiveInteger)));g.add((ex,wiki.excerptText,Literal(e['excerpt_wikitext'],lang='vi')))
    atomic(root/'provenance.ttl',g.serialize(format='turtle').encode())
    Graph().parse(root/'provenance.ttl',format='turtle')
    return len(g)


def report(root,manifest,validation,triples):
    counts=manifest['counts'];issues=[]
    for row in manifest['targets']:
        r=row['match_review'];t=row['input']
        issues.append({'target_id':t['target_id'],'phase':t['phase'],'label':t['label'],'status':r['status'],'conflicts':r['conflicts'],'unverified_fields':r['unverified_fields'],'cited_documents_from_wikipedia':r.get('wikipedia_cited_documents',[])})
    put_json(root/'issues.json',issues)
    table=['| Mốc | Target | Trạng thái | Nguồn đã chọn (page/revision) |','|---|---|---|---|']
    for row in manifest['targets']:
        t=row['input'];v=row['match_review'];keys=sorted({e['source_key'] for e in v['accepted_evidence']})
        table.append(f"| {t['phase']} | [{t['label']}](targets/{t['target_id']}/index.md) | {v['status']} | {', '.join(keys)} |")
    missing_n=sum(bool(i['unverified_fields']) for i in issues)
    text='''---
okf_version: "0.2"
type: report
title: "Wikipedia đối chiếu 63 tỉnh trước / 34 tỉnh sau NQ202/2025"
updated: "'''+now()[:10]+'''"
status: completed_with_open_verification_items
---

# Gói đối chiếu tỉnh trước và sau NQ202/2025

Gói RAW đã kiểm tra nguồn/checksum cho toàn bộ target. **Hoàn tất thu thập và đóng gói không có nghĩa tất cả phát biểu Wikipedia đúng pháp lý hoặc INF đã duyệt.** Không ghi vào INF, không tạo ID INF, không thay thế danh mục chuẩn.

## Kết quả đếm riêng

'''+json.dumps(counts,ensure_ascii=False,indent=2).join(['```json\n','\n```\n'])+f'''
- Có 97 kết quả target (63 trước + 34 sau), giữ hai mốc độc lập kể cả trùng pageid/QID/ID quan sát.
- Số bài/revision đã tải bao gồm ứng viên bị loại và bài bối cảnh; số selected_pages/selected_revisions chỉ đếm nguồn dùng làm bằng chứng.
- {triples} triple RDF provenance; không ascribe legal:DiaBan cho ID quan sát INF.
- {missing_n} target còn trường cần INF xác minh. Chi tiết [issues.json](issues.json).

## Danh mục input và thời gian

Bản sao input: [JSON nguyên bản](input/province-before-after-2025.json). SHA-256: `{manifest['input']['sha256']}`. Input không khai báo version; sử dụng checksum như phiên bản nội dung, không bịa version của INF. Checksum PDF là metadata do input cung cấp, không phải một lần RAW tải/kiểm tra lại PDF.

Ngày hiệu lực 12/06/2025 và vận hành 01/07/2025 lấy từ input events; metadata input_subject/input_events giữ nguyên. Những địa bàn không sắp xếp không được gán một event hợp nhất giả. Revision_timestamp, retrieved_at và ngày pháp lý là các trường riêng. Ngày chọn revision chỉ thu hẹp tìm kiếm; thời kỳ được đối chiếu bằng nội dung và trích đoạn riêng.

Hai tập năm 2025 không được coi là hiện trạng ngày crawl. Bài năm 2026 có thông tin khác baseline; phần đó chỉ là nguồn lịch sử bổ sung, không ghi đè baseline.

## Pilot và phương pháp

[Pilot validation](pilot-validation.json) xác nhận 5 target Gia Lai cũ, Bình Định cũ, Gia Lai mới và Hà Nội hai mốc. Pilot được đọc trích đoạn trực tiếp; lượt toàn bộ sử dụng quy tắc tên/loại + quan hệ NQ202, bổ sung bài tiền thân/kế thừa khi một bài không nêu đủ, rồi kiểm tra các trường hợp bất thường. Không có benchmark chứng nhận entity linking hoàn hảo.

Bản gốc response API và wikitext revision được giữ, có cache/checkpoint. Redirect và title đã tìm nằm trong raw_result.discovery; bài liên quan là source bổ sung, không biến thành một target mới. Bản Hà Nam của Trung Quốc, Hà Nội tỉnh thế kỷ XIX và các ứng viên không đúng mốc được giữ làm dấu vết, không chọn làm nhận diện target.

## Mâu thuẫn đáng chú ý

- Bình Định: phần mô tả tồn tại đến 01/07 và infobox giải thể 12/06; không trộn hai mốc.
- Vĩnh Phúc và một số bài dùng cách ghi hiệu lực 01/07, khác ngày hiệu lực trong input. Các đoạn cụ thể được giữ trong review/issue.
- Gia Lai: diễn đạt “sáp nhập vào” không đồng nghĩa tỉnh cũ tồn tại như cùng identity tỉnh mới. Bài hiện tại còn có citation NQ1668 với tiêu đề Cần Thơ trong đoạn Gia Lai; không dùng làm chứng cứ cấp tỉnh.
- Bà Rịa–Vũng Tàu: đoạn hiện tại ghi giai đoạn từ 1991 đến 1976, tự mâu thuẫn thời gian; không dùng câu này làm chronology pháp lý.
- Bài bối cảnh có phần dự kiến tháng 4/2025 và cập nhật 2026; chỉ dùng đúng đoạn không sắp xếp năm 2025, không coi toàn bài là nghị quyết có hiệu lực.

## Tệp để INF đọc

- [Manifest](manifest.json): input, kết quả nguồn, review, conflict và unresolved fields theo từng target.
- [Target–page–revision–evidence JSONL](target-page-revision-evidence.jsonl) / [CSV](target-page-revision-evidence.csv): mỗi dòng bằng chứng gắn target và revision; một target có thể nhiều dòng.
- [RDF provenance](provenance.ttl); [kiểm định](validation.json); [checksum toàn gói](checksums.json).
- [Checkpoint](checkpoint.json), [quyết định đối sánh](reviews.json), [giấy phép từ API](license-source.json).

## Việc còn thiếu

INF cần tự phân xử canonical identity và các mâu thuẫn pháp lý, kiểm chứng văn bản Wikipedia dẫn; RAW không thực hiện nhập INF. Thông tin diện tích/dân số, website, tính đúng tất cả reference hoặc hiện trạng 2026 không được chứng nhận. Hợp đồng 0.1.0 chưa biểu diễn ID quan sát và many-to-many theo thời kỳ: sử dụng staging có phiên bản, không ép kiểu ID. Không tải ảnh/media; giấy phép media không suy từ giấy phép văn bản.

## Ghi công và tái lập

Wikipedia tiếng Việt contributors; [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Mỗi nguồn có revision URL và contributor history URL. Trích đoạn là wikicode nguyên văn; Markdown báo cáo là dẫn xuất của RAW.

Từ root RAW_WIKIPEDIA, kiểm tra lại:

```bash
.venv/bin/python tools/province_package.py packages/province-before-after-2025 --inventory
```

Kết quả “PASS” xác nhận phạm vi và toàn vẹn file/bytes theo quy tắc kiểm định; không phải phê duyệt của INF.

## Danh sách target

'''+ '\n'.join(table)+'\n'
    atomic(root/'report.md',text.encode())
    atomic(root/'index.md',('---\nokf_version: "0.2"\ntype: index\ntitle: "Gói tỉnh trước sau 2025"\nupdated: "'+now()[:10]+'"\nstatus: active\n---\n\n# Gói tỉnh trước/sau 2025\n\n[Đọc báo cáo](report.md) · [Manifest](manifest.json) · [Kiểm định](validation.json) · [Checksum](checksums.json)\n').encode())


def finalize(root):
    enhance_reviews(root)
    result=validate(root)
    manifest=export(root)
    triples=graph_export(root,manifest)
    report(root,manifest,result,triples)
    put_json(root/'validation.json',result)
    # All files except this inventory are included, including the saved validation result.
    inventory(root)
    final=validate(root,inventory=True)
    print(json.dumps(final,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);finalize(p.parse_args().package)
