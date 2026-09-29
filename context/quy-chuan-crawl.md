---
okf_version: "0.2"
type: context
title: "Quy chuẩn crawl Wikipedia"
updated: "2026-09-29"
status: active
---

# Quy chuẩn crawl Wikipedia

# Mục tiêu và quy chuẩn crawl

Đây là hợp đồng triển khai cho crawler tương lai. Những yêu cầu chưa có mã thực hiện không được báo là đã đạt.

## Mục tiêu

Thu thập mô tả/lịch sử và infobox phục vụ đối chiếu địa bàn, cơ quan Việt Nam. Mỗi kết quả phải trả lời được: thực thể nào, nguồn nào, revision nào, lấy lúc nào, dùng parser nào và vì sao chấp nhận match. Wikipedia không thay danh mục tên/mã pháp lý. Giữ số 0 đầu mã hành chính dưới dạng chuỗi. Tách địa bàn khỏi UBND/HĐND; không dùng bài địa bàn thay bài cơ quan khi cơ quan không có bài riêng.

Input bắt buộc: danh mục chuẩn với ngày hiệu lực, nguồn và SHA-256; mỗi target có ID ổn định, loại thực thể, tên, mã khi có, tỉnh và thời kỳ. Không đưa đường dẫn tuyệt đối của máy người phát triển vào cấu hình dùng chung. Không crawl toàn Wikipedia hoặc tự lập lịch hằng ngày.

## Đối sánh

Chuẩn hóa Unicode NFC và khoảng trắng, giữ nguyên dấu và label nguồn. Alias là ứng viên, không phải bằng chứng. Resolve redirect, ghi title trước/sau; bỏ trang định hướng. Đối chiếu loại, cấp, địa bàn cha, thời kỳ và QID nếu có. QID/P131 cũng phải xét thời gian; không dùng một tín hiệu tên hoặc QID để bỏ qua mâu thuẫn địa bàn. Nếu thiếu bằng chứng, gắn `ambiguous`/`needs_review`, không `hit`. “Không có bài” hợp lệ và không phải lỗi mạng.

Tách khóa trang `(language, pageid)` khỏi khóa target hành chính. Một trang có thể được đề xuất cho nhiều target nhưng quan hệ đó cần duyệt; không nhân bản tự động dưới nhiều xã trùng tên. Dữ liệu lịch sử phải có trạng thái và thời kỳ rõ ràng, kể cả tỉnh cũ; `Huyen` chỉ dùng cho lịch sử theo quy ước corpus.

## Thu thập API

Endpoint `https://vi.wikipedia.org/w/api.php`; không scrape HTML `/wiki/` hàng loạt. Đọc lại [API etiquette](https://www.mediawiki.org/wiki/API:Etiquette) khi triển khai. Dùng User-Agent mô tả tên/phiên bản và địa chỉ liên hệ thật; mặc định tuần tự, khoảng nghỉ ít nhất 1 giây, `maxlag=5`, timeout 30 giây, tối đa 5 lần thử (các giá trị là lựa chọn ban đầu của dự án).

Kiểm tra cả HTTP status và `error` trong JSON HTTP 200. Với 429/503/maxlag: tôn trọng Retry-After (giây hoặc HTTP-date), exponential backoff + jitter; không gửi sớm hơn Retry-After. Hết số lần thử thì ghi `error`, lưu checkpoint và kết thúc có báo cáo; nếu Retry-After quá dài cho phiên làm việc thì hoãn, không cắt ngắn thời gian chờ để tiếp tục. Không retry 401/403 vô hạn. Cache và negative cache có thời hạn cấu hình; chỉ retry target cần thiết. Phân biệt missing/disambiguation/ambiguous/error/skipped/unchanged.

Lấy raw revision và lưu pageid, revid/oldid, timestamp của revision, content SHA-256. Văn bản derived phải được tạo từ đúng raw revision đã lưu. Không lấy `extracts` hiện tại rồi gắn một oldid lấy từ request khác mà chưa chứng minh cùng revision. Nếu dùng `action=parse`, khóa `oldid`; kết quả render template vẫn có thể phụ thuộc template hiện tại nên raw wikitext là bằng chứng lưu trữ chính. Lưu version parser và extract_mode; không ghi lead_infobox nếu chỉ có lead mà không khai báo thiếu infobox.

## Lưu trữ và truy nguyên

Giữ layout `DiaBan/{TW|Tinh|Huyen}/{slug}/index.md`, `DiaBan/Xa/{tinh}/{slug}/index.md` và `CoQuan/{TW|Tinh}/{slug}/index.md`, `CoQuan/Xa/{tinh}/{slug}/index.md`. Kiểm tra path nằm trong output root, tránh collision tên và traversal. Snapshot raw lớn đặt ngoài Git theo cấu hình; mọi tham chiếu snapshot phải có checksum và cách tìm lại, không dùng đường dẫn máy cá nhân.

Một record mới cần: `schema_version`, `run_id`, `target_id`, `status`, `match_evidence`, `wiki_title`, `wiki_pageid`, `wikidata_qid` (rỗng nếu thiếu), `source_url`, `revision_url`, `oldid`, `revision_timestamp`, `extracted_at` UTC, `license`, `raw_sha256`, `parser_version`, `extract_mode`, `wiki_kind`, `capHanhChinh`, `ma_dvhc`/`cq_id` khi xác minh được. Trạng thái không hit không được đòi trường revision của một bài không tồn tại.

DiaBan giữ `wikipedia == source_url`, `website` rỗng khi chưa xác minh; không đoán domain. Lưu nguồn và thời điểm xác minh website, ví dụ revision Wikidata/P856. Trang Markdown phải có mục Liên kết, ghi công, liên kết revision và giấy phép; phân biệt phần trích nguồn và phần do dự án bổ sung. Media có giấy phép riêng, không suy giấy phép ảnh từ bài.

Ghi file tạm rồi atomic replace; chỉ ghi hit vào manifest sau khi file và checksum được kiểm tra. Resume dùng target + revision + parser/config version; chạy lại cùng input/snapshot/config phải cho cùng nội dung (metadata run có thể khác). Catalog mới append-only theo run_id; manifest current là snapshot riêng, cập nhật nguyên tử. Không xóa catalog legacy để làm đẹp số liệu.

## Các gate trước khi mở rộng

1. 100% hit của pilot có raw snapshot, revision và attribution; không thiếu ID/checksum.
2. Không có match mâu thuẫn cấp/tỉnh/thời kỳ được chấp nhận; trường hợp chưa rõ chuyển review.
3. Không có path thiếu, path vượt root hoặc file ghi dở trong manifest mới.
4. Tổng target đầu vào = tổng trạng thái cuối; request/retry/event đếm riêng, không coi là target duy nhất.
5. Kiểm thử offline cho Unicode, trùng tên, redirect, định hướng, lỗi HTTP/API, Retry-After, timeout, resume, crash khi ghi file và lặp run.
6. Pilot được rà soát thủ công và audit strict đạt cho dữ liệu mới. Nợ legacy phải được cô lập/ghi nhận cụ thể; không tuyên bố toàn corpus sạch khi còn lỗi.
7. Báo cáo run gồm input hash, config, commit code, thời gian, counts, lỗi, danh sách review và thay đổi dữ liệu; kiểm tra diff trước khi commit/push.

Không áp đặt tỷ lệ hit tối thiểu: miss có thể phản ánh đúng việc Wikipedia không có bài. Chất lượng match và truy nguyên quan trọng hơn độ phủ danh nghĩa.
