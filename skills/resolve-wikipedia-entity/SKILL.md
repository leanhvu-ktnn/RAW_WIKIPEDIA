---
name: resolve-wikipedia-entity
description: Đối sánh ứng viên Wikipedia với thực thể địa bàn hoặc cơ quan, xử lý trùng tên, redirect, định hướng và sai thời kỳ trước khi chấp nhận hit.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0"
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
