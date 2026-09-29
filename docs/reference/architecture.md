# Target architecture

This is the build contract, not an implementation-status report. Requirements: SYS-ARC-001..005, SYS-TEN-001..008, SYS-ASY-001..005, SR-CORE-001/002, SR-NFR-SEC-002/003. Decisions: [modular monolith](../adr/0001-modular-monolith.md), [identity](../adr/0002-identity-oidc.md), [sessions](../adr/0003-browser-sessions.md), [tenancy](../adr/0004-tenancy-defense-in-depth.md). The phase files own work and tests; [progress](../implementation/progress.md) alone records completion.

## Verified starting point

Source evidence is relative to the umbrella at backend `b5f32a4`, frontend `31aeb9a`, umbrella `eed4437`. A declaration or import is not proof that a feature works.

| Observation | Evidence | Final owner |
|---|---|---|
| Nest imports auth, medical, scouting and other domain modules into one application. | `backend/src/app.module.ts:12`, `backend/src/app.module.ts:30` | `0.2.6` establishes the executable baseline; each domain step proves behavior. |
| The current Prisma service holds AsyncLocalStorage and exposes a tenant-filter helper; the helper is not universal query enforcement. | `backend/src/infrastructure/prisma/prisma.service.ts:15`, `:98`, `:113` | `0.4.3`, `0.4.12` |
| Audit is currently submitted to a broker queue. | `backend/src/infrastructure/events/event.service.ts:37` | `0.7.1`, `0.7.2`, `0.7.5` |
| The browser adds a tenant header from local storage and logs bodies in development. | `frontend/src/shared/lib/api-client.ts:58`, `:65`, `:83` | `0.1.4`, `0.9.4` |
| The root layout selects Latin font subsets and sets English as its language. | `frontend/app/layout.tsx:9`, `:14`, `:29` | `0.9.2`, `0.9.3` |
| Readiness returns a constant ready result. | `backend/src/health/health.controller.ts:20` | `0.3.7` |

