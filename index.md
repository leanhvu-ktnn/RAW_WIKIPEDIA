---
okf_version: "0.2"
type: index
title: "RAW/WIKIPEDIA — Wikipedia tiếng Việt (đối chiếu địa bàn / cơ quan)"
updated: 2026-09-01
tags: [RAW, wikipedia, dia-ban]
---

# RAW/WIKIPEDIA

## Hệ thống vận hành độc lập

[[context/index|Context OKF 0.2]] · [[SKILLS|Skills]] · [[wiki/index|WikiSkill]] · [[context/ontology-schema|Ontology]]

**Cảnh báo kiểm kê 29/09/2026:** số liệu sóng bên dưới là lịch sử, không đồng nhất catalog hiện tại. Xem [[context/nghien-cuu-2026-09-29|báo cáo kiểm kê]] trước khi crawl tiếp.

Corpus **đối chiếu** từ [vi.wikipedia.org](https://vi.wikipedia.org) (OKF v0.2). Không thay [[INF/context/DANH_MUC_DVHC.tsv|DANH_MUC_DVHC]] (QĐ 19) hay `ten` trên [[INF/COQUAN_DONVI/index|COQUAN_DONVI]].

Khác [[KLG/concepts/wiki/index|KLG/concepts/wiki]] (hub Knowledge). HOW: [[RAW/context/nguon/wikipedia/index|wikipedia]]. Ontology: [[INF/context/nghiencuu/Thuoctinh_dia_ban_va_cap|Thuoctinh_dia_ban_va_cap]].

## Cây

```text
RAW/WIKIPEDIA/
  DiaBan/{TW|Tinh|Huyen}/{slug}/index.md
  DiaBan/Xa/{tinh}/{slug}/index.md
  CoQuan/{TW|Tinh}/{slug}/index.md
  CoQuan/Xa/{tinh}/{slug}/index.md   # chỉ bài UBND riêng
```

`Huyen` chỉ bài lịch sử / đã giải thể (`capHanhChinh: huyen` + `da_dung`). License mỗi file: CC BY-SA 4.0 + `wiki_title` + `oldid`.

**DiaBan — bắt buộc hai link:** YAML `wikipedia` + `website` và mục `## Liên kết` trên trang. Spec: [[RAW/WIKIPEDIA/DiaBan/index|DiaBan]] · [[INF/context/nghiencuu/Thuoctinh_dia_ban_va_cap|Thuoctinh_dia_ban_va_cap]].

<!-- WAVE_B_STATS -->
## Sóng B — 2026-09-01

Thử **131** · hit **130** · miss **1**.

| Nhóm | Thử | Hit | Miss |
|------|-----|-----|------|
| TW / chính quyền 2 cấp | 3 | 3 | 0 |
| Tỉnh / TP | 34 | 34 | 0 |
| Xã Đà Nẵng | 94 | 93 | 1 |

### Miss (không có bài / định hướng)

- Xã Chiến Đàn

<!-- /WAVE_B_STATS -->

<!-- WAVE_C_STATS -->
## Sóng C — 2026-09-01

Thử **3321** · hit **3181** · miss **57** · bỏ qua đã có **83**.

| Nhóm | Thử | Hit | Miss |
|------|-----|-----|------|
| Xã | 3321 | 3181 | 57 |

Miss **57** — không liệt kê hết (xem `_catalog.jsonl`). Ví dụ:

- PhườngÔ Chợ Dừa
- XãÔ Diên
- XãỨng Thiên
- XãỨng Hòa
- XãYên Thành
- PhườngÂu Lâu
- Xã Vũ Lãng
- PhườngÂu Cơ
- Xã Băng Luân
- PhườngÁi Quốc
- XãÂn Thi
- XãÁi Quốc
- XãÝ Yên
- XãÁi Tử
- Xã Chân Mây-Lăng Cô
- Xã Chiến Đàn
- Xã la Chim
- Xã la Đal
- Xã la Tơi
- XãÂn Hảo
- XãÂn Tường
- Xã la Băng
- Xã AI Bá
- XãÔ Loan
- Xã Cư M’gar

<!-- /WAVE_C_STATS -->

<!-- WAVE_D_STATS -->
## Sóng D — 2026-09-01

Thử **3357** · hit **17** · miss **3339** · bỏ qua đã có **1**.

| Nhóm | Thử | Hit | Miss |
|------|-----|-----|------|
| Bộ / UBND-HĐND tỉnh | 83 | 17 | 65 |
| UBND xã (bài riêng) | 3274 | 0 | 3274 |

Miss **3339** — không liệt kê hết (xem `_catalog.jsonl`). Ví dụ:

- Ủy ban nhân dân tỉnh Cao Bằng
- Hội đồng nhân dân tỉnh Cao Bằng
- Ủy ban nhân dân tỉnh Tuyên Quang
- Hội đồng nhân dân tỉnh Tuyên Quang
- Ủy ban nhân dân tỉnh Điện Biên
- Hội đồng nhân dân tỉnh Điện Biên
- Ủy ban nhân dân tỉnh Lai Châu
- Hội đồng nhân dân tỉnh Lai Châu
- Ủy ban nhân dân tỉnh Sơn La
- Hội đồng nhân dân tỉnh Sơn La
- Ủy ban nhân dân tỉnh Lào Cai
- Hội đồng nhân dân tỉnh Lào Cai
- Ủy ban nhân dân tỉnh Thái Nguyên
- Hội đồng nhân dân tỉnh Thái Nguyên
- Ủy ban nhân dân tỉnh Lạng Sơn
- Hội đồng nhân dân tỉnh Lạng Sơn
- Ủy ban nhân dân tỉnh Quảng Ninh
- Hội đồng nhân dân tỉnh Quảng Ninh
- Ủy ban nhân dân tỉnh Bắc Ninh
- Hội đồng nhân dân tỉnh Bắc Ninh
- Ủy ban nhân dân tỉnh Phú Thọ
- Hội đồng nhân dân tỉnh Phú Thọ
- Ủy ban nhân dân thành phố Hải Phòng
- Hội đồng nhân dân thành phố Hải Phòng
- Ủy ban nhân dân tỉnh Hưng Yên

<!-- /WAVE_D_STATS -->

## Liên kết

- Nghiên cứu: [[RAW/context/nghien-cuu/Crawl_Plan_wikipedia|Crawl_Plan_wikipedia]]
- Catalog nguồn: [[RAW/status/nguon-du-lieu]]
- Lưu trữ: [[RAW/context/luutru/theo-nguon]]
