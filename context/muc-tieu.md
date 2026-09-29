---
okf_version: "0.2"
type: context
title: "Mục tiêu địa bàn và cơ quan"
updated: "2026-09-29"
status: active
---

# Mục tiêu địa bàn và cơ quan

Ưu tiên 1: đối chiếu toàn bộ target địa bàn trong danh mục chuẩn do người dùng cung cấp, theo cấp và thời kỳ. Ưu tiên 2: đối chiếu cơ quan có định danh chính thức, tìm bài riêng trên Wikipedia. Phạm vi thực tế và mẫu số độ phủ lấy từ input có phiên bản, không hard-code số xã/tỉnh vào crawler.

100% target phải có trạng thái cuối và lý do; không yêu cầu 100% có bài Wikipedia. Các trạng thái: hit, missing, disambiguation, ambiguous, error, skipped, unchanged. Kết quả thiếu bằng chứng không tính hit.

Đầu ra: Markdown OKF 0.2, revision có thể truy nguyên, mapping ontology và manifest theo run. Wikipedia chỉ là nguồn bổ sung mô tả/lịch sử. Không sửa tên/mã pháp lý, không suy cơ quan từ bài địa bàn. Không có lịch crawl hằng ngày mặc định.

Hiện có hệ thống skill, context, ontology, audit và ghi trace offline. Chưa có engine crawl production hay chứng minh vận hành tự học tự động. [[context/ke-hoach|Kế hoạch]] phân tách phần đã làm và phần còn thiếu.

## Ranh giới INF–RAW

Ưu tiên địa bàn trước, cơ quan sau. INF xác định thiếu gì và gửi yêu cầu; RAW nhận, tìm, lưu bản nguồn và phản hồi. RAW không ghi trực tiếp vào INF. ID đối tượng INF, ID bài và revision tách biệt. Hợp đồng đề xuất: [[context/trao-doi-inf-raw|schema trao đổi 0.1.0]].
