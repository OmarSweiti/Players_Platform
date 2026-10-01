# Phase 3 — Agency intelligence (BRD release 3)

> **Exit:** Sourced analytics support recruitment; dossier sharing is explicitly scoped and revocable; finance and provider signatures operate only under approved policies with recoverable evidence.

All microsteps are planned targets. Refinement may split work but must preserve existing IDs. Every new tenant table includes tenant-safe references, ENABLE/FORCE RLS, least-privilege grants and catalog tests in the same migration. [OPEN decisions](00-master-plan.md#open-register) keep external finance/signature integration disabled until settled. Scouting moved into Phase 1 (group 1.11, [ADR-0021](../adr/0021-a-product-built-to-sell.md)) and is released by `1.11.7`; no Phase-3 feature reintroduces local credentials, provider token storage or unrestricted public files.

```text
2.4.4 + 1.11.2 → 3.2 affiliation/comparison → analytics UI ───┤
1.11.7 + 3.2.2 → 3.3 snapshot → grant → portal → staff UI ───┤
2.10.3 → 3.4.5 finance policy → ledger/provider/reconcile ────┤
1.4 evidence + 2.10.3 → 3.5 provider policy → evidence ───────┤
3.2 + 3.4 + 2.9 → 3.6 report schedules ─────────────────────┤
all leaves → 3.7 security → load → restore → release acceptance
```

Each step’s dependency field is authoritative, including intentional references to a later-numbered policy or gate step. Verify commands run from the umbrella after the Phase-0 harness exists.

**Effort:** 22 steps (0 S / 5 M / 17 L); sizing capacity up to 312 focused hours +30% reserve = 405.6 hours, 16.2 weeks at 25 focused hours/week. This is a falsifiable planning bound, not a promised date; re-estimate at entry and split any step exceeding 16 hours.

## Group 3.2 — Affiliations and traceable analytics

### 3.2.1 — Complete organization, team and competition history
**Repo:** backend · **Size:** L · **Depends on:** `2.4.4`, `1.11.2` · **Requirements:** SR-PF-001/002, BR-OBJ-04, SR-DB-003
**Files:** `backend/src/modules/organizations/` · `backend/src/modules/performance/application/affiliations.reader.ts` · `backend/test/analytics/affiliations.e2e-spec.ts`
**Build:** Extend Phase-1 Organization/affiliation and Phase-2 Competition/Match models; do not duplicate them under analytics. Add team membership periods and transfer provenance needed for season/competition analysis. Validate non-overlap where policy requires a single primary affiliation; retain unknown dates explicitly. Analysts receive a permitted sporting projection, never compensation or contract documents through joins.
**Tests:** `analytics_affiliations_preserve_historical_club_context`
**Verify:** `(cd backend && just test-e2e -- test/analytics/affiliations.e2e-spec.ts)`
**Done when:** A historical performance record resolves to its period-correct sporting affiliation without disclosing compensation.

### 3.2.2 — Build traceable player and cohort comparisons
**Repo:** backend · **Size:** L · **Depends on:** `3.2.1`, `2.5.3` · **Requirements:** SR-PF-005, SR-RT-004/005, BR-OBJ-04
**Files:** `backend/src/modules/analytics/application/comparisons.reader.ts` · `backend/test/analytics/comparisons.e2e-spec.ts`
**Build:** comparePlayers(ctx,query) accepts bounded player/season/position cohorts and approved metrics. Return sample size, missing-data indicators, period, source record IDs and rating scheme versions; do not compare incompatible scheme totals without an approved normalization rule. Cohort membership, aggregates and caches enforce authorized player scope and minimum disclosure policy. Expensive calculations use outbox-backed jobs.
**Tests:** `analytics_comparison_reports_sources_and_missing_data` · `analytics_cohort_excludes_unauthorized_players`
**Verify:** `(cd backend && just test-e2e -- test/analytics/comparisons.e2e-spec.ts)`
**Done when:** Every comparison value can be traced to authorized records and incompatible rating schemes are explicitly identified.

### 3.2.3 — Present accessible comparisons and analytical uncertainty
**Repo:** frontend · **Size:** L · **Depends on:** `3.2.2` · **Requirements:** PRD-PF-001, UX-002/003/008/009/010/011, TEST-010
**Files:** `frontend/app/[locale]/analytics/` · `frontend/src/features/analytics/` · `frontend/tests/analytics/comparisons.spec.ts`
**Build:** Build period/player/cohort controls, trend and comparison charts with equivalent keyboard-accessible tables. Label missing data, sample size, units and scheme version; do not convert missing metrics to zero. Drill-down uses only authorized links and export follows the existing job flow.
**Tests:** `analytics_ui_distinguishes_missing_data_from_zero`
**Verify:** `(cd frontend && npx --no-install playwright test tests/analytics/comparisons.spec.ts --project=ar --project=en)`
**Done when:** Both locales display the same sourced values and provide an accessible table equivalent to every chart.

## Group 3.3 — Dossiers and scoped sharing

### 3.3.1 — Render approved dossier snapshots and archival copies
**Repo:** backend · **Size:** L · **Depends on:** `1.11.7`, `3.2.2` · **Requirements:** SR-PL-009, PRD-PL-003, SR-DOC-005/008, BR-OBJ-07
**Files:** `backend/src/modules/dossiers/application/render.service.ts` · `backend/src/worker/dossier.worker.ts` · `backend/test/dossiers/render.e2e-spec.ts`
**Build:** Create a versioned template with an allowlisted public field/media selection and explicit approval of the resolved snapshot. Store source versions, approver, purpose, immutable artifact hash and FileObject binding. Default excludes passport, contacts, legal, medical and compensation; clinical availability is not public by default. Render in an isolated worker with remote fetch disabled and bounded resources. PDF/A is required only for an approved archival classification and validated with a pinned validator; never label an ordinary PDF PDF/A.
**Tests:** `dossier_snapshot_excludes_protected_field_canaries` · `dossier_archival_pdf_is_validated_before_labeling`
**Verify:** `(cd backend && just test-e2e -- test/dossiers/render.e2e-spec.ts)`
**Done when:** An approved dossier artifact contains only the permitted snapshot and any PDF/A claim has a validator result.

### 3.3.2 — Issue scoped expiring share grants
**Repo:** backend · **Size:** L · **Depends on:** `3.3.1` · **Requirements:** SR-PL-010, BR-RULE-06, SR-API-009
**Files:** `backend/src/modules/sharing/application/share-grants.service.ts` · `backend/test/sharing/grants.e2e-spec.ts`
**Build:** issueShare(ctx,snapshotId,{expiresAt,recipientPolicy}) returns a high-entropy capability once; persist only its hash and scope. Require explicit share permission and recipient/purpose approval. Each request checks expiry, revocation, snapshot and file allowlist, and writes a safe access audit. Never resolve a share to the latest broader player profile. Download URLs remain immutable-version-pinned; disclose their bounded post-revocation lifetime or use an authorized proxy where policy needs immediate revocation.
**Tests:** `sharing_grant_cannot_expand_approved_snapshot` · `sharing_revocation_denies_new_download_authority`
**Verify:** `(cd backend && just test-e2e -- test/sharing/grants.e2e-spec.ts)`
**Done when:** A revoked or expired grant cannot authorize a new view or download of any resource.

### 3.3.3 — Isolate the public dossier portal
**Repo:** frontend + backend · **Size:** L · **Depends on:** `3.3.2` · **Requirements:** SR-API-009, SR-PL-010, TEST-003/009/010
**Files:** `backend/src/modules/sharing/presentation/public-sharing.controller.ts` · `frontend/app/[locale]/share/` · `backend/test/sharing/public-portal.e2e-spec.ts`
**Build:** Expose a minimal separately throttled public API and no-store portal using only share scope, independent of tenant user APIs. Exchange a fragment-delivered capability through a bounded POST where practical so raw tokens do not enter server URL/access logs; apply Referrer-Policy no-referrer and no third-party analytics. Invalid/expired/revoked results are indistinguishable. Portal pages are read-only and cannot mint internal sessions or fetch arbitrary FileObjects.
**Tests:** `sharing_portal_token_cannot_access_internal_api` · `sharing_portal_omits_capability_from_telemetry`
**Verify:** `(cd backend && just test-e2e -- test/sharing/public-portal.e2e-spec.ts)`
**Done when:** A public share recipient can read only the approved snapshot and cannot pivot into the tenant API.

### 3.3.4 — Build dossier approval and share management screens
**Repo:** frontend · **Size:** L · **Depends on:** `3.3.3` · **Requirements:** PRD-PL-003, UX-003/005/006/008/009/011, TEST-005
**Files:** `frontend/app/[locale]/players/[id]/dossiers/` · `frontend/src/features/dossiers/` · `frontend/tests/dossiers/sharing.spec.ts`
**Build:** Implement field selection, safe preview, approval summary, render job progress, grant creation and revocation. Display snapshot version, expiry and already-issued URL exposure window accurately. The recipient experience is tested in ar/en, keyboard, mobile and expired states; changing a template requires a new approved snapshot.
**Tests:** `dossier_approval_and_revocation_work_in_both_locales`
**Verify:** `(cd frontend && npx --no-install playwright test tests/dossiers/sharing.spec.ts --project=ar --project=en)`
**Done when:** A staff user approves and revokes a dossier while a recipient sees only the corresponding immutable snapshot.

## Group 3.4 — Finance

### 3.4.1 — Model finance documents and append-only balanced entries
**Repo:** backend · **Size:** L · **Depends on:** `3.4.5` · **Requirements:** SR-CT-005, SR-TR-006, SR-DB-003, BR-OBJ-09
**Files:** `backend/prisma/schema.prisma` · `backend/prisma/migrations/<timestamp>_finance_ledger/migration.sql` · `backend/test/finance/ledger.e2e-spec.ts`
**Build:** Add Invoice/InvoiceLine, PaymentIntent/Payment, allocation, ledger transaction/entry and compensation components with typed same-tenant links. Money is NUMERIC(19,4) plus CurrencyDefinition exponent validation, string DTOs and explicit currency. Post balanced debit/credit entries per currency atomically; only reversal entries correct posted facts. Mutable drafts have revision; posted documents and entries receive immutable-evidence protections. Unknown historical observations stay unverified and do not become ledger transactions.
**Tests:** `finance_ledger_balances_exact_decimal_per_currency` · `finance_posted_entries_require_reversal_not_edit`
**Verify:** `(cd backend && just test-e2e -- test/finance/ledger.e2e-spec.ts)`
**Done when:** Unbalanced or invalid-precision posting fails atomically and posted amounts cannot be overwritten.

### 3.4.2 — Integrate a payment provider with durable verified callbacks
**Repo:** backend · **Size:** L · **Depends on:** `3.4.1` · **Requirements:** SR-API-007, SR-CORE-010, SYS-ASY-005
**Files:** `backend/src/modules/finance/ports/payment-provider.ts` · `backend/src/modules/finance/infrastructure/payment-provider.adapter.ts` · `backend/test/finance/provider.e2e-spec.ts`
**Build:** Define PaymentProvider.createIntent/readStatus/refund behind sandbox credentials. Outbox creates remote intents with stable provider idempotency identity; callbacks validate raw bytes/signature/account/timestamp/event, map trusted provider account to tenant, and persist WebhookReceipt unique(provider,providerAccountId,remoteEventId). Commit that receipt and a local tenant-bound OutboxEvent UUID atomically; ConsumerInbox references the local UUID. Reject the same remote ID with a changed payload hash. Accepted callbacks are durable receipts, not settlement until verified state processing succeeds. Unknown send outcomes reconcile before retry; never infer payment success from browser redirects. Provider selection, currencies and refund rules remain OPEN until approved.
**Tests:** `finance_webhook_replay_and_wrong_account_are_denied` · `finance_provider_unknown_outcome_requires_reconciliation`
**Verify:** `(cd backend && just test-e2e -- test/finance/provider.e2e-spec.ts)`
**Done when:** A duplicated verified callback posts at most one local payment while an ambiguous remote outcome remains pending reconciliation.

### 3.4.3 — Settle training balances through finance allocations
**Repo:** backend · **Size:** M · **Depends on:** `3.4.2`, `2.2.4` · **Requirements:** SR-TR-006, BR-RULE-02
**Files:** `backend/src/modules/finance/application/training-allocations.service.ts` · `backend/test/finance/training-allocations.e2e-spec.ts`
**Build:** Allocate approved payments/refunds/waivers to enrollment charges with exact currency matching and bounded outstanding balance. Training consumes a restricted derived status; it cannot post finance entries directly. Preserve Phase-2 payment observations with source and verification state, presenting disagreement for reconciliation rather than overwriting history.
**Tests:** `finance_training_status_derives_from_verified_allocations`
**Verify:** `(cd backend && just test-e2e -- test/finance/training-allocations.e2e-spec.ts)`
**Done when:** An enrollment’s verified payment status agrees with its finance allocations while prior observations remain attributable.

### 3.4.4 — Build the restricted finance workspace
**Repo:** frontend · **Size:** L · **Depends on:** `3.4.3`, `3.4.6` · **Requirements:** SR-ACL-008/009, SR-CT-005, UX-003/005/008/009/011
**Files:** `frontend/app/[locale]/finance/` · `frontend/src/features/finance/` · `frontend/tests/finance/workspace.spec.ts`
**Build:** Provide invoice drafts/posting, payment status, allocations, reconciliation and reversal approval under explicit finance permissions. Display exact strings and currency, source provenance and Unknown remote status. Separate preparer/approver actions per approved policy, require fresh assurance for privileged money commands and show no compensation in general dashboards.
**Tests:** `finance_workspace_hides_compensation_from_ordinary_users` · `finance_decimal_inputs_roundtrip_in_both_locales`
**Verify:** `(cd frontend && npx --no-install playwright test tests/finance/workspace.spec.ts --project=ar --project=en)`
**Done when:** Authorized finance users reconcile a payment without disclosing amounts to an ordinary tenant member.

### 3.4.5 — Approve the finance operating scope before integration
**Repo:** umbrella + backend · **Size:** M · **Depends on:** `2.10.3` · **Requirements:** SR-CT-005, SR-TR-006, BR-RULE-02, BR-OBJ-09
**Files:** `docs/reference/domain-workflows.md` · `backend/src/modules/finance/domain/finance-policy.ts` · `backend/test/finance/policy.e2e-spec.ts`
**Build:** OPEN — finance operating policy: owner/accountant chooses invoice jurisdiction/tax responsibilities, chart of accounts, currency set, payment provider, refund approvals, segregation and reconciliation cadence. Default sandbox only with synthetic money and no tax/accounting compliance claims. Record policy version and acceptance examples; do not implement invented local tax rules.
**Tests:** `finance_activation_requires_approved_operating_policy`
**Verify:** `(cd backend && just test-e2e -- test/finance/policy.e2e-spec.ts)`
**Done when:** Production finance activation is denied until the owner approves the operating policy and examples.

### 3.4.6 — Reconcile provider statements and controlled discrepancies
**Repo:** backend · **Size:** L · **Depends on:** `3.4.2` · **Requirements:** SR-API-006/007, SR-ACL-009, TEST-002/004
**Files:** `backend/src/modules/finance/application/reconciliation.service.ts` · `backend/test/finance/reconciliation.e2e-spec.ts`
**Build:** Import bounded provider statements into immutable source batches, match provider IDs/amount/currency/status, and classify missing/duplicate/fee/refund differences. Reconciliation commands require finance scope, current revision and idempotency; a discrepancy cannot auto-write off money. Approved corrections post reversals/adjustments with source links; export is audited and reauthorized.
**Tests:** `finance_reconciliation_flags_amount_and_currency_mismatch` · `finance_duplicate_statement_does_not_duplicate_entries`
**Verify:** `(cd backend && just test-e2e -- test/finance/reconciliation.e2e-spec.ts)`
**Done when:** The same statement can be retried without duplicate entries and unexplained differences remain visible for approval.

## Group 3.5 — Provider e-signature

### 3.5.0 — Approve the signature provider and evidence policy
**Repo:** umbrella + backend · **Size:** M · **Depends on:** `2.10.3`, `1.4.5` · **Requirements:** SR-CT-008/011, BR-RULE-04
**Files:** `docs/reference/domain-workflows.md` · `backend/test/signatures/provider-policy.e2e-spec.ts`
**Build:** OPEN — e-signature policy: the owner selects jurisdictions, provider, required signatory identity/assurance, document format, evidence retention and failure/dispute process. Default provider integration disabled; the Phase-1 approved manual evidence policy, if any, remains valid. Do not call a provider-certified flow legally valid without this decision. Add accepted/rejected evidence examples and a provider-exit retrieval exercise.
**Tests:** `signature_provider_requires_approved_evidence_policy`
**Verify:** `(cd backend && just test-e2e -- test/signatures/provider-policy.e2e-spec.ts)`
**Done when:** Provider activation is blocked until the owner approves the evidence policy and retrieval examples.

### 3.5.1 — Connect signature envelopes to the approved version
**Repo:** backend · **Size:** L · **Depends on:** `3.5.0`, `1.4.8`, `1.4.9` · **Requirements:** SR-CT-011, SR-API-007, SR-CORE-010
**Files:** `backend/src/modules/signatures/ports/signature-provider.ts` · `backend/src/modules/signatures/infrastructure/provider.adapter.ts` · `backend/test/signatures/provider.e2e-spec.ts`
**Build:** Extend Phase-1 SignatureEvidence/Signatory/SignatureEvent with SignatureEnvelope and provider mapping; do not create a second evidence truth. SignatureProvider.createEnvelope/getEnvelope/downloadEvidence uses an approved immutable ContractVersion source hash, required signatories and policy version. Store provider account/envelope mapping, deliver through outbox and reconcile Unknown outcomes before resubmitting. Receiver authenticates bounded raw callback bytes, account, timestamp and event identity into WebhookReceipt plus an atomic tenant-bound local OutboxEvent UUID; ConsumerInbox deduplicates that local UUID. Reject a reused remote event ID with a changed payload hash; no callback field alone selects tenant.
**Tests:** `signature_envelope_is_bound_to_approved_version` · `signature_callback_rejects_forgery_replay_and_wrong_account`
**Verify:** `(cd backend && just test-e2e -- test/signatures/provider.e2e-spec.ts)`
**Done when:** Only an authenticated provider event can reference the correct tenant envelope and approved source version.

### 3.5.2 — Retain provider evidence and enforce completion
**Repo:** backend · **Size:** L · **Depends on:** `3.5.1` · **Requirements:** SR-CT-008/011/012, BR-RULE-04/05, SR-DB-009
**Files:** `backend/src/modules/signatures/application/reconcile-evidence.service.ts` · `backend/test/signatures/evidence.e2e-spec.ts`
**Build:** Reconcile provider status and obtain signed artifact/certificate into the same immutable scan pipeline. Bind approved source version/hash separately from signed-result hash; signatures can change PDF bytes. Verify the approved policy, every required signatory, approval round, provider evidence and source binding before the contract can become SIGNED. Duplicate/out-of-order events append evidence without regressing state. Grants plus UPDATE/DELETE/TRUNCATE triggers protect evidence; restore must preserve verifiability.
**Tests:** `signature_completion_requires_all_policy_evidence` · `signature_out_of_order_events_cannot_regress_contract` · `signature_restored_evidence_preserves_source_binding`
**Verify:** `(cd backend && just test-e2e -- test/signatures/evidence.e2e-spec.ts)`
**Done when:** A contract becomes SIGNED only when the approved source and every required signatory have complete immutable policy-valid evidence.

## Group 3.6 — Scheduled reports

### 3.6.1 — Schedule reports without persisting excess disclosure
**Repo:** backend · **Size:** L · **Depends on:** `3.2.2`, `3.4.6`, `2.9.2` · **Requirements:** SYS-ASY-001/002/003/004, SR-ACL-009, SR-NF-006
**Files:** `backend/src/modules/reporting/application/schedules.service.ts` · `backend/src/worker/report-schedule.worker.ts` · `backend/test/reporting/schedules.e2e-spec.ts`
**Build:** ReportDefinition fixes allowlisted query/fields and recipients; ReportSchedule stores IANA zone and occurrence identity. Recheck owner/recipient membership, source authorization and permitted projection at execution and download. Jobs carry references, not confidential rows; default email/push contains only a safe in-app link. Persist deduplication per scheduled occurrence and local delivery attempt; external delivery can remain Unknown and cannot promise exactly-once email.
**Tests:** `report_schedule_rechecks_revoked_recipient_access` · `report_schedule_retry_preserves_one_local_occurrence`
**Verify:** `(cd backend && just test-e2e -- test/reporting/schedules.e2e-spec.ts)`
**Done when:** A revoked recipient receives no new report authority and schedule retries create one local occurrence.

### 3.6.2 — Build report scheduling and delivery administration
**Repo:** frontend · **Size:** M · **Depends on:** `3.6.1` · **Requirements:** SR-API-006, UX-003/008/009/011
**Files:** `frontend/app/[locale]/reports/schedules/` · `frontend/src/features/reporting/` · `frontend/tests/reporting/schedules.spec.ts`
**Build:** Provide scoped definition preview, schedule timezone, recipients, pause/resume, occurrence history and safe delivery status. Distinguish generated, provider-accepted, Unknown and recipient-authorized; a delivery badge never changes business state. Explain expired artifacts and re-run permissions.
**Tests:** `report_schedule_ui_distinguishes_acceptance_from_completion`
**Verify:** `(cd frontend && npx --no-install playwright test tests/reporting/schedules.spec.ts --project=ar --project=en)`
**Done when:** An authorized user can schedule, pause and inspect a report in both locales without seeing confidential payloads in delivery metadata.

## Group 3.7 — Release 3

### 3.7.1 — Attack the public portal and provider integration boundaries
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `1.11.7`, `3.3.4`, `3.4.4`, `3.5.2`, `3.6.2` · **Requirements:** TEST-003/006, SR-NFR-SEC-001/003, SR-API-009
**Files:** `backend/test/security/phase3-boundaries.e2e-spec.ts` · `docs/implementation/evidence/phase3-security.md`
**Build:** Run target-version DAST and adversarial cases for capability guessing/leaks, IDOR, expired shares, alternate file versions, callback forgery, provider account mixup, finance projections and scout draft leakage. Use synthetic adversarial tenants and approved staging scope. Record manual assessment findings and remediate blocking findings before release; passing automation is not an ASVS certification.
**Tests:** `phase_three_public_and_provider_boundaries_resist_abuse`
**Verify:** `(cd backend && just test-e2e -- test/security/phase3-boundaries.e2e-spec.ts)`
**Done when:** Every blocking public-sharing and provider-boundary finding is fixed with a named regression.

### 3.7.2 — Accept and promote the agency intelligence release
**Repo:** umbrella · **Size:** M · **Depends on:** `3.7.1`, `3.7.3`, `3.7.4` · **Requirements:** BR-OBJ-07/09, TEST-005
**Files:** `docs/implementation/evidence/phase3-acceptance.md` · `docs/implementation/progress.md` · `scripts/tests/phase3_acceptance.py`
**Build:** Collect owner acceptance of scouting, sourced analytics, dossier sharing, finance policy and signature provider evidence; every prior Phase-3 leaf must be done at pinned merged revisions. Run the phase exit commands and demonstrate the journeys below. Promote with the existing per-repo development→staging→main flow and pin rules; the existing workflow, not this plan, governs release tags.
**Tests:** `phase_three_acceptance_requires_complete_evidence`
**Verify:** `python3 scripts/tests/phase3_acceptance.py && python3 scripts/check-plan.py`
**Done when:** Owner acceptance and passing exit evidence reference the merged application revisions pinned by the umbrella.

### 3.7.3 — Measure analytics, dossier and provider workload capacity
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `3.7.1`, `3.2.3` · **Requirements:** TEST-007, SR-NFR-PERF-001/002/003
**Files:** `backend/test/performance/phase3-capacity.spec.ts` · `docs/implementation/evidence/phase3-capacity.md`
**Build:** Extend the approved capacity envelope for comparative reads, concurrent public shares, PDF jobs and callback bursts. Check p95 simple≤500ms and complex≤2s, pool/worker queue budgets and fair tenant scheduling; report actual fixtures, concurrency, durations and infrastructure. Provider time is a separate measured dependency, never hidden inside an unbounded HTTP request.
**Tests:** `phase_three_capacity_envelope_meets_agreed_budgets`
**Verify:** `(cd backend && just test-int -- phase3-capacity)`
**Done when:** The reproducible workload stays within approved budgets or the release remains blocked with measured evidence.

### 3.7.4 — Recover immutable dossiers, signature and finance evidence
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `3.7.3` · **Requirements:** TEST-008, SR-NFR-REL-002, SR-AUD-007
**Files:** `backend/test/integration/phase3-recovery.integration-spec.ts` · `docs/implementation/evidence/phase3-recovery.md`
**Build:** Restore staging database/object versions/encryption keys/identity configuration to an isolated environment; verify ledger balance, signature source/result hashes, revoked shares, immutable grants/triggers and unreplayed outbox/inbox work. Measure RPO/RTO against approved targets and reconcile provider outcomes without repeating charges/signatures.
**Tests:** `phase_three_restore_preserves_finance_and_signature_evidence`
**Verify:** `(cd backend && just test-int -- phase3-recovery)`
**Done when:** A measured restore preserves immutable financial/signature evidence and does not duplicate external effects.

## Exit gate

```bash
python3 scripts/check-plan.py
(cd backend && just check && just migrations && just test-int && just test-e2e)
(cd frontend && just check && npx --no-install playwright test --project=ar --project=en)
python3 scripts/tests/phase3_acceptance.py
```

Demonstrate at pinned staging revisions: scout draft→immutable review→approved onboarding; source-traceable Arabic/English comparison; approved dossier shared, viewed, expired and revoked; rejected forged callbacks; one local posting after duplicate payment/signature events; policy-valid provider signing; scheduled report denied after recipient revocation; and measured recovery of source hashes, ledger entries and revoked grants. Acceptance records actual command results, dates, fixtures, owner approvals and unresolved nonblocking limits. Production provider/policy OPEN items are release blockers for the corresponding activated feature, not permission to mark an unbuilt requirement done.
