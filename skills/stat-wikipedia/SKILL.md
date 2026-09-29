---
name: stat-wikipedia
description: Kiểm kê cấu trúc corpus Wikipedia, kiểm tra manifest, pageid, provenance, ontology và hệ thống skill; phân biệt lỗi legacy với kết quả mới.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0"
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
