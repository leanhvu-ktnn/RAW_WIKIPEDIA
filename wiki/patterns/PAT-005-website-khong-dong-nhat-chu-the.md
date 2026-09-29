---
okf_version: "0.2"
type: pattern
title: "Link website không đồng nhất với chủ thể"
updated: "2026-09-29"
status: active
---

# Link website không đồng nhất với chủ thể

## Quan sát và bằng chứng

[Trace nghiên cứu](../../raw/coverage-websites-2026-09-29.json) giữ hash wikitext Hà Nội 80/73509990: dòng 71 khai báo web hanoi.gov.vn, dòng 465 dẫn tài liệu HĐND. Một revision chứa cả portal địa bàn, nguồn cơ quan và nguồn báo chí. Đây là quan sát về nội dung đã tải, chưa là kiểm tra live website hoặc lỗi owner-matching đã tái hiện.

## Hệ quả và giả thuyết

Dùng mọi external link làm official website có nguy cơ gán sai chủ thể. Cần tách bài riêng, mention, link role, owner verification và download outcome. Giả thuyết: phân loại theo span/chủ thể/thời kỳ giảm false-positive so với lấy mọi URL; chưa có phép đo baseline/candidate.

## Ca kiểm định đề xuất

Portal tỉnh dùng chung UBND/HĐND; URL báo chí trong citation; bài cơ quan chưa có nhưng có mention trong bài tỉnh; website cũ redirect sang portal tỉnh mới; HTTP200 là trang lỗi/challenge. Chọn nguồn thật và đóng băng gold độc lập trước đánh giá, không bịa kết quả.

## Áp dụng

[Skill candidate](../../skills/discover-wikipedia-websites/SKILL.md) và [đề xuất triển khai](../../context/de-xuat-doi-soat-dia-ban-co-quan-website.md). Trạng thái observed/deferred, chưa accepted-evolution.
