# The demo milestone — the first sales demo, built as the real product

> **Goal:** show a sports agency, from a laptop, in Arabic and English, a working Sadara — its
> dashboard and alerts, its players and their 360 view, its contracts and documents, and its
> scouting — all real features on the real foundation, filled with two fictional agencies' working
> lives. First pitch: in four to six months (owner, 1 October 2026). The demo is the product: every
> invariant, test and review applies, and nothing is faked
> ([ADR-0021](../adr/0021-a-product-built-to-sell.md)).

This file is the **build order**. The phase files still define every step; this list says which steps
the demo needs and in what order to build them. The plan check verifies it: every listed step exists,
and each one's dependencies come earlier in the list or are already done. The frontier in
[`README.md`](README.md) shows the next steps from it first.

## What the demo shows

| Area | What an agency sees | Steps |
|---|---|---|
| **Dashboard and alerts** | the actions waiting for each person; contracts entering their reminder windows; a portfolio summary for the agency's leadership; a notification center | `1.8.2`, `1.8.3`, `1.4.4`, `1.6.1`, `1.6.2` |
| **Players and profiles** | a searchable bilingual directory; the Player 360 view with club history, photos, documents, contracts, scouting and activity; completeness by stage; duplicate warnings | `1.2.1`–`1.2.8` (not `1.2.3`), `1.3.3`, `1.7.2`, `1.8.1`, `1.8.4` |
| **Contracts and documents** | representation and player contracts through drafting, immutable versions, ordered approvals, signature evidence, expiry and termination; documents that are scanned before anyone can open them | `1.4.1`–`1.4.10`, `1.3.1`, `1.3.2`, `1.3.5`, `0.8.1`–`0.8.5` |
| **Scouting** | assignments, reports and their review, private watchlists, a prospect onboarded into the roster | `1.11.1`–`1.11.8` |
| **Around them** | Arabic and English with right-to-left layout; the bilingual sign-in page; each agency's own branding; user administration; the roles, visible; every agency's data separate from every other's | `0.9.1`–`0.9.6`, `1.1.7`, `1.1.2`, `1.1.1`, `1.1.6`, `1.1.5`, `0.4.5`, `0.6.9` |

## After the demo, before production

Not in this milestone, and not dropped. These follow the demo and come before anything is hosted for
real users:

- **The production gate** `0.11.1` and what it adds: guardian relationships (`0.6.5`), the legacy medical
  routes (`0.6.8`), and the restore and failure drills (`0.10.3`, `0.10.4`).
- **The rest of Phase 1:** legal tickets (`1.5.1`–`1.5.6`), retention (`1.3.4`), own profile and avatars
  (`1.1.3`, `1.1.8`), the player and guardian workspace (`1.2.3`), the production email provider
  (`1.6.3`, `1.6.4`), the audit workspace (`1.7.3`), exports (`1.9.1`, `1.9.2`), and production
  readiness and launch (`1.10.1`–`1.10.15`).
- **Phases 2–4**, in their order.

## The hosted demo, later

Step `1.12.4` — planned, not scheduled; the owner decides when to rent the server. The demo then runs on
**one small server** with the same images the laptop runs, public TLS and production-mode Keycloak, and
`just demo-sandbox <prospect>` gives each prospect a branded sandbox agency that expires. Because it faces
the internet, it waits for the production gate, the deployment path, managed secrets, telemetry and
security scanning (`0.11.1`, `1.10.1`, `1.10.2`, `1.10.11`, `1.10.3`, `1.10.4`, `1.10.7`), and each
sandbox gets its own identities. Everything before it stays portable: nothing in the milestone may depend on a managed cloud
service that cannot run on that server.

## Forecast and checkpoints

**The target: pitch-ready by 31 March 2027**, six months from the owner's decision. The early end of the
window, four months, is 1 February 2027.

