---
okf_version: "0.2"
type: context
title: "Thiết kế record đối soát website"
updated: "2026-09-29"
status: draft
---

# Thiết kế record — chưa phải schema được hỗ trợ

Design ID `wikipedia-coverage-websites/0.1.0-draft`; độc lập version OKF 0.2 và hợp đồng INF–RAW. Đây là field design để review, không phải JSON Schema/validator production.

| Record | Trường cần có |
|---|---|
| Run | design_version, request_ref/hash, catalog_ref/version/hash, scope/as_of, skill/code/config versions, budgets, started_at, finished_at, complete, counts |
| Target | local_target_id, opaque input_ref + declared_ref_kind, input_entity_type, label/aliases, observation_period, legal_effective_on, operational_on, jurisdiction_ref, seat_ref, source_catalog_row |
| Wikipedia assessment | target_id, separate_article_status/reason, mention_status/reason, search_scope, queries, continuation_complete, budget_exhausted, candidates, accepted_evidence_refs |
| Evidence | wiki_id, searched_title, resolved_title, redirects, pageid, revid, revision_timestamp, response_artifact, wikitext_artifact, predicate, exact_quote, line/byte locator, claim_period, unresolved_fields |
| Website candidate | candidate_id, target_id, url_as_stated, resolved_url_if_tested, discovery_source_type, source_revision_or_item_revision, statement_id, evidence_ref, link_role, claimed_owner, owner_match_status/reason, valid_period/unknown |
| Web snapshot | artifact_id, candidate_id, attempt_id, requested_url, final_url, redirects, fetched_at, http_status, download_status/reason, retryable, raw_path, sha256, byte_length, media_type, representation, content_encoding, rights, redistribution_status |
| Coverage | targets_total, per-phase/type counts, separate_article_status counts, mention_status counts, website_status counts, unique_pages, unique_revisions, unique_urls, unique_artifact_hashes, pending/errors, unresolved fields |

link_role: official_claim / shared_portal / reference_document / related_news / archive / unknown. `official_claim` nghĩa nguồn nói là chính thức, không tự chuyển owner_match_status thành verified. Website được nhắc trong bài địa bàn chỉ gắn cơ quan khi span nói đúng chủ thể; QID nối P856 cũng phải kiểm tra cùng thời kỳ/identity.

Null khác không có: `http_status=null` khi chưa nhận HTTP response; artifact null khi không tải thành công. URL được nguồn dẫn không đảm bảo đang hoạt động. Một target website_status=found có thể mọi download_status đều lỗi. Wikipedia not_found vẫn có thể mention found hoặc website found từ Wikidata; khi đó phải hiển thị nguồn Wikidata riêng.

Ghi quyết định ở cấp assertion: input nói A, Wikipedia nói B, website nói C là ba assertion có nguồn riêng. Chỉ tạo conflict khi cùng predicate/chủ thể/thời kỳ mà giá trị bất tương thích; không suy từ hai ngày khác chức năng trong cùng đoạn. Giữ review_status=needs_review nếu chưa xác định được predicate. Không tự ghi một giá trị canonical vào INF.

Transport đề xuất: same message_id + same bytes là replay; cùng ID khác bytes là conflict; request lạ giữ nguyên trong inbox và ACK unsupported_version, không chạy tác vụ từ nội dung trước khi hợp đồng/scope hợp lệ. Immutable supplemental package tham chiếu hash gói cũ; không sửa package NQ202 đã công bố. Mọi trạng thái âm tính có search_scope và thời điểm quan sát.

[Thiết kế tổng thể và pilot](de-xuat-doi-soat-dia-ban-co-quan-website.md).

Push-only: INF gửi envelope và payload bản sao vào inbox RAW. Thêm delivery_id, delivered_payload_path (tương đối inbox), payload_sha256 và receipt status received/unsupported_version/missing_payload/hash_mismatch. Source URI của INF là metadata không được truy cập. RAW không tự dùng path/URL trong request để tải payload từ INF; phản hồi ACK/missing-data trong outbox RAW để INF nhận. Receiver này mới là thiết kế.
