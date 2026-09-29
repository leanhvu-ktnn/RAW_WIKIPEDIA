---
okf_version: "0.2"
type: index
title: "Bằng chứng thực thi WikiSkill"
updated: "2026-09-29"
status: active
---

# Bằng chứng thực thi WikiSkill

- [Audit bootstrap](bootstrap-2026-09-29/audit.json)
- [Metadata bootstrap](bootstrap-2026-09-29/trace.json)

Trace được tạo bằng `tools/record_trace.py` với ID duy nhất, không ghi đè. Bất biến ở đây được thực thi bởi create-exclusive và checksum, không phải WORM storage. File Git vẫn có thể bị người dùng sửa; đối chiếu hash để phát hiện. Thư mục corpus DiaBan/CoQuan độc lập với raw trace.

- [Kiểm định hợp đồng INF–RAW](exchange-contract-2026-09-29.json) — offline, không phải crawl.

- [Kiểm định gói 97 target NQ202](province-nq202-2026-09-29.json) — crawl thực tế, nguồn và revision có checksum.
