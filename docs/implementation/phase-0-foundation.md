# Phase 0 — Foundation & hardening

> **Exit:** nothing that exists can leak across tenants or be abused; sign-in works end to end through
> the identity provider; and every later feature is built on rails — tenant transactions under
> row-level security, authorization, atomic audit, durable work, a private file pipeline, the API
> contract and the bilingual shell are in place, tested and green in CI.

**Effort:** 82 microsteps — 22 S, 49 M, 11 L — **328–656 engineering hours** before the 30% reserve
(the size weights are ceilings); [`00-master-plan.md`](00-master-plan.md#effort-model) turns that into a
forecast and recalibrates it from measured hours after the first five steps. No new product
features: the demonstrations are about what can no longer go wrong.
**Baseline:** [`../reference/current-state.md`](../reference/current-state.md) — what the code does today,
verified on 28 September 2026. Every defect listed there names its owning microstep below.

**Why this order.** The local sign-in does not work today and hides exploitable defects behind the
failure, so it is **retired first** (group 0.1), not repaired; identity is rebuilt on an external
provider (0.5). The database learns to enforce tenancy (0.4) before identity and every feature table
arrive, so everything after it is born under row-level security. Money, dates and identifiers are cheap
to fix now and painful once production rows exist.

---

## Group dependency graph

```text
0.1 adoption & containment ──┐        (0.1.1–0.1.3 land first: this documentation set)
0.2 runtimes & harnesses ────┼──→ 0.3 API platform ──┐
                              └──→ 0.4 database integrity & tenant transactions ──┬──→ 0.5 identity & sessions ──→ 0.6 authorization
                                                                                   └──→ 0.7 audit & durable work ──→ 0.8 file pipeline
0.9 bilingual browser foundation: 0.9.1–0.9.3 after 0.2.4; 0.9.4 after backend 0.3.9; 0.9.5 after backend 0.5.6 and 0.6.6
0.10 operational proof: after 0.3, 0.7 and 0.8 ──→ 0.11 Phase-0 gate (after everything)
```

**Build order:** `0.1.1–0.1.3` (this documentation set) → `0.2.1`, `0.2.2`, `0.2.3` → `0.1.5`,
`0.1.4`, `0.1.8`, `0.4.1`, `0.1.6`, `0.1.7` → the rest of `0.2` → `0.3` → `0.4` → `0.5` → `0.6` →
`0.7` → `0.8` → `0.10` → `0.11`. Group 0.9 runs beside the backend once its dependencies land, and
`0.2.4`, `0.2.5`, `0.9.1` have none — good first sideways steps. The per-step **Depends on** lines are
authoritative; this order is one valid path through them.

**Repos:** a microstep that touches two repositories is two PRs, backend first, both titled with the
same microstep ID; the umbrella records both when it moves the pins. **Every new tenant-owned table
after `0.4.5` ships with its row-level-security policy, grants and tests in the same migration.**

---

## Group 0.1 — Adoption and containment

### 0.1.1 — The documentation set lands; the legacy documents are retired
**Repo:** umbrella + backend + frontend · **Size:** M · **Depends on:** — · **Requirements:** —
**Files:** umbrella `docs/**`, `README.md` (new), `CONTRIBUTING.md`, `.github/labeler.yml`,
`.github/ISSUE_TEMPLATE/config.yml`; the 13 root guides and `.lingma/` (delete); backend
`BACKEND_IMPLEMENTATION_STANDARDS.md`, `build_output.txt` (delete), `README.md` (rewrite),
`.github/ISSUE_TEMPLATE/config.yml`; frontend `FEATURE_IMPLEMENTATION_TEMPLATE.md`,
`FRONTEND_IMPLEMENTATION.md`, `QUICK_START.md` (delete), `README.md` (rewrite), `.github/ISSUE_TEMPLATE/config.yml`
This `docs/` tree lands and the 25 legacy documents are retired after their valid content has been
merged, each recorded with its last commit in [`../reference/consolidation.md`](../reference/consolidation.md).
The live references to them are repaired in the same PRs: the "plan" link in each repository's issue
template, the umbrella's `CONTRIBUTING.md:10`, and the `area: plan` label globs.
**Verify:** `git ls-files | grep -E 'AUTH_|_GUIDE|IMPLEMENTATION_|QUICK_|SWAGGER_|FEATURE_|\.lingma|build_output'` prints nothing in any of the three repositories
**Done when:** no legacy document remains in any repository, no file links to one, and each is
recoverable from the commit the consolidation map names.

### 0.1.2 — Agent entry files and scoped rules
**Repo:** umbrella + backend + frontend · **Size:** S · **Depends on:** `0.1.1` · **Requirements:** —
**Files:** umbrella `AGENTS.md`, `CLAUDE.md`, `.claude/rules/{backend,frontend,migrations,security}.md`;
backend `AGENTS.md`, `CLAUDE.md` (new); frontend `AGENTS.md`, `CLAUDE.md`
One authority, reachable from anywhere: the umbrella `AGENTS.md` (Codex and other agents) and
`CLAUDE.md` (Claude) route to the plan; path-scoped rules load only for the files being changed, and
`security.md` always loads. Each application's `AGENTS.md` routes to the umbrella in one hop; the
frontend keeps the Next.js block — "This is NOT the Next.js you know … read `node_modules/next/dist/docs/`"
— byte for byte.
**Verify:** `python3 scripts/check-plan.py` (the agent files are link-checked)
**Done when:** an agent opened in any one of the three repositories reaches the plan, the frontier and
the rules for the files it is changing without searching.

### 0.1.3 — The plan checks itself in CI
**Repo:** umbrella · **Size:** M · **Depends on:** `0.1.1` · **Requirements:** —
**Files:** `scripts/check-plan.py` (new), `justfile` (`check` runs it; `plan` regenerates),
`.github/workflows/ci.yml` (a step in the required `test` job), `scripts/test-policy.sh` (the self-test)
`check-plan.py` parses the phase files and verifies: unique microstep IDs, dependencies that exist and
form no cycle, one `progress.md` row per step with a valid status, `done` only with a PR for **every**
repository the step touches and all dependencies done — and, in CI, each PR verified as merged with its
merge commit inside the pinned history — every named test **declared (not merely mentioned) and not
skipped**, nor inside a skipped suite, in the pinned application commit for a `done` step, every requirement ID owned by a step or explicitly deferred, the frozen requirement
checksums, every relative link and anchor, and the freshness of the generated blocks (frontier, test
catalog, traceability). Standard library only; it fetches a pinned application commit only when a
`done` step needs it.
**Tests:** `a_missing_progress_row_is_refused` · `a_done_step_without_a_merged_pr_is_refused` · `a_two_repository_step_needs_a_pr_per_repository` · `an_unmerged_pr_is_refused` · `a_pr_outside_the_pinned_history_is_refused` · `a_done_step_with_an_undone_dependency_is_refused` · `a_done_step_whose_named_test_is_missing_is_refused` · `a_name_only_in_a_comment_is_refused` · `a_skipped_named_test_is_refused` · `a_skipped_suite_is_refused` · `an_unowned_requirement_is_refused` · `an_edited_frozen_requirement_is_refused` · `a_broken_link_or_anchor_is_refused`
**Verify:** `python3 scripts/check-plan.py --self-test && just check`
**Done when:** CI's required `test` job fails on any disagreement between plan, progress, requirements
and links, and `guards` proves the checker still refuses each case.

### 0.1.4 — Stop secrets and personal data reaching logs and error responses
**Repo:** backend + frontend · **Size:** M · **Depends on:** `0.2.3`, `0.2.4` · **Requirements:** SR-CORE-009
**Files:** backend `src/infrastructure/mail/mail.service.ts`, `src/common/interceptors/logging.interceptor.ts`,
`src/common/filters/http-exception.filter.ts`, every use case that logs an email; frontend
`src/shared/lib/api-client.ts`; backend `test/security/log-leaks.e2e-spec.ts` (new)
Today the mail stub writes whole emails — raw reset and verification links included — to the debug log
in every environment (`mail.service.ts:21–22`); the access log records full URLs, so `?token=…` lands in
it (`logging.interceptor.ts:24`); unhandled exceptions are `console.error`'d raw and Prisma errors echo
argument values (`http-exception.filter.ts:41`); 25 log lines identify users by email; the web client
logs request bodies, passwords included, in development (`api-client.ts:64–70`). Remove every one: log
the route template, never the URL; log exceptions through the logger with values stripped; identify
users by id, never email; never log a body. The allowlist-based logger and its canaries follow in
`0.10.1`–`0.10.2`.
**Tests:** `no_log_line_contains_a_token_or_password` · `urls_are_logged_without_query_strings` · `the_web_client_never_logs_a_request_body`
**Verify:** `just test-e2e -- test/security/log-leaks.e2e-spec.ts` (backend) · `npx vitest run src/shared/lib` (frontend)
**Done when:** a request carrying a token in its query and a password in its body leaves no trace of
either in the backend log or the browser console, and no log line contains an email address.

### 0.1.5 — Refuse to boot without real configuration
**Repo:** backend · **Size:** S · **Depends on:** `0.2.3` · **Requirements:** —
**Files:** `src/config/env.schema.ts` (new), `src/config/*.ts`, `src/main.ts`, `src/app.module.ts`,
`src/modules/auth/auth.module.ts`, `src/modules/auth/infrastructure/strategies/jwt.strategy.ts`, `.env.example` (new)
The signing key falls back to the literal `'default-secret'` (`auth.module.ts:35`, `jwt.strategy.ts:36`)
— anyone could forge a token — and Swagger is served whenever `NODE_ENV` is unset (`main.ts:54`).
Validate the environment at boot with one zod schema: every secret required, no defaults, `NODE_ENV`
required, Swagger only when it is exactly `development`. No `process.env` outside `src/config/`. A
failure names the variables, never their values. `.env.example` documents every variable (the list is in
`current-state.md` §1). The JWT keys disappear with `0.1.6`; the schema is what later identity, session
and storage settings join.
```ts
export const Env = z.object({ NODE_ENV: z.enum(['development', 'test', 'staging', 'production']), /* … */ });
export type Env = z.infer<typeof Env>;
```
**Tests:** `boot_fails_without_a_required_secret` · `boot_errors_name_the_variable_but_not_its_value` · `swagger_is_served_only_in_development`
**Verify:** `npx jest src/config && ! grep -rn "default-secret" src && test -z "$(grep -rln 'process\.env' src | grep -v '^src/config/')"`
**Done when:** the API refuses to start with any required variable missing, and nothing outside
`src/config/` reads the environment.

### 0.1.6 — Retire the local credential system
**Repo:** backend · **Size:** L · **Depends on:** `0.2.3`, `0.4.1` · **Requirements:** SR-AUTH-005, SR-AUTH-006, SR-DB-010
**Files:** `src/modules/auth/**` (the controller's 16 routes, the use cases, DTOs, strategies and guards — delete),
`src/common/guards/tenant.guard.ts`, `src/modules/auth/config/throttler-config.module.ts` (delete),
`src/common/guards/session.guard.ts` (new placeholder), `src/app.module.ts`, `prisma/schema.prisma`,
migration `…_retire_local_credentials`, `test/auth/retirement.e2e-spec.ts` (new)
The local sign-in does not work end to end and carries more than a dozen verified defects —
self-registration with any role, `'default-tenant'` in a UUID column, refresh that reads a body the
browser never sends, placeholder sessions, 2FA that is never asked for and stored in plaintext,
verification tokens stored raw, a lockout that never resets ([`current-state.md`](../reference/current-state.md#defects-each-with-its-owner)
A-1…A-22). Identity moves to an external provider (group 0.5,
[ADR-0002](../adr/0002-identity-oidc.md)), so these are **removed, not repaired**: delete every local
credential route, use case, DTO, strategy and guard, and replace the global JWT guard with a placeholder
`SessionGuard` that answers `401` on every non-public route until `0.5.6` supplies sessions. Nothing that
works today stops working — sign-in fails today. The migration drops the credential columns
(`passwordHash`, `twoFASecret`, `is2FAEnabled`, reset and verification tokens and expiries,
`failedLoginAttempts`, `lockedUntil`, `passwordChangedAt`, `emailVerifiedAt`) — **only after** the
`0.4.1` preflight reports no real account in the target database; if it reports one, stop and raise the
OPEN item on existing data.
**Tests:** `no_local_credential_route_remains` · `protected_routes_refuse_without_a_session` · `credential_columns_are_gone`
**Verify:** `just test-e2e -- test/auth/retirement.e2e-spec.ts && just migrations`
**Done when:** the route inventory (read from controller metadata, not from a guessed URL) contains no
register, login, refresh, password, verification or 2FA route; every non-public route answers `401`;
and no credential column exists.

### 0.1.7 — Retire the local sign-in pages
**Repo:** frontend · **Size:** S · **Depends on:** `0.2.4` · **Requirements:** —
**Files:** `app/(auth)/register/**`, `app/(auth)/forgot-password/**`, `app/(auth)/reset-password/**`,
`app/(auth)/verify-email/**`, `app/(dashboard)/settings/2fa/**` (delete), `app/(auth)/login/page.tsx`,
`src/features/auth/**`, `tests/e2e/retirement.spec.ts` (new)
The pages the backend no longer serves go too, and with them three defects: the login form sends
`rememberMe`, which the API rejects (`app/(auth)/login/page.tsx:16`); the 2FA page invents "backup codes"
in the browser that nothing stores (`settings/2fa/page.tsx:59`); the reset form's `.refine` returns an
object on mismatch, which counts as valid (`reset-password-content.tsx:22–29`). The login page becomes a
single "Sign in" entry, wired to the provider in `0.9.5`; the hook that waits for unreadable cookies
(`use-auth.ts:86–88`) is deleted.
**Tests:** `no_route_renders_a_password_field` · `no_page_generates_security_codes`
**Verify:** `npx playwright test tests/e2e/retirement.spec.ts`
**Done when:** no page collects a password or produces recovery codes, and the build is green.

### 0.1.8 — Quarantine unfinished modules behind server-side flags
**Repo:** backend · **Size:** S · **Depends on:** `0.2.3` · **Requirements:** SR-MED-007
**Files:** `src/common/feature-flags/feature-gate.guard.ts` (new), `src/config/env.schema.ts`,
`src/modules/medical/medical.module.ts`, `src/modules/scouting/scouting.module.ts`, `test/platform/feature-flags.e2e-spec.ts` (new)
Medical and scouting are partial, carry verified defects (fixed in `0.6.8`) and are rebuilt in Phases 2
and 3. Until then `FEATURE_MEDICAL` and `FEATURE_SCOUTING` are **off in every environment unless
explicitly set**, and a controller-level gate answers `404` before any repository is touched. A client
navigation flag is never the control. Per-tenant flags replace these in `1.1.4`.
**Tests:** `medical_routes_are_not_found_when_disabled` · `scouting_routes_are_not_found_when_disabled` · `a_disabled_module_never_reaches_its_repository`
**Verify:** `just test-e2e -- test/platform/feature-flags.e2e-spec.ts`
**Done when:** with the flags unset, every medical and scouting route answers `404` and no medical or
scouting query runs.

---

## Group 0.2 — Reproducible runtimes and test harnesses

### 0.2.1 — The local stack: PostgreSQL 18, S3-compatible storage, Valkey, ClamAV, Mailpit, Keycloak
**Repo:** umbrella · **Size:** M · **Depends on:** — · **Requirements:** SR-DB-001
**Files:** `infra/compose.yaml` (new), `infra/postgres/init/` (new), `infra/keycloak/` (new), `infra/proxy/Caddyfile` (new),
`justfile` (`up`, `down`, `logs`, `reset`, `trust-dev-ca`, `dev-ca-path`), `.env.example` (new)
One command brings up everything the applications need: PostgreSQL 18, Valkey, an S3-compatible object
store that supports presigned URLs **and bucket versioning** (chosen and pinned in this step), ClamAV,
Mailpit, Keycloak, and **a local HTTPS proxy** (Caddy, `tls internal`) that serves
`https://sadara.localhost` and `https://northwind.localhost` exactly as production will be routed — `/` to
the web app, `/api/` to the API — so the `__Host-` session cookie is tested as specified, not weakened;
`just trust-dev-ca` trusts the proxy's local certificate authority. Every image is pinned **by digest**, every service has a health check and a named
volume, and Keycloak runs `start-dev` only here — development mode has insecure defaults and never
leaves an isolated machine. `just reset` destroys the local volumes and refuses any other target. Tenant
hosts resolve through `*.localhost`.
**Verify:** `just up && docker compose -f infra/compose.yaml ps --format json | jq -se 'all(.[]; .Health == "healthy")'`
**Done when:** a fresh clone brings every service up healthy with `just up`, `https://sadara.localhost`
reaches the web app and `https://sadara.localhost/api/` the API, and every image reference is a digest.

### 0.2.2 — PostgreSQL 18 in CI and in the replay recipe
**Repo:** backend · **Size:** S · **Depends on:** — · **Requirements:** SR-DB-005
**Files:** `.github/workflows/ci.yml`, `justfile` (`migrations`)
CI's migration replay and `just migrations` move from `postgres:17` — introduced with the delivery flow
on 28 September 2026 (`68be90a`), not a qualified choice — to `postgres:18`, pinned by digest. The
qualification is already on record: PostgreSQL 18.6 with Prisma 7.10.0 applied all six migrations and
`prisma migrate diff --exit-code` reported no difference ([ADR-0013](../adr/0013-postgresql-18.md)).
**Verify:** `just migrations`
**Done when:** CI replays every migration on PostgreSQL 18 with no drift on every pull request.

### 0.2.3 — The API test harness on a real database
**Repo:** backend · **Size:** M · **Depends on:** `0.2.2` · **Requirements:** TEST-001, TEST-002
**Files:** `jest.config.ts` (new), `test/jest-e2e.json`, `test/harness/{app,db,fixtures}.ts` (new),
`justfile` (`test-int`, `test-e2e`), `package.json`; `src/app.controller.ts`, `src/app.service.ts`,
`src/app.controller.spec.ts`, `test/app.e2e-spec.ts` (delete)
Jest projects with disjoint globs: `unit` (`src/**/*.spec.ts`), `integration`
(`test/**/*.integration-spec.ts`) and `e2e` (`test/**/*.e2e-spec.ts`). The harness boots the
app per file against `DATABASE_URL_TEST`, applies migrations into a fresh schema per run
(`sadara_test_<random>`), and creates tenants and members **directly** — never through the seed. Once
`0.4.2` lands, tests connect as the runtime role, never the owner. The starter `AppController` (not even
registered) and the e2e test that expects "Hello World" are deleted. `--passWithNoTests` is forbidden.
```ts
export async function bootApp(): Promise<{ app: INestApplication; http: SuperTest<Test> }>;
export async function createTenant(opts?: { slug?: string }): Promise<Tenant>;
export async function createMember(tenant: Tenant, role: UserRole): Promise<User>;
```
**Tests:** `harness_boots_against_an_isolated_schema` · `two_harness_runs_never_share_a_schema`
**Verify:** `just test-int && just test-e2e`
**Done when:** both suites run green against the compose PostgreSQL, a concurrent second run uses a
different schema, and an empty suite fails.

### 0.2.4 — The web test harness: Vitest, Testing Library, MSW, Playwright in Arabic and English, axe
**Repo:** frontend · **Size:** M · **Depends on:** — · **Requirements:** TEST-009
**Files:** `vitest.config.ts`, `playwright.config.ts`, `tests/setup.ts`, `tests/msw/` (new), `justfile`, `package.json`
Vitest with Testing Library in jsdom and MSW for API responses, on `src/**/*.test.{ts,tsx}`; Playwright
on `tests/**/*.spec.ts` with an `ar` and an `en` project and axe on every page it visits — disjoint globs,
so neither runner picks up the other's files; both wired into `just check` and CI's `test` job.
**Tests:** `the_unit_runner_renders_a_component` · `each_locale_project_opens_the_sign_in_page`
**Verify:** `just check`
**Done when:** CI runs both runners on every pull request and an empty suite fails.

### 0.2.5 — Lint and format gates in both applications
**Repo:** backend + frontend · **Size:** M · **Depends on:** — · **Requirements:** —
**Files:** backend `.prettierrc`, `eslint.config.mjs`, `.git-blame-ignore-revs`, `justfile`, `.github/workflows/ci.yml`;
frontend `eslint.config.mjs`, `justfile`, `.github/workflows/ci.yml`
Backend: Prettier over `src` and `test` in one formatting-only commit (listed in `.git-blame-ignore-revs`),
then the remaining ESLint errors (748 problems today); frontend: the 21 problems (13 errors). Then
`prettier --check` and `eslint --max-warnings=0` join `just check` and CI's `test` job in both.
**Verify:** `just check` in each application
**Done when:** CI fails on any new lint or formatting problem in either application.

### 0.2.6 — A production build that starts, in a container
**Repo:** backend · **Size:** M · **Depends on:** `0.1.5`, `0.3.7` · **Requirements:** TEST-006
**Files:** `tsconfig.build.json`, `package.json`, `Dockerfile` (new), `.dockerignore` (new),
`scripts/smoke-start.sh` (new), `.github/workflows/ci.yml`
`npm run start:prod` runs `node dist/main`, but the build emits `dist/src/main.js` because
`prisma.config.ts` sits in the compilation root — fix the root so the entry point is where the script
looks. A multi-stage `Dockerfile` builds a non-root image; CI builds it, scans it for known
vulnerabilities, and runs the smoke test against it.
**Tests:** `the_built_image_answers_liveness`
**Verify:** `npm run build && bash scripts/smoke-start.sh`
**Done when:** the image starts as a non-root user and answers `/health/live`, and CI fails on a critical
image vulnerability.

### 0.2.7 — Declared dependencies only; one naming scheme
**Repo:** backend + frontend · **Size:** S · **Depends on:** `0.1.6`, `0.1.7`, `0.2.5` · **Requirements:** —
**Files:** both `package.json` / `package-lock.json`; backend use-case files; `src/main.ts`,
`src/database/seed.ts`; frontend `app/layout.tsx`
Declare what the code imports (`@nestjs/mapped-types` in four DTOs; `dotenv` in `prisma.config.ts:3`) and
remove what nothing imports — backend `socket.io`, `@nestjs/websockets`, `@nestjs/platform-socket.io`,
`redis`, `ioredis`, `multer`, `@types/multer`, `dayjs`, and the credential libraries `0.1.6` orphaned;
frontend 12 of 27 dependencies (seven Radix packages, `@tsparticles/*`, `framer-motion`, `date-fns`,
`zustand`). A dependency returns with the step that first imports it. Every `@nestjs/*` package sits on
**one** major version — today `@nestjs/event-emitter` is on 12 (its peers accept 11) while the rest of the
family is on 11; `0.2.9` moves the family to 12 together. Use cases are `*.usecase.ts` (the
11 `*.use-case.ts` files are renamed in one mechanical commit); the product is **Sadara** everywhere —
the API title (`main.ts:56–57`), the page title (`app/layout.tsx:18`) and the packages (`backend`,
`players_platform_frontend` → `sadara-backend`, `sadara-frontend`).
**Verify:** `npx depcheck` in each application · `test -z "$(find src -name '*.use-case.ts')"`
**Done when:** `depcheck` reports nothing in either application, one use-case suffix remains, and no
user-visible string names the old product.

### 0.2.8 — Integration and end-to-end tests in CI
**Repo:** backend · **Size:** S · **Depends on:** `0.2.3` · **Requirements:** SR-NFR-MNT-001
**Files:** `.github/workflows/ci.yml`
The required `test` job runs the integration and e2e projects against PostgreSQL 18 and Valkey service
containers, in addition to the unit tests.
**Verify:** CI on the pull request
**Done when:** a deliberately failing e2e test turns the required `test` check red.

### 0.2.9 — NestJS 12, TypeScript 6 and an ES-module test setup, together
**Repo:** backend · **Size:** L · **Depends on:** `0.2.3`, `0.2.5`, `0.2.7` · **Requirements:** SR-NFR-MNT-002
**Files:** `package.json`, `package-lock.json`, `tsconfig.json`, `jest.config.ts`, `test/jest-e2e.json`, `.github/dependabot.yml`
Dependabot offered the NestJS 12 family, `bullmq` 6, TypeScript 7 and ESLint 10 on 28 September; they were
merged with failing checks and reverted (backend #26), because NestJS 12 ships as ES modules and the Jest
setup cannot load them. This step makes the move deliberately and in one piece: every `@nestjs/*` package
to 12 with `bullmq` 6; TypeScript 6 — TypeScript 7 waits until `ts-jest` and typescript-eslint support it;
the TypeScript 6 settings decided explicitly (whether to turn `strict` on, `types`, `rootDir`); a test
runner that loads ES-module packages; then the Dependabot holds on those majors are lifted.
**Tests:** `the_app_boots_on_nestjs_12` · `the_test_runner_loads_es_module_packages`
**Verify:** `rm -rf node_modules && npm ci && just check && just test-e2e`
**Done when:** every `@nestjs/*` package is on 12, TypeScript is on 6, CI is green, and `dependabot.yml`
no longer holds those majors.

---

## Group 0.3 — The API platform

*Today controllers build `{ statusCode, data }` bodies by hand (38 of them), the response wrapper is
registered twice (`main.ts:19`, `app.module.ts:54`), a missing record comes back as HTTP 200 with a 404
inside (`medical.controller.ts:123, 241`, `scouting.controller.ts:116`), validation runs twice with two
option sets, and 46 plain `Error` throws become 500s. One of each, registered once:
[`../reference/api.md`](../reference/api.md) is the contract.*

### 0.3.1 — One error format: RFC 9457 problem details
**Repo:** backend · **Size:** M · **Depends on:** `0.2.3` · **Requirements:** SR-CORE-003
**Files:** `src/common/filters/problem-details.filter.ts` (replaces `http-exception.filter.ts`),
`src/common/errors/{error-codes,domain-error}.ts` (new), every use case that throws a plain `Error`,
`test/platform/errors.e2e-spec.ts` (new)
Every error is `application/problem+json` — `type`, `title`, `status`, `code`, `message`, `requestId`,
`fieldErrors` (an empty array when no field is implicated) — registered once in the bootstrap shared by production and tests. The 46 plain
`throw new Error(…)` in the modules become typed domain errors; Prisma `P2002` maps to `409 CONFLICT`,
`P2025` to `404 NOT_FOUND`, `P2003` to `409 CONFLICT`; anything unknown to `500 INTERNAL_ERROR`
with nothing internal in it. Codes are stable forever and clients branch on `code`, never on `message`.
**Tests:** `validation_errors_list_their_fields` · `unknown_errors_leak_nothing` · `every_error_carries_the_request_id` · `a_missing_record_is_a_404_not_a_500`
**Verify:** `just test-e2e -- test/platform/errors.e2e-spec.ts && ! grep -rn "throw new Error(" src/modules`
**Done when:** a thrown `Error('boom at /srv/secret')` returns `INTERNAL_ERROR` without the path, with a
request id equal to the response header, and no module throws a plain `Error`.

### 0.3.2 — Strict validation, registered once
**Repo:** backend · **Size:** S · **Depends on:** `0.3.1` · **Requirements:** SR-CORE-005, SR-API-003
**Files:** `src/main.ts`, `src/app.module.ts`, `src/common/pipes/validation.pipe.ts`, query DTOs,
`test/platform/validation.e2e-spec.ts` (new)
One global pipe — `whitelist`, `forbidNonWhitelisted`, `transform`, `forbidUnknownValues`, trimmed
strings, bounded string and array lengths — instead of today's two (`main.ts:45` and `APP_PIPE` in
`app.module.ts:56`, with different options). Every query is a typed DTO (the medical controller takes
`@Query() query: any`, `medical.controller.ts:65, 92, 208`); every path id passes `ParseUUIDPipe`; an
empty `PATCH` is a `400`.
**Tests:** `an_unknown_property_is_refused` · `a_malformed_uuid_is_a_validation_error` · `an_unknown_query_parameter_is_refused`
**Verify:** `just test-e2e -- test/platform/validation.e2e-spec.ts`
**Done when:** a body carrying an extra `tenantId` or `role` is refused with `VALIDATION_FAILED`, and
exactly one validation pipe is registered.

### 0.3.3 — Versioned routes under /api/v1
**Repo:** backend + frontend · **Size:** S · **Depends on:** `0.3.1` · **Requirements:** —
**Files:** backend `src/main.ts`, `src/config/app.config.ts`, `test/platform/versioning.e2e-spec.ts` (new); frontend API base URL
URI versioning makes every route `/api/v1/…` (today `/api/…`, `main.ts:40–41`); health stays unversioned.
**Tests:** `routes_are_served_under_v1`
**Verify:** `just test-e2e -- test/platform/versioning.e2e-spec.ts`
**Done when:** no route answers outside `/api/v1` except the health endpoints.

### 0.3.4 — One success envelope, registered once
**Repo:** backend · **Size:** S · **Depends on:** `0.3.1` · **Requirements:** SYS-ARC-003
**Files:** `src/common/interceptors/envelope.interceptor.ts` (replaces `transform.interceptor.ts`),
`src/main.ts`, `src/app.module.ts`, the medical and scouting controllers, `test/platform/responses.e2e-spec.ts` (new)
Success is `{ data }` — collections `{ data, page }` (`0.3.5`) — applied by one interceptor registered in
one place. Delete the second registration, the 38 hand-built `{ statusCode, data }` bodies and every
"not found" returned as a 200. Responses are built from response DTOs, never Prisma rows, so a schema
refactor is not an API change. `204`, downloads and errors are never wrapped.
**Tests:** `a_single_resource_is_wrapped_once` · `a_not_found_is_never_a_200` · `timestamps_are_iso_utc`
**Verify:** `just test-e2e -- test/platform/responses.e2e-spec.ts && ! grep -rn "statusCode: HttpStatus" src/modules`
**Done when:** every existing route answers `{ data }` exactly once and no success body carries an error.

### 0.3.5 — Cursor pagination and allowlisted filters
**Repo:** backend · **Size:** M · **Depends on:** `0.3.2`, `0.3.4` · **Requirements:** SR-CORE-004, SR-API-004
**Files:** `src/common/pagination/**`, `src/common/filtering/**` (new)
Keyset pagination over `(createdAt, id)`: `limit` default 25, maximum 100 — above it is a `400`, never a
silent cap. The cursor is opaque and bound to tenant, sort and filter hash, so a cursor from another
query is `INVALID_CURSOR`. Filters and sort fields come from a per-endpoint allowlist; no totals unless
an endpoint needs one, and then counted within the caller's visible scope.
```ts
export interface Page<T> { data: T[]; page: { nextCursor: string | null; hasMore: boolean } }
export function paginate<T>(query: PageQuery, fetch: (args: KeysetArgs) => Promise<T[]>): Promise<Page<T>>;
```
**Tests:** `a_limit_above_100_is_refused` · `cursors_stay_stable_under_inserts` · `a_cursor_from_another_query_is_refused` · `an_unlisted_filter_is_refused`
**Verify:** `npx jest src/common/pagination src/common/filtering`
**Done when:** the four tests pass.

### 0.3.6 — Optimistic concurrency: revisions, ETag, If-Match
**Repo:** backend · **Size:** M · **Depends on:** `0.3.4` · **Requirements:** SR-API-005
**Files:** `src/common/concurrency/**` (new), `test/platform/concurrency.e2e-spec.ts` (new)
Editable aggregates carry `revision Int @default(1)`, added by each domain step as it builds its tables.
The helper returns a strong, opaque `ETag` bound to the representation, its revision and the caller's
projection, requires `If-Match` on edits and transitions — missing is
`428 PRECONDITION_REQUIRED`, stale is `412 REVISION_MISMATCH` — and updates `WHERE id, tenantId, revision`
with an atomic increment. Immutable records (versions, decisions) accept no `PATCH` at all.
**Tests:** `a_stale_if_match_is_refused_with_412` · `a_missing_if_match_is_refused_with_428` · `two_concurrent_edits_produce_one_winner`
**Verify:** `just test-e2e -- test/platform/concurrency.e2e-spec.ts`
**Done when:** the three tests pass on a fixture aggregate.

### 0.3.7 — Liveness and real readiness
**Repo:** backend · **Size:** S · **Depends on:** `0.2.3` · **Requirements:** SR-NFR-OBS-001
**Files:** `src/health/health.controller.ts`, `test/platform/health.e2e-spec.ts` (new)
`GET /health/live` answers while the process runs; `GET /health/ready` checks PostgreSQL and Valkey (and
the identity provider's configuration once `0.5.4` lands) — today it returns "ready" unconditionally
(`health.controller.ts:20–27`). Neither reveals versions or configuration.
**Tests:** `readiness_fails_when_the_database_is_down` · `readiness_fails_when_valkey_is_down`
**Verify:** `just test-e2e -- test/platform/health.e2e-spec.ts`
**Done when:** readiness reports `503` with the database or Valkey stopped, and `200` when both return.

### 0.3.8 — Rate limits by category, shared through Valkey
**Repo:** backend · **Size:** M · **Depends on:** `0.2.3` · **Requirements:** SR-API-008, SR-AUTH-004
**Files:** `src/common/rate-limit/**` (new), `src/app.module.ts`, `src/config/env.schema.ts`, `test/platform/rate-limits.e2e-spec.ts` (new)
A global guard backed by Valkey (so limits hold across instances), with categories `auth` (sign-in
start, callback, invitation acceptance — per IP and per account), `upload`, `export`, `message`,
`privileged` and `default` ([`../reference/api.md`](../reference/api.md)), `Retry-After` on `429`, and a
trusted-proxy setting so the client address is not spoofable. Credential brute-force protection itself
lives at the identity provider (`0.5.1`).
**Tests:** `each_category_applies_its_own_limit` · `limits_hold_across_two_api_instances` · `a_spoofed_forwarded_for_header_is_ignored`
**Verify:** `just test-e2e -- test/platform/rate-limits.e2e-spec.ts`
**Done when:** the three tests pass with two API instances sharing one Valkey.

### 0.3.9 — The committed OpenAPI contract and the breaking-change check
**Repo:** backend · **Size:** M · **Depends on:** `0.3.2`, `0.3.3`, `0.3.4`, `0.3.5` · **Requirements:** SR-CORE-002, TEST-004
**Files:** `scripts/export-openapi.ts` (new), `openapi/openapi.json` (new, committed), `nest-cli.json`,
`src/main.ts`, `.github/workflows/ci.yml`, `justfile`
The `@nestjs/swagger` CLI plugin describes the DTOs; the document registers the session-cookie scheme
and the CSRF header (today two controllers reference an unregistered `bearer` scheme, `main.ts:59–69`)
and is titled **Sadara API**. `npm run openapi` writes it without starting a server; CI fails if the
committed file differs from the generated one and runs `oasdiff breaking` against `development`'s copy —
a breaking change needs `v2` of that endpoint or a reviewed exception
([ADR-0010](../adr/0010-api-contract.md)).
**Tests:** `the_committed_contract_matches_the_code` · `problem_details_are_declared_for_every_operation`
**Verify:** `npm run openapi && git diff --exit-code openapi/openapi.json`
**Done when:** CI regenerates and diffs the contract on every pull request, and every operation declares
its success and problem responses.

---

## Group 0.4 — Database integrity and tenant transactions

*Today every repository adds `tenantId` by hand and nothing fails when one forgets; six relations can
point across tenants; the database has no tenant enforcement at all. This group makes the database
refuse what the code might forget ([ADR-0004](../adr/0004-tenancy-defense-in-depth.md)); the rules are in
[`../reference/database.md`](../reference/database.md). Partial indexes, CHECKs, policies, triggers and
grants are written in migration SQL and proven by catalog tests, because Prisma's drift check neither
sees nor protects them ([ADR-0017](../adr/0017-sql-managed-database-objects.md)).*

### 0.4.1 — Preflight: report every integrity violation before constraining anything
**Repo:** backend · **Size:** M · **Depends on:** `0.2.2` · **Requirements:** SR-DB-003
**Files:** `scripts/preflight.sql` (new), `scripts/preflight.ts` (new), `justfile` (`preflight`), `test/db/preflight.integration-spec.ts` (new)
A read-only report, run before every constraint migration in this group and before any data migration
later. Each rule emits counts and row identifiers, never personal content: the six cross-tenant edges,
treatment sessions whose record belongs to another player, attendance joining two programs, orphaned
references, duplicate normalised emails per tenant, money beyond its currency's scale, timestamps of
unknown provenance, soft-deleted audit rows, and **whether any real (non-seed) account exists**. A
non-zero count blocks the dependent migration until the owner approves a correction; nothing is deleted
to make a constraint pass.
**Tests:** `preflight_reports_cross_tenant_edges` · `preflight_reports_same_parent_violations` · `preflight_output_contains_no_personal_data`
**Verify:** `just preflight && just test-int -- preflight`
**Done when:** every rule finds its seeded counter-example in the fixture database and reports zero on a
clean one.

### 0.4.2 — Database roles: owner, migrator, runtime
**Repo:** backend + umbrella · **Size:** M · **Depends on:** `0.2.1`, `0.2.2` · **Requirements:** SR-NFR-SEC-002
**Files:** umbrella `infra/postgres/init/10-roles.sql`; backend `prisma.config.ts`, `src/config/env.schema.ts`,
`.github/workflows/ci.yml`, `justfile`, `test/db/roles.integration-spec.ts` (new)
`sadara_owner` (NOLOGIN) owns the schema; `sadara_migrator` assumes it only to run migrations
(`MIGRATION_DATABASE_URL`, used by a new `just migrate`); `sadara_app`, the runtime role, is **not an owner and has NOBYPASSRLS**, with
default privileges granting it only DML. The application never connects as the owner or migrator, in
any environment, and CI and the test harness use the same split.
**Tests:** `the_runtime_role_owns_no_table` · `the_runtime_role_cannot_run_ddl` · `the_runtime_role_cannot_bypass_rls`
**Verify:** `just migrations && just test-int -- roles`
**Done when:** the three tests pass as the runtime role in CI.

### 0.4.3 — Explicit tenant context and the tenant transaction
**Repo:** backend · **Size:** L · **Depends on:** `0.4.2`, `0.2.3` · **Requirements:** SYS-TEN-001, SYS-TEN-002, SR-DB-004
**Files:** `src/common/tenancy/{tenant-context,tenant-transaction}.ts` (new),
`src/infrastructure/prisma/prisma.service.ts`, `eslint.config.mjs` (a boundary rule), `test/db/tenant-transaction.integration-spec.ts` (new)
Use cases receive an `AuthorizedTenantContext` — minted only by the session guard (`0.5.6`), the worker's
job loader (`0.7.6`) or an audited platform operation — and run their database work through
`withTenantTransaction(ctx, fn)`, which sets `app.tenant_id` **transaction-locally** on the connection
that runs `fn`. The actor is explicit: a signed-in member, or the system acting for a job — never an
invented account. Repositories take the transaction client **and the context**, and still write
`tenantId: ctx.tenantId` into their predicates — row-level security is the backstop, not the only filter;
what disappears is any tenant id taken from a caller or from ambient state. A lint rule forbids modules
from importing the root Prisma client. The second, unused tenancy mechanism on `PrismaService` — `runWithTenant`,
`getCurrentTenantId`, `getTenantFilter` (`prisma.service.ts:98–120`) — is deleted.
```ts
export type Actor = { kind: 'USER'; userId: UserId; sessionId: SessionId } | { kind: 'SYSTEM'; job: string };   // PLATFORM arrives in 4.1
export type AuthorizedTenantContext = Readonly<{ tenantId: TenantId; actor: Actor; requestId: string; locale: 'ar' | 'en' }>;
export type TenantTx = Prisma.TransactionClient;
export function withTenantTransaction<T>(ctx: AuthorizedTenantContext, fn: (tx: TenantTx) => Promise<T>): Promise<T>;
```
**Tests:** `queries_run_inside_the_tenant_transaction` · `a_context_cannot_be_built_from_request_input` · `the_setting_does_not_outlive_its_transaction`
**Verify:** `just test-int -- tenant-transaction && npm run lint`
**Done when:** the three tests pass and the lint rule rejects a module that imports the root client.

### 0.4.4 — Composite and same-parent foreign keys
**Repo:** backend · **Size:** M · **Depends on:** `0.4.1` · **Requirements:** SYS-TEN-004
**Files:** `prisma/schema.prisma`, migration `…_tenant_integrity`, `test/db/foreign-keys.integration-spec.ts` (new)
Make `Contract.season` (`schema.prisma:638`), `Training.season` (`:834`), `PerformanceRecord.season`
(`:756`), `LegalTicket.assignedTo` (`:975`), `Message.sender` (`:1287`), `AuditLog.user` (`:1358`) and
`Document.uploadedBy` composite `(…Id, tenantId)` with `RESTRICT`; change the two composite `SET NULL`
keys (`scouting_reports_playerId_tenantId_fkey`, `treatment_sessions_medicalRecordId_tenantId_fkey`) to
`RESTRICT`, because `SET NULL` would null `tenantId` too. Add the **same-parent** keys: a treatment
session references `(medicalRecordId, playerId, tenantId)`, so it cannot cite another player's record;
attendance carries `trainingId`, so its enrollment and session must belong to one program. Constraints
are added `NOT VALID`, validated in a separate statement, and only then is the weaker key dropped.
**Tests:** `foreign_keys_refuse_cross_tenant_edges` · `a_treatment_cannot_cite_another_players_record` · `attendance_cannot_mix_training_programs` · `no_composite_foreign_key_uses_set_null`
**Verify:** `just preflight && just migrations && just test-int -- foreign-keys`
**Done when:** raw inserts violating each rule fail in PostgreSQL and `just migrations` reports no drift.

### 0.4.5 — Row-level security on every tenant-owned table; tenant ids immutable
**Repo:** backend · **Size:** L · **Depends on:** `0.4.3`, `0.4.4` · **Requirements:** SYS-TEN-005, BR-RULE-01, SR-ACL-001
**Files:** `src/infrastructure/prisma/model-classification.ts` (new), migration `…_tenant_rls`,
`scripts/generate-rls.ts` (new), `test/db/rls.integration-spec.ts` (new)
Every model is classified `tenant-owned` or `global` in one table; a test fails on an unclassified model
or on any table with a `tenantId` column that lacks a policy. Each tenant-owned table gets `ENABLE` and
`FORCE ROW LEVEL SECURITY` and one policy for the runtime role:
`USING ("tenantId" = NULLIF(current_setting('app.tenant_id', true), '')::uuid)` with the same `WITH
CHECK`. A full `tenants` row is visible only to its own tenant; host resolution and job discovery read a
narrow `tenant_directory` view (`id`, `slug`, `domain`, `isActive` — nothing else) granted to the runtime
and registry roles. Global tables get **per-table** privileges: reference data (permissions, the default
matrix, currencies) is read-only; `identities` is readable and insertable only through the identity
adapter; `security_events` is insert-only for the runtime role, with reads through a restricted path
(`0.7.3`). A trigger refuses any `UPDATE` of `tenantId`. Missing context means no rows and no writes. RLS separates tenants; it does
not replace the policies that separate roles inside one tenant (`0.6`).
**Tests:** `rls_missing_context_denies_reads_and_writes` · `rls_pool_reuse_never_leaks_the_previous_tenant` · `every_tenant_table_has_forced_rls_and_a_policy` · `tenant_ids_cannot_be_updated` · `the_tenant_directory_exposes_only_routing_columns`
**Verify:** `just migrations && just test-int -- rls`
**Done when:** raw SQL as the runtime role cannot read or write tenant B while running as tenant A or
with no context, including across interleaved transactions on one small pool.

### 0.4.6 — Tenant-leading indexes; duplicate indexes dropped
**Repo:** backend · **Size:** S · **Depends on:** `0.4.4` · **Requirements:** SR-DB-006
**Files:** `prisma/schema.prisma`, migration `…_tenant_indexes`, `test/db/indexes.integration-spec.ts` (new)
Prefix the unprefixed filter indexes ([`../reference/database.md`](../reference/database.md)) with
`tenantId` and drop the redundant `tenants.slug` index that duplicates its unique constraint
(`schema.prisma:278`, `:318`).
**Tests:** `every_index_on_a_tenant_table_leads_with_tenant_id`
**Verify:** `just migrations && just test-int -- indexes`
**Done when:** the catalog test passes with a short, reviewed allowlist of tenant-safe exceptions.

### 0.4.7 — Money: NUMERIC(19,4) with currency rules
**Repo:** backend · **Size:** M · **Depends on:** `0.4.1` · **Requirements:** —
**Files:** `src/common/money/money.ts` (new), `prisma/schema.prisma`, migration `…_money`, contract and training DTOs
Money columns become `Decimal @db.Decimal(19, 4)` (today `Decimal(…, 2)` — JOD has three decimals;
`schema.prisma:616, 621, 825, 898`); a global `CurrencyDefinition(code, minorUnitExponent, enabled)` is
seeded with **every active ISO 4217 currency and its official decimals** — 0 to 4, all of which
`NUMERIC(19,4)` holds — all enabled (owner decision, 29 September 2026); a tenant's default is JOD;
enrollment payments capture their own currency; amounts in different currencies are never added without
a recorded exchange rate. `Money` wraps Prisma's exact decimal and a currency code, validates payable amounts to the
currency's exponent, refuses NaN, infinity and excess scale **before** PostgreSQL could round them, and
travels as `{ "amount": "1250.500", "currency": "JOD" }` ([ADR-0006](../adr/0006-money.md)).
```ts
export class Money { static parse(amount: string, currency: CurrencyCode): Money; add(other: Money): Money; toWire(): { amount: string; currency: CurrencyCode }; format(locale: 'ar' | 'en'): string }
```
**Tests:** `jod_amounts_keep_three_decimals` · `excess_scale_is_refused_not_rounded` · `money_never_passes_through_a_javascript_number` · `every_active_iso_4217_currency_is_seeded_with_its_decimals`
**Verify:** `npx jest src/common/money && just migrations`
**Done when:** `Money.parse('1.255', 'JOD').toWire()` round-trips exactly, `Money.parse('1.255', 'USD')`
is refused, and no money column keeps scale 2.

### 0.4.8 — Calendar dates, instants and tenant time zones
**Repo:** backend · **Size:** M · **Depends on:** `0.4.1` · **Requirements:** SR-CORE-006, UX-007
**Files:** `prisma/schema.prisma`, migration `…_dates_instants_zones`, `src/common/time/**` (new), `test/db/time.integration-spec.ts` (new)
Civil values — birth dates, passport expiry, contract and season boundaries — become `DATE`; every
instant becomes `timestamptz(3)`, converted `AT TIME ZONE 'UTC'` only where the preflight shows the
source is known to be UTC. `TrainingSession` gains `startsAt` and `endsAt` plus an IANA zone. `Tenant`
gains typed `timezone` (IANA, validated), `defaultLocale` (`ar` | `en`) and `defaultCurrency`, which
leave the untyped `settings` JSON. Rules take an injected clock ([ADR-0007](../adr/0007-time.md)).
**Tests:** `a_birth_date_is_the_same_day_in_every_timezone` · `instants_round_trip_in_utc` · `an_invalid_tenant_timezone_is_refused`
**Verify:** `just migrations && just test-int -- time`
**Done when:** a birth date stored from UTC−10 reads back unchanged from UTC+14, and `Tenant.settings`
no longer holds the three typed values.

### 0.4.9 — Normalised emails; lifetime uniqueness with audited reactivation
**Repo:** backend · **Size:** S · **Depends on:** `0.4.1` · **Requirements:** SR-ACL-002
**Files:** `prisma/schema.prisma`, migration `…_normalized_email`, `src/modules/users/**`
`normalizedEmail` (trimmed, lowercased, Unicode-normalised) is unique per tenant **for the life of the
membership**: an archived member keeps the address reserved, and bringing them back is an audited
`reactivateMembership` command, not a second account. Email is contact data; it never links an identity
(`0.5.3`).
**Tests:** `emails_are_unique_regardless_of_case_and_spacing` · `an_archived_members_email_stays_reserved` · `reactivation_restores_the_same_membership`
**Verify:** `just migrations && just test-int -- users`
**Done when:** the three tests pass and the preflight reports no duplicate normalised email.

### 0.4.10 — Integrity constraints in SQL: checks, partial uniques, safe defaults, bounded JSON
**Repo:** backend · **Size:** M · **Depends on:** `0.4.4` · **Requirements:** SR-DB-007
**Files:** migration `…_integrity_constraints`, `test/db/constraints.integration-spec.ts` (new)
CHECK constraints for the existing numeric and date fields (non-negative minutes, goals and capacity;
end dates not before start dates; finite numerics); a partial unique index for **one current season per
tenant** and **one featured image per player**; legal notes **internal by default** (today
`isInternal` defaults to `false`, `schema.prisma:1001`); size and shape bounds on the JSON columns so
metadata cannot become a hidden relational store.
**Tests:** `impossible_values_are_refused_by_the_database` · `a_tenant_has_at_most_one_current_season` · `legal_notes_are_internal_by_default`
**Verify:** `just migrations && just test-int -- constraints`
**Done when:** each rule refuses its counter-example in raw SQL, and a catalog test lists every
constraint by name.

### 0.4.11 — UUIDv7 for high-ingest tables
**Repo:** backend · **Size:** S · **Depends on:** `0.4.1` · **Requirements:** SR-DB-002
**Files:** `prisma/schema.prisma`, `src/infrastructure/prisma/model-classification.ts`
UUID keys stay (v4 by default); append-heavy tables whose index locality matters — audit logs, security
events, outbox and inbox, sessions, messages, notifications — use `@default(uuid(7))`, declared when each
table is created. The classification records which, so a reviewer sees the choice.
**Tests:** `high_ingest_ids_are_time_ordered`
**Verify:** `just test-int -- ids`
**Done when:** the test passes for `audit_logs`, the one high-ingest table that exists today.

### 0.4.12 — The existing modules on the tenant transaction
**Repo:** backend · **Size:** M · **Depends on:** `0.4.5`, `0.1.8` · **Requirements:** SYS-TEN-003
**Files:** `src/modules/users/**`, `src/modules/medical/**`, `src/modules/scouting/**`
Every repository in users, medical and scouting moves onto the transaction client and the verified
context: a tenant id passed in by a caller becomes `ctx.tenantId`, still written explicitly into each
predicate. The quarantined modules are exercised with their flags on.
**Tests:** `medical_reads_see_only_the_context_tenant` · `scouting_writes_are_stamped_with_the_context_tenant`
**Verify:** `FEATURE_MEDICAL=on FEATURE_SCOUTING=on just test-e2e -- test/legacy-modules`
**Done when:** no module repository accepts a caller-supplied tenant id, every query runs on the tenant
transaction, and both tests pass.

---

## Group 0.5 — OIDC identity and application sessions

*Identity moves to an external OpenID Connect provider, as SysRD §2 specifies — Keycloak in development
and staging, the production choice settled with hosting ([ADR-0002](../adr/0002-identity-oidc.md)). The
provider authenticates (passwords, MFA, recovery, lockout); Sadara decides membership, roles and
policy. The API is the confidential OIDC client and owns one opaque session per browser, on the same
origin as the web app ([ADR-0003](../adr/0003-browser-sessions.md)); no provider token is ever stored.*

### 0.5.1 — The Keycloak realm as code
**Repo:** umbrella · **Size:** M · **Depends on:** `0.2.1` · **Requirements:** SR-AUTH-008, SR-AUTH-004
**Files:** `infra/keycloak/realm-sadara.json` (new), `infra/keycloak/test-realm.sh` (new), `infra/compose.yaml`
The realm is a reviewed file, imported at start. Client `sadara-api`: confidential, standard flow only,
**PKCE S256 required**, exact redirect and post-logout URIs per tenant host, back-channel logout URL
with session required. Authentication: password policy length ≥ 12 with no composition rules and a
blocked-password list; brute-force detection with temporary lockout; email verification; a conditional
flow mapping **MFA (OTP or WebAuthn) to level of assurance 2**; WebAuthn and passkeys available without
being required, so they can be adopted without changing any business API. Locales Arabic and English;
mail to Mailpit. Capabilities the pinned release does not provide (for example an `amr` claim) are
recorded, not assumed.
**Tests:** `the_api_client_requires_pkce` · `brute_force_detection_is_enabled` · `mfa_maps_to_assurance_level_2`
**Verify:** `just up && bash infra/keycloak/test-realm.sh`
**Done when:** the realm imports on a fresh stack and the script proves each setting from the running
server's admin API, not from the file.

### 0.5.2 — Resolve the tenant from the host
**Repo:** backend · **Size:** S · **Depends on:** `0.4.5` · **Requirements:** —
**Files:** `src/common/tenancy/tenant-resolver.ts` (new), `src/config/app.config.ts`, `test/auth/tenant-resolution.e2e-spec.ts` (new)
Before anyone is signed in, the tenant comes from the host, read through the `tenant_directory` view:
an exact `Tenant.domain`, else `{slug}.{APEX_DOMAIN}`; the single-agency launch may map an **explicitly
allowlisted** host to `DEFAULT_TENANT_SLUG`, and every other host is refused. The host is taken from a
forwarded header only when the request came through the configured trusted proxy. An inactive tenant is
refused, and an unknown host looks exactly like "no account here". The resolved tenant scopes the
sign-in transaction and the membership lookup; after sign-in the session is the only source of tenant.
**Tests:** `sign_in_uses_the_tenant_of_the_host` · `an_unknown_host_looks_like_no_account` · `an_inactive_tenant_cannot_sign_in`
**Verify:** `just test-e2e -- test/auth/tenant-resolution.e2e-spec.ts`
**Done when:** the three tests pass on `sadara.localhost` and `other.localhost`.

### 0.5.3 — Identities, memberships and sessions in the schema
**Repo:** backend · **Size:** M · **Depends on:** `0.4.5` · **Requirements:** —
**Files:** `prisma/schema.prisma`, migration `…_identity_sessions`, `test/db/identity.integration-spec.ts` (new)
`Identity(id, issuer, subject, createdAt)` is global and unique on `(issuer, subject)`; the tenant `User`
is the **membership**, with `identityId` unique per tenant, and keeps its id so every business foreign
key survives. `UserSession` (tenant-owned, UUIDv7, under RLS) stores only hashes of the session and CSRF
tokens, the identity provider's `sid`, the `acr`, `amr` and `auth_time` it asserted, idle and absolute
expiry, and revocation. An identity is never linked by email alone.
**Tests:** `an_identity_links_to_at_most_one_membership_per_tenant` · `sessions_store_only_token_hashes`
**Verify:** `just migrations && just test-int -- identity`
**Done when:** both tests pass as the runtime role and the new tables carry forced RLS.

### 0.5.4 — The identity-provider port and the Keycloak adapter
**Repo:** backend · **Size:** L · **Depends on:** `0.5.1`, `0.5.3` · **Requirements:** SR-AUTH-001
**Files:** `src/modules/identity/application/identity-provider.port.ts` (new),
`src/modules/identity/infrastructure/keycloak/**` (new), `test/support/test-issuer.ts` (new)
One port hides the provider. Protocol calls use a certified OIDC client library: discovery, JWKS cached
with rotation, an allowlisted issuer, and ID-token verification of `iss`, `aud`, `azp`, `exp`, `iat` and
`nonce`. Administration calls use the provider's admin API with a least-privilege service account.
Automated tests run against an in-process test issuer (which can mint malformed and hostile tokens);
realm behaviour is proven against Keycloak itself in `0.5.1` and at the gate.
```ts
export interface IdentityProviderPort {
  authorizationUrl(p: { state: string; nonce: string; codeChallenge: string; loginHint?: string; acrValues?: string; locale: 'ar' | 'en' }): URL;
  exchange(code: string, codeVerifier: string, expectedNonce: string): Promise<VerifiedSignIn>;   // issuer, subject, sid, acr, amr, authTime, email, emailVerified
  verifyLogoutToken(jwt: string): Promise<{ subject?: string; sid?: string }>;
  createAccount(email: string, locale: 'ar' | 'en', requiredActions: RequiredAction[]): Promise<{ subject: string }>;
  sendSetupEmail(subject: string): Promise<void>;
  disableAccount(subject: string): Promise<void>;
}
```
**Tests:** `id_tokens_from_another_issuer_are_refused` · `id_tokens_for_another_audience_are_refused` · `a_mismatched_nonce_is_refused` · `rotated_signing_keys_are_accepted`
**Verify:** `just test-int -- identity-provider`
**Done when:** the four tests pass against the test issuer and the adapter's admin calls pass against
the compose Keycloak.

### 0.5.5 — Sign-in through the API: authorization code with PKCE
**Repo:** backend · **Size:** L · **Depends on:** `0.5.2`, `0.5.4` · **Requirements:** SR-CORE-001
**Files:** `src/modules/identity/presentation/auth.controller.ts` (new), `src/modules/identity/application/sign-in.usecase.ts` (new), `test/auth/sign-in.e2e-spec.ts` (new)
`GET /api/v1/auth/login?returnTo=` stores a one-time login transaction (state, nonce, PKCE verifier,
tenant, validated same-origin `returnTo`) in Valkey for ten minutes — losing it only aborts a sign-in —
and **binds it to the initiating browser** with a short-lived `__Host-sadara_preauth` cookie (HttpOnly,
Secure, SameSite=Lax, `Path=/`, no `Domain`) that grants no access and is cleared at the callback; for a step-up the existing session plays that role. It then
redirects to the provider with the tenant's locale. `GET /api/v1/auth/callback` requires the pre-auth cookie to match, consumes the state
once, exchanges the code, verifies the ID token, and looks up the membership of **that identity in the
host's tenant**: none, archived or inactive means a refusal page and no session (and a security event,
`0.7.3`); otherwise this step creates the `UserSession` row, issues the `__Host-sadara_session` cookie and returns
the browser to `returnTo`. Authenticating later requests with it, expiry and CSRF are `0.5.6`.
**Tests:** `a_member_signs_in_end_to_end` · `a_non_member_gets_no_session` · `a_replayed_or_mismatched_state_is_refused` · `a_callback_from_another_browser_is_refused` · `return_to_cannot_leave_the_origin`
**Verify:** `just test-e2e -- test/auth/sign-in.e2e-spec.ts`
**Done when:** the five tests pass against the test issuer — including a login-CSRF attempt, in which a
callback completed in a browser that did not start the sign-in creates no session.

### 0.5.6 — Server sessions, the session cookie and CSRF
**Repo:** backend · **Size:** L · **Depends on:** `0.5.5`, `0.3.8` · **Requirements:** SR-AUTH-003, SR-ACL-007
**Files:** `src/modules/identity/application/session.service.ts` (new), `src/common/guards/session.guard.ts`
(replaces the placeholder), `src/common/security/csrf.guard.ts` (new), `test/auth/sessions.e2e-spec.ts` (new)
The session `0.5.5` issued is one random 256-bit value in `__Host-sadara_session` (HttpOnly, Secure,
SameSite=Lax, Path=/); PostgreSQL holds only its hash. This step makes it authenticate requests. **Every request checks the session, the membership and the
tenant against PostgreSQL** — not a cache — so revocation and deactivation take effect on the very next
request; a cache may come later only with a tested consistency protocol. Idle expiry 30 minutes, absolute
12 hours (provisional — OPEN). Writes need the session's synchronizer token in `X-CSRF-Token` **and** an
`Origin` equal to the configured origin; non-JSON bodies are refused. The token is derived, not stored —
an HMAC of the session's token hash under a keyed, rotatable secret — so it stays the same in every tab
until the session rotates. `GET /api/v1/auth/session` returns
the member, the tenant and the CSRF token. The guard mints the `AuthorizedTenantContext`.
**Tests:** `the_session_cookie_is_host_only_httponly_and_secure` · `a_write_without_the_csrf_token_is_refused` · `a_write_from_another_origin_is_refused` · `a_revoked_session_fails_on_the_next_request` · `a_deactivated_member_loses_access_on_the_next_request`
**Verify:** `just test-e2e -- test/auth/sessions.e2e-spec.ts`
**Done when:** the five tests pass.

### 0.5.7 — Sign-out, back-channel logout and session management
**Repo:** backend · **Size:** M · **Depends on:** `0.5.6` · **Requirements:** SR-AUTH-007
**Files:** `src/modules/identity/presentation/auth.controller.ts`, `src/modules/identity/application/*.usecase.ts`, `test/auth/session-management.e2e-spec.ts` (new)
`POST /api/v1/auth/logout` revokes the session, clears the cookie with its original attributes and
returns the provider's end-session URL; `POST /api/v1/auth/logout-all` revokes every session of the
member; `GET /api/v1/auth/sessions` and `DELETE /api/v1/auth/sessions/{id}` manage one's **own** sessions
(another member's is a 404). `POST /api/v1/auth/backchannel-logout` verifies the logout token fully —
issuer, audience, `iat`, `jti` replay, the logout event, `sid` or `sub` — and revokes the matching
sessions. **The exposure window, stated:** app-side revocation and deactivation are immediate;
provider-side changes (a disabled account, a reset) reach Sadara through a back-channel event, and if that
event is lost, at the session's idle or absolute expiry at the latest. The owner accepts this window
(OPEN); offboarding is therefore done in Sadara, which is immediate.
**Tests:** `logout_revokes_the_session_server_side` · `logout_everywhere_revokes_every_session` · `a_member_cannot_revoke_another_members_session` · `a_valid_back_channel_logout_revokes_matching_sessions` · `a_forged_or_replayed_logout_token_is_refused`
**Verify:** `just test-e2e -- test/auth/session-management.e2e-spec.ts`
**Done when:** the five tests pass.

### 0.5.8 — MFA assurance for privileged roles; recent authentication for sensitive actions
**Repo:** backend · **Size:** M · **Depends on:** `0.5.6` · **Requirements:** SR-AUTH-002
**Files:** `src/modules/identity/application/assurance.policy.ts` (new), `src/common/decorators/requires-recent-auth.decorator.ts` (new), `test/auth/assurance.e2e-spec.ts` (new)
Members holding a privileged role — owner, admin, legal, finance, medical, physiotherapist, sporting
director by default; tenant-configurable in `1.1.2` — get **no session** until the provider asserts level
of assurance 2: the callback sends them back with `acr_values` for step-up. Sensitive actions (role and
permission changes, approvals, signature evidence, confidential exports, support grants) require
authentication within the last five minutes, else `403 STEP_UP_REQUIRED` with a re-authentication URL;
a successful step-up updates the existing session.
**Tests:** `a_privileged_member_without_mfa_gets_no_session` · `a_sensitive_action_requires_recent_authentication` · `step_up_upgrades_the_existing_session`
**Verify:** `just test-e2e -- test/auth/assurance.e2e-spec.ts`
**Done when:** the three tests pass against the test issuer, and the gate repeats the first against
Keycloak.

### 0.5.9 — The tenant provisioning command
**Repo:** backend · **Size:** M · **Depends on:** `0.5.4` · **Requirements:** BR-OBJ-08
**Files:** `src/cli/provision-tenant.ts` (new), `package.json` (`tenant:provision`), `test/cli/provision-tenant.e2e-spec.ts` (new)
A command, not an endpoint, and an audited platform operation: it creates the tenant and its domain,
registers the tenant's redirect URIs with the provider, creates the owner's provider account with the
required actions (verify email, set password, configure MFA), links the identity to an `OWNER`
membership and asks the provider to send the setup email. It never accepts a password and is idempotent
per slug.
```
npm run tenant:provision -- --slug sadara --name "Sadara Sports Agency" --domain sadara.example --owner-email owner@sadara.test
```
**Tests:** `provisioning_creates_a_tenant_and_an_invited_owner` · `provisioning_is_idempotent_per_slug` · `provisioning_never_accepts_a_password`
**Verify:** `just test-e2e -- test/cli/provision-tenant.e2e-spec.ts`
**Done when:** the three tests pass against the compose Keycloak.

### 0.5.10 — Invitations
**Repo:** backend · **Size:** M · **Depends on:** `0.5.9`, `0.5.6` · **Requirements:** —
**Files:** `prisma/schema.prisma` + migration `…_invitations`, `src/modules/users/**`, `test/users/invitations.e2e-spec.ts` (new)
`POST /api/v1/users/invitations` (`user.invite`, recent authentication) creates or finds the invitee's
provider account and an `Invitation` — email, role, seven-day expiry. Its single-use token is generated
**by the delivery handler at send time** (`0.7.8`), which stores only its hash and puts the raw value only
in the email — so no outbox payload, log or table ever holds a usable link; a resend issues a new token;
the inviter cannot grant a role above their own. The emailed link starts a sign-in that carries the
invitation; the callback binds the membership only when **both** the token matches **and** the provider
asserts that verified email — proof of mailbox and identity, never email alone. `DELETE` revokes; the
list shows pending, accepted, expired and revoked.
**Tests:** `accepting_binds_the_invited_role_to_the_signed_in_identity` · `an_invitation_works_once` · `an_expired_invitation_is_refused` · `an_admin_cannot_invite_above_their_role` · `invitation_tokens_are_stored_hashed`
**Verify:** `just test-e2e -- test/users/invitations.e2e-spec.ts`
**Done when:** the five tests pass.

### 0.5.11 — Development identities and the synthetic seed
**Repo:** backend + umbrella + frontend · **Size:** M · **Depends on:** `0.5.10`, `0.4.7`, `0.4.8`, `0.2.4` · **Requirements:** —
**Files:** umbrella `infra/keycloak/realm-sadara.json` (development users), `infra/keycloak/README.md` (the development members),
`justfile` (`dev-cookie`); backend `src/database/seed.ts`, `justfile` (`seed`); frontend `scripts/dev-cookie.ts` (new)
Two fictional tenants (`sadara`, `northwind`), one member per role in each, linked to development
identities in the realm (documented development-only passwords; privileged members pre-enrolled in
MFA), and synthetic players with Arabic and Latin names. Every address is on the reserved `.test`
domain; today's seed names tenants after real clubs on a real-looking domain (`seed.ts:81–91`) and seeds
a `SUPER_ADMIN` with a known address (`seed.ts:42`) — both go. The seed is idempotent and grows with each
phase. `just dev-cookie <member>` signs a development member in headlessly (Playwright against the local
Keycloak) and prints a curl cookie jar, for manual API testing.
**Tests:** `the_seed_is_idempotent` · `seed_data_uses_only_reserved_domains`
**Verify:** `just seed && just seed && just test-int -- seed`
**Done when:** two consecutive seeds leave the same data and every seeded member can sign in locally.

---

## Group 0.6 — Authorization and confidential projections

*Today the permission seed crashes on 20 of its 63 names, so every permission-guarded route answers
403; any route that declares nothing is allowed; a player holds `medical.read` and the caller chooses
whether confidential records are filtered. The model: an explicit permission catalog, deny by default,
object policies in use cases, and confidential fields that never leave the server without permission
([ADR-0005](../adr/0005-authorization.md), [`../reference/security-privacy.md`](../reference/security-privacy.md)).*

### 0.6.1 — The permission catalog is code; the seed cannot crash
**Repo:** backend · **Size:** M · **Depends on:** `0.4.3` · **Requirements:** SR-ACL-004
**Files:** `src/modules/users/domain/{permission-catalog,default-role-matrix}.ts` (new),
`src/modules/users/application/services/permission.service.ts`, `src/shared/constants/permissions.constants.ts` (delete),
`prisma/schema.prisma` + migration if enums change, `test/authz/catalog.integration-spec.ts` (new)
The seeding splits each name into enums that have no `REJECT`, `SUBMIT`, `VIEW`, `UPLOAD`, `SEND`,
`ASSIGN_ROLE`, `SCOUTING.REPORT` or `PERFORMANCE` (`permission.service.ts:46–54`, called from
`seed.ts:18`). Each catalog entry now declares its key, category, action and confidentiality explicitly
— nothing is parsed from a name — and all of today's permissions exist, deduplicated. The catalog and
the default matrix sync in one transaction, idempotently; the API refuses to boot if the database
disagrees with the code. `SUPER_ADMIN: Object.values(PERMISSIONS)` (`permission.service.ts:93`) is gone.
**Tests:** `every_catalog_entry_can_be_stored` · `the_database_matrix_equals_the_code_matrix` · `the_permission_sync_is_idempotent`
**Verify:** `just test-int -- catalog && just seed && just seed`
**Done when:** the three tests pass and two consecutive seeds succeed on a fresh database.

### 0.6.2 — Deny by default: every route declares its permission
**Repo:** backend · **Size:** M · **Depends on:** `0.6.1`, `0.5.6` · **Requirements:** SR-AUTH-009, SR-API-001
**Files:** `src/common/guards/roles.guard.ts` → `permission.guard.ts`, `src/common/decorators/{permissions,public}.decorator.ts`,
`src/common/decorators/roles.decorator.ts` (delete), `src/shared/types/user.types.ts` (delete), controllers, `test/authz/route-coverage.e2e-spec.ts` (new)
The global `RolesGuard` (`app.module.ts:53`) lets through any route that declares nothing
(`roles.guard.ts:27`). The permission guard enforces `@RequirePermission('contract.approve')` and the
application **refuses to start** if any route has neither a permission nor `@Public()`. The unused
`@Roles` decorator and `ROLE_HIERARCHY` go — two authorization systems invite the wrong one.
**Tests:** `a_route_without_a_permission_or_public_fails_startup` · `each_route_refuses_a_member_without_its_permission`
**Verify:** `just test-e2e -- test/authz/route-coverage.e2e-spec.ts`
**Done when:** every route carries an explicit decorator and both tests pass.

### 0.6.3 — Object policies in the use cases
**Repo:** backend · **Size:** M · **Depends on:** `0.6.2` · **Requirements:** SR-ACL-005, SR-API-002, BR-RULE-02
**Files:** `src/common/policy/policy.ts` (new), `src/modules/*/application/policies/*.policy.ts`
A policy is a pure function evaluated **inside the use case**, after the resource is loaded and before
it is returned or changed — so it holds for every caller, not only HTTP. Relationship, sensitivity and
state are inputs; an id is never authorization. A read denied by policy is `404`, indistinguishable from
absence.
```ts
export type Decision = { allow: true } | { allow: false; reason: DenyReason };
export function authorize(ctx: AuthorizedTenantContext, action: Action, resource: ResourceView): Decision;
```
**Tests:** `a_read_denied_by_policy_is_not_found` · `policies_apply_to_direct_use_case_calls`
**Verify:** `npx jest src/common/policy`
**Done when:** both tests pass and every existing use case that loads a resource calls `authorize`.

### 0.6.4 — Confidential projections, checked against an independent classification
**Repo:** backend · **Size:** L · **Depends on:** `0.6.3` · **Requirements:** SR-ACL-008, BR-OBJ-05
**Files:** `test/fixtures/field-classification.ts` (new), response DTOs, repositories, `test/authz/confidential-fields.e2e-spec.ts` (new)
Repositories **select** the fields a response needs — never `include` a whole related record — and the
response carries a confidential field only when the caller's permission and the policy allow it. The
test does not trust the code's own markers: an **independent fixture** classifies every response field
(`PUBLIC`, `IDENTITY`, `MEDICAL`, `LEGAL_INTERNAL`, `FINANCE`, `MINOR`), and the suite compares real
payloads for every role against it — so a removed marker, a new unclassified field or a widened select
fails.
**Tests:** `confidential_fields_are_absent_for_roles_without_permission` · `every_response_field_is_classified` · `an_unclassified_new_field_fails_the_suite`
**Verify:** `just test-e2e -- test/authz/confidential-fields.e2e-spec.ts`
**Done when:** the three tests pass, and deleting any confidentiality marker in the code makes the suite
fail.

### 0.6.5 — Player-account and guardian relationships
**Repo:** backend · **Size:** M · **Depends on:** `0.6.3` · **Requirements:** —
**Files:** `prisma/schema.prisma` + migration `…_relationships`, `src/modules/players/domain/relationships.ts` (new), `test/authz/relationships.integration-spec.ts` (new)
`PlayerAccountLink` (a member's own player record) and `GuardianLink` (a guardian's scoped access to a
minor) — tenant-owned, composite keys, validity windows, provenance and verification. **No live link
means deny**; nothing is inferred from a surname or an email. The administration workflow arrives in
`1.2.3`; guardian authority rules are OPEN (child protection).
**Tests:** `own_record_access_requires_a_live_link` · `an_expired_guardian_link_denies_access`
**Verify:** `just test-int -- relationships`
**Done when:** both tests pass under RLS.

### 0.6.6 — Effective permissions for the web app
**Repo:** backend · **Size:** S · **Depends on:** `0.6.2` · **Requirements:** —
**Files:** `src/modules/identity/presentation/auth.controller.ts`, `src/modules/users/application/services/permission.service.ts`
`GET /api/v1/auth/session` adds the member's effective permissions, computed per request from the
database, so the web app can shape navigation. Display only: the API still decides every call.
**Tests:** `the_session_lists_effective_permissions` · `a_role_change_applies_on_the_next_request`
**Verify:** `just test-e2e -- test/authz/effective-permissions.e2e-spec.ts`
**Done when:** both tests pass.

### 0.6.7 — No implicit platform access
**Repo:** backend · **Size:** S · **Depends on:** `0.6.1` · **Requirements:** SR-ACL-003, BR-RULE-12
**Files:** `src/modules/users/domain/default-role-matrix.ts`, `src/modules/users/**`, `test/authz/platform-access.e2e-spec.ts` (new)
`SUPER_ADMIN` holds no tenant-data permission and cannot be granted through an invitation or a role
change; platform support access waits for audited, time-boxed grants (`4.1.2`).
**Tests:** `super_admin_reads_no_tenant_data` · `super_admin_cannot_be_granted_by_invitation`
**Verify:** `just test-e2e -- test/authz/platform-access.e2e-spec.ts`
**Done when:** both tests pass.

### 0.6.8 — The existing medical and scouting routes obey the rules
**Repo:** backend · **Size:** M · **Depends on:** `0.6.4`, `0.6.5` · **Requirements:** BR-RULE-07
**Files:** `src/modules/medical/**`, `src/modules/scouting/**`, `src/modules/users/domain/default-role-matrix.ts`, `test/legacy-modules/*.e2e-spec.ts`
They stay flagged off (`0.1.8`) but must be safe when switched on. Medical: `medical.view_confidential`
is defined and never checked (`permissions.constants.ts:28`); the player role holds `medical.read`
(`permission.service.ts:227`) and the caller picks the confidentiality filter
(`medical.controller.ts:70–74`) — enforce the medical policy, limit players to their own record through
`0.6.5`, and take the filter away from the caller; treatment sessions are archived, not hard-deleted
(`treatment-session.repository.ts:202`). Scouting: `status` is writable through `PATCH`
(`update-scouting-report.dto.ts:8`, `update-assignment.dto.ts:8`), so a scout can approve their own
report; the edit check `scoutId !== scoutId && status !== 'DRAFT'` (`update-scouting-report.use-case.ts:18`)
lets anyone edit a draft and the author edit an approved report; reports embed the whole player,
passport included (`scouting-report.repository.ts:56, 79, 158`) — remove, fix and select.
**Tests:** `a_coach_cannot_read_a_medical_record` · `a_player_reads_only_their_own_medical_record` · `the_confidentiality_filter_is_not_caller_controlled` · `treatment_sessions_are_archived_not_deleted` · `patch_cannot_change_a_scouting_report_status` · `only_the_author_edits_a_report_and_only_in_draft` · `a_scouting_report_never_carries_identity_fields`
**Verify:** `FEATURE_MEDICAL=on FEATURE_SCOUTING=on just test-e2e -- test/legacy-modules`
**Done when:** the seven tests pass.

### 0.6.9 — The two-tenant isolation suite over every route
**Repo:** backend · **Size:** L · **Depends on:** `0.6.2`, `0.4.12` · **Requirements:** SR-NFR-SEC-003, TEST-003
**Files:** `test/isolation/isolation.e2e-spec.ts`, `test/isolation/route-inventory.ts` (new)
Introspect every registered route (flags on). For each route that takes an object id, create the object
in tenant B and call it as every role of tenant A: the answer is `404` (or `403` for a function-level
denial), never `2xx`, and nothing in B changed. Lists, counts and search never include B's rows. A route
missing from the inventory fails the suite, so a new route cannot ship unexamined.
**Tests:** `no_route_reads_another_tenants_object` · `no_route_mutates_another_tenants_object` · `every_route_is_in_the_isolation_inventory`
**Verify:** `FEATURE_MEDICAL=on FEATURE_SCOUTING=on just test-e2e -- test/isolation`
**Done when:** the suite covers every route and passes.

---

## Group 0.7 — Atomic audit and durable work

*Today audit is an ordinary table with `deletedAt`, written — when at all — by queuing a job
(`event.service.ts:37`), so a crash loses it. Here audit and side effects commit **with** the business
change, in the same transaction ([ADR-0014](../adr/0014-async-outbox.md)).*

### 0.7.1 — Audit evidence is append-only in the database
**Repo:** backend · **Size:** M · **Depends on:** `0.4.2` · **Requirements:** SR-AUD-005, SR-DB-009, BR-RULE-05
**Files:** migration `…_audit_append_only`, `prisma/schema.prisma`, `test/db/audit-immutability.integration-spec.ts` (new)
The runtime role gets `INSERT` and policy-controlled `SELECT` on `audit_logs` — no `UPDATE`, `DELETE` or
`TRUNCATE`. Triggers refuse row updates and deletes and, separately, `TRUNCATE` (which fires no row
trigger), for every role, until an approved retention path exists. The table gains `eventId` (UUIDv7),
`actorType` (`USER | SYSTEM | PLATFORM`), an actor snapshot, `requestId`, `reason`, `outcome` and
`schemaVersion`; it stops using `deletedAt`, which is dropped once the preflight shows no archived rows.
**Tests:** `the_runtime_role_cannot_update_audit` · `the_runtime_role_cannot_delete_audit` · `truncating_audit_is_refused`
**Verify:** `just migrations && just test-int -- audit-immutability`
**Done when:** each operation fails as the runtime role **and** as the owner, on PostgreSQL 18.

### 0.7.2 — Audit inside the business transaction, redacted; a failed audit aborts the change
**Repo:** backend · **Size:** M · **Depends on:** `0.7.1`, `0.4.3` · **Requirements:** SR-AUD-002, SR-AUD-003, SR-AUD-004, SR-ACL-006
**Files:** `src/infrastructure/audit/audit.service.ts` (new), `src/infrastructure/events/event.service.ts` (delete the queued audit), the users module, `test/db/audit.integration-spec.ts` (new)
`audit.record(tx, ctx, event)` writes inside the caller's transaction. Payloads are allowlisted
structural deltas — who, what, when, tenant, request, before and after — with confidential values
replaced by references; never a request body. If the audit insert fails, the business change rolls back.
Permission and role changes record the previous and the new state.
**Tests:** `a_rolled_back_change_leaves_no_audit_row` · `a_failed_audit_insert_aborts_the_change` · `audit_payloads_carry_no_confidential_values` · `role_changes_record_before_and_after`
**Verify:** `just test-int -- audit`
**Done when:** the four tests pass, the failure case by injected fault.

### 0.7.3 — Security events that have no tenant
**Repo:** backend · **Size:** S · **Depends on:** `0.7.1`, `0.5.5` · **Requirements:** SR-AUD-001
**Files:** `prisma/schema.prisma` + migration `…_security_events`, `src/infrastructure/audit/security-events.ts` (new)
A refused sign-in on an unknown host has no tenant to belong to, and inventing one would falsify the
record. `SecurityEvent` — global, UUIDv7, append-only by the same grants and triggers — records sign-in
success and refusal, step-up, logout, back-channel events and session revocations, with the tenant when
it is known and hashed network data. Reading it is restricted (the tenant's own view arrives in `1.7.1`).
**Tests:** `a_refused_sign_in_is_recorded_without_a_tenant` · `security_events_are_append_only`
**Verify:** `just test-int -- security-events`
**Done when:** both tests pass.

### 0.7.4 — Access audit for confidential reads
**Repo:** backend · **Size:** S · **Depends on:** `0.7.2`, `0.6.4` · **Requirements:** —
**Files:** `src/infrastructure/audit/access-audit.ts` (new), the confidential projections
Returning a `MEDICAL`, `LEGAL_INTERNAL`, `IDENTITY` or `FINANCE` field records who read which record's
which class, in the same transaction and **before** the data is released; if that record cannot be
written, the data is withheld. The event carries identifiers, never the content.
**Tests:** `reading_a_medical_record_leaves_an_access_event` · `a_failed_access_audit_withholds_the_data`
**Verify:** `just test-int -- access-audit`
**Done when:** both tests pass.

### 0.7.5 — The transactional outbox and the consumer inbox
**Repo:** backend · **Size:** M · **Depends on:** `0.7.2` · **Requirements:** SYS-ASY-005, SYS-ASY-002, BR-RULE-10
**Files:** `prisma/schema.prisma` + migration `…_outbox`, `src/infrastructure/outbox/**` (new), `test/db/outbox.integration-spec.ts` (new)
`OutboxEvent` (tenant-owned, UUIDv7, under RLS like every tenant table): type, aggregate reference, a
payload of **identifiers only**, a unique `dedupKey`, state `CREATED → LEASED → PUBLISHED` or `DEAD`,
attempts and next-attempt time. `outbox.enqueue(tx, ctx, event)` writes it in the business transaction.
`ConsumerInbox` — tenant-owned under forced RLS, unique on `(consumer, eventId)`, with a composite foreign
key to its `OutboxEvent` — lets a handler commit its effect exactly once however often the event is
delivered. A notification is advisory; the workflow record stays the truth.
**Tests:** `a_rolled_back_change_enqueues_nothing` · `a_duplicate_dedup_key_is_a_no_op` · `a_consumer_commits_an_event_once`
**Verify:** `just test-int -- outbox`
**Done when:** the three tests pass.

### 0.7.6 — The worker process, with tenant-safe job discovery
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `0.7.5` · **Requirements:** SYS-ARC-005, SYS-ASY-003, SYS-ASY-004, SYS-TEN-006
**Files:** backend `src/worker.ts` (new), `src/infrastructure/queue/**` (new), `src/infrastructure/tenancy/tenant-registry.ts` (new),
migration `…_registry_role`; umbrella `infra/compose.yaml` (a `worker` service), `infra/postgres/init/`
A second entry point runs BullMQ on Valkey. It finds work without a privileged client: a registry role
may read only the `tenant_directory` view (`0.4.5`); for each active tenant the relay opens a tenant
transaction and claims due events `FOR UPDATE SKIP LOCKED`, then publishes them. Every job carries its tenant and a
business reference; its handler restores that tenant's context and runs in its own tenant transaction.
Retries back off exponentially to a bound, then mark `DEAD` with the last error; shutdown drains
in-flight jobs.
**Tests:** `a_crashed_worker_redelivers_and_the_handler_stays_idempotent` · `retries_stop_at_the_bound_and_mark_dead` · `a_job_runs_only_in_its_own_tenant` · `the_registry_role_reads_nothing_but_tenant_ids`
**Verify:** `just test-int -- worker`
**Done when:** the four tests pass and `just up` runs `api` and `worker` as separate processes.

### 0.7.7 — Idempotency keys for retried commands
**Repo:** backend · **Size:** M · **Depends on:** `0.4.5`, `0.3.1` · **Requirements:** SR-CORE-010
**Files:** `prisma/schema.prisma` + migration `…_idempotency`, `src/common/idempotency/**` (new), `test/platform/idempotency.e2e-spec.ts` (new)
`IdempotencyRecord` (tenant-owned, RLS): tenant, actor, method and canonical path, key hash, request
hash, state `IN_PROGRESS → SUCCEEDED | REJECTED`, a processing lease with a fencing token, a minimal receipt
(status, resource id — never a confidential snapshot), expiry — the canonical schema in
[`../reference/api.md`](../reference/api.md). An expired lease is recovered without repeating a committed
effect. Commands that clients retry —
invitation acceptance, uploads' completion, exports, and later signatures and payments — claim the key
atomically: the same key and body return the original outcome after re-checking authorization — without
re-evaluating the original `If-Match`, which the first success has legitimately made stale; the same
key with a different body is `409 IDEMPOTENCY_KEY_REUSED`; a concurrent duplicate is
`409 IDEMPOTENCY_IN_PROGRESS` with `Retry-After`.
**Tests:** `a_replayed_command_has_one_effect` · `a_reused_key_with_a_different_body_conflicts` · `a_concurrent_duplicate_is_refused_while_in_progress` · `a_stale_lease_is_recovered_without_a_second_effect` · `a_replay_succeeds_despite_its_stale_original_if_match`
**Verify:** `just test-e2e -- test/platform/idempotency.e2e-spec.ts`
**Done when:** the five tests pass.

### 0.7.8 — Transactional email with honest delivery semantics
**Repo:** backend · **Size:** M · **Depends on:** `0.7.6`, `0.5.10` · **Requirements:** —
**Files:** `src/infrastructure/mail/**` (replaces the logging stub), templates `src/infrastructure/mail/templates/{ar,en}/*`,
`prisma/schema.prisma` + migration `…_email_delivery`, `test/mail/email.integration-spec.ts` (new)
An SMTP adapter (Mailpit locally; the production provider is `1.6.3`) and per-locale templates; the
first consumer is the invitation notice, whose handler generates the invitation token at send time and
stores only its hash (`0.5.10`) — the outbox event carries the invitation id, never a link. **What is promised:** the intent to send is durable (the outbox) and local processing is deduplicated per
event and recipient (an `EmailDelivery` record). **What is not:** delivery exactly once. A worker that
crashes after the SMTP server accepted a message but before recording it sends it again — and repeated
crashes can repeat that; retries are bounded, so a message that keeps failing ends in an explicit `FAILED`
state that raises an alert. Nothing is lost silently; duplicates are possible unless the provider offers an
idempotency key, which the adapter then uses.
**Tests:** `an_invitation_notice_is_sent_in_the_recipients_locale` · `a_redelivered_event_does_not_resend_a_recorded_email`
**Verify:** `just test-int -- email`
**Done when:** an invitation created through the API arrives in Mailpit in the invitee's language, and
the redelivery test passes.

---

## Group 0.8 — The private file pipeline

*Today files would go to the API's local disk under a caller-influenced path (`local.storage.service.ts:18–19`,
a latent traversal — no route uses it yet), and file metadata is scattered across eight URL columns.
The pipeline: private objects, uploads into quarantine, a malware scan, and downloads pinned to the
exact bytes that were scanned ([ADR-0009](../adr/0009-object-storage.md)).*

### 0.8.1 — The storage port and an S3 adapter; local-disk storage removed
**Repo:** backend · **Size:** M · **Depends on:** `0.2.1` · **Requirements:** SR-DOC-006
**Files:** `src/infrastructure/storage/**` (port, S3 adapter, key builder), `local.storage.service.ts` (delete), `test/storage/storage.integration-spec.ts` (new)
`StoragePort` offers presigned PUT and GET, head, ranged read, server-side copy and delete — every read
addressable by **object version**. Keys come from one builder, `tenants/{tenantId}/{quarantine|objects}/{uuid}`,
never from a filename. The bucket is private and versioned.
**Tests:** `object_keys_are_opaque_and_tenant_prefixed` · `the_bucket_refuses_anonymous_reads`
**Verify:** `just test-int -- storage`
**Done when:** both tests pass against the compose object store.

### 0.8.2 — File objects and upload sessions
**Repo:** backend · **Size:** M · **Depends on:** `0.8.1`, `0.4.5` · **Requirements:** SR-DOC-001, SR-DB-008
**Files:** `prisma/schema.prisma` + migration `…_file_objects`, `src/modules/files/domain/**` (new)
`FileObject` (tenant-owned, RLS): object key and version, `sha256`, `sizeBytes BigInt`, content type,
original name (display only), status `CREATED → UPLOADING → UPLOADED → SCANNING → PROCESSING → READY` or
`REJECTED | FAILED | ABORTED` (`PROCESSING` stays unused until derivatives arrive in `1.3.3`), scan verdict, classification, retention class, creator. `UploadSession`
records the declared size and type, the owner it is for and its expiry. The polymorphic `Document`
table (`entityType` + `entityId`, no referential integrity) is **contained** here — no new writes, rows kept
— and migrated and retired by `1.3.1`; each domain adds a typed binding when it is built — player documents `1.3.1`, player media `1.3.3`, contract versions `1.4.8`,
legal attachments `1.5.3`, message attachments `2.6.5`.
**Tests:** `a_file_object_never_stores_a_url` · `sizes_beyond_two_gibibytes_are_representable`
**Verify:** `just migrations && just test-int -- files`
**Done when:** both tests pass and no table references files by URL except the legacy columns their
owning steps replace.

### 0.8.3 — Upload: authorize, presign into quarantine, finalize with content checks
**Repo:** backend · **Size:** M · **Depends on:** `0.8.2`, `0.6.3` · **Requirements:** SR-DOC-003, SR-NFR-PERF-002
**Files:** `src/modules/files/presentation/uploads.controller.ts` (new), `src/modules/files/application/**`, `test/files/uploads.e2e-spec.ts` (new)
`POST /api/v1/uploads` names the owner and the declared type and size; the owner's policy authorizes
it; the answer is a presigned PUT **into quarantine**, valid for ten minutes and bound to that size and
type. `POST /api/v1/uploads/{id}/complete` records the quarantined object's **exact `versionId`**, checks that
version's size, magic bytes against the declared type, and the filename, then marks the file `UPLOADED`
and queues its scan. Nothing is processed inside
the request.
**Tests:** `an_executable_renamed_pdf_is_refused` · `an_upload_for_another_tenants_owner_is_not_found` · `a_size_mismatch_is_refused`
**Verify:** `just test-e2e -- test/files/uploads.e2e-spec.ts`
**Done when:** the three tests pass.

### 0.8.4 — Scan, then promote to an immutable version
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `0.8.3`, `0.7.6` · **Requirements:** SR-DOC-004
**Files:** backend `src/modules/files/application/scan-file.handler.ts` (new), `src/infrastructure/scanning/clamav.adapter.ts` (new); umbrella `infra/compose.yaml`
A worker handler streams **the recorded quarantine version** — never "the latest" — to ClamAV while
computing its `sha256`. Clean: a server-side copy **of that same version** to the immutable `objects/` key,
recording the new `versionId` and the hash; the quarantine
object is deleted; the file becomes `READY`. Infected: `REJECTED`. A scanner outage retries and **never**
marks a file clean. Because downloads read only the promoted version, replaying the old upload URL —
still valid for minutes — cannot change what anyone downloads.
**Tests:** `a_clean_file_is_promoted_to_an_immutable_version` · `an_infected_file_is_rejected` · `replaying_the_upload_url_after_promotion_changes_nothing` · `a_replay_between_scan_and_copy_cannot_promote_unscanned_bytes` · `a_scanner_outage_never_marks_a_file_clean`
**Verify:** `just test-int -- scanning`
**Done when:** the five tests pass with the EICAR test file against the compose ClamAV — the race case
driven by a barrier between the scan and the copy.

### 0.8.5 — Download: version-pinned, authorized, short-lived
**Repo:** backend · **Size:** S · **Depends on:** `0.8.4` · **Requirements:** SR-DOC-002
**Files:** `src/modules/files/presentation/files.controller.ts` (new), `test/files/downloads.e2e-spec.ts` (new)
`GET /api/v1/files/{id}/download` authorizes through the owner's policy, requires `READY` and a clean
verdict, and returns a presigned GET for the **exact key and version** that were scanned, valid for 60
seconds, as an attachment with a sanitised name. Confidential classes leave an access event (`0.7.4`).
**Tests:** `a_download_is_pinned_to_the_scanned_version` · `a_download_for_another_tenant_is_not_found` · `an_unscanned_file_cannot_be_downloaded`
**Verify:** `just test-e2e -- test/files/downloads.e2e-spec.ts`
**Done when:** the three tests pass.

---

## Group 0.9 — The bilingual browser foundation

*Today the web app is a sign-in form in front of pages that do not exist: `/` is the Next.js starter,
colliding with `(dashboard)/page.tsx`; eleven links point at `/dashboard/…` routes never built
(`src/shared/lib/constants.ts:31–34`); the page is `lang="en"` with a Latin-only typeface. This group
builds the shell every feature screen lands in ([ADR-0008](../adr/0008-i18n.md),
[`../reference/ui-ux.md`](../reference/ui-ux.md)). Read `frontend/AGENTS.md` first: this Next.js differs
from training data.*

### 0.9.1 — The route map
**Repo:** frontend · **Size:** M · **Depends on:** `0.2.4` · **Requirements:** —
**Files:** `app/page.tsx` (delete), `app/(dashboard)/**` → `app/[locale]/(app)/**`, `app/[locale]/(public)/**`,
`src/shared/lib/constants.ts` (delete the route table), `next.config.ts`, `loading.tsx` / `error.tsx` / `not-found.tsx` per segment
One tree under the locale: `/{locale}` (home), `/{locale}/sign-in`, and features by noun —
`/{locale}/players`, `/{locale}/contracts`, `/{locale}/legal`, `/{locale}/settings` — with no `/dashboard`
prefix. `typedRoutes` is on, so a link to a route that does not exist fails the type-check; every segment
has its loading, error and not-found state.
**Tests:** `every_internal_link_resolves` · `an_unknown_route_renders_not_found`
**Verify:** `npx tsc --noEmit && npm run build && npx playwright test routes`
**Done when:** the build lists no route outside `/[locale]` and no starter content remains.

### 0.9.2 — Arabic and English, RTL and LTR
**Repo:** frontend · **Size:** M · **Depends on:** `0.9.1` · **Requirements:** SR-CORE-007, SR-NFR-I18N-001, UX-008, TEST-010
**Files:** `src/i18n/**`, `messages/{ar,en}.json` (new), `app/[locale]/layout.tsx`, `app/layout.tsx`, `proxy.ts`
`next-intl` with locale routing; `<html lang dir>` rendered on the server (no flash of the wrong
direction); an Arabic-capable, licensed typeface beside the Latin one; every string in the catalogs, with
ICU plurals that cover Arabic's categories; numbers, dates and money through `Intl` with the locale.
Switching language never changes a business value.
**Tests:** `the_catalogs_have_identical_keys` · `the_arabic_layout_renders_rtl_on_the_server` · `no_user_facing_literal_remains`
**Verify:** `npx vitest run src/i18n && npx playwright test i18n`
**Done when:** the sign-in page renders in Arabic with `dir="rtl"` and in English with `dir="ltr"` from
the server, and the literal check passes.

### 0.9.3 — Logical CSS and bidirectional isolation
**Repo:** frontend · **Size:** S · **Depends on:** `0.9.2` · **Requirements:** —
**Files:** `eslint.config.mjs` (a rule), components with physical utilities, `src/shared/ui/bidi.tsx` (new)
A lint rule refuses physical-direction utilities (`ml-`, `pr-`, `left-`, `text-right`, `rounded-l-`, …);
the 17 existing ones, in seven files, move to logical equivalents. Identifiers, emails, URLs and mixed
Latin numbers render inside a bidi-isolating component so they never reorder in Arabic text;
directional icons mirror, media controls do not.
**Tests:** `the_lint_refuses_a_physical_margin` · `a_mixed_identifier_does_not_reorder_in_arabic`
**Verify:** `npm run lint && npx vitest run src/shared/ui`
**Done when:** lint passes with the rule on and the isolation test passes.

### 0.9.4 — A typed client generated from the contract, on the same origin
**Repo:** frontend · **Size:** M · **Depends on:** backend `0.3.9`, `0.9.1`, umbrella `0.2.1` · **Requirements:** —
**Files:** `src/shared/api/{client,problem}.ts` (new), `src/shared/api/schema.d.ts` (generated),
`src/shared/lib/api-client.ts` (delete), `package.json`
`openapi-typescript` generates types from the backend's committed contract at the pinned backend
version, and `openapi-fetch` calls **`/api/v1` on the web app's own origin** — the local HTTPS proxy
(`0.2.1`) in development, the same path routing in every hosted environment — so the session cookie is
never cross-site. Server components call the API's internal address and forward the session cookie only
there.
Problem details become a typed `ApiProblem`. The client never sends a tenant header — today it sends
`X-Tenant-ID` from `localStorage` (`api-client.ts:58–61`) — and `axios` goes.
**Tests:** `a_contract_change_breaks_the_typecheck` · `problem_details_expose_code_and_field_errors` · `no_request_carries_a_tenant_header`
**Verify:** `npm run api:generate && npx tsc --noEmit && npx vitest run src/shared/api`
**Done when:** every API call goes through the generated client and the three tests pass.

### 0.9.5 — Sessions in the browser
**Repo:** frontend · **Size:** M · **Depends on:** `0.9.4`, backend `0.5.6`, backend `0.6.6` · **Requirements:** —
**Files:** `src/features/session/**` (new), `app/[locale]/(public)/sign-in/page.tsx`, `proxy.ts`, `tests/e2e/session.spec.ts` (new)
"Sign in" navigates to `/api/v1/auth/login?returnTo=…`; the current member, tenant, permissions and CSRF
token come from `GET /api/v1/auth/session` — never from reading cookies, which JavaScript cannot see. A
`401` returns to sign-in with the return path; writes carry the CSRF token; TanStack Query keys include
the tenant and the projection, and logout or a tenant change clears every cached query before navigating
to the provider's sign-out. `proxy.ts` looks at cookie presence only to route, never to decide.
**Tests:** `no_session_secret_is_readable_by_javascript` · `an_expired_session_returns_to_sign_in_with_the_return_path` · `logout_clears_every_cached_query`
**Verify:** `npx playwright test tests/e2e/session.spec.ts`
**Done when:** a seeded member signs in through the local Keycloak in Arabic and English, and the three
tests pass.

### 0.9.6 — The application shell
**Repo:** frontend · **Size:** M · **Depends on:** `0.9.3`, `0.9.5` · **Requirements:** UX-010, UX-011, UX-012, SR-NFR-A11Y-001
**Files:** `src/components/shell/**`, `src/shared/ui/states/**` (new), `app/globals.css`
Design tokens; navigation built from the member's effective permissions (display only); shared empty,
loading, error, offline and retry states; light and dark themes with the `dark:` variant bound to the
theme class (`@custom-variant dark`) — today `globals.css:49` styles `.dark` while `dark:` follows the
operating system. Landmarks, headings, visible focus and keyboard operation from the start.
**Tests:** `navigation_hides_what_the_member_cannot_open` · `empty_states_name_the_next_action` · `a_failed_request_offers_retry`
**Verify:** `npx vitest run src/components && npx playwright test shell`
**Done when:** the three tests pass and axe reports no serious violation on the shell in either locale.

---

## Group 0.10 — Operational proof and local recovery

### 0.10.1 — Structured logs with request correlation
**Repo:** backend · **Size:** M · **Depends on:** `0.3.1` · **Requirements:** SR-CORE-008, SYS-TEN-007
**Files:** `src/infrastructure/logging/**` (new), `src/main.ts`, `src/common/interceptors/logging.interceptor.ts` (delete), `test/platform/logging.integration-spec.ts` (new)
`nestjs-pino` JSON logs carrying `requestId`, opaque tenant and member ids, the **route template**,
status and duration. A well-formed incoming `X-Request-Id` is kept, otherwise a UUIDv7 is generated;
it is returned on the response and travels into jobs, so one id follows a request through the worker.
The hand-rolled interceptor and its random ids go.
**Tests:** `a_request_id_reaches_the_worker_log` · `logs_carry_route_templates_not_urls`
**Verify:** `just test-int -- logging`
**Done when:** both tests pass.

### 0.10.2 — Redaction by allowlist, proven by canaries
**Repo:** backend · **Size:** S · **Depends on:** `0.10.1`, `0.1.4` · **Requirements:** —
**Files:** `src/infrastructure/logging/serializers.ts`, `test/security/telemetry-canaries.e2e-spec.ts` (new)
Log serializers **allowlist** what may be logged instead of blocklisting what may not. A canary test
plants secrets and personal data — in query strings, bodies, headers, cookies, error messages and job
payloads — drives requests and jobs, and scans every captured log line for any of them.
**Tests:** `telemetry_canaries_never_escape`
**Verify:** `just test-e2e -- test/security/telemetry-canaries.e2e-spec.ts`
**Done when:** the canary test passes and fails when a canary field is added to the allowlist.

### 0.10.3 — Local backup and restore, drilled
**Repo:** umbrella + backend · **Size:** M · **Depends on:** `0.8.4`, `0.7.1` · **Requirements:** TEST-008
**Files:** umbrella `infra/scripts/{backup,restore}.sh` (new), `justfile` (`backup`, `restore`, `drill`); backend `scripts/verify-restore.ts` (new)
`just backup` captures the database, the object store's versions and the identity realm; `just restore`
rebuilds them into a **fresh, disposable local stack** — and refuses any target that is not local. The
drill then proves the restore: catalog tests pass, every `READY` file's bytes match its recorded hash, and
the audit trail is continuous. The rehearsal on staging, with measured recovery objectives, is Phase 1's.
**Tests:** `a_restored_stack_passes_the_catalog_tests` · `restored_files_match_their_recorded_hashes` · `restore_refuses_a_non_local_target`
**Verify:** `just drill`
**Done when:** the drill passes end to end on a seeded stack.

### 0.10.4 — Failure drills: worker crash, database loss, storage loss
**Repo:** backend · **Size:** M · **Depends on:** `0.7.6`, `0.3.7` · **Requirements:** —
**Files:** `test/drills/*.e2e-spec.ts` (new)
Stop each dependency mid-flight and prove the system fails safe and recovers: a worker killed mid-job
redelivers into an idempotent handler; with PostgreSQL down, readiness fails and requests answer
`503 DEPENDENCY_UNAVAILABLE`, then recover; with storage down, uploads fail and nothing becomes `READY`;
with Valkey down, the `auth` rate-limit category **fails closed**.
**Tests:** `the_api_recovers_when_the_database_returns` · `uploads_fail_safely_when_storage_is_down` · `auth_rate_limits_fail_closed_without_valkey`
**Verify:** `just test-e2e -- test/drills`
**Done when:** the three drills pass.

---

## Group 0.11 — The Phase-0 gate

### 0.11.1 — Run the Phase-0 gate and record the evidence
**Repo:** umbrella + backend + frontend · **Size:** M · **Depends on:** `0.1.2`, `0.1.3`, `0.1.4`, `0.1.6`, `0.1.7`, `0.2.6`, `0.2.7`, `0.2.8`, `0.3.6`, `0.3.9`, `0.4.6`, `0.4.9`, `0.4.10`, `0.4.11`, `0.5.7`, `0.5.8`, `0.5.11`, `0.6.7`, `0.6.8`, `0.6.9`, `0.7.3`, `0.7.4`, `0.7.7`, `0.7.8`, `0.8.5`, `0.9.6`, `0.10.2`, `0.10.3`, `0.10.4` · **Requirements:** BR-OBJ-09, TEST-006
**Files:** umbrella `docs/implementation/progress.md`, `docs/implementation/handoff.md`, the gate PR's body
Run every command of the exit gate below on `development` in each repository and perform the
demonstrations by hand on a freshly seeded stack; record the application commits, the CI runs and the
results in the gate PR; move the pins; regenerate the frontier; review the risk and long-lead registers
and re-forecast Phase 1 from the measured hours. A demonstration that fails keeps the phase open.
**Verify:** the exit-gate commands below
**Done when:** the gate PR is merged with every command green and every demonstration recorded.

---

## Phase 0 exit gate

**Commands**, green on `development` in each repository at the recorded commits:

```bash
# backend
just check && just migrations && just test-int && just test-e2e      # isolation suite, route coverage, drills
npm run build && bash scripts/smoke-start.sh                         # the production image starts
# frontend
just check && npx playwright test                                   # ar + en projects, axe
# umbrella
just check && just guards && just drill                             # pins, plan, links, local restore
```

**Demonstrations**, by hand on a freshly seeded stack, recorded in the gate PR:

1. The route inventory has no local credential route; `POST /api/v1/auth/login` does not exist as a
   password endpoint, and a request with a token signed by `default-secret` is simply unauthenticated.
2. A seeded coach of tenant `sadara` signs in through Keycloak in Arabic on `https://sadara.localhost`,
   lands on the home page, and `GET /api/v1/auth/session` answers; the same identity is refused on
   `https://northwind.localhost`.
3. A seeded owner without MFA gets no session until they complete the step-up; a sensitive action more
   than five minutes after sign-in asks for re-authentication.
4. Signed in as `sadara`'s admin, requesting a `northwind` player by id returns `404`; in `psql` as the
   runtime role with no tenant set, `SELECT count(*) FROM players` returns `0`.
5. After logout, the old session cookie fails on the next request; logging out in Keycloak revokes the
   Sadara session through the back channel.
6. `UPDATE`, `DELETE` and `TRUNCATE` on `audit_logs` are refused by the database, even for the owner.
7. After a full sign-in, invitation and upload flow, the logs contain no email address, token, cookie
   or body — and the canary test proves it automatically.
8. The sign-in page and the shell render in Arabic RTL and English LTR with no untranslated text.
9. A PDF uploads into quarantine, is scanned, promoted and downloads; the EICAR file is rejected;
   replaying the upload URL afterwards changes nothing that downloads.
10. An invitation notice arrives in Mailpit through the worker; killing the worker mid-delivery delivers
    the email on restart — possibly twice if the crash fell after the SMTP server accepted it — and a
    message the provider keeps refusing ends in an alerted `FAILED` state, never silence.
11. `just drill` restores the stack into a fresh local environment and verifies it.
