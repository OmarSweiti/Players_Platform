# Database review and evolution

Status: converged implementation specification, 29 September 2026. Source baseline: backend `b5f32a4`, frontend `31aeb9a`, umbrella `eed4437`. Every model and all six checked-in migrations were reviewed. This author did not connect to a deployed database or inspect production data. Owner-reported execution evidence is identified separately below. Paths are relative to the umbrella. Target models and SQL are instructions, not claims of implementation.

Requirements: BR-RULE-01/02/05/08/09/11; SYS-TEN-001–008; SYS-ASY-005; SR-DB-001–010; SR-AUD-001–007; SR-CT-006–012; TEST-002/003/008.

## Read the existing schema accurately

The baseline has 29 models and 26 enums, counted from `backend/prisma/schema.prisma:15` through `backend/prisma/schema.prisma:1340`. PostgreSQL is the configured provider (`backend/prisma/schema.prisma:7`); the connection URL comes from `DATABASE_URL` (`backend/prisma.config.ts:11`). The client uses the PostgreSQL adapter and a ten-connection pool (`backend/src/infrastructure/prisma/prisma.service.ts:26`, `backend/src/infrastructure/prisma/prisma.service.ts:34`). These facts establish configuration, not successful deployment.

The checked-in CI/recipe still declares PostgreSQL 17 (`backend/.github/workflows/ci.yml:39`; `backend/justfile:69`). **The adopted target is PostgreSQL 18 everywhere**, aligned in `0.2.1`/`0.2.2`; retain exact release/image digest in environment configuration. The owner reports a PostgreSQL 18.6 / Prisma 7.10.0 replay with no schema difference on 28 September 2026. This is reported qualification evidence, not a claim that this author ran it or that production was upgraded. See [ADR-0013](../adr/0013-postgresql-18.md).

The current migration chain, in execution order:

| Migration | Reviewed content and evidence |
|---|---|
| `20260506200624_init` | 23 initial tables; enums at `backend/prisma/migrations/20260506200624_init/migration.sql:1`, tables at `:56`, FKs at `:853`; final statement at `:1009`. |
| `20260508165634_add_permission_system_and_roles` | Two permission enums, role additions, staff fields, two tables and role/permission FK; `backend/prisma/migrations/20260508165634_add_permission_system_and_roles/migration.sql:2`, `:15`, `:27`, `:37`, `:50`, `:78`. |
| `20260508173239_add_scouting_module` | Two enums and three scouting tables; `backend/prisma/migrations/20260508173239_add_scouting_module/migration.sql:2`, `:8`, `:41`, `:55`, `:117`. |
| `20260508180138_add_medical_enhanced_module` | Four enums and treatment sessions; `backend/prisma/migrations/20260508180138_add_medical_enhanced_module/migration.sql:2`, `:14`, `:52`. |
| `20260508204750_add_password_reset_fields` | Two nullable user fields; `backend/prisma/migrations/20260508204750_add_password_reset_fields/migration.sql:2`. |
| `20260508205107_add_email_verification_fields` | Two nullable user fields; `backend/prisma/migrations/20260508205107_add_email_verification_fields/migration.sql:2`. |

CI is configured to deploy this chain into an empty database and compare the result against Prisma (`backend/.github/workflows/ci.yml:80`). This author did not execute that check. The SQL-managed-object probe and its limits are recorded below; replay/diff does not replace catalog assertions.

### Complete model inventory

| Model | Existing responsibility and review disposition | Evidence |
|---|---|---|
| Tenant | Name/slug/domain, active flag, JSON settings; retain, type critical settings. | `backend/prisma/schema.prisma:275` |
| User | Tenant-owned credential/profile row with one enum role; retain ID as membership identity while moving credentials to OIDC. | `backend/prisma/schema.prisma:321` |
| Season | Tenant dates and current flag; add civil-date and current-season integrity. | `backend/prisma/schema.prisma:411` |
| Document | Polymorphic owner and file URL metadata; replace ownership and storage semantics. | `backend/prisma/schema.prisma:441` |
| Player | Tenant master record including sensitive identity fields; split confidential projections and add identity links. | `backend/prisma/schema.prisma:475` |
| PlayerMedia | Player-scoped file metadata and featured flag; reference canonical assets. | `backend/prisma/schema.prisma:533` |
| MedicalRecord | Confidential by default but injury-centric string fields; preserve data, add controlled record type and codes. | `backend/prisma/schema.prisma:559` |
| Contract | Lifecycle, player, creator, optional season, compensation; strengthen state/version/evidence model. | `backend/prisma/schema.prisma:600` |
| ContractVersion | Numbered file snapshots, mutable timestamps/deletion; make evidence immutable. | `backend/prisma/schema.prisma:661` |
| ContractApproval | Contract-wide approver and step/status; bind decisions to version and approval round. | `backend/prisma/schema.prisma:692` |
| PerformanceRecord | Player/match-date statistics; add range checks and eventual match identity. | `backend/prisma/schema.prisma:727` |
| Rating | Three decimal dimensions plus stored average; introduce immutable scheme versions. | `backend/prisma/schema.prisma:772` |
| Training | Program dates, capacity, price and recurrence flag; add publish/completion policy. | `backend/prisma/schema.prisma:811` |
| TrainingSession | Program session with date/start/end; define timezone and generated-occurrence identity. | `backend/prisma/schema.prisma:854` |
| Enrollment | Player/program unique pair, enrollment/payment status; retain historical identity and add payment snapshot. | `backend/prisma/schema.prisma:885` |
| Attendance | Enrollment/session unique pair; also enforce same training program. | `backend/prisma/schema.prisma:919` |
| LegalTicket | Player case, creator, assignee, due/status/priority; tenant-safe assignee and explicit access classification. | `backend/prisma/schema.prisma:952` |
| LegalNote | Author/ticket/body and internal flag; change confidentiality default and retain revision evidence. | `backend/prisma/schema.prisma:994` |
| Conversation | Tenant thread and group flag; add direct-thread identity and membership lifecycle. | `backend/prisma/schema.prisma:1023` |
| ConversationMember | Unique thread/user membership with last-read timestamp; introduce sequence-based cursor. | `backend/prisma/schema.prisma:1050` |
| ScoutingReport | Player or prospect text, scores and state; enforce subject identity and link assignment. | `backend/prisma/schema.prisma:1079` |
| PlayerWatchlist | Unique user/player pair, untyped priority; retain with governed priority. | `backend/prisma/schema.prisma:1131` |
| ScoutingAssignment | Assigner/scout, age/region filters, untyped status; controlled transitions and linked reports. | `backend/prisma/schema.prisma:1154` |
| TreatmentSession | Patient, optional record, staff, notes and state; enforce record/patient consistency and archival policy. | `backend/prisma/schema.prisma:1189` |
| Permission | Global name/category/action catalog; retain explicit typed definitions. | `backend/prisma/schema.prisma:1227` |
| RolePermission | Global role-to-permission defaults; do not confuse defaults with tenant policy or ABAC. | `backend/prisma/schema.prisma:1244` |
| Message | Thread/sender/content/inline file metadata, edits and deletion; normalize attachments and durable ordering. | `backend/prisma/schema.prisma:1259` |
| Notification | In-app text/reference/read state; introduce delivery/outbox state and safe templates. | `backend/prisma/schema.prisma:1305` |
| AuditLog | Tenant/actor/action/entity, JSON before/after, deletion timestamp; lock down immediately. | `backend/prisma/schema.prisma:1340` |

Enum inventory: UserRole (`:15`), ContractStatus (`:36`), ContractType (`:46`), EnrollmentStatus (`:55`), PaymentStatus (`:63`), MessageType (`:71`), ConversationMemberRole (`:78`), LegalTicketStatus (`:83`), LegalTicketPriority (`:91`), ApprovalStatus (`:98`), PlayerPosition (`:104`), PlayerStatus (`:117`), NotificationType (`:126`), DocumentEntityType (`:140`), FootPreference (`:158`), AttendanceStatus (`:164`), Currency (`:171`), SalaryPeriod (`:178`), PermissionCategory (`:188`), PermissionAction (`:205`), ScoutReportStatus (`:222`), RecommendationLevel (`:230`), InjuryType (`:238`), InjurySeverity (`:248`), TreatmentStatus (`:255`), MedicalRecordType (`:262`), all in `backend/prisma/schema.prisma`.

