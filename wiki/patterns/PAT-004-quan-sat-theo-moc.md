---
okf_version: "0.2"
type: pattern
title: "Giữ ID quan sát và thời kỳ độc lập"
updated: "2026-09-29"
status: active
---

# Giữ ID quan sát và thời kỳ độc lập

## Quan sát

97 target gồm 63 trước và 34 sau NQ202/2025 chỉ dùng 64 bài Wikipedia làm bằng chứng. Hà Nội hai mốc dùng chung pageid; Gia Lai cùng tên không chứng minh tỉnh cũ và tỉnh mới là một thực thể. Bài Hà Nam không định danh quốc gia có thể dẫn sang tỉnh Trung Quốc.

## Bằng chứng

[Trace kiểm định](../../raw/province-nq202-2026-09-29.json) và [báo cáo gói](../../packages/province-before-after-2025/report.md). Trạng thái observed, không phải benchmark độ chính xác đối sánh.

## Áp dụng

Dùng staging có nguồn gốc cho ID quan sát chưa canonical, target tách theo mốc; quan hệ target–page–revision là nhiều–nhiều. Tìm bằng tên có quốc gia/loại khi mơ hồ. Ngày revision không thay bằng chứng nội dung về thời kỳ. Lỗi mạng giữ error; không chuyển thành not_found.
