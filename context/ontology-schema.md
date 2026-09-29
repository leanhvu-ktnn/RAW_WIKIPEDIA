---
okf_version: "0.2"
type: context
title: "Ontology địa bàn, cơ quan và nguồn Wikipedia"
updated: "2026-09-29"
status: active
---

# Ontology địa bàn, cơ quan và nguồn Wikipedia

[ontology.ttl](ontology.ttl) là profile RDF/OWL của kho, phiên bản 0.1.0. Namespace `legal:` giữ nguyên `http://vbpl.vn/ontology/legal#` từ ontology INF đã đọc (v3.3.2); namespace `wiki:` riêng cho provenance, không giả làm namespace của cơ quan nhà nước. Profile chỉ tái sử dụng phần địa bàn/cơ quan, không sao chép toàn bộ ontology pháp luật.

| Khái niệm/field | Ánh xạ | Quy tắc |
|---|---|---|
| Địa bàn | `legal:DiaBan` | Địa bàn không phải tổ chức. |
| Cơ quan | `legal:CoQuan` | Có quan hệ `legal:thuocDiaBan` tới địa bàn. |
| `diaBan` | `legal:diaBan` | Tên địa bàn hiển thị, không dùng làm cấp. |
| `cap` | `legal:capDonVi` | TW, Bo, Tinh, Dang, Khac; không có Xa. |
| `capHanhChinh` | `legal:capHanhChinh` | TW, tinh, xa, huyen. |
| `theHe` | `legal:theHeDiaBan` | Moi hoặc Cu, xác minh theo input thời kỳ. |
| `trangThai` | `wiki:entityStatus` | dang_hoat_dong hoặc da_dung; huyện lịch sử phải da_dung. |
| `ma_dvhc` / `cq_id` | `wiki:administrativeCode` / `wiki:agencyId` | Chuỗi từ danh mục chuẩn, không suy từ pageid. |
| Bài / revision | `wiki:Page` / `wiki:Revision` | Page ổn định theo ngôn ngữ+pageid; revision theo oldid. |
| Đề xuất match | `wiki:Match` | Target, bài, trạng thái và evidence; không dùng owl:sameAs. |
| Lần crawl | `wiki:CrawlRun` | Phiên bản input/config/code, thời điểm, trạng thái. |

`validFrom`/`validTo` là thời kỳ thực thể; `revision_timestamp` là thời gian sửa Wikipedia; `extracted_at` là thời gian lấy. Không trộn ba loại thời gian. Chưa biết để trống và review, không điền từ đồng hồ hiện tại.

Khóa target phải kèm nguồn danh mục và thời kỳ nếu mã có thể được tái dùng. Không gắn `owl:sameAs` giữa bài viết và địa bàn/cơ quan; một bài là tài liệu nói về thực thể. `wikidata_qid` là tham chiếu ứng viên; mapping chỉ được xuất khi có bằng chứng.

Ví dụ cơ quan cấp xã: `cap: Tinh`, `capHanhChinh: xa`, `diaBan: Đà Nẵng`, `loaiDonVi: UBND_xa`. Không dùng ví dụ này để khẳng định một cơ quan cụ thể đang tồn tại.

`tools/validate_project.py` kiểm tra parse RDF và sự hiện diện các lớp/quan hệ lõi, không phải OWL reasoner hay SHACL toàn corpus. Export ABox production là bước tiếp theo, chưa triển khai.
