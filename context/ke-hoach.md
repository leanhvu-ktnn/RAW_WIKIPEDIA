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