On 3 October 2026 the milestone has 125 steps, 7 of them done. The 118 left weigh **608–1,216
engineering hours** before the reserve; sizes are ceilings ([effort model](00-master-plan.md#effort-model)).

- **The plan's model**, which assumes no speed-up: 32–63 weeks at 25 focused hours a week with the 30%
  reserve. That lands past the target.
- **Measured so far:** `0.2.2` took 0.5 h of its 4 h ceiling, `0.2.4` 1.5 h of 8, `0.2.5` 3.2 h of 8, and
  `0.2.1` 4 h of 8: a median near **0.3 of the ceiling**.
  - At that pace the milestone needs about **475 hours with the reserve: 19 weeks at 25 hours a week**.
    Completion would be around mid-February 2027, inside the window.
  - At 0.5 of the ceiling it needs 32 weeks, until mid-May 2027.
  - Four early, mostly mechanical steps are thin evidence, and the hardest foundation steps (row-level
    security, sign-in, sessions) are still ahead.
- **Checkpoints:** at the foundation gate (`0.11.0`), and after every ten completed steps, project the
  completion date: today plus the remaining forecast, using the master plan's formula with measured hours
  and actual weekly capacity. If it lands after 31 March 2027, the owner chooses among:
  - more weekly capacity;
  - the tier-1 cuts below;
  - a later date;
  - a deeper cut, planned in its own PR that names its companion changes as the tier-1 cuts do.

  The 0.5-pace case would need about 216 ceiling hours removed, or a date in May 2027. The owner decides
  that at the first checkpoint, not now.
- **Tier-1 cuts** (64 ceiling hours), each with the change that goes with it. A cut step leaves only the
  demo; it stays in Phase 1 for production.
  1. Global search (`1.8.1`, `1.8.4`): remove both from the list and from `1.12.3`'s dependencies. The
     pitch finds players through the directory (`1.2.4`).
  2. The visible permission matrix (`1.1.5`): remove it from the list and from `1.12.3`'s dependencies.
     The pitch shows roles through user administration (`1.1.6`).
  3. The executive summary (`1.8.3`): remove it from the list and from `1.12.1`'s dependencies. The
     dataset's leadership story moves to the home dashboard (`1.8.2`).
  4. The custom Keycloak theme (`1.1.7`): remove it from the list and from `1.12.2`'s dependencies.
     Sign-in uses Keycloak's default theme until the step ships.

  Two steps cannot be cut. Duplicate detection (`1.2.6`) is used by scouting's onboarding (`1.11.5`),
  which reviews duplicate candidates. Termination (`1.4.6`) is part of the contract workspace (`1.4.7`).

## The steps, in build order

Edit this list to change the milestone; `just plan` regenerates the table below it. Stage letters group
the work; within a stage, steps run in the order shown, and any step whose dependencies are done may
run early.

<!-- milestone:steps:begin -->
| Stage | Steps, in build order |
|---|---|
| A — Harnesses, containment and the bilingual groundwork | `0.1.1` · `0.1.2` · `0.1.3` · `0.2.1` · `0.2.2` · `0.2.4` · `0.2.5` · `0.2.3` · `0.2.8` · `0.1.4` · `0.1.5` · `0.1.8` · `0.2.10` · `0.1.7` · `0.9.1` · `0.9.2` · `0.9.3` |
| B — Clear the old code, then move to NestJS 12 | `0.4.1` · `0.1.6` · `0.2.7` · `0.2.9` |
| C — The API platform on NestJS 12, and the typed web client | `0.3.1` · `0.3.2` · `0.3.3` · `0.3.4` · `0.3.5` · `0.3.6` · `0.3.7` · `0.3.8` · `0.3.9` · `0.9.4` · `0.10.1` |
| D — The data foundation: tenancy, row-level security, types | `0.4.2` · `0.4.3` · `0.4.4` · `0.4.5` · `0.4.6` · `0.4.7` · `0.4.8` · `0.4.9` · `0.4.10` · `0.4.11` · `0.4.12` |
| E — Identity and access: sign-in, sessions, authorization | `0.5.1` · `0.5.2` · `0.5.3` · `0.5.4` · `0.5.5` · `0.5.6` · `0.5.7` · `0.5.8` · `0.5.9` · `0.5.10` · `0.5.11` · `0.6.1` · `0.6.2` · `0.6.3` · `0.6.4` · `0.6.6` · `0.6.7` · `0.6.9` |
| F — Durable work and files | `0.2.6` · `0.7.1` · `0.7.2` · `0.7.3` · `0.7.4` · `0.7.5` · `0.7.6` · `0.7.7` · `0.7.8` · `0.8.1` · `0.8.2` · `0.8.3` · `0.8.4` · `0.8.5` · `0.10.2` |
| G — The application shell, then the foundation gate | `0.9.5` · `0.9.6` · `0.11.0` |
| H — Administration and branding | `1.1.1` · `1.1.2` · `1.1.4` · `1.1.5` · `1.1.6` · `1.1.7` |
| I — Players and documents | `1.2.1` · `1.2.2` · `1.2.4` · `1.2.5` · `1.2.8` · `1.2.6` · `1.3.1` · `1.3.2` · `1.3.3` · `1.3.5` |
| J — Contracts and alerts | `1.4.8` · `1.4.1` · `1.4.2` · `1.4.3` · `1.4.9` · `1.4.5` · `1.4.10` · `1.6.1` · `1.4.4` · `1.4.6` · `1.4.7` · `1.6.2` |
| K — Scouting | `1.11.1` · `1.11.2` · `1.11.3` · `1.11.4` · `1.11.5` · `1.11.6` · `1.11.7` |
| L — Timeline, search, dashboards, Player 360 | `1.7.1` · `1.7.2` · `1.2.7` · `1.8.1` · `1.8.2` · `1.8.3` · `1.8.4` · `1.11.8` |
| M — The demo | `1.12.1` · `1.12.2` · `1.12.3` |
<!-- milestone:steps:end -->

## Progress

*Generated from this list and [`progress.md`](progress.md) by `just plan`; the plan check fails if it is
stale.*

<!-- plan:milestone:begin -->
**Demo milestone** — 20 of 125 microsteps done; 564–1128 engineering hours left before the reserve.

Next in build order (every dependency done): `0.2.9`, `0.3.1`, `0.3.7`, `0.3.8`, `0.4.2`, `0.4.4`, `0.4.7`, `0.4.8`. … and 4 more.

| Stage | Step | Title | Repo | Size | Status |
|---|---|---|---|---|---|
| A | 0.1.1 | The documentation set lands; the legacy documents are retired | umbrella + backend + frontend | M | done |
| A | 0.1.2 | Agent entry files and scoped rules | umbrella + backend + frontend | S | done |
| A | 0.1.3 | The plan checks itself in CI | umbrella | M | done |
| A | 0.2.1 | The local stack: PostgreSQL 18, S3-compatible storage, Valkey, ClamAV, Mailpit, Keycloak | umbrella + frontend | M | done |
| A | 0.2.2 | PostgreSQL 18 in CI and in the replay recipe | backend | S | done |
| A | 0.2.4 | The web test harness: Vitest, Testing Library, MSW, Playwright in Arabic and English, axe | frontend | M | done |
| A | 0.2.5 | Lint and format gates in both applications | backend + frontend | M | done |
| A | 0.2.3 | The API test harness on a real database | backend | M | done |
| A | 0.2.8 | Integration and end-to-end tests in CI | backend | S | done |
| A | 0.1.4 | Stop secrets and personal data reaching logs and error responses | backend + frontend | M | done |
| A | 0.1.5 | Refuse to boot without real configuration | backend | S | done |
| A | 0.1.8 | Quarantine unfinished modules behind server-side flags | backend | S | done |
| A | 0.2.10 | Module boundaries, checked from the first module | backend + frontend | M | done |
| A | 0.1.7 | Retire the local sign-in pages | frontend | S | done |
| A | 0.9.1 | The route map | frontend | M | done |
| A | 0.9.2 | Arabic and English, RTL and LTR | frontend | M | done |
| A | 0.9.3 | Logical CSS and bidirectional isolation | frontend | S | done |
| B | 0.4.1 | Preflight: report every integrity violation before constraining anything | backend | M | done |
| B | 0.1.6 | Retire the local credential system | backend | L | done |
| B | 0.2.7 | Declared dependencies only; one naming scheme | backend + frontend | S | done |
| B | 0.2.9 | NestJS 12, TypeScript 6 and an ES-module test setup, together | backend | L | todo |
| C | 0.3.1 | One error format: RFC 9457 problem details | backend | M | todo |
| C | 0.3.2 | Strict validation, registered once | backend | S | todo |
| C | 0.3.3 | Versioned routes under /api/v1 | backend + frontend | S | todo |
| C | 0.3.4 | One success envelope, registered once | backend | S | todo |
| C | 0.3.5 | Cursor pagination and allowlisted filters | backend | M | todo |
| C | 0.3.6 | Optimistic concurrency: revisions, ETag, If-Match | backend | M | todo |
| C | 0.3.7 | Liveness and real readiness | backend | S | todo |
| C | 0.3.8 | Rate limits by category, shared through Valkey | backend | M | todo |
| C | 0.3.9 | The committed OpenAPI contract and the breaking-change check | backend | M | todo |
| C | 0.9.4 | A typed client generated from the contract, on the same origin | frontend | M | todo |
| C | 0.10.1 | Structured logs with request correlation | backend | M | todo |
| D | 0.4.2 | Database roles: owner, migrator, runtime | backend + umbrella | M | todo |
| D | 0.4.3 | Explicit tenant context and the tenant transaction | backend | L | todo |
| D | 0.4.4 | Composite and same-parent foreign keys | backend | M | todo |
| D | 0.4.5 | Row-level security on every tenant-owned table; tenant ids immutable | backend | L | todo |
| D | 0.4.6 | Tenant-leading indexes; duplicate indexes dropped | backend | S | todo |
| D | 0.4.7 | Money: NUMERIC(19,4) with currency rules | backend | M | todo |
| D | 0.4.8 | Calendar dates, instants and tenant time zones | backend | M | todo |
| D | 0.4.9 | Normalised emails; lifetime uniqueness with audited reactivation | backend | S | todo |
| D | 0.4.10 | Integrity constraints in SQL: checks, partial uniques, safe defaults, bounded JSON | backend | M | todo |
| D | 0.4.11 | UUIDv7 for high-ingest tables | backend | S | todo |
| D | 0.4.12 | The existing modules on the tenant transaction | backend | M | todo |
| E | 0.5.1 | The Keycloak realm as code | umbrella | M | todo |
| E | 0.5.2 | Resolve the tenant from the host | backend | S | todo |
| E | 0.5.3 | Identities, memberships and sessions in the schema | backend | M | todo |
| E | 0.5.4 | The identity-provider port and the Keycloak adapter | backend | L | todo |
| E | 0.5.5 | Sign-in through the API: authorization code with PKCE | backend | L | todo |
| E | 0.5.6 | Server sessions, the session cookie and CSRF | backend | L | todo |
| E | 0.5.7 | Sign-out, back-channel logout and session management | backend | M | todo |
| E | 0.5.8 | MFA assurance for privileged roles; recent authentication for sensitive actions | backend | M | todo |
| E | 0.5.9 | The tenant provisioning command | backend | M | todo |
| E | 0.5.10 | Invitations | backend | M | todo |
| E | 0.5.11 | Development identities and the synthetic seed | backend + umbrella + frontend | M | todo |
| E | 0.6.1 | The permission catalog is code; the seed cannot crash | backend | M | todo |
| E | 0.6.2 | Deny by default: every route declares its permission | backend | M | todo |
| E | 0.6.3 | Object policies in the use cases | backend | M | todo |
| E | 0.6.4 | Confidential projections, checked against an independent classification | backend | L | todo |
| E | 0.6.6 | Effective permissions for the web app | backend | S | todo |
| E | 0.6.7 | No implicit platform access | backend | S | todo |
| E | 0.6.9 | The two-tenant isolation suite over every route | backend | L | todo |
| F | 0.2.6 | A production build that starts, in a container | backend | M | todo |
| F | 0.7.1 | Audit evidence is append-only in the database | backend | M | todo |
| F | 0.7.2 | Audit inside the business transaction, redacted; a failed audit aborts the change | backend | M | todo |
| F | 0.7.3 | Security events that have no tenant | backend | S | todo |
| F | 0.7.4 | Access audit for confidential reads | backend | S | todo |
| F | 0.7.5 | The transactional outbox and the consumer inbox | backend | M | todo |
| F | 0.7.6 | The worker process, with tenant-safe job discovery | backend + umbrella | L | todo |
| F | 0.7.7 | Idempotency keys for retried commands | backend | M | todo |
| F | 0.7.8 | Transactional email with honest delivery semantics | backend | M | todo |
| F | 0.8.1 | The storage port and an S3 adapter; local-disk storage removed | backend | M | todo |
| F | 0.8.2 | File objects and upload sessions | backend | M | todo |
| F | 0.8.3 | Upload: authorize, presign into quarantine, finalize with content checks | backend | M | todo |
| F | 0.8.4 | Scan, then promote to an immutable version | backend + umbrella | L | todo |
| F | 0.8.5 | Download: version-pinned, authorized, short-lived | backend | S | todo |
| F | 0.10.2 | Redaction by allowlist, proven by canaries | backend | S | todo |
| G | 0.9.5 | Sessions in the browser | frontend | M | todo |
| G | 0.9.6 | The application shell | frontend | M | todo |
| G | 0.11.0 | The foundation gate: what every product feature builds on | umbrella + backend + frontend | M | todo |
| H | 1.1.1 | Users: list, invite, deactivate and change role | backend | L | todo |
| H | 1.1.2 | Tenant settings and private branding | backend + frontend | L | todo |
| H | 1.1.4 | Per-tenant release flags | backend | M | todo |
| H | 1.1.5 | The permission matrix, visible | backend + frontend | M | todo |
| H | 1.1.6 | The user administration workspace | frontend | L | todo |
| H | 1.1.7 | Keycloak Arabic and English journey theme | umbrella + frontend | L | todo |
| I | 1.2.1 | The player record and lifecycle | backend | L | todo |
| I | 1.2.2 | Organizations and club history | backend | L | todo |
| I | 1.2.4 | Player directory, search and filters | backend + frontend | L | todo |
| I | 1.2.5 | Profile completeness by lifecycle stage | backend + frontend | M | todo |
| I | 1.2.8 | Player creation, editing and archive forms | frontend | L | todo |
| I | 1.2.6 | Duplicate detection before player creation | backend + frontend | M | todo |
| I | 1.3.1 | Typed document ownership and legacy URL retirement | backend | L | todo |
| I | 1.3.2 | Document scan operations and recovery | backend + frontend | M | todo |
| I | 1.3.3 | Player images and private media bindings | backend + frontend | L | todo |
| I | 1.3.5 | Shared document upload and history component | frontend | L | todo |
| J | 1.4.8 | Immutable contract versions and file migration | backend | L | todo |
| J | 1.4.1 | Contracts: counterparties, terms and current version | backend | L | todo |
| J | 1.4.2 | The contract state machine | backend | M | todo |
| J | 1.4.3 | Drafting and immutable version commands | backend | L | todo |
| J | 1.4.9 | Ordered approval rounds and immutable decisions | backend | L | todo |
| J | 1.4.5 | Signature evidence under an approved manual policy | backend | L | todo |
| J | 1.4.10 | Draft editor, version history and approval actions | frontend | L | todo |
| J | 1.6.1 | Templated, localized, tracked notifications | backend | L | todo |
| J | 1.4.4 | Expiry monitoring and reminders | backend | L | todo |
| J | 1.4.6 | Termination | backend + frontend | M | todo |
| J | 1.4.7 | The contract workspace | frontend | L | todo |
| J | 1.6.2 | The notification center | backend + frontend | L | todo |
| K | 1.11.1 | Unify prospects with the player lifecycle | backend | L | todo |
| K | 1.11.2 | Control scouting assignments and reassignment | backend | L | todo |
| K | 1.11.3 | Make report review preserve the submitted evidence | backend | L | todo |
| K | 1.11.4 | Provide private watchlists with deliberate sharing | backend | M | todo |
| K | 1.11.5 | Convert an approved prospect through an explicit onboarding action | backend | M | todo |
| K | 1.11.6 | Build the scouting workspace and review experience | frontend | L | todo |
| K | 1.11.7 | Authorize scouting activation with an abuse gate | backend + umbrella | L | todo |
| L | 1.7.1 | Restricted audit search API | backend | M | todo |
| L | 1.7.2 | The permission-filtered player timeline | backend | L | todo |
| L | 1.2.7 | Player 360 | frontend | L | todo |
| L | 1.8.1 | Authorized global search API | backend | L | todo |
| L | 1.8.2 | The home dashboard | backend + frontend | L | todo |
| L | 1.8.3 | The executive summary | backend + frontend | L | todo |
| L | 1.8.4 | Global search interaction | frontend | M | todo |
| L | 1.11.8 | Scouting on the shared surfaces: Player 360 and the home dashboard | backend + frontend | M | todo |
| M | 1.12.1 | The demo dataset: two fictional agencies at work | backend + umbrella | L | todo |
| M | 1.12.2 | The laptop demo: one command, production images | umbrella + backend + frontend | L | todo |
| M | 1.12.3 | Demo acceptance: rehearse the pitch, record the evidence | umbrella + frontend | M | todo |
<!-- plan:milestone:end -->
