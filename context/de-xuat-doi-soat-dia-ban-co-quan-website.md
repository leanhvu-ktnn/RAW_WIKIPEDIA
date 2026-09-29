---
okf_version: "0.2"
type: context
title: "Đề xuất đối soát địa bàn, cơ quan và website"
updated: "2026-09-29"
status: draft
---

# Đối soát địa bàn, cơ quan và website

## Kết luận và phạm vi

Có thể tái sử dụng kinh nghiệm đợt NQ202 để xây hệ thống đối soát toàn danh mục. “Tất cả” nghĩa là **mỗi target do INF cung cấp có kết quả**, không phải mọi đối tượng đều có bài Wikipedia hoặc website. Mẫu số phải cố định theo catalog/version/checksum/thời kỳ và loại đối tượng. Wikipedia giúp đối chiếu và phát hiện ứng viên thiếu; không tự tạo danh mục nhà nước đầy đủ từ category hoặc liên kết.

Đề xuất này chưa triển khai crawler cơ quan/website toàn quốc. Đã có collector chuyên biệt 97 target tỉnh, snapshot, retry/cache và validator. Chưa có generic catalog adapter, bộ tìm bài cơ quan có đánh giá, extractor URL theo cấu trúc, downloader web ngoài hoặc kiểm chứng chủ thể website. Có inbox local mới dùng `inf-raw-task/0.2.0-proposed`; phiên bản này chưa được validator hiện có hỗ trợ. Không tự coi payload đó là giao thức đã được chấp nhận, không sửa hay thực thi inbox trong tác vụ nghiên cứu này.

## Bài học thực tế

- Pilot 5 target rồi 97 target; 68 bài/169 revision đã tải, 64 bài/149 revision dùng bằng chứng. Tách target theo thời kỳ dù chung tên/pageid/QID.
- Input có ID quan sát: staging giữ nguồn; không tạo ID INF hay đổi observation thành DiaBan/CoQuan.
- Hà Nam trùng tên tỉnh Trung Quốc; Hà Nội có bài tỉnh lịch sử. Tìm tên đúng không đủ: cần loại, quốc gia, địa bàn và thời kỳ.
- Ngày revision, ngày hiệu lực pháp lý, ngày vận hành là ba trường khác nhau. Một câu chứa nhiều mốc thời gian cần predicate/span cụ thể; phát hiện từ khóa “hiệu lực” gần một ngày chỉ tạo ứng viên QA, không đủ chứng minh mâu thuẫn.
- Revision Hà Nội `80/73509990`, dòng 71 có `web = {{url|hanoi.gov.vn}}`; dòng 465 có liên kết tài liệu HĐND. Dòng 71 chứng minh Wikipedia ghi địa chỉ đó cho bài Hà Nội; không chứng minh đây là website riêng của UBND hay HĐND, còn hoạt động, hoặc đúng ở mọi thời kỳ.
- Resume/chống trùng, checksum và giữ lỗi mạng riêng đã có kiểm thử. Mức chính xác đối sánh cơ quan và URL chưa được đo.

## Kết quả riêng cho mỗi target

| Trục | Trạng thái | Ý nghĩa |
|---|---|---|
| Bài riêng | found / not_found / ambiguous / error | Tìm trong phạm vi truy vấn và thời kỳ đã khai báo; lỗi mạng không là không tìm thấy. |
| Nhắc trong bài khác | found / not_found / ambiguous / error / not_checked | Có span cụ thể trong bài tỉnh, danh sách hoặc bài liên quan; không nâng thành bài riêng. |
| Website được nguồn dẫn | found / not_found / ambiguous / error / not_checked | Có URL trong revision hoặc nguồn bổ sung; không suy không tồn tại website ngoài Wikipedia. |
| Xác minh chủ thể website | verified / unverified / conflicting / historical | Câu nhận diện chủ thể, cơ quan chủ quản và thời kỳ; miền gov.vn là tín hiệu, không tự chứng minh chủ thể. |
| Tải từng URL | downloaded / http_error / network_error / blocked_policy / unsupported / not_attempted | Chỉ downloaded khi đã lưu bytes và kiểm tra hash; URL tồn tại không đồng nghĩa tải thành công. |

`not_found` phải ghi phạm vi, truy vấn, số kết quả đã xét và giới hạn. Chạm giới hạn tìm kiếm/phân trang hoặc chưa kiểm tra không được biến thành kết luận không tồn tại. Báo cáo ghi “chưa tìm thấy trong phạm vi đã xét”. Website status tổng hợp không được che lỗi ở URL con.

## Luồng xử lý đề xuất

