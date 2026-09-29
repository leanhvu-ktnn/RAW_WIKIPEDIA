---
name: crawl-wikipedia-coquan
description: Lập và thực hiện đợt thu thập bài riêng về Bộ, cơ quan, UBND và HĐND từ Wikipedia; phân biệt cơ quan với địa bàn cùng tên.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.2.1"
---

# crawl-wikipedia-coquan

## Mục đích và đầu vào
Đọc [quy chuẩn](../../context/quy-chuan-crawl.md) và [ontology](../../context/ontology-schema.md). Input cần cq_id, tên chính thức, loại cơ quan, khối cap, cấp hành chính, địa bàn và thời kỳ từ danh mục chuẩn. Không sinh cq_id từ tên Wikipedia.

## Runbook
1. Audit corpus, nhóm target Bộ/TW, tỉnh, xã. Xác định lịch sử đổi tên/sáp nhập của cơ quan từ input; không dùng ngày sửa bài làm ngày hiệu lực.
2. Tìm bài tên cơ quan đầy đủ, cho phép alias viết tắt có bằng chứng; chuyển sang `resolve-wikipedia-entity` xác minh. UBND và HĐND là hai target khác nhau; bài tỉnh/xã hoặc trang định hướng không phải bài cơ quan.
3. Cơ quan xã giữ `cap: Tinh`, `capHanhChinh: xa`, `loaiDonVi` thích hợp; `diaBan` là tên địa bàn, không phải cấp. Quan hệ cơ quan–địa bàn là `legal:thuocDiaBan`, không sameAs.
4. Thu thập pilot API và snapshot đúng revision theo chuẩn. Không có bài riêng thì missing/ambiguous tùy bằng chứng, không tạo bản hit từ đoạn nói về chính quyền trong bài địa bàn. Hiện chưa có CLI crawler production; không báo đã crawl chỉ vì đã lập kế hoạch.
5. Ghi `CoQuan/{TW|Tinh}/{slug}/index.md` hoặc `CoQuan/Xa/{tinh}/{slug}/index.md`, manifest và trace cùng run. Dùng `stat-wikipedia` kiểm tra path/ID/provenance; báo riêng độ phủ bài cơ quan.

## Phục hồi
Dừng retry theo giới hạn, giữ error riêng với missing. Manifest D legacy rỗng không có nghĩa không có bài CoQuan; kiểm kê file trước khi đề xuất tải lại. Không chép bài địa bàn để làm đầy manifest.

## Hợp đồng INF–RAW

Đọc [schema trao đổi](../../context/trao-doi-inf-raw.md). INF xác định phần thiếu và cấp inf_ref/request_item_id; RAW chỉ tìm, lưu nguyên bản và báo cáo, không ghi vào INF. Giữ ID đối tượng INF, wiki page_id và revision_id riêng biệt. Request/report phải qua `tools/validate_exchange.py`; PASS schema không chứng minh crawl hoặc match thành công. Ưu tiên địa bàn, chỉ chuyển sang cơ quan ở giai đoạn sau theo yêu cầu.

## Input do INF chuyển xuống

RAW không đọc hoặc tìm kiếm trong IN/INF. Chỉ dùng request/payload đã được INF chủ động chuyển vào inbox RAW hoặc input RAW đã đóng băng; đường dẫn INF chỉ là metadata truy nguyên. Thiếu dữ liệu thì ghi yêu cầu bổ sung ở outbox RAW, không tự lên INF lấy; không ghi INF. Xem [ranh giới push-only](../../context/trao-doi-inf-raw.md).