### Existing strengths, with limits

- Tenant columns and many composite FKs already exist; PlayerMedia.player and MedicalRecord.player/creator are examples (`backend/prisma/schema.prisma:546`, `backend/prisma/schema.prisma:580`). Do not claim that the entire schema lacks tenant constraints.
- Contract version number, enrollment and attendance duplicate prevention already have unique constraints (`backend/prisma/schema.prisma:683`, `backend/prisma/schema.prisma:910`, `backend/prisma/schema.prisma:938`). They do not establish workflow correctness.
- Money is already Decimal, not Float (`backend/prisma/schema.prisma:616`, `backend/prisma/schema.prisma:825`). The defect is fixed two-place scale and missing denomination/range policy, not binary floating-point storage.
- MedicalRecord defaults to confidential (`backend/prisma/schema.prisma:574`), and medical ID lookup scopes tenant and excludes archived records (`backend/src/modules/medical/infrastructure/repositories/medical-record.repository.ts:65`). Neither fact establishes object/property authorization.
- Password-reset tokens are hashed before storage (`backend/src/modules/auth/application/use-cases/forgot-password.usecase.ts:30`); email verification and TOTP have different behavior, below.

## Findings, ranked and owned

Severity describes potential release impact, not a demonstrated production exploit. **Defect** means an existing shape/path permits invalid or unsafe behavior; **gap** means required functionality is absent; **risk** needs data/policy/workload confirmation. High defects block the affected feature; containment and tenant/session failures block all new exposure. None is marked fixed. Stable DB IDs preserve the earlier review; sorting by severity intentionally places DB-43/44 before medium findings.

