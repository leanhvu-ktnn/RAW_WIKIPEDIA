---
okf_version: "0.2"
type: context
title: "Quy chuẩn OKF 0.2 của dự án"
updated: "2026-09-29"
status: active
---

# Quy chuẩn OKF 0.2 của dự án

Kế thừa cách tổ chức từ các dự án RAW trước của người dùng. Đây là profile nội bộ, không tuyên bố được một tổ chức bên ngoài chứng nhận.

- `context/`: đặc tả, mục tiêu, ontology, kế hoạch và nghiên cứu.
- `DiaBan/`, `CoQuan/`: dữ liệu nguồn theo layout hiện có.
- `raw/`: bằng chứng thực thi WikiSkill, bất biến sau khi ghi; không nhầm với toàn tầng RAW trong vault.
- `wiki/`: patterns, nhật ký tiến hóa và tác động; giữ cả kết quả bác bỏ.
- `skills/`: nguồn skill dùng chung cho agent, `SKILLS.md` điều phối.
- `reports/`: báo cáo kiểm định; `tools/` và `tests/`: công cụ và kiểm thử.

Trang context/wiki/hub mới có YAML `okf_version: "0.2"`, `type`, `title`, `updated`, `status`. Mọi thư mục tri thức mới có `index.md`; `SKILL.md` là entrypoint của thư mục skill. Metadata OKF của skill đặt dưới `metadata` để tương thích định dạng skill chuẩn (`name`, `description`), không thêm key tùy ý ở top-level.

Bài nguồn mới có metadata trong [[context/quy-chuan-crawl|quy chuẩn crawl]]; không gắn hit hoặc type wiki_page cho nội dung tự soạn không có revision. Ghi nguồn và phần biến đổi riêng. Giữ ID/mã dạng chuỗi, UTF-8, Unicode NFC. Không đặt đường dẫn tuyệt đối máy cá nhân vào dữ liệu/tài liệu.

Dữ liệu legacy được bảo toàn; việc profile mới đạt không chứng nhận 3.331 trang cũ đạt. Hubs cấp cha thiếu được bổ sung nhưng không đổi nội dung trang nguồn. Kiểm tra legacy riêng bằng audit strict; không giấu lỗi bằng cách hạ gate.
