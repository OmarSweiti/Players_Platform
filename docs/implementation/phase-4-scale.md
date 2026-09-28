# Phase 4 — Scale and automation (BRD release 4)

> **Exit:** A second agency is onboarded without a code change; support access is explicit and attributable; measured scale, recovery and integration controls preserve current authorization.

These are planned targets. OIDC, PostgreSQL 18 and mandatory RLS are completed prerequisites from Phase 0; existing Phase-4 IDs now deepen assurance and operations rather than postponing those controls. Every new tenant table still ships same-tenant references, ENABLE/FORCE RLS, grants and catalog tests. [OPEN policy decisions](00-master-plan.md#open-register) keep optional integrations/AI/native transports disabled until approved; a feature gate is not evidence that the feature itself has been delivered.

```text
3.7.2 → 4.1 operators → support/provisioning → roles/usage/quotas ──┐
3.7.2 → 4.3.2 legal holds → 4.1.6 offboarding → operator UI ──────┤
3.7.2 → 4.2 SSO portability/passkeys → 4.3.4 upgrade/recovery ─────┤
4.1 roles/quotas → 4.3 RLS inventory/capacity ────────────────────┤
3.7.2 → 4.4 webhooks → partner/calendar → integration UI ─────────┤
3.7.2 → 4.5 policy → evaluation → reviewed suggestions ──────────┤
4.2 + 4.4 → 4.6 native contract/responsive readiness ─────────────┤
all leaves → 4.7 attack/load → second-agency acceptance
```

Step dependency fields are authoritative; later-numbered policy/evaluation/gate steps can precede earlier-numbered implementation steps. Commands run from the umbrella through the Phase-0 harness.

**Effort:** 25 steps (0 S / 3 M / 22 L); sizing capacity up to 376 focused hours +30% reserve = 488.8 hours, 19.6 weeks at 25 focused hours/week. Re-estimate against actual throughput at entry; split any step exceeding 16 hours before work.

## Group 4.1 — Platform operations

### 4.1.1 — Complete the separate platform operator control plane
**Repo:** backend · **Size:** L · **Depends on:** `3.7.2` · **Requirements:** SR-ACL-003, BR-RULE-12, SR-NFR-SEC-002
**Files:** `backend/src/modules/platform/application/operators.service.ts` · `backend/test/platform/operators.e2e-spec.ts`
**Build:** Extend the Phase-0 separation between platform identity and tenant membership; do not reintroduce SUPER_ADMIN as implicit tenant authority. PlatformOperator references verified global Identity with explicit operational permissions and assurance requirements. Add global PlatformSession linked to that operator/Identity, carrying only derived OIDC claims and the same opaque-cookie, CSRF, expiry, assurance and revocation semantics; every request checks the current session/operator in PostgreSQL. UserSession remains tenant-membership-bound; never invent a hidden User membership for operator login. TenantRegistry returns only permitted routing/status metadata. Control-plane services use narrow reviewed functions; platform operator credentials cannot perform arbitrary cross-tenant business queries or bypass RLS.
**Tests:** `platform_operator_has_no_implicit_business_data_access` · `platform_session_requires_no_hidden_tenant_membership`
**Verify:** `(cd backend && just test-e2e -- test/platform/operators.e2e-spec.ts)`
**Done when:** An operator can inspect permitted tenant routing metadata but cannot read any tenant confidential record without an active grant.

### 4.1.2 — Implement explicit time-limited support elevation
**Repo:** backend · **Size:** L · **Depends on:** `4.1.1` · **Requirements:** SR-ACL-003, SYS-TEN-008, BR-RULE-12
**Files:** `backend/src/modules/platform/application/support-grants.service.ts` · `backend/test/platform/support-grants.e2e-spec.ts`
**Build:** SupportAccessGrant binds operator identity, tenant, case, reason, allowed actions/resource classes, approver, startsAt/expiresAt and revokedAt. No self-approval; confidential classes require the corresponding owner’s approval and permitted purpose. Current PostgreSQL grant/identity/session/assurance checks precede each use; elevation establishes an explicit TenantContext through the same transaction wrapper. Audit request/approval/use/revocation using actor kind PLATFORM with {operatorId, sessionId, supportGrantId}; every tenant action carries that actor and grant, never a fabricated User or impersonation that hides the actual operator.
**Tests:** `support_grant_requires_distinct_approver_and_current_assurance` · `support_expiry_immediately_denies_subsequent_actions`
**Verify:** `(cd backend && just test-e2e -- test/platform/support-grants.e2e-spec.ts)`
**Done when:** Expired or revoked support elevation denies the next operation and every permitted action identifies the real operator and grant.

### 4.1.3 — Turn tenant provisioning into a recoverable operator workflow
**Repo:** backend · **Size:** L · **Depends on:** `4.1.1` · **Requirements:** BR-OBJ-08, SYS-TEN-001/008, SR-CORE-010
**Files:** `backend/src/modules/platform/application/provisioning.service.ts` · `backend/test/platform/provisioning.e2e-spec.ts`
**Build:** Wrap the 0.5.9 provisioning CLI contract in a durable idempotent workflow: validate slug/region/policy/entitlement selection, create TenantRegistry/Tenant, seed minimal roles/configuration and invite the initial owner through approved OIDC enrollment. Persist resumable step receipts and compensate only safe incomplete work. Never generate a shared password or hidden tenant-member support account. Failures leave a visible restricted provisioning state.
**Tests:** `platform_provisioning_retry_creates_one_tenant` · `platform_provisioning_failure_is_resumable_without_hidden_access`
**Verify:** `(cd backend && just test-e2e -- test/platform/provisioning.e2e-spec.ts)`
**Done when:** Retrying after any provisioning checkpoint creates one tenant and one accountable owner invitation.

### 4.1.4 — Allow tenant roles within an approved permission ceiling
**Repo:** backend · **Size:** L · **Depends on:** `4.1.2` · **Requirements:** SR-ACL-004/005/006/008
**Files:** `backend/src/modules/authorization/application/tenant-roles.service.ts` · `backend/test/authorization/custom-roles.e2e-spec.ts`
**Build:** TenantRole and assignments reference the versioned global permission catalog, with same-tenant FKs, FORCE RLS and grants. Custom roles select allowed permissions; they cannot weaken ABAC, add unsupported categories, grant platform operations, self-escalate or assign confidential authority without the approved owner workflow. Changes are audited and take effect on the next request; snapshot prior permissions in safe evidence and test cache invalidation.
**Tests:** `custom_role_cannot_exceed_assigner_or_policy_ceiling` · `custom_role_revocation_applies_on_next_request`
**Verify:** `(cd backend && just test-e2e -- test/authorization/custom-roles.e2e-spec.ts)`
**Done when:** A role edit changes permitted actions immediately without bypassing relationship, confidentiality or platform boundaries.

### 4.1.5 — Measure entitlements and tenant usage
**Repo:** backend · **Size:** L · **Depends on:** `4.1.3` · **Requirements:** BR-OBJ-08/09, SYS-TEN-006, SR-DB-003
**Files:** `backend/src/modules/platform/application/entitlements.service.ts` · `backend/test/platform/entitlements.e2e-spec.ts`
**Build:** Version tenant entitlements and metered dimensions such as active memberships, storage bytes and processing jobs. Counts use durable idempotent usage events and reconciliation against authoritative records. Feature/limit checks are server-side and do not become permissions to hidden data. OPEN — commercial packaging: default one owner-approved package with explicit limits, no automatic billing or invented pricing; finance consumes approved charges only through its own workflow.
**Tests:** `tenant_usage_reconciliation_preserves_exact_counts` · `tenant_entitlement_does_not_grant_data_permission`
**Verify:** `(cd backend && just test-e2e -- test/platform/entitlements.e2e-spec.ts)`
**Done when:** Repeated usage events do not inflate counts and a granted feature never bypasses authorization.

### 4.1.6 — Offboard tenants while preserving required evidence
**Repo:** backend · **Size:** L · **Depends on:** `4.1.5`, `4.3.2` · **Requirements:** BR-RULE-11/12, SR-AUD-007, SR-ACL-009
**Files:** `backend/src/modules/platform/application/offboarding.service.ts` · `backend/test/platform/offboarding.e2e-spec.ts`
**Build:** Implement approved Suspend→ExportPending→RetentionPending→EligibleForPurge workflow. Suspension revokes application sessions and disables API/realtime/jobs except reviewed recovery/export duties. Deliver a permission-scoped documented data export with integrity manifest; preserve legal holds, finance/signature/audit evidence and approved retention. No timed purge is enabled without owner/counsel policy and separately authorized retention credentials.
**Tests:** `tenant_suspension_revokes_sessions_jobs_and_realtime` · `tenant_offboarding_preserves_held_evidence`
**Verify:** `(cd backend && just test-e2e -- test/platform/offboarding.e2e-spec.ts)`
**Done when:** Suspension denies new business access while offboarding cannot delete held or unexpired required evidence.

### 4.1.7 — Enforce fair quotas under noisy-neighbor load
**Repo:** backend · **Size:** L · **Depends on:** `4.1.5` · **Requirements:** SR-NFR-PERF-001/002/003, SYS-ASY-004
**Files:** `backend/src/modules/platform/application/quotas.service.ts` · `backend/test/performance/tenant-fairness.spec.ts`
**Build:** Apply atomic per-tenant concurrent job/upload/storage quotas and bounded API categories; partition worker scheduling by tenant fairness without treating Valkey as the correctness store. Reserve/refund usage idempotently across crash/retry. Demonstrate one tenant’s import/video flood cannot exhaust all DB connections or prevent another tenant’s normal API traffic; tune measured envelopes and explicit 429/queued states.
**Tests:** `tenant_noisy_neighbor_cannot_starve_other_tenant` · `tenant_quota_reservation_recovers_after_worker_crash`
**Verify:** `(cd backend && just test-int -- tenant-fairness)`
**Done when:** A noisy tenant remains bounded while another tenant stays within its agreed API latency budget.

### 4.1.8 — Build the operator and tenant administration workspace
**Repo:** frontend · **Size:** L · **Depends on:** `4.1.2`, `4.1.3`, `4.1.4`, `4.1.6`, `4.1.7` · **Requirements:** PRD-AD-001, SYS-TEN-008, UX-003/005/006/008/009/011
**Files:** `frontend/app/[locale]/platform/` · `frontend/src/features/platform/` · `frontend/tests/platform/operations.spec.ts`
**Build:** Provide provisioning status, usage/limits, support request/approval/revocation and controlled offboarding. Clearly distinguish platform context from selected tenant context, actual operator and expiring support scope. Tenant admins receive only their role/entitlement screens. Clear confidential query state on every context switch; privileged operations route through current MFA/reauth requirements.
**Tests:** `platform_workspace_shows_real_actor_and_support_scope`
**Verify:** `(cd frontend && npx --no-install playwright test tests/platform/operations.spec.ts --project=ar --project=en)`
**Done when:** An operator provisions and supports a tenant in both locales without confusing platform authority with tenant data permission.

## Group 4.2 — Enterprise identity assurance

### 4.2.1 — Prove enterprise SSO and identity-provider portability
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `3.7.2` · **Requirements:** SR-AUTH-001/002/007, BR-OBJ-08, SR-DB-010
**Files:** `backend/src/modules/auth/oidc/` · `backend/test/auth/enterprise-sso.e2e-spec.ts` · `docs/implementation/evidence/identity-portability.md`
**Build:** OIDC is already implemented in Phase 0; this step qualifies enterprise federation and provider exit. Test a second approved issuer in isolated staging, explicit issuer/subject mapping, assurance mapping, verified back-channel logout and failure isolation. Linking or migration requires identity proof and an audited owner-approved mapping; email equality never links identities. Rehearse exporting recoverable identity configuration without persisting login provider tokens in Sodara. Document residual provider-change exposure until validated event or app-session expiry.
**Tests:** `enterprise_sso_never_links_identity_by_email` · `identity_provider_exit_preserves_membership_and_revocation`
**Verify:** `(cd backend && just test-e2e -- test/auth/enterprise-sso.e2e-spec.ts)`
**Done when:** A rehearsed approved issuer change preserves membership policy and revocation behavior without email-only linking.

### 4.2.2 — Qualify provider-managed passkeys and recovery assurance
**Repo:** backend + frontend · **Size:** L · **Depends on:** `4.2.1` · **Requirements:** SR-AUTH-008/002, TEST-005/009/010
**Files:** `backend/test/auth/passkey-assurance.e2e-spec.ts` · `frontend/tests/auth/passkeys.spec.ts` · `docs/implementation/evidence/passkeys.md`
**Build:** Enable passkeys only in the approved IdP profile after verifying authenticators, enrollment/recovery, accessibility and assurance mapping on the pinned provider release. Sodara consumes validated acr/amr/auth_time and does not implement a second credential store. Test recovery or weaker fallback cannot satisfy a privileged step-up policy accidentally; use ar/en provider screens and avoid assuming every passkey ceremony means MFA.
**Tests:** `passkey_recovery_cannot_bypass_privileged_assurance` · `passkey_provider_screens_support_both_locales`
**Verify:** `(cd backend && just test-e2e -- test/auth/passkey-assurance.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/auth/passkeys.spec.ts --project=ar --project=en)`
**Done when:** Approved passkey and recovery journeys preserve the same privileged authorization requirements in both locales.

## Group 4.3 — Continuous data defense and measured scale

### 4.3.1 — Keep RLS coverage complete as the schema grows
**Repo:** backend · **Size:** M · **Depends on:** `3.7.2`, `4.1.4` · **Requirements:** SYS-TEN-005, SR-NFR-SEC-003, TEST-002/003
**Files:** `backend/test/integration/rls-inventory.integration-spec.ts` · `backend/prisma/migrations/` · `docs/implementation/evidence/rls-inventory.md`
**Build:** RLS on all tenant tables is a Phase-0 requirement and a migration invariant, not work first introduced here. Expand automated catalog discovery to flag any tenant table without ENABLE/FORCE policies, grants or same-tenant relationships, including partition children and new outbox/inbox tables. Exercise non-owner roles, missing/hostile tenant context, pooled rollback/reuse, worker contexts and denied TRUNCATE on evidence.
**Tests:** `rls_inventory_rejects_unprotected_new_tenant_table`
**Verify:** `(cd backend && just test-int -- rls-inventory)`
**Done when:** The schema-wide runtime-role suite fails when a new tenant table lacks any required isolation control.

### 4.3.2 — Complete governed legal-hold administration
**Repo:** backend · **Size:** L · **Depends on:** `3.7.2` · **Requirements:** SR-AUD-007, BR-RULE-11/12, SR-DOC-007
**Files:** `backend/src/modules/retention/application/legal-holds.service.ts` · `backend/test/retention/legal-holds.e2e-spec.ts`
**Build:** Extend the Phase-1 retention classifications and hold/purge safety guards into a formal hold workflow with case, scope, authority, effective time, approver, release reason and immutable history. Hold checks apply to business records, linked immutable FileObjects, derived artifacts, exports and backup expiry policy. Distinct approval releases a hold; release does not immediately purge, but recalculates ordinary retention eligibility. Jurisdiction and duration are counsel-owned OPEN policy, not hard-coded law.
**Tests:** `legal_hold_blocks_all_linked_retention_actions` · `legal_hold_release_requires_authorized_approval`
**Verify:** `(cd backend && just test-e2e -- test/retention/legal-holds.e2e-spec.ts)`
**Done when:** An active hold prevents deletion of every scoped record/artifact and release leaves an attributable approval trail.

### 4.3.3 — Scale only the measured bottleneck
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `4.3.1`, `4.1.7` · **Requirements:** SYS-ARC-004, SR-DB-006, SR-NFR-PERF-001/003
**Files:** `backend/test/performance/scale-envelope.spec.ts` · `docs/implementation/evidence/scale-decision.md`
**Build:** Profile the approved multi-tenant envelope before selecting an intervention. Compare index/query/worker tuning first; partition audit/messages, add replicas/search infrastructure or extract a service only when a measured requirement justifies its operations cost. Retain same tenant/field policy in derived stores; never read current session, membership, support grants or authorization from a lagging replica. Implement one smallest qualifying improvement or record that no topology change is needed, with reproducible before/after evidence.
**Tests:** `scale_candidate_preserves_authorization_and_capacity`
**Verify:** `(cd backend && just test-int -- scale-envelope)`
**Done when:** The chosen change or no-change decision is supported by reproducible capacity and authorization results.

### 4.3.4 — Rehearse platform upgrades and full recovery
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `4.3.3`, `4.2.2` · **Requirements:** SR-DB-005, TEST-008, SR-NFR-REL-002
**Files:** `backend/test/integration/platform-upgrade.integration-spec.ts` · `docs/implementation/evidence/platform-upgrade.md`
**Build:** PostgreSQL 18 is aligned in Phase 0; this step rehearses its next approved patch/toolchain/provider upgrade rather than deferring that alignment. Restore production-shaped synthetic database/object versions/keys/IdP configuration into isolation, replay forward migrations, validate SQL-managed objects separately from Prisma diff and run OIDC/session/RLS/evidence tests. Record rollback-by-restore boundaries, measured RPO/RTO and provider compatibility before promotion.
**Tests:** `platform_upgrade_restores_sql_objects_and_identity_config`
**Verify:** `(cd backend && just test-int -- platform-upgrade)`
**Done when:** The approved upgrade passes a timed recoverable rehearsal with all custom SQL and identity controls intact.

## Group 4.4 — Integrations

### 4.4.1 — Deliver signed outbound webhooks safely
**Repo:** backend · **Size:** L · **Depends on:** `3.7.2` · **Requirements:** SYS-ASY-001/002/003/004/005, SR-API-007/009
**Files:** `backend/src/modules/integrations/application/outbound-webhooks.service.ts` · `backend/test/integrations/outbound-webhooks.e2e-spec.ts`
**Build:** WebhookSubscription binds tenant, approved event types, endpoint and rotating signing-secret reference. Outbox/inbox processing creates stable event/delivery IDs; sign bounded minimal payload bytes with timestamp and key ID. Validate HTTPS destinations, DNS resolution and redirects against SSRF/private-network policy on every attempt, bound response/time/size and retry/backoff. Record Accepted/Failed/Unknown honestly; consumers deduplicate stable event IDs and no exactly-once remote effect is promised.
**Tests:** `outbound_webhook_blocks_private_network_and_redirect_targets` · `outbound_webhook_retry_reuses_stable_event_identity`
**Verify:** `(cd backend && just test-e2e -- test/integrations/outbound-webhooks.e2e-spec.ts)`
**Done when:** A retried signed event retains its identity and cannot reach disallowed network destinations.

### 4.4.2 — Expose a narrow partner API with current authorization
**Repo:** backend · **Size:** L · **Depends on:** `4.4.1`, `4.1.4` · **Requirements:** SR-API-009/001/002, SR-ACL-005/008
**Files:** `backend/src/modules/integrations/application/partner-access.service.ts` · `backend/test/integrations/partner-api.e2e-spec.ts`
**Build:** Define approved partner capabilities and a separate service-principal credential profile: tenant-bound, least-scope, expiring/rotatable/revocable opaque secrets stored only as hashes, or an approved equivalent after ADR review. Keep the public partner route group and throttle independent of browser routes. Every request checks current credential, tenant, permission and object policy under TenantContext/RLS; an IdP bearer token alone is not accepted by the browser API. No medical/legal/finance projection is enabled without explicit owner policy.
**Tests:** `partner_credential_cannot_exceed_tenant_object_scope` · `partner_credential_revocation_applies_on_next_request`
**Verify:** `(cd backend && just test-e2e -- test/integrations/partner-api.e2e-spec.ts)`
**Done when:** A revoked or out-of-scope partner credential cannot access either internal routes or unauthorized tenant objects.

### 4.4.3 — Integrate calendars through explicit limited consent
**Repo:** backend · **Size:** L · **Depends on:** `4.4.1` · **Requirements:** SYS-ASY-002/003, SR-CORE-009, BR-RULE-07
**Files:** `backend/src/modules/integrations/application/calendar.service.ts` · `backend/test/integrations/calendar.e2e-spec.ts`
**Build:** OPEN — calendar provider/data policy: default disabled. Once approved, request minimum scopes and store connector-specific refresh credentials encrypted with separate key access, never in browser/logs. This storage is for an explicitly approved integration, not persistence of OIDC login tokens. Synchronize approved training/general events only with stable mapping and tombstones; exclude medical appointments and confidential narratives by default. Disconnect revokes provider consent where supported, stops jobs and removes secrets according to policy.
**Tests:** `calendar_consent_excludes_confidential_event_content` · `calendar_disconnect_stops_jobs_and_revokes_connector`
**Verify:** `(cd backend && just test-e2e -- test/integrations/calendar.e2e-spec.ts)`
**Done when:** An approved calendar connection syncs only permitted events and disconnection prevents later synchronization.

### 4.4.4 — Build integration consent and delivery administration
**Repo:** frontend · **Size:** L · **Depends on:** `4.4.2`, `4.4.3` · **Requirements:** PRD-AD-001, UX-003/005/006/008/009/011
**Files:** `frontend/app/[locale]/settings/integrations/` · `frontend/src/features/integrations/` · `frontend/tests/integrations/administration.spec.ts`
**Build:** Provide scopes/consent review, credential issue-once/rotation/revoke, webhook delivery status/retry and calendar disconnect. Never display stored full secrets after issuance or confidential webhook payloads in history. Show target, event scope and unknown remote outcome distinctly; privileged changes require current assurance and confirmation.
**Tests:** `integration_admin_exposes_scope_without_stored_secrets`
**Verify:** `(cd frontend && npx --no-install playwright test tests/integrations/administration.spec.ts --project=ar --project=en)`
**Done when:** An administrator can revoke each integration type in both locales without exposing stored credentials.

## Group 4.5 — Human-reviewed assistance

### 4.5.1 — Approve AI data, model and human-review governance
**Repo:** umbrella + backend · **Size:** M · **Depends on:** `3.7.2` · **Requirements:** BR-OBJ-09, BR-RULE-02/07/12, SR-CORE-009
**Files:** `docs/reference/domain-workflows.md` · `backend/src/modules/assistance/domain/assistance-policy.ts` · `backend/test/assistance/policy.e2e-spec.ts`
**Build:** OPEN — AI assistance policy: default disabled. Owner/privacy counsel approves provider/region/retention, permitted fields, consent basis, attribution, evaluation criteria, cost limit and human approval. No clinical diagnosis, player eligibility, contract approval, signing or financial posting is delegated to a model. Treat retrieved reports as untrusted data; no tool authority, hidden workflow mutation or unapproved provider training reuse.
**Tests:** `assistance_activation_requires_approved_data_policy`
**Verify:** `(cd backend && just test-e2e -- test/assistance/policy.e2e-spec.ts)`
**Done when:** The assistance feature cannot call a model until an approved data policy and evaluation criteria exist.

### 4.5.2 — Offer attributable draft summaries under human control
**Repo:** backend + frontend · **Size:** L · **Depends on:** `4.5.1`, `4.5.3` · **Requirements:** PRD-SC-001, BR-OBJ-04, SR-ACL-005/008, UX-005/011
**Files:** `backend/src/modules/assistance/application/summaries.service.ts` · `frontend/src/features/assistance/` · `backend/test/assistance/summaries.e2e-spec.ts` · `frontend/tests/assistance/summaries.spec.ts`
**Build:** Generate bounded scouting/report draft summaries from the current caller’s permitted source snapshot only. Record source IDs/versions, model/policy version and review action without unnecessary source text in telemetry. UI labels suggestions and requires human edit/approve/reject before any saved business note; source access is rechecked at retrieval/acceptance. Model output cannot alter ratings, recommend clinical clearance, post money or transition contracts.
**Tests:** `assistance_summary_requires_human_acceptance_and_current_sources` · `assistance_output_cannot_execute_business_commands` · `assistance_review_ui_requires_explicit_human_acceptance`
**Verify:** `(cd backend && just test-e2e -- test/assistance/summaries.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/assistance/summaries.spec.ts --project=ar --project=en)`
**Done when:** A generated suggestion becomes an attributed draft note only after explicit authorized human acceptance.

### 4.5.3 — Evaluate source faithfulness and disclosure before activation
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `4.5.1` · **Requirements:** TEST-003/006, BR-RULE-02/07, SR-NFR-SEC-003
**Files:** `backend/test/assistance/evaluation.e2e-spec.ts` · `docs/implementation/evidence/assistance-evaluation.md`
**Build:** Use synthetic Arabic/English source sets with unsupported-claim, missing-data, conflicting-record, prompt-injection, tenant and confidential-field canaries. Measure source faithfulness and prohibited-output rates against preapproved thresholds; compare relevant cohorts for systematic quality differences without inventing legal fairness certification. An unapproved provider/version or failing evaluation disables calls. Document limits and human review workload.
**Tests:** `assistance_evaluation_blocks_injection_and_cross_tenant_canaries` · `assistance_unapproved_model_version_is_disabled`
**Verify:** `(cd backend && just test-e2e -- test/assistance/evaluation.e2e-spec.ts)`
**Done when:** Only a policy-approved model version meeting the recorded evaluation thresholds can be activated.

## Group 4.6 — Mobile readiness

### 4.6.1 — Review a native client session profile without weakening web sessions
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `4.2.2`, `4.4.2` · **Requirements:** SR-CORE-002/003/004, SR-AUTH-007, BR-OBJ-08
**Files:** `backend/test/auth/native-session-contract.e2e-spec.ts` · `docs/implementation/evidence/native-readiness.md`
**Build:** This is mobile readiness, not delivery of a native app. Review a public-client authorization-code/PKCE and app-session exchange profile with proof of redirect ownership, secure device storage, explicit revocation and the same current PostgreSQL session/membership policy. Keep the profile disabled until a separate reviewed ADR resolves threats and provider support; no bare provider bearer bypass or persisted browser login tokens. Run adapter contract fixtures proving any proposed transport cannot skip app-session revocation, tenant context or projection. Web cookie/CSRF behavior remains the canonical deployed profile.
**Tests:** `native_session_profile_cannot_bypass_app_revocation`
**Verify:** `(cd backend && just test-e2e -- test/auth/native-session-contract.e2e-spec.ts)`
**Done when:** The reviewed readiness record and executable contract fixtures preserve app-session authorization without enabling an unapproved native transport.

### 4.6.2 — Verify responsive workflows under constrained networks
**Repo:** frontend · **Size:** L · **Depends on:** `4.1.8`, `4.4.4`, `4.5.2`, `4.6.1` · **Requirements:** UX-009/011, SR-NFR-A11Y-001, TEST-009/010
**Files:** `frontend/tests/mobile/readiness.spec.ts` · `docs/implementation/evidence/mobile-readiness.md`
**Build:** Test supported narrow viewports, touch/keyboard, interrupted uploads, reconnecting chat, slow API, expired sessions and ar/en bidirectional data. Preserve safe user drafts after recoverable failures, keep medical/finance content out of persistent browser caches and avoid offline write queues that bypass current policy. Record supported devices/browsers and unresolved native-only capabilities as scope, not implemented features.
**Tests:** `mobile_readiness_recovers_without_persistent_confidential_cache`
**Verify:** `(cd frontend && npx --no-install playwright test tests/mobile/readiness.spec.ts --project=ar --project=en)`
**Done when:** The supported responsive workflows remain usable under network interruption without stale-authority writes or confidential persistent caches.

## Group 4.7 — Release 4

### 4.7.1 — Accept a second agency through the complete operating model
**Repo:** umbrella · **Size:** M · **Depends on:** `4.7.2`, `4.3.4`, `4.6.2` · **Requirements:** BR-OBJ-08/09, TEST-005/008
**Files:** `docs/implementation/evidence/phase4-acceptance.md` · `scripts/tests/phase4_acceptance.py` · `docs/implementation/progress.md`
**Build:** Onboard a synthetic second agency in staging through the operator interface alone. Demonstrate isolated identity/membership, permitted support, custom roles, quotas, offboarding safeguards, integration revocation and recovery. Collect owner approval and complete every prior Phase-4 leaf at merged/pinned revisions; promote through the existing delivery flow. Optional AI/calendar/native features may remain policy-disabled, but implemented gates/fixtures and their approved scope disposition must be recorded honestly.
**Tests:** `phase_four_acceptance_requires_second_agency_evidence`
**Verify:** `python3 scripts/tests/phase4_acceptance.py && python3 scripts/check-plan.py`
**Done when:** Owner-approved evidence proves a second agency can operate and recover without a code change or implicit platform access.

### 4.7.2 — Attack and load-test the full multi-tenant platform
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `4.1.8`, `4.3.4`, `4.4.4`, `4.5.2`, `4.6.2` · **Requirements:** TEST-003/006/007, SR-NFR-PERF-001/003, SR-NFR-SEC-003
**Files:** `backend/test/performance/phase4-capacity.spec.ts` · `backend/test/security/phase4-isolation.e2e-spec.ts` · `docs/implementation/evidence/phase4-assurance.md`
**Build:** Run the agreed two-agency workload with skewed noisy-neighbor traffic, support grants expiring mid-operation, role revocation, partner callbacks, share access and worker retries. Combine runtime-role SQL tests with object/cache/job/socket/file abuse tests and scoped staging DAST. Publish capacity, p95, queue lag, pool utilization and blocking finding closure; do not label a penetration test or certification complete unless independently performed with evidence.
**Tests:** `phase_four_workload_preserves_two_tenant_isolation` · `phase_four_capacity_resists_skewed_tenant_load`
**Verify:** `(cd backend && just test-e2e -- test/security/phase4-isolation.e2e-spec.ts && just test-int -- phase4-capacity)`
**Done when:** Two agencies remain isolated and within approved capacity budgets with every blocking security finding resolved.

## Exit gate

```bash
python3 scripts/check-plan.py
(cd backend && just check && just migrations && just test-int && just test-e2e)
(cd frontend && just check && npx --no-install playwright test --project=ar --project=en)
python3 scripts/tests/phase4_acceptance.py
```

Demonstrate: a second agency provisioned without source changes; no cross-agency business access from platform metadata; distinct support approval, expiry and revocation; custom-role revocation on the next request; tenant fairness under skewed load; a held document surviving offboarding; verified integration disconnect/revocation; passkey recovery respecting assurance; and a timed PostgreSQL/object/key/IdP recovery. Optional assistance, calendar and native readiness retain explicit policy scope and do not count as an implemented native application or an automated professional decision system.
