---
okf_version: "0.2"
type: index
title: "RAW/WIKIPEDIA/DiaBan — địa bàn (OKF)"
updated: 2026-09-01
tags: [RAW, wikipedia, DiaBan]
---

# DiaBan

Một đơn vị địa bàn = một thư mục + `index.md`. Ontology liên kết: [[INF/context/nghiencuu/Thuoctinh_dia_ban_va_cap|Thuoctinh_dia_ban_va_cap]]. Hub: [[RAW/WIKIPEDIA/index|RAW/WIKIPEDIA]].

## YAML bắt buộc (ngoài schema wiki_page chung)

- `wikipedia` — URL bài vi.wikipedia (cùng `source_url`)
- `website` — URL cổng chính thức; `""` nếu Wikidata/infobox không có

Thân file: mục `## Liên kết` với hai dòng Wikipedia + Website.

```text
DiaBan/TW/{slug}/
DiaBan/Tinh/{slug}/
DiaBan/Huyen/{slug}/     # chỉ bài lịch sử / đã giải thể
DiaBan/Xa/{tinh}/{slug}/
```