| ID / severity / kind | Finding, evidence and proposed remedy | Final owner |
|---|---|---|
| DB-01 critical / hardening gap | There are no database row-isolation policies in the reviewed migration chain; its tenant controls are FKs (`backend/prisma/migrations/20260506200624_init/migration.sql:853`). `runWithTenant` only sets AsyncLocalStorage and `getTenantFilter` returns an optional caller-applied filter (`backend/src/infrastructure/prisma/prisma.service.ts:98`, `:113`); TenantGuard only sets request.tenantId (`backend/src/common/guards/tenant.guard.ts:18`). Add RLS, roles and mandatory transaction-scoped repositories. This establishes a missing safety layer, not evidence every existing query leaks. | 0.4.2, 0.4.3, 0.4.5, 0.4.12 |
| DB-02 high / defect | Six nullable references permit cross-tenant links: Contract.season (`backend/prisma/schema.prisma:638`), PerformanceRecord.season (`:756`), Training.season (`:834`), LegalTicket.assignedTo (`:975`), Message.sender (`:1287`), AuditLog.user (`:1358`). Replace all with tenant-aware references after mismatch preflight. | 0.4.1, 0.4.4 |
| DB-03 high / defect | Composite SET NULL includes required tenantId for ScoutingReport.player and TreatmentSession.medicalRecord (`backend/prisma/schema.prisma:1116`, `:1208`; scouting migration `backend/prisma/migrations/20260508173239_add_scouting_module/migration.sql:123`; medical migration `backend/prisma/migrations/20260508180138_add_medical_enhanced_module/migration.sql:58`). Parent deletion can attempt to null tenantId and fail; use RESTRICT plus archival and explicit detach where policy permits. | 0.4.4 |
| DB-04 high / defect | Audit evidence is an ordinary table with `deletedAt` and nullable actor using SET NULL (`backend/prisma/schema.prisma:1358`, `:1361`; initial migration `backend/prisma/migrations/20260506200624_init/migration.sql:502`). Add append-only grants/triggers; retain original actor snapshot and separate restricted retention role. | 0.7.1, 0.7.2 |
| DB-05 high / defect | Verification token and TOTP seed are stored raw (`backend/src/modules/auth/application/use-cases/register.usecase.ts:50`; `backend/src/modules/auth/application/use-cases/enable-2fa.usecase.ts:25`) in fields `backend/prisma/schema.prisma:349`, `:354`. Disable legacy flows and invalidate old secrets during OIDC migration; store no provider tokens in the application; hash opaque application-session handles. Reset tokens are already hashed, as noted above. | 0.1.6 |
| DB-06 high / defect | Document owner is an unconstrained entityType/entityId pair; uploadedById has no User relation (`backend/prisma/schema.prisma:445`, `:455`, `:457`). A tenant FK alone cannot validate file ownership. Introduce typed owner bindings, composite uploader FK and deny unknown owner kinds. | 0.4.4 uploader; 0.8.2 assets; 1.3.1 bindings |
| DB-07 high / defect | TreatmentSession's patient and linked record each independently match a tenant, but may identify different patients (`backend/prisma/schema.prisma:1207`, `:1208`). Current creation only checks time/duration (`backend/src/modules/medical/application/use-cases/create-treatment-session.use-case.ts:10`). Add a composite `(medicalRecordId,playerId,tenantId)` FK and test wrong-patient insert. | 0.4.4 |
| DB-08 high / defect | Attendance independently references enrollment and session without proving the same program (`backend/prisma/schema.prisma:931`, `:932`). Add trainingId and composite FKs to both parents; backfill only rows where their training IDs agree. | 0.4.4 |
| DB-09 high / defect | Permission seeding splits a dotted permission into only category/action and casts to any (`backend/src/modules/users/application/services/permission.service.ts:46`). Names include `contract.reject`, `scouting.report.create`, `document.upload`, `performance.create` (`backend/src/shared/constants/permissions.constants.ts:15`, `:37`, `:86`, `:95`), while enums do not represent those extracted values (`backend/prisma/schema.prisma:188`, `:205`). Replace parsing with an explicit typed catalog; do not broaden permissions to make seeding pass. | 0.6.1 |
| DB-10 high / defect | Email uniqueness is raw VARCHAR per tenant (`backend/prisma/schema.prisma:325`, `:397`) and registration passes dto.email unchanged (`backend/src/modules/auth/application/use-cases/register.usecase.ts:43`). Add canonical normalizedEmail and unique tenant index after collision review. Never merge identities solely by email. | 0.4.1, 0.4.9 |
| DB-11 high / defect | ContractVersion is mutable/soft deletable and identifies a file by URL without digest (`backend/prisma/schema.prisma:670`, `:680`, `:681`). Immutable version content must reference a clean immutable asset and hash; corrections create a new version. | 1.4.8 |
| DB-12 high / gap | Approvals reference the contract, not the approved version or round, and unique(contractId, approvedById) permits only one lifetime row per approver (`backend/prisma/schema.prisma:695`, `:714`). Add approval round/version and append-only decisions so new content invalidates old approval authority. | 1.4.9 |
| DB-13 high / gap | Contract has signedAt/status but no envelope, signatory or evidence relation (`backend/prisma/schema.prisma:609`, `:626`, `:640`). Add signature evidence before enabling SIGNED; require approved signature policy. Do not fabricate signed evidence from timestamps. | 1.4.5; provider integration 3.5.1 |
| DB-14 high / defect | Decimal money scale is two places across contracts/training/enrollment; enrollment has no captured currency (`backend/prisma/schema.prisma:616`, `:621`, `:825`, `:898`). Standardize Decimal(19, 4), explicit currency/exponent validation, denomination snapshot and nonnegative checks. Existing two-place values cannot recover already-rounded precision. | 0.4.7; snapshots 1.4.1, 2.2.4 |
| DB-15 high / defect | Calendar dates and instants are undifferentiated DateTime; migrations use TIMESTAMP(3) without timezone (`backend/prisma/schema.prisma:480`, `:611`; `backend/prisma/migrations/20260506200624_init/migration.sql:136`, `:214`, `:228`). Add DATE for civil dates, TIMESTAMPTZ for instants, and explicit historical timezone conversion plan. | 0.4.1, 0.4.8 |
| DB-16 high / gap | Tenant-owned User with one role has no provider identity or durable sessions (`backend/prisma/schema.prisma:323`, `:330`); refresh verifies a JWT and creates another access token without session state (`backend/src/modules/auth/application/use-cases/refresh-token.usecase.ts:16`). Add Identity and revocable server-side sessions; preserve User IDs as memberships. | 0.5.3, 0.5.6 |
| DB-17 high / gap | Player and User have no account/guardian ownership relation (`backend/prisma/schema.prisma:371`, `:509`); permissions merely comment "own"/"linked" (`backend/src/modules/users/application/services/permission.service.ts:223`). Add PlayerAccountLink and GuardianLink with scope, validity and audited approval; no player/guardian portal until present. | 0.6.5, 1.2.3 |
| DB-18 high / defect | LegalNote defaults `isInternal=false` (`backend/prisma/schema.prisma:1001`), while ticket lacks an explicit confidential visibility class (`backend/prisma/schema.prisma:959`). Default restricted; record audience explicitly, avoid automatic public-to-requester notes. Existing rows require owner classification, not automatic relabeling. | 1.5.1, 1.5.3 |
| DB-19 high / gap | File URL/size/mime appear separately on Document, PlayerMedia, ContractVersion and Message (`backend/prisma/schema.prisma:448`, `:538`, `:670`, `:1270`); no quarantine/hash/object-version state accompanies these shapes. Consolidate FileObject metadata and typed references; no stored permanent public URL. | 0.8.2, 0.8.4; domain owners in the eight-column map |
| DB-20 high / gap | Notification is only in-app state (`backend/prisma/schema.prisma:1305`); no outbox/delivery transaction model exists among inventory above. Add outbox and channel attempts before async side effects are required; retries cannot manufacture duplicate business outcomes. | 0.7.5, 0.7.6; delivery 1.6.1 |
| DB-43 high / gap | Contract has no counterparty relation and ContractType lacks a representation-agreement category (`backend/prisma/schema.prisma:46`, `:600`, `:640`). Add Organization and counterparty FK; add REPRESENTATION, decided as a first-class type whose counterparty is the tenant's agency organization (ADR-0021). This is a product-model gap, not a legal conclusion about required agreement form. Coaching/non-player subjects stay OPEN; never create a fictitious Player. | 1.2.2, 1.4.1 |
| DB-44 high / defect | File sizes use 32-bit Int (`backend/prisma/schema.prisma:450`, `:540`, `:672`, `:1272`), which cannot represent files above 2,147,483,647 bytes. Use bounded BigInt byte counts on FileObject/UploadSession and eliminate duplicated per-domain size fields after reconciliation. This does not prescribe the allowed upload limit. | 0.8.2; domain owners in the eight-column map |
| DB-21 medium / defect | No CHECK constraints accompany numeric/date fields in any reviewed migration. Examples: negative performance minutes/goals (`backend/prisma/migrations/20260506200624_init/migration.sql:282`), inverted contract dates (`:214`), negative training capacity (`:328`). Add direct SQL constraints; app validators remain required. | 0.4.1, 0.4.10; domain checks 1.4.1, 2.2.1, 2.4.1 |
| DB-22 medium / defect | Season.isCurrent is indexed, not uniquely constrained (`backend/prisma/schema.prisma:418`, `:434`); multiple live current seasons are representable. Add partial unique tenant index WHERE isCurrent AND deletedAt IS NULL, if one season is the approved policy. | 0.4.10 |
| DB-23 medium / defect | PlayerMedia.isFeatured has no uniqueness predicate (`backend/prisma/schema.prisma:543`, `:552`); multiple featured items are possible. Adopt one featured image per player, partial unique index, and transactional replacement. | 0.4.10, 1.3.3 |
| DB-24 medium / defect | Medical enums are declared but MedicalRecord uses required injuryType string and optional severity string, with no recordType (`backend/prisma/schema.prisma:238`, `:262`, `:565`, `:567`). Add typed record type and controlled codes; injury attributes nullable for non-injury records. | 2.1.1 |
| DB-25 medium / defect | TreatmentSession has no archive timestamp and repository physically deletes (`backend/prisma/schema.prisma:1211`; `backend/src/modules/medical/infrastructure/repositories/treatment-session.repository.ts:203`). Add archive/revision events; physical purge requires retention approval. | 0.1.8 containment; 2.1.3 archival |
| DB-26 medium / gap | Ratings store mutable totals described as a simple mean (`backend/prisma/schema.prisma:782`), without scheme/version/date range. Add immutable RatingSchemeVersion, criteria/weights and component snapshots; preserve old scores under a legacy-unverified scheme. Only label them a computed mean if provenance and recomputation prove that claim; never invent historical weights. | 2.5.1 |
| DB-27 medium / defect | ScoutingReport allows neither or both player and prospect identity (`backend/prisma/schema.prisma:1083`, `:1086`); prospectAge becomes stale and scores lack database bounds (`:1087`, `:1095`). Introduce Player.lifecycleStage=PROSPECT, then require one canonical player subject after reconciling legacy prospect fields. Keep unknown birth dates nullable; retain observed age with observed-on date and provenance. Do not invent a birthday from age. | 1.11.1 |
| DB-28 medium / gap | ScoutingAssignment and report have no association, assignment.status and watchlist.priority are arbitrary strings (`backend/prisma/schema.prisma:1114`, `:1137`, `:1167`). Add report assignment FK and controlled transition/priority vocabularies. | 1.11.1, 1.11.2, 1.11.4 |
| DB-29 medium / gap | PerformanceRecord repeats opponent/venue/competition strings (`backend/prisma/schema.prisma:734`); Player.currentClub is free text (`:487`). Add tenant-owned Organization/Team/Competition/Match and affiliation history when those workflows arrive; preserve legacy display strings during reconciliation. | 1.2.2, 2.4.4, 3.2.1 |
| DB-30 medium / defect | Message type permits empty text/files; sender isn't constrained to membership (`backend/prisma/schema.prisma:1265`, `:1267`, `:1270`, `:1275`). Add content-by-type CHECKs, tenant sender FK and active-membership policy inside transaction. Nullable sender remains valid only for explicit system events. | 0.4.4 tenant; 2.6.3 content/membership |
| DB-31 medium / gap | Conversation.isGroup alone cannot enforce two-party direct conversations or deduplicate the pair (`backend/prisma/schema.prisma:1027`); membership cursor is only a timestamp (`:1059`). Add canonical direct-pair uniqueness and monotonic per-thread sequence/read cursor. | 2.6.2, 2.6.4 |
| DB-32 medium / defect | isRead/readAt can disagree and polymorphic notification references have no validity mechanism (`backend/prisma/schema.prisma:1315`, `:1318`). Make readAt authoritative, derive isRead; validate typed target through module resolver on read and click. | 1.6.1, 1.6.2 |
| DB-33 medium / gap | Required UUID entityId and tenantId on AuditLog cannot naturally represent pre-tenant authentication failures or global platform changes (`backend/prisma/schema.prisma:1342`, `:1349`). Use separate append-only SecurityEvent and nullable resource ID with typed event contract; never assign a fake business tenant. | 0.7.3 |
| DB-34 medium / risk | Soft-deleted rows remain in lifetime unique keys: users/email, enrollment, conversation membership (`backend/prisma/schema.prisma:395`, `:397`, `:908`, `:910`, `:1066`, `:1068`). Keep lifetime identity for enrollment/membership and reactivate via audited commands; retain email reservation by default. Do not blindly change all keys to partial uniqueness. | 0.4.9, 1.1.1, 2.2.3, 2.6.2 |
| DB-35 medium / gap | Mutable workflows lack an explicit revision for optimistic concurrency (`backend/prisma/schema.prisma:643`, `:979`, `:1118`). Add revision integer and compare-and-increment; updatedAt alone is not an agreed concurrency token. | 0.3.6; 1.2.1, 1.4.1, 1.5.1 |
| DB-36 medium / gap | No certificate or completion rule entity exists in training models (`backend/prisma/schema.prisma:811`, `:885`, `:919`). Add versioned eligibility policy, immutable issuance snapshot and revocation events. | 2.3.2, 2.3.3 |
| DB-37 medium / gap | Salary and enrollment payment fields do not form a financial ledger (`backend/prisma/schema.prisma:614`, `:892`); finance role is only a role (`:28`). Add invoices/payment transactions/reconciliation in Phase 3; never treat paymentStatus as settlement proof. | 3.4.1, 3.4.2, 3.4.3 |
| DB-38 medium / risk | Arbitrary JSON includes settings, player metadata, medical metadata, contract bonuses and extra stats (`backend/prisma/schema.prisma:284`, `:505`, `:577`, `:620`, `:752`). Version JSON schemas, size-limit them, disallow secrets and unapproved restricted fields; promote frequently queried properties to columns. | 0.4.10; 1.1.2, 1.2.1, 1.4.1, 2.1.1, 2.4.1 |
| DB-45 medium / gap | SUPER_ADMIN belongs to the tenant UserRole enum and User requires tenantId (`backend/prisma/schema.prisma:16`, `:323`). Separate PlatformOperator from tenant membership; until that workflow exists, reject implicit platform-to-business access. | 0.6.7; 4.1.1, 4.1.2 |
| DB-46 medium / gap | Notification stores already-rendered title/content (`backend/prisma/schema.prisma:1311`, `:1312`), with no template/version/locale or channel-attempt relation in that model. Use template keys and safe parameters; capture recipient locale on dispatch and keep in-app rendering deterministic. | 1.6.1, 1.6.3 |
| DB-47 medium / gap | RolePermission is a global default keyed by enum role without tenantId (`backend/prisma/schema.prisma:1244`, `:1246`). Treat it as an explicit platform reference table; any tenant customizations need separate tenant-scoped role assignments and deny-by-default policy composition. | 0.6.1; 4.1.4 |
| DB-39 low / defect | Duplicate tenant slug B-tree indexes derive from @unique plus @@index (`backend/prisma/schema.prisma:278`, `:318`; initial migration `backend/prisma/migrations/20260506200624_init/migration.sql:520`, `:529`). Drop the redundant nonunique index in a new migration after verifying no external dependency. | 0.4.6 |
| DB-40 low / risk | Several filter indexes start with status, position or global date instead of tenant (`backend/prisma/schema.prisma:529`, `:943`, `:1127`, `:1219`). Measure representative plans; add tenant/filter/stable-order indexes and remove redundancy from observed use, not guesswork. | 0.4.6; measured follow-up 4.3.3 |
| DB-41 low / risk | Float height/weight lack units or reasonable constraints (`backend/prisma/schema.prisma:490`). Use named unit columns and Decimal or documented bounded Float; no reason to invent medical precision requirements. | 1.2.1 |
| DB-42 low / risk | Fixed currency/position enums constrain international/sport extension (`backend/prisma/schema.prisma:104`, `:171`). Currency reference data is needed now for amount validation; keep football position codes until scope explicitly expands. | 0.4.7 |
| DB-48 low / risk | ConversationMember lacks updatedAt and composite id/tenant uniqueness; TreatmentSession.conductedBy has inconsistent Id naming (`backend/prisma/schema.prisma:1050`, `:1065`, `:1068`, `:1204`). Add the composite key before children reference membership, record read-cursor updates, and rename the staff FK during its owned migration rather than a sweeping cosmetic rewrite. | 2.6.2, 2.6.4, 2.1.3 |

