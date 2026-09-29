---
okf_version: "0.2"
type: log
title: "Skill impact"
updated: "2026-09-29"
status: active
---

# Skill impact

| Proposal | Nguồn | Trạng thái | Đo trước/sau | Kết luận |
|---|---|---|---|---|
| bootstrap-2026-09-29 | Audit legacy, PAT-001/002/003 | seeded | Chưa đo | Thiết lập skill thủ công, không gọi là cải thiện đã được kiểm chứng. |

Các proposal tiếp theo cần skill version, diff, validation IDs, score trước/sau, quyết định và lý do; giữ cả rejected/deferred.

## exchange-contract-0.1.0

Theo yêu cầu người dùng: địa bàn trước; INF phát hiện thiếu và gửi request, RAW trả evidence/report, không ghi INF. Năm skill liên quan nâng metadata.version lên 0.2.0. Trạng thái: configured; kiểm định hợp đồng và hồi quy đạt 13 test. Chưa đo hiệu quả task trước/sau, không gắn accepted-evolution. [Trace](../raw/exchange-contract-2026-09-29.json).

## coverage-websites-2026-09-29

- Nguồn: PAT-004, PAT-005; [trace](../raw/coverage-websites-2026-09-29.json) giữ baseline commit/hash của các skill hiện hữu và candidate.
- Thay đổi: thêm `discover-wikipedia-websites` 0.1.0-draft; route trong hai skill index; không thay nội dung skill đối sánh đang dùng hoặc schema 0.1.0.
- Quyết định: **deferred** cho acceptance/evolution; đã tạo candidate để nghiên cứu/chuẩn bị pilot. Chưa có điểm baseline/candidate, chưa triển khai downloader web ngoài. Không lấy unit tests/profile PASS làm chứng nhận tăng độ chính xác.
- Validation/test IDs: chưa lập dataset; kế hoạch 24 validation + 12 test ngoài 97 target NQ202, cùng hard-fail và metric trong [đề xuất](../context/de-xuat-doi-soat-dia-ban-co-quan-website.md). Đóng băng ca trước khi đánh giá.
- Nếu bị reject: gỡ candidate khỏi routing tác nghiệp hoặc sửa đúng candidate, giữ trace/pattern; không reset repo/gói cũ.

## push-only-boundary-2026-09-29

Configured theo chỉ đạo người dùng, không phải accepted-evolution: crawl địa bàn/resolve/stat 0.3.1, crawl cơ quan 0.2.1 và website candidate cập nhật ranh giới nhận input. Collector 0.1.1, 24 tests PASS gồm chặn đọc upstream/symlink; snapshot cũ không đổi. [Trace](../raw/push-only-boundary-2026-09-29.json) bổ sung hash candidate sau sửa ranh giới; trace nghiên cứu trước vẫn là lịch sử, không bị ghi đè. Receiver/ACK và downloader web ngoài vẫn chưa triển khai.
