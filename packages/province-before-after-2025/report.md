---
okf_version: "0.2"
type: report
title: "Wikipedia đối chiếu 63 tỉnh trước / 34 tỉnh sau NQ202/2025"
updated: "2026-09-29"
status: completed_with_open_verification_items
---

# Gói đối chiếu tỉnh trước và sau NQ202/2025

Gói RAW đã kiểm tra nguồn/checksum cho toàn bộ target. **Hoàn tất thu thập và đóng gói không có nghĩa tất cả phát biểu Wikipedia đúng pháp lý hoặc INF đã duyệt.** Không ghi vào INF, không tạo ID INF, không thay thế danh mục chuẩn.

## Kết quả đếm riêng

```json
{
  "targets": 97,
  "before": 63,
  "after": 34,
  "status": {
    "found": 97
  },
  "unique_retrieved_pages": 68,
  "unique_retrieved_revisions": 169,
  "selected_pages": 64,
  "selected_revisions": 149
}
```

- Có 97 kết quả target (63 trước + 34 sau), giữ hai mốc độc lập kể cả trùng pageid/QID/ID quan sát.
- Số bài/revision đã tải bao gồm ứng viên bị loại và bài bối cảnh; số selected_pages/selected_revisions chỉ đếm nguồn dùng làm bằng chứng.
- 2080 triple RDF provenance; không ascribe legal:DiaBan cho ID quan sát INF.
- 97 target còn trường cần INF xác minh. Chi tiết [issues.json](issues.json).

## Danh mục input và thời gian

Bản sao input: [JSON nguyên bản](input/province-before-after-2025.json). SHA-256: `b70c2ab311adcee3fca2963b21a49f00c32966f595bea57b433fe8b00e24751d`. Input không khai báo version; sử dụng checksum như phiên bản nội dung, không bịa version của INF. Checksum PDF là metadata do input cung cấp, không phải một lần RAW tải/kiểm tra lại PDF.

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

