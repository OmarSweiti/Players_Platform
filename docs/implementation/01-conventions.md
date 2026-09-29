# Engineering law

The rules every change follows — for HTTP handlers, jobs, scripts, sockets, exports and direct service
calls alike. The code may violate them today (see [`../reference/current-state.md`](../reference/current-state.md));
new code may not. If a rule conflicts with a requirement, record an erratum in the
[master plan](00-master-plan.md#errata-and-concordance); never quietly weaken either.

---

## Invariants

Each names what it serves and what enforces it. An invariant nothing enforces is a wish; each of these
has a test, a database rule or a CI check behind it.

### I-1 · One tenant, enforced by the database
Every business operation runs under a verified, immutable tenant context minted from the session, a
job or an audited platform operation — never from a body, header, query or `localStorage`. Use cases
receive it explicitly and run their database work in `withTenantTransaction`; row-level security is
forced on every tenant-owned table for the non-owner runtime role; repositories still write `tenantId: ctx.tenantId`
into their predicates (the database is the backstop, not the only filter); every foreign key between
tenant-owned tables is composite `(id, tenantId)`. Caches, jobs, object keys, search and sockets carry
the tenant.
*Serves* BR-RULE-01, SYS-TEN-001…007, SR-NFR-SEC-003. *Enforced by* `0.4.3`, `0.4.4`, `0.4.5`, `0.6.9`.

### I-2 · Confidential by policy
Tenant membership, `ADMIN` or `SUPER_ADMIN` alone never grants medical, legal-internal, finance or
identity data. The server evaluates action, relationship, sensitivity, purpose and state, and
**selects** only permitted fields before serialising; confidential data never reaches search, counts,
exports, notifications, caches, files or logs by another path. Missing policy denies.
*Serves* BR-RULE-02, BR-RULE-07, SR-ACL-008. *Enforced by* `0.6.3`, `0.6.4` (an independent field
classification), `0.10.2`.

### I-3 · Authentication is not authorization
The identity provider proves who someone is; Sadara decides what they may do — on every protected
action, on the server. A route declares its permission or is `@Public()`, or the application does not
start. Hidden navigation is UX, never control.
*Serves* SR-AUTH-009, SR-API-001. *Enforced by* `0.6.2`, `0.6.9`.

### I-4 · Workflow transitions only
Contract, approval, signature, legal, enrollment and scouting states change only through commands with
preconditions. Generic create and update DTOs never accept `status`, `role`, `tenantId`, an audit actor, a
computed total or evidence state; a dedicated command (change a role, record signature evidence) takes
exactly the validated input it needs, and the server — never the client — sets the actor and the
resulting state. `SIGNED` means evidence that satisfies an **approved** evidence policy for the exact approved
version — never a timestamp or an upload.
*Serves* BR-RULE-03, BR-RULE-04. *Enforced by* `0.3.2` (mass assignment refused), each domain's
state-machine tests, [`../reference/domain-workflows.md`](../reference/domain-workflows.md).

### I-5 · Atomic, append-only evidence
A sensitive change, its audit record and its outbox event commit in one transaction; if the audit
cannot be written, the change rolls back. Audit and immutable evidence (contract versions, approval
decisions, signature events) cannot be updated, deleted or truncated by any runtime role. Reading
confidential data records an access event before the data is released.
*Serves* BR-RULE-05, SR-AUD-001…005, SR-DB-009. *Enforced by* `0.7.1`–`0.7.4`.

### I-6 · Exact money
`NUMERIC(19,4)` plus a currency whose exponent comes from `CurrencyDefinition`; payable amounts carry no
more decimals than the currency has; amounts travel as decimal strings; no JavaScript `number` or
`parseFloat` ever holds money; rounding is an explicit domain operation.
*Serves* SR-CT-005, SR-TR-006. *Enforced by* `0.4.7`, the `Money` type.

### I-7 · Time has two kinds
Civil values — birthdays, contract and season days — are `DATE` and `YYYY-MM-DD`; instants are
`timestamptz(3)` and ISO-8601 in UTC; schedules also store an IANA zone. Never parse a birthday as
midnight UTC. Rules take an injected clock.
*Serves* SR-CORE-006, UX-007. *Enforced by* `0.4.8`.

### I-8 · Arabic and English are equal
Every screen, state, message, validation error and document template ships in both, together. Layout
uses logical properties only; identifiers, emails and mixed-script numbers are bidi-isolated;
switching language never changes a business value.
*Serves* SR-CORE-007, SR-NFR-I18N-001, UX-008. *Enforced by* `0.9.2`, `0.9.3`, the `ar` and `en`
Playwright projects.

### I-9 · The contract comes first
The committed OpenAPI document is the API; responses are built from response DTOs, never Prisma rows;
routes live under `/api/v1`; errors are RFC 9457 problem details with stable codes; success is wrapped
once. The frontend calls only the client generated from the contract.
*Serves* SR-CORE-002…004, SYS-ARC-003. *Enforced by* `0.3.1`–`0.3.9`, `0.9.4`.

### I-10 · Retries are safe
Commands a client may retry take an idempotency key bound to tenant, actor, operation and request hash.
The outbox delivers at least once; consumers commit each event once. An external outcome that is
unknown is reconciled, never guessed.
*Serves* SR-CORE-010, SYS-ASY-002, SYS-ASY-005. *Enforced by* `0.7.5`–`0.7.7`.

### I-11 · Files are private and pinned
Uploads land in quarantine through short-lived presigned URLs, are checked and scanned, then promoted to
an immutable version; downloads are authorized, short-lived and pinned to the scanned version. No
public URL is stored; no user-supplied name becomes a path.
*Serves* SR-DOC-001…006. *Enforced by* `0.8.1`–`0.8.5`.

### I-12 · The schema moves forward only
Never edit a committed migration (CI refuses it). Change in steps — expand, backfill, validate, switch,
contract — with a preflight before any constraint or data change. Partial indexes, CHECKs, policies,
triggers and grants are hand-written SQL proven by catalog tests. The runtime role cannot migrate.
*Serves* SR-DB-005, SR-NFR-MNT-002. *Enforced by* `protected-paths`, `0.4.1`, `0.4.2`, [migrations](#migrations).

### I-13 · No secrets or personal data in telemetry
Logs allowlist their fields; no body, query string, cookie, token, email, medical, legal or payment
content in any environment. Request ids are generated or validated, never free text.
*Serves* SR-CORE-009. *Enforced by* `0.1.4`, `0.10.2` (canaries).

### I-14 · Work is bounded
Pages hold at most 100 items; uploads, imports and bodies have limits; slow work — media, imports,
reports, bulk notifications — leaves the request path as a job; no network call happens inside a
database transaction.
*Serves* SYS-ASY-001, SR-NFR-PERF-002. *Enforced by* `0.3.5`, `0.7.6`, code review.

### I-15 · Done means proven
A microstep is done when its named tests exist, run and pass in CI and its PR is merged — not when
code exists, a checkbox is ticked or an agent says so. A missing or skipped test fails; an empty
suite fails; "verified locally" is still in progress.
*Serves* SR-NFR-MNT-001. *Enforced by* `0.1.3`, [the microstep definition of done](#microstep-definition-of-done).

---

## Architecture

- **A modular monolith with three processes** from one codebase: `api` (HTTP), `worker` (jobs, from
  `0.7.6`) and `realtime` (sockets, Phase 2). No microservice without a measured need
  ([ADR-0001](../adr/0001-modular-monolith.md)); the details are in
  [`../reference/architecture.md`](../reference/architecture.md).
- **Modules own their tables.** `src/modules/<domain>/{presentation,application,domain,infrastructure}`.
  Another module is reached through its application service or an event — never by importing its
  repository or touching its tables.
- **Layers point inward.** Presentation (controllers, DTOs) → application (use cases, policies) →
  domain (pure rules and types) ← infrastructure (repositories, adapters). A `domain/` folder exists
  when an aggregate has real invariants; there is no ceremony class for a plain record.
- **A use case owns its transaction** and receives the tenant context and the principal as plain
  arguments — never an HTTP request object.
- **The frontend:** routes in `app/[locale]/…`; feature logic in `src/features/<feature>/`; shared UI in
  `src/shared/ui/`; server-only code in `src/server/`. Server state through TanStack Query with keys that
  include the tenant; forms with React Hook Form and zod, the server still validating.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Files | kebab-case; use cases `*.usecase.ts` | `approve-contract.usecase.ts` |
| Types, components | PascalCase | `ContractVersion`, `PlayerCard` |
| Functions, fields | camelCase | `withTenantTransaction`, `signedAt` |
| Constants, enums, error codes | UPPER_SNAKE | `CONTRACT_NOT_APPROVABLE` |
| Prisma models | singular PascalCase, mapped to plural snake_case tables | `model LegalTicket` → `legal_tickets` |
| Permissions | `category.action` keys declared explicitly — never parsed | `contract.approve` |
| Routes | plural kebab-case nouns; actions as sub-resources | `POST /api/v1/contracts/{id}/approvals` |
| Migrations | name the invariant | `…_tenant_rls`, never `…_fix` |
| Tests | the title contains the plan's lower_snake name verbatim | `it('rls_missing_context_denies_reads_and_writes', …)` |
| Commits and PRs | `type(scope): summary  [N.N.N]` | [`03-github-workflow.md`](03-github-workflow.md#titles) |

## Errors

RFC 9457 problem details, one format everywhere, codes stable forever: the table of statuses and codes
is in [`../reference/api.md`](../reference/api.md). A thrown plain `Error` is a bug. Never catch broadly
and return an empty success. `202` means a job was accepted, not that its effect happened.

## Testing

| Layer | Runner | Proves | Lives in |
|---|---|---|---|
| Unit (backend) | Jest | pure rules: state transitions, policies, money, dates, normalisation — property tests where inputs vary | beside the code: `backend/src/**/*.spec.ts` |
| Integration | Jest on real PostgreSQL 18 | constraints, RLS, grants, triggers, transactions, concurrency, audit, outbox, storage adapters — **as the runtime role** | `backend/test/**/*.integration-spec.ts` |
| API | Jest + supertest | contracts, status codes, problem details, authorization, the isolation suite | `backend/test/**/*.e2e-spec.ts` |
| Unit (frontend) | Vitest + Testing Library | components, hooks, formatting, catalogs | beside the code: `frontend/src/**/*.test.{ts,tsx}` |
| Browser | Playwright (`ar`, `en`) + axe | the critical journeys, RTL, accessibility, session behaviour | `frontend/tests/**/*.spec.ts` |

The globs are disjoint on purpose: each runner finds only its own files, and a file in the wrong place
runs nowhere — so put it where the table says.

Rules:

- **Tests belong to features, not to plan steps.** A microstep lists exact test names; the test title
  contains the name verbatim so the plan check can find it. Renumbering the plan never moves a test.
- **Two tenants, always.** Every authorization and data test uses at least two tenants and a same-tenant
  member who must be refused.
- **Falsify, don't mirror.** A mocked repository that received `tenantId` proves nothing about
  isolation; confidentiality is asserted against an independent classification, not the code's markers.
- **Concurrency with barriers**, never with sleeps; property tests keep their failing seeds; the clock
  and ids are injected.
- **Coverage is a diagnostic, not the gate.** The gate is every named test passing, none skipped.
- No real personal data in tests, fixtures, seeds or screenshots — synthetic data on `.test` domains.

## Microstep definition of done

- [ ] Every dependency is `done`; every OPEN default it touches is followed or settled.
- [ ] The behaviour exists end to end in the files named, including DTOs, translations, policies, audit,
      migration and failure states where they apply.
- [ ] Every named test exists, runs and passes in CI; the Verify command's output is in the PR; the
      Done-when sentence is true.
- [ ] `just check` and `just pre-push` pass; migrations replay with no drift when data changed; the
      committed OpenAPI document matches the code when the API changed.
- [ ] The PR is merged through the flow, titled with the microstep ID, with no assistant attribution.
- [ ] The umbrella moves the pins and marks the step `done` with the PR URL; `just plan` regenerated the
      frontier, catalog and traceability.

## Budgets

Proposals to measure, except where a requirement sets the number.

| Surface | Budget | Measured at |
|---|---|---|
| Simple API read or write | p95 ≤ 500 ms, errors < 1%, under the capacity envelope (SR-NFR-PERF-001) | `1.10.6` |
| Dashboard or report request | p95 ≤ 2 s to start; large results as a `202` job | `1.10.6` |
| Browser journeys | LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 on a declared mid-range phone and network | `1.10.6` |
| Outbox | p95 from commit to dispatch ≤ 60 s; alert when the oldest pending event is older than 5 min | `1.10.4` |
| Database pool | alert above 80% sustained use or on any acquisition timeout (today 10 connections, `prisma.service.ts:26`) | `1.10.4` |
| Availability | 99.9% monthly target, with a defined maintenance window (SR-NFR-REL-001) — a target, not a measurement | `1.10.9` |
| Recovery | MVP: RPO ≤ 24 h, RTO ≤ 8 h, keys and objects included | `1.10.5` |

Security denials tolerate **zero** failures; no performance work may relax them.

## Migrations

1. Always a **new** migration; the six historical ones are immutable.
2. Run `just preflight` before a constraint or data migration; a non-zero report blocks it until the
   owner approves a correction. Never delete rows to make a constraint pass.
3. Large changes go expand → backfill → validate (`NOT VALID` then `VALIDATE`) → switch → contract, each
   stage deployable with the previous application version.
4. Anything Prisma cannot model — partial indexes, CHECKs, RLS policies, triggers, grants — is written in
   the migration SQL, commented in `schema.prisma`, and asserted by a catalog test; Prisma's drift check
   neither sees nor protects these objects ([ADR-0017](../adr/0017-sql-managed-database-objects.md)).
5. A new tenant-owned table ships with its RLS policy, grants, composite keys and tests in the same
   migration.
6. `just migrations` (a throwaway PostgreSQL 18, full replay, no drift) must pass before a PR.

## Internationalisation

Catalogs in `messages/{ar,en}.json` with identical keys (a test checks); ICU plurals, which Arabic needs;
no concatenated sentence fragments; the backend returns codes, the frontend translates them;
`Intl` for numbers, dates and money; Western digits for identifiers and amounts in both locales unless
the agency decides otherwise. [ADR-0008](../adr/0008-i18n.md), [`../reference/ui-ux.md`](../reference/ui-ux.md).

## Security, in one page

The model, the threat table and the role matrix are in
[`../reference/security-privacy.md`](../reference/security-privacy.md). The rules that apply to every
change: tenant from the session only (I-1); policy before data (I-2, I-3); no secrets in code, logs or
fixtures (I-13); dependencies pinned, reviewed and audited by CI; a found secret is rotated first and
removed second; nothing is published that the owner has not approved.