1. INF chủ động chuyển request và toàn bộ payload vào inbox RAW; RAW không đọc, tìm kiếm hay tải từ IN/INF. INF đóng băng catalog địa bàn rồi catalog cơ quan, khai báo mốc lịch sử, loại đơn vị và phạm vi “cơ quan nhà nước”. Tách đơn vị sự nghiệp/doanh nghiệp nhà nước/khối Đảng nếu danh mục có; không tự gộp vào CoQuan. Đơn vị cấp huyện lịch sử vẫn được đối soát khi nằm trong catalog lịch sử. Các cấp/loại lấy từ input ontology, không hardcode hiện trạng theo năm crawl.
2. RAW chỉ tiếp nhận bản đã được chuyển vào RAW, kiểm tra hash và ACK theo phiên bản được hỗ trợ; thiếu payload thì trả yêu cầu bổ sung qua outbox, không dereference đường dẫn INF; phiên bản lạ nhận trạng thái unsupported_version, giữ request nguyên bản. Entity ref opaque giữ nguyên loại do INF khai báo. Target local bao gồm nguồn + item + mốc. Cơ quan–địa bàn phải chỉ rõ jurisdiction, seat hoặc relation_unspecified: trụ sở trên địa bàn không đồng nghĩa thẩm quyền quản lý địa bàn đó.
3. Dùng `crawl-wikipedia-diaban`, `crawl-wikipedia-coquan`, `resolve-wikipedia-entity` theo target. Tìm title/alias/địa bàn/loại, resolve redirect, kiểm tra định hướng rồi search có giới hạn công khai. Tìm mention/danh sách riêng khi không có bài cơ quan; giữ candidates và lý do loại. Không tự nhận mọi cơ quan được nhắc là một INF target mới; trả catalog_gap_candidates cho INF xét.
4. Lưu response nguyên bản + wikitext đúng revision, timestamp, locator, checksum và ghi công. Giữ assertion ở cấp câu/predicate, tách nguồn input và Wikipedia. Website bổ sung không thay kết quả Wikipedia.
5. Dùng skill mới [discover-wikipedia-websites](../skills/discover-wikipedia-websites/SKILL.md): trích infobox, mục liên kết ngoài, references và liên kết từ bài có mention. Phân loại URL theo role, không chỉ domain. Wikidata P856 chỉ bổ sung khi QID đã đối sánh, ghi nguồn Wikidata/revision/statement ID/qualifier riêng.
6. Kiểm tra chủ thể/thời kỳ rồi tải tập URL được chọn trong ngân sách. Lưu requested_url, redirect chain, final_url, HTTP status, fetched_at, MIME, bytes, checksum và rights riêng từng site. Bản HTML/PDF gốc khác bản text/Markdown dẫn xuất. Chia sẻ cache artifact theo hash nhưng giữ mọi cạnh target–source.
7. Trả manifest target–page–revision–span–URL–artifact, coverage và missing-fields cho INF. RAW không ghi INF. Địa bàn hoàn thành pilot trước, sau đó cơ quan trên địa bàn đó; tầng trung ương cần catalog riêng, không chỉ mở rộng cây địa bàn.

## Download web bên ngoài

Mặc định pilot: lưu tất cả link ứng viên đã phát hiện; chọn tối đa 5 URL có liên hệ rõ/target (trang chủ, giới thiệu/liên hệ, tài liệu được dẫn). Chỉ tải URL đã chọn, depth=0; không tự crawl toàn website. Mỗi host 1 request đồng thời, khoảng cách tối thiểu 1 giây hoặc dài hơn theo quy tắc host; tối đa 3 lần thử/URL, 30 giây timeout, 20 MiB/response và ngân sách tổng do request khai báo. Đây là cấu hình đề xuất, cần kiểm thử thực tế và điều chỉnh theo nguồn.

Tuân thủ robots và điều kiện nguồn, giữ lỗi TLS/robots/403/429 riêng, không vượt chặn. Kiểm tra HTTP(S), DNS/IP công khai ở từng redirect; chặn địa chỉ nội bộ, URL có credential và redirect ra tài nguyên cục bộ. Không gửi cookie/token; header metadata chỉ giữ danh sách cho phép. Kiểm tra kích thước khi streaming, không chỉ Content-Length. Khi quá giới hạn giữ trạng thái/bytes chẩn đoán riêng, không gắn nhãn snapshot hoàn chỉnh. Trang cần JS chỉ đánh dấu chưa trích được nội dung, không nhận challenge/login page là nội dung mục tiêu.

Giấy phép Wikipedia không bao trùm website ngoài. Lưu rights=unknown khi chưa rõ; gói công khai chỉ chứa artifact đủ quyền tái phân phối. Bản tải phục vụ nội bộ và manifest công khai phải tách khi cần. Bản live tải năm 2026 không chứng minh website của cơ quan năm 2025; bản lưu trữ lịch sử là nguồn riêng có timestamp và provenance riêng.

## Mở rộng hợp đồng và ontology (thiết kế, chưa phát hành)

[Thiết kế record](doi-soat-website-record-design.md) đề xuất nhiều nguồn trên mỗi observation và kết quả bài/mention/website độc lập. Không sửa nghĩa schema 0.1.0 hoặc nhận `inf-raw-task/0.2.0-proposed` ngầm định. Chốt namespace, migration và validator cùng INF trước khi công bố supported_versions mới.