| Mốc | Target | Trạng thái | Nguồn đã chọn (page/revision) |
|---|---|---|---|
| before | [tỉnh Hà Giang](targets/before-3e293464-98e1-47b3-8125-cd71a01b0af5/index.md) | found | 67/73446368, 67/75583460 |
| before | [tỉnh Tuyên Quang](targets/before-504ffb57-8afc-46ea-afd6-bd825c3d9d0b/index.md) | found | 705/73422454, 705/75495326 |
| before | [tỉnh Yên Bái](targets/before-dc197b73-16aa-4db6-b728-2fd93c6e0e17/index.md) | found | 997/73401358, 997/75593504 |
| before | [tỉnh Lào Cai](targets/before-2c7ffbab-578a-46fc-86a1-3df5a0c2b377/index.md) | found | 44/73401357, 44/75592493 |
| before | [tỉnh Bắc Kạn](targets/before-ba1a543d-db36-4550-961c-6311b68a98af/index.md) | found | 670/73467962, 670/75590858 |
| before | [tỉnh Thái Nguyên](targets/before-f5be51da-1df9-4f18-8b04-5f367ce190fe/index.md) | found | 10732/73432400, 10732/75597969 |
| before | [tỉnh Vĩnh Phúc](targets/before-66b2e551-e8af-4c1b-aa8d-1634ff03f566/index.md) | found | 4172/73562076, 4172/75593497, 9249/75583465 |
| before | [tỉnh Hòa Bình](targets/before-8ebca2ae-5502-4e32-839c-7bd9f50e5d83/index.md) | found | 9249/73577368, 9249/75583465 |
| before | [tỉnh Phú Thọ](targets/before-a0825807-89c5-45bb-bfc0-6059722cc206/index.md) | found | 3970/73471339, 3970/75590415 |
| before | [tỉnh Bắc Giang](targets/before-f7449735-fedd-4c6e-94e5-f59fb2f0866a/index.md) | found | 10885/73577778, 10885/75593850 |
| before | [tỉnh Bắc Ninh](targets/before-4180ccfc-0109-4876-a40e-6dffca08c1eb/index.md) | found | 4669/73561752, 4669/75598300 |
| before | [tỉnh Thái Bình](targets/before-f0e93617-5e31-42f8-b849-a2a65802cb5f/index.md) | found | 4755/73564844, 4755/75583552 |
| before | [tỉnh Hưng Yên](targets/before-210f2492-7de4-4501-9f50-b3dc57735fe4/index.md) | found | 4666/73542650, 4666/75597544 |
| before | [thành phố Hải Phòng](targets/before-99a27e9e-b6cd-42c6-a366-3940454fe014/index.md) | found | 362339/73542147, 362339/75597922 |
| before | [tỉnh Hải Dương](targets/before-92302357-30b6-4f7e-8f3e-9447c03ca4a8/index.md) | found | 2171/73542781, 2171/75586396 |
| before | [tỉnh Hà Nam](targets/before-d23772ed-9d1e-4671-9a72-1bdd61bb7aec/index.md) | found | 3943/73426010, 3943/75589428 |
| before | [tỉnh Nam Định](targets/before-c7c04e40-92fc-4729-9a51-07905ff41f71/index.md) | found | 4759/73579200, 4759/75592868 |
| before | [tỉnh Ninh Bình](targets/before-315fb257-8efa-4dd9-903c-8ab863ed267a/index.md) | found | 4769/73579065, 4769/75584626 |
| before | [tỉnh Quảng Bình](targets/before-2400e0b3-1336-492c-9314-b130271de54e/index.md) | found | 11252/73467877, 11252/75583498 |
| before | [tỉnh Quảng Trị](targets/before-008d4d64-6e0a-4ee9-baa0-b94aa903cf69/index.md) | found | 6500/73542163, 6500/75598560 |
| before | [thành phố Đà Nẵng](targets/before-0f3c29bb-1697-4473-93bc-57cf0bd75b8f/index.md) | found | 999/73545080, 999/75572754 |
| before | [tỉnh Quảng Nam](targets/before-d1405a58-a656-4515-a3b9-7a6bf698601b/index.md) | found | 1328/73498686, 1328/75596545 |
| before | [tỉnh Kon Tum](targets/before-b3f479fe-ef82-49bd-b7e5-f12955f58450/index.md) | found | 11200/73549059, 11200/75583441 |
| before | [tỉnh Quảng Ngãi](targets/before-6b88788a-d98c-4b2f-95c1-fe0db56e737e/index.md) | found | 11249/73479186, 11249/75579250 |
| before | [tỉnh Bình Định](targets/before-b43098d0-f25d-410f-ac08-760408dda032/index.md) | found | 11189/73514115, 11189/75583543 |
| before | [tỉnh Gia Lai](targets/before-d6fba89f-0084-4883-b4dd-0c4a4012780d/index.md) | found | 11165/73563669, 11165/75598956 |
| before | [tỉnh Ninh Thuận](targets/before-db0553c5-a89f-4616-9053-cb5c725846ec/index.md) | found | 11205/72105645, 11205/75583444 |
| before | [tỉnh Khánh Hòa](targets/before-149a9569-bdfa-4472-9d70-98500bd61bfb/index.md) | found | 2764/73485374, 2764/75580535 |
| before | [tỉnh Đắk Nông](targets/before-a75cdf18-847d-4f99-8780-77d7d02a9b8a/index.md) | found | 30614/73467978, 30614/75583443 |
| before | [tỉnh Bình Thuận](targets/before-b79cd411-11c3-4c73-b7ff-1fe6fa1f318c/index.md) | found | 11193/73438589, 11193/75583538 |
| before | [tỉnh Lâm Đồng](targets/before-bdd0ffed-6d5c-42f5-b7d4-48ef3bc80dee/index.md) | found | 11203/73486427, 11203/75577843 |
| before | [tỉnh Phú Yên](targets/before-b94949cd-4602-44e1-bf74-4c435939187e/index.md) | found | 11254/73471344, 11254/75583496 |
| before | [tỉnh Đắk Lắk](targets/before-f63954a1-bd8a-404b-bd43-4d9a3d82c359/index.md) | found | 11195/73562966, 11195/75592941 |
| before | [Thành phố Hồ Chí Minh](targets/before-d0eb00f7-20a7-4b13-988a-f2181a7cea65/index.md) | found | 39/73494086, 39/75588539 |
| before | [tỉnh Bà Rịa - Vũng Tàu](targets/before-e4824342-5c8a-4edc-88eb-c79ea20ec6b9/index.md) | found | 5612/73531970, 5612/75581918 |
| before | [tỉnh Bình Dương](targets/before-9df78c95-439a-4880-87d7-c9a663ce4e17/index.md) | found | 11191/73495743, 11191/75583566 |
| before | [tỉnh Bình Phước](targets/before-b961765f-124d-462d-ac0d-831c6f69e78e/index.md) | found | 11192/72710293, 11192/75583500 |
| before | [tỉnh Đồng Nai](targets/before-700552bc-037d-4910-adc0-1e1d89f35f97/index.md) | found | 1275/73546286, 1275/75591377 |
| before | [tỉnh Long An](targets/before-3a09825a-7bec-427b-bb2b-fc8b2a0bcbdd/index.md) | found | 11204/73566420, 11204/75583544 |
| before | [tỉnh Tây Ninh](targets/before-69bd5e27-42ca-4860-994f-2168f3cf00f1/index.md) | found | 11253/73496604, 11253/75569181 |
| before | [thành phố Cần Thơ](targets/before-911b3735-1a84-4c5e-8abc-ee3b8b8c8d60/index.md) | found | 1022/73467889, 1022/75583922 |
| before | [tỉnh Sóc Trăng](targets/before-0833216b-21e1-4072-8e44-ea80a196bdf6/index.md) | found | 1022/75583922, 11248/73467928 |
| before | [tỉnh Hậu Giang](targets/before-8bcbdce6-2fec-4a16-b879-204d2e6d327c/index.md) | found | 11198/73467974, 11198/75593634 |
| before | [tỉnh Bến Tre](targets/before-d5aa2846-2183-496b-b66f-f23d9f5a8f9a/index.md) | found | 11188/73411754, 11188/75597725 |
| before | [tỉnh Trà Vinh](targets/before-cd3fb4df-124b-475d-be16-f67d36d767d5/index.md) | found | 11247/73560367, 11247/75583499 |
| before | [tỉnh Vĩnh Long](targets/before-31f72a00-09b7-4c82-b5c1-8af4ab0a60d2/index.md) | found | 11232/73579938, 11232/75581713 |
| before | [tỉnh Tiền Giang](targets/before-804585e0-701c-4f26-9c83-5a49b167e4df/index.md) | found | 5454/73401375, 5454/75590370 |
| before | [tỉnh Đồng Tháp](targets/before-b19a826b-361d-471a-b453-2af4d403cb8d/index.md) | found | 11197/73467906, 11197/75599205 |
| before | [tỉnh Bạc Liêu](targets/before-ff4d961e-2632-4874-8b8a-8b56e6803eb8/index.md) | found | 11187/73467945, 11187/75593630 |
| before | [tỉnh Cà Mau](targets/before-e5fb7371-5cf0-4c77-85bb-e337abdc08f0/index.md) | found | 11194/73421893, 11194/75588225 |
| before | [tỉnh Kiên Giang](targets/before-2831355d-4a59-452e-a5c3-f80a68d931fb/index.md) | found | 11199/73497809, 11199/75583553 |
| before | [tỉnh An Giang](targets/before-0daad321-c6c1-49ca-82df-d925d2fb4299/index.md) | found | 3972/73498291, 3972/75593858 |
| before | [tỉnh Cao Bằng](targets/before-06a054f2-be7a-4902-b601-1ff6e081136c/index.md) | found | 19920857/75595156, 68/73467902 |
| before | [tỉnh Điện Biên](targets/before-886684a1-1e22-4c0b-b6d0-f45602ddae7c/index.md) | found | 19920857/75595156, 7322/73484929 |
| before | [tỉnh Hà Tĩnh](targets/before-f2fecb5e-11a8-4cb2-97f7-a089ac0ecf79/index.md) | found | 11181/73471350, 19920857/75595156 |
| before | [tỉnh Lai Châu](targets/before-0552144d-8f63-4d7f-ab23-262e100fa112/index.md) | found | 11202/73467944, 19920857/75595156 |
| before | [tỉnh Lạng Sơn](targets/before-9c0ae658-883a-41b7-8de3-8e5a08bc6177/index.md) | found | 19920857/75595156, 671/73471336 |
| before | [tỉnh Nghệ An](targets/before-d6fd8782-80d8-4d91-986c-254bf2e05ec3/index.md) | found | 19920857/75595156, 99282/73561333 |
| before | [tỉnh Quảng Ninh](targets/before-651dfe5c-8dd5-49b4-9bd4-a04148a79ed2/index.md) | found | 19920857/75595156, 5393/73417590 |
| before | [tỉnh Thanh Hóa](targets/before-fbc7cbac-5f23-48a5-a8a4-ab4d2902c2ba/index.md) | found | 19920857/75595156, 3203766/73453626 |
| before | [tỉnh Sơn La](targets/before-3013985e-02d9-45ff-8e7d-c22c53fd39ed/index.md) | found | 19920857/75595156, 9252/73467913 |
| before | [thành phố Hà Nội](targets/before-9d6837cd-1196-4073-bb43-85a7ee0cc8e5/index.md) | found | 19920857/75595156, 80/73509990 |
| before | [thành phố Huế](targets/before-c19ff93f-bc7c-4941-908b-1d7dadd26c84/index.md) | found | 11244/73541666, 19920857/75595156 |
| after | [tỉnh Tuyên Quang](targets/after-54ada0d0-c554-433d-abe0-8ea0929d2f0d/index.md) | found | 705/73651746 |
| after | [tỉnh Lào Cai](targets/after-e8f5d888-ee8c-4036-9a83-952367d5668c/index.md) | found | 44/73652032 |
| after | [tỉnh Thái Nguyên](targets/after-fdb66544-727f-43ff-877a-511e3651142b/index.md) | found | 10732/73645746 |
| after | [tỉnh Phú Thọ](targets/after-1382c005-17ce-4d0a-9b74-228aafee4e73/index.md) | found | 3970/73649976 |
| after | [tỉnh Bắc Ninh](targets/after-140dd32d-ef0e-4309-8fc6-6c3db73e19d1/index.md) | found | 4669/73651296 |
| after | [tỉnh Hưng Yên](targets/after-69bfada8-8d5a-4494-b4a5-06d9d6a4678f/index.md) | found | 4666/73652072 |
| after | [thành phố Hải Phòng](targets/after-8440de11-9955-43c0-bb4b-52a400cb49ef/index.md) | found | 362339/73649173 |
| after | [tỉnh Ninh Bình](targets/after-8ef013e4-5652-494a-83e0-6336809da66c/index.md) | found | 4769/73644011 |
| after | [tỉnh Quảng Trị](targets/after-39a615da-cad1-42ce-b5e0-dede80a3524e/index.md) | found | 6500/73650037 |
| after | [thành phố Đà Nẵng](targets/after-3fe520e0-442b-47ad-bb5c-773359b64a2f/index.md) | found | 999/73651635 |
| after | [tỉnh Quảng Ngãi](targets/after-ffa329b1-2301-4d14-9a51-26002353068e/index.md) | found | 11249/73637895 |
| after | [tỉnh Gia Lai](targets/after-01f21d1a-e83c-4043-ab0c-ab72d8c47f2f/index.md) | found | 11165/73646444 |
| after | [tỉnh Khánh Hòa](targets/after-0561c911-7b42-478c-b230-33e6249b65e3/index.md) | found | 2764/73637060 |
| after | [tỉnh Lâm Đồng](targets/after-d1e3973c-16fd-4e9f-acd8-4724176fbcae/index.md) | found | 11203/73648221 |
| after | [tỉnh Đắk Lắk](targets/after-bcffd08e-12a7-4e9c-b744-317d81aeb51a/index.md) | found | 11195/73640352 |
| after | [Thành phố Hồ Chí Minh](targets/after-99de8263-bc71-4bce-9d69-50364c38af02/index.md) | found | 39/73652156 |
| after | [tỉnh Đồng Nai](targets/after-26395bb3-f134-40bd-844f-fc99a1d6657c/index.md) | found | 1275/73650779 |
| after | [tỉnh Tây Ninh](targets/after-7a2c9093-b860-419a-9849-11f4a977465a/index.md) | found | 11253/73652263 |
| after | [thành phố Cần Thơ](targets/after-c3369da1-333a-4886-8e1f-105aaadcbc6a/index.md) | found | 1022/73641932 |
| after | [tỉnh Vĩnh Long](targets/after-0e997715-f491-46d6-bbc8-bd94e5585b9d/index.md) | found | 11232/73652009 |
| after | [tỉnh Đồng Tháp](targets/after-df5d06de-fff3-4fcd-8a3d-13e8d2d306f6/index.md) | found | 11197/73651906 |
| after | [tỉnh Cà Mau](targets/after-f9f0970f-57bc-4900-9613-558ea3d2bbca/index.md) | found | 11194/73638792 |
| after | [tỉnh An Giang](targets/after-b8a52eac-6aec-4106-8e8d-e12e63701b03/index.md) | found | 3972/73652075 |
| after | [tỉnh Cao Bằng](targets/after-06a054f2-be7a-4902-b601-1ff6e081136c/index.md) | found | 19920857/75595156, 68/73641886 |
| after | [tỉnh Điện Biên](targets/after-886684a1-1e22-4c0b-b6d0-f45602ddae7c/index.md) | found | 19920857/75595156, 7322/73637193 |
| after | [tỉnh Hà Tĩnh](targets/after-f2fecb5e-11a8-4cb2-97f7-a089ac0ecf79/index.md) | found | 11181/73637043, 19920857/75595156 |
| after | [tỉnh Lai Châu](targets/after-0552144d-8f63-4d7f-ab23-262e100fa112/index.md) | found | 11202/73637037, 19920857/75595156 |
| after | [tỉnh Lạng Sơn](targets/after-9c0ae658-883a-41b7-8de3-8e5a08bc6177/index.md) | found | 19920857/75595156, 671/73637117 |
| after | [tỉnh Nghệ An](targets/after-d6fd8782-80d8-4d91-986c-254bf2e05ec3/index.md) | found | 19920857/75595156, 99282/73645673 |
| after | [tỉnh Quảng Ninh](targets/after-651dfe5c-8dd5-49b4-9bd4-a04148a79ed2/index.md) | found | 19920857/75595156, 5393/73649191 |
| after | [tỉnh Thanh Hóa](targets/after-fbc7cbac-5f23-48a5-a8a4-ab4d2902c2ba/index.md) | found | 19920857/75595156, 3203766/73648968 |
| after | [tỉnh Sơn La](targets/after-3013985e-02d9-45ff-8e7d-c22c53fd39ed/index.md) | found | 19920857/75595156, 9252/73642055 |
| after | [thành phố Hà Nội](targets/after-9d6837cd-1196-4073-bb43-85a7ee0cc8e5/index.md) | found | 19920857/75595156, 80/73649736 |
| after | [thành phố Huế](targets/after-c19ff93f-bc7c-4941-908b-1d7dadd26c84/index.md) | found | 11244/73649183, 19920857/75595156 |
