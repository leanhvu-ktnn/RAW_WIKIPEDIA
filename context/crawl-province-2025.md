---
okf_version: "0.2"
type: context
title: "Thu thập tỉnh trước và sau NQ202/2025 — staging quan sát"
updated: "2026-09-29"
status: active
---

# Thu thập tỉnh trước và sau NQ202/2025

Phạm vi được người dùng giao: 63 tỉnh/thành ngay trước sắp xếp và 34 tỉnh/thành theo baseline sau NQ202/2025/QH15; không khẳng định hiện trạng tại ngày crawl. Không thu thập target cơ quan hoặc xã.

## Input và ranh giới

Nguồn tham chiếu: `INF/context/bao-cao/evidence/vietnam-territory-law/province-before-after-2025.json`. Dùng bốn tập historical_before_reorganization, post_reorganization_baseline, subjects và events. Đóng băng bytes tại `packages/province-before-after-2025/input/`; checksum là phiên bản nội dung khi input không khai báo version. Giữ checksum PDF do input cung cấp riêng với checksum JSON; RAW không tuyên bố đã tải lại PDF.

Hợp đồng INF–RAW 0.1.0 đòi `inf_ref.entity_type` là DiaBan/CoQuan, chưa biểu diễn đầy đủ ID quan sát pending_resolution và nhiều thời kỳ. Không ép input vào contract đó. `staging_schema_version: province-observation-0.1.0` giữ nguyên input_subject/input_events và ID quan sát, kể cả canonical_territory_inf_id nếu input đã cung cấp; không suy hoặc tạo ID INF. `target_id` thuộc namespace nội bộ RAW, khóa theo phase + observation ID. Hà Nội ở hai mốc là hai target dù cùng ID quan sát.

## Công cụ thực tế

`tools/crawl_province_2025.py`: client read-only Action API tuần tự, User-Agent liên hệ, maxlag=5, timeout 30s, tối đa 5 lần thử, hỗ trợ Retry-After số/HTTP-date. Nếu phải đợi hơn 60s, ghi lỗi deferred để tiếp tục sau, không gửi sớm. Cache theo URL trong package đóng băng kết quả discovery/latest cho lần chạy này; không coi đây là cache latest vĩnh viễn dùng cho mọi đợt sau. Đợt mới dùng package mới.

Response body JSON lưu đúng bytes chưa biến đổi; wikitext dẫn xuất được kiểm tra trùng nội dung revision trong response. SHA-256 cả hai loại. Checkpoint theo target, nguyên bản theo hash, atomic replace cho metadata; chạy lại cùng package không nhân bản kết quả. Retry chỉ error khi dùng --retry-errors. Không xóa raw khi đổi review. Chưa có bảo vệ nhiều tiến trình đồng thời; chỉ chạy một collector cho một package.

Title là ứng viên, không tự động match thực thể. Bài định hướng bị loại; giữ toàn bộ danh sách title đã hỏi và redirect/normalized do API trả. Revision trước được chọn <= 2025-06-11T23:59:59Z; baseline sau <= 2025-07-02T23:59:59Z. Đây là mốc chọn bản sửa UTC, **không phải ngày hiệu lực của địa bàn**; phải đọc nội dung trước khi gắn mốc. Thu thêm bài hiện tại để đối chiếu phần lịch sử, không dùng thông tin 2026 thay baseline 2025.

## Pilot và toàn bộ

```bash
.venv/bin/python tools/crawl_province_2025.py --input packages/province-before-after-2025/input/province-before-after-2025.json --package packages/province-before-after-2025 --mode pilot
.venv/bin/python tools/province_package.py packages/province-before-after-2025 --pilot
.venv/bin/python tools/crawl_province_2025.py --input packages/province-before-after-2025/input/province-before-after-2025.json --package packages/province-before-after-2025 --mode all
```

Pilot Gia Lai cũ, Bình Định cũ, Gia Lai mới và Hà Nội hai mốc phải có review trích đoạn và gate PASS trước all. `found` là tìm được nguồn đối chiếu có bằng chứng, không có nghĩa mọi field/quan hệ pháp lý đã xác minh. Mâu thuẫn ngữ nghĩa và ngày được lưu riêng. `ambiguous` giữ nguồn nhưng chưa đủ bằng chứng cho mốc; lỗi API luôn error.

`tools/province_package.py` kiểm tra đủ target, input/source/checksum, revision trong response, wikitext, trích đoạn theo dòng và giấy phép; export manifest, JSONL/CSV, Markdown theo target. Trường excerpt giữ nguyên wikicode, không thực thi nội dung nguồn. Gói còn cần semantic review, báo cáo và inventory cuối; không công bố hoàn tất chỉ vì downloader đã xong.

## Bàn giao

Package root: `packages/province-before-after-2025/`. INF đọc manifest, target-page-revision-evidence.jsonl hoặc CSV, report.md và validation.json. checksums.json kiểm kê file toàn gói (trừ chính nó). Gói là sản phẩm RAW, không ghi trực tiếp INF. Nợ legacy của corpus cũ không bị che hoặc tự sửa trong đợt này.

## Cập nhật ranh giới input

Đợt đã công bố từng đọc tham chiếu INF theo yêu cầu tại thời điểm đó; giữ nguyên gói và trace lịch sử. Theo chỉ đạo mới, mọi lượt sau dùng bản input đã đóng băng trong RAW hoặc payload do INF chủ động đặt vào `inbox/inf/`. Không mở logical_path nguồn INF, không kiểm tra lại checksum bằng cách đọc INF. Collector 0.1.1 áp dụng kiểm tra containment trước khi đọc input, từ chối đường dẫn ngoài RAW và symlink thoát vùng nhận. Lệnh mẫu ở trên dùng input RAW nên vẫn phù hợp.
