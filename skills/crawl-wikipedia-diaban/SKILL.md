---
name: crawl-wikipedia-diaban
description: Lập và thực hiện đợt thu thập Wikipedia cho địa bàn Việt Nam theo danh mục chuẩn, ontology và revision; ưu tiên khi người dùng yêu cầu crawl tỉnh, xã hoặc địa bàn lịch sử.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0"
---

# crawl-wikipedia-diaban

## Mục đích và đầu vào
Thu thập đúng địa bàn, không chỉ bài trùng tên. Đọc [mục tiêu](../../context/muc-tieu.md), [quy chuẩn](../../context/quy-chuan-crawl.md) và [ontology](../../context/ontology-schema.md). Input có phiên bản, tên/mã chuỗi, tỉnh, cấp, thời kỳ và nguồn.

## Runbook
1. Kiểm kê bằng `python3 tools/audit_corpus.py`; lập danh sách target cần xử lý, giữ kết quả cũ có provenance.
2. Chuẩn hóa NFC/khoảng trắng, sinh ứng viên tên đầy đủ + tỉnh; dùng `resolve-wikipedia-entity` để duyệt bằng chứng. Cấp xã không được nhận bài tỉnh như lỗi Phú Thọ. Huyện và địa bàn cũ phải có trạng thái/thời kỳ lịch sử.
3. Nếu có API tool phù hợp, thực hiện pilot trong phạm vi yêu cầu, tuân thủ User-Agent/maxlag/backoff; nếu xây client mới, triển khai và kiểm thử các gate trước. Hiện chưa có engine production, không gọi script download không tồn tại.
4. Chỉ ghi hit khi có raw snapshot đúng revision, match evidence và attribution. `website` rỗng nếu không xác minh được; `wikipedia` bằng `source_url`. Đường dẫn xã bắt buộc tầng tỉnh. Không bịa nội dung cho target missing.
5. Ghi catalog trạng thái riêng với manifest hit, run_id và trace; audit output mới, báo target/hit/missing/ambiguous/error và phần cần review. Dùng `stat-wikipedia` nghiệm thu; chỉ đồng bộ Git khi thuộc yêu cầu.

## Phục hồi
429/503/maxlag theo quy chuẩn; lỗi mạng không thành missing. Giữ checkpoint, không ghi đè bài tốt bằng nội dung lỗi. Không tự sửa danh mục pháp lý hoặc nâng tỷ lệ hit bằng bỏ kiểm tra tỉnh. Không crawl diện rộng trước pilot.
