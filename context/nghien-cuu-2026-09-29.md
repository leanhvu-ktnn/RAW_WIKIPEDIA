---
okf_version: "0.2"
type: context
title: "Nghiên cứu và đánh giá"
updated: "2026-09-29"
status: active
---

# Nghiên cứu và đánh giá

# Nghiên cứu và đánh giá RAW_WIKIPEDIA

Ngày kiểm tra: 29/09/2026. Phạm vi: toàn bộ dữ liệu local, metadata GitHub, kế hoạch cũ nằm ngoài kho, và tài liệu chính thức của các dự án tham khảo. Không chạy crawl mạng mới, không xác nhận lại tình trạng pháp lý của địa bàn.

## Kết luận

**Chưa đầy đủ để vận hành độc lập hoặc crawl mở rộng.** Mục tiêu nghiệp vụ và một số quy chuẩn đã tồn tại trong vault nguồn, nhưng chưa được đóng gói cùng dữ liệu. Tại thời điểm bắt đầu, GitHub trống (size 0, `git ls-remote` không có ref), thư mục local chưa có `.git`, README, skill, mã crawler, kiểm thử hay CI. Đây là khởi tạo đồng bộ, không phải cập nhật từ một dự án GitHub đã có mã nguồn.

Đã đọc tài liệu cũ: `RAW/context/nghien-cuu/Crawl_Plan_wikipedia.md` và `RAW/context/nguon/wikipedia/index.md` trong vault cha. Chúng quy định API, khoảng 1 request/giây, User-Agent, Retry-After, các sóng B/C/D, không daily, không sửa tên/mã pháp lý. Chúng nhắc `tools/download_wikipedia_vi.py`, nhưng file đó không được cung cấp trong thư mục dự án. Không coi mô tả lệnh trong tài liệu là bằng chứng crawler đang hoạt động.

## Bằng chứng kiểm kê

Tái tạo bằng `python3 tools/audit_corpus.py`. Kết quả đầy đủ trong [JSON](../reports/audit-2026-09-29.json).

| Hạng mục | Kết quả |
|---|---:|
| File Markdown ban đầu, gồm cả hub | 3.359 |
| Trang có `type: wiki_page` | 3.331 |
| DiaBan / CoQuan | 3.313 / 18 |
| Dòng catalog | 11.043 |
| Manifest B / C / D | 129 / 3.181 / 0 |
| Bản ghi manifest trỏ đường dẫn không có trang | 92 |
| Trang không có trong các manifest | 113 |
| Nhóm trùng pageid | 11 |
| Trường pageid/oldid thiếu hoặc không hợp lệ | 4 trên 2 trang |

92 hit trong catalog cũng trỏ đường dẫn không tồn tại. Đây không mặc nhiên là mất dữ liệu: ví dụ `DiaBan/Xa/Xa_Hai_Van/index.md` thiếu tầng tỉnh so với cây thư mục hiện tại. Cần xác minh bằng pageid và mã trước khi sửa đường dẫn.

Catalog chứa B: 129 hit, 2 miss; C: 3.181 hit, 57 miss, 83 skip; D: 18 hit, 7.537 miss, 36 skip. Các con số này đếm **sự kiện**, không phải đơn vị duy nhất hay một lần chạy. Không có run_id/timestamp cho mọi sự kiện nên không thể suy ngược chính xác mỗi đợt. Bảng legacy trên `index.md` ghi B 130/1 và D 17/3.339; không dùng làm KPI hiện tại.

## Các vấn đề cần ưu tiên

