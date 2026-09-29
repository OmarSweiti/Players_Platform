# Phase 2 — Operational depth (BRD release 2)

> **Exit:** Approved medical, training, performance, ratings and chat workflows operate under current tenant and resource policy, with durable files, jobs and measurable recovery.

**Effort:** 44 steps (0 S / 13 M / 31 L), planning capacity up to 600 focused hours +30% reserve = 780 hours, or 31.2 weeks at 25 focused hours/week. These are sizing bounds, not a promised date; re-estimate at entry and split a step before work if it exceeds 16 hours. Status: planned, no product acceptance claimed.

All paths and signatures are implementation targets. Every new tenant table ships composite keys, ENABLE/FORCE RLS, grants and catalog tests in its own migration. Feature tests live with their domain and keep these exact names. Commands run from the umbrella; the Phase-0 harness owns the variadic recipes. The policy and provider decisions are in the [OPEN register](00-master-plan.md#open-register); safe defaults remain active until settled. Existing medical routes remain server-disabled until `2.1.8`.

```text
1.10.9 → 2.1 policy/clinical → availability ────────────────────┐
1.10.9 → 2.2 programs → 2.3 attendance/certificates ────────────┤
1.10.9 → 2.4 performance → 2.5 ratings ────────────────────────┤
1.10.9 → 2.6 conversations/messages → realtime → 2.7 push ─────┤
1.3.3 + 0.8.4 → 2.8 multipart/media ──────────────────────────┤
1.10.9 → 2.9.1 jobs → 2.4.3 import → 2.9 reporting ───────────┤
2.1.7 + 2.6.5 + 2.9 reports → 2.1.8 medical activation ───────┤
all domain leaves → 2.10 load + recovery + accessibility → release
```

Group arrows summarize; each step's dependencies below are authoritative. A later number in the same phase may be an earlier build dependency.

## Group 2.1 — Medical and rehabilitation

### 2.1.0 — Approve the medical activation policy
**Repo:** umbrella + backend · **Size:** M · **Depends on:** `1.10.9` · **Requirements:** PRD-ME-001, BR-RULE-02/07, SR-MED-001/007
**Files:** `docs/reference/security-privacy.md` · `backend/src/modules/medical/domain/medical-policy.ts` · `backend/test/medical/policy.e2e-spec.ts`
**Build:** Record the owner's and the medical lead's decisions on purpose, recipients, minors/guardians, hosting, retention, key custody and approved availability summaries. OPEN — medical policy: default disabled with synthetic fixtures only; settlement requires signed-off access scenarios and a recoverable-key exercise. Policy approval has a version; no role alone creates clinical authority.
**Tests:** `medical_activation_requires_approved_policy`
**Verify:** `(cd backend && just test-e2e -- test/medical/policy.e2e-spec.ts)`
**Done when:** The server refuses activation without a recorded approved policy version.

### 2.1.1 — Type medical records without losing legacy provenance
**Repo:** backend · **Size:** L · **Depends on:** `2.1.0` · **Requirements:** SR-MED-002/003/004, SR-DB-003/007
**Files:** `backend/prisma/schema.prisma` · `backend/prisma/migrations/<timestamp>_medical_types/migration.sql` · `backend/src/modules/medical/domain/`
**Build:** Add recordType for injury/illness/treatment/vaccination/examination/rehabilitation and controlled injury/severity/body-part dictionaries. Injury-specific fields are nullable for other types; capture civil dates and preserve unknown legacy terms in restricted provenance, never invent a mapping. New medical tables include tenant-safe FKs, FORCE RLS, grants and catalog assertions.
**Tests:** `medical_types_preserve_unknown_legacy_values` · `medical_record_types_reject_incompatible_fields`
**Verify:** `(cd backend && just test-int -- medical-types)`
**Done when:** Every required record type round-trips and ambiguous legacy values remain explicitly unresolved.

### 2.1.2 — Enforce purpose and immutable clinical amendments
**Repo:** backend · **Size:** L · **Depends on:** `2.1.1` · **Requirements:** SR-MED-001/004, BR-RULE-07, SR-AUD-002/004
**Files:** `backend/src/modules/medical/application/records.service.ts` · `backend/src/modules/medical/domain/medical.policy.ts` · `backend/test/medical/records.e2e-spec.ts`
**Build:** Implement readRecord(ctx,id,purpose) and amendRecord(ctx,id,revision,change,reason). Require active patient relationship or approved explicit recipient grant, confidential permission and permitted purpose. Audit reads before releasing content; amendments preserve prior values in restricted evidence. Apply approved versioned encryption/decrypt boundary; test tamper refusal and key recovery. Attachments use MedicalRecordDocument→FileObject and never broaden visibility.
**Tests:** `medical_unassigned_user_and_unapproved_purpose_are_denied` · `medical_amendments_preserve_prior_clinical_evidence` · `medical_ciphertext_tamper_and_key_restore_are_checked`
**Verify:** `(cd backend && just test-e2e -- test/medical/records.e2e-spec.ts)`
**Done when:** A permitted clinician can append an audited amendment while an unrelated clinician cannot retrieve the record.

### 2.1.3 — Implement treatment session transitions
**Repo:** backend · **Size:** L · **Depends on:** `2.1.2` · **Requirements:** SR-MED-005/006
**Files:** `backend/src/modules/medical/application/treatment.service.ts` · `backend/test/medical/treatment.e2e-spec.ts`
**Build:** transitionTreatment(ctx,id,expectedRevision,command) permits Scheduled→InProgress→Completed or Cancelled under explicit policy. Store startsAt instant, duration, type, description, exercises, progress and responsible medical User. Enforce same-player record/session FK, clinician eligibility and If-Match; completed narrative corrections append amendments. No physical delete through ordinary API.
**Tests:** `treatment_transition_and_responsible_clinician_are_checked` · `treatment_cannot_attach_another_players_record`
**Verify:** `(cd backend && just test-e2e -- test/medical/treatment.e2e-spec.ts)`
**Done when:** Only an eligible clinician advances a same-patient session and stale edits return 412.

### 2.1.4 — Record human return-to-play decisions
**Repo:** backend · **Size:** M · **Depends on:** `2.1.3` · **Requirements:** SR-MED-008
**Files:** `backend/src/modules/medical/application/return-to-play.service.ts` · `backend/test/medical/return-to-play.e2e-spec.ts`
**Build:** recordReturnToPlay(ctx,recordId,revision,{effectiveDate,decision,rationale}) records author, policy version and immutable assessment evidence. Validate clinician authority; predicted recovery dates never generate clearance. Correcting a decision produces a new version and safe availability event, not replacement of earlier evidence.
**Tests:** `return_to_play_requires_human_authority` · `recovery_date_never_implies_medical_clearance`
**Verify:** `(cd backend && just test-e2e -- test/medical/return-to-play.e2e-spec.ts)`
**Done when:** Return-to-play status changes only through an attributable authorized human assessment.

### 2.1.5 — Publish a minimal availability projection
**Repo:** backend · **Size:** M · **Depends on:** `2.1.4` · **Requirements:** PRD-ME-001, SR-MED-007, BR-RULE-07
**Files:** `backend/src/modules/medical/application/availability.reader.ts` · `backend/test/medical/availability.e2e-spec.ts`
**Build:** getAvailability(ctx,playerId) returns only policy-approved available/unavailable/returning status and permitted effective date. Independent field classification forbids diagnosis, treatment, clinician notes and hidden-record counts. Player 360, coaching and reports call this projection; they never join medical tables directly.
**Tests:** `availability_projection_omits_all_clinical_canaries`
**Verify:** `(cd backend && just test-e2e -- test/medical/availability.e2e-spec.ts)`
**Done when:** A coach receives the approved availability projection with no clinical values or hidden-record counts.

### 2.1.6 — Reprove medical database isolation and key recovery
**Repo:** backend · **Size:** M · **Depends on:** `2.1.5` · **Requirements:** SYS-TEN-005, SR-NFR-SEC-003, TEST-003/008
**Files:** `backend/test/integration/medical-isolation.integration-spec.ts` · `backend/prisma/migrations/` · `docs/implementation/evidence/medical-isolation.md`
**Build:** Extend the mandatory Phase-0 RLS inventory for every new medical/amendment/file-binding table. Exercise sadara_app reads/writes without context, tenant mismatch, pooled transaction reuse, UPDATE/DELETE/TRUNCATE evidence protection and restored keys. This step verifies expanded coverage; it does not defer initial RLS until Phase 2.
**Tests:** `medical_new_tables_force_rls_and_preserve_evidence`
**Verify:** `(cd backend && just test-int -- medical-isolation)`
**Done when:** Runtime-role and restored-fixture tests prove isolation for every medical table.

### 2.1.7 — Build the medical workspace
**Repo:** frontend · **Size:** L · **Depends on:** `2.1.6` · **Requirements:** PRD-ME-001, UX-003/005/008/009/011, TEST-005/009/010
**Files:** `frontend/app/[locale]/medical/` · `frontend/src/features/medical/` · `frontend/tests/medical/workspace.spec.ts`
**Build:** Implement assigned-player list, record/treatment detail, amendment form, purpose selector and human clearance action through generated client. Keep clinical content out of navigation previews and general player payloads; show confidentiality and access purpose. Test keyboard navigation, ar/en, mobile layout, permission loss and stale revision while preserving only non-sensitive draft input.
**Tests:** `medical_workspace_handles_rtl_and_revoked_access`
**Verify:** `(cd frontend && npx --no-install playwright test tests/medical/workspace.spec.ts --project=ar --project=en)`
**Done when:** An eligible clinician completes the record and treatment journey in both locales without exposing clinical content elsewhere.

### 2.1.8 — Gate medical activation against every disclosure channel
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `2.1.7`, `2.6.5`, `2.9.2`, `2.9.3` · **Requirements:** SR-MED-007, BR-RULE-07, TEST-006
**Files:** `backend/test/medical/activation.e2e-spec.ts` · `docs/implementation/evidence/medical-activation.md`
**Build:** Run a unique clinical canary across list/detail/count/search/Player360/export/notifications/chat attachments/logs/traces/object URLs/caches under own-player, guardian, coach, admin, unrelated medic and support roles. Verify approved policy, hold/retention and key drill evidence; medical owner signs activation record. Server flag remains off if any negative fails.
**Tests:** `medical_canary_is_absent_from_every_unauthorized_channel` · `medical_flag_requires_policy_and_abuse_gate`
**Verify:** `(cd backend && just test-e2e -- test/medical/activation.e2e-spec.ts)`
**Done when:** The medical owner approves evidence that every unauthorized surface omits the clinical canary.

## Group 2.2 — Training and camps

### 2.2.1 — Model training programs and governed pricing
**Repo:** backend · **Size:** L · **Depends on:** `1.10.9` · **Requirements:** SR-TR-001, PRD-TR-001, BR-OBJ-03
**Files:** `backend/src/modules/training/domain/program.ts` · `backend/prisma/schema.prisma` · `backend/test/training/programs.e2e-spec.ts`
**Build:** Create program/camp with lifecycle, title, description, civil date range, IANA zone, location, capacity, Money and versioned recurrence metadata. Validate end≥start, capacity≥0 and payable exponent. Publish/archive commands require current revision; all new owned tables ship tenant constraints, RLS/grants and catalog tests.
**Tests:** `training_program_validates_dates_capacity_and_money`
**Verify:** `(cd backend && just test-e2e -- test/training/programs.e2e-spec.ts)`
**Done when:** A valid program persists with exact currency-aware pricing and rejects invalid dates or capacity.

### 2.2.2 — Generate recurrence instances and explicit exceptions
**Repo:** backend · **Size:** L · **Depends on:** `2.2.1` · **Requirements:** SR-TR-002, SYS-ASY-002
**Files:** `backend/src/modules/training/application/schedule.service.ts` · `backend/test/training/schedule.e2e-spec.ts`
**Build:** expandSchedule(programId,horizon,ruleVersion) uses a bounded recurrence rule and unique(programId,occurrenceKey). Each session stores beginsAt/endsAt and zone. Define DST gap/fold choice, cancellation and reschedule exceptions. Editing a rule preserves completed sessions/attendance and reconciles future instances; notifications follow committed schedule state.
**Tests:** `training_recurrence_preserves_completed_sessions` · `training_dst_exception_has_one_occurrence`
**Verify:** `(cd backend && just test-e2e -- test/training/schedule.e2e-spec.ts)`
**Done when:** Retrying recurrence expansion produces no duplicate occurrence and preserves completed sessions.

### 2.2.3 — Make enrollment and waitlist capacity concurrency-safe
**Repo:** backend · **Size:** L · **Depends on:** `2.2.2` · **Requirements:** SR-TR-003/004/005, PRD-TR-001
**Files:** `backend/src/modules/training/application/enrollment.service.ts` · `backend/test/training/enrollment.e2e-spec.ts`
**Build:** approveEnrollment(ctx,id,revision,idempotencyKey) locks the capacity-bearing program row or uses serializable retry. Model Pending/Approved/Rejected/Cancelled/Waitlisted; deterministic waitlist order and one lifetime player/program record. Reenrollment reactivates through an audited command. Eligibility/capacity/audit/outbox commit together.
**Tests:** `training_last_seat_has_one_winner` · `training_reenrollment_reactivates_existing_membership`
**Verify:** `(cd backend && just test-e2e -- test/training/enrollment.e2e-spec.ts)`
**Done when:** Two concurrent approvals cannot exceed capacity or create duplicate enrollment history.

### 2.2.4 — Record operational payment observations honestly
**Repo:** backend · **Size:** M · **Depends on:** `2.2.3` · **Requirements:** SR-TR-006
**Files:** `backend/src/modules/training/application/payment-observation.service.ts` · `backend/test/training/payment-observation.e2e-spec.ts`
**Build:** Record Unpaid/Partial/Paid/Refunded/Waived observations with actor, source, date and reason under separate permission. Mark them unverified operational status until finance allocations arrive in 3.4.3; never manufacture receipts or settlement entries. Future reconciliation preserves observations as provenance.
**Tests:** `training_payment_status_is_not_settlement_evidence`
**Verify:** `(cd backend && just test-e2e -- test/training/payment-observation.e2e-spec.ts)`
**Done when:** An authorized observation changes displayed status without creating a settled-money fact.

### 2.2.5 — Build the calendar and enrollment experience
**Repo:** frontend · **Size:** L · **Depends on:** `2.2.4` · **Requirements:** PRD-TR-001, UX-003/004/008/009/011
**Files:** `frontend/app/[locale]/training/` · `frontend/src/features/training/` · `frontend/tests/training/programs.spec.ts`
**Build:** Build list/calendar, program/session editing, enrollment/waitlist actions and cancellation confirmation. Display tenant timezone, exact prices and payment provenance. Generated-client errors distinguish full capacity, stale revision and forbidden action; accessible list alternative accompanies calendar.
**Tests:** `training_calendar_and_enrollment_work_in_both_locales`
**Verify:** `(cd frontend && npx --no-install playwright test tests/training/programs.spec.ts --project=ar --project=en)`
**Done when:** A staff member schedules and enrolls a player through a capacity conflict in Arabic and English.

## Group 2.3 — Attendance, completion and certificates

### 2.3.1 — Record attendance against the correct enrollment and session
**Repo:** backend + frontend · **Size:** L · **Depends on:** `2.2.5` · **Requirements:** SR-TR-007/008, BR-RULE-08
**Files:** `backend/src/modules/training/application/attendance.service.ts` · `frontend/src/features/training/attendance/` · `backend/test/training/attendance.e2e-spec.ts`
**Build:** upsertAttendance(ctx,enrollmentId,sessionId,revision,state) permits Present/Absent/Late/Excused under roster policy. Composite FKs prove same training and tenant; unique(enrollmentId,sessionId) prevents duplication. Corrections preserve recorder/reason/audit; no silent offline overwrite. Provide roster batch action with per-row authorized outcome.
**Tests:** `attendance_rejects_wrong_training_and_duplicate_pair` · `attendance_correction_requires_revision_and_reason`
**Verify:** `(cd backend && just test-e2e -- test/training/attendance.e2e-spec.ts)`
**Done when:** Each attendance pair identifies one enrollment and same-program session with attributable corrections.

### 2.3.2 — Version program completion rules
**Repo:** backend · **Size:** M · **Depends on:** `2.3.1` · **Requirements:** SR-TR-009, BR-OBJ-03
**Files:** `backend/src/modules/training/domain/completion.ts` · `backend/test/integration/training-completion.integration-spec.ts`
**Build:** evaluateCompletion(ruleVersion,attendanceSnapshot): CompletionDecision uses approved thresholds and cancellation/excusal treatment. Publish immutable rule versions; eligibility stores inputs and rule ID so later rules cannot rewrite historical completion. Undefined policy denies issuance rather than choosing a threshold silently.
**Tests:** `completion_uses_captured_rule_and_attendance_snapshot`
**Verify:** `(cd backend && just test-int -- training-completion)`
**Done when:** The same captured rule and attendance snapshot always produce the same completion decision.

### 2.3.3 — Issue immutable bilingual certificates
**Repo:** backend · **Size:** L · **Depends on:** `2.3.2` · **Requirements:** SR-TR-010, PRD-TR-002, SYS-ASY-001
**Files:** `backend/src/modules/training/application/certificates.service.ts` · `backend/src/workers/certificates/` · `backend/test/training/certificates.e2e-spec.ts`
**Build:** Issue Certificate with eligibility snapshot, template/font version, immutable FileObject/hash and random verification-token digest. Outbox rendering is idempotent; Arabic PDF uses embedded approved font. Amendments/reissues get new issuance identity; revoke preserves original evidence. No duplicate certificate on worker retry.
**Tests:** `certificate_retry_preserves_one_issuance` · `certificate_arabic_render_preserves_template_provenance`
**Verify:** `(cd backend && just test-e2e -- test/training/certificates.e2e-spec.ts)`
**Done when:** An eligible participant receives one immutable certificate linked to its completion and template evidence.

### 2.3.4 — Expose minimal certificate verification
**Repo:** backend + frontend · **Size:** M · **Depends on:** `2.3.3` · **Requirements:** SR-TR-010, PRD-TR-002, SR-API-009
**Files:** `backend/src/modules/training/presentation/certificate-verification.controller.ts` · `frontend/app/[locale]/verify-certificate/` · `frontend/tests/training/certificate-verification.spec.ts`
**Build:** Public verification uses opaque random token, independent limits and no indexing. Default response validity/issuer/course/date; display name requires approved policy, never medical or attendance details. Revocation updates public validity immediately through authoritative lookup. Build certificate view/download for authorized participants.
**Tests:** `certificate_public_verification_omits_private_details` · `revoked_certificate_displays_revoked_state`
**Verify:** `(cd frontend && npx --no-install playwright test tests/training/certificate-verification.spec.ts --project=ar --project=en)`
**Done when:** Public verification reports current validity while exposing only the approved minimal certificate fields.

## Group 2.4 — Performance

### 2.4.1 — Validate performance records and metric units
**Repo:** backend · **Size:** L · **Depends on:** `1.10.9` · **Requirements:** SR-PF-001/002/003, PRD-PF-001
**Files:** `backend/src/modules/performance/` · `backend/prisma/migrations/<timestamp>_performance_rules/migration.sql` · `backend/test/performance/records.e2e-spec.ts`
**Build:** Persist player, match date, optional season, opponent/venue/competition provenance and every required metric. Controlled units/ranges reject negative minutes, shotsOnTarget>shots, percentages outside0..100 and invalid cards; configured match duration bounds minutes. Null means unknown, not zero. CHECK constraints complement DTO/domain validation.
**Tests:** `performance_records_reject_impossible_metric_combinations`
**Verify:** `(cd backend && just test-e2e -- test/performance/records.e2e-spec.ts)`
**Done when:** Required metrics persist with units and impossible combinations fail in both service and database paths.

### 2.4.2 — Provide authorized trends and period comparison
**Repo:** backend + frontend · **Size:** L · **Depends on:** `2.4.1` · **Requirements:** SR-PF-005, PRD-PF-001, BR-OBJ-04
**Files:** `backend/src/modules/performance/application/trends.reader.ts` · `frontend/src/features/performance/` · `frontend/tests/performance/trends.spec.ts`
**Build:** Aggregate indexed tenant/player/season/date ranges and expose denominator/source period and missing-data counts. Build accessible chart plus table, match entry and comparison UI; missing/hidden data never appears as zero or discloses inaccessible records. Validate period bounds and current player access.
**Tests:** `performance_trends_reconcile_to_visible_source_records`
**Verify:** `(cd frontend && npx --no-install playwright test tests/performance/trends.spec.ts --project=ar --project=en)`
**Done when:** A permitted analyst reproduces each displayed period aggregate from authorized source records.

### 2.4.3 — Import performance with preview and deterministic row outcomes
**Repo:** backend · **Size:** L · **Depends on:** `2.4.1`, `2.9.1` · **Requirements:** SR-PF-004, SR-API-006
**Files:** `backend/src/modules/performance/application/import.service.ts` · `backend/src/workers/imports/performance.handler.ts` · `backend/test/performance/import.e2e-spec.ts`
**Build:** Stage bounded CSV rows after the secure file pipeline; store mapping version, file hash and source/externalRef. Preview validation before confirmed commit; unique job/row identity records accepted/rejected outcome. Retry only unfinished rows; counts reconcile; cross-tenant IDs and formula-bearing exported cells cannot escape validation. Default 10,000 rows, larger batches require capacity approval.
**Tests:** `performance_import_retry_preserves_accepted_rows` · `performance_import_reports_exact_partial_failures`
**Verify:** `(cd backend && just test-e2e -- test/performance/import.e2e-spec.ts)`
**Done when:** A partially invalid import has an exact row report and retry duplicates no accepted record.

### 2.4.4 — Introduce matches and structured sporting references
**Repo:** backend · **Size:** L · **Depends on:** `2.4.1`, `1.2.2` · **Requirements:** SR-PF-001/002, SR-DB-003
**Files:** `backend/prisma/schema.prisma` · `backend/src/modules/performance/application/matches.service.ts` · `backend/test/performance/matches.e2e-spec.ts`
**Build:** Add tenant Team, Competition, Match and PlayerMatchStat with organization links and optional season. Competitions are their own sporting entity; organizers may reference Organization. Preserve imported free-text provenance; unresolved opponents stay unmapped. Enforce one player/match/stat-source identity and same-tenant FK/RLS rules.
**Tests:** `performance_match_mapping_preserves_unknown_opponents`
**Verify:** `(cd backend && just test-e2e -- test/performance/matches.e2e-spec.ts)`
**Done when:** A structured match links valid same-tenant sporting entities without inventing legacy mappings.

### 2.4.5 — Build the import preview and recovery UI
**Repo:** frontend · **Size:** M · **Depends on:** `2.4.3` · **Requirements:** SR-PF-004, UX-003/011
**Files:** `frontend/src/features/performance/import/` · `frontend/tests/performance/import.spec.ts`
**Build:** Expose mapping, validation preview, explicit commit, progress, safe row-error download and resumed retry. Confirm accepted/rejected totals and prevent a browser retry from starting another commit. Preserve mapping selections after recoverable failure, never store CSV content in browser logs or local storage.
**Tests:** `performance_import_ui_preserves_mapping_and_safe_retry`
**Verify:** `(cd frontend && npx --no-install playwright test tests/performance/import.spec.ts --project=ar --project=en)`
**Done when:** The analyst previews and retries a mixed-validity CSV while the UI reflects persisted row outcomes.

## Group 2.5 — Ratings

### 2.5.1 — Version rating schemes and deterministic totals
**Repo:** backend · **Size:** L · **Depends on:** `2.4.1` · **Requirements:** SR-RT-001/002/003/004, PRD-RT-001, BR-RULE-09
**Files:** `backend/src/modules/ratings/domain/` · `backend/prisma/schema.prisma` · `backend/test/ratings/schemes.e2e-spec.ts`
**Build:** RatingSchemeVersion owns immutable technical/physical/mental and extensible dimensions, scale, weights and rounding. Calculate decimal totals server-side; validate approved weight total and evaluator policy. Capture dimension observations and scheme version; imported legacy scores retain legacy-unverified provenance rather than invented historic weights.
**Tests:** `rating_total_is_computed_from_immutable_scheme` · `rating_scheme_change_preserves_previous_scores`
**Verify:** `(cd backend && just test-e2e -- test/ratings/schemes.e2e-spec.ts)`
**Done when:** A new scheme cannot alter prior scores and clients cannot write their own calculated total.

### 2.5.2 — Build rating entry and historical comparison
**Repo:** frontend · **Size:** L · **Depends on:** `2.5.1`, `2.4.2` · **Requirements:** PRD-RT-001, SR-RT-004, BR-OBJ-04, TEST-009
**Files:** `frontend/src/features/ratings/` · `frontend/tests/ratings/history.spec.ts`
**Build:** Implement evaluator entry, review and historical score tables/charts with scheme labels and source period. Compare unlike schemes only with visible discontinuity or approved mapping. Present permission/empty/loading/stale-edit states in both locales and an accessible data table.
**Tests:** `rating_history_exposes_scheme_changes_accessibly`
**Verify:** `(cd frontend && npx --no-install playwright test tests/ratings/history.spec.ts --project=ar --project=en)`
**Done when:** A reviewer interprets historical scores with visible scheme provenance in both locales.

### 2.5.3 — Support approved position-specific rating criteria
**Repo:** backend · **Size:** M · **Depends on:** `2.5.1` · **Requirements:** SR-RT-005
**Files:** `backend/src/modules/ratings/domain/position-scheme.ts` · `backend/test/ratings/position-schemes.e2e-spec.ts`
**Build:** Bind optional position criteria to immutable scheme versions and approved eligibility. No automatic renormalization when a player changes position; record the evaluated position and use configured weights. Default disabled until sporting owner approves examples; no unsupported statistical equivalence claim.
**Tests:** `position_rating_scheme_captures_evaluated_position`
**Verify:** `(cd backend && just test-e2e -- test/ratings/position-schemes.e2e-spec.ts)`
**Done when:** A position change cannot reinterpret an earlier position-specific score.

## Group 2.6 — Realtime and chat

### 2.6.1 — Run an independently authenticated realtime gateway
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `2.6.2`, `2.6.3` · **Requirements:** SYS-ARC-005, SR-CH-008, SR-CORE-008, SYS-TEN-006
**Files:** `backend/src/realtime.ts` · `backend/src/modules/chat/presentation/chat.gateway.ts` · `infra/compose.yaml` · `backend/test/chat/gateway.e2e-spec.ts`
**Build:** Route same-origin websocket path to a separate Socket.IO process with Valkey adapter. Handshake validates Origin and opaque application session; every protected event checks PostgreSQL session/membership and conversation policy. Rooms carry tenant/conversation; revoked membership disconnects and cannot receive subsequent deliveries. No provider bearer or session ID in query URLs. Propagate safe request/event IDs and test broker restart.
**Tests:** `chat_gateway_denies_revoked_sessions_and_foreign_rooms`
**Verify:** `(cd backend && just test-e2e -- test/chat/gateway.e2e-spec.ts)`
**Done when:** A revoked or foreign member cannot join, send or receive through the realtime process.

### 2.6.2 — Model explicit conversation membership and private images
**Repo:** backend · **Size:** L · **Depends on:** `1.10.9` · **Requirements:** SR-CH-001/002, SR-CH-010
**Files:** `backend/src/modules/chat/application/conversations.service.ts` · `backend/prisma/migrations/<timestamp>_conversation_membership/migration.sql` · `backend/test/chat/conversations.e2e-spec.ts`
**Build:** Canonical direct-pair unique key prevents duplicate one-to-one threads; groups have explicit member/admin lifecycle. Audited rejoin reactivates existing membership. Replace legacy Conversation.imageUrl with typed ConversationImage→FileObject, migrating only proved same-tenant clean assets; unknown legacy URLs remain quarantined. Members-only metadata/image projection and new-table FORCE RLS/catalog checks.
**Tests:** `chat_direct_pair_and_membership_are_unique` · `conversation_images_require_current_membership`
**Verify:** `(cd backend && just test-e2e -- test/chat/conversations.e2e-spec.ts)`
**Done when:** One direct thread exists per pair and only current members can retrieve its metadata or image.

### 2.6.3 — Persist ordered messages before acknowledgment
**Repo:** backend · **Size:** L · **Depends on:** `2.6.2` · **Requirements:** SR-CH-003/004/005/006, PRD-CH-001, BR-OBJ-06
**Files:** `backend/src/modules/chat/application/messages.service.ts` · `backend/test/chat/messages.e2e-spec.ts`
**Build:** sendMessage(ctx,conversationId,clientMessageId,body) atomically allocates sequence, persists message/audit/outbox and deduplicates client ID. Validate content by Text/File/Image/System type; only trusted services create system messages. Edit requires revision and policy; recall hides ordinary content while preserving restricted evidence according to approved retention. Broadcast never precedes commit.
**Tests:** `chat_duplicate_send_has_one_committed_sequence` · `chat_edit_and_recall_preserve_required_evidence`
**Verify:** `(cd backend && just test-e2e -- test/chat/messages.e2e-spec.ts)`
**Done when:** Retries yield one committed ordered message and edits or recall retain required evidence.

### 2.6.4 — Use monotonic read cursors and reconnect synchronization
**Repo:** backend · **Size:** M · **Depends on:** `2.6.1` · **Requirements:** SR-CH-007, SR-CH-004
**Files:** `backend/src/modules/chat/application/read-state.service.ts` · `backend/test/chat/reconnect.e2e-spec.ts`
**Build:** Store lastReadSequence per member and advance monotonically to an existing authorized message. Reconnect fetches persisted sequence gaps through bounded REST pagination; last-read timestamps alone are not reliable ordering. Replayed broadcasts reconcile by message ID/sequence, and removed members cannot sync old attachments or counts.
**Tests:** `chat_read_cursor_never_moves_backwards` · `chat_reconnect_recovers_committed_messages_once`
**Verify:** `(cd backend && just test-e2e -- test/chat/reconnect.e2e-spec.ts)`
**Done when:** A reconnect recovers committed gaps without duplicates or a regressing read cursor.

### 2.6.5 — Bind chat files and enforce abuse limits
**Repo:** backend · **Size:** L · **Depends on:** `2.6.3` · **Requirements:** SR-CH-009/010, SR-API-008
**Files:** `backend/src/modules/chat/application/attachments.service.ts` · `backend/prisma/migrations/<timestamp>_chat_file_objects/migration.sql` · `backend/test/chat/attachments.e2e-spec.ts`
**Build:** Replace Message.fileUrl with MessageAttachment→FileObject using same-tenant FKs and typed conversation/message ownership. Resolve legacy URLs only from proved private objects; unknown entries remain unavailable. Reauthorize current membership and source classification for upload/attach/download; ordinary chat cannot launder medical/legal/finance files. Per-user/conversation rates, bounded bodies, report/block controls and restricted moderation metadata.
**Tests:** `chat_files_cannot_launder_confidential_objects` · `chat_message_rate_and_payload_limits_hold`
**Verify:** `(cd backend && just test-e2e -- test/chat/attachments.e2e-spec.ts)`
**Done when:** Only current members can share clean authorized files and restricted source files cannot enter ordinary chat.

### 2.6.6 — Build durable chat and reconnect UX
**Repo:** frontend · **Size:** L · **Depends on:** `2.6.4`, `2.6.5` · **Requirements:** PRD-CH-001, UX-008/009/011, TEST-005
**Files:** `frontend/app/[locale]/communication/` · `frontend/src/features/chat/` · `frontend/tests/chat/conversations.spec.ts`
**Build:** Conversation list, unread state, composer, file state, edit/recall and reconnect banner use generated client and session-authenticated socket. Optimistic messages reconcile by stable clientMessageId; pending/sent/failed are distinct. Test two users, loss/reconnect, removed membership, mixed-direction text and mobile keyboard/focus.
**Tests:** `chat_ui_reconnect_preserves_one_message_and_rtl_order`
**Verify:** `(cd frontend && npx --no-install playwright test tests/chat/conversations.spec.ts --project=ar --project=en)`
**Done when:** Two authorized users exchange durable messages through a reconnect in Arabic and English.

## Group 2.7 — Push and live notifications

### 2.7.1 — Add approved push delivery and device lifecycle
**Repo:** backend · **Size:** L · **Depends on:** `1.6.1`, `2.6.1` · **Requirements:** SR-NF-002/005, SR-NF-006
**Files:** `backend/src/modules/notifications/infrastructure/push/` · `backend/src/modules/notifications/application/devices.service.ts` · `backend/test/notifications/push.e2e-spec.ts`
**Build:** OPEN — push provider/consent: default disabled; approval requires delivery/data-flow and device-policy evidence. Register, rotate and revoke devices under current identity/tenant; purge invalid endpoints safely. Track queued/accepted/failed/retry separately from device display. Generic payloads and authorized deep links only; provider keys plus inbox prevent duplicate local processing without claiming exactly-once external delivery.
**Tests:** `push_device_rotation_and_revocation_stop_delivery` · `push_payload_contains_no_confidential_canaries`
**Verify:** `(cd backend && just test-e2e -- test/notifications/push.e2e-spec.ts)`
**Done when:** An approved device receives safe push while revoked or cross-tenant endpoints receive none.

### 2.7.2 — Synchronize the notification center in realtime
**Repo:** frontend · **Size:** M · **Depends on:** `2.7.1`, `2.6.4` · **Requirements:** PRD-NF-001, SR-NF-004/007, BR-OBJ-06
**Files:** `frontend/src/features/notifications/` · `frontend/tests/notifications/realtime.spec.ts`
**Build:** Persisted inbox remains truth; realtime updates trigger scoped refetch/reconciliation. Read/all-read commands are idempotent, optional push requires user consent and preferences, mandatory security notices remain policy-controlled. Reconnect restores unseen entries and every deep link reauthorizes.
**Tests:** `notification_reconnect_and_deep_link_authorization_hold`
**Verify:** `(cd frontend && npx --no-install playwright test tests/notifications/realtime.spec.ts --project=ar --project=en)`
**Done when:** Reconnection restores the correct unread inbox without exposing a now-forbidden resource.

## Group 2.8 — Media pipeline

### 2.8.1 — Bound multipart video uploads and cleanup
**Repo:** backend · **Size:** L · **Depends on:** `1.3.3`, `0.8.4` · **Requirements:** SR-PL-006, SR-NFR-PERF-002
**Files:** `backend/src/modules/documents/application/multipart.service.ts` · `backend/test/documents/multipart.e2e-spec.ts`
**Build:** Extend UploadSession with expected size/parts, expiry and reservation. Authorize bounded part URLs for quarantine only; finalize validates aggregate checksum/size then uses existing scan→immutable-version promotion. Retry does not reserve twice; abort/expiry releases capacity and cleans unreferenced parts. Test replayed old PUT cannot replace downloadable READY+CLEAN bytes.
**Tests:** `video_multipart_retry_and_abort_preserve_quota` · `video_old_upload_url_cannot_replace_clean_bytes`
**Verify:** `(cd backend && just test-e2e -- test/documents/multipart.e2e-spec.ts)`
**Done when:** Multipart retry or abort cannot bypass limits or change the immutable downloadable version.

### 2.8.2 — Transform verified video in a sandboxed worker
**Repo:** backend · **Size:** L · **Depends on:** `2.8.1` · **Requirements:** SR-PL-007, SYS-ASY-001/002
**Files:** `backend/src/workers/media/` · `backend/test/integration/media-transforms.integration-spec.ts`
**Build:** Read only the pinned READY+CLEAN original version/hash; sandbox FFmpeg with no network, CPU/memory/time/duration limits and approved formats. Produce versioned metadata/thumbnail/stream variants with source hash. Outbox/inbox dedupe and deterministic job keys make retries safe; never fall back to an unscanned object after decoder failure.
**Tests:** `video_worker_variants_bind_exact_scanned_source` · `video_decoder_limits_fail_without_releasing_original`
**Verify:** `(cd backend && just test-int -- media-transforms)`
**Done when:** Worker retries produce one verified variant set and malicious media stays unavailable.

### 2.8.3 — Expose resumable video processing states
**Repo:** frontend · **Size:** M · **Depends on:** `2.8.2` · **Requirements:** SR-PL-006/007, UX-003/009/011
**Files:** `frontend/src/features/media/` · `frontend/tests/media/video.spec.ts`
**Build:** Show uploaded bytes separately from scanning/processing/ready; persist resumable session identifiers without credentials or confidential metadata. Support cancel, recoverable part retry and safe playback of ready variants. Browser tests cover offline resume, expired part URL, scanner failure and permission loss.
**Tests:** `video_ui_never_confuses_upload_with_ready_state`
**Verify:** `(cd frontend && npx --no-install playwright test tests/media/video.spec.ts --project=ar --project=en)`
**Done when:** An interrupted upload resumes while playback remains unavailable until verified processing completes.

## Group 2.9 — Jobs and department dashboards

### 2.9.1 — Provide shared audited import and export job contracts
**Repo:** backend · **Size:** L · **Depends on:** `1.10.9` · **Requirements:** SR-API-006, SYS-ASY-001/003/004, SR-ACL-009
**Files:** `backend/src/modules/jobs/` · `backend/src/workers/imports/` · `backend/src/workers/exports/` · `backend/test/jobs/lifecycle.e2e-spec.ts`
**Build:** ImportJob/ExportJob store actor, tenant, source/template version, progress, idempotency key, lease and safe error counts. Stage/preview/confirm/execute/cancel APIs use existing outbox/inbox, bounded retry and tenant registry. Reauthorize at execution and release; cancellation never undoes committed rows silently. Formula-safe CSV/error outputs expire under policy; audit every export.
**Tests:** `bulk_job_retry_and_revocation_preserve_authorized_outcomes`
**Verify:** `(cd backend && just test-e2e -- test/jobs/lifecycle.e2e-spec.ts)`
**Done when:** A retried or revoked job cannot duplicate committed effects or release unauthorized output.

### 2.9.2 — Build policy-scoped department report services
**Repo:** backend · **Size:** L · **Depends on:** `2.3.4`, `2.4.4`, `2.5.3`, `2.6.5`, `2.1.5`, `2.9.1` · **Requirements:** PRD-PF-001, PRD-ME-001, BR-OBJ-03/04, SYS-TEN-006
**Files:** `backend/src/modules/reporting/application/department-reports.ts` · `backend/test/reporting/departments.e2e-spec.ts`
**Build:** Aggregate attendance, performance, scheme-aware ratings and approved medical availability through module application readers. Apply policy before counts/grouping/pagination; never join confidential narrative into a general aggregate. Use source period/as-of version and tenant-leading query plans; exports use job release reauthorization.
**Tests:** `department_reports_exclude_hidden_rows_and_clinical_counts`
**Verify:** `(cd backend && just test-e2e -- test/reporting/departments.e2e-spec.ts)`
**Done when:** Each department receives reproducible aggregates containing only its authorized source projection.

### 2.9.3 — Build operational reports and job recovery UI
**Repo:** frontend · **Size:** L · **Depends on:** `2.9.2`, `2.4.5` · **Requirements:** UX-004/008/009/010/011, TEST-005
**Files:** `frontend/app/[locale]/reports/operations/` · `frontend/src/features/jobs/` · `frontend/tests/reports/operations.spec.ts`
**Build:** Filters, source/as-of labels, accessible charts/tables, export confirmation and job progress/error/retry use tenant/projection query keys. Distinguish no data from forbidden operation without hidden totals. No automatic download after permissions change; generate a fresh authorized file request.
**Tests:** `operational_report_ui_handles_revoked_export_and_empty_state`
**Verify:** `(cd frontend && npx --no-install playwright test tests/reports/operations.spec.ts --project=ar --project=en)`
**Done when:** A user filters a department report and recovers a failed export without receiving a revoked file.

## Group 2.10 — Release 2

### 2.10.1 — Measure operational load and isolation under contention
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `2.1.8`, `2.6.6`, `2.7.2`, `2.8.3`, `2.9.3` · **Requirements:** TEST-007, SR-NFR-PERF-001/003
**Files:** `backend/test/load/operations.js` · `backend/test/integration/operations-capacity.integration-spec.ts` · `docs/implementation/evidence/phase-2-load.md`
**Build:** Use the approved Phase-1 envelope plus declared concurrent websocket connections, uploads and imports; record hardware, dataset, durations and pool budgets. Assert p95 budgets and zero isolation leaks under capacity/attendance races, broker delay and one busy tenant. Missing owner envelope remains OPEN, never an invented production capacity claim.
**Tests:** `operations_capacity_keeps_pool_and_tenant_budgets`
**Verify:** `(cd backend && just test-int -- operations-capacity)`
**Done when:** Measured operations load meets the declared latency, connection and isolation budgets.

### 2.10.2 — Restore operational data and immutable files on staging
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `2.10.1` · **Requirements:** TEST-008, SR-NFR-REL-002
**Files:** `backend/test/integration/operations-recovery.integration-spec.ts` · `docs/implementation/evidence/phase-2-recovery.md`
**Build:** Restore staging-shaped PostgreSQL18, versioned blobs, identity config and required encryption keys into isolated services. Invalidate restored sessions, block real provider delivery, reconcile outbox and verify attendance/certificate/message/audit hashes. Measure approved RPO/RTO; a backup success notification is insufficient.
**Tests:** `operations_restore_preserves_messages_certificates_and_audit`
**Verify:** `(cd backend && just test-int -- operations-recovery)`
**Done when:** A timed isolated restore preserves operational records, immutable evidence and tenant separation.

### 2.10.3 — Accept and promote operational depth
**Repo:** umbrella + backend + frontend · **Size:** M · **Depends on:** `2.10.2`, `2.10.4` · **Requirements:** BR-OBJ-03/04/06/09, TEST-005/006
**Files:** `docs/implementation/evidence/phase-2.md` · `backend/test/acceptance/operations-release.e2e-spec.ts`
**Build:** Execute this phase gate and all inherited checks; attach sanitized automated/manual results, accepted medical policy, exact three repository SHAs and merged PRs. Promote through existing development→staging→main/pin recipes; no automatic new tag convention. Failed or externally unapproved features keep the release incomplete.
**Tests:** `operations_release_manifest_requires_all_domain_gates`
**Verify:** `(cd backend && just test-e2e -- test/acceptance/operations-release.e2e-spec.ts)`
**Done when:** The promoted pins have owner-approved operational evidence and no unresolved critical or high confidentiality defect.

### 2.10.4 — Verify operational accessibility and bilingual journeys
**Repo:** frontend + umbrella · **Size:** L · **Depends on:** `2.1.7`, `2.2.5`, `2.3.4`, `2.5.2`, `2.6.6`, `2.8.3`, `2.9.3` · **Requirements:** TEST-009/010, SR-NFR-A11Y-001, UX-008/009/012
**Files:** `frontend/tests/accessibility/operations.spec.ts` · `docs/implementation/evidence/phase-2-accessibility.md`
**Build:** Run Playwright ar/en with axe plus recorded keyboard and screen-reader checks at360/768/1440px. Cover medical purpose entry, calendar alternative, attendance, certificate, charts and chat reconnect. Document any target not achieved; no blanket WCAG certification statement.
**Tests:** `operations_bilingual_accessibility_journeys_pass`
**Verify:** `(cd frontend && npx --no-install playwright test tests/accessibility/operations.spec.ts --project=ar --project=en)`
**Done when:** The recorded Arabic and English operational journeys meet the agreed accessibility acceptance checks.

## Phase 2 exit gate

Run only against configured disposable services and staging test fixtures; commands do not replace policy approval or deployment evidence.

```sh
python3 scripts/check-plan.py
(cd backend && just check)
(cd backend && just migrations)
(cd backend && just test-int)
(cd backend && just test-e2e)
(cd frontend && just check)
(cd frontend && npx --no-install playwright test --project=ar --project=en)
```

1. An unrelated medic, coach, guardian and administrator fail the clinical canary tests; the approved clinician records an amendment and human return-to-play decision.
2. Two simultaneous enrollments contend for the final seat; attendance rejects another program's session and certificate verification reflects revocation.
3. A mixed-validity CSV produces exact row outcomes; retry leaves accepted performance records unchanged and rating history retains its scheme.
4. Two users reconnect after message delivery interruption; membership revocation prevents later chat/file access and the persisted cursor recovers gaps.
5. Replay an old multipart PUT after CLEAN; the authorized download still returns the scanned immutable bytes. Scanner/decoder failure releases nothing.
6. Revoke export permission during a job; neither reports, push nor downloads disclose the result. Demonstrate ar/en keyboard and mobile workflows.
7. Record measured load, staging restore/key recovery and required owner approvals in `docs/implementation/evidence/phase-2.md`, with exact pinned SHAs and CI URLs before2.10.3 closes.
