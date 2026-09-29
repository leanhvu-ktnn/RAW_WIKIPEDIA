---
name: discover-wikipedia-websites
description: Tìm và phân loại website được Wikipedia hoặc Wikidata dẫn cho địa bàn, cơ quan; lập bằng chứng chủ thể và kế hoạch tải nguồn có giới hạn.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0-draft"
  status: candidate
---

# discover-wikipedia-websites

Candidate từ đợt 97 target tỉnh; chưa đánh giá hành vi hoặc có downloader web ngoài. Đọc [thiết kế và giới hạn](../../context/de-xuat-doi-soat-dia-ban-co-quan-website.md), [record design](../../context/doi-soat-website-record-design.md) khi chuẩn bị kết quả. Không trình bày kế hoạch hay link trích được là snapshot đã tải.

## Input và routing

Nhận target có nguồn danh mục, loại, thời kỳ, quan hệ địa bàn và evidence từ `resolve-wikipedia-entity`. Giữ ID quan sát khi input chưa canonical; không tạo cq_id hoặc biến bài tỉnh thành bài cơ quan. Dùng `crawl-wikipedia-diaban`/`crawl-wikipedia-coquan` để tìm nguồn phù hợp; hỗ trợ cả bài riêng và mention có span, ghi hai trạng thái riêng.

## Quyết định nghiệp vụ

1. Trích URL từ revision đã lưu: infobox, liên kết ngoài và citation; giữ locator/template/field cùng URL nguyên văn. Website trong citation thường là nhà xuất bản, không phải website target. Không chỉ dùng regex bắt mọi URL làm bằng chứng ownership.
2. Phân loại official_claim, shared_portal, reference_document, related_news, archive, unknown. Portal tỉnh không mặc nhiên là website riêng UBND/HĐND. Bài cùng tên/QID không gộp cơ quan hoặc thời kỳ.
3. Dùng extlinks hiện tại để discovery; với lịch sử dùng frozen wikitext và parse oldid có lưu response/phụ thuộc. Nếu thêm P856 thì đối sánh QID, lưu Wikidata revision/statement/qualifier riêng; không gán URL đó cho Wikipedia nếu bài không nêu.
4. Tách source_claim và owner verification. Cần câu nhận diện cơ quan/chủ quản/thời kỳ; gov.vn, HTTPS hay HTTP200 đơn lẻ không đủ. Website hiện tại không chứng minh website lịch sử. Quan hệ seat khác jurisdiction.
5. Tìm hết phạm vi đã khai báo mới ghi not_found; incomplete/budget/technical failures có trạng thái và lý do riêng. Không thấy link trong Wikipedia chỉ là chưa tìm thấy ở nguồn đó.
6. Khi được giao tải, kiểm tra công cụ thực tế và dùng ngân sách/robots/URL validation trong thiết kế. Chưa có downloader phù hợp thì báo thiếu, giữ candidates để tiếp tục; không bịa lệnh hoặc báo downloaded. Tải trang được chọn, không tự mở rộng cả website.
7. Trả target–revision–span–URL–snapshot, requested/final URL, headers được phép, checksum, quyền nội dung và các trường chưa xác minh. Chống trùng artifact không làm mất cạnh target. RAW giữ gói riêng, INF xét duyệt; không sửa INF hoặc gói đã công bố.

## Kiểm định candidate

Ca từ NQ202 dùng regression, không tính là validation độc lập. Hard fail khi sai chủ thể, lấy báo chí làm website chính thức, trộn thời kỳ hoặc có downloaded thiếu bytes/hash. Trước khi nâng skill thành accepted cần baseline/candidate trên cùng bộ validation và trace theo [WikiSkill](../../context/quy-trinh-wikiskill.md). Hiện trạng deferred, chưa đo cải thiện.

## Input do INF chuyển xuống

RAW không đọc hoặc tìm kiếm trong IN/INF. Chỉ dùng request/payload đã được INF chủ động chuyển vào inbox RAW hoặc input RAW đã đóng băng; đường dẫn INF chỉ là metadata truy nguyên. Thiếu dữ liệu thì ghi yêu cầu bổ sung ở outbox RAW, không tự lên INF lấy; không ghi INF. Xem [ranh giới push-only](../../context/trao-doi-inf-raw.md).
