---
okf_version: "0.2"
type: context
title: "Quy ước liên kết"
updated: "2026-09-29"
status: active
---

# Quy ước liên kết

Wikilink mới dùng đường dẫn từ root kho, bỏ `.md`: `[[context/index|Context]]`. Trong bảng escape dấu phân cách thành `\|`. Link tới file RDF/JSON/script dùng Markdown tương đối; link web dùng URL đầy đủ.

Các link `INF/...`, `RAW/context/...` cũ là tham chiếu vault ngoài, không tự coi chúng tồn tại trong kho GitHub. Tài liệu mới phải dùng context local hoặc ghi rõ nguồn ngoài. Không ghi số hiệu có dấu `/` thành wikilink trần. Không rewrite hàng loạt link legacy khi chưa có mapping kiểm chứng.
