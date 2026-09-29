---
okf_version: "0.2"
type: context
title: "Kế hoạch và các cổng nghiệm thu"
updated: "2026-09-29"
status: active
---

# Kế hoạch và các cổng nghiệm thu

1. Đã thiết lập: context OKF 0.2 tách riêng, ontology Turtle, skill địa bàn/cơ quan, đối sánh, audit, ontology, Wiki Maintainer, Skill Proposer, Git sync; công cụ audit và trace offline.
2. Cần xử lý dữ liệu: lỗi Phú Thọ, hai trang thiếu revision, 11 nhóm trùng, 92 đường dẫn manifest và 113 trang không được manifest liệt kê. Không tự vá nguồn chưa xác minh.
3. Tiếp theo về crawler: input có phiên bản, HTTP client có giới hạn, revision snapshot, dry-run/pilot/resume, manifest nguyên tử và test lỗi mạng theo [[context/quy-chuan-crawl|quy chuẩn]]. Không có lệnh crawl production trong kho hiện tại.
4. Gate hệ thống skill/context: `.venv/bin/python tools/validate_project.py`; unit tests: `.venv/bin/python -m unittest discover -s tests -v`.
5. Gate dữ liệu: `python3 tools/audit_corpus.py --strict` hiện còn FAIL do legacy; chạy và công bố lỗi trước khi kết thúc. Commit thiết lập có thể mang baseline lỗi đã công khai, không có nghĩa gate dữ liệu PASS. Crawl mở rộng phải thỏa các gate dữ liệu mới, không vượt gate chỉ vì skill hợp lệ.
6. Đồng bộ GitHub: kiểm tra diff, commit, push không force rồi so SHA. Không bật crawl định kỳ hoặc merge thay đổi người khác trong lần thiết lập.

## Ưu tiên và thực trạng bổ sung

Địa bàn trước, cơ quan sau. Đã bổ sung hợp đồng đề xuất INF–RAW 0.1.0, fixture và validator offline; chưa có inbox tích hợp INF, request thật, snapshot downloader hoặc crawl mới. Baseline audit 3.331 trang chưa đổi. Việc có schema không có nghĩa trao đổi hai hệ thống đã hoạt động.

## Đợt tỉnh NQ202/2025 đã thực hiện

Đã có downloader thực tế, pilot 5 target và gói 97 target (63 trước, 34 sau), kiểm định byte/revision/trích đoạn và chạy lại cache. [Runbook](crawl-province-2025.md) và [gói bàn giao](../packages/province-before-after-2025/report.md) ghi phạm vi công cụ và các trường chưa xác minh. Các mục “chưa có downloader/crawl mới” phía trên mô tả thời điểm thiết lập ban đầu; chưa có tích hợp ghi INF hoặc crawler production tổng quát.