Giữ `legal:DiaBan`, `legal:CoQuan` cho thực thể được INF phân loại; `wiki:ObservationTarget` cho staging. Đề xuất lớp `WebsiteCandidate`, `WebSnapshot`, `SourceAssertion` trong namespace wiki; quan hệ assertion có subject_ref, predicate, object, period, source_revision, span. Không dùng owl:sameAs cho website/page và cơ quan; nhiều cơ quan có thể dùng một portal, một cơ quan có thể có nhiều URL theo thời kỳ. Các lớp mới chỉ là đề xuất, chưa có trong ontology.ttl đang phát hành.

## Pilot và tiêu chí nhận skill

- Discovery pilot tối đa 15 target cơ quan: 4 loại UBND, HĐND, Sở Nội vụ, Sở Tài chính × 3 bối cảnh Gia Lai cũ/Bình Định cũ/Gia Lai mới = 12; tối đa 3 đơn vị sự nghiệp chỉ khi input có nguồn và người dùng đưa vào phạm vi. Đây là mẫu thiết kế, chưa khẳng định đã đủ catalog hoặc ID.
- Chọn 12 ca website từ nguồn thật sau discovery: trang riêng, mention-only, portal dùng chung, domain cũ đổi chủ/redirect, không thấy link, lỗi mạng. Phân biệt trường hợp chưa có bằng chứng; không tạo ca negative giả từ việc chưa tìm.
- Bộ 97 target đã dùng rút bài học là regression, không là bộ đánh giá độc lập. Trước đánh giá, đóng băng validation 24 ca và test 12 ca ngoài tập này, đa dạng tỉnh/xã/cơ quan TW/địa phương và lịch sử. Gold về target/URL có provenance, được review trước khi chạy baseline/candidate; người đánh giá không đưa đáp án wiki cho agent thực thi. Số ca là kế hoạch, chưa có dataset/gold.
- Hard fail: sai thực thể được chấp nhận, lấy bài tỉnh làm bài UBND, trộn hai thời kỳ, gán URL báo chí là website cơ quan, sửa INF, bịa nguồn hoặc không giữ bytes/hash. Báo riêng precision của accepted matches và accepted website-owner relations; coverage trên toàn catalog; retrieval success; error rate; bytes/requests và chi phí.
- Chỉ accepted-evolution khi điểm nhiệm vụ trên cùng validation tăng, không hard fail và regression PASS. Nếu chỉ thêm tài liệu hoặc unit tests: configured/deferred; không nói đã cải thiện độ chính xác.

## Việc cần triển khai sau đề xuất

1. Catalog adapter và hợp đồng version mới hỗ trợ observation + assertion + many-to-many; receiver/ACK có idempotency.
2. Tách downloader Wikipedia dùng chung khỏi cấu hình NQ202; thêm search/continuation, resolver cơ quan và context evidence.
3. URL extractor theo AST/rendered evidence, P856 adapter, phân loại chủ thể/thời kỳ và web fetcher theo giới hạn nêu trên.
4. Pilot thực tế, gold validation độc lập và quality report; mới mở rộng theo lô catalog, địa bàn trước/cơ quan sau.

## Nguồn nghiên cứu

- [WikiSkill, Google Research/Virginia Tech](https://arxiv.org/html/2608.27454v1): tách raw/wiki/skills, tích lũy bài học và chỉ nhận thay đổi qua validation; đây là vận dụng nghiên cứu, không phải chứng nhận Google.
- [MediaWiki Search](https://www.mediawiki.org/wiki/API:Search), [Extlinks](https://www.mediawiki.org/wiki/API:Extlinks), [Parsing wikitext](https://www.mediawiki.org/wiki/API:Parsing_wikitext): search là tìm ứng viên; query extlinks phản ánh bản hiện tại. Khi cần revision dùng parse oldid hoặc wikitext đã đóng băng. Parse oldid không tự đóng băng mọi template/Wikidata phụ thuộc; lưu response render và provenance của các phụ thuộc nếu dùng làm bằng chứng lịch sử.
- [Wikidata P856](https://www.wikidata.org/wiki/Property:P856), [Data access](https://www.wikidata.org/wiki/Wikidata:Data_access): website chính thức là statement bổ sung; giữ qualifiers/references và revision của item, không gán là nội dung Wikipedia.
- [MediaWiki etiquette](https://www.mediawiki.org/wiki/API:Etiquette): client nhận diện, giới hạn tải và xử lý server load; [RFC9309](https://www.rfc-editor.org/rfc/rfc9309.html) mô tả robots, không phải giấy phép nội dung.
- [Scrapy jobs](https://docs.scrapy.org/en/latest/topics/jobs.html): tham khảo lưu hàng đợi và trạng thái resume; không cần chuyển engine ở pilot. Checkpoint của repo vẫn phải kiểm tra version/hash và không gộp target theo URL.
