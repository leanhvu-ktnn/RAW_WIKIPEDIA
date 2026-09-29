---
name: ontology-wikipedia
description: Thiết lập hoặc kiểm định mapping ontology cho địa bàn, cơ quan và provenance Wikipedia; dùng khi thay schema hoặc chuẩn bị xuất RDF.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0"
---

# ontology-wikipedia

## Mục đích và runbook
Đọc [ontology-schema](../../context/ontology-schema.md), [Turtle](../../context/ontology.ttl) và [OKF](../../context/tieu-chuan-okf-02.md).

- Dùng legal:DiaBan và legal:CoQuan, phân biệt diaBan/capDonVi/capHanhChinh/theHe. Chuẩn hóa cq_id và mã từ input, không từ slug hay pageid.
- Tách Page, Revision, Match, CrawlRun. Không sameAs bài và cơ quan; match phải có evidence, status và run. Chỉ xuất quan hệ hành chính có provenance và thời kỳ phù hợp.
- Trước sửa namespace hoặc property, kiểm tra caller/mapping; cập nhật tài liệu và version cùng nhau. Profile RDF là tập con liên quan Wikipedia, không mặc nhiên thay ontology INF nguồn.
- Chạy `.venv/bin/python tools/validate_project.py`. Parse RDF và kiểm tra lớp chỉ là gate cấu trúc, không chứng nhận suy luận ngữ nghĩa hoặc validate toàn ABox. Export ABox production chưa được triển khai.

## Phục hồi
Giữ mapping chưa rõ ở review; không phát biểu quan hệ pháp lý chưa chứng minh. Không điền ngày hiệu lực từ extracted_at.
