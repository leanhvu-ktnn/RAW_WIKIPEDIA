---
okf_version: "0.2"
type: context
title: "Tham khảo các dự án RAW trước"
updated: "2026-09-29"
status: active
---

# Tham khảo các dự án RAW trước

Đã đọc trực tiếp AGENTS, context và skill trong các kho cùng workspace; chỉ kế thừa cấu trúc phù hợp Wikipedia.

| Dự án | Điều kế thừa | Điều không áp dụng máy móc |
|---|---|---|
| RAW/tulieuvankien | context riêng, hub OKF, skills catalog, wiki-maintainer, proposer, gates | Không lấy quy tắc tải binary/robots của cổng Đảng áp cho Wikipedia. |
| RAW/dvcqg-tthc | ontology riêng, tách định danh nghiệp vụ, skill audit và sync | Không dùng UUID TTHC làm khóa bài/địa bàn, không kế thừa tuyên bố cảm biến dưới 10ms chưa đo. |
| RAW/hethongphapluat | WikiSkill có bằng chứng và ghi rõ giới hạn triển khai | Không kế thừa daily sync hoặc các thuộc tính hiệu lực văn bản pháp luật cho bài Wikipedia. |
| INF/context/nghiencuu | Phân biệt diaBan/capDonVi/capHanhChinh/theHe, namespace legal | Không đồng nhất bài Wikipedia với thực thể hay ghi đè tên pháp lý. |

Các đường dẫn trên là nguồn ngoài vault, không phải file đã đóng gói. Căn cứ nghiên cứu gốc: [WikiSkill](https://arxiv.org/abs/2608.27454). Dự án bên thứ ba mang tên WikiSkill không mặc nhiên là implementation chính thức Google. Tham khảo crawler và parser nằm trong [[context/nghien-cuu-2026-09-29|báo cáo nghiên cứu]].
