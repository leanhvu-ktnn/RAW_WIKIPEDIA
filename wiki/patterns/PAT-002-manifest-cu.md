---
okf_version: "0.2"
type: pattern
title: "Manifest lệch layout"
updated: "2026-09-29"
status: active
---

# Manifest lệch layout

## Quan sát
92 đường dẫn manifest thiếu file; ví dụ đường dẫn xã Hải Vân thiếu tầng tỉnh. 113 trang không nằm trong manifest.

## Bằng chứng
[Audit gốc](../../raw/bootstrap-2026-09-29/audit.json). Trạng thái: observed; nguyên nhân chi tiết trong crawler chưa chứng minh vì chưa tái hiện lần chạy gốc.

## Đề xuất và kiểm định
Đối chiếu pageid và mã trước migration; ghi manifest nguyên tử. Chưa chạy migration.
