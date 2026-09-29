---
name: sync-wikipedia-github
description: Đồng bộ RAW_WIKIPEDIA với GitHub khi người dùng yêu cầu, kiểm tra quyền, remote, diff, gate và SHA sau push.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0"
---

# sync-wikipedia-github

## Mục đích và runbook
Remote dự kiến `https://github.com/leanhvu-ktnn/RAW_WIKIPEDIA.git`. Đọc [kế hoạch/gate](../../context/ke-hoach.md).

1. Kiểm tra status, remote và fetch. Remote rỗng có thể init lần đầu; đã có lịch sử thì so nhánh và diff trước thay đổi. Giữ file ngoài phạm vi.
2. Chạy gate hệ thống, tests và audit strict; ghi rõ nợ legacy. Không trình bày baseline lỗi như đã sạch.
3. Stage đúng file, kiểm tra diff và tệp nhạy cảm/đường dẫn máy; commit với nội dung có thể review. Không force push. Khi remote có main, ưu tiên nhánh/PR cho sửa đổi tiếp theo.
4. Push trong phạm vi được giao; kiểm tra local HEAD bằng remote ref. Không báo đồng bộ khi push lỗi hoặc chưa kiểm tra SHA. Nếu tạo PR, đính kèm PR vào chat bằng tool tương ứng.

## Phục hồi
Fetch lại khi remote tiến lên, giải quyết conflict có kiểm soát; không ghi đè. Thiếu quyền thì giữ commit local và báo giới hạn cụ thể.