1. **P0 — ghép sai thực thể:** `DiaBan/Xa/Ho_Chi_Minh/Xa_Phu_Tho_27226/index.md` mang cấp xã, mã 27226, nhưng pageid 3970/Q36610, nội dung và website là tỉnh Phú Thọ. Đây là lỗi cụ thể, không chỉ nguy cơ. Dừng xuất bản kết quả match mới khi chỉ khớp tên; yêu cầu bằng chứng cấp hành chính, tỉnh và thời kỳ. Các nhóm trùng khác cần đánh giá riêng, không tự xóa.
2. **P0 — nguồn chưa truy nguyên được:** Quảng Nam và Chiến Đàn thiếu pageid/oldid. Chiến Đàn còn có liên kết thân bài tới tháp Chiên Đàn, khác thực thể mục tiêu. Không bổ sung revision bằng phỏng đoán hoặc dùng revision mới để gắn cho văn bản cũ.
3. **P1 — manifest và catalog lệch corpus:** 92 đường dẫn, 113 trang không có manifest, D rỗng dù có 18 trang CoQuan. Khôi phục manifest từ nguồn đã xác minh, giữ nguyên log cũ làm bằng chứng.
4. **P1 — chưa thể tái chạy độc lập:** thiếu crawler, input danh mục chuẩn, khóa phiên bản parser, checkpoint và kiểm thử lỗi mạng. Tài liệu cũ phụ thuộc vault cha.
5. **P1 — Unicode/title:** catalog có ứng viên như `PhườngÔ Chợ Dừa`, `H ải V ân`. Cần NFC, khoảng trắng và bộ kiểm thử dấu tiếng Việt. Không tự đổi “la” thành “Ia” hoặc bỏ dấu làm khóa đối sánh.
6. **P2 — kiểm soát chất lượng:** còn thiếu kiểm chứng tự động schema đầy đủ, URL nguồn, thời gian, thực thể và giấy phép ở cấp run. Audit mới là kiểm kê cấu trúc có giới hạn, không chứng nhận độ đúng toàn corpus.

## Tham khảo dự án tương tự

Nguồn được đọc ngày 29/09/2026; đánh giá phù hợp dưới đây là đề xuất của đợt nghiên cứu này, không phải kết quả benchmark.

| Dự án/tài liệu | Cách tiếp cận | Áp dụng ở đây |
|---|---|---|
| [Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot) | Thư viện và công cụ tương tác MediaWiki | Cân nhắc nếu muốn dùng framework API thay vì tự bảo trì client; vẫn cần logic match hành chính riêng. |
| [mwparserfromhell](https://github.com/earwig/mwparserfromhell) | Parser wikicode, template và cấu trúc bài | Phù hợp trích infobox; không xem parser là bộ xác minh thực thể hay renderer đầy đủ. |
| [WikiExtractor](https://github.com/WikiExtractor/wikiextractor) | Trích văn bản từ dump, có JSON chứa revid | Tham khảo tách raw và derived; không dùng mặc định vì corpus hiện tại chọn lọc và cần cấu trúc infobox. |
| [python-mwxml](https://github.com/mediawiki-utilities/python-mwxml) | Đọc XML dump theo luồng, giữ cấu trúc page/revision | Hướng mở rộng nếu sau này thực sự cần bulk; chưa cần tải toàn dump trong phạm vi hiện tại. |
| [MediaWiki API etiquette](https://www.mediawiki.org/wiki/API:Etiquette) | User-Agent, request tuần tự, cache, maxlag và backoff | Chuẩn vận hành client; 1 request/giây là mặc định dự án đề xuất, không phải hạn mức cố định Wikimedia cam kết. |

Đề xuất kiến trúc: danh mục chuẩn có phiên bản → sinh ứng viên → resolve redirect/disambiguation → kiểm chứng thực thể → snapshot đúng revision → trích xuất → kiểm định → ghi nguyên tử → manifest + run report. Ưu tiên API chọn lọc, giữ dữ liệu gốc để có thể tái trích. Không dùng full dump hay thêm lịch crawl tự động khi chưa có nhu cầu.

## Lộ trình và tiêu chí hoàn tất

- **Giai đoạn 0 (đợt này):** đóng gói báo cáo, mục tiêu/quy chuẩn, skill và audit offline; bảo toàn corpus legacy; khởi tạo Git và thử đẩy GitHub.
- **Giai đoạn 1:** phân loại toàn bộ 11 nhóm trùng; xử lý lỗi Phú Thọ và 2 trang thiếu revision có bằng chứng; đối chiếu 92 path và 113 trang không có manifest. Không tự sửa nội dung trong đợt kiểm kê.
- **Giai đoạn 2:** khôi phục hoặc triển khai crawler có input tường minh, dry-run, resume, retry có giới hạn và kiểm thử. Thử nhỏ khoảng 10–20 mục, gồm trùng tên, redirect, định hướng, lịch sử và thiếu bài; kiểm tra thủ công mọi match của pilot.
- **Giai đoạn 3:** chỉ mở rộng sau khi đạt các gate trong [quy chuẩn](quy-chuan-crawl.md). Không tối đa hóa tỷ lệ hit bằng cách chấp nhận kết quả tìm kiếm đầu tiên.

Skill và quy chuẩn mới không đồng nghĩa crawler đã hoàn thành; tình trạng lỗi dữ liệu được giữ rõ trong README và báo cáo.
