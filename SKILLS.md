---
okf_version: "0.2"
type: index
title: "Điều phối skill Wikipedia"
updated: "2026-09-29"
status: active
---

# Điều phối skill Wikipedia

- [[skills/crawl-wikipedia-diaban/SKILL|crawl-wikipedia-diaban]] — Lập và thực hiện đợt thu thập Wikipedia cho địa bàn Việt Nam theo danh mục chuẩn, ontology và revision; ưu tiên khi người dùng yêu cầu crawl tỉnh, xã hoặc địa bàn lịch sử.
- [[skills/crawl-wikipedia-coquan/SKILL|crawl-wikipedia-coquan]] — Lập và thực hiện đợt thu thập bài riêng về Bộ, cơ quan, UBND và HĐND từ Wikipedia; phân biệt cơ quan với địa bàn cùng tên.
- [[skills/resolve-wikipedia-entity/SKILL|resolve-wikipedia-entity]] — Đối sánh ứng viên Wikipedia với thực thể địa bàn hoặc cơ quan, xử lý trùng tên, redirect, định hướng và sai thời kỳ trước khi chấp nhận hit.
- [[skills/stat-wikipedia/SKILL|stat-wikipedia]] — Kiểm kê cấu trúc corpus Wikipedia, kiểm tra manifest, pageid, provenance, ontology và hệ thống skill; phân biệt lỗi legacy với kết quả mới.
- [[skills/ontology-wikipedia/SKILL|ontology-wikipedia]] — Thiết lập hoặc kiểm định mapping ontology cho địa bàn, cơ quan và provenance Wikipedia; dùng khi thay schema hoặc chuẩn bị xuất RDF.
- [[skills/wiki-maintainer/SKILL|wiki-maintainer]] — Đúc kết trace thực thi RAW_WIKIPEDIA thành pattern có bằng chứng, cập nhật wiki và nhật ký tích lũy mà không tự nhận skill đã cải thiện.
- [[skills/wisdom-skill-proposer/SKILL|wisdom-skill-proposer]] — Đề xuất và đánh giá một thay đổi skill Wikipedia dựa trên pattern; ghi baseline, validation và quyết định giữ hoặc rollback có bằng chứng.
- [[skills/sync-wikipedia-github/SKILL|sync-wikipedia-github]] — Đồng bộ RAW_WIKIPEDIA với GitHub khi người dùng yêu cầu, kiểm tra quyền, remote, diff, gate và SHA sau push.

Skill là quy trình agent; không chứng minh đã có crawler production. Agent đọc đúng SKILL.md khi nhận task phù hợp. Vị trí skills/ là nguồn dùng chung của kho; không tự cài skill vào cấu hình cá nhân.
