---
name: wisdom-skill-proposer
description: Đề xuất và đánh giá một thay đổi skill Wikipedia dựa trên pattern; ghi baseline, validation và quyết định giữ hoặc rollback có bằng chứng.
metadata:
  okf_version: "0.2"
  type: skill
  version: "0.1.0"
---

# wisdom-skill-proposer

## Mục đích và runbook
Đọc [quy trình](../../context/quy-trinh-wikiskill.md), [impact](../../wiki/skill-impact.md) và pattern liên quan.

1. Chọn một pattern có trace, lưu phiên bản skill trước và diff dự kiến. Định nghĩa tiêu chí chấp nhận trước thử nghiệm.
2. Tách ca rút bài học khỏi validation/test; khi thực hiện đánh giá skill, agent làm task chỉ nhận task/skill, không nhận wiki đáp án. Không tự chọn model khác hoặc spawn agent khi chưa được phép.
3. Chạy cùng tập validation cho baseline và candidate; lưu outcome từng ca. Hard fail nếu chấp nhận sai thực thể, bịa provenance hoặc vi phạm giới hạn nguồn. Chỉ accept khi điểm tăng và gate hệ thống/regression đều đạt.
4. Ghi accepted/rejected/deferred cùng trace, version, score và lý do. Unit test cấu trúc không thay phép đo hiệu quả skill; chưa có đánh giá thì deferred.
5. Nếu reject, hoàn tác riêng bản sửa proposal, giữ raw và wiki. Không dùng reset --hard làm mất thay đổi người dùng.

## Phục hồi
Nếu không đủ dữ liệu validation, chuẩn bị đề xuất reviewable và ghi chưa đánh giá; không bịa điểm hay tự coi đã tối ưu.