The full defect list is [current-state](current-state.md#defects-each-with-its-owner); the [database review](database.md) distinguishes present schema from target migrations.

## Runtime topology

```text
Browser
  │ HTTPS, one application origin, opaque session cookie
  ▼
Ingress / local HTTPS proxy (0.2.1)
  ├── /[locale]/… ─────────── Next web
  ├── /api/v1/… ──────────── Nest api ───── PostgreSQL 18
  └── /socket.io/… (P2) ──── Nest realtime ───┤
                               │             │
Keycloak / approved IdP ◄── Nest OIDC client   │
                                             │
TenantRegistry → per-tenant outbox claims → worker → BullMQ / Valkey
                                             ├── private object store / ClamAV
                                             └── approved email/signature/payment adapters
```

One backend codebase and database, with separately started API and worker processes; realtime starts in `2.6.1`. Sharing a codebase does not require deploying a placeholder realtime process before it serves a feature. Build one backend artifact with separately declared entry commands. Next is the web runtime. Provider integrations remain adapters within the monolith. Extraction requires measured scaling, fault isolation or organizational need and a new ADR; domain count alone is insufficient.

| Runtime | Owns | Must not own | Initial delivery |
|---|---|---|---|
| `api` | HTTP validation, OIDC protocol endpoints, session checks, policy, transactional business commands, OpenAPI | Long file processing, synchronous email delivery, schema migration at startup | `0.2.6`, `0.5.5`, `0.7.5` |
| `worker` | Tenant-scoped relay/consumer work, schedules, scanning, rendering, bounded external delivery retries | Unscoped business queries, interpreting client-supplied tenant context as authority | `0.7.6`, `0.8.4` |
| `realtime` | Authenticated connection lifecycle, authorized conversation subscriptions, committed event delivery | Independent chat persistence or a second authorization implementation | `2.6.1` |
| `web` | Locale routing, server rendering, interaction and accessible presentation, generated API calls | Credential issuance, direct database access, provider-token custody, business authorization | `0.9.1`, `0.9.4`, `0.9.5` |
| Release migration job | Forward migrations, explicit privileged catalog changes | Application traffic or sharing its credentials with runtime containers | `0.4.2`, `1.10.2` |

Local services are installed in `0.2.1`: PostgreSQL 18, Valkey, private S3-compatible storage, ClamAV, Mailpit and an exact pinned Keycloak image. Production hosting and provider choice remain OPEN in `1.10.1`; staging uses production-mode Keycloak with TLS and restricted administration. The existing branch, promotion, ruleset and pin flow remains unchanged; see [delivery workflow](../implementation/03-github-workflow.md#the-umbrella-pins-and-progress).

## Module boundaries and dependency direction

Each backend domain uses presentation → application → domain dependencies. Infrastructure implements ports declared by application/domain; the domain does not import Nest, Prisma, HTTP or provider SDKs. Do not create one class per trivial DTO merely to imitate a directory diagram.

```text
src/modules/<domain>/
  presentation/             controllers, request/response DTOs, OpenAPI metadata
  application/              use cases, policies, ports, projections
  domain/                   pure states, decisions, money/date rules
  infrastructure/           Prisma repositories and provider adapters
src/infrastructure/         tenant transactions, storage, audit, outbox, telemetry
src/worker.ts               worker composition root
src/realtime.ts             realtime composition root (Phase 2)
test/<domain>/              database and HTTP feature suites
```

Dependencies across modules use exported application services and typed identifiers, not another module's repository or Prisma model. A use case that coordinates several modules shares one supplied tenant transaction for atomic writes; it does not create nested independent transactions. Events carry stable reference IDs and payload schema versions. A module owns the schema and transitions of its aggregates; shared infrastructure supplies mechanisms without selecting business policy.

| Module | Owned facts | Exported boundary / implementation owner |
|---|---|---|
| Identity and users | Global identity links, tenant membership, sessions, invitations, roles | `authenticateSession`, `requireAssurance`, `acceptInvitation`; `0.5.3`–`0.5.10`, `1.1.1` |
| Tenant administration | Locale/zone/currency settings, feature enablement, organization access | `getTenantSettings`, `requireFeature`; `1.1.2`, `1.1.4` |
| Players | Profiles, affiliations, lifecycle, account/guardian presentation, completeness | `getAuthorizedPlayerSummary`, `assertPlayerRelation`; `1.2.1`, `1.2.3`, `1.2.5` |
| Files | Upload sessions, immutable file versions, scan and derivative state | `authorizeUpload`, `finalizeUpload`, `issueDownload`; `0.8.2`–`0.8.5`, typed domain bindings in `1.3.1` |
| Contracts | Drafts, immutable versions, approval rounds/decisions, evidence, reminders | `submitForReview`, `decideApproval`, `recordSignatureEvidence`; `1.4.1`–`1.4.5`, `1.4.8`, `1.4.9` |
| Legal | Ticket lifecycle, assignment, internal notes, deadlines | `transitionTicket`, `addAuthorizedNote`; `1.5.1`–`1.5.3` |
| Notifications and audit | Recipient delivery records/preferences; append-only evidence | `enqueueNotification(tx, …)`, `audit.record(tx, …)`; `0.7.2`, `1.6.1`, `1.7.1` |
| Medical | Restricted records, treatment, clinician-authored availability/RTP | Restricted summary port, never full medical entity exports; `2.1.1`–`2.1.7` |
| Training | Programs, sessions, enrollment, attendance, completion, certificates | `enroll`, `markAttendance`, `evaluateCompletion`; `2.2.1`, `2.2.3`, `2.3.1`–`2.3.3` |
| Performance and ratings | Validated observations, imports, versioned rating schemes | `importPerformance`, `calculateRating`; `2.4.1`, `2.4.3`, `2.5.1` |
| Chat | Conversation membership, ordered messages, read cursors | `sendMessage`, `syncConversation`; `2.6.2`–`2.6.5` |
| Scouting | Prospects, assignments, report review, watchlists | `submitReport`, `approveReport`, `onboardProspect`; `3.1.1`–`3.1.5` |
| Sharing and analytics | Authorized read models, dossier snapshots, grants | `buildDossier`, `resolveShare`; `3.2.2`, `3.3.1`–`3.3.3` |
| Finance | Financial documents, movements, provider reconciliation | `recordPaymentOutcome`, `reconcilePayment`; `3.4.1`–`3.4.3` |
| Platform operations | Separate operator identity, approved support access, entitlements | `grantSupportAccess`, `provisionTenant`; `4.1.1`–`4.1.5` |

The listed ranges are navigation, not dependency syntax. Exact prerequisite IDs are in each step. Medical and scouting remain disabled until their release gates. Creating a module or table does not enable its route.

## Authentication and trusted tenancy

Nest is the confidential OIDC client. The browser starts at `/api/v1/auth/login`; authorization-code exchange uses PKCE, state and nonce. The login attempt is bound to the initiating browser: the existing session for a step-up, otherwise a short-lived `__Host-sadara_preauth` cookie that never authorizes a business request. The callback requires the matching binding and consumes the attempt once before setting the authenticated session. Nest validates issuer, signature, audience, lifetime and protocol context, then links `(issuer, subject)` to an existing or explicitly invited membership. Matching email alone never links accounts. Neither Next nor the browser receives provider tokens. Tokens received during the exchange are used transiently and discarded; persisted derived claims are `issuer`, `subject`, IdP `sid`, `acr`, `amr`, and `auth_time`.

The browser receives one high-entropy `__Host-sadara_session` cookie, `HttpOnly; Secure; SameSite=Lax; Path=/`, without Domain. Persist a digest of its random secret. Session and membership are checked against primary PostgreSQL on every protected request. Idle 30 minutes and absolute 12 hours are provisional policy defaults; sensitive actions also require recent authentication and configured MFA assurance. App revocation affects requests whose authorization check follows the committed revocation. Already-running requests need explicitly tested business preconditions, not an impossible promise that every operation is retroactively cancelled.

An exact configured host produces a **tenant hint**, not authorization. The narrow `AuthBootstrapRepository` uses that validated hint plus the opaque session digest in a transaction restricted by RLS, selecting only authentication/membership fields. It exposes no generic repository access. Only a successful active-session/membership check yields `TenantContext` for a business use case. Unknown hosts fail closed. A host, request body or tenant selector cannot independently create this context. Cross-host tenant selection uses an approved canonical destination and a new host-bound session; same-host selection, if adopted, must validate membership and rotate the session before changing scope. Both clear browser query caches.

```ts
export type TenantContext = Readonly<{
  tenantId: string;
  actor: { kind: 'USER'; userId: string; sessionId: string }
       | { kind: 'SYSTEM'; service: string; eventId: string };
  requestId: string;
  assurance: { authTime?: string; acr?: string; amr: readonly string[] };
}>;
export type TenantTransaction = Prisma.TransactionClient;
export function withTenantTransaction<T>(
  ctx: TenantContext,
  run: (tx: TenantTransaction) => Promise<T>,
): Promise<T>;
```

The helper opens the transaction, sets `app.tenant_id` using parameterized `set_config(..., true)`, and passes that transaction client to every repository. Repository methods receive both the transaction and explicit context/tenant ID; they cannot obtain the root client as a fallback. Policies run before data release or mutation. Repositories require explicit tenant predicates; composite and same-parent foreign keys plus ENABLE/FORCE RLS protect omissions. Runtime is non-owner `sadara_app`, without BYPASSRLS; `sadara_owner` is NOLOGIN and the migrator is separate. See [database](database.md) for the SQL and tests. CLS may carry log correlation, never hidden authorization or query rewriting.

The actor union above is the Phase-0/1 contract. `4.1.1` adds a separately authorized global `PlatformSession`, because an operator must not acquire a hidden tenant User merely to authenticate. `4.1.2` adds an explicit `PLATFORM` actor with operatorId, sessionId and supportGrantId; only a current approved tenant-scoped support grant can create that tenant context. Recheck the operator, session and grant against PostgreSQL and audit the operator identity without impersonating a User. This future extension grants no Phase-0/1 platform access.

OIDC logout events revoke matching derived issuer/subject/sid sessions. Cross-tenant discovery uses a narrow TenantRegistry followed by tenant-scoped operations. Back-channel signature/audience/time/event/replay validation is mandatory. Provider-side disablement or recovery is not assumed to generate every required event: changes take effect at the next validated event or session expiry. That exposure window requires owner acceptance before real-user launch. See OPEN — identity provider and session freshness in the [OPEN register](../implementation/00-master-plan.md#open-register).

## Transaction and durable-work boundaries

```text
Validate DTO → validate current session → choose tenant transaction
  → load scoped resource → current permission/visibility policy → receipt lookup
  → matching completed receipt: authorized replay without re-executing
  → new claim: lifecycle + revision guard → business mutation
      → append audit → append outbox intent + terminal receipt → commit → respond
TenantRegistry → tenant transaction → claim due outbox with lease
  → publish event ID → worker tenant transaction → inbox dedup + local effect → commit
```

Audit failure aborts the protected mutation. Provider/network calls never occur while holding the business transaction. Outbox/inbox rows carrying tenant data have RLS and tenant-safe uniqueness; they are not platform exceptions. Consumer inbox uniqueness is `(consumer, eventId)` with globally unique event IDs and composite tenant bindings. A publish/acknowledgment crash permits redelivery; local effects are deduplicated. External acceptance followed by a crash may duplicate an email unless the provider supplies an adequate idempotency contract. Record `UNKNOWN` remote outcomes and reconcile where necessary.

Valkey is transport, throttling and later realtime distribution, not the authority for membership or session revocation. Database outbox intent survives broker loss. TenantRegistry exposes only eligible tenant IDs, not business data; relay and schedules claim work separately within each tenant transaction. Bounded leases, retries, jitter, dead-state review and fair per-tenant concurrency are established before increasing throughput.

## Files, caches and confidential projections

Upload authorization resolves a typed owner; browser-controlled keys and filesystem paths are not accepted. Uploads land at quarantine keys; finalization checks declared/actual size, type and safe filename. ClamAV scans the exact version that is promoted to a server-controlled immutable object reference `(key, versionId, sha256)`. Downloads and derivatives use that version, never latest-by-key. Replaying the old PUT must not alter approved/downloaded evidence. SQL row immutability does not make storage bytes immutable; both boundaries are tested.

Backend DTOs select permitted fields before serialization. Classification fixtures are independent of DTO annotations. TanStack Query keys include tenant, projection/permission context and filters; caches clear on logout and tenant changes. Server-rendered authenticated data uses per-request access and `no-store`; do not put it into a shared Next cache. Workers, exported files, search indexes, timeline counts and notifications apply the same current authorization rules. A cached summary is not permission to expose its underlying record.

## Deployment and evolution

Phase 0 proves local processes, empty migration replay, SQL catalogs and disposable recovery. Phase 1 chooses hosting and builds images, secrets, telemetry and backup tooling (`1.10.1`–`1.10.5`); `1.10.11` deploys staging and `1.10.12`/`1.10.13` demonstrate alert response and independent restore/key recovery. Realtime is added in Phase 2. New schemas use expand/backfill/validate/switch/contract, forward-only migrations and compatibility tests; migrations do not execute at app startup.

Do not perform a distributed rewrite to share types: backend owns committed OpenAPI, frontend generates its client from an explicit backend revision. Umbrella pins and release evidence record compatible revisions. A module's downstream readers use authorized ports or explicit read projections; no universal “include all” player aggregate. Exact API behavior is in [API](api.md); domain transitions are in [workflows](domain-workflows.md); deployment failure handling is in [observability](observability.md).

## Architecture verification

Owners `0.4.3`, `0.4.5`, `0.6.9`, `0.7.6`, `0.8.5`, `1.10.7` prove transaction context, denied cross-tenant access, worker scope, immutable downloads and integrated security. Run their named feature suites through the phase Verify commands. Domain imports are checked in application lint; new exceptions need a narrow documented port, not a disabled lint rule. A passing diagram or documentation checker proves no runtime behavior.
