---
name: resolve-wikipedia-entity
description: Đối sánh ứng viên Wikipedia với thực thể địa bàn hoặc cơ quan, xử lý trùng tên, redirect, định hướng và sai thời kỳ trước khi chấp nhận hit.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.3.0"
---

# resolve-wikipedia-entity

## Mục đích và đầu vào
Dùng [ontology](../../context/ontology-schema.md). Nhận một target có nguồn chuẩn và danh sách ứng viên có pageid/QID/loại/cấp/địa bàn/thời kỳ; không coi title đơn lẻ là chứng cứ.

## Runbook
- Ghi label gốc, chuẩn hóa NFC và khoảng trắng, giữ dấu. Resolve redirect và lưu cả hai title; định hướng chuyển trạng thái riêng.
- Lập bảng bằng chứng loại, cấp, địa bàn cha, thời kỳ, mã nếu nguồn thật sự cung cấp; dẫn URL/revision. Missing là không tìm thấy bài qua quy trình, ambiguous là có ứng viên chưa đủ phân biệt, error là thất bại kỹ thuật.
- Có mâu thuẫn thì không hit; QID trùng không xóa mâu thuẫn. Một bài tỉnh và một phường cùng tên phải được tách. Bài về địa bàn không thay bài UBND/HĐND.
- Lưu candidate và lý do rejected/accepted theo target_id/run_id. Không xóa duplicate file tự động; một pageid xuất hiện nhiều nơi có thể do alias hoặc lỗi và cần review.

## Phục hồi
Thiếu input thời kỳ/địa bàn thì tiếp tục phần kiểm kê độc lập, yêu cầu thông tin còn thiếu cho quyết định match. Không đoán mã, sửa tên chính thức hay gắn sameAs để vượt gate.

## Hợp đồng INF–RAW

Đọc [schema trao đổi](../../context/trao-doi-inf-raw.md). INF xác định phần thiếu và cấp inf_ref/request_item_id; RAW chỉ tìm, lưu nguyên bản và báo cáo, không ghi vào INF. Giữ ID đối tượng INF, wiki page_id và revision_id riêng biệt. Request/report phải qua `tools/validate_exchange.py`; PASS schema không chứng minh crawl hoặc match thành công. Ưu tiên địa bàn, chỉ chuyển sang cơ quan ở giai đoạn sau theo yêu cầu.

## Đợt tỉnh trước/sau NQ202/2025

Dùng [runbook staging quan sát](../../context/crawl-province-2025.md) cho yêu cầu cụ thể này. Khi input là ID quan sát, không ép thành DiaBan/canonical INF ID để vượt validator 0.1.0; giữ metadata gốc trong staging. Collector thực tế: `tools/crawl_province_2025.py`; kiểm định gói: `tools/province_package.py`. Chọn revision theo ngày chỉ là thu hẹp nguồn, không chứng minh thời kỳ; cần trích đoạn theo mốc. Bài/pageid/QID chung không gộp target trước–sau.