## Target schema contract

Preserve existing UUIDs and migration history. Add `revision Int @default(1)` to editable aggregate roots; conditional writes use `(id, tenantId, revision)` and increment atomically. Every tenant-owned table carries tenantId and has `@@unique([id, tenantId])`; business FKs prove tenant and, where necessary, the same player/program/contract. The Tenant root scopes on its own id. Global tables are an explicit allowlist: Identity, Permission/RolePermission defaults, CurrencyDefinition, SecurityEvent, PlatformOperator, its Phase-4 PlatformSession and migration bookkeeping. A table is never global merely because its author omitted tenantId. Platform support grants carry a tenant and use RLS.

UUID v4 remains the ordinary default. `0.4.11` changes AuditLog/SecurityEvent to Prisma `@default(uuid(7))`; OutboxEvent, ConsumerInbox, Message and Notification use v7 in their respective migrations. Keep existing IDs unchanged. Prisma generates `uuid(7)` client-side, so raw-SQL insertion supplies its own UUID; there is no implicit SQL default. A future native `uuidv7()` default must also be represented as `@default(dbgenerated("uuidv7()"))` and pass drift checks. UUID ordering is not a substitute for `(createdAt,id)` pagination or a per-conversation sequence. [Prisma default semantics](https://www.prisma.io/docs/orm/v7/prisma-schema/data-model/unsupported-database-features).

### Identity, memberships and sessions

`0.5.3` creates the following minimum model. Signatures enumerate stored fields and constraints; all tenant tables also get RLS/grants/catalog tests in that migration.

```text
Identity(id UUID, issuer TEXT, subject TEXT, createdAt TIMESTAMPTZ)
  UNIQUE(issuer, subject)
User(existing id, tenantId, identityId UUID?, normalizedEmail, role, isActive, revision, ...)
  UNIQUE(tenantId, identityId), UNIQUE(tenantId, normalizedEmail)
  UNIQUE(id, tenantId, identityId); FK identityId -> Identity.id
UserSession(id UUID, tokenHash BYTEA UNIQUE, tenantId, userId, identityId,
  issuer, subject, providerSid?, acr?, amr TEXT[], authTime TIMESTAMPTZ,
  createdAt, lastSeenAt, idleExpiresAt, absoluteExpiresAt, revokedAt?, revokeReason?,
  revision)                      -- no CSRF column: the token is derived by HMAC (0.5.6)
  FK(userId, tenantId, identityId) -> User(id, tenantId, identityId)
  UNIQUE(id, tenantId); INDEX(tenantId, identityId, providerSid)
-- login attempts are not a table: 0.5.5 keeps {state, nonce, PKCE verifier, tenant, returnTo,
-- browser binding} in Valkey for ten minutes, consumed once; losing one only aborts a sign-in
Invitation(id UUID, tenantId, normalizedEmail, rolePolicyKey, tokenHash UNIQUE NULL,   -- set by the delivery handler
  tokenIssuedAt?, invitedById, expiresAt, acceptedAt?, revokedAt?, acceptedIdentityId?)
```

Keep User IDs as tenant membership IDs; do not rename the underlying table merely to change vocabulary. Expand identityId nullable, link only through approved proof of issuer/subject, keep unlinked legacy accounts disabled, then enforce required identityId for active members. Preserve archived normalized-email reservations. Reactivation is an audited command, never automatic account linking. One identity can have multiple memberships; no email-only linking, merging, or role assignment from arbitrary IdP claims.

Nest is the confidential OIDC relying party. No provider access, refresh or ID token is persisted. The login attempt's PKCE verifier is short-lived protocol state held in Valkey, never a stored provider token, and is gone after consumption or expiry. Provider responses are validated and discarded after deriving issuer/subject/sid/assurance/session times. `0.5.5` binds each attempt to the initiating browser: the existing session for a step-up, otherwise a short-lived `__Host-Http-sadara_preauth` cookie that can only complete authentication and never authorizes a business route. The callback requires that binding plus state, consumes the attempt and sets a new authenticated session. Step-up binds the existing session and keeps it intact until successful replacement. Use the configured GET/query callback compatible with SameSite=Lax; do not silently switch to a cross-site form POST without redesigning cookie/protocol handling. Store only a digest of the opaque application cookie. `0.5.6` stores no CSRF token: it derives one as an HMAC of the session-token digest under a keyed, rotatable secret, so `GET /api/v1/auth/session` returns the same value to every tab until the session rotates. This is application CSRF material, not a provider token. A dedicated AuthBootstrapRepository resolves the exact configured host through TenantRegistry, then reads the matching session hash and membership in a tenant-scoped transaction; it cannot return domain records or mint the domain TenantContext until session, membership, tenant status and required assurance pass. Host resolution is routing, not authorization.

Every protected request checks PostgreSQL session and membership state. App revocation applies to authorization checks after the revocation transaction commits; already-running commands must recheck critical preconditions before commit. Provider-side changes take effect at the next validated back-channel event or application-session expiry. That exposure window and provisional 30-minute idle / 12-hour absolute limits require owner acceptance. Back-channel logout enumerates TenantRegistry tenants with potentially live matching sessions, including disabled tenants, and revokes matching `(issuer, providerSid)` sessions within each tenant; a valid subject-only logout revokes that issuer/subject's sessions. Reject events with neither valid sid nor subject; never let an omitted identifier become an unfiltered query. There is no global bypass session scan. See [security](security-privacy.md) and [ADR-0003](../adr/0003-browser-sessions.md).

`0.5.10` adds invitations with server-assigned roles; an invitation exists before its token. The delivery handler of `0.7.8` generates the single-use token **at send time**, stores only its hash, and puts the raw value only in the email; the outbox carries the invitation id, never a link, and no table holds recoverable token material. A resend or a retried delivery issues a new token and invalidates the previous one; acceptance consumes the token atomically, once. `0.6.5` adds PlayerAccountLink and GuardianLink: `(id, tenantId, userId, playerId, scope, verifiedAt, effectiveAt, expiresAt, revokedAt, approvedById, evidenceRef)`, composite user/player/approver FKs and lifetime pair identity. Missing, expired or unverified links deny access. `1.2.3` owns the administrative workflow; a guardian link never implies unrestricted medical/legal access. `4.1.1` adds PlatformOperator plus a separate global PlatformSession referencing operator/Identity, with the same opaque-handle digest, derived CSRF token, assurance, expiry and revocation contract. Its narrow authentication adapter has no domain-table grants; no hidden tenant User is created. `4.1.2` adds tenant-scoped SupportAccessGrant with reason, approved actions/resources, approver, expiry and immutable grant events, and a PLATFORM actor context carrying operatorId, sessionId and supportGrantId. Every use checks the current operator/session/grant in PostgreSQL; support never impersonates a User. PlatformSession back-channel cleanup uses its own narrow issuer/sid/subject lookup, not a global business client.

### Composite and same-parent integrity

`0.4.1` inventories violations before `0.4.4` constrains anything. Nullable references use a nullable entity ID with required tenantId; PostgreSQL MATCH SIMPLE permits null parent IDs. Prefer RESTRICT plus explicit archive/detach policy, not composite SET NULL.

```prisma
seasonId String? @db.Uuid
tenantId String  @db.Uuid
season Season? @relation(fields: [seasonId, tenantId],
  references: [id, tenantId], onDelete: Restrict, map: "contracts_season_tenant_fk")
```

```sql
-- New migration. Do not edit the historical single-column FK.
BEGIN;
ALTER TABLE contracts ADD CONSTRAINT contracts_season_tenant_fk
  FOREIGN KEY ("seasonId", "tenantId") REFERENCES seasons(id, "tenantId")
  ON DELETE RESTRICT NOT VALID;
COMMIT;
ALTER TABLE contracts VALIDATE CONSTRAINT contracts_season_tenant_fk;
BEGIN;
ALTER TABLE contracts DROP CONSTRAINT "contracts_seasonId_fkey";
COMMIT;
```

Set reviewed lock/statement timeouts. Separate add/validation phases when a table is large; maintain compatibility with the replay/schema comparison throughout deployment, and never disable drift checks to hide an intermediate mismatch. New writes are checked by a NOT VALID FK while old rows await validation. Prisma does not automatically make a SQL migration transactionally safe; assess each file.

For Attendance add trainingId; Enrollment and TrainingSession each expose a unique `(id,tenantId,trainingId)`, and both Attendance FKs include the same trainingId. For TreatmentSession, MedicalRecord exposes unique `(id,tenantId,playerId)` and the medicalRecord FK includes all three. For Contract.currentVersionId, reference unique `(id,tenantId,contractId)` on ContractVersion so another contract's version cannot become current. ApprovalRound references that same triple. These are relational FKs, not cross-table CHECK expressions. Never silently pick one parent's value when a preflight mismatch is found.

### Database identities, grants and RLS

`0.4.2` provisions `sadara_owner NOLOGIN`, a deployment-only `sadara_migrator` allowed to assume owner, and `sadara_app LOGIN NOBYPASSRLS` without ownership, superuser, CREATEDB, CREATEROLE or membership in either privileged role. Secrets are supplied by environment/hosting provisioning, never migration literals. Revoke PUBLIC schema creation and broad default grants; explicitly grant schema usage and reviewed table/sequence/function privileges. Migration credentials never enter API, worker or realtime containers.

`0.4.5` enables and forces RLS on **every tenant-owned table**; every subsequent tenant-table migration repeats the policy/grant/test pattern, including UserSession, UploadSession, outbox and inbox. Tenant IDs cannot be updated. Catalog tests inventory tables, RLS/FORCE flags, policy roles and predicates, owner identities, runtime grants and role membership; a new unclassified table fails CI.

```sql
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE players FORCE ROW LEVEL SECURITY;
CREATE POLICY players_tenant ON players FOR ALL TO sadara_app
  USING ("tenantId" = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
  WITH CHECK ("tenantId" = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
```

```ts
export type TenantTransaction = Prisma.TransactionClient; // alias, not a wrapper
export async function withTenantTransaction<T>(
  ctx: TenantContext, work: (tx: TenantTransaction) => Promise<T>,
): Promise<T> {
  assertAuthorizedTenantContext(ctx);
  return prisma.$transaction(async tx => {
    await tx.$queryRaw`SELECT set_config('app.tenant_id', ${ctx.tenantId}, true)`;
    return work(tx); // repositories receive this client; no root client fallback
  });
}
```

Explicit repository tenant predicates remain mandatory. Use parameters, transaction-local configuration and the same checked-out connection for every query. Missing context denies reads/writes; malformed context fails closed. Network/provider calls run outside transactions. Tests use the actual sadara_app identity, not owner credentials, including concurrent pool reuse, rollback and raw SQL.

TenantRegistry is a narrow infrastructure adapter over an explicitly maintained routing/discovery relation containing only tenant ID, canonical host/slug and active state. Business-job discovery receives only active eligible IDs; auth host resolution receives an exact match. Back-channel security cleanup includes disabled tenants with potentially live sessions so reactivation cannot revive provider-logged-out access. This global projection contains no Tenant.settings, member list or domain data and is updated transactionally with tenant lifecycle changes. Workers enumerate it, then claim work in separate tenant transactions. There is no BYPASSRLS worker or universal unscoped outbox query. The auth bootstrap and registry modules are not exported to business repositories.

RLS limits accidental missing predicates; it does not supply same-tenant medical authorization or protect against fully compromised runtime credentials that can set arbitrary context. FORCE does not constrain a superuser/BYPASSRLS identity. These limits are part of the threat model, not reasons to omit policy and projections. [PostgreSQL row security](https://www.postgresql.org/docs/18/ddl-rowsecurity.html).

### Audit, security events and immutable evidence

`0.7.1` locks down existing AuditLog first. Preserve historical deletedAt values in a restricted migration report; do not silently undelete or erase evidence. `0.7.2` adds actor kind, immutable actor ID/display snapshot, requestId, reason, outcome, payloadSchemaVersion and redacted structural delta. Business mutation, audit and outbox intent share one transaction: a failed audit aborts the business command. Confidential reads create access audit before the authorized payload is released (`0.7.4`).

`0.7.3` creates global SecurityEvent `(id, occurredAt, eventType, outcome, issuer?, identityRef?, tenantHint?, requestId, reasonCode, redactedMetadata)` for pre-tenant authentication failures and other genuine platform security events. An untrusted tenant hint is not a business-tenant FK or proof of membership. Restrict insertion through a typed adapter and reading to security operators; never manufacture a fake tenant/entity UUID to satisfy AuditLog fields. Business resource IDs may be nullable only for typed events with no resource.

```sql
REVOKE UPDATE, DELETE, TRUNCATE ON audit_logs FROM sadara_app;
CREATE FUNCTION reject_evidence_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'evidence is append-only' USING ERRCODE = '42501';
END $$;
CREATE TRIGGER audit_no_update_delete BEFORE UPDATE OR DELETE ON audit_logs
  FOR EACH ROW EXECUTE FUNCTION reject_evidence_mutation();
CREATE TRIGGER audit_no_truncate BEFORE TRUNCATE ON audit_logs
  FOR EACH STATEMENT EXECUTE FUNCTION reject_evidence_mutation();
```

Apply corresponding privileges and triggers to SecurityEvent, ContractVersion, ApprovalDecision and SignatureEvent in their owning migrations. Mutable approval task/round coordination rows are separate from immutable decisions. Triggers deny every role until a separately reviewed retention mechanism exists; there is no caller-settable bypass flag. Database-owner compromise remains outside this guarantee. Legal hold and approved retention must be designed before destructive purge; no ordinary endpoint can assume a maintenance identity.

### Money, time, safe defaults and concurrency

`0.4.7` creates CurrencyDefinition `(code CHAR(3) PK, minorUnitExponent SMALLINT, enabled BOOLEAN)`, checks exponent bounds and changes existing monetary columns to `NUMERIC(19,4)`. Currency codes are reference FKs, not guessed from tenant locale. Salary period is required with salary; signing fees have explicit denomination; enrollment captures agreed price/currency independently from later program changes. Payable amounts must be nonnegative where the domain requires, finite, within magnitude limits and exactly expressible at the currency exponent. Credits/reversals use explicit transaction direction or bounded signed posting amounts, not negative invoice quantities by accident.

Use decimal-string DTOs and exact decimal arithmetic; never JS Number/parseFloat. Reject excess fractional scale **before** the database rounds to a declared precision. Reject `NaN`, `Infinity` and `-Infinity`; a nonnegative CHECK alone is insufficient for numeric NaN. Add scalar checks, e.g. `CHECK ("salaryAmount" IS NULL OR ("salaryAmount" >= 0 AND "salaryAmount" <> 'NaN'::numeric))`; finite Decimal(19,4) range and application finite-value validation work together. Currency exponent validation occurs in the domain and a reviewed database constraint trigger referencing CurrencyDefinition; disallow exponent edits while dependent payable records exist, using a versioned conversion policy instead. Historical two-decimal data cannot recover previously rounded fractions. [PostgreSQL numeric semantics](https://www.postgresql.org/docs/18/datatype-numeric.html).

`0.4.8` distinguishes civil `DATE` values (birth date, passport expiry, contract/season calendar boundaries) from `TIMESTAMPTZ(3)` instants (created/updated, approvals, messages, expiry/revocation). DATE crosses the API as `YYYY-MM-DD`, never a midnight-in-UTC surrogate. Instants cross as ISO UTC strings and display in tenant timezone. Schedules store startsAt/endsAt plus IANA zone; recurrence additionally stores wall time and explicit DST ambiguity/nonexistent-time handling. Determine historical timestamp provenance before conversion: known UTC uses `USING "createdAt" AT TIME ZONE 'UTC'`; unknown provenance is quarantined for owner resolution, not inferred from the developer's location.

`0.4.9` normalizes email through one documented trim/case policy, reviews collisions, retains archived addresses and preserves membership identity during audited reactivation. Keep lifetime unique enrollment `(trainingId,playerId)` and conversation membership `(conversationId,userId)`; cancelling is a state transition, not permission to create a second historical identity. Approval identity is different: unique round `(contractVersionId,roundNumber)` and ordered step `(roundId,stepOrder)`; decisions have their own immutable event IDs and deduplication.

`0.4.10` adds database ranges/date checks, safe confidentiality defaults, bounded/versioned JSON schemas, a partial unique active current-season index and one-featured-image index. Define current-season scope with the owner before enforcing; no silent deletion of duplicates. Global unique reference keys and proven worker queries may use non-tenant-leading indexes; `0.4.6` reviews a justified allowlist rather than mechanically removing every global index. Capacity writes serialize on the program row; revision checks prevent lost updates and return the [API contract](api.md)'s 412/428 responses.

### Durable work and command idempotency

`0.7.5` creates OutboxEvent `(id,tenantId,type,aggregateType,aggregateId,payloadVersion,payloadRefs,createdAt,availableAt,attempts,status,leaseOwner?,leaseUntil?,dispatchedAt?,lastErrorCode?)` and ConsumerInbox `(id,tenantId,consumer,eventId,completedAt,resultRef?)`. Outbox has unique `(id,tenantId)`; inbox has required `UNIQUE(consumer,eventId)` plus a composite FK `(eventId,tenantId)` to OutboxEvent. This prevents accepting another tenant's event while keeping the required consumer/event identity. Provider callback owners `3.4.2`/`3.5.1` create WebhookReceipt `(id,tenantId,provider,providerAccountId,remoteEventId,payloadHash,localEventId,receivedAt,status)` with unique `(provider,providerAccountId,remoteEventId)`. Authenticate provider/account mapping before tenant resolution; commit the bounded receipt and a tenant-bound local OutboxEvent UUID atomically, then acknowledge. ConsumerInbox deduplicates processing that local event. A duplicate remote ID with different payload hash is a security conflict. Do not put provider-specific event strings into ConsumerInbox or copy confidential callback bodies into generic payloads.

Each tenant claim uses `FOR UPDATE SKIP LOCKED`, a bounded lease and fencing/CAS version. The relay publishes with the event UUID as BullMQ job ID; a consumer records its inbox receipt in the same transaction as its database effect. Crashes before/after commit/publish and stale leases are tested. Database leases/status are operational state, so outbox is durable but not append-only in the same sense as audit. Retention cannot delete an event still needed for replay or evidence. Email has durable intent and local deduplication; a crash after provider acceptance can duplicate delivery unless the provider offers idempotency. Do not call this exactly-once delivery.

Before mutation, authenticate, check current action/resource access and validate request shape. Resolve a matching terminal idempotency receipt before reevaluating the original revision/lifecycle precondition: a legitimate retry carries the old If-Match after its first execution changed revision. A changed body or precondition changes requestHash and conflicts; revoked current access still denies. Only a new/reclaimed execution evaluates the current revision and workflow guards.

`0.7.7` creates IdempotencyRecord `(id,tenantId,actorUserId,method,canonicalPath,keyHash,requestHash,state,leaseOwner,leaseUntil,fencingGeneration,outcomeStatus,resultRef,expiresAt)` with unique `(tenantId,actorUserId,method,canonicalPath,keyHash)`. States are IN_PROGRESS, SUCCEEDED and terminal REJECTED; a terminal receipt is re-authorized before release. Reusing a key with a different validated request hash (including precondition) returns conflict; expired/stale claims cannot repeat an already committed outcome. Business mutation, audit, outbox intent and the terminal receipt commit atomically. External dispatch ambiguity is a separate UNKNOWN delivery state, not permission to repeat a successful command. Confidential response bodies are not copied into a generic idempotency cache.

### Private file objects and domain bindings

`0.8.2` creates FileObject `(id,tenantId,quarantineKey,objectKey?,objectVersionId?,sha256?,sizeBytes,mimeType,originalName,status,scanVerdict,classification,retentionClass,createdById,createdAt,finalizedAt?,purgedAt?)` and UploadSession `(id,tenantId,fileObjectId,createdById,declaredSize,declaredType,expiresAt,finalizedAt?,abortedAt?,revision)`. Size is bounded BigInt bytes; the policy maximum is separate from the column capacity. Composite uploader/object FKs and RLS ship with both models. The raw client filename is display metadata only.

Canonical lifecycle: CREATED → UPLOADING → UPLOADED → SCANNING → PROCESSING → READY, with FAILED/REJECTED/ABORTED terminal outcomes. Scan verdict is PENDING/CLEAN/INFECTED/ERROR. READY requires CLEAN for the exact finalized bytes; CLEAN alone is not download authorization. Upload writes only to quarantine. After scan, promote to a separately protected, versioned final key, persist provider objectVersionId and SHA-256, and pin every download to that version. Final object identity/hash cannot subsequently be updated. Replaying the original PUT after READY must not change downloaded evidence. Provider version IDs are opaque strings, not assumed UUIDs.

Each domain owns typed binding rows with composite owner/FileObject FKs, and checks that the object's classification is at least as restrictive as its owner. Rebinding never declassifies. Supersession links include same tenant, owner and lineage; version number is unique within that lineage. Unresolved legacy polymorphic owners stay quarantined. No automatic HTTP fetch/import from an old URL: import requires an allowlisted source, SSRF-safe resolver, provenance and rescan. Approved purge checks holds and all typed references, then uses a durable job; database cascades never implicitly delete cloud objects.

| Legacy column (verified source) | Exact target and migration owner |
|---|---|
| Document.fileUrl (`backend/prisma/schema.prisma:448`) | FileObject + typed Document ownership bindings. `0.8.2` expands asset schema; **1.3.1** reconciles/backfills and retires this column. |
| PlayerMedia.fileUrl (`backend/prisma/schema.prisma:538`) | PlayerMedia.fileObjectId with same-player/tenant policy; **1.3.3**. |
| Contract.fileUrl (`backend/prisma/schema.prisma:624`) | Contract.currentVersionId; **1.4.1** maps verified values, validates the same-contract version FK and retires this column after **1.4.8** establishes immutable versions and their parent key. |
| ContractVersion.fileUrl (`backend/prisma/schema.prisma:670`) | ContractVersion.fileObjectId plus immutable hash/version evidence; **1.4.8**. |
| Tenant.logoUrl (`backend/prisma/schema.prisma:280`) | Tenant.brandingFileObjectId / typed branding binding; **1.1.2**. |
| User.avatarUrl (`backend/prisma/schema.prisma:334`) | User.avatarFileObjectId / typed avatar binding; **1.1.8**. |
| Conversation.imageUrl (`backend/prisma/schema.prisma:1029`) | ConversationImage → FileObject; **2.6.2**. |
| Message.fileUrl (`backend/prisma/schema.prisma:1270`) | MessageAttachment → FileObject; **2.6.5**. |

### Domain schema completion

| Final owner | Target models / invariants |
|---|---|
| 1.1.1, 1.1.2, 1.1.4 | UserRoleAssignment/history, typed Tenant timezone/locale/currency settings, tenant FeatureFlag with default-off medical/scouting. Reuse identity/invitation tables; no second credential store. |
| 1.2.1, 1.2.2, 1.2.5 | Player protected identity/projection fields, lifecycleStage and revisions; Organization `(id,tenantId,kind,name)`; PlayerAffiliation `(id,tenantId,playerId,organizationId,startDate,endDate,isCurrent)` with same-tenant FKs; versioned profile-completeness policy. Preserve legacy club labels pending reconciliation. |
| 1.4.1, 1.4.8 | Contract counterparty and captured compensation/period/currency; ContractVersion `(id,tenantId,contractId,versionNumber,fileObjectId,sha256,termsSnapshot,createdById,createdAt,changeNote)` immutable, unique `(contractId,versionNumber)`, unique `(id,tenantId,contractId)`. |
| 1.4.9 | ApprovalRound `(id,tenantId,contractId,contractVersionId,roundNumber,state)`, ApprovalStep `(id,tenantId,roundId,stepOrder,eligibleRole,assignedUserId?)`, immutable ApprovalDecision `(id,tenantId,stepId,actorUserId,outcome,comment,decidedAt,requestKey)`; no approval survives a different version. |
| 1.4.5 | SignatureEvidence/Signatory/SignatureEvent bound to contract version/source hash and approved evidence-policy version; preserve sourceSha256 separately from signedArtifactSha256 because signing may change PDF bytes; manual evidence records method, verified actor/authority and file references. `SIGNED` stays blocked without approved policy. Provider envelopes/adapters extend this model in 3.5.1; do not create a second signature truth. |
| 1.5.1, 1.5.2, 1.5.3 | LegalTicket classification, requester/assignee policy, SLA policy/timezone snapshot, revision; LegalNote audience defaults restricted and revisions are evidence. Typed ticket/note file bindings. |
| 1.6.1, 1.6.3, 2.7.1 | Notification template/version, safe params, authoritative readAt; NotificationDelivery `(id,tenantId,notificationId,recipientId,channel,attempt,status,providerRef,errorCode,acceptedAt?,deliveredAt?)` with unique attempt identity; preferences and later PushDevice token lifecycle. |
| 1.9.1, 2.9.1 | ExportJob/ImportJob with policy snapshot, requested fields, source/output FileObject, expiry, row validation, dedupe and resumable progress. Reauthorize before artifact release. |
| 2.1.1, 2.1.2, 2.1.3, 2.1.4 | MedicalRecord.recordType/coded fields, MedicalAccessGrant and amendment events; treatment archive/revision history; return-to-play decision event with human author. Injury-specific fields nullable for other types. New medical tables inherit tenant RLS before the 2.1.8 activation gate. |
| 2.2.1, 2.2.2, 2.2.3, 2.2.4 | Training publication/completion policy, capacity, exact price; session recurrence identity unique `(trainingId,occurrenceKey)` and zone; audited enrollment reactivation/waitlist; agreedPrice/paidCurrency snapshots; payment state is not settlement evidence. |
| 2.3.1, 2.3.2, 2.3.3, 2.3.4 | Attendance recorder + immutable adjustment history and same-program FK; CompletionRuleVersion; CertificateTemplateVersion and immutable CertificateIssue `(tenantId,enrollmentId,ruleVersionId,templateVersionId,fileObjectId,verificationTokenHash,issuedAt)` plus revocation events. Public verification releases only an approved minimal subset. |
| 2.4.1, 2.4.3, 2.4.4 | Performance range checks, import source/externalRef uniqueness; Match and PlayerMatchStat with tenant-safe player/match/season relations. Preserve raw imported values in restricted staging with provenance; never overwrite accepted history silently. |
| 2.5.1, 2.5.2 | RatingSchemeVersion/RatingCriterion immutable versions, component values, precision/rounding and computed total snapshot; preserve legacy scores under legacy-unverified provenance, not invented historical weights. |
| 2.6.2, 2.6.3, 2.6.4, 2.6.5 | Direct conversation canonical pair key; lifetime membership plus join/leave history; per-thread message sequence and unique `(conversationId,senderId,clientMessageId)`; edit/recall events; lastReadSequence cursor and typed attachments. |
| 2.8.1, 2.8.2 | Extend UploadSession with multipart IDs/parts/expiry; MediaVariant `(tenantId,sourceFileObjectId,transformVersion,kind,outputFileObjectId)` unique per transform, pinned source bytes and scan verdict. |
| 1.11.1, 1.11.2, 1.11.3, 1.11.4 | Player stage PROSPECT with optional unknown birth date; ScoutingReport canonical player FK, assignment FK, observed-age provenance, bounded scores/state; typed assignment/watchlist vocabularies. Existing watchlists remain player-based. |
| 3.2.1, 3.2.2 | Team/Competition and affiliation structures where needed; AnalyticsDefinitionVersion/authorized snapshots with source watermark, period and metric provenance. |
| 3.3.1, 3.3.2 | DossierVersion with approved field subset, immutable private artifact; ShareGrant token hash, expiry, revocation, recipient restrictions and per-view audit. No unrestricted live player lookup behind a share token. |
| 3.4.1, 3.4.2, 3.4.3, 3.4.6 | Invoice/InvoiceLine, Payment/Allocation, immutable balanced JournalEntry/Posting and reversals; provider receipt dedupe and reconciliation. No cross-currency total without explicit rate/source/time policy. |
| 3.5.1, 3.5.2 | SignatureEnvelope and verified provider-event receipts extend Phase-1 evidence with provider/envelope/signatory IDs and separate source/result document hashes; append-only SignatureEvent remains authoritative evidence. |
| 3.6.1 | ReportDefinition/ReportSchedule with timezone, scope and recipient authorization; each run stores source watermark and generated artifact. |
| 4.1.1, 4.1.2, 4.1.4, 4.1.5, 4.1.7 | PlatformOperator/PlatformSession, SupportAccessGrant, tenant role customization, Entitlement and UsageReservation/Ledger; no implicit support bypass. |
| 4.3.2, 4.3.3 | LegalHold and release events; measured index/partition/archival changes with restore/catalog regression tests. |
| 4.4.1, 4.4.2, 4.4.3 | IntegrationClient/ScopeGrant, WebhookSubscription/Delivery and calendar consent/sync cursors. Provider integration credentials require their own encrypted secret lifecycle; this does not authorize storing OIDC login tokens. |
| 4.5.1, 4.5.2 | AI input manifest, approved provider/model/config version, generated artifact and human review decision; no autonomous clinical/contract decision. |

## Forward-only migration and verification sequence

New timestamped migrations use descriptive suffixes, never plan numbers as test/file organization. Do not edit the six historical migrations. The feature test suites live under their modules; exact required test titles and commands belong to the phase steps and [test catalog](test-catalog.md).

| Order / owner | Migration work | Evidence before activation |
|---|---|---|
| 0.2.2 | Pin PostgreSQL 18 CI/replay; preserve historical chain. | Empty replay and existing schema diff pass with captured versions. |
| 0.4.1 | Read-only `backend/scripts/schema-preflight.sql` and report tool. | Deterministic cross-tenant/orphan/same-parent/collision/range/date/secret-state findings; no mutation or raw confidential values. |
| 0.4.2, 0.4.3 | Provision roles/grants and tenant transaction adapter. | Actual role membership/privileges; parameterized transaction-local context and pool-reset proof. |
| 0.4.4, 0.4.5, 0.4.6 | Add/backfill/validate composite and same-parent FKs; RLS/immutable tenant IDs; indexes. | Runtime raw SQL cross-tenant and wrong-parent denial; nullable valid rows pass; all table policies/grants cataloged. |
| 0.4.7, 0.4.8, 0.4.9, 0.4.10 | Currency/NUMERIC, date conversion, normalized email reservations, range/partial uniqueness/JSON constraints. | Approved data-correction manifest; exact currency/date roundtrips, archived identity reactivation and concurrent uniqueness tests. |
| 0.4.11, 0.4.12 | Selective UUIDv7 defaults; existing modules use the tenant transaction. | Existing IDs unchanged, expected UUID versions, every repository path scoped and no local-credential fallback. |
| 0.5.3, 0.5.10, 0.6.1, 0.6.5 | Identity/UserSession/OIDC attempt, invitations, permission catalog, player/guardian links. | No email-only link, expired/consumed attempt rejected, every-request revocation, relationship denial. |
| 0.7.1, 0.7.2, 0.7.3 | Audit protections/typed events and tenantless SecurityEvent. | UPDATE/DELETE/TRUNCATE and grant tests; audit failure rolls back domain change; no fake tenant for unknown login. |
| 0.7.5, 0.7.7 | Outbox/inbox/leases and IdempotencyRecord, all tenant-scoped. | Crash/replay/lease takeover, duplicate payload conflict, cross-tenant receipt rejection. |
| 0.8.2, 0.8.4 | FileObject/UploadSession, scan attempts and immutable promotion metadata. | Old PUT replay cannot alter READY bytes; orphan/unclean assets unavailable; full version-bound hash evidence. |
| Phase 1 owners above | Typed owner bindings, domain revisions, immutable contract/approval/signature evidence, legal access and notification delivery. | Old-schema fixture upgrade, empty replay, custom catalogs, full positive/negative vertical slice; eight URL migrations tracked explicitly. |
| Phases 2–4 owners above | Add only the domain tables needed by the active microstep, with RLS/grants/FKs in the same migration. | Re-run isolation, custom-object, recovery and domain tests; update schema/model inventory and ownership map. |

Preflight output: `{schemaVersion, inspectedAt, counts, violations, unknowns}`; each violation carries stable rule/table/rowId/tenantId/reason, never raw passport/medical/token/compensation values. Six unsafe edges need mismatched-tenant and orphan checks. Same-patient/program joins compare both tenant and parent identity. Email collision reports use safe row identifiers. Inventory historical deleted audit rows, financial denomination and timestamp provenance. Every real correction needs a reviewed manifest naming rows, action, approver and reason; the default tool cannot update data.

Deploy expand → backfill → validate → switch reads/writes → retire compatibility columns in a later change. Preserve an application rollback path through expansion; do not reverse committed migrations. For large tables document locks, batch size, resumability and temporary dual-write consistency. No-data claims require an inspected empty-state report. Run restore rehearsals only on disposable local services in `0.10.3`; production-shaped staging recovery is designed in `1.10.5` and independently rehearsed in `1.10.13`, including identity configuration and key restoration.

### SQL-managed object registry and the reported probe

Partial indexes, CHECKs, RLS policies, grants and triggers live in reviewed migration SQL; `partialIndexes` preview remains **off**. Prisma7.10 can represent partial indexes through a preview feature, but this project deliberately does not adopt it. The owner reports that on **29 September 2026**, Prisma7.10.0 against PostgreSQL18.6 returned **no difference** after `migrate deploy` followed by adding a raw partial unique index, CHECK, RLS policy and trigger and running:

```sh
npx prisma migrate diff --from-config-datasource --to-schema prisma/schema.prisma --exit-code
```

That probe demonstrates the tested configuration's blind spots; it does not prove production privileges, all possible SQL objects, future Prisma behavior or any product microstep complete. Preserve its script/output with adoption evidence and rerun the probe on upgrades. The existing diff check stays enabled; catalog tests prove objects it does not model. See [ADR-0017](../adr/0017-sql-managed-database-objects.md).

| Object family | Owning step | Catalog and behavioral assertion |
|---|---|---|
| Role ownership, default grants and schema privileges | 0.4.2 | pg_roles/pg_auth_members and privilege functions; app non-owner/NOBYPASS/no owner membership. |
| Composite/same-parent FKs | 0.4.4; every new binding | pg_constraint column order, parent keys, validated flag and delete action; bad inserts fail. |
| ENABLE/FORCE RLS, policy predicates and immutable tenant trigger | 0.4.5; every new tenant table | pg_class/pg_policy/pg_trigger plus missing/wrong-tenant reads/writes and pool reuse. |
| Money/date/range/JSON CHECKs and currency trigger | 0.4.7, 0.4.8, 0.4.10 | Definition and enforcement for invalid raw SQL, finite numeric values and policy-safe bounds. |
| Partial unique season/featured indexes | 0.4.10, 1.3.3 | pg_index/pg_get_indexdef predicate, uniqueness and concurrent competing writes. |
| Audit/SecurityEvent U/D/TRUNCATE rejection | 0.7.1, 0.7.3 | Row/statement trigger events and runtime privileges; exercise all three operations. |
| ContractVersion/ApprovalDecision/SignatureEvent immutability | 1.4.8, 1.4.9, 1.4.5; 3.5.2 extension | Same U/D/TRUNCATE and grant assertions, including evidence retention under domain archival. |
| Outbox/inbox/idempotency uniqueness, policies and lease constraints | 0.7.5, 0.7.7 | Tenant receipt FK, consumer/event identity and fenced recovery tests. |

Implementation verification uses the adopted repository recipes, not a substitute migration command or a shared database. Existing `just migrations` creates/destroys a replay container (`backend/justfile:63`). After the harness and feature suites exist, run the exact phase Verify plus:

```sh
cd backend
just prisma
just migrations
just test-int
just check
```

Missing or skipped named tests fail acceptance. Test raw SQL as sadara_app and HTTP/repository paths with two tenants, two players per tenant, a wrong-patient/program pair, archived rows, revoked membership, unlinked identity and platform operator. Include denied counts/joins, pool rollback, audit failure injection and immutable storage versions. This specification does not assert these commands have passed.

## Policy dependencies

The [master OPEN register](../implementation/00-master-plan.md#open-register) is authoritative. Existing-data/timestamp provenance gates conversion; current-season semantics gates its partial unique index; currency/rounding policy gates new payable currencies; medical/guardian policy gates confidential access; evidence policy gates SIGNED; hosting/retention gates production data and purging. Keep synthetic data and denied/quarantined surfaces as the default while these are unresolved. No engineering decision establishes legal sufficiency, certification or a production database's safety.
