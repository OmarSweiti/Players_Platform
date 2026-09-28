# Phase 1 — MVP (BRD release 1)

> **Exit:** the first agency operates its player, contract and legal workflows in production, in Arabic and English, with reviewed signature evidence, confidential projections, reliable notifications and a demonstrated recovery path.

This is a prospective execution plan; no step is implemented by this document. All original 45 Phase-1 IDs are retained. Appended IDs split schema, API, UI and operational work into reviewable changes. Read the [engineering law](01-conventions.md), [domain workflows](../reference/domain-workflows.md) and [progress](progress.md). Requirement priorities P0/P1 are not release numbers. Medical, training, chat and provider signing retain their later release owners.

**Entry:** Phase-0 gate 0.11.1 passes at reviewed umbrella pins. Estimates are falsifiable: S ≤ 4 hours, M ≤ 8 hours, L ≤ 16 hours, excluding stakeholder/provider waiting. Record actual cycle time; split before exceeding 16 hours. An OPEN prerequisite cannot be marked done by assuming its answer.

**Effort:** 64 steps (0 S / 17 M / 47 L), sizing capacity up to 888 focused hours +30% reserve = 1,154.4 hours, or 46.2 weeks at 25 focused hours/week. This is a capacity bound, not a promised date. Reforecast from measured cycle time using the [effort model](00-master-plan.md#effort-model); provider and reviewer waiting time is tracked separately.

**Execution contract:** commands run from the umbrella root unless a subshell changes directory. Phase-0 owns just test-int/test-e2e argument forwarding and zero-test failure. Tests live in feature-based files; every title has exactly one microstep owner. Each Files list gives the test location. Cross-app steps run each applicable runner. Scripts/manifests named below are FUTURE artifacts implemented by their owning step, not commands claimed to exist today.

Every route joins the permission/two-tenant inventories from 0.6.2/0.6.9. Mutations use revision/If-Match, tenant transaction, atomic redacted audit/outbox and the agreed response/error contract. Every new tenant table ships composite FKs, FORCE RLS, runtime grants, SQL catalog assertions and negative runtime tests in the same migration. Append-only versions, decisions and signature evidence deny runtime UPDATE/DELETE/TRUNCATE and test their guards. Migrations test empty replay and populated upgrade fixtures; unmapped legacy content stays quarantined. Every UI slice covers ar/en, RTL/LTR, loading/empty/error/retry states, keyboard focus and forbidden users.

## Group dependency graph

```text
0.11.1 ──→ 1.1 administration ─────────────────────────────────────────┐
       ├─→ 1.2 core player/organizations → 1.3 documents → 1.4 contracts├─→ 1.7 audit/timeline
       │                                       └──────→ 1.5 legal ───┘
       ├─→ 1.6 notifications ──────────────────────────→ 1.4 / 1.5
       └─→ 1.10.1 hosting → 1.10.2 images → 1.10.11 staging
1.4 / 1.5 ──→ 1.8 search/dashboard and 1.9 exports
1.7 + 1.3/1.4/1.5 safe summaries ──→ 1.2.7 Player 360
all feature groups + staging → operational gates 1.10.3–1.10.15 → 1.10.9 launch
```

This summarizes integration boundaries, not a rigid group order: Player 360 waits for later safe summaries; initial CRUD does not. Exact Depends on fields govern execution. Hosting inquiries start early.

## Legacy URL retirement ownership

The current stored URL fields and their source evidence appear below; existing values are not assumed safe.

| Current field and evidence | Final owner | Replacement |
|---|---|---|
| Tenant.logoUrl (backend/prisma/schema.prisma:280) | 1.1.2 | brandingFileObjectId, tenant branding binding |
| User.avatarUrl (backend/prisma/schema.prisma:334) | 1.1.8 | avatarFileObjectId, membership avatar binding |
| Document.fileUrl (backend/prisma/schema.prisma:448) | 1.3.1 | fileObjectId plus typed entity binding; 0.8.2 provides prerequisite |
| PlayerMedia.fileUrl (backend/prisma/schema.prisma:538) | 1.3.3 | fileObjectId plus player-media binding |
| Contract.fileUrl (backend/prisma/schema.prisma:624) | 1.4.1 | currentVersionId constrained to this contract and tenant |
| ContractVersion.fileUrl (backend/prisma/schema.prisma:670) | 1.4.8 | immutable fileObjectId, SHA-256 and exact storage version |
| Conversation.imageUrl (backend/prisma/schema.prisma:1029) | 2.6.2 | conversation image binding; chat remains gated meanwhile |
| Message.fileUrl (backend/prisma/schema.prisma:1270) | 2.6.5 | message attachment binding; chat remains gated meanwhile |

Each removal owner inventories values, maps verified same-tenant blobs through quarantine/scan, retains a restricted remediation report, expands and reads safe typed references, then drops the legacy column after compatibility is proven. Never fetch arbitrary legacy URLs on a request or invent clean scan results.

## Group 1.1 — Tenant and user administration

### 1.1.1 — Users: list, invite, deactivate and change role
**Repo:** backend · **Size:** L · **Depends on:** `0.11.1` · **Requirements:** PRD-AD-001, SR-ACL-002, SR-ACL-006, SR-ACL-007, UX-001, BR-OBJ-08
**Files:** `backend/src/modules/users/application/administration.service.ts`, `backend/src/modules/users/presentation/users.controller.ts`, `backend/test/users/administration.e2e-spec.ts`
**Build:** GET /api/v1/users, PATCH /users/{id}/role and POST /users/{id}/deactivate|reactivate reuse invitation commands from 0.5.10. Change tenant membership, never provider credentials. changeRole(ctx,targetId,role,expectedRevision) checks grant policy, locks the active-owner set, refuses last-owner removal and immediately invalidates affected application sessions. Concurrent owner deactivations cannot remove every owner. Explicit audited reactivation preserves reserved normalized email. Lists use safe membership projections. Test ownership in the matching feature file on Files: backend owns `user_administration_preserves_last_owner_under_race`; backend owns `membership_deactivation_revokes_access_immediately`; backend owns `role_change_is_audited_and_cannot_escalate`.
**Tests:** `user_administration_preserves_last_owner_under_race` · `membership_deactivation_revokes_access_immediately` · `role_change_is_audited_and_cannot_escalate`
**Verify:** `(cd backend && just test-e2e -- test/users/administration.e2e-spec.ts)`
**Done when:** Concurrent role/deactivation commands preserve an active owner, deny escalation and revoke the target's next application request.

### 1.1.2 — Tenant settings and private branding
**Repo:** backend + frontend · **Size:** L · **Depends on:** `0.11.1` · **Requirements:** PRD-AD-001, UX-001, UX-007, SR-AUTH-002, SR-CORE-006, SR-DOC-002
**Files:** `backend/src/modules/tenants/application/settings.service.ts`, `backend/src/modules/tenants/presentation/settings.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_tenant_branding/migration.sql`, `frontend/src/features/settings/tenant-settings.tsx`, `frontend/app/[locale]/settings/tenant/page.tsx`, `backend/test/settings/tenant.e2e-spec.ts`, `frontend/tests/settings/tenant.spec.ts`
**Build:** PATCH /api/v1/tenant allows name, default locale, IANA timezone, enabled currency and stricter MFA role requirements; it cannot weaken mandatory policy. Use If-Match and safe before/after audit. Retire Tenant.logoUrl for same-tenant brandingFileObjectId using the protocol above; only clean immutable images qualify. Branding uses authorized downloads, never public buckets. Currency changes do not reinterpret existing amounts; timezone changes affect rendering and future schedule calculations only. Test ownership in the matching feature file on Files: backend owns `tenant_settings_preserve_existing_money_and_instants`; frontend owns `tenant_settings_branding_rejects_foreign_file`.
**Tests:** `tenant_settings_preserve_existing_money_and_instants` · `tenant_settings_branding_rejects_foreign_file`
**Verify:** `(cd backend && just test-e2e -- test/settings/tenant.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/settings/tenant.spec.ts) && (cd backend && just migrations)`
**Done when:** An owner changes safe settings in both locales without reinterpreting existing amounts/instants or exposing foreign branding.

### 1.1.3 — Own profile, locale and identity security links
**Repo:** backend + frontend · **Size:** L · **Depends on:** `0.11.1`, `1.1.7` · **Requirements:** SR-CORE-007, SR-AUTH-002, SR-AUTH-007, UX-003, UX-008, PRD-AD-001
**Files:** `backend/src/modules/users/application/profile.service.ts`, `backend/src/modules/users/presentation/profile.controller.ts`, `frontend/src/features/profile/profile-page.tsx`, `frontend/app/[locale]/settings/profile/page.tsx`, `backend/test/users/profile.e2e-spec.ts`, `frontend/tests/users/profile.spec.ts`
**Build:** PATCH /api/v1/me changes local display fields and preferred locale only. Show application sessions and existing revoke commands. Security actions redirect through the approved Keycloak flow with validated return path and ui_locales. Do not render local passwords, TOTP seeds, generated recovery codes or provider tokens. Provider email/credentials stay provider-managed; primary PostgreSQL membership/session checks remain mandatory on every request. Test ownership in the matching feature file on Files: backend owns `own_profile_update_cannot_change_roles_or_identity`; frontend owns `profile_security_actions_use_localized_provider_flow`.
**Tests:** `own_profile_update_cannot_change_roles_or_identity` · `profile_security_actions_use_localized_provider_flow`
**Verify:** `(cd backend && just test-e2e -- test/users/profile.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/users/profile.spec.ts)`
**Done when:** A user changes locale, revokes an application session and reaches localized provider security pages without local credential handling.

### 1.1.4 — Per-tenant release flags
**Repo:** backend · **Size:** M · **Depends on:** `0.11.1` · **Requirements:** PRD-AD-001, SR-ACL-006, SR-MED-007, BR-RULE-07
**Files:** `backend/src/modules/tenants/application/feature-flags.service.ts`, `backend/src/modules/tenants/presentation/feature-flags.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_tenant_feature_flags/migration.sql`, `backend/test/settings/feature-flags.e2e-spec.ts`
**Build:** FeatureFlag(tenantId,key,enabled,revision) sits below a server release allowlist and environment kill switch: effective = released AND environmentEnabled AND tenantEnabled. Admins cannot enable medical/scouting before their later release gates. Changes audit and invalidate effective navigation/cache; disabled routes return 404. Expose only current tenant flags. Test ownership in the matching feature file on Files: backend owns `tenant_flag_cannot_override_unreleased_module`; backend owns `flag_change_is_audited_and_immediately_effective`.
**Tests:** `tenant_flag_cannot_override_unreleased_module` · `flag_change_is_audited_and_immediately_effective`
**Verify:** `(cd backend && just test-e2e -- test/settings/feature-flags.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** A tenant flag affects released modules immediately and cannot enable quarantined medical or scouting routes.

### 1.1.5 — The permission matrix, visible
**Repo:** backend + frontend · **Size:** M · **Depends on:** `1.1.1` · **Requirements:** PRD-AD-001, SR-ACL-004, SR-ACL-005, UX-004
**Files:** `backend/src/modules/users/presentation/permissions.controller.ts`, `frontend/src/features/settings/permission-matrix.tsx`, `frontend/app/[locale]/settings/permissions/page.tsx`, `backend/test/users/permission-matrix.e2e-spec.ts`, `frontend/tests/users/permission-matrix.spec.ts`
**Build:** GET /api/v1/permissions/matrix requires administration permission and returns catalog version, baseline roles and object-policy caveats. Render a read-only accessible matrix; explain that roles alone do not grant confidential access. Do not expose another tenant's configuration; customization remains later work. Test ownership in the matching feature file on Files: backend owns `permission_matrix_is_scoped_to_authorized_administrator`; frontend owns `permission_matrix_distinguishes_role_from_object_policy`.
**Tests:** `permission_matrix_is_scoped_to_authorized_administrator` · `permission_matrix_distinguishes_role_from_object_policy`
**Verify:** `(cd backend && just test-e2e -- test/users/permission-matrix.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/users/permission-matrix.spec.ts)`
**Done when:** The matrix matches the catalog and distinguishes role grants from resource-policy decisions.

### 1.1.6 — The user administration workspace
**Repo:** frontend · **Size:** L · **Depends on:** `1.1.1`, `1.1.4` · **Requirements:** PRD-AD-001, UX-001, UX-002, UX-003, UX-004, UX-009
**Files:** `frontend/src/features/users/user-directory.tsx`, `frontend/src/features/users/invitation-dialog.tsx`, `frontend/app/[locale]/settings/users/page.tsx`, `frontend/tests/users/administration.spec.ts`
**Build:** Build users/pending-invitations tables, invite/revoke/resend, role changes and deactivate/reactivate confirmation. Preserve safe input after validation; stale revisions require reload/compare, never blind replay of privilege changes. Tenant identity comes from the session. Show forbidden and last-owner outcomes using stable API codes. Test ownership in the matching feature file on Files: frontend owns `administrator_invites_and_deactivates_in_both_locales`; frontend owns `administrator_conflicting_role_edit_requires_reload`.
**Tests:** `administrator_invites_and_deactivates_in_both_locales` · `administrator_conflicting_role_edit_requires_reload`
**Verify:** `(cd frontend && npx --no-install playwright test tests/users/administration.spec.ts)`
**Done when:** An owner completes invitation, role change and deactivation with localized confirmation and accurate post-change access.

### 1.1.7 — Keycloak Arabic and English journey theme
**Repo:** umbrella + frontend · **Size:** L · **Depends on:** `0.11.1` · **Requirements:** SR-CORE-007, SR-NFR-I18N-001, SR-NFR-A11Y-001, TEST-009, TEST-010, UX-008, UX-012
**Files:** `infra/keycloak/themes/sodara/login/theme.properties`, `infra/keycloak/themes/sodara/login/messages/messages_ar.properties`, `infra/keycloak/themes/sodara/login/messages/messages_en.properties`, `infra/keycloak/themes/sodara/login/resources/css/sodara.css`, `infra/keycloak/realm-sodara.json`, `scripts/check-keycloak-theme.py`, `scripts/tests/test_keycloak_theme.py`, `frontend/tests/identity/keycloak-theme.spec.ts`
**Build:** Extend the exact pinned Keycloak release's supported theme contract: login, reset/recovery, required actions, MFA enrollment/challenge, errors and return-to-application. Include localized provider email actions. Credentials stay entirely in Keycloak. Implement lang/dir, logical CSS, accessible labels/focus/live errors. check-keycloak-theme.py compares required message keys/templates against that release. Browser tests use synthetic provider users and cover each state in both locales; launch includes native Arabic and screen-reader review. Test ownership in the matching feature file on Files: umbrella owns `test_keycloak_theme_has_required_locale_keys`; frontend owns `keycloak_login_recovery_and_mfa_are_bilingual`. This step also wires `python3 -m unittest discover -s scripts/tests` into the umbrella's `just check` and its required `test` job, so umbrella tests run in CI.
**Tests:** `test_keycloak_theme_has_required_locale_keys` · `keycloak_login_recovery_and_mfa_are_bilingual`
**Verify:** `python3 scripts/check-keycloak-theme.py && python3 -m unittest discover -s scripts/tests -p 'test_keycloak_theme.py' && (cd frontend && npx --no-install playwright test tests/identity/keycloak-theme.spec.ts)`
**Done when:** Provider login, recovery and MFA journeys complete in Arabic RTL and English LTR with accessible translated states.

### 1.1.8 — Private membership avatars
**Repo:** backend + frontend · **Size:** M · **Depends on:** `1.1.3` · **Requirements:** SR-DOC-001, SR-DOC-002, SR-DOC-003, SR-ACL-008, UX-003
**Files:** `backend/src/modules/users/application/avatar.service.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_membership_avatar_file/migration.sql`, `frontend/src/features/profile/avatar-editor.tsx`, `backend/test/users/avatar.e2e-spec.ts`, `frontend/tests/users/avatar.spec.ts`
**Build:** Retire User.avatarUrl or its migrated membership equivalent for avatarFileObjectId plus same-tenant owner binding. Do not trust an IdP image URL as an authorized object. setAvatar(ctx,fileId,expectedRevision) accepts a clean immutable allowed image, strips unsafe metadata and audits replacement. Memberships in different tenants do not implicitly share avatar objects. Test ownership in the matching feature file on Files: backend owns `membership_avatar_rejects_cross_tenant_or_pending_file`; frontend owns `profile_avatar_uses_authorized_versioned_download`.
**Tests:** `membership_avatar_rejects_cross_tenant_or_pending_file` · `profile_avatar_uses_authorized_versioned_download`
**Verify:** `(cd backend && just test-e2e -- test/users/avatar.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/users/avatar.spec.ts) && (cd backend && just migrations)`
**Done when:** An avatar uses the private file pipeline and cannot reference another tenant or unscanned content.

## Group 1.2 — Players

### 1.2.1 — The player record and lifecycle
**Repo:** backend · **Size:** L · **Depends on:** `0.11.1` · **Requirements:** BR-OBJ-01, SR-PL-001, SR-PL-002, SR-PL-003, SR-PL-011, BR-RULE-11, SYS-ARC-001, SYS-ARC-002
**Files:** `backend/src/modules/players/domain/player.ts`, `backend/src/modules/players/application/player.service.ts`, `backend/src/modules/players/presentation/players.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_player_profile/migration.sql`, `backend/test/players/record.e2e-spec.ts`
**Build:** Implement create/read/update/archive/reactivate with revision and safe projections. Cover the SRS fields: bilingual names, civil DOB, nationalities, positions, preferred foot, dimensions and protected identity/emergency fields. Separate lifecycleStage(PROSPECT, ONBOARDING, ACTIVE, ARCHIVED) from sporting availability; use named transition commands. Minimal prospects support later scouting; full onboarding uses stage completeness. Passport/minor/emergency data is absent by default including errors/logs. Archive preserves files/audit; reactivation is explicit. Reach identity/documents through module application interfaces. Test ownership in the matching feature file on Files: backend owns `player_write_preserves_tenant_and_protected_fields`; backend owns `player_archive_is_recoverable_without_evidence_loss`.
**Tests:** `player_write_preserves_tenant_and_protected_fields` · `player_archive_is_recoverable_without_evidence_loss`
**Verify:** `(cd backend && just test-e2e -- test/players/record.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Authorized CRUD/archive works while protected fields stay absent from unauthorized projections and evidence remains recoverable.

### 1.2.2 — Organizations and club history
**Repo:** backend · **Size:** L · **Depends on:** `1.2.1` · **Requirements:** BR-OBJ-01, SR-PL-002, PRD-PL-001, SR-DB-003, SR-NFR-MNT-002
**Files:** `backend/src/modules/organizations/application/organizations.service.ts`, `backend/src/modules/players/application/affiliations.service.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_player_affiliations/migration.sql`, `backend/test/players/affiliations.e2e-spec.ts`
**Build:** Add tenant-owned Organization(id,tenantId,nameAr,nameEn,kind,revision) and PlayerAffiliation(playerId,organizationId,kind,startsOn,endsOn). Map currentClub strings through reviewed mappings only; preserve unresolved values for remediation. An open permanent affiliation determines current club; loan/permanent kinds may coexist according to policy. Enforce ordered dates, same-tenant parents and no overlapping permanent affiliation under concurrent writes. Export application services for contract counterparties. Test ownership in the matching feature file on Files: backend owns `club_history_rejects_overlapping_permanent_affiliations`; backend owns `club_upgrade_preserves_unmatched_legacy_names`.
**Tests:** `club_history_rejects_overlapping_permanent_affiliations` · `club_upgrade_preserves_unmatched_legacy_names`
**Verify:** `(cd backend && just test-e2e -- test/players/affiliations.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Club history preserves legacy evidence and refuses cross-tenant or overlapping permanent affiliations.

### 1.2.3 — Player and guardian account workspace
**Repo:** backend + frontend · **Size:** L · **Depends on:** `1.2.1` · **Requirements:** PRD-PL-001, SR-ACL-005, SR-ACL-008, SR-PL-003, UX-005
**Files:** `backend/src/modules/players/application/account-links.service.ts`, `backend/src/modules/players/presentation/account-links.controller.ts`, `frontend/src/features/players/account-links.tsx`, `frontend/app/[locale]/my-player/page.tsx`, `backend/test/players/accounts.e2e-spec.ts`, `frontend/tests/players/accounts.spec.ts`
**Build:** Reuse relationships from 0.6.5, adding audited grant/revoke commands with revision, scopes and evidence reference. OPEN child-protection policy: default gives guardians nothing until an authorized explicit link and approved scope exist. PLAYER/GUARDIAN roles alone do not grant passport/medical/legal/compensation access. Revoke invalidates caches and denies the next request. Own-player workspace omits hidden sections, counts and snippets. Test ownership in the matching feature file on Files: backend owns `guardian_link_revocation_denies_next_request`; frontend owns `player_and_guardian_views_omit_ungranted_sections`.
**Tests:** `guardian_link_revocation_denies_next_request` · `player_and_guardian_views_omit_ungranted_sections`
**Verify:** `(cd backend && just test-e2e -- test/players/accounts.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/players/accounts.spec.ts)`
**Done when:** A linked account sees only approved scopes and loses them on the first request after revocation.

### 1.2.4 — Player directory, search and filters
**Repo:** backend + frontend · **Size:** L · **Depends on:** `1.2.2` · **Requirements:** PRD-PL-001, SR-PL-002, SR-CORE-004, SR-API-004, UX-004, UX-009
**Files:** `backend/src/modules/players/application/search-players.query.ts`, `backend/src/modules/players/domain/name-search.ts`, `frontend/src/features/players/player-directory.tsx`, `frontend/app/[locale]/players/page.tsx`, `backend/test/players/directory.e2e-spec.ts`, `frontend/tests/players/directory.spec.ts`
**Build:** GET /api/v1/players uses cursor envelope, stable sort and allowlisted position/status/club/nationality/stage filters. Arabic alef/diacritic normalization changes search keys only, never displayed names. Latin-Arabic matching requires explicit bilingual names/aliases, not assumed transliteration. Apply policy before counts/page construction. Add keyboard table controls, filter chips and user-scoped saved views. Test ownership in the matching feature file on Files: backend owns `player_search_preserves_names_and_scopes_results`; frontend owns `player_directory_filters_are_keyboard_accessible`.
**Tests:** `player_search_preserves_names_and_scopes_results` · `player_directory_filters_are_keyboard_accessible`
**Verify:** `(cd backend && just test-e2e -- test/players/directory.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/players/directory.spec.ts)`
**Done when:** Normalized Arabic names and explicit Latin aliases find only authorized players with stable pagination.

### 1.2.5 — Profile completeness by lifecycle stage
**Repo:** backend + frontend · **Size:** M · **Depends on:** `1.2.1` · **Requirements:** PRD-PL-002, SR-PL-004, BR-OBJ-01
**Files:** `backend/src/modules/players/domain/profile-completeness.ts`, `backend/src/modules/players/application/completeness-rules.service.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_profile_completeness_rules/migration.sql`, `frontend/src/features/players/completeness-panel.tsx`, `backend/test/players/completeness.e2e-spec.ts`, `frontend/tests/players/completeness.spec.ts`
**Build:** ProfileCompletenessRule(tenantId,stage,fieldKey,required,version) is allowlisted. computeCompleteness(player,ruleVersion,projection) returns deterministic score and visible missing actions; rule changes audit/invalidate results. OPEN agency field requirements: provisional defaults are visibly marked; minimal prospects are not blocked by active-player fields. Hidden fields/values must not leak through missing-field names or scores. Test ownership in the matching feature file on Files: backend owns `profile_completeness_uses_versioned_stage_rules`; frontend owns `profile_completeness_hides_ungranted_field_details`.
**Tests:** `profile_completeness_uses_versioned_stage_rules` · `profile_completeness_hides_ungranted_field_details`
**Verify:** `(cd backend && just test-e2e -- test/players/completeness.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/players/completeness.spec.ts) && (cd backend && just migrations)`
**Done when:** The same rule version gives the same score and exposes only permitted actionable missing information.

### 1.2.6 — Duplicate detection before player creation
**Repo:** backend + frontend · **Size:** M · **Depends on:** `1.2.4`, `1.2.8` · **Requirements:** BR-OBJ-01, PRD-PL-002, SR-PL-001, UX-003
**Files:** `backend/src/modules/players/application/find-duplicates.query.ts`, `frontend/src/features/players/duplicate-review.tsx`, `backend/test/players/duplicates.e2e-spec.ts`, `frontend/tests/players/duplicates.spec.ts`
**Build:** Offer authorized possible duplicates from normalized name/DOB/nationality with safe reasons. Similarity is advisory; never merge automatically or treat a name as unique. User opens an existing authorized record or confirms creation with reason; audit that choice. Hidden candidates do not reveal existence. Recheck on final create to handle concurrent submissions without rejecting legitimate same-name people. Test ownership in the matching feature file on Files: backend owns `duplicate_suggestions_never_reveal_hidden_players`; frontend owns `player_creation_requires_duplicate_review_when_suggested`.
**Tests:** `duplicate_suggestions_never_reveal_hidden_players` · `player_creation_requires_duplicate_review_when_suggested`
**Verify:** `(cd backend && just test-e2e -- test/players/duplicates.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/players/duplicates.spec.ts)`
**Done when:** A user resolves a duplicate warning without silent merging or disclosure of an inaccessible player.

### 1.2.7 — Player 360
**Repo:** frontend · **Size:** L · **Depends on:** `1.2.5`, `1.3.3`, `1.4.7`, `1.5.4`, `1.7.2` · **Requirements:** PRD-PL-001, SR-PL-008, UX-005, UX-009, TEST-005
**Files:** `frontend/src/features/players/player-360.tsx`, `frontend/app/[locale]/players/[id]/page.tsx`, `frontend/tests/players/player-360.spec.ts`
**Build:** Compose identity/completeness/club/media/contracts/legal/activity from safe application query APIs. Performance/training/medical wait for later release flags and policies; no hidden diagnostic counts. Panels recover independently from errors. Query keys include tenant/projection; clear on logout or membership change. Mobile tabs, headings, keyboard navigation and absolute/relative timeline dates work both directions. Test ownership in the matching feature file on Files: frontend owns `player_360_composes_only_permitted_module_summaries`; frontend owns `player_360_is_usable_in_mobile_rtl_and_ltr`.
**Tests:** `player_360_composes_only_permitted_module_summaries` · `player_360_is_usable_in_mobile_rtl_and_ltr`
**Verify:** `(cd frontend && npx --no-install playwright test tests/players/player-360.spec.ts)`
**Done when:** The MVP 360 shows authorized current summaries in both locales without requesting unreleased or confidential sections for unprivileged users.

### 1.2.8 — Player creation, editing and archive forms
**Repo:** frontend · **Size:** L · **Depends on:** `1.2.1`, `1.2.2` · **Requirements:** SR-PL-001, SR-PL-002, SR-PL-011, UX-002, UX-003, UX-009
**Files:** `frontend/src/features/players/player-form.tsx`, `frontend/src/features/players/archive-dialog.tsx`, `frontend/app/[locale]/players/new/page.tsx`, `frontend/app/[locale]/players/[id]/edit/page.tsx`, `frontend/tests/players/forms.spec.ts`
**Build:** Build accepted profile fields, organization picker and civil-date inputs. Preserve safe input after recoverable errors; discard protected inputs on permission loss. If-Match conflicts require reload/compare. Archive confirmation explains recoverability; reactivation is explicit. UI permissions shape rendering/payload but never replace backend checks. Test ownership in the matching feature file on Files: frontend owns `player_form_preserves_safe_input_after_validation_error`; frontend owns `player_archive_and_conflict_actions_require_confirmation`.
**Tests:** `player_form_preserves_safe_input_after_validation_error` · `player_archive_and_conflict_actions_require_confirmation`
**Verify:** `(cd frontend && npx --no-install playwright test tests/players/forms.spec.ts)`
**Done when:** Staff create/edit/archive in ar/en without timezone date shifts or silent conflicting overwrites.

## Group 1.3 — Documents and media

### 1.3.1 — Typed document ownership and legacy URL retirement
**Repo:** backend · **Size:** L · **Depends on:** `1.2.1` · **Requirements:** SR-DOC-001, SR-DOC-002, SR-DOC-005, SR-DOC-006, SR-DB-008, BR-OBJ-02
**Files:** `backend/src/modules/documents/application/document-bindings.service.ts`, `backend/src/modules/documents/presentation/documents.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_typed_document_ownership/migration.sql`, `backend/test/documents/ownership.e2e-spec.ts`
**Build:** Finish Document.fileUrl retirement through the Phase-0 pipeline. Add explicit PlayerDocument/ContractDocument/LegalTicketDocument relationships with valid same-tenant parents, replacing active polymorphic ownership. bindDocument(ctx,owner,fileObjectId,classification,expectedRevision) checks current owner policy and clean immutable version. List/download/archive inherit file and entity confidentiality. Replacements create new versions; unknown legacy blobs/bindings remain inaccessible in a remediation queue. Test ownership in the matching feature file on Files: backend owns `typed_document_binding_requires_same_tenant_parent`; backend owns `document_upgrade_quarantines_unmapped_legacy_url`; backend owns `document_replacement_preserves_historical_file_version`.
**Tests:** `typed_document_binding_requires_same_tenant_parent` · `document_upgrade_quarantines_unmapped_legacy_url` · `document_replacement_preserves_historical_file_version`
**Verify:** `(cd backend && just test-e2e -- test/documents/ownership.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Every accessible document has a typed same-tenant owner and immutable file version with no active legacy URL path.

### 1.3.2 — Document scan operations and recovery
**Repo:** backend + frontend · **Size:** M · **Depends on:** `1.3.1` · **Requirements:** SR-DOC-003, SR-DOC-004, SR-NFR-PERF-002, UX-010, UX-011
**Files:** `backend/src/modules/documents/application/scan-status.query.ts`, `backend/src/modules/documents/application/retry-scan.command.ts`, `frontend/src/features/documents/scan-status.tsx`, `backend/test/documents/scan-operations.e2e-spec.ts`, `frontend/tests/documents/scan-operations.spec.ts`
**Build:** Reuse 0.8.4 scanning/promotion. Display pending/scanning/clean/rejected/failed states; missing scanner means unavailable, never clean. Authorized transient retries are idempotent and bind immutable source identity. No user can override INFECTED or change a clean object's version. Errors do not reflect malicious filenames or confidential scanner internals. Test ownership in the matching feature file on Files: backend owns `scan_retry_cannot_promote_infected_or_changed_object`; frontend owns `document_scan_failure_has_safe_accessible_retry`.
**Tests:** `scan_retry_cannot_promote_infected_or_changed_object` · `document_scan_failure_has_safe_accessible_retry`
**Verify:** `(cd backend && just test-e2e -- test/documents/scan-operations.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/documents/scan-operations.spec.ts)`
**Done when:** Transient scans can be retried while infected or changed source bytes never become downloadable.

### 1.3.3 — Player images and private media bindings
**Repo:** backend + frontend · **Size:** L · **Depends on:** `1.3.1`, `1.3.2` · **Requirements:** SR-PL-005, SR-PL-007, SR-DOC-002
**Files:** `backend/src/modules/players/application/player-media.service.ts`, `backend/src/workers/media/image-variants.handler.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_player_media_files/migration.sql`, `frontend/src/features/players/media-gallery.tsx`, `backend/test/players/media.e2e-spec.ts`, `frontend/tests/players/media.spec.ts`
**Build:** Retire PlayerMedia.fileUrl for fileObjectId plus same-tenant binding. Keep caption/attribution/safe metadata; SQL partial unique and serialized command enforce one active featured image per player. Bounded image worker strips EXIF/GPS, limits dimensions/decompression and writes immutable variants. Refuse executable/SVG inline content. Authorize player and exact version for every image. Video remains Phase 2. Test ownership in the matching feature file on Files: backend owns `player_featured_image_is_unique_under_concurrent_changes`; backend owns `image_variant_processing_removes_location_metadata`; frontend owns `player_gallery_only_displays_authorized_clean_images`.
**Tests:** `player_featured_image_is_unique_under_concurrent_changes` · `image_variant_processing_removes_location_metadata` · `player_gallery_only_displays_authorized_clean_images`
**Verify:** `(cd backend && just test-e2e -- test/players/media.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/players/media.spec.ts) && (cd backend && just migrations)`
**Done when:** The gallery has one featured clean image at most and exposes neither legacy URLs nor location metadata.

### 1.3.4 — Retention classification and hold-aware cleanup
**Repo:** backend · **Size:** L · **Depends on:** `1.3.1` · **Requirements:** SR-DOC-007, SR-AUD-007, BR-RULE-11
**Files:** `backend/src/modules/documents/application/retention.service.ts`, `backend/src/workers/documents/retention.handler.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_retention_classification/migration.sql`, `backend/test/documents/retention.e2e-spec.ts`
**Build:** RetentionClass records policy version/category; document classification retains the applied version. OPEN counsel/agency periods: default is no purge of business/evidence records, archive only. Unfinished temporary uploads expire only under approved operational policy with no finalized reference or preservation marker. Every cleanup checks holds/dependencies; audit classification changes. Full hold administration remains later work; preservation guards are required now. Test ownership in the matching feature file on Files: backend owns `document_retention_default_never_purges_business_evidence`; backend owns `document_cleanup_preserves_held_or_referenced_versions`.
**Tests:** `document_retention_default_never_purges_business_evidence` · `document_cleanup_preserves_held_or_referenced_versions`
**Verify:** `(cd backend && just test-e2e -- test/documents/retention.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Cleanup removes only eligible unreferenced temporary uploads and preserves business evidence and held content.

### 1.3.5 — Shared document upload and history component
**Repo:** frontend · **Size:** L · **Depends on:** `1.3.1`, `1.3.2` · **Requirements:** SR-DOC-001, SR-DOC-005, UX-002, UX-003, UX-009, UX-011
**Files:** `frontend/src/features/documents/document-uploader.tsx`, `frontend/src/features/documents/document-history.tsx`, `frontend/tests/documents/workspace.spec.ts`
**Build:** Build reusable upload/list/download/archive for an authorized typed owner. Progress includes quarantine/scan. Reauthorize expired download links; never persist presigned URLs in local storage/analytics. Show immutable version/uploader/time. Archive/replacement explain retained evidence. Retry finalization with original operation identity and accessible errors. Test ownership in the matching feature file on Files: frontend owns `document_upload_journey_waits_for_clean_scan`; frontend owns `document_replacement_keeps_visible_version_history`.
**Tests:** `document_upload_journey_waits_for_clean_scan` · `document_replacement_keeps_visible_version_history`
**Verify:** `(cd frontend && npx --no-install playwright test tests/documents/workspace.spec.ts)`
**Done when:** Users upload, wait for scanning, download and replace documents while authorized history remains intact.

## Group 1.4 — Contracts

### 1.4.1 — Contracts: counterparties, terms and current version
**Repo:** backend · **Size:** L · **Depends on:** `1.2.2`, `1.4.8` · **Requirements:** BR-OBJ-02, SR-CT-002, SR-CT-003, SR-CT-004, SR-CT-005, SR-DB-003
**Files:** `backend/src/modules/contracts/domain/contract.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_contract_terms/migration.sql`, `backend/test/contracts/terms.integration-spec.ts`
**Build:** Add same-tenant counterpartyOrganizationId, optional season, tenant-unique human reference and revision. Represent compensation as NUMERIC(19,4)+CurrencyDefinition+period; JSON APIs use decimal strings. Validate enabled currency/exponent and ordered civil dates. Preserve all SRS contract types; REPRESENTATION is an agency-policy extension pending agency confirmation, not assumed legal fact. OPEN contract subject policy: retain the required player link by default; coaching/non-player agreements need an approved model extension, never a fabricated player. Retire Contract.fileUrl for currentVersionId constrained by (versionId,contractId,tenantId); only verified mappings may populate it. Restrict compensation projection and never copy values to generic audit payloads. Test ownership in the matching feature file on Files: backend owns `contract_terms_enforce_dates_currency_and_counterparty`; backend owns `contract_current_version_belongs_to_same_contract`.
**Tests:** `contract_terms_enforce_dates_currency_and_counterparty` · `contract_current_version_belongs_to_same_contract`
**Verify:** `(cd backend && just test-int -- test/contracts/terms.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** Contracts have valid same-tenant parties, exact restricted compensation and a current version belonging to that contract.

### 1.4.2 — The contract state machine
**Repo:** backend · **Size:** M · **Depends on:** `1.4.1` · **Requirements:** BR-RULE-03, BR-RULE-04, SR-CT-001, SR-CT-008, PRD-CT-001
**Files:** `backend/src/modules/contracts/domain/contract-state-machine.ts`, `backend/src/modules/contracts/domain/signature-policy.ts`, `backend/src/modules/contracts/domain/contract-state-machine.spec.ts`
**Build:** transition(state,command,context) is pure over DRAFT, IN_REVIEW, APPROVED, SIGNED, EXPIRED, TERMINATED and REJECTED. Define every allowed edge and rejected edge in domain-workflows; no generic PATCH status. SIGNED requires approvals for current immutable version plus evidence satisfying an approved enabled policy. Missing counsel-approved policy means SIGNED disabled; uploaded PDFs alone do not qualify. Domain tests use synthetic approved-policy fixtures, not claims of legal validity. New versions invalidate stale approvals; termination/expiry require their explicit guards. Test ownership in the matching feature file on Files: backend owns `contract_state_machine_rejects_every_illegal_edge`; backend owns `contract_signing_requires_enabled_policy_and_current_evidence`.
**Tests:** `contract_state_machine_rejects_every_illegal_edge` · `contract_signing_requires_enabled_policy_and_current_evidence`
**Verify:** `(cd backend && npx --no-install jest --selectProjects unit --runInBand --runTestsByPath src/modules/contracts/domain/contract-state-machine.spec.ts)`
**Done when:** Exhaustive state/command tests reject illegal transitions and signing without current approvals plus an approved evidence policy.

### 1.4.3 — Drafting and immutable version commands
**Repo:** backend · **Size:** L · **Depends on:** `1.4.2`, `1.3.1` · **Requirements:** SR-CT-006, SR-CT-012, PRD-CT-003, SR-API-005, SR-DOC-005
**Files:** `backend/src/modules/contracts/application/draft-contract.command.ts`, `backend/src/modules/contracts/application/create-version.command.ts`, `backend/src/modules/contracts/presentation/contracts.controller.ts`, `backend/test/contracts/drafting.e2e-spec.ts`
**Build:** Require Idempotency-Key for version creation; check current authorization, then replay a completed matching request before applying If-Match to a new execution. A successful retry using its original now-stale revision returns the original result; changed payload under the same key conflicts. Create/list/read drafts and createVersion(ctx,contractId,cleanFileId,terms,changeNote,expectedRevision). Lock contract revision and allocate the next version number atomically; unique(contractId,version) prevents duplicates. Store immutable terms/file snapshot and SHA-256; replace no evidence bytes. A new version preserves prior snapshots and emits a version-changed outbox event; 1.4.9 adds atomic approval invalidation when approval tables exist, and 1.4.5 adds signature-evidence invalidation when its tables exist. Audit every access and mutation safely, and fail the read when mandatory confidential-access audit fails. The additional retry test is in backend/test/contracts/drafting.e2e-spec.ts. Test ownership in the matching feature file on Files: backend owns `contract_version_creation_serializes_concurrent_writers`; backend owns `contract_new_version_preserves_previous_snapshot`; backend owns `contract_access_requires_successful_redacted_audit`.
**Tests:** `contract_version_creation_serializes_concurrent_writers` · `contract_new_version_preserves_previous_snapshot` · `contract_access_requires_successful_redacted_audit` · `contract_retry_replays_success_despite_stale_original_revision`
**Verify:** `(cd backend && just test-e2e -- test/contracts/drafting.e2e-spec.ts)`
**Done when:** Concurrent drafting creates unique immutable versions without changing prior snapshots and audits all permitted contract access.

### 1.4.4 — Expiry monitoring and reminders
**Repo:** backend · **Size:** L · **Depends on:** `1.4.3`, `1.6.1` · **Requirements:** SR-CT-009, PRD-CT-002, BR-RULE-10, UX-007
**Files:** `backend/src/modules/contracts/application/expiry.service.ts`, `backend/src/workers/contracts/expiry.handler.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_contract_reminders/migration.sql`, `backend/test/contracts/expiry.integration-spec.ts`
**Build:** Tenant settings define reminder offsets, provisionally 90/30/7 calendar days until agency approval. Persist reminder schedule policy/version and dedupe by tenant/contract/version/offset/dueDate/recipient/channel. Worker discovers tenants then claims in each tenant transaction. Reevaluate current status/policy; signed contracts expire after civil endDate in the named tenant timezone. Notification failure does not reverse expiry or make an unsigned contract effective. Fix clocks in tests across DST and UTC−10/UTC+14. Test ownership in the matching feature file on Files: backend owns `contract_expiry_uses_tenant_civil_date`; backend owns `contract_reminders_dedupe_without_driving_business_state`.
**Tests:** `contract_expiry_uses_tenant_civil_date` · `contract_reminders_dedupe_without_driving_business_state`
**Verify:** `(cd backend && just test-int -- test/contracts/expiry.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** Expiry and reminders run correctly across timezone boundaries and retries without duplicate business outcomes.

### 1.4.5 — Signature evidence under an approved manual policy
**Repo:** backend · **Size:** L · **Depends on:** `1.4.9`, `1.3.1` · **Requirements:** BR-RULE-04, SR-CT-008, SR-CT-012, SR-DOC-005
**Files:** `backend/src/modules/contracts/application/create-version.command.ts`, `backend/src/modules/contracts/domain/signature-policy.ts`, `backend/src/modules/contracts/application/record-signature-evidence.command.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_signature_evidence/migration.sql`, `backend/test/contracts/signature-evidence.e2e-spec.ts`
**Build:** Add Signatory(id,tenantId,contractVersionId,identityReference,required) and append-only SignatureEvent(evidenceId,kind,occurredAt,actorId,sourceReference) beside append-only SignatureEvidence(id,tenantId,contractVersionId,fileObjectId,sha256,policyVersion,signatoryReference,attestedById,attestedAt,recordedState). All same-version/tenant links are constrained; manual events are distinguished from later provider events. OPEN counsel/agency must approve permitted manual evidence, signatory verification and jurisdiction; until then SIGNED is disabled, evidence may be collected in pending-review state only. Record original approved-document hash and signed-artifact hash distinctly, plus immutable linkage and attestation; a different artifact cannot replace the approved version. verifyEvidence(ctx,id,expectedRevision) appends a verification event after checking current approval, reviewer and policy; current verification state is derived from append-only events, never updated on evidence. Extend create-version.command.ts to append superseded-evidence events atomically when the current contract version changes. No legal-validity claim follows from hashing. Provider envelope/webhook implementation belongs to Phase 3. Test ownership in the matching feature file on Files: backend owns `manual_signature_stays_disabled_without_approved_policy`; backend owns `signature_evidence_is_bound_to_approved_version`; backend owns `signature_evidence_cannot_be_mutated_by_runtime_role`.
**Tests:** `manual_signature_stays_disabled_without_approved_policy` · `signature_evidence_is_bound_to_approved_version` · `signature_evidence_cannot_be_mutated_by_runtime_role`
**Verify:** `(cd backend && just test-e2e -- test/contracts/signature-evidence.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Signing is possible only with the current version's approvals and evidence verified under a recorded counsel-approved policy.

### 1.4.6 — Termination
**Repo:** backend + frontend · **Size:** M · **Depends on:** `1.4.4` · **Requirements:** SR-CT-010, SR-CT-012, UX-002
**Files:** `backend/src/modules/contracts/application/terminate-contract.command.ts`, `frontend/src/features/contracts/terminate-dialog.tsx`, `backend/test/contracts/termination.e2e-spec.ts`, `frontend/tests/contracts/termination.spec.ts`
**Build:** terminate(ctx,id,effectiveDate,reason,expectedRevision) requires explicit permission and recent authentication, validates domain transitions/dates and audits the reason safely. Cancel unsent reminders atomically while retaining all historical versions/evidence. Future-dated termination must be an explicit scheduled policy decision; default requires effective-now civil date until agency answers. UI confirms consequence and resolves conflicts without automatic retry. Test ownership in the matching feature file on Files: backend owns `contract_termination_preserves_evidence_and_cancels_reminders`; frontend owns `contract_termination_requires_reason_and_confirmation`.
**Tests:** `contract_termination_preserves_evidence_and_cancels_reminders` · `contract_termination_requires_reason_and_confirmation`
**Verify:** `(cd backend && just test-e2e -- test/contracts/termination.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/contracts/termination.spec.ts)`
**Done when:** Authorized termination records its effective date/reason and cancels future reminders without altering historical evidence.

### 1.4.7 — The contract workspace
**Repo:** frontend · **Size:** L · **Depends on:** `1.4.3`, `1.4.4`, `1.4.5`, `1.4.6`, `1.4.10`, `1.3.5` · **Requirements:** PRD-CT-001, PRD-CT-002, PRD-CT-003, UX-004, UX-005, UX-006, TEST-005
**Files:** `frontend/src/features/contracts/contract-workspace.tsx`, `frontend/src/features/contracts/signature-evidence-panel.tsx`, `frontend/app/[locale]/contracts/page.tsx`, `frontend/app/[locale]/contracts/[id]/page.tsx`, `frontend/tests/contracts/workspace.spec.ts`
**Build:** Lists filter by player/status/expiry/season/owner; details compose timeline, version metadata, approval history and evidence state. Compensation is omitted from unauthorized API payloads and cache, not CSS-hidden. Show pending legal policy explicitly; do not offer SIGNED while policy disabled. Upload/attest evidence through the existing document component. Present civil deadlines consistently in ar/en and show document/version identity to reviewers. Test ownership in the matching feature file on Files: frontend owns `contract_workspace_hides_ungranted_compensation`; frontend owns `contract_workspace_respects_policy_and_civil_deadlines`.
**Tests:** `contract_workspace_hides_ungranted_compensation` · `contract_workspace_respects_policy_and_civil_deadlines`
**Verify:** `(cd frontend && npx --no-install playwright test tests/contracts/workspace.spec.ts)`
**Done when:** Users navigate contracts, approvals and evidence in both locales with accurate signing availability and no unauthorized compensation.

### 1.4.8 — Immutable contract versions and file migration
**Repo:** backend · **Size:** L · **Depends on:** `1.2.2`, `1.3.1` · **Requirements:** SR-CT-006, SR-DOC-005, SR-NFR-MNT-002
**Files:** `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_immutable_contract_versions/migration.sql`, `backend/src/modules/contracts/infrastructure/version.repository.ts`, `backend/test/contracts/version-schema.integration-spec.ts`
**Build:** Retire ContractVersion.fileUrl for clean fileObjectId, SHA-256, immutable terms snapshot, creator and change note. Add unique(contractId,version), unique(id,contractId,tenantId) for same-parent references. Preserve baseline records via explicit verified blob mappings and quarantine unresolved ones; never rewrite signed bytes or fabricate a digest. Protect versions with grants and triggers against runtime UPDATE/DELETE/TRUNCATE. Tests inspect pg_catalog and attempt mutations under sodara_app, including migration replay and populated upgrade. Test ownership in the matching feature file on Files: backend owns `contract_version_file_upgrade_preserves_original_evidence`; backend owns `contract_version_sql_guards_reject_runtime_mutations`.
**Tests:** `contract_version_file_upgrade_preserves_original_evidence` · `contract_version_sql_guards_reject_runtime_mutations`
**Verify:** `(cd backend && just test-int -- test/contracts/version-schema.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** Version identity/file/hash survive populated upgrade and all runtime attempts to change historical versions are rejected.

### 1.4.9 — Ordered approval rounds and immutable decisions
**Repo:** backend · **Size:** L · **Depends on:** `1.4.3` · **Requirements:** SR-CT-007, SR-CT-008, SR-CT-012, BR-RULE-03, PRD-CT-001
**Files:** `backend/src/modules/contracts/application/create-version.command.ts`, `backend/src/modules/contracts/application/submit-review.command.ts`, `backend/src/modules/contracts/application/decide-approval.command.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_contract_approval_rounds/migration.sql`, `backend/test/contracts/approvals.e2e-spec.ts`
**Build:** Snapshot approval policy into ApprovalRound(contractId,contractVersionId,round,policyVersion) and ordered ApprovalStep plus append-only ApprovalDecision. Same-contract/tenant constraints prevent mismatched approval references. OPEN agency chains/default separation of duties: legal then owner; requester cannot approve own request. decide(ctx,stepId,decision,comment,expectedRevision) locks the current round, checks current authorized actor/order and rejects superseded versions/repeated decisions. Extend create-version.command.ts in this step to atomically close old pending approval rounds and force fresh approval for a new version. Do not infer role hierarchy from enum order. Audit/outbox failures roll back the entire decision. Test ownership in the matching feature file on Files: backend owns `approval_decision_enforces_order_and_separation_of_duties`; backend owns `approval_race_records_one_current_version_decision`; backend owns `approval_audit_failure_rolls_back_business_change`.
**Tests:** `approval_new_version_invalidates_prior_pending_round` · `approval_decision_enforces_order_and_separation_of_duties` · `approval_race_records_one_current_version_decision` · `approval_audit_failure_rolls_back_business_change`
**Verify:** `(cd backend && just test-e2e -- test/contracts/approvals.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Only the authorized current-step approver records one immutable decision for the current version and round.

### 1.4.10 — Draft editor, version history and approval actions
**Repo:** frontend · **Size:** L · **Depends on:** `1.4.9`, `1.3.5` · **Requirements:** PRD-CT-001, PRD-CT-003, SR-CT-006, SR-CT-007, UX-002, UX-003, UX-006
**Files:** `frontend/src/features/contracts/draft-editor.tsx`, `frontend/src/features/contracts/version-history.tsx`, `frontend/src/features/contracts/approval-actions.tsx`, `frontend/app/[locale]/contracts/new/page.tsx`, `frontend/tests/contracts/review-ui.spec.ts`
**Build:** Build draft editor, immutable version upload/change note, safe metadata comparison and ordered approval actions. Display current version/round and invalidate cached actions after a newer version arrives. Confirm rejection, preserve permitted form fields after error and require reload for 412 conflicts. Show only server-allowed transitions; never construct arbitrary status PATCH requests. Reuse localized document widgets. Test ownership in the matching feature file on Files: frontend owns `contract_approval_ui_refuses_superseded_version`; frontend owns `contract_version_history_preserves_change_notes`.
**Tests:** `contract_approval_ui_refuses_superseded_version` · `contract_version_history_preserves_change_notes`
**Verify:** `(cd frontend && npx --no-install playwright test tests/contracts/review-ui.spec.ts)`
**Done when:** Staff draft, version and approve in ar/en while stale approvals fail visibly and prior change notes remain readable.

## Group 1.5 — Legal tickets

### 1.5.1 — Ticket schema and state machine
**Repo:** backend · **Size:** L · **Depends on:** `1.2.1` · **Requirements:** SR-LE-001, SR-LE-002, SR-LE-003, SR-LE-004, SR-LE-007, BR-OBJ-02
**Files:** `backend/src/modules/legal/domain/ticket-state-machine.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_legal_ticket_workflow/migration.sql`, `backend/test/legal/ticket-schema.integration-spec.ts`
**Build:** Ticket stores same-tenant player, requester, active legal assignee, priority, revision, due instant and policy version. Pure transitions OPEN→IN_PROGRESS→PENDING_REVIEW→RESOLVED→CLOSED plus explicit reopen(reason) enumerate all permitted edges. Assignment requires active authorized legal membership, not merely a matching UUID. Internal text defaults confidential. Approved threat model/key custody must cover legal narratives before production; storage encryption alone is not silently declared adequate. Test ownership in the matching feature file on Files: backend owns `legal_ticket_state_machine_refuses_invalid_edges`; backend owns `legal_ticket_assignee_must_be_active_same_tenant_legal_user`.
**Tests:** `legal_ticket_state_machine_refuses_invalid_edges` · `legal_ticket_assignee_must_be_active_same_tenant_legal_user`
**Verify:** `(cd backend && just test-int -- test/legal/ticket-schema.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** The database and domain reject invalid assignees and state transitions while preserving a versioned ticket history.

### 1.5.2 — SLA and overdue monitoring
**Repo:** backend · **Size:** L · **Depends on:** `1.5.5`, `1.6.1` · **Requirements:** SR-LE-009, SR-LE-004, PRD-LE-001, UX-007, BR-RULE-10
**Files:** `backend/src/modules/legal/domain/sla-calendar.ts`, `backend/src/workers/legal/overdue.handler.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_legal_sla_policy/migration.sql`, `backend/test/legal/sla.integration-spec.ts`
**Build:** SlaPolicy stores priority→duration, calendar, timezone, version and any pause rules. OPEN agency hours/holidays/escalation: provisional elapsed-time targets 240/120/48/24 hours for low/medium/high/urgent, clearly labeled provisional; do not invent business-day calendars. Persist dueAt and applied policy so policy changes do not silently rewrite cases. Worker reevaluates current status/deadline and creates deduplicated safe notifications; no automatic reopening or legal outcome. Test ownership in the matching feature file on Files: backend owns `legal_sla_preserves_applied_policy_and_due_instant`; backend owns `legal_overdue_retry_never_reopens_closed_ticket`.
**Tests:** `legal_sla_preserves_applied_policy_and_due_instant` · `legal_overdue_retry_never_reopens_closed_ticket`
**Verify:** `(cd backend && just test-int -- test/legal/sla.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** A fixed-clock SLA breach produces one durable advisory event without rewriting policy history or closed-ticket state.

### 1.5.3 — Notes, internal notes and attachments
**Repo:** backend · **Size:** L · **Depends on:** `1.5.5`, `1.3.1` · **Requirements:** SR-LE-005, SR-LE-006, SR-LE-008, SR-MED-007, BR-RULE-02
**Files:** `backend/src/modules/legal/application/notes.service.ts`, `backend/src/modules/legal/presentation/notes.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_legal_note_bindings/migration.sql`, `backend/test/legal/notes.e2e-spec.ts`
**Build:** LegalNote has immutable author/time, content classification and explicit ticket relation. Creating legal internal notes defaults confidential; releasing a note requires a separate authorized reviewed command. Counts/snippets/search/activity for requesters exclude inaccessible notes. Attachments use typed same-tenant bindings and inherit note/ticket policy; download authorizes at request time. Internal bodies never enter notifications, generic logs or ordinary exports. Test ownership in the matching feature file on Files: backend owns `legal_internal_notes_are_absent_from_requester_counts`; backend owns `legal_attachment_inherits_current_note_policy`.
**Tests:** `legal_internal_notes_are_absent_from_requester_counts` · `legal_attachment_inherits_current_note_policy`
**Verify:** `(cd backend && just test-e2e -- test/legal/notes.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Requesters cannot discover internal notes or download their attachments while authorized legal users can.

### 1.5.4 — The legal queue and requester journey
**Repo:** frontend · **Size:** L · **Depends on:** `1.5.2`, `1.5.3`, `1.3.5` · **Requirements:** PRD-LE-001, UX-002, UX-003, UX-004, UX-005, UX-009, TEST-005
**Files:** `frontend/src/features/legal/legal-queue.tsx`, `frontend/src/features/legal/ticket-page.tsx`, `frontend/app/[locale]/legal/page.tsx`, `frontend/app/[locale]/legal/[id]/page.tsx`, `frontend/tests/legal/workspace.spec.ts`
**Build:** Queues filter by permitted status/priority/assignee/due time. Build creation from player, assignment, transition actions, typed attachments and safe note timeline. Internal-note composer visibly states confidential audience; requester receives only approved projection with no hidden-note badge. Confirm closure/reopen/rejection and show 412 conflicts without overwriting. Dates expose tenant timezone and exact instant on demand. Test ownership in the matching feature file on Files: frontend owns `legal_requester_finishes_case_without_internal_note_leak`; frontend owns `legal_queue_handles_conflict_and_overdue_in_both_locales`.
**Tests:** `legal_requester_finishes_case_without_internal_note_leak` · `legal_queue_handles_conflict_and_overdue_in_both_locales`
**Verify:** `(cd frontend && npx --no-install playwright test tests/legal/workspace.spec.ts)`
**Done when:** Requester and legal assignee complete the case journey in ar/en with controlled actions and correctly different projections.

### 1.5.5 — Ticket commands and assignment API
**Repo:** backend · **Size:** L · **Depends on:** `1.5.1` · **Requirements:** SR-LE-001, SR-LE-004, SR-LE-007, SR-API-005
**Files:** `backend/src/modules/legal/application/create-ticket.command.ts`, `backend/src/modules/legal/application/transition-ticket.command.ts`, `backend/src/modules/legal/application/assign-ticket.command.ts`, `backend/src/modules/legal/presentation/tickets.controller.ts`, `backend/test/legal/commands.e2e-spec.ts`
**Build:** Expose POST/GET /api/v1/legal-tickets and named assign/priority/due-date/transition commands. Each uses tenant context, object policy, If-Match, audit and outbox in one transaction. Query projections distinguish requester and legal staff before pagination. Assignment rechecks active legal membership under transaction; unauthorized reads are not-found. A failed audit leaves no assignment/status/priority change. Test ownership in the matching feature file on Files: backend owns `legal_concurrent_assignment_returns_revision_conflict`; backend owns `legal_audit_failure_rolls_back_ticket_mutation`.
**Tests:** `legal_concurrent_assignment_returns_revision_conflict` · `legal_audit_failure_rolls_back_ticket_mutation`
**Verify:** `(cd backend && just test-e2e -- test/legal/commands.e2e-spec.ts)`
**Done when:** Ticket commands enforce current authorization and concurrency and cannot commit without their audit evidence.

## Group 1.6 — Notifications

### 1.6.1 — Templated, localized, tracked notifications
**Repo:** backend · **Size:** L · **Depends on:** `0.11.1` · **Requirements:** BR-OBJ-06, PRD-NF-001, SR-NF-001, SR-NF-005, SR-NF-006, SYS-ASY-001, BR-RULE-10
**Files:** `backend/src/modules/notifications/application/notify.service.ts`, `backend/src/workers/notifications/notification.handler.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_notification_delivery/migration.sql`, `backend/test/notifications/delivery.integration-spec.ts`
**Build:** notify(tx,recipientIds,templateKey,safeParams,sourceRef) writes durable intent; worker uses existing outbox/inbox. Notification has template key/parameters, locale policy and unique recipient/event key; NotificationDelivery distinguishes queued, provider-accepted, delivered-if-confirmed, failed, retry and uncertain. Do not equate SMTP acceptance with inbox delivery or promise exactly once. Render per recipient locale from allowlisted safe references, not confidential contract/legal/medical values. Recheck recipient membership/policy before dispatch; business state remains authoritative. Test ownership in the matching feature file on Files: backend owns `notification_rendering_is_localized_and_confidentiality_safe`; backend owns `notification_redelivery_preserves_one_in_app_record`.
**Tests:** `notification_rendering_is_localized_and_confidentiality_safe` · `notification_redelivery_preserves_one_in_app_record`
**Verify:** `(cd backend && just test-int -- test/notifications/delivery.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** Events create one safe localized in-app notification per recipient and honestly tracked external delivery attempts.

### 1.6.2 — The notification center
**Repo:** backend + frontend · **Size:** L · **Depends on:** `1.6.1` · **Requirements:** PRD-NF-001, SR-NF-007, UX-010, UX-011
**Files:** `backend/src/modules/notifications/presentation/notifications.controller.ts`, `frontend/src/features/notifications/notification-center.tsx`, `frontend/app/[locale]/notifications/page.tsx`, `backend/test/notifications/center.e2e-spec.ts`, `frontend/tests/notifications/center.spec.ts`
**Build:** Provide cursor list/unread count/idempotent mark-read endpoints and a bell/center with bounded polling. Deep-link routes reauthorize current membership/object access; expired/deleted/forbidden links show safe not-found with no confidential preview. Persist read state in PostgreSQL and keep separate tabs/users consistent without trusting client ids. Realtime transport remains later work. Test ownership in the matching feature file on Files: backend owns `notification_mark_read_is_recipient_scoped_and_idempotent`; frontend owns `notification_deep_link_rechecks_current_authorization`.
**Tests:** `notification_mark_read_is_recipient_scoped_and_idempotent` · `notification_deep_link_rechecks_current_authorization`
**Verify:** `(cd backend && just test-e2e -- test/notifications/center.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/notifications/center.spec.ts)`
**Done when:** Users read actionable notifications and safely handle revoked or expired destinations in both locales.

### 1.6.3 — Production email provider and preferences
**Repo:** backend · **Size:** L · **Depends on:** `1.6.1`, `1.10.1` · **Requirements:** SR-NF-003, SR-NF-004, SR-NF-005
**Files:** `backend/src/infrastructure/mail/production-mail.adapter.ts`, `backend/src/modules/notifications/application/preferences.service.ts`, `backend/src/modules/notifications/presentation/preferences.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_notification_preferences/migration.sql`, `backend/test/notifications/provider-preferences.integration-spec.ts`
**Build:** OPEN provider/account/domain approval must be settled for production; retain Mailpit in development only. Implement approved provider behind existing mail port and record accepted/uncertain responses; bounded retries with dedupe/reconciliation where provider supports it. Verify sending-domain records through provider-supported checks. Per-type/channel preferences are constrained by mandatory security notices. Provider credentials come from the selected secret store, never logs or frontend configuration. Test ownership in the matching feature file on Files: backend owns `mandatory_security_notification_ignores_optional_opt_out`; backend owns `mail_provider_uncertain_acceptance_is_recorded_honestly`.
**Tests:** `mandatory_security_notification_ignores_optional_opt_out` · `mail_provider_uncertain_acceptance_is_recorded_honestly`
**Verify:** `(cd backend && just test-int -- test/notifications/provider-preferences.integration-spec.ts) && (cd backend && just migrations)`
**Done when:** The approved provider accepts a synthetic localized message and preferences cannot suppress mandatory security notices.

### 1.6.4 — Notification preference controls
**Repo:** frontend · **Size:** M · **Depends on:** `1.6.3` · **Requirements:** SR-NF-004, PRD-NF-001, UX-003
**Files:** `frontend/src/features/notifications/preference-form.tsx`, `frontend/app/[locale]/settings/notifications/page.tsx`, `frontend/tests/notifications/preferences.spec.ts`
**Build:** Render supported type/channel choices and explain mandatory security notices. Unsupported push settings remain absent until the approved Phase-2 provider ships. Save with revision and accessible success/failure feedback; on conflict refetch instead of overwriting another session's choice. Locale-specific previews use synthetic safe content. Test ownership in the matching feature file on Files: frontend owns `notification_preferences_explain_mandatory_security_delivery`.
**Tests:** `notification_preferences_explain_mandatory_security_delivery`
**Verify:** `(cd frontend && npx --no-install playwright test tests/notifications/preferences.spec.ts)`
**Done when:** Users save allowed preferences in ar/en and understand which security notifications remain mandatory.

## Group 1.7 — Audit and activity

### 1.7.1 — Restricted audit search API
**Repo:** backend · **Size:** M · **Depends on:** `0.11.1` · **Requirements:** SR-AUD-006, SR-AUD-004, PRD-AD-001
**Files:** `backend/src/modules/audit/application/search-audit.query.ts`, `backend/src/modules/audit/presentation/audit.controller.ts`, `backend/test/audit/search.e2e-spec.ts`
**Build:** GET /api/v1/audit requires explicit audit.read, not broad admin ownership. Allowlist actor/entity/action/date filters with bounded cursor pagination and tenant scope before counting. Authorized results remain redacted; permission to inspect audit never decrypts source compensation or legal narratives. Audit the search/access and prohibit update/delete endpoints. Index query shapes and test runtime-role permissions. Test ownership: backend `backend/test/audit/search.e2e-spec.ts` owns `audit_search_requires_explicit_permission_and_tenant_scope`, `audit_search_never_exposes_confidential_before_after`.
**Tests:** `audit_search_requires_explicit_permission_and_tenant_scope` · `audit_search_never_exposes_confidential_before_after`
**Verify:** `(cd backend && just test-e2e -- test/audit/search.e2e-spec.ts)`
**Done when:** An authorized auditor searches bounded tenant evidence without receiving confidential values or any mutation capability.

### 1.7.2 — The permission-filtered player timeline
**Repo:** backend · **Size:** L · **Depends on:** `1.7.1`, `1.4.3`, `1.5.3` · **Requirements:** SR-PL-008, PRD-PL-001, BR-OBJ-01, SR-MED-007
**Files:** `backend/src/modules/players/application/player-timeline.query.ts`, `backend/src/modules/contracts/application/contract-summary.query.ts`, `backend/src/modules/legal/application/legal-summary.query.ts`, `backend/test/players/timeline.e2e-spec.ts`
**Build:** Query authorized domain summary interfaces and safe audit events for a player; modules own their tables. Filter before cursor counts, do not expose raw audit blobs. Contract access/compensation, legal internal events and unreleased medical events require their policies; an inaccessible event is absent rather than labeled hidden. Preserve stable time/id ordering and timezone display metadata. Summary failure returns an explicit partial-panel outcome, not invented totals. Test ownership: backend `backend/test/players/timeline.e2e-spec.ts` owns `player_timeline_omits_unauthorized_events_and_counts`, `player_timeline_queries_modules_through_application_ports`.
**Tests:** `player_timeline_omits_unauthorized_events_and_counts` · `player_timeline_queries_modules_through_application_ports`
**Verify:** `(cd backend && just test-e2e -- test/players/timeline.e2e-spec.ts)`
**Done when:** The same player's timeline exposes only events the current reader may know, with stable pagination and no confidential counts.

### 1.7.3 — Audit investigation workspace
**Repo:** frontend · **Size:** M · **Depends on:** `1.7.1` · **Requirements:** PRD-AD-001, SR-AUD-006, UX-004, UX-007
**Files:** `frontend/src/features/audit/audit-search.tsx`, `frontend/app/[locale]/settings/audit/page.tsx`, `frontend/tests/audit/workspace.spec.ts`
**Build:** Build actor/entity/action/date filters, cursor table and redacted event detail with correlation id. Dates show tenant rendering plus exact UTC on demand. No edit/delete controls or generic raw JSON viewer; copy only safe evidence references. Explain denied/no-results/error states and preserve filters across paging. Test ownership: frontend `frontend/tests/audit/workspace.spec.ts` owns `audit_workspace_is_read_only_and_accessible`.
**Tests:** `audit_workspace_is_read_only_and_accessible`
**Verify:** `(cd frontend && npx --no-install playwright test tests/audit/workspace.spec.ts)`
**Done when:** An auditor traces a workflow through safe immutable evidence in both locales using keyboard-accessible filters.

## Group 1.8 — Search and dashboards

### 1.8.1 — Authorized global search API
**Repo:** backend · **Size:** L · **Depends on:** `1.2.4`, `1.3.1`, `1.4.3`, `1.5.5` · **Requirements:** BR-OBJ-01, PRD-PL-001, SR-MED-007, SR-ACL-008, SYS-TEN-006
**Files:** `backend/src/modules/search/application/search.query.ts`, `backend/src/modules/search/presentation/search.controller.ts`, `backend/prisma/migrations/<timestamp>_authorized_search_indexes/migration.sql`, `backend/test/search/global.e2e-spec.ts`
**Build:** Use PostgreSQL text/trigram indexes and the explicit Arabic normalization policy for permitted player names, contract references, safe ticket titles and document names. Search each domain through policy-bearing query ports; filter before rank/page/count. No confidential full-text index for ordinary search; never index medical narratives, internal notes, passport values or compensation. An authorization change takes effect immediately, including query caches. Bound query length, result size and execution budget. Test ownership: backend `backend/test/search/global.e2e-spec.ts` owns `global_search_excludes_forbidden_hits_and_counts`, `global_search_permission_change_invalidates_cached_projection`.
**Tests:** `global_search_excludes_forbidden_hits_and_counts` · `global_search_permission_change_invalidates_cached_projection`
**Verify:** `(cd backend && just test-e2e -- test/search/global.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** Search results, snippets and counts expose only resources the current caller may open.

### 1.8.2 — The home dashboard
**Repo:** backend + frontend · **Size:** L · **Depends on:** `1.4.4`, `1.5.2`, `1.2.5` · **Requirements:** PRD-CT-002, BR-OBJ-02, UX-001, UX-010, UX-011
**Files:** `backend/src/modules/dashboard/application/home-dashboard.query.ts`, `frontend/src/features/dashboard/home-dashboard.tsx`, `frontend/app/[locale]/page.tsx`, `backend/test/dashboard/home.e2e-spec.ts`, `frontend/tests/dashboard/home.spec.ts`
**Build:** Return authorized actions: approvals awaiting this actor, expiring contracts, assigned overdue cases and permitted incomplete-profile tasks. Derive from authoritative workflow queries, not notification delivery or a new generic task system. Show per-panel loading/error/empty states; deep links reauthorize. Use tenant civil-date cutoffs for expiry bands, bounded cache keyed by membership/projection revision and query indexes. Performance evidence is produced by 1.10.6, not claimed from component tests. Test ownership: backend `backend/test/dashboard/home.e2e-spec.ts` owns `home_dashboard_derives_tasks_from_authorized_workflows`; frontend `frontend/tests/dashboard/home.spec.ts` owns `home_dashboard_handles_partial_failure_without_false_counts`.
**Tests:** `home_dashboard_derives_tasks_from_authorized_workflows` · `home_dashboard_handles_partial_failure_without_false_counts`
**Verify:** `(cd backend && just test-e2e -- test/dashboard/home.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/dashboard/home.spec.ts)`
**Done when:** The home page lists only current authorized actions and makes failed/empty panels explicit in both locales.

### 1.8.3 — The executive summary
**Repo:** backend + frontend · **Size:** L · **Depends on:** `1.8.2` · **Requirements:** BR-OBJ-01, BR-OBJ-02, PRD-AD-001, UX-004
**Files:** `backend/src/modules/dashboard/application/executive-summary.query.ts`, `frontend/src/features/dashboard/executive-summary.tsx`, `frontend/app/[locale]/reports/overview/page.tsx`, `backend/test/dashboard/executive.e2e-spec.ts`, `frontend/tests/dashboard/executive.spec.ts`
**Build:** Show portfolio counts, expiry bands, legal SLA compliance and profile completeness under explicit summary permissions. Every aggregate links to the same policy-filtered source query; do not infer permission for legal metrics from a general executive role. Define denominators/time window and provisional-policy labels; zero/unknown are distinct. Avoid identifying individuals through restricted small groups by omitting unauthorized dimensions entirely. Test ownership: backend `backend/test/dashboard/executive.e2e-spec.ts` owns `executive_aggregate_matches_authorized_source_records`; frontend `frontend/tests/dashboard/executive.spec.ts` owns `executive_summary_discloses_window_and_denominator`.
**Tests:** `executive_aggregate_matches_authorized_source_records` · `executive_summary_discloses_window_and_denominator`
**Verify:** `(cd backend && just test-e2e -- test/dashboard/executive.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/dashboard/executive.spec.ts)`
**Done when:** Every displayed figure reconciles to its authorized records with an explicit window and denominator.

### 1.8.4 — Global search interaction
**Repo:** frontend · **Size:** M · **Depends on:** `1.8.1` · **Requirements:** UX-003, UX-004, UX-009, UX-011
**Files:** `frontend/src/features/search/global-search.tsx`, `frontend/app/[locale]/search/page.tsx`, `frontend/tests/search/workspace.spec.ts`
**Build:** Add debounced keyboard-accessible search, result categories, bounded paging and cancellation of obsolete requests. Never show stale tenant results after membership switch/logout. Display no raw search content in telemetry; use safe query-length/result metrics. Result links recheck authorization and denied responses reveal no title/snippet. Test ownership: frontend `frontend/tests/search/workspace.spec.ts` owns `global_search_clears_stale_tenant_results`, `global_search_supports_arabic_keyboard_navigation`.
**Tests:** `global_search_clears_stale_tenant_results` · `global_search_supports_arabic_keyboard_navigation`
**Verify:** `(cd frontend && npx --no-install playwright test tests/search/workspace.spec.ts)`
**Done when:** Users search in either locale without stale cross-tenant results or inaccessible snippets.

## Group 1.9 — Exports

### 1.9.1 — Permission-gated, audited export jobs
**Repo:** backend · **Size:** L · **Depends on:** `1.2.4`, `1.4.3`, `1.5.5`, `1.3.4` · **Requirements:** SR-ACL-009, SR-API-006, SYS-ASY-001, SYS-TEN-006, BR-OBJ-02
**Files:** `backend/src/modules/exports/application/request-export.command.ts`, `backend/src/workers/exports/export.handler.ts`, `backend/src/modules/exports/presentation/exports.controller.ts`, `backend/prisma/schema.prisma`, `backend/prisma/migrations/<timestamp>_export_jobs/migration.sql`, `backend/test/exports/jobs.e2e-spec.ts`
**Build:** ExportJob stores tenant/requester/filter/projection revision/state and expiresAt, with outbox/inbox-backed processing. Require domain export permission and object policy at request, worker execution and download. Default excludes confidential columns; explicit field permission plus approved export purpose is required for inclusion. Stream authorized rows without loading all records; neutralize spreadsheet formula prefixes in CSV, quote multiline cells and write private clean FileObject with short retention. Recheck revocation before publishing; audit filters/row counts but no raw confidential cells. Replayed jobs produce one output reference. Test ownership: backend `backend/test/exports/jobs.e2e-spec.ts` owns `export_job_rechecks_permission_before_download`, `export_csv_neutralizes_formulas_and_excludes_confidential_fields`, `export_retry_has_one_audited_output_reference`.
**Tests:** `export_job_rechecks_permission_before_download` · `export_csv_neutralizes_formulas_and_excludes_confidential_fields` · `export_retry_has_one_audited_output_reference`
**Verify:** `(cd backend && just test-e2e -- test/exports/jobs.e2e-spec.ts) && (cd backend && just migrations)`
**Done when:** An export produces one private audited artifact containing only currently authorized rows/columns and safe CSV cells.

### 1.9.2 — Export progress and download interface
**Repo:** frontend · **Size:** M · **Depends on:** `1.9.1` · **Requirements:** SR-ACL-009, UX-004, UX-010, UX-011
**Files:** `frontend/src/features/exports/export-dialog.tsx`, `frontend/src/features/exports/export-status.tsx`, `frontend/app/[locale]/exports/page.tsx`, `frontend/tests/exports/workspace.spec.ts`
**Build:** Reuse current list filters to request an export; state exactly which safe projection is included. Show queued/running/failed/expired/revoked states, row count and download expiry. Refresh a download through current authorization, never retain presigned links. No synchronous browser CSV export bypassing the job API. Retry uses idempotency and provides safe error detail. Test ownership: frontend `frontend/tests/exports/workspace.spec.ts` owns `export_workspace_handles_expiry_revocation_and_retry`.
**Tests:** `export_workspace_handles_expiry_revocation_and_retry`
**Verify:** `(cd frontend && npx --no-install playwright test tests/exports/workspace.spec.ts)`
**Done when:** Users request and retrieve authorized exports asynchronously and cannot download an expired or revoked artifact.

## Group 1.10 — Production readiness and launch

### 1.10.1 — Hosting, provider operation and residency decision
**Repo:** umbrella · **Size:** M · **Depends on:** `0.11.1` · **Requirements:** BR-OBJ-09, SR-NFR-REL-001, SR-NFR-SEC-002
**Files:** `docs/decisions/hosting.md`, `infra/environments/staging.yaml`, `infra/environments/production.yaml`, `scripts/hosting-preflight.py`, `scripts/tests/test_ops_hosting.py`
**Build:** OPEN owner-approved provider/region/residency and Keycloak production operator block production. Compare supported PostgreSQL18/PITR, private versioned S3, Valkey, TLS container hosting, key custody, backup isolation and incident ownership; do not choose a jurisdiction from inference. Record exact service versions/digests, costs and rollback/support responsibilities. Keycloak production uses TLS and restricted admin, never start-dev. Implement hosting-preflight.py to validate approved decisions and environment completeness; unit fixtures fail unknown residency/operator/approval. No real data until privacy decisions permit it. Test ownership: umbrella `scripts/tests/test_ops_hosting.py` owns `test_hosting_preflight_rejects_unapproved_residency_or_operator`.
**Tests:** `test_hosting_preflight_rejects_unapproved_residency_or_operator`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_hosting.py' && python3 scripts/hosting-preflight.py --decision docs/decisions/hosting.md --check-approval`
**Done when:** The owner approves a complete hosting/provider-operation decision and preflight rejects any incomplete production environment.

### 1.10.2 — Reproducible application images
**Repo:** umbrella + backend + frontend · **Size:** L · **Depends on:** `1.10.1` · **Requirements:** SR-NFR-MNT-002, SYS-ARC-005
**Files:** `infra/images.yaml`, `scripts/build-images.py`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/scripts/image-smoke.sh`, `frontend/scripts/image-smoke.sh`, `scripts/tests/test_ops_images.py`, `backend/test/ops/images.e2e-spec.ts`, `frontend/tests/ops/images.spec.ts`
**Build:** Build API/worker and web from pinned app SHAs with exact non-root base digests, lockfile installs, SBOM and immutable image digests. A realtime image is not deployed before its Phase-2 implementation. Separate worker entrypoint and runtime least-privilege credentials; no database migration at container startup. build-images.py validates pin provenance, builds images and invokes app smoke scripts to probe health/static routing and assert no baked secrets. The public origin maps /api to Nest and other paths to Next; browser has no provider tokens. Test ownership: umbrella `scripts/tests/test_ops_images.py` owns `test_image_build_manifest_matches_pinned_app_commits`; backend `backend/test/ops/images.e2e-spec.ts` owns `api_image_starts_with_nonowner_runtime_role`; frontend `frontend/tests/ops/images.spec.ts` owns `web_image_serves_localized_same_origin_routes`.
**Tests:** `test_image_build_manifest_matches_pinned_app_commits` · `api_image_starts_with_nonowner_runtime_role` · `web_image_serves_localized_same_origin_routes`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_images.py' && python3 scripts/build-images.py --environment staging --pins-from-gitlinks --smoke && (cd backend && just test-e2e -- test/ops/images.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/ops/images.spec.ts)`
**Done when:** Images built from the exact pins start as non-root processes with correct routes and no embedded secrets.

### 1.10.3 — Production secrets and configuration lifecycle
**Repo:** umbrella + backend · **Size:** L · **Depends on:** `1.10.11` · **Requirements:** SR-DB-010, SR-CORE-009, SR-NFR-SEC-002
**Files:** `infra/secrets/README.md`, `scripts/rotate-runtime-secrets.py`, `docs/runbooks/secret-rotation.md`, `backend/src/config/production-config.ts`, `scripts/tests/test_ops_secrets.py`, `backend/test/ops/secrets.e2e-spec.ts`
**Build:** Use the approved secret store for database, mail, storage and OIDC confidential-client credentials. Persist only derived OIDC identity/assurance fields in application sessions, never provider access/refresh tokens; no session token vault. Version any field-encryption keys justified by approved threat model. Script supports --check and staged --rehearse on isolated staging: introduce new credential, deploy, revoke old, assert existing permitted application sessions and new login behavior, prove old credential denied. Record recovery custody without secret values. Test ownership: umbrella `scripts/tests/test_ops_secrets.py` owns `test_secret_rotation_refuses_missing_recovery_reference`; backend `backend/test/ops/secrets.e2e-spec.ts` owns `production_config_never_persists_provider_tokens`.
**Tests:** `test_secret_rotation_refuses_missing_recovery_reference` · `production_config_never_persists_provider_tokens`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_secrets.py' && python3 scripts/rotate-runtime-secrets.py --environment staging --rehearse && (cd backend && just test-e2e -- test/ops/secrets.e2e-spec.ts)`
**Done when:** Staging credential rotation/revocation completes with documented recovery and no secret or provider token persisted in application evidence.

### 1.10.4 — OpenTelemetry and bounded operational metrics
**Repo:** backend + frontend + umbrella · **Size:** L · **Depends on:** `1.10.11` · **Requirements:** SR-NFR-OBS-001, SR-NFR-PERF-003, SYS-TEN-007, SR-CORE-008
**Files:** `backend/src/infrastructure/telemetry/otel.ts`, `backend/src/infrastructure/telemetry/metrics.ts`, `frontend/src/instrumentation.ts`, `infra/observability/collector.yaml`, `scripts/telemetry-smoke.py`, `backend/test/ops/telemetry.e2e-spec.ts`, `frontend/tests/ops/telemetry.spec.ts`, `scripts/tests/test_ops_telemetry.py`
**Build:** Instrument web→API→database/outbox→worker using bounded attributes; no bodies, filenames, tokens or confidential user values. Tenant attributes stay in restricted traces/logs; avoid tenant/user labels on unbounded metrics. Measure latency/error rate, DB pool active/wait/timeout, queue age/retries, scan failures and readiness. Configure approved retention/access at collector and any error-tracking provider. telemetry-smoke.py sends a synthetic request and verifies correlated worker trace plus explicit allowlist of emitted fields. Test ownership: backend `backend/test/ops/telemetry.e2e-spec.ts` owns `telemetry_redacts_canaries_and_preserves_job_trace`; frontend `frontend/tests/ops/telemetry.spec.ts` owns `browser_telemetry_omits_sensitive_route_values`; umbrella `scripts/tests/test_ops_telemetry.py` owns `test_telemetry_smoke_rejects_missing_worker_span`.
**Tests:** `telemetry_redacts_canaries_and_preserves_job_trace` · `browser_telemetry_omits_sensitive_route_values` · `test_telemetry_smoke_rejects_missing_worker_span`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_telemetry.py' && (cd backend && just test-e2e -- test/ops/telemetry.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/ops/telemetry.spec.ts) && python3 scripts/telemetry-smoke.py --environment staging`
**Done when:** A synthetic browser request is traceable through its worker while restricted values stay absent and pool pressure is measurable.

### 1.10.5 — Backups, retention and recovery runbook
**Repo:** umbrella · **Size:** L · **Depends on:** `1.10.11`, `1.10.3` · **Requirements:** SR-NFR-REL-002, SR-AUD-007, TEST-008
**Files:** `infra/backups/policy.yaml`, `scripts/backup-verify.py`, `docs/runbooks/disaster-recovery.md`, `scripts/tests/test_ops_backups.py`
**Build:** Configure approved PostgreSQL backups/PITR, object version recovery, Keycloak database/realm/theme backup and key/secret recovery references. Isolate backup writer/reader roles and retention from ordinary runtime deletion. Specify restore order, tenant/audit/file-integrity checks and forward-compatible application pins; no rollback by editing committed migrations. backup-verify.py verifies recent successful artifacts, object-version inventory and required key/config references without reading secrets into logs. A successful backup is not a completed recovery drill; that is 1.10.13. Test ownership: umbrella `scripts/tests/test_ops_backups.py` owns `test_backup_verification_refuses_missing_object_or_identity_backup`.
**Tests:** `test_backup_verification_refuses_missing_object_or_identity_backup`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_backups.py' && python3 scripts/backup-verify.py --environment staging --require-recent`
**Done when:** All required data, object, identity and key-reference backups are verifiable under the approved policy and the restore runbook is complete.

### 1.10.6 — Load test at the declared capacity envelope
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `1.10.4`, `1.2.7`, `1.8.3`, `1.9.2`, `1.6.4` · **Requirements:** SR-NFR-PERF-001, SR-NFR-PERF-002, SR-NFR-PERF-003, TEST-007
**Files:** `backend/test/load/mvp.js`, `backend/test/load/seed-envelope.ts`, `infra/testing/capacity.yaml`, `scripts/run-load.py`, `docs/evidence/phase-1-capacity.md`, `backend/test/ops/load.integration-spec.ts`, `scripts/tests/test_ops_load.py`
**Build:** OPEN agency envelope; provisional test-only default: two tenants, 50 users and 500 players per tenant, 20k document metadata records per tenant, 50 concurrent sessions with 80/20 reads/writes and five concurrent uploads. Record hardware/pool limits, synthetic dataset and exact image/commit digests. Pinned k6 image runs 5-minute warmup+15-minute measurement; simple API p95≤500ms, dashboards≤2s, error rate<1%, no isolation failure; separately report provider latency/upload processing. Fail sustained pool exhaustion/timeouts, report resource saturation. run-load.py checks live thresholds and writes evidence, never reuses a stale report. Test ownership: backend `backend/test/ops/load.integration-spec.ts` owns `load_envelope_fixtures_are_tenant_isolated_and_repeatable`; umbrella `scripts/tests/test_ops_load.py` owns `test_load_report_rejects_failed_or_stale_thresholds`.
**Tests:** `load_envelope_fixtures_are_tenant_isolated_and_repeatable` · `test_load_report_rejects_failed_or_stale_thresholds`
**Verify:** `(cd backend && just test-int -- test/ops/load.integration-spec.ts) && python3 -m unittest discover -s scripts/tests -p 'test_ops_load.py' && python3 scripts/run-load.py --environment staging --scenario backend/test/load/mvp.js --envelope infra/testing/capacity.yaml --output docs/evidence/phase-1-capacity.md`
**Done when:** A current measured staging report meets API budgets and records pool, upload and worker behavior at the declared envelope.

### 1.10.7 — Security scanning and evidence collection
**Repo:** umbrella + backend · **Size:** L · **Depends on:** `1.10.11`, `1.10.3` · **Requirements:** SR-NFR-SEC-001, TEST-006, SR-NFR-SEC-003
**Files:** `scripts/security-gate.py`, `infra/security/asvs-mapping.md`, `infra/security/zap-baseline.yaml`, `docs/evidence/phase-1-security.md`, `scripts/tests/test_ops_security.py`, `backend/test/ops/security.e2e-spec.ts`
**Build:** Map applicable ASVS 5.0 Level 2 controls and API risk requirements to actual tests/config/manual evidence; justify non-applicable controls and do not claim certification. security-gate.py runs approved pinned DAST against isolated synthetic staging, ingests exact-SHA existing SAST/dependency/secret checks and image scanning, and fails missing/stale reports or open critical/high findings. Confirm scanner scope cannot contact production or third-party endpoints. Include RLS/catalog/runtime-role, provider/session and signed URL replay suites; independent review and incident abuse exercises are 1.10.14. Test ownership: umbrella `scripts/tests/test_ops_security.py` owns `test_security_gate_rejects_stale_or_high_severity_findings`; backend `backend/test/ops/security.e2e-spec.ts` owns `security_regression_covers_every_mvp_route_and_file_path`.
**Tests:** `test_security_gate_rejects_stale_or_high_severity_findings` · `security_regression_covers_every_mvp_route_and_file_path`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_security.py' && (cd backend && just test-e2e -- test/ops/security.e2e-spec.ts) && python3 scripts/security-gate.py --environment staging --pins-from-gitlinks --output docs/evidence/phase-1-security.md`
**Done when:** Current automated security evidence covers the pinned release and contains no unresolved critical/high finding.

### 1.10.8 — Accessibility and responsive browser acceptance
**Repo:** frontend + umbrella · **Size:** L · **Depends on:** `1.2.7`, `1.4.7`, `1.5.4`, `1.6.4`, `1.7.3`, `1.8.4`, `1.9.2`, `1.1.6` · **Requirements:** SR-NFR-A11Y-001, UX-009, UX-012, TEST-009, TEST-005
**Files:** `frontend/tests/accessibility/mvp.spec.ts`, `docs/evidence/phase-1-accessibility.md`, `scripts/check-acceptance-evidence.py`, `frontend/tests/ops/accessibility.spec.ts`, `scripts/tests/test_ops_accessibility.py`
**Build:** Run axe and real keyboard flows on every MVP page in ar/en at 360/768/1440 widths; check zoom, focus/error recovery and file widgets. Manually test one supported screen reader/browser pair with named reviewer/version. Keycloak pages are included. Automated tooling cannot certify WCAG; record manual criteria, defects and resolutions. check-acceptance-evidence.py rejects missing pages/locales/viewports, unresolved blocker/serious findings and unsigned manual review. Test ownership: frontend `frontend/tests/ops/accessibility.spec.ts` owns `mvp_pages_pass_keyboard_axe_and_responsive_checks`; umbrella `scripts/tests/test_ops_accessibility.py` owns `test_accessibility_evidence_requires_manual_screen_reader_review`.
**Tests:** `mvp_pages_pass_keyboard_axe_and_responsive_checks` · `test_accessibility_evidence_requires_manual_screen_reader_review`
**Verify:** `(cd frontend && npx --no-install playwright test tests/ops/accessibility.spec.ts tests/accessibility/mvp.spec.ts) && python3 -m unittest discover -s scripts/tests -p 'test_ops_accessibility.py' && python3 scripts/check-acceptance-evidence.py --kind accessibility --file docs/evidence/phase-1-accessibility.md`
**Done when:** All MVP pages have passing automated coverage and resolved manual keyboard/screen-reader acceptance evidence.

### 1.10.9 — Accept, promote and launch
**Repo:** umbrella + backend + frontend · **Size:** M · **Depends on:** `1.1.1`, `1.1.2`, `1.1.3`, `1.1.4`, `1.1.5`, `1.1.6`, `1.1.7`, `1.1.8`, `1.2.1`, `1.2.2`, `1.2.3`, `1.2.4`, `1.2.5`, `1.2.6`, `1.2.7`, `1.2.8`, `1.3.1`, `1.3.2`, `1.3.3`, `1.3.4`, `1.3.5`, `1.4.1`, `1.4.2`, `1.4.3`, `1.4.4`, `1.4.5`, `1.4.6`, `1.4.7`, `1.4.8`, `1.4.9`, `1.4.10`, `1.5.1`, `1.5.2`, `1.5.3`, `1.5.4`, `1.5.5`, `1.6.1`, `1.6.2`, `1.6.3`, `1.6.4`, `1.7.1`, `1.7.2`, `1.7.3`, `1.8.1`, `1.8.2`, `1.8.3`, `1.8.4`, `1.9.1`, `1.9.2`, `1.10.1`, `1.10.2`, `1.10.3`, `1.10.4`, `1.10.5`, `1.10.6`, `1.10.7`, `1.10.8`, `1.10.10`, `1.10.11`, `1.10.12`, `1.10.13`, `1.10.14`, `1.10.15` · **Requirements:** BR-OBJ-01, BR-OBJ-02, BR-OBJ-05, BR-OBJ-06, BR-OBJ-09, PRD-PL-001, PRD-CT-001, PRD-LE-001, TEST-005
**Files:** `scripts/release-evidence.py`, `docs/evidence/phase-1-release.md`, `docs/runbooks/first-tenant-launch.md`, `backend/test/release/mvp.e2e-spec.ts`, `frontend/tests/release/mvp.spec.ts`, `scripts/tests/test_release_mvp.py`
**Build:** Run the phase gate below against exact pins, link all acceptance reports and resolve release-blocking OPEN items: hosting/operator, approved signature evidence policy, privacy/retention duties, permission matrix and staffed operations. Record owner/domain sign-off. Rehearse on staging with agency users and approved synthetic data; record soak duration/failures. Use the existing app-first then umbrella pin/promotion flow, merge commits for promotions and approved signed release tags; never substitute deployments for required checks. release-evidence.py validates report SHAs/actual executed counts and live health after deployment; a PR link alone cannot prove acceptance. No production SIGNED or launch-complete claim while counsel approval is missing. Test ownership: backend `backend/test/release/mvp.e2e-spec.ts` owns `mvp_acceptance_enforces_negative_business_paths`; frontend `frontend/tests/release/mvp.spec.ts` owns `mvp_staff_journeys_complete_in_both_locales`; umbrella `scripts/tests/test_release_mvp.py` owns `test_release_evidence_rejects_unapproved_or_mismatched_pins`.
**Tests:** `mvp_acceptance_enforces_negative_business_paths` · `mvp_staff_journeys_complete_in_both_locales` · `test_release_evidence_rejects_unapproved_or_mismatched_pins`
**Verify:** `(cd backend && just test-e2e -- test/release/mvp.e2e-spec.ts) && (cd frontend && npx --no-install playwright test tests/release/mvp.spec.ts) && python3 -m unittest discover -s scripts/tests -p 'test_release_mvp.py' && python3 scripts/release-evidence.py --phase 1 --file docs/evidence/phase-1-release.md --pins-from-gitlinks --verify-live`
**Done when:** Owner-approved production pins serve the first authorized agency users after every release gate and required OPEN decision is evidenced.

### 1.10.10 — Enforce module and process boundaries
**Repo:** backend + frontend · **Size:** L · **Depends on:** `0.11.1` · **Requirements:** SYS-ARC-001, SYS-ARC-002, SYS-ARC-004, SR-NFR-MNT-001
**Files:** `backend/dependency-cruiser.config.cjs`, `backend/eslint.config.mjs`, `backend/package.json`, `backend/justfile`, `frontend/eslint.config.mjs`, `frontend/justfile`, `backend/src/architecture/boundaries.spec.ts`, `frontend/src/architecture/boundaries.test.ts`
**Build:** Install an exact pinned dependency-boundary analyzer and wire it into existing check/CI test jobs. Domain imports no Nest/Prisma/I/O; cross-module consumers may import only public application interfaces, never another module's repository/tables. The composition root may wire adapters explicitly. Enforce frontend feature/public API boundaries and prevent server-only modules in browser bundles. Add deliberately invalid fixture imports proving failure. A new service/process needs an ADR with measured requirement; do not split the monolith by module count. Test ownership: backend `backend/src/architecture/boundaries.spec.ts` owns `module_boundary_gate_rejects_repository_and_framework_leaks`; frontend `frontend/src/architecture/boundaries.test.ts` owns `browser_boundary_gate_rejects_server_only_imports`.
**Tests:** `module_boundary_gate_rejects_repository_and_framework_leaks` · `browser_boundary_gate_rejects_server_only_imports`
**Verify:** `(cd backend && npx --no-install jest --selectProjects unit --runInBand --runTestsByPath src/architecture/boundaries.spec.ts && just check) && (cd frontend && npx --no-install vitest run src/architecture/boundaries.test.ts && just check)`
**Done when:** CI refuses forbidden module/browser imports and the modular monolith remains the implemented default architecture.

### 1.10.11 — Staging deployment and forward migration orchestration
**Repo:** umbrella · **Size:** L · **Depends on:** `1.10.2` · **Requirements:** SR-NFR-MNT-002, SR-DB-005, SR-NFR-REL-001
**Files:** `scripts/deploy.py`, `scripts/release-preflight.py`, `infra/deployment/staging.yaml`, `infra/deployment/production.yaml`, `docs/runbooks/deployment.md`, `scripts/tests/test_ops_deployment.py`
**Build:** Deploy immutable reviewed images through the selected hosting adapter. release-preflight.py checks exact app/umbrella SHAs, approved configuration, migration compatibility and recent backups. deploy.py deploys to an explicit environment, uses the migrator role in a one-off release job, then rolls app/worker images and verifies readiness/same-origin routing/TLS. Staging never uses Keycloak start-dev. Exercise failed readiness: keep prior compatible app image; repair DB forward, never edit/delete migrations. Scripts require explicit production environment and approval evidence; default staging. Test ownership: umbrella `scripts/tests/test_ops_deployment.py` owns `test_deployment_refuses_unreviewed_pins_and_unsafe_migration`.
**Tests:** `test_deployment_refuses_unreviewed_pins_and_unsafe_migration`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_deployment.py' && python3 scripts/release-preflight.py --environment staging --pins-from-gitlinks && python3 scripts/deploy.py --environment staging --pins-from-gitlinks --verify`
**Done when:** A reviewed candidate deploys reproducibly to staging and a failed rollout preserves a compatible service with forward-only database history.

### 1.10.12 — Alerting, availability and operational response
**Repo:** umbrella · **Size:** M · **Depends on:** `1.10.4` · **Requirements:** SR-NFR-REL-001, SR-NFR-OBS-001, SR-NFR-PERF-003
**Files:** `infra/observability/alerts.yaml`, `scripts/alert-drill.py`, `docs/runbooks/operations.md`, `docs/evidence/phase-1-alerts.md`, `scripts/tests/test_ops_alerts.py`
**Build:** Define the 99.9% monthly availability SLI with approved maintenance accounting, external probes and a named responder. Alert on error rate, latency, pool wait/exhaustion, queue age, scan failures, failed backups and TLS expiration with actionable runbooks. alert-drill.py injects a bounded synthetic staging failure, captures delivery/acknowledgment and verifies recovery; it cannot disable production services. Record operational coverage and escalation; do not claim measured monthly availability from one drill. Test ownership: umbrella `scripts/tests/test_ops_alerts.py` owns `test_alert_drill_requires_delivery_and_human_acknowledgment`.
**Tests:** `test_alert_drill_requires_delivery_and_human_acknowledgment`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_alerts.py' && python3 scripts/alert-drill.py --environment staging --output docs/evidence/phase-1-alerts.md`
**Done when:** A synthetic fault pages the named responder and recovery clears the alert with recorded timestamps.

### 1.10.13 — Independent restore and incident rehearsal
**Repo:** umbrella + backend · **Size:** L · **Depends on:** `1.10.5`, `1.10.12` · **Requirements:** SR-NFR-REL-002, TEST-008, BR-OBJ-09
**Files:** `scripts/restore-drill.py`, `docs/evidence/phase-1-recovery.md`, `docs/runbooks/security-incident.md`, `backend/test/ops/recovery.e2e-spec.ts`, `scripts/tests/test_ops_recovery.py`
**Build:** A reviewer follows the runbook into an isolated recovery environment without author-only knowledge. Restore database/object versions/Keycloak/config/key references; validate tenant isolation, audit/version hashes, file downloads and identity login. Measure RPO≤24h/RTO≤8h from timestamps (requirements/03_Sodara_SysRD.md:235–236); report actual values. Rehearse containment/revocation/evidence preservation for a suspected leak; counsel decides any legal notification obligations. restore-drill.py refuses an existing/production target and records dataset/backup/pin provenance. Test ownership: backend `backend/test/ops/recovery.e2e-spec.ts` owns `restored_mvp_preserves_tenant_audit_and_file_integrity`; umbrella `scripts/tests/test_ops_recovery.py` owns `test_restore_drill_refuses_production_or_missing_key_reference`.
**Tests:** `restored_mvp_preserves_tenant_audit_and_file_integrity` · `test_restore_drill_refuses_production_or_missing_key_reference`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_recovery.py' && python3 scripts/restore-drill.py --environment staging --new-isolated-target --output docs/evidence/phase-1-recovery.md && (cd backend && just test-e2e -- test/ops/recovery.e2e-spec.ts)`
**Done when:** An independently followed restore meets measured RPO/RTO and the incident rehearsal preserves evidence and revokes affected access.

### 1.10.14 — Security review and abuse-case acceptance
**Repo:** umbrella · **Size:** L · **Depends on:** `1.10.7`, `1.10.13` · **Requirements:** SR-NFR-SEC-001, TEST-006, BR-OBJ-05
**Files:** `docs/evidence/phase-1-security-review.md`, `scripts/check-security-review.py`, `scripts/tests/test_ops_security_review.py`
**Build:** Arrange an independent reviewer before launch; provider scheduling is waiting time, not hidden implementation effort. Review applicable ASVS/API coverage plus tenant-context attacks, object policy, confidential projections, OIDC callback/CSRF/session revocation, signed PUT replay, export leakage and worker privilege boundaries. Record evidence per control and findings with fixes/retests. check-security-review.py rejects unreviewed applicable controls and open critical/high findings, and validates reviewer/date/pin provenance. If review scope exceeds this PR budget, append explicit review slices; never mark a blanket review complete. Test ownership: umbrella `scripts/tests/test_ops_security_review.py` owns `test_security_review_rejects_unreviewed_controls_or_high_findings`.
**Tests:** `test_security_review_rejects_unreviewed_controls_or_high_findings`
**Verify:** `python3 -m unittest discover -s scripts/tests -p 'test_ops_security_review.py' && python3 scripts/check-security-review.py --file docs/evidence/phase-1-security-review.md --pins-from-gitlinks`
**Done when:** A named independent reviewer accepts the exact release evidence with no unresolved critical/high finding.

### 1.10.15 — Arabic language and domain-owner acceptance
**Repo:** umbrella + frontend · **Size:** M · **Depends on:** `1.10.8`, `1.1.7` · **Requirements:** SR-NFR-I18N-001, TEST-010, UX-008, PRD-PL-001, PRD-CT-001, PRD-LE-001
**Files:** `docs/evidence/phase-1-language.md`, `scripts/check-language-review.py`, `frontend/tests/ops/language.spec.ts`, `scripts/tests/test_ops_language.py`
**Build:** A named native Arabic reviewer and agency workflow owner review every MVP and Keycloak state, notices/email, validation/error messages and contract/date terminology against a fixed inventory. Verify locale switch does not alter business data and mixed identifiers use bidi isolation. Record approved terminology and resolve ambiguous translations; no machine-only acceptance. check-language-review.py rejects missing routes/states/locales, unresolved findings or absent reviewer/pin evidence. Test ownership: frontend `frontend/tests/ops/language.spec.ts` owns `locale_switch_preserves_mvp_business_data`; umbrella `scripts/tests/test_ops_language.py` owns `test_language_review_requires_provider_and_business_states`.
**Tests:** `locale_switch_preserves_mvp_business_data` · `test_language_review_requires_provider_and_business_states`
**Verify:** `(cd frontend && npx --no-install playwright test tests/ops/language.spec.ts) && python3 -m unittest discover -s scripts/tests -p 'test_ops_language.py' && python3 scripts/check-language-review.py --file docs/evidence/phase-1-language.md --pins-from-gitlinks`
**Done when:** Native Arabic and agency reviewers accept all inventoried business/provider journeys at the exact tested pins.

## Phase-specific OPEN dependencies

These are execution references to the [master OPEN register](00-master-plan.md#open-register), using its question/default/owner/evidence shape. Defaults do not settle legal or stakeholder questions.

| Question | Safe default meanwhile | Owning microstep | What settles it |
|---|---|---|---|
| Which child/guardian scopes are permitted? | No guardian access without explicit approved link/scopes; protected fields denied | 1.2.3 | Recorded agency and counsel access policy |
| Which fields are required per lifecycle stage? | Visibly provisional seed rules; minimal prospect fields remain minimal | 1.2.5 | Agency approval of versioned rule set |
| Which contract types/subjects include representation or non-player coaching? | Preserve required player link and baseline types; never fabricate a player | 1.4.1 | Agency-approved type/subject policy and reviewed schema extension |
| Who approves each contract type and which duties must be separated? | Legal then owner; requester cannot approve own request | 1.4.9 | Agency-approved versioned chain and exception policy |
| What manual signature evidence is acceptable in each jurisdiction? | Collect pending evidence; SIGNED disabled | 1.4.5 | Counsel-approved enabled policy and verified evidence procedure |
| Which business hours, holidays, pause rules and SLA targets apply? | Labeled provisional elapsed-hour targets, no invented business calendar | 1.5.2 | Agency approval of versioned SLA calendar/policy |
| What retention/preservation duties apply by record class? | Archive business evidence; no purge; preservation blocks cleanup | 1.3.4 | Counsel/owner-approved retention and preservation policy |
| Which production hosting, residency and Keycloak operator are approved? | Synthetic isolated environments only; production blocked | 1.10.1 | Owner decision with jurisdiction/policy review and named operator |
| Which email provider/domain is approved? | Local Mailpit only; no production delivery claim | 1.6.3 | Approved provider account/domain checks and operational acceptance |
| What capacity envelope represents the first agency? | Explicit provisional synthetic envelope in 1.10.6 | 1.10.6 | Agency volume/concurrency figures and reviewed load thresholds |

## Phase 1 exit gate

Run these future commands after their owning steps are merged and pinned. Record exact application SHAs, environment, time, actual executed/pass/fail/skip counts and evidence links; all required tests must execute and pass. Test discovery, a merged PR or a documentation checker alone does not prove the product. Scope any production operation to owner-approved release authorization and follow the existing [GitHub workflow](03-github-workflow.md).

```bash
python3 scripts/check-plan.py
(cd backend && just check && just migrations && just test-int && just test-e2e)
(cd frontend && just check && npx --no-install playwright test)
just check
python3 scripts/release-preflight.py --environment staging --pins-from-gitlinks
python3 scripts/run-load.py --environment staging --scenario backend/test/load/mvp.js --envelope infra/testing/capacity.yaml --output docs/evidence/phase-1-capacity.md
python3 scripts/security-gate.py --environment staging --pins-from-gitlinks --output docs/evidence/phase-1-security.md
python3 scripts/check-security-review.py --file docs/evidence/phase-1-security-review.md --pins-from-gitlinks
python3 scripts/check-acceptance-evidence.py --kind accessibility --file docs/evidence/phase-1-accessibility.md
python3 scripts/check-language-review.py --file docs/evidence/phase-1-language.md --pins-from-gitlinks
python3 scripts/release-evidence.py --phase 1 --file docs/evidence/phase-1-release.md --pins-from-gitlinks --verify-live
```

Before the final command can pass, 1.10.13's current recovery record and 1.10.12's alert/acknowledgment record must identify the same candidate or a reviewed compatible deployment. Production deployment does not run during a documentation check. Promote app repositories first, update reviewed umbrella pins, then promote the umbrella using existing just promote-staging / just promote-main / just promote-merge recipes; approved signed tags and draft release publication follow the existing delivery workflow. Deployment scripts use reviewed image digests and release approval evidence. No new branch topology or release automation is implied.

Record these demonstrations in docs/evidence/phase-1-release.md, once in Arabic and once in English, with synthetic staging fixtures and separately approved production smoke data:

1. Invite a membership through Keycloak; verify locale/MFA, owner limits, deactivation and first-request revocation.
2. Create a player, review a duplicate warning, complete stage requirements, attach scanned documents and preserve club history; switch locale without changing business data.
3. Draft a contract, create two immutable versions, run ordered separated approvals, attach verified policy-approved evidence and sign only when counsel-approved policy permits it; replay a successful command with its original stale If-Match and obtain the original result.
4. Advance a fixed clock for expiry/reminders, then terminate under the allowed policy; failed notification delivery never changes contract truth.
5. Create/assign/resolve/close a legal ticket with an internal note and attachment; requester cannot discover either and an overdue job cannot reopen the case.
6. Search, timeline, dashboard and CSV export show only authorized records; coach, guardian, administrator without confidential permission and tenant B cannot obtain tenant A's protected fields/files/counts.
7. Follow correlation from UI to API/outbox/worker; trigger an alert and verify acknowledgment, while secret/confidential canaries remain absent.
8. Restore PostgreSQL, versioned objects, Keycloak and key references into an isolated target from the runbook alone, verifying tenant isolation, audit/version hashes and measured RPO/RTO.
9. Complete keyboard, screen-reader, mobile-width and native-Arabic review including Keycloak errors/recovery/MFA and all document/contract failure states.

**Exit is blocked** by unapproved hosting/provider operation, incomplete signature policy, unresolved production privacy duties, failed recovery or required security findings. A sandbox demonstration is recorded as a sandbox result, never production completion. The owner accepts the exact promoted pins; progress changes only with that evidence.
