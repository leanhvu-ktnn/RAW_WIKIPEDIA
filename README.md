# RAW_WIKIPEDIA

Corpus Wikipedia tiếng Việt để **đối chiếu** địa bàn và cơ quan Việt Nam; không thay thế danh mục tên/mã hành chính chính thức.

**Trạng thái 29/09/2026:** có dữ liệu legacy và công cụ kiểm kê offline; chưa có crawler độc lập, chưa đủ điều kiện crawl mở rộng. Có lỗi ghép thực thể và thiếu provenance cần xử lý. Skill là hướng dẫn cho agent, không phải crawler đã triển khai.

- [Báo cáo nghiên cứu và đánh giá](context/nghien-cuu-2026-09-29.md)
- [Mục tiêu, quy chuẩn và tiêu chí nghiệm thu](context/quy-chuan-crawl.md)
- [Danh mục skill địa bàn/cơ quan và WikiSkill](SKILLS.md)
- [Báo cáo máy đọc được](reports/audit-2026-09-29.json)
- [Tổng quan dữ liệu legacy](index.md) — thống kê cũ chưa nhất quán.
- [Nguồn và ghi công](ATTRIBUTION.md)

## Kiểm tra dữ liệu

Audit corpus dùng Python 3.9 trở lên và thư viện chuẩn. Kiểm thử toàn hệ thống cần cài requirements-dev.txt theo hướng dẫn bên dưới:

```bash
python3 tools/audit_corpus.py
python3 tools/audit_corpus.py --strict
.venv/bin/python -m unittest discover -s tests -v
```

`--strict` trả mã 1 nếu còn phát hiện; hiện tại **dự kiến thất bại** vì lỗi dữ liệu legacy. Lệnh không có `--strict` chỉ kiểm kê, mã 0 không chứng nhận chất lượng. Công cụ hỗ trợ frontmatter scalar phẳng của corpus này, không phải parser YAML tổng quát và không kiểm chứng nội dung Wikipedia online.

## Phạm vi và dữ liệu

`DiaBan/` chứa địa bàn, `CoQuan/` chứa cơ quan. Mỗi bài lưu trong `index.md`; `_manifest*.json` là manifest legacy, `_catalog.jsonl` là nhật ký sự kiện cũ, không phải bảng thực thể duy nhất. Tiền tố `RAW/WIKIPEDIA/` trong path legacy được công cụ chuyển thành đường dẫn tương đối khi đọc.

Các liên kết `[[INF/...]]`, `[[RAW/context/...]]` thuộc vault nguồn, không có sẵn trong kho độc lập. Không tự suy luận tên/mã pháp lý từ Wikipedia. Người chạy cần cung cấp danh mục chuẩn có phiên bản trước khi thiết kế đợt crawl mới.

## Đồng bộ GitHub

Remote dự kiến: `https://github.com/leanhvu-ktnn/RAW_WIKIPEDIA.git`.
Sau lần khởi tạo, dùng `git fetch origin`, kiểm tra diff và chỉ pull fast-forward khi cây làm việc sạch. Làm thay đổi trên nhánh riêng khi đã có lịch sử chung; không force push. Chỉ báo đồng bộ thành công sau khi SHA local và remote trùng nhau. Kho này không tự chạy crawl hàng ngày.

## Hệ thống WikiSkill, OKF và ontology

[Context](context/index.md) · [Ontology](context/ontology-schema.md) · [Wiki](wiki/index.md) · [Skills](SKILLS.md). Dựa trên nghiên cứu Google WikiSkill; chưa có engine tự tiến hóa hoặc crawler production.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python tools/validate_project.py
```
