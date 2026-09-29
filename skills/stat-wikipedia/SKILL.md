---
name: stat-wikipedia
description: Kiểm kê cấu trúc corpus Wikipedia, kiểm tra manifest, pageid, provenance, ontology và hệ thống skill; phân biệt lỗi legacy với kết quả mới.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.3.1"
---

# stat-wikipedia

## Mục đích và runbook
1. Đọc [giới hạn công cụ](../../README.md), chạy `python3 tools/audit_corpus.py` và `python3 tools/audit_corpus.py --strict`.
2. Chạy `.venv/bin/python tools/validate_project.py` và `.venv/bin/python -m unittest discover -s tests -v` cho hệ thống skill/context.
3. Báo counts kèm đường dẫn và mức ảnh hưởng. Catalog là sự kiện, không là số thực thể duy nhất; đối chiếu raw run và manifest trước khi tính tỷ lệ.
4. Kiểm tra thủ công mẫu mâu thuẫn địa bàn/loại/thời kỳ; audit offline không chứng minh factual accuracy. Không ghép số lỗi từ các nhóm chồng lấp thành số trang lỗi.
5. Ghi trace từ JSON audit bằng `tools/record_trace.py`; dùng wiki-maintainer nếu cần rút bài học. Không sửa dữ liệu chỉ để kiểm tra PASS.

## Phục hồi
Script lỗi parse thì báo lỗi và giữ input. `--strict` hiện FAIL do legacy là kết quả cần công bố. Gate hệ thống PASS không thay gate corpus.

## Hợp đồng INF–RAW

Đọc [schema trao đổi](../../context/trao-doi-inf-raw.md). INF xác định phần thiếu và cấp inf_ref/request_item_id; RAW chỉ tìm, lưu nguyên bản và báo cáo, không ghi vào INF. Giữ ID đối tượng INF, wiki page_id và revision_id riêng biệt. Request/report phải qua `tools/validate_exchange.py`; PASS schema không chứng minh crawl hoặc match thành công. Ưu tiên địa bàn, chỉ chuyển sang cơ quan ở giai đoạn sau theo yêu cầu.

## Đợt tỉnh trước/sau NQ202/2025

Dùng [runbook staging quan sát](../../context/crawl-province-2025.md) cho yêu cầu cụ thể này. Khi input là ID quan sát, không ép thành DiaBan/canonical INF ID để vượt validator 0.1.0; giữ metadata gốc trong staging. Collector thực tế: `tools/crawl_province_2025.py`; kiểm định gói: `tools/province_package.py`. Chọn revision theo ngày chỉ là thu hẹp nguồn, không chứng minh thời kỳ; cần trích đoạn theo mốc. Bài/pageid/QID chung không gộp target trước–sau.

## Input do INF chuyển xuống

RAW không đọc hoặc tìm kiếm trong IN/INF. Chỉ dùng request/payload đã được INF chủ động chuyển vào inbox RAW hoặc input RAW đã đóng băng; đường dẫn INF chỉ là metadata truy nguyên. Thiếu dữ liệu thì ghi yêu cầu bổ sung ở outbox RAW, không tự lên INF lấy; không ghi INF. Xem [ranh giới push-only](../../context/trao-doi-inf-raw.md).
