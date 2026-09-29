---
okf_version: "0.2"
type: log
title: "Nhật ký WikiSkill"
updated: "2026-09-29"
status: active
---

# Nhật ký WikiSkill

2026-09-29: khởi tạo từ audit offline corpus legacy. Ghi ba pattern quan sát; chưa có crawl mới hoặc vòng evolution được đánh giá. Giữ trace gốc để đối chiếu.

2026-09-29: ghi nhận yêu cầu INF–RAW từ người dùng. Bổ sung schema đề xuất 0.1.0 và validator offline; 13 unit test đạt, chưa có request thật/crawl mới. Trace: [exchange-contract](../raw/exchange-contract-2026-09-29.json). Đây là thay đổi yêu cầu nghiệp vụ, không phải kết quả evolution có đo điểm.

2026-09-29: hoàn tất thu thập 97 target NQ202/2025 sau pilot 5 target; 68 bài/169 revision tải về, 64 bài/149 revision được chọn. [Trace kiểm định](../raw/province-nq202-2026-09-29.json). Ghi nhận tách ID quan sát theo thời kỳ và xử lý Hà Nam trùng tên quốc gia; bổ sung runbook ba skill. Chưa đo mức cải thiện entity linking hoặc chạy vòng evolution có benchmark.

2026-09-29: từ gói NQ202 và tài liệu MediaWiki/Wikidata, bổ sung PAT-005 và skill candidate website 0.1.0-draft. [Trace](../raw/coverage-websites-2026-09-29.json) giữ baseline/hash và trích đoạn; proposal deferred vì chưa có đánh giá độc lập, chưa tải cơ quan/website mới. Inbox đề xuất version khác được giữ nguyên, không coi là request đã được engine hỗ trợ.

2026-09-29: người dùng quy định RAW không đọc/tìm/lấy dữ liệu từ IN/INF; INF đẩy payload vào inbox RAW. Collector 0.1.1 chặn input ngoài vùng nhận trước read_bytes, có test symlink escape. 24 tests PASS; gói NQ202 cũ giữ nguyên. [Trace](../raw/push-only-boundary-2026-09-29.json).
