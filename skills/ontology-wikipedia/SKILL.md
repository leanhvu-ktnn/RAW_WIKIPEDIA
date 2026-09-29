---
name: ontology-wikipedia
description: Thiết lập hoặc kiểm định mapping ontology cho địa bàn, cơ quan và provenance Wikipedia; dùng khi thay schema hoặc chuẩn bị xuất RDF.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.2.0"
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

## Hợp đồng INF–RAW

Đọc [schema trao đổi](../../context/trao-doi-inf-raw.md). INF xác định phần thiếu và cấp inf_ref/request_item_id; RAW chỉ tìm, lưu nguyên bản và báo cáo, không ghi vào INF. Giữ ID đối tượng INF, wiki page_id và revision_id riêng biệt. Request/report phải qua `tools/validate_exchange.py`; PASS schema không chứng minh crawl hoặc match thành công. Ưu tiên địa bàn, chỉ chuyển sang cơ quan ở giai đoạn sau theo yêu cầu.
