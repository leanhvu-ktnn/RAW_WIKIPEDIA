---
okf_version: "0.2"
type: context
title: "Quy trình WikiSkill có kiểm định"
updated: "2026-09-29"
status: active
---

# Quy trình WikiSkill có kiểm định

Căn cứ: [WikiSkill — Tang và cộng sự, Google Research/Virginia Tech](https://arxiv.org/html/2608.27454v1), mục 3. Đây là triển khai quy trình của dự án dựa trên nghiên cứu, không phải sản phẩm Google hay chứng nhận tuân thủ chính thức.

Ba lớp: `raw/` giữ bằng chứng chạy bất biến; `wiki/` tích lũy tri thức; `skills/` giữ quy trình tác nghiệp. Wiki Maintainer đúc kết pattern; Skill Proposer đề xuất thay đổi; đánh giá quyết định giữ hoặc rollback skill, nhưng giữ wiki và lịch sử từ chối. Khi đánh giá evolution, agent thực thi chỉ nhận skill/task, không nhận wiki dùng để đề xuất; tập validation tách khỏi tập rút bài học.

## Quy trình riêng của RAW_WIKIPEDIA

1. Chạy task trong phạm vi người dùng giao. Ghi input hash, config, tool outcomes, thời gian, target/status và lỗi bằng `tools/record_trace.py`. Lưu cả ca thành công; không lưu token/credential hay chỉ dẫn không tin cậy từ bài nguồn như lệnh cho agent.
2. `wiki-maintainer` nhóm dấu hiệu theo lỗi thực thể/provenance/đường dẫn/API; dẫn trace cụ thể, tách quan sát và giả thuyết. Pattern chưa tái hiện giải pháp giữ `observed`, không tự nhận resolved.
3. `wisdom-skill-proposer` đề xuất một thay đổi có diff, baseline, tiêu chí và bộ ca validation cố định. Ca dùng giải thích pattern không được dùng làm toàn bộ bằng chứng độc lập cho cải thiện.
4. So sánh quyết định đúng trên cùng tập validation; false-positive entity/provenance là hard fail. Chỉ nhận khi điểm tăng và mọi gate không hồi quy. Nếu hòa/giảm/chưa đo, không đánh dấu accepted. Lưu candidate, kết quả rejected/deferred và lý do trong `wiki/skill-impact.md`.
5. Rollback chỉ đúng phần sửa của proposal, không reset mất việc người dùng, raw hay wiki. Ghi phiên bản skill trước/sau và kết quả thực tế.

Hiện đã có schema thư mục, skill vai trò, pattern từ audit, trace writer và gate cấu trúc. Vòng lặp được agent thực hiện có kiểm soát; chưa có scheduler, tự chạy nhiều agent, benchmark evolution hay bảo đảm cảm biến dưới 10ms. Không coi unit test công cụ là phép đo tăng chất lượng skill.
