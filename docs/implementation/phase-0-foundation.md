# Phase 0 — Foundation & hardening

> **Exit:** nothing that exists can leak across tenants or be abused; sign-in works end to end through
> the identity provider; and every later feature is built on rails — tenant transactions under
> row-level security, authorization, atomic audit, durable work, a private file pipeline, the API
> contract and the bilingual shell are in place, tested and green in CI.

**Effort:** 85 microsteps — 22 S, 52 M, 11 L — **340–680 engineering hours** before the 30% reserve
(the size weights are ceilings); [`00-master-plan.md`](00-master-plan.md#effort-model) turns that into a
forecast and recalibrates it from measured hours after the first five steps. No new product
features: the demonstrations are about what can no longer go wrong.
**Two gates.** The [demo milestone](demo-milestone.md) builds the product on the **foundation gate**
(`0.11.0`), which with the gate itself takes 79 of these steps. The other five are production work:
guardian relationships (`0.6.5`), the legacy medical routes (`0.6.8`), the restore and failure drills
(`0.10.3`, `0.10.4`), and the **production gate** (`0.11.1`) itself, without which nothing reaches
staging or production ([ADR-0021](../adr/0021-a-product-built-to-sell.md)).
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
`src/common/filters/http-exception.filter.ts`, `src/common/logging/` (new), `src/infrastructure/prisma/prisma.service.ts`
(Prisma's own error log printed the failing call and its values), every use case that logs an email,
`test/harness/log-capture.ts` (new); frontend `src/shared/lib/api-client.ts`; backend
`test/security/log-leaks.e2e-spec.ts` (new)
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
**Verify:** `npx vitest run src/config && ! grep -rn "default-secret" src && test -z "$(grep -rln 'process\.env' src | grep -v '^src/config/')"`
**Done when:** the API refuses to start with any required variable missing, and nothing outside
`src/config/` reads the environment.

### 0.1.6 — Retire the local credential system
**Repo:** backend · **Size:** L · **Depends on:** `0.2.3`, `0.4.1` · **Requirements:** SR-AUTH-005, SR-AUTH-006, SR-DB-010
**Files:** `src/modules/auth/**` (the controller's 16 routes, the use cases, DTOs, strategies and guards — delete),
`src/common/guards/tenant.guard.ts`, `src/modules/auth/config/throttler-config.module.ts` (delete),
`src/common/guards/session.guard.ts` (new placeholder), `src/app.module.ts`, `prisma/schema.prisma`,
migration `…_retire_local_credentials`, `src/config/env.schema.ts` and `.env.example` (the JWT keys go),
`src/database/seed.ts` (no password), `scripts/preflight.sql` (secret material read from the catalog),
`test/harness/session.ts` (new: a stand-in for sessions in tests), `test/auth/retirement.e2e-spec.ts` (new)
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
`src/features/auth/**`, `src/components/providers/auth-provider.tsx` (signed out until `0.9.5`), `proxy.ts`
(its public routes), `tests/e2e/retirement.spec.ts` (new)
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
**Files:** `src/common/feature-flags/feature-gate.guard.ts` (new), `src/config/env.schema.ts`, `.env.example`,
`src/app.module.ts` (the gate is the first global guard, so it answers before authentication),
`src/modules/medical/medical.module.ts`, `src/modules/scouting/scouting.module.ts`, `test/platform/feature-flags.e2e-spec.ts` (new)
Medical and scouting are partial and carry verified defects: medical's are fixed in `0.6.8` and the module
is rebuilt in Phase 2; scouting is rebuilt in the demo milestone (`1.11.1`–`1.11.8`) and released by
`1.11.7`. Until then `FEATURE_MEDICAL` and `FEATURE_SCOUTING` are **off in every environment unless
explicitly set**, and a controller-level gate answers `404` before any repository is touched. A client
navigation flag is never the control. Per-tenant flags replace these in `1.1.4`.
**Tests:** `medical_routes_are_not_found_when_disabled` · `scouting_routes_are_not_found_when_disabled` · `a_disabled_module_never_reaches_its_repository`
**Verify:** `just test-e2e -- test/platform/feature-flags.e2e-spec.ts`
**Done when:** with the flags unset, every medical and scouting route answers `404` and no medical or
scouting query runs.

---

## Group 0.2 — Reproducible runtimes and test harnesses

### 0.2.1 — The local stack: PostgreSQL 18, S3-compatible storage, Valkey, ClamAV, Mailpit, Keycloak
**Repo:** umbrella + frontend · **Size:** M · **Depends on:** — · **Requirements:** SR-DB-001
**Files:** `infra/compose.yaml` (new), `infra/.env.example` (new), `infra/postgres/init/` (new), `infra/keycloak/` (new),
`infra/proxy/Caddyfile` (new), `infra/objectstore/bootstrap.py` (new), `infra/README.md` (new), `scripts/check-stack.py` (new),
`justfile` (`up`, `down`, `logs`, `reset`, `trust-dev-ca`, `dev-ca-path`); frontend `package.json` (`dev` on `:3001`)
One command brings up everything the applications need: PostgreSQL 18, Valkey, an S3-compatible object
store that supports presigned URLs **and bucket versioning** (Versity S3 Gateway, chosen on evidence in
[ADR-0020](../adr/0020-local-object-store.md) and proven by `infra/objectstore/bootstrap.py` on every `just up`), ClamAV,
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
**Files:** `vitest.config.mts` (new), `test/harness/{app,db,fixtures}.ts` (new),
`justfile` (`test`, `test-int`, `test-e2e`), `package.json` (Jest and `ts-jest` out); `src/app.controller.ts`,
`src/app.service.ts`, `src/app.controller.spec.ts`, `test/app.e2e-spec.ts`, `test/jest-e2e.json` (delete)
Vitest projects with disjoint globs ([ADR-0024](../adr/0024-zod-schemas-and-vitest-on-nestjs-12.md)):
`unit` (`src/**/*.spec.ts`), `integration` (`test/**/*.integration-spec.ts`) and `e2e`
(`test/**/*.e2e-spec.ts`), compiled by SWC so Nest's decorator metadata survives. Vitest loads ES-module
packages natively, which NestJS 12 needs (`0.2.9`). The harness boots the
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
**Files:** `vitest.config.mts`, `playwright.config.ts`, `tests/setup.ts`, `tests/msw/` (new), `tests/e2e/fixtures.ts` (new), `justfile`, `package.json`
Vitest with Testing Library in jsdom and MSW for API responses, on `src/**/*.test.{ts,tsx}`; Playwright
on `tests/**/*.spec.ts` with an `ar` and an `en` project and axe on every page it visits — disjoint globs,
so neither runner picks up the other's files; both wired into `just check` and CI's `test` job. The axe
fixture checks the page every test ends on and exports `expectAccessible(page)` for each navigation
inside a journey; a serious or critical WCAG 2.2 AA finding fails, lesser ones are attached to the report.
**Tests:** `the_unit_runner_renders_a_component` · `each_locale_project_opens_the_sign_in_page`
**Verify:** `just check`
**Done when:** CI runs both runners on every pull request and an empty suite fails.

### 0.2.5 — Lint and format gates in both applications
**Repo:** backend + frontend · **Size:** M · **Depends on:** — · **Requirements:** —
**Files:** in each application `.prettierrc`, `eslint.config.mjs`, `eslint-suppressions.json`, `.git-blame-ignore-revs`,
`justfile`, `.github/workflows/ci.yml`
In each application: Prettier over the application code in one formatting-only commit (listed in
`.git-blame-ignore-revs`), then the ESLint findings — 748 problems in the backend, 21 in the frontend on
28 September 2026. They are fixed in code that stays; in code a later step rewrites or deletes they are
recorded in `eslint-suppressions.json` (ESLint's bulk suppressions), which fails on any new finding and
on a fixed one until `just lint-prune` removes it, so the baseline only shrinks. Then `prettier --check`
and `eslint --max-warnings=0` join `just check` and CI's `test` job in both.
**Verify:** `just check` in each application
**Done when:** CI fails on any new lint or formatting problem in either application.

### 0.2.6 — A production build that starts, in a container
**Repo:** backend · **Size:** M · **Depends on:** `0.1.5`, `0.3.7` · **Requirements:** TEST-006
**Files:** `tsconfig.build.json`, `Dockerfile` (new), `.dockerignore` (new), `scripts/smoke-start.sh` (new),
`test/image/image.image-spec.ts` (new), `vitest.config.mts`, `.github/workflows/ci.yml`
`npm run start:prod` runs `node dist/main`, but the build emits `dist/src/main.js` because
`tsconfig.json` roots the compilation at the repository, where `prisma.config.ts` sits — fix the root so
the entry point is where the script looks: `tsconfig.build.json` compiles `src` alone, rooted there, and
`tsconfig.json` (the type-check over `test/` and `scripts/`) is unchanged. A two-stage `Dockerfile` on
Node 24 Alpine, pinned by digest, builds from the lockfile and keeps only `package.json`, the production
`node_modules` and `dist`, owned by root; it runs as the unprivileged `node` user with a health check on
`/health/live`, and its one writable directory is `uploads/` until the object store replaces the local
storage service. The runtime stage removes npm, npx, corepack and yarn: the first scan found every
vulnerability in npm's bundled dependencies, a critical one among them. `.dockerignore` is an allowlist.
The smoke script starts the image beside a throwaway PostgreSQL 18 (with the `0.4.2` roles) and Valkey on
a network of its own, makes every request inside the container (no published port), and runs the image
test as a fourth Vitest project, `image`. CI's `image` job builds the image, scans it with Trivy (pinned
by digest), failing on a critical vulnerability that has a fix, and runs the smoke test; it is not yet a
required check. The test holds that live and ready answer 200, the process is uid 1000, and it cannot
write its own `dist/main.js`.
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
`zustand`) — 16 of 28 by the time the step ran, since `0.1.7` had retired the last users of
`react-hook-form`, `@hookform/resolvers`, `zod` and `qrcode.react`. A dependency returns with the step that
first imports it; `.depcheckrc.yml` in each application names the few used where depcheck cannot see. Every `@nestjs/*` package sits on
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
**Files:** `package.json`, `package-lock.json`, `tsconfig.json`, `src/app.setup.ts`, `src/common/logging/route-template.ts`,
`src/common/filters/http-exception.filter.ts`, `src/common/feature-flags/feature-gate.guard.ts`,
`src/infrastructure/events/events.module.ts`, `test/harness/app.ts`, `test/platform/nestjs-12.e2e-spec.ts` (new),
`.github/dependabot.yml`
Dependabot offered the NestJS 12 family, `bullmq` 6, TypeScript 7 and ESLint 10 on 28 September; they were
merged with failing checks and reverted (backend #26), because NestJS 12 ships as ES modules and the Jest
setup cannot load them. This step makes the move deliberately and in one piece: every `@nestjs/*` package
to 12 with `bullmq` 6, which makes `ioredis` an optional peer that host/port connections need, so it is
declared again; TypeScript 6 — TypeScript 7 waits until typescript-eslint supports it; the
TypeScript 6 settings decided explicitly (whether to turn `strict` on, given the `any`s of B-9; `types`,
`rootDir`) — decided: `strict` with no exception, since the `any`s of B-9 are explicit and `noImplicitAny`
finds nothing (they stay in the lint baseline of `0.2.5` until their code is rewritten), `types: ["node"]`,
`rootDir: "./"`; Nest's Standard Schema validation registered for the Zod schemas that `0.3.2` writes
([ADR-0024](../adr/0024-zod-schemas-and-vitest-on-nestjs-12.md)), in `app.setup.ts`, the pipeline that
`main.ts` and the test harness share; the Vitest harness of `0.2.3` proven
to load the ES-module packages; then the Dependabot holds on those majors are lifted, and `bullmq` majors
travel in the NestJS group. `@nestjs/swagger` 12
depends on a fixed js-yaml, so the `overrides` entry that patched it under 11 (backend #42) is removed.
NestJS 12 mounts its not-found handler under the global prefix, where `request.path` is relative, so error
bodies and the feature gate of `0.1.8` read the full path from the original URL, without the query.
**Tests:** `the_app_boots_on_nestjs_12` · `the_test_runner_loads_es_module_packages`
**Verify:** `rm -rf node_modules && npm ci && just check && just test-e2e`
**Done when:** every `@nestjs/*` package is on 12, TypeScript is on 6, CI is green, and `dependabot.yml`
no longer holds those majors.


### 0.2.10 — Module boundaries, checked from the first module
**Repo:** backend + frontend · **Size:** M · **Depends on:** `0.2.3`, `0.2.4` · **Requirements:** SYS-ARC-001, SYS-ARC-002, SYS-ARC-004, SR-NFR-MNT-001
**Files:** backend `.dependency-cruiser.cjs` (new), `.dependency-cruiser-known-violations.json` (new),
`scripts/check-boundaries.mjs` (new), `src/architecture/boundaries.spec.ts` (new), `test/architecture/fixtures/**`
(new), `justfile`, `.github/workflows/ci.yml`; frontend `.dependency-cruiser.cjs` (new),
`.dependency-cruiser-known-violations.json` (new), `scripts/{check-boundaries,client-boundary}.mjs` (new),
`src/architecture/boundaries.test.ts` (new), `tests/architecture/fixtures/**` (new), `justfile`,
`.github/workflows/ci.yml`
Moved forward from `1.10.10` so that every module is born inside its boundaries instead of being fenced
in after the features exist. dependency-cruiser, pinned, runs in `just check` and CI's `test` job in both
applications, independently of the linter. Backend: a module's `domain/` imports no Nest, Prisma, HTTP or
provider SDK; another module is reached only through its exported application interface — never its
repository, Prisma model or infrastructure; `presentation/` never imports `infrastructure/`; only the
composition roots wire adapters. Frontend: a feature is imported only through its `index.ts`;
`src/shared` imports no feature; `src/server` and anything marked `server-only` never reach a client
bundle ([ADR-0025](../adr/0025-the-web-app-data-path.md)). Each rule has a deliberately invalid fixture
import that must fail. Violations in code a later step rewrites are recorded in a baseline that only
shrinks, as the lint baseline is (`0.2.5`): 30 in the backend's auth, medical and scouting, 8 deep imports
into the web app's auth feature. The browser boundary needs the `'use client'` directive, which
dependency-cruiser's rules cannot see, so a script walks the same graph from every client module. A new
process or service still needs an ADR with a measured reason ([ADR-0001](../adr/0001-modular-monolith.md)).
**Tests:** `module_boundary_gate_rejects_repository_and_framework_leaks` · `browser_boundary_gate_rejects_server_only_imports`
**Verify:** `(cd backend && npx --no-install vitest run src/architecture && just check) && (cd frontend && npx --no-install vitest run src/architecture && just check)`
**Done when:** CI refuses each forbidden import in both applications, proven by its fixture.
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
`src/common/errors/{error-codes,domain-error,locale,schema-issues}.ts` (new), `src/common/logging/request-id.ts` (new),
`src/infrastructure/prisma/prisma-errors.ts` (new), `src/app.setup.ts`, `src/app.module.ts`, every use case that
throws a plain `Error`, `test/platform/errors.e2e-spec.ts` (new)
Every error is `application/problem+json` — `type`, `title`, `status`, `detail`, `instance`, `code`, `message`, `requestId`,
`fieldErrors` (an empty array when no field is implicated) — registered once in the bootstrap shared by production and tests. The 46 plain
`throw new Error(…)` in the modules (45 by the time the step ran) become typed domain errors; Prisma `P2002` maps to `409 CONFLICT`,
`P2025` to `404 NOT_FOUND`, `P2003` to `409 CONFLICT`; the body parsers' `413` and `415` keep their status; anything unknown to `500 INTERNAL_ERROR`
with nothing internal in it. Only a typed domain error says more than its code: a framework exception's own message is discarded,
since Nest's quotes the URL or the body. Messages are in Arabic and English, chosen by `Accept-Language`; every
request gets an id (`X-Request-Id`), which 0.10.1 hands to the structured logs. Codes are stable forever and clients branch on `code`, never on `message`.
**Tests:** `validation_errors_list_their_fields` · `unknown_errors_leak_nothing` · `every_error_carries_the_request_id` · `a_missing_record_is_a_404_not_a_500`
**Verify:** `just test-e2e -- test/platform/errors.e2e-spec.ts && ! grep -rn "throw new Error(" src/modules`
**Done when:** a thrown `Error('boom at /srv/secret')` returns `INTERNAL_ERROR` without the path, with a
request id equal to the response header, and no module throws a plain `Error`.

### 0.3.2 — Strict validation, registered once
**Repo:** backend · **Size:** S · **Depends on:** `0.3.1`, `0.2.9` · **Requirements:** SR-CORE-005, SR-API-003
**Files:** `src/app.setup.ts`, `src/app.module.ts`, `src/common/validation/**` (new), `src/common/pipes/validation.pipe.ts`
(delete), the medical and scouting DTOs and controllers, `package.json`, `test/platform/validation.e2e-spec.ts` (new)
One validation mechanism — NestJS 12's Standard Schema pipe with Zod 4 schemas
([ADR-0024](../adr/0024-zod-schemas-and-vitest-on-nestjs-12.md)): bodies are strict objects, so an unknown
property is refused; strings trimmed and bounded; arrays bounded; queries coerced explicitly — instead of
today's two class-validator pipes (`app.setup.ts:54`, beside the Standard Schema pipe `0.2.9` registered,
and `APP_PIPE` in `app.module.ts:56`, with different options). Every query is a typed DTO (the medical controller takes
`@Query() query: any`, `medical.controller.ts:65, 92, 208`); every path id is a UUID — through a strict
path schema, the same mechanism, rather than `ParseUUIDPipe`; an empty `PATCH` is a `400`. `class-validator`,
`class-transformer` and `@nestjs/mapped-types` leave the dependencies.
**Tests:** `an_unknown_property_is_refused` · `a_malformed_uuid_is_a_validation_error` · `an_unknown_query_parameter_is_refused`
**Verify:** `just test-e2e -- test/platform/validation.e2e-spec.ts`
**Done when:** a body carrying an extra `tenantId` or `role` is refused with `VALIDATION_FAILED`, and
exactly one validation mechanism is registered.

### 0.3.3 — Versioned routes under /api/v1
**Repo:** backend + frontend · **Size:** S · **Depends on:** `0.3.1` · **Requirements:** —
**Files:** backend `src/app.setup.ts`, `src/health/health.controller.ts`, `test/harness/routes.ts` (new),
`test/platform/versioning.e2e-spec.ts` (new); frontend `src/shared/lib/constants.ts` (the API base URL)
URI versioning makes every route `/api/v1/…` (today `/api/…`, `main.ts:40–41`); health stays unversioned, at `/api/health`.
**Tests:** `routes_are_served_under_v1`
**Verify:** `just test-e2e -- test/platform/versioning.e2e-spec.ts`
**Done when:** no route answers outside `/api/v1` except the health endpoints.

### 0.3.4 — One success envelope, registered once
**Repo:** backend · **Size:** S · **Depends on:** `0.3.1` · **Requirements:** SYS-ARC-003
**Files:** `src/common/interceptors/envelope.interceptor.ts` (replaces `transform.interceptor.ts`),
`src/app.setup.ts`, `src/app.module.ts`, the medical and scouting controllers, `test/harness/fixtures.ts`,
`test/platform/responses.e2e-spec.ts` (new)
Success is `{ data }` — collections `{ data, page }` (`0.3.5`) — applied by one interceptor registered in
one place. Delete the second registration, the 38 hand-built `{ statusCode, data }` bodies and every
"not found" returned as a 200. Responses are built from response DTOs, never Prisma rows, so a schema
refactor is not an API change — every route built from here on; medical and scouting, off everywhere (`0.1.8`),
keep their repositories' rows until their rebuilds (`1.11.x`, `2.1.x`) build DTOs with the field classification.
`204`, downloads and errors are never wrapped; a command with nothing to return answers `{ "data": null }`.
**Tests:** `a_single_resource_is_wrapped_once` · `a_not_found_is_never_a_200` · `timestamps_are_iso_utc`
**Verify:** `just test-e2e -- test/platform/responses.e2e-spec.ts && ! grep -rn "statusCode: HttpStatus" src/modules`
**Done when:** every existing route answers `{ data }` exactly once and no success body carries an error.

### 0.3.5 — Cursor pagination and allowlisted filters
**Repo:** backend · **Size:** M · **Depends on:** `0.3.2`, `0.3.4` · **Requirements:** SR-CORE-004, SR-API-004
**Files:** `src/common/pagination/{cursor,paginate,keyset}.ts`, `src/common/filtering/list-query.ts` (new),
`test/platform/pagination.integration-spec.ts` (new)
Keyset pagination over `(createdAt, id)`: `limit` default 25, maximum 100 — above it is a `400`, never a
silent cap. The cursor is opaque and bound to tenant, sort and filter hash, so a cursor from another
query is `INVALID_CURSOR`; the hash is recomputed from trusted request state on every use, never read
from the cursor. Filters and sort fields come from a per-endpoint allowlist (`listQuery`); one sort,
newest first, until an endpoint needs another with its tiebreaker; no totals unless an endpoint needs
one, and then counted within the caller's visible scope.
```ts
export interface Page<T> { data: T[]; page: { nextCursor: string | null; hasMore: boolean } }
export function paginate<T extends Keyset>(
  query: { limit: number; cursor?: string; scope: CursorScope }, // scope: tenantId, filters, sort
  fetch: (args: KeysetArgs) => Promise<T[]>, // KeysetArgs: take, after; keysetWhere(after) for Prisma
): Promise<Page<T>>;
```
**Tests:** `a_limit_above_100_is_refused` · `cursors_stay_stable_under_inserts` · `a_cursor_from_another_query_is_refused` · `an_unlisted_filter_is_refused`
**Verify:** `npx vitest run src/common/pagination src/common/filtering`
**Done when:** the four tests pass.

### 0.3.6 — Optimistic concurrency: revisions, ETag, If-Match
**Repo:** backend · **Size:** M · **Depends on:** `0.3.4` · **Requirements:** SR-API-005
**Files:** `src/common/concurrency/{revision.ts,if-match.decorator.ts}` (new), `src/app.setup.ts` (CORS lets a
browser send `If-Match` and read `ETag` and `X-Request-Id`), `test/platform/concurrency.e2e-spec.ts` (new)
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
**Files:** `src/health/{health.controller,health.module,readiness.service,probes}.ts`, `src/app.setup.ts`,
`src/app.module.ts`, `src/main.ts`, `src/common/filters/problem-details.filter.ts`, `test/harness/{app,routes}.ts`,
`test/platform/health.e2e-spec.ts` (new), `test/platform/probes.integration-spec.ts` (new)
`GET /health/live` answers while the process runs; `GET /health/ready` checks PostgreSQL and Valkey (and
the identity provider's configuration once `0.5.4` lands), each within one second, and answers a `503`
`DEPENDENCY_UNAVAILABLE` problem when one does not — today it returns "ready" unconditionally
(`health.controller.ts:20–27`). Neither reveals versions or configuration. These are the first routes outside
the `/api` prefix (the old `/api/health` goes), where an unknown path still gets Express's own HTML 404 today
(0.3.1): this step makes every error a problem, wherever the path.
**Tests:** `readiness_fails_when_the_database_is_down` · `readiness_fails_when_valkey_is_down`
**Verify:** `just test-e2e -- test/platform/health.e2e-spec.ts`
**Done when:** readiness reports `503` with the database or Valkey stopped, and `200` when both return.

### 0.3.8 — Rate limits by category, shared through Valkey
**Repo:** backend · **Size:** M · **Depends on:** `0.2.3` · **Requirements:** SR-API-008, SR-AUTH-004
**Files:** `src/common/rate-limit/**` (new), `src/common/errors/domain-error.ts`, `src/common/filters/problem-details.filter.ts`,
`src/app.module.ts`, `src/app.setup.ts`, `src/main.ts`, `src/config/env.schema.ts`, `src/health/health.controller.ts`,
`.env.example`, `test/harness/app.ts`, `test/platform/rate-limits.e2e-spec.ts` (new)
A global guard, after the session guard, that counts every request in Valkey so that limits hold across
instances: a window opens with a client's first request in a category, and one transaction counts it and
sets its expiry. The categories are `auth` (sign-in start, callback, invitation acceptance), `upload`,
`export`, `message`, `privileged` and `default`, each stricter than `default`; their limits are in
[`../reference/api.md`](../reference/api.md#rate-limits). A signed-in member counts as themselves; anyone
else counts as their address, an IPv6 client as its /64. `auth` always counts by address, and `0.5.5` and
`0.5.10` add the per-account count where the account is known. `429 RATE_LIMITED` carries `Retry-After`,
never longer than the window. `TRUSTED_PROXIES` names the proxies whose `X-Forwarded-For` is believed,
none by default, so the client address is not spoofable. Without Valkey, a limited request is refused
with `503`: the limits fail closed, and only the probes go unlimited. Credential brute-force protection
itself lives at the identity provider (`0.5.1`).
**Tests:** `each_category_applies_its_own_limit` · `limits_hold_across_two_api_instances` · `a_spoofed_forwarded_for_header_is_ignored`
**Verify:** `just test-e2e -- test/platform/rate-limits.e2e-spec.ts`
**Done when:** the three tests pass with two API instances sharing one Valkey.

### 0.3.9 — The committed OpenAPI contract and the breaking-change check
**Repo:** backend · **Size:** M · **Depends on:** `0.3.2`, `0.3.3`, `0.3.4`, `0.3.5` · **Requirements:** SR-CORE-002, TEST-004
**Files:** `src/common/openapi/{contract,responses,zod-schema-converter}.ts` (new), `src/contract.ts` (new),
`scripts/{export-openapi,contract-env}.ts` (new), `openapi/openapi.json` (new, committed),
`scripts/{check-breaking-contract,install-oasdiff}.sh` (new), `scripts/test-policy.sh`, `src/app.setup.ts`,
`src/config/swagger.ts`, `src/health/health.controller.ts`, `src/common/feature-flags/feature-gate.guard.ts`,
`src/common/concurrency/if-match.decorator.ts`, `.github/workflows/ci.yml`, `justfile`, `CONTRIBUTING.md`,
`test/platform/contract.e2e-spec.ts` (new)
`@nestjs/swagger` 12 generates the document, OpenAPI 3.1, from the same Zod schemas through its
`standardSchemaConverter`, as JSON Schema 2020-12 ([ADR-0024](../adr/0024-zod-schemas-and-vitest-on-nestjs-12.md)),
in Nest's preview mode, so `npm run openapi` starts no server and reaches no database. It is titled
**Sadara API** and registers the session cookie and the CSRF header; the unregistered `bearer` scheme is
gone. Each route declares its success (`@Returns`, `@ReturnsPage`) and the problems it raises itself
(`@Raises`); its security and the problems the HTTP pipeline can answer it with are derived from its route
(public, `If-Match`, path, body, rate limit), and generation fails on a route that declares no success.
Gated modules (`0.1.8`) stay out of the contract until they are rebuilt. CI fails if the committed file
differs from the generated one and runs `oasdiff breaking` (pinned and digest-verified) against
`development`'s copy — a breaking change needs `v2` of that endpoint or a reviewed exception: a line of
`openapi/breaking-changes.allowed` as `development` holds it, so a change cannot excuse itself
([ADR-0010](../adr/0010-api-contract.md)). `just contract` runs both locally, and the guards prove the
check refuses.
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

### 0.4.0 — One naming scheme in the database: lower snake_case
**Repo:** backend · **Size:** M · **Depends on:** `0.4.1` · **Requirements:** —
**Files:** `prisma/schema.prisma`, migration `…_snake_case_names`, `scripts/preflight.sql`,
`test/db/naming.integration-spec.ts` (new)
The tables are snake_case, but their 282 columns, the 26 enum types and the index and constraint names
built from them are camelCase, so every SQL statement must quote them (`"tenantId"`) — DB-49, decided by
the owner on 16 October 2026: rename, before this group writes most of the project's SQL. Every camelCase
field gets `@map("snake_case")` and every enum `@@map`; the Prisma client keeps its field names, so no
application code changes. One forward-only migration renames in place — `RENAME COLUMN`, `ALTER TYPE …
RENAME TO`, `ALTER INDEX … RENAME TO`, `RENAME CONSTRAINT` — never a drop and an add, so no row moves; the
preflight's SQL follows. A catalog test refuses any table, column, type, index or constraint name that is
not lower snake_case, so a field added later without its `@map` fails CI. The step's record moves the
plan's SQL examples and constraint names to the new names.
**Tests:** `every_database_name_is_lower_snake_case`
**Verify:** `just migrations && just preflight && just test-int -- naming && just test-e2e`
**Done when:** the catalog test passes, `just migrations` reports no drift, and every existing suite
passes unchanged.

### 0.4.1 — Preflight: report every integrity violation before constraining anything
**Repo:** backend · **Size:** M · **Depends on:** `0.2.2` · **Requirements:** SR-DB-003
**Files:** `scripts/preflight.sql` (new), `scripts/preflight.ts` (new), `justfile` (`preflight`, and `scripts/` joins the
lint and format gates), `.github/workflows/ci.yml`, `test/db/preflight.integration-spec.ts` (new)
A read-only report, run before every constraint migration in this group and before any data migration
later. Each rule emits counts and row identifiers, never personal content: the six cross-tenant edges,
treatment sessions whose record belongs to another player, attendance joining two programs, orphaned
references, duplicate normalised emails per tenant, money beyond its currency's scale, timestamps of
unknown provenance, soft-deleted audit rows, and **whether any real (non-seed) account exists**. A
non-zero count blocks the dependent migration until the violation is corrected; nothing is deleted to
make a constraint pass. No real data exists ([ADR-0021](../adr/0021-a-product-built-to-sell.md)), so a
database the report identifies as holding only synthetic seed data may instead be reset and reseeded;
migrations still move forward only, and a database with any real account follows the correction path.
**Tests:** `preflight_reports_cross_tenant_edges` · `preflight_reports_same_parent_violations` · `preflight_output_contains_no_personal_data`
**Verify:** `just preflight && just test-int -- preflight`
**Done when:** every rule finds its seeded counter-example in the fixture database and reports zero on a
clean one.

### 0.4.2 — Database roles: owner, migrator, runtime
**Repo:** backend + umbrella · **Size:** M · **Depends on:** `0.4.0`, `0.2.1`, `0.2.2` · **Requirements:** SR-NFR-SEC-002
**Files:** umbrella `infra/postgres/init/10-roles.sql`, `infra/compose.yaml`, `infra/.env.example`, `justfile`; backend
`scripts/database-roles.sql` (new — the roles' one definition, which the umbrella's init, CI and `just migrations` all
run), `prisma.config.ts`, `src/config/env.schema.ts`, `.github/workflows/ci.yml`, `justfile`, `test/harness/db.ts`,
`test/db/roles.integration-spec.ts` (new)
`sadara_owner` (NOLOGIN) owns the schema; `sadara_migrator` assumes it only to run migrations
(`MIGRATION_DATABASE_URL`, used by a new `just migrate`); `sadara_app`, the runtime role, is **not an owner and has NOBYPASSRLS**, with
default privileges granting it only DML. The application never connects as the owner or migrator, in
any environment, and CI and the test harness use the same split.
The runtime role's defaults bound its work (DB-52): `statement_timeout` 15 s, `lock_timeout` 5 s,
`idle_in_transaction_session_timeout` 60 s and `TimeZone` UTC; a job that needs longer says so with `SET LOCAL`
inside its transaction. Databases are created with PostgreSQL's builtin `C.UTF-8` collation provider — the
local stack, CI and the replay alike — so no operating-system upgrade can reorder an index (DB-51); the
local volume is recreated once (`just reset`).
**Tests:** `the_runtime_role_owns_no_table` · `the_runtime_role_cannot_run_ddl` · `the_runtime_role_cannot_bypass_rls` · `the_runtime_role_has_bounded_work`
**Verify:** `just migrations && just test-int -- roles`
**Done when:** the four tests pass as the runtime role in CI.

### 0.4.3 — Explicit tenant context and the tenant transaction
**Repo:** backend · **Size:** L · **Depends on:** `0.4.2`, `0.2.3` · **Requirements:** SYS-TEN-001, SYS-TEN-002, SR-DB-004
**Files:** `src/common/tenancy/{tenant-context,tenant-transaction}.ts` (new),
`src/infrastructure/prisma/{prisma.service,prisma.module}.ts`, `eslint.config.mjs` (a boundary rule) and
`eslint-suppressions.json` (its baseline), `test/db/tenant-transaction.integration-spec.ts` (new), `test/harness/db.ts`
Use cases receive an `AuthorizedTenantContext` — minted only by the session guard (`0.5.6`), the worker's
job loader (`0.7.6`) or an audited platform operation — and run their database work through
`withTenantTransaction(ctx, fn)`, which sets `app.tenant_id` **transaction-locally** on the connection
that runs `fn`. It is a method of `TenantTransactions`, an injectable the global Prisma module provides,
so Nest wires the client. The actor is explicit: a signed-in member, or the system acting for a job — never an
invented account. Repositories take the transaction client **and the context**, and still write
`tenantId: ctx.tenantId` into their predicates — row-level security is the backstop, not the only filter;
what disappears is any tenant id taken from a caller or from ambient state. A lint rule forbids modules
from importing the root Prisma client; the quarantined modules' existing imports sit in the lint baseline
until each is rebuilt, so a new one fails. The second, unused tenancy mechanism on `PrismaService` — `runWithTenant`,
`getCurrentTenantId`, `getTenantFilter` (`prisma.service.ts:98–120`) — is deleted.
```ts
export type Actor = { kind: 'USER'; userId: UserId; sessionId: SessionId } | { kind: 'SYSTEM'; job: string };   // PLATFORM arrives in 4.1
export type AuthorizedTenantContext = Readonly<{ tenantId: TenantId; actor: Actor; requestId: string; locale: 'ar' | 'en' }>;
export type TenantTx = Prisma.TransactionClient;
@Injectable() export class TenantTransactions {
  withTenantTransaction<T>(ctx: AuthorizedTenantContext, fn: (tx: TenantTx) => Promise<T>): Promise<T>;
}
```
**Tests:** `queries_run_inside_the_tenant_transaction` · `a_context_cannot_be_built_from_request_input` · `the_setting_does_not_outlive_its_transaction`
**Verify:** `just test-int -- tenant-transaction && npm run lint`
**Done when:** the three tests pass and the lint rule rejects a module that imports the root client.

### 0.4.4 — Composite and same-parent foreign keys
**Repo:** backend · **Size:** M · **Depends on:** `0.4.0` · **Requirements:** SYS-TEN-004
**Files:** `prisma/schema.prisma`, migration `20261103181236_tenant_integrity`, `test/db/foreign-keys.integration-spec.ts` (new),
`scripts/preflight.ts` and `test/db/preflight.integration-spec.ts` (`0.4.1`'s preflight reports a rule left with nothing to inspect as
zero, and its test restores the keys from before this step)
Make `Contract.season` (`schema.prisma:638`), `Training.season` (`:834`), `PerformanceRecord.season`
(`:756`), `LegalTicket.assignedTo` (`:975`), `Message.sender` (`:1287`) and `AuditLog.user` (`:1358`)
composite `(…Id, tenantId)` with `RESTRICT`, and give `Document.uploadedById` the composite relation it
lacks; change the two composite `SET NULL`
keys (`scouting_reports_player_id_tenant_id_fkey`, `treatment_sessions_medical_record_id_tenant_id_fkey`) to
`RESTRICT`, because `SET NULL` would null `tenantId` too. Add the **same-parent** keys: a treatment
session references `(medicalRecordId, tenantId, playerId)`, so it cannot cite another player's record;
attendance carries `trainingId`, so its enrollment and session must belong to one program. Constraints
are added `NOT VALID`, validated in a separate statement, and only then is the weaker key dropped.
Every relation also declares `onUpdate: Restrict`: before this step all 67 keys were `ON UPDATE CASCADE`, so a
changed parent key would rewrite its children, `tenantId` included (DB-53).
**Tests:** `foreign_keys_refuse_cross_tenant_edges` · `a_treatment_cannot_cite_another_players_record` · `attendance_cannot_mix_training_programs` · `no_composite_foreign_key_uses_set_null` · `no_foreign_key_cascades_a_key_change`
**Verify:** `just preflight && just migrations && just test-int -- foreign-keys`
**Done when:** raw inserts violating each rule fail in PostgreSQL and `just migrations` reports no drift.

### 0.4.5 — Row-level security on every tenant-owned table; tenant ids immutable
**Repo:** backend · **Size:** L · **Depends on:** `0.4.3`, `0.4.4` · **Requirements:** SYS-TEN-005, BR-RULE-01, SR-ACL-001
**Files:** `src/infrastructure/prisma/model-classification.ts` (new), migration `20261104065628_tenant_rls`,
`scripts/generate-rls.ts` (new), `test/db/rls.integration-spec.ts` (new), `scripts/preflight.ts` and `justfile` (the
preflight runs as the migrator), `test/harness/{fixtures,session}.ts` and the specs whose fixtures now write as their tenant
Every model is classified `tenant-owned` or `global` in one table; a test fails on an unclassified model
or on any table with a `tenant_id` column that lacks a policy. Each tenant-owned table gets `ENABLE` and
`FORCE ROW LEVEL SECURITY` and one policy for the runtime role:
`USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)` with the same `WITH
CHECK`. `FORCE` holds the owner to the policies too, so each table also gets a read-only policy for the
owner: the preflight (now run as the migrator), the directory view and a data migration's reads see every
tenant, and the owner writes no tenant row — a data migration that must write lifts `FORCE` on its table
inside its own transaction and restores it before the transaction ends. A full `tenants` row is visible
only to its own tenant; host resolution and job discovery read a narrow `tenant_directory` view (`id`,
`slug`, `domain`, `is_active` — nothing else) granted to the runtime role, and to the registry role when
`0.7.6` creates it. Global tables get **per-table** privileges, each in the step that creates the table:
reference data (permissions, the default matrix, currencies) is read-only; `identities` is readable and
insertable only through the identity adapter; `security_events` is insert-only for the runtime role, with
reads through a restricted path (`0.7.3`); the runtime role has no privilege on the migration history. A
trigger refuses any `UPDATE` that changes `tenant_id` (and `tenants.id`). Missing context means no rows and
no writes. RLS separates tenants; it does not replace the policies that separate roles inside one tenant (`0.6`).
**Tests:** `rls_missing_context_denies_reads_and_writes` · `rls_pool_reuse_never_leaks_the_previous_tenant` · `every_tenant_table_has_forced_rls_and_a_policy` · `tenant_ids_cannot_be_updated` · `the_tenant_directory_exposes_only_routing_columns`
**Verify:** `just migrations && just test-int -- rls`
**Done when:** raw SQL as the runtime role cannot read or write tenant B while running as tenant A or
with no context, including across interleaved transactions on one small pool.

### 0.4.6 — Tenant-leading indexes; duplicate indexes dropped
**Repo:** backend · **Size:** S · **Depends on:** `0.4.4` · **Requirements:** SR-DB-006
**Files:** `prisma/schema.prisma`, migration `20261104073137_tenant_indexes`, `test/db/indexes.integration-spec.ts` (new)
Prefix the unprefixed filter indexes ([`../reference/database.md`](../reference/database.md)) with
`tenantId` and drop the redundant `tenants.slug` index that duplicates its unique constraint
(`schema.prisma:278`, `:318`). Only the row's own `id` (the primary key and the unique keys composite foreign
keys reference) may lead instead, and six reviewed uniqueness rules over a parent's id — tenant-safe, since the
parent's id is unique across tenants and the composite key ties it to the row's tenant.
The same catalog test asserts that an index serves every foreign key and that no plain index is a left prefix
of another (a unique index enforces its rule, so it is never redundant). An index serves a key when every
column it leads with, up to and including the one naming the parent's id, is a key column. Seven foreign keys
gain an index — DB-54's six and the uploader's key `0.4.4` added — and 39 redundant indexes go: DB-54's 25,
DB-39's `tenants.slug`, and 13 made redundant once their table's indexes lead with `tenant_id`.
**Tests:** `every_index_on_a_tenant_table_leads_with_tenant_id` · `every_foreign_key_is_served_by_an_index` · `no_index_repeats_the_leading_columns_of_another`
**Verify:** `just migrations && just test-int -- indexes`
**Done when:** the catalog test passes with a short, reviewed allowlist of tenant-safe exceptions.

### 0.4.7 — Money: NUMERIC(19,4) with currency rules
**Repo:** backend · **Size:** M · **Depends on:** `0.4.0` · **Requirements:** —
**Files:** `src/common/money/{money,iso-4217}.ts` (new), `prisma/schema.prisma`, migration `20261104080023_money`,
`src/infrastructure/prisma/model-classification.ts`, `scripts/preflight.{ts,sql}`, `test/db/{money,indexes,preflight}.integration-spec.ts`;
the contract and training DTOs take `Money` when their modules are built (both are empty today)
Money columns become `Decimal @db.Decimal(19, 4)` (today `Decimal(…, 2)` — JOD has three decimals;
`schema.prisma:616, 621, 825, 898`); a global `CurrencyDefinition(code, minorUnitExponent, enabled)` is
seeded with **every active ISO 4217 currency and its official decimals** — every code of list one with
defined minor units, currencies and funds, 165 as published on 17 September 2026 (`iso-4217.ts` records the
source); 0 to 4 decimals, all of which `NUMERIC(19,4)` holds — all enabled (owner decision, 29 September
2026), and read-only to the runtime role; a tenant's default is JOD (the columns' default until `0.4.8` types
`Tenant.defaultCurrency`); enrollment payments capture their own currency, and a stored payment's currency
is never guessed (the migration stops on one without); amounts in different currencies are never added
without a recorded exchange rate. `Money` wraps Prisma's exact decimal and a currency code, validates payable
amounts to the currency's exponent, refuses NaN, infinity, negatives and excess scale **before** PostgreSQL
could round them, and travels as `{ "amount": "1250.500", "currency": "JOD" }` ([ADR-0006](../adr/0006-money.md)).
A key to reference data such as the currencies needs no serving index (`0.4.6`'s test exempts it).
```ts
export class Money { static parse(amount: string, currency: string, at?: string): Money; static fromDatabase(amount: Prisma.Decimal, currency: string): Money; add(other: Money): Money; toDecimal(): Prisma.Decimal; toWire(): { amount: string; currency: CurrencyCode }; format(locale: 'ar' | 'en'): string }
```
**Tests:** `jod_amounts_keep_three_decimals` · `excess_scale_is_refused_not_rounded` · `money_never_passes_through_a_javascript_number` · `every_active_iso_4217_currency_is_seeded_with_its_decimals` · `money_columns_hold_every_currencys_decimals`
**Verify:** `npx vitest run src/common/money && just migrations && just test-int -- money`
**Done when:** `Money.parse('1.255', 'JOD').toWire()` round-trips exactly, `Money.parse('1.255', 'USD')`
is refused, and no money column keeps scale 2.

### 0.4.8 — Calendar dates, instants and tenant time zones
**Repo:** backend · **Size:** M · **Depends on:** `0.4.0` · **Requirements:** SR-CORE-006, UX-007
**Files:** `prisma/schema.prisma`, migration `20261104083217_dates_instants_zones`, `src/common/time/{clock,civil-date,time-zone}.ts` (new),
`test/db/time.integration-spec.ts` (new), `scripts/preflight.sql`, `test/db/{preflight,rls,foreign-keys}.integration-spec.ts`
Civil values — birth dates, passport expiry, contract and season boundaries, and every other field that names
a day (21 columns) — become `DATE`, each keeping the UTC day it was stored on; every instant (90 columns)
becomes `timestamptz(3)`, converted `AT TIME ZONE 'UTC'` only where the preflight shows the
source is known to be UTC — as every value the application wrote is: Prisma stores a DateTime as UTC, the
roles' session zone is UTC, and no database holds real data (OPEN-11). `TrainingSession` gains `startsAt` and
`endsAt` plus an IANA zone, which replace its zoneless `start_time` and `end_time` (existing sessions read in
their tenant's zone). `Tenant` gains typed `timezone` (IANA, validated; default `UTC` until an agency sets its
own), `defaultLocale` (`ar` | `en`; default `ar`, ADR-0008) and `defaultCurrency` (default JOD), which leave the
untyped `settings` JSON; a CHECK keeps them out of it, and a trigger refuses any zone PostgreSQL does not know
by name. Rules take an injected clock ([ADR-0007](../adr/0007-time.md)); `CivilDate` and `TimeZone` are the types
code handles them as.
**Tests:** `a_birth_date_is_the_same_day_in_every_timezone` · `instants_round_trip_in_utc` · `an_invalid_tenant_timezone_is_refused`
**Verify:** `just migrations && just test-int -- time`
**Done when:** a birth date stored from UTC−10 reads back unchanged from UTC+14, and `Tenant.settings`
no longer holds the three typed values.

### 0.4.9 — Normalised emails; lifetime uniqueness with audited reactivation
**Repo:** backend · **Size:** S · **Depends on:** `0.4.0` · **Requirements:** SR-ACL-002
**Files:** `prisma/schema.prisma`, migration `20261104100021_normalized_email`, `src/modules/users/{domain/email.ts,application/use-cases/reactivate-membership.usecase.ts,users.module.ts}`,
`test/db/users.integration-spec.ts` (new), `scripts/preflight.sql`, `test/harness/fixtures.ts`, `src/database/seed.ts`
`normalizedEmail` (NFKC, trimmed, lowercased — `lower(btrim(normalize(email, NFKC), E' \t\r\n'))`, which a
CHECK holds every row to) is unique per tenant **for the life of the membership**: an archived member
(`deletedAt` set) keeps the address reserved, and bringing them back is an audited `ReactivateMembership`
use case — the same membership, its audit entry in the same transaction until `0.7.2`'s audit service writes
it — not a second account. The migration stops, rather than merges, on two members whose addresses collide
once normalised; the preflight's `duplicate_email` rule uses the same form. Email is contact data; it never
links an identity (`0.5.3`).
**Tests:** `emails_are_unique_regardless_of_case_and_spacing` · `an_archived_members_email_stays_reserved` · `reactivation_restores_the_same_membership`
**Verify:** `just migrations && just test-int -- users`
**Done when:** the three tests pass and the preflight reports no duplicate normalised email.

### 0.4.10 — Integrity constraints in SQL: checks, partial uniques, safe defaults, bounded JSON
**Repo:** backend · **Size:** M · **Depends on:** `0.4.4` · **Requirements:** SR-DB-007
**Files:** migration `20261104133235_integrity_constraints`, `scripts/integrity-checks.ts` (new),
`scripts/preflight.sql`, `scripts/preflight.ts`, `prisma/schema.prisma`, `src/common/validation/schemas.ts`,
`test/db/constraints.integration-spec.ts` (new), `test/db/preflight.integration-spec.ts`
The database refuses what is impossible; what is merely unwise (a prospect of 45) stays the API's to
refuse. CHECK constraints for the existing numeric and date fields (non-negative counts, sizes, minutes,
goals and capacity; end dates not before start dates; a scouting score 1 to 10, a pass accuracy 0 to 100;
finite numerics — money amounts finite and not negative, a salary with its period, and a reviewed
constraint trigger that holds each amount to its currency's minor units, with a guard refusing an
exponent change while any amount is in the currency, as [`database.md`](../reference/database.md)
describes; `0.4.7` validates them in `Money`); a partial unique index for **one current season per
tenant** and **one featured image per player**, among live rows; legal notes **internal by default** for
new rows (existing notes keep their value); one shape and a size cap on each JSON column (16 KiB; audit
snapshots 1 MiB, the request-body limit) so metadata cannot become a hidden relational store.
Tenant slugs and domains are lower case by CHECK — a DNS label; the domain in ASCII, punycode for an
Arabic name — and live seasons are unique by name within their tenant (DB-55); every TEXT column gets a
length CHECK equal to its API bound, `PROSE_MAX` (DB-56). `scripts/integrity-checks.ts` is the one list
of the 81 CHECKs: the migration carries them as it printed them, and the preflight reports a row that
would break one (`check_violation`), with `duplicate_current_season`, `duplicate_season_name` and
`duplicate_featured_media` for the indexes. The same spec also holds
`a_player_has_at_most_one_featured_image`, `a_currency_exponent_cannot_change_under_amounts` and
`the_catalog_holds_every_integrity_constraint_by_name`.
**Tests:** `impossible_values_are_refused_by_the_database` · `a_tenant_has_at_most_one_current_season` · `legal_notes_are_internal_by_default`
**Verify:** `just migrations && just test-int -- constraints`
**Done when:** each rule refuses its counter-example in raw SQL, and a catalog test lists every
constraint by name.

### 0.4.11 — UUIDv7 for high-ingest tables
**Repo:** backend · **Size:** S · **Depends on:** `0.4.0` · **Requirements:** SR-DB-002
**Files:** `prisma/schema.prisma`, `src/infrastructure/prisma/model-classification.ts`,
`test/db/ids.integration-spec.ts` (new)
UUID keys stay (v4 by default); append-heavy tables whose index locality matters — audit logs, security
events, outbox and inbox, sessions, messages, notifications — use `@default(uuid(7))`, declared when each
table is created. The classification records which (`ids: 'time-ordered'` on a model's class), so a
reviewer sees the choice. Prisma makes the id, so the column has no SQL default and a raw INSERT supplies
its own; no migration is needed and existing ids are unchanged. Prisma 7's runtime model carries no
defaults, so the test reads each model's `@default` from the schema.
**Tests:** `high_ingest_ids_are_time_ordered`
**Verify:** `just test-int -- ids`
**Done when:** the test passes for `audit_logs`, the one high-ingest table this step migrates; messages and
notifications switch in the migrations of the steps that rebuild them.

### 0.4.12 — The existing modules on the tenant transaction
**Repo:** backend · **Size:** M · **Depends on:** `0.4.5`, `0.1.8` · **Requirements:** SYS-TEN-003
**Files:** `src/modules/users/**`, `src/modules/medical/**`, `src/modules/scouting/**`,
`src/common/decorators/tenant-context.decorator.ts` (new), `src/common/tenancy/tenant-context.ts`,
`test/harness/session.ts`, `test/legacy-modules/tenant-transaction.e2e-spec.ts` (new),
`eslint-suppressions.json`, `.dependency-cruiser-known-violations.json`
Every repository in users, medical and scouting moves onto the transaction client and the verified
context: a tenant id passed in by a caller becomes `ctx.tenantId`, still written explicitly into each
predicate. A handler receives the context the session guard minted through `@CurrentTenantContext()`
(in tests, the test session guard mints it, as `0.5.6`'s will); the acting member — a report's scout, a
record's author — comes from it (`actingMemberOf`). Each use case depends on a port in its module's
`application/ports/`, which the module wires to the repository, so the reads and deletes controllers made
directly become small use cases, and the lint suppressions and boundary baseline of both modules go. The
quarantined modules are exercised with their flags on. `PermissionService` reads only the global
permission tables and waits for `0.6.1`.
Their ordinary reads exclude archived rows: the archive rule of `database.md` (DB-57).
**Tests:** `medical_reads_see_only_the_context_tenant` · `scouting_writes_are_stamped_with_the_context_tenant`
**Verify:** `just test-e2e -- test/legacy-modules` (the spec switches `FEATURE_MEDICAL` and `FEATURE_SCOUTING` on itself)
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
**Files:** `infra/keycloak/realm-sadara.json` (new), `infra/keycloak/blocked-passwords.txt` (new),
`infra/keycloak/test-realm.sh` (new), `infra/keycloak/README.md`, `infra/compose.yaml`, `infra/.env.example`,
`infra/proxy/Caddyfile`, `justfile` (`realm-reset`)
The realm is a reviewed file, imported at start. Client `sadara-api`: confidential, standard flow only,
**PKCE S256 required**, exact redirect and post-logout URIs per tenant host, back-channel logout URL
with session required. Authentication: password policy length ≥ 12 with no composition rules and a
blocked-password list; brute-force detection with temporary lockout; email verification; a conditional
flow mapping **MFA (OTP or WebAuthn) to level of assurance 2**; WebAuthn and passkeys available without
being required, so they can be adopted without changing any business API. Locales Arabic and English;
mail to Mailpit. Capabilities the pinned release does not provide (for example an `amr` claim) are
recorded, not assumed.
The realm stores its login and admin events — failed sign-ins, lockouts, MFA changes — for a stated
retention, so that `0.7.3` can import them (DB-61).
As built: the client secret is a placeholder the import resolves from `infra/.env`
(`SADARA_API_CLIENT_SECRET`); the redirect URIs are `https://{host}/api/v1/auth/callback` and the post-logout
URIs `https://{host}/` for each host of the proxy's Caddyfile; back-channel logout goes to the API on this
machine. The blocked list is the 12-character-and-longer entries of the NCSC's 100,000 most-used passwords
(SecLists, pinned; provenance in the README). The lockout is Keycloak's default temporary one (30 failures,
waits from 60 s to 15 minutes), within NIST SP 800-63B's limit. Level 1 lasts 12 hours (the session's
absolute lifetime, OPEN-02), level 2 five minutes (the step-up window). Events are kept without expiry
(OPEN-06). Keycloak 26.7.4 has an `amr` mapper; the realm asserts assurance through `acr` instead. Keycloak
imports a realm only when it is missing, so `just realm-reset` starts Keycloak fresh on a changed file.
`test-realm.sh` holds ten checks, the three named tests among them.
**Tests:** `the_api_client_requires_pkce` · `brute_force_detection_is_enabled` · `mfa_maps_to_assurance_level_2`
**Verify:** `just up && bash infra/keycloak/test-realm.sh`
**Done when:** the realm imports on a fresh stack and the script proves each setting from the running
server's admin API, not from the file.

### 0.5.2 — Resolve the tenant from the host
**Repo:** backend · **Size:** S · **Depends on:** `0.4.5` · **Requirements:** —
**Files:** `src/common/tenancy/tenant-resolver.ts` (new), `src/common/tenancy/tenant-resolver.spec.ts` (new),
`src/config/env.schema.ts`, `src/config/env.schema.spec.ts`, `.env.example`,
`src/infrastructure/prisma/prisma.module.ts`, `test/auth/tenant-resolution.e2e-spec.ts` (new)
Before anyone is signed in, the tenant comes from the host, read through the `tenant_directory` view:
an exact `Tenant.domain`, else `{slug}.{APEX_DOMAIN}`; the single-agency launch may map an **explicitly
allowlisted** host to `DEFAULT_TENANT_SLUG`, and every other host is refused. The host is taken from a
forwarded header only when the request came through the configured trusted proxy. An inactive tenant is
refused, and an unknown host looks exactly like "no account here". The resolved tenant scopes the
sign-in transaction and the membership lookup; after sign-in the session is the only source of tenant.
As built: `TenantResolver.resolve(request)` reads the host Express reads — `X-Forwarded-Host` only from a
peer `TRUSTED_PROXIES` names (`0.3.8`) — in lower case, without the port or a trailing dot; anything that
is not a host name resolves to nothing. The slug is one label under `APEX_DOMAIN`, never two. "No account
here" is `NoAccountHereError`, an ordinary 404 `NOT_FOUND` that never repeats the host; `0.5.5` gives a
person with no membership the same answer. The settings live in `src/config/env.schema.ts` beside every
other variable, not in an `app.config.ts`: `APEX_DOMAIN` (`localhost` locally), and `DEFAULT_TENANT_SLUG`
with `DEFAULT_TENANT_HOSTS`, which must be set together or the API refuses to boot. An empty `NAME=`
counts as unset, and a setting that fails its pattern says what the pattern wants. Until sign-in exists,
the e2e test asks the resolver through a test-only probe route.
**Tests:** `sign_in_uses_the_tenant_of_the_host` · `an_unknown_host_looks_like_no_account` · `an_inactive_tenant_cannot_sign_in`
**Verify:** `just test-e2e -- test/auth/tenant-resolution.e2e-spec.ts`
**Done when:** the three tests pass on `sadara.localhost` and `other.localhost`.

### 0.5.3 — Identities, memberships and sessions in the schema
**Repo:** backend · **Size:** M · **Depends on:** `0.4.5` · **Requirements:** —
**Files:** `prisma/schema.prisma`, migration `20261105075926_identity_sessions`,
`src/infrastructure/prisma/model-classification.ts`, `scripts/generate-rls.ts`,
`test/db/identity.integration-spec.ts` (new), and the catalog tests whose inventories grew
(`test/db/{rls,indexes,constraints,ids,time}.integration-spec.ts`)
`Identity(id, issuer, subject, createdAt)` is global and unique on `(issuer, subject)`; the tenant `User`
is the **membership**, with `identityId` unique per tenant, and keeps its id so every business foreign
key survives. `UserSession` (tenant-owned, UUIDv7, under RLS) stores only the hash of the session
token — the CSRF token is derived from it and never stored (`0.5.6`) — the identity provider's `sid`,
the `acr`, `amr` and `auth_time` it asserted, idle and absolute
expiry, and revocation. An identity is never linked by email alone.
As built: identities take a new global class, `append-only`: the runtime role reads and adds them and
never updates or deletes one (`generate-rls.ts` prints the `REVOKE`); being global, they have no tenant
policy. The subject is at most 255 characters (OpenID Connect Core 1.0 §2), the issuer 500. One
membership per identity and tenant is keyed `(identity_id, tenant_id)`, so the same index serves the key
to identities. A session's key to `users` is `(user_id, tenant_id, identity_id)`: it names the member,
its tenant and its linked identity together. The token's SHA-256 digest is unique within its tenant,
`(tenant_id, token_hash)`, since every tenant index leads with `tenant_id` (`0.4.6`) and a session is
looked up only inside the host's tenant. `revoke_reason` is an enum of the five ways `0.5.7` and `0.5.8`
end a session early. CHECKs hold the digest to 32 bytes, idle expiry to the absolute, a revocation to its
reason and the revision from 1; the identity's issuer and subject are never empty.
**Tests:** `an_identity_links_to_at_most_one_membership_per_tenant` · `sessions_store_only_token_hashes`
**Verify:** `just migrations && just test-int -- identity`
**Done when:** both tests pass as the runtime role and the new tables carry forced RLS.

### 0.5.4 — The identity-provider port and the Keycloak adapter
**Repo:** backend + umbrella · **Size:** L · **Depends on:** `0.5.1`, `0.5.3` · **Requirements:** SR-AUTH-001
**Files:** backend `src/modules/identity/application/ports/identity-provider.port.ts` (new),
`src/modules/identity/infrastructure/keycloak/{oidc-relying-party,keycloak-identity-provider}.ts` (new),
`src/modules/identity/identity.module.ts` (new), `src/app.module.ts`, `src/config/env.schema.ts`, `.env.example`,
`vitest.config.mts` (a `keycloak` project), `test/support/test-issuer.ts` (new),
`test/identity/identity-provider.integration-spec.ts` (new), `test/identity/keycloak-accounts.keycloak-spec.ts`
(new); umbrella `infra/keycloak/{realm-sadara.json,test-realm.sh,README.md}`, `infra/compose.yaml`, `infra/.env.example`
One port hides the provider. Protocol calls use a certified OIDC client library: discovery, JWKS cached
with rotation, an allowlisted issuer, and ID-token verification of `iss`, `aud`, `azp`, `exp`, `iat` and
`nonce`. Administration calls use the provider's admin API with a least-privilege service account.
Automated tests run against an in-process test issuer (which can mint malformed and hostile tokens);
realm behaviour is proven against Keycloak itself in `0.5.1` and at the gate.
```ts
export abstract class IdentityProviderPort {
  authorizationUrl(p: { redirectUri: URL; state: string; nonce: string; codeChallenge: string; loginHint?: string; acrValues?: string; locale: 'ar' | 'en' }): Promise<URL>;
  exchange(p: { callbackUrl: URL; codeVerifier: string; expectedState: string; expectedNonce: string }): Promise<VerifiedSignIn>;   // issuer, subject, sid, acr, amr, authTime, email, emailVerified
  verifyLogoutToken(jwt: string): Promise<{ subject?: string; sid?: string }>;
  createAccount(email: string, locale: 'ar' | 'en', requiredActions: RequiredAction[]): Promise<{ subject: string }>;
  sendSetupEmail(subject: string): Promise<void>;
  disableAccount(subject: string): Promise<void>;
}
```
As built: the port is an abstract class in `application/ports/`, as every port is since `0.4.12`, and
two signatures changed. `authorizationUrl` takes the callback of the host the browser came from and
returns a promise, because discovery happens on first use, never at boot. `exchange` takes the URL
the browser came back to, with the expected state and nonce, because the token request repeats that
host's callback and Keycloak's answer carries `iss`, which is checked. The library is openid-client 6
(OpenID Certified), with jose 6 for logout tokens. ID-token signatures are checked against the
issuer's keys (`enableNonRepudiationChecks`; the library otherwise trusts TLS) and RS256 is pinned,
since Keycloak also advertises HMAC algorithms; the adapter refuses an `iat` in the future, which the
library does not. The key set is the library's cache: five minutes, or one when a token names an
unknown key. A refusal is `ProviderAnswerRefusedError` (401 `AUTHENTICATION_REQUIRED`), naming the
failed check and never a value; a provider that does not answer is `DependencyUnavailableError`.
The admin calls go through the realm's admin REST API as `sadara-admin`, an umbrella service account
holding only `manage-users` (`test-realm.sh` proves its reach); a subject that is not shaped like a
Keycloak id is not found, every call times out after 10 s, and an expired admin token is renewed once.
Five settings are required (`OIDC_ISSUER`: HTTPS, or HTTP on this machine; two client ids and their
secrets). Readiness (`0.3.7`) does not call the provider: its settings are checked at boot, and a
provider that is down stops new sign-ins, not the sessions Sadara already holds. Accounts are created
without a name, so Keycloak's default profile asks for one at the first sign-in (`0.5.10`).
**Tests:** `id_tokens_from_another_issuer_are_refused` · `id_tokens_for_another_audience_are_refused` · `a_mismatched_nonce_is_refused` · `rotated_signing_keys_are_accepted`
**Verify:** `just test-int -- identity-provider`; the admin calls, with the stack up: `npx vitest run --project keycloak`
**Done when:** the four tests pass against the test issuer and the adapter's admin calls pass against
the compose Keycloak.

### 0.5.5 — Sign-in through the API: authorization code with PKCE
**Repo:** backend · **Size:** L · **Depends on:** `0.5.2`, `0.5.4` · **Requirements:** SR-CORE-001
**Files:** `src/modules/identity/presentation/{auth.controller,dto/sign-in.dto}.ts` (new),
`src/modules/identity/application/use-cases/sign-in.usecase.ts` (new), `src/modules/identity/application/ports/sign-in-attempts.port.ts`
(new), `src/modules/identity/infrastructure/valkey/valkey-sign-in-attempts.ts` (new),
`src/modules/identity/domain/{return-path,secrets,session-lifetime}.ts` (new), `src/modules/identity/identity.module.ts`,
`src/common/tenancy/auth-bootstrap.ts` (new), `src/infrastructure/prisma/prisma.module.ts`,
`src/common/security/session-cookies.ts` (new), `src/common/openapi/{responses,contract}.ts` (`@Redirects`),
`openapi/openapi.json`, `test/harness/app.ts`, `test/auth/sign-in.e2e-spec.ts` (new), and the route inventories that
now hold sign-in's routes (`test/auth/retirement.e2e-spec.ts`, `test/platform/{versioning,contract}.e2e-spec.ts`)
`GET /api/v1/auth/login?returnTo=` stores a one-time login transaction (state, nonce, PKCE verifier,
tenant, validated same-origin `returnTo`) in Valkey for ten minutes — losing it only aborts a sign-in —
and **binds it to the initiating browser** with a short-lived `__Host-Http-sadara_preauth` cookie (HttpOnly,
Secure, SameSite=Lax, `Path=/`, no `Domain`) that grants no access and is cleared at the callback; for a step-up the existing session plays that role. It then
redirects to the provider with the tenant's locale. `GET /api/v1/auth/callback` requires the pre-auth cookie to match, consumes the state
once, exchanges the code, verifies the ID token, and looks up the membership of **that identity in the
host's tenant**: none, archived or inactive means a refusal page and no session (and a security event,
`0.7.3`); otherwise this step creates the `UserSession` row, issues the `__Host-Http-sadara_session` cookie ([ADR-0023](../adr/0023-session-cookies-per-rfc-10017.md)) and returns
the browser to `returnTo`. Both routes are in the `auth` rate-limit category (`0.3.8`): the guard counts by
address, and the callback also counts by account, through `RateLimiter.take('auth', 'account:<id>')`, once
the ID token names the identity. Authenticating later requests with it, expiry and CSRF are `0.5.6`.
As built: both routes answer a `303` with `Cache-Control: no-store`; the contract declares it with
`@Redirects` (a `Location`, no body), the one success that is not `{ data }`. The attempt is keyed in
Valkey by the SHA-256 of its state and taken with `GETDEL`; it holds the digest of the pre-auth cookie,
never its value, and a browser that already holds a pre-auth cookie keeps it, so sign-ins begun in two
tabs both finish. The callback checks, in order, the pre-auth cookie, the state, the cookie's digest
(constant-time), the host's tenant against the attempt's, then exchanges the code; it clears the pre-auth
cookie whatever the outcome. An ID token without `auth_time` is refused, since `0.5.8` measures recent
authentication from it; the account counted is the digest of issuer and subject. The membership is read,
and the session opened, in one transaction of the host's tenant by `AuthBootstrap` (`src/common/tenancy`),
the narrow pre-session access [architecture](../reference/architecture.md) calls AuthBootstrapRepository:
it selects authentication fields only, mints no context, and a module still cannot reach the root client.
The session cookie holds 256 random bits for 12 hours; the row holds its SHA-256, the provider's `sid`,
`acr`, `amr` and `auth_time`, idle expiry at 30 minutes and absolute at 12 hours. The refusal page is the
`404` "no account here" problem `0.5.2` gives an unknown host; the web app's page comes with `0.9.5`. A
return path is a path on this origin: one leading `/`, no backslash, white space or control character,
at most 2,048 characters, still on this origin once resolved. A browser that signs in again gets a new
session; the one its old cookie named expires idle, and revoking it belongs to `0.5.7`/`0.5.8`.
**Tests:** `a_member_signs_in_end_to_end` · `a_non_member_gets_no_session` · `a_replayed_or_mismatched_state_is_refused` · `a_callback_from_another_browser_is_refused` · `return_to_cannot_leave_the_origin`
**Verify:** `just test-e2e -- test/auth/sign-in.e2e-spec.ts`
**Done when:** the five tests pass against the test issuer — including a login-CSRF attempt, in which a
callback completed in a browser that did not start the sign-in creates no session.

### 0.5.6 — Server sessions, the session cookie and CSRF
**Repo:** backend · **Size:** L · **Depends on:** `0.5.5`, `0.3.8` · **Requirements:** SR-AUTH-003, SR-ACL-007
**Files:** `src/modules/identity/application/session.service.ts` (new), `src/common/guards/session.guard.ts`
(replaces the placeholder), `src/common/security/{csrf.guard,csrf-tokens}.ts` (new), `src/common/tenancy/auth-bootstrap.ts`,
`src/modules/identity/application/{ports/session-views.port,use-cases/read-session.usecase}.ts` (new),
`src/modules/identity/infrastructure/repositories/session-view.repository.ts` (new),
`src/modules/identity/presentation/{auth.controller,dto/session.dto}.ts`, `src/common/interfaces/request-with-user.interface.ts`,
`src/config/env.schema.ts` (`CSRF_SECRET`, `CSRF_SECRET_PREVIOUS`), `eslint.config.mjs` (the guard mints contexts),
`src/common/openapi/contract.ts`, `openapi/openapi.json`, `test/harness/session.ts` (real sessions),
`test/auth/sessions.e2e-spec.ts` (new), and the six earlier tests that sign in through the harness
The session `0.5.5` issued is one random 256-bit value in `__Host-Http-sadara_session` (HttpOnly, Secure,
SameSite=Lax, Path=/ — [ADR-0023](../adr/0023-session-cookies-per-rfc-10017.md)); PostgreSQL holds only its hash. This step makes it authenticate requests. **Every request checks the session, the membership and the
tenant against PostgreSQL** — not a cache — so revocation and deactivation take effect on the very next
request; a cache may come later only with a tested consistency protocol. Idle expiry 30 minutes, absolute
12 hours (provisional — OPEN). Writes need the session's synchronizer token in `X-CSRF-Token`, an
`Origin` equal to the configured origin, **and** `Sec-Fetch-Site: same-origin` when the browser sends
fetch metadata; non-JSON bodies are refused. The token is derived, not stored —
an HMAC of the session's token hash under a keyed, rotatable secret — so it stays the same in every tab
until the session rotates. `GET /api/v1/auth/session` returns
the member, the tenant and the CSRF token. The guard mints the `AuthorizedTenantContext`.
As built: the session is found by the SHA-256 of its cookie in the host's tenant, through
`AuthBootstrap.sessionOf`, and the guard mints the context from it alone — a tenant the request names
changes nothing. No cookie, a host with no active tenant, an unknown or revoked session, or a member no
longer active is `401 AUTHENTICATION_REQUIRED`; past either expiry, `401 SESSION_EXPIRED`. Renewal moves
the idle expiry 30 minutes on, never past the absolute one, and writes at most once a minute per session,
so a session may lapse up to a minute early, never late. The `Origin` a write needs is `https://` and the
host it came to: each tenant has its own host (`0.5.2`), so one configured origin cannot serve them, and
another tenant's host is refused. The CSRF guard runs after the session guard and the rate limit, before
permissions; a failure is `403 CSRF_FAILED`, then a body that is not JSON is `415`. The token is
HMAC-SHA-256 under `CSRF_SECRET` (32 characters at least, no default) with a purpose prefix;
`CSRF_SECRET_PREVIOUS` keeps the old key's tokens valid while it rotates. `GET /api/v1/auth/session`
answers the member (id, role, name), the tenant (id, slug, name, language) and the token, `no-store`,
read through the tenant transaction as the context's own session. The request holds the session's member
only (id, tenant, role), never a user row. The test harness's stand-in guard is retired: `signedInAs`
opens a real session and returns its host, cookie, `Origin` and token, so every API test goes through
the real guards.
**Tests:** `the_session_cookie_is_host_only_httponly_and_secure` · `a_write_without_the_csrf_token_is_refused` · `a_write_from_another_origin_is_refused` · `a_cross_site_fetch_is_refused_even_with_the_token` · `a_revoked_session_fails_on_the_next_request` · `a_deactivated_member_loses_access_on_the_next_request`
**Verify:** `just test-e2e -- test/auth/sessions.e2e-spec.ts`
**Done when:** the six tests pass.

### 0.5.7 — Sign-out, back-channel logout and session management
**Repo:** backend · **Size:** M · **Depends on:** `0.5.6` · **Requirements:** SR-AUTH-007
**Files:** `src/modules/identity/presentation/{auth.controller,dto/session-management.dto}.ts`,
`src/modules/identity/application/use-cases/{sign-out,own-sessions,backchannel-logout}.usecase.ts` (new),
`src/modules/identity/application/ports/{own-sessions,logout-token-replays,identity-provider}.port.ts`,
`src/modules/identity/infrastructure/repositories/own-session.repository.ts` (new),
`src/modules/identity/infrastructure/valkey/{identity-valkey,valkey-logout-token-replays,valkey-sign-in-attempts}.ts`,
`src/modules/identity/infrastructure/keycloak/{oidc-relying-party,keycloak-identity-provider}.ts`,
`src/common/tenancy/auth-bootstrap.ts`, `src/common/validation/schemas.ts` (`cursorPaging`), `openapi/openapi.json`,
`test/harness/session.ts`, `test/identity/identity-provider.integration-spec.ts`, `test/auth/session-management.e2e-spec.ts`
(new), and the route inventories (`test/auth/retirement.e2e-spec.ts`, `test/platform/versioning.e2e-spec.ts`)
`POST /api/v1/auth/logout` revokes the session, clears the cookie with its original attributes and
returns the provider's end-session URL; `POST /api/v1/auth/logout-all` revokes every session of the
member; `GET /api/v1/auth/sessions` and `DELETE /api/v1/auth/sessions/{id}` manage one's **own** sessions
(another member's is a 404). `POST /api/v1/auth/backchannel-logout` verifies the logout token fully —
issuer, audience, `iat`, `jti` replay, the logout event, `sid` or `sub` — and revokes the matching
sessions. **The exposure window, stated:** app-side revocation and deactivation are immediate;
provider-side changes (a disabled account, a reset) reach Sadara through a back-channel event, and if that
event is lost, at the session's idle or absolute expiry at the latest. The owner accepts this window
(OPEN); offboarding is therefore done in Sadara, which is immediate.
As built: the sessions end in PostgreSQL first (`SIGN_OUT`, `SIGN_OUT_EVERYWHERE`, `REVOKED_BY_MEMBER`); the
end-session URL returns to `https://{host}/`, which the realm registers per host (`0.5.1`), and names the
client, since no ID token is kept; if the provider does not answer it is `null` and the sign-out holds.
"Everywhere" is the member's membership of this tenant: the same person's membership of another tenant
keeps its sessions. The list shows a session's id, its sign-in and last use, its expiries, its `acr` and
whether it is this browser's, by cursor (`0.3.5`), the cursor bound to its member; ending this browser's
own session clears its cookie. Back-channel logout is public — the signed token is its proof, and a test
holds it to being the only public write, since the CSRF guard exempts public routes. The adapter (`0.5.4`)
now refuses a logout token older than five minutes or issued in the future, and returns its issuer,
`jti` and `iat`; the `jti` is recorded in Valkey with `SET NX` for ten minutes, and released if ending
the sessions fails, so the provider may retry. A named subject is resolved to its identity first, so each
tenant's lookup is the `(tenant_id, identity_id, provider_sid)` index; every tenant is visited, switched
off or not, each in its own transaction; a token naming only a `sid` ends that session, one naming
neither ends nothing. A refused or replayed token is `400` on `/logout_token`, as OpenID Connect
Back-Channel Logout 1.0 (2.8) asks. The identity module shares one Valkey connection. The three
addresses the retired credential system used (`POST /auth/logout`, `POST /auth/logout-all`,
`GET /auth/sessions`) return as session routes, which the retirement test (`0.1.6`) names explicitly.
**Tests:** `logout_revokes_the_session_server_side` · `logout_everywhere_revokes_every_session` · `a_member_cannot_revoke_another_members_session` · `a_valid_back_channel_logout_revokes_matching_sessions` · `a_forged_or_replayed_logout_token_is_refused`
**Verify:** `just test-e2e -- test/auth/session-management.e2e-spec.ts`
**Done when:** the five tests pass.

### 0.5.8 — MFA assurance for privileged roles; recent authentication for sensitive actions
**Repo:** backend · **Size:** M · **Depends on:** `0.5.6` · **Requirements:** SR-AUTH-002
**Files:** `src/modules/identity/application/assurance.policy.ts` (new), `src/common/decorators/requires-recent-auth.decorator.ts` (new),
`src/common/guards/recent-auth.guard.ts` (new), `src/app.module.ts`, `src/common/errors/domain-error.ts` (`StepUpRequiredError`),
`src/common/filters/problem-details.filter.ts` and `src/common/openapi/{contract,responses}.ts` (`stepUpUrl`),
`src/common/tenancy/auth-bootstrap.ts`, `src/common/guards/session.guard.ts`, `src/modules/identity/application/{session.service,use-cases/sign-in.usecase,ports/*}.ts`,
`src/modules/identity/infrastructure/{keycloak,valkey}/**`, `src/modules/identity/presentation/auth.controller.ts`,
`src/modules/scouting/presentation/scouting.controller.ts`, `openapi/openapi.json`, `test/harness/session.ts`,
`test/identity/identity-provider.integration-spec.ts`, `test/auth/assurance.e2e-spec.ts` (new)
Members holding a privileged role — owner, admin, legal, finance, medical, physiotherapist, sporting
director by default; tenant-configurable in `1.1.2` — get **no session** until the provider asserts level
of assurance 2: the callback sends them back with `acr_values` for step-up. Sensitive actions (role and
permission changes, approvals, signature evidence, confidential exports, support grants) require
authentication within the last five minutes, else `403 STEP_UP_REQUIRED` with a re-authentication URL;
a successful step-up updates the existing session.
As built: the privileged roles are the plan's seven and `SUPER_ADMIN`, as the safe default; a second
factor is the realm's `acr` "2" (`0.5.1`). A privileged member's level-1 sign-in gets no session: the
callback sends the same browser back with `acr_values=2`, keeping its pre-auth binding, and refuses (`401`)
if the factor is asked for and still not given, so it never loops. The rule holds on every request too:
a session whose member's role now needs level 2, and which never proved it, is refused, so a promotion
cannot skip the factor. `@RequiresRecentAuth()` (`RecentAuthGuard`, global, after permissions) needs an
authentication within five minutes; otherwise `403 STEP_UP_REQUIRED` carries `stepUpUrl`, an RFC 9457
extension member naming `/api/v1/auth/step-up`, to which the client adds `returnTo` — the API cannot
know the page a request came from. Scouting's approve and reject are marked; the other sensitive actions
take the decorator as their steps build them. `GET /api/v1/auth/step-up` asks the provider for a fresh
authentication (`max_age=0`, checked against `auth_time`) and, for a privileged role, level 2; the attempt
is bound to the session the browser holds. Its callback updates that session in one transaction — the
same id, sign-in time and absolute expiry; new `auth_time`, `acr`, `amr` and provider `sid`; **its token
replaced** (OWASP, on a rise in privilege), the cookie living only to the absolute expiry — and only if
the same person authenticated in the same browser, the row still holds the current token, and the
assurance holds; otherwise nothing changes. The test harness opens a privileged member's session at
level 2, as sign-in requires.
**Tests:** `a_privileged_member_without_mfa_gets_no_session` · `a_sensitive_action_requires_recent_authentication` · `step_up_upgrades_the_existing_session`
**Verify:** `just test-e2e -- test/auth/assurance.e2e-spec.ts`
**Done when:** the three tests pass against the test issuer, and the gate repeats the first against
Keycloak.

### 0.5.9 — The tenant provisioning command
**Repo:** backend + umbrella · **Size:** M · **Depends on:** `0.5.4` · **Requirements:** BR-OBJ-08
**Files:** backend `src/cli/provision-tenant.ts` (new), `package.json` (`tenant:provision`),
`src/modules/platform/{provisioning.module,application/ports/provisioning-records.port,application/use-cases/provision-tenant.usecase,infrastructure/repositories/provisioning.repository}.ts`
(new), `src/modules/identity/identity-admin.module.ts` (new), `src/modules/identity/application/ports/provider-clients.port.ts` (new),
`src/modules/identity/application/ports/identity-provider.port.ts` (`findAccount`),
`src/modules/identity/infrastructure/keycloak/{keycloak-admin-api,keycloak-provider-clients}.ts` (new),
`src/modules/identity/infrastructure/keycloak/keycloak-identity-provider.ts`, `src/config/env.schema{,.spec}.ts`, `.env.example`,
`eslint.config.mjs` (a context minter), `vitest.config.mts`, `test/cli/provision-tenant.keycloak-spec.ts` (new); umbrella
`infra/keycloak/{realm-sadara.json,test-realm.sh,README.md}`, `infra/compose.yaml`, `infra/.env.example`
A command, not an endpoint, and an audited platform operation: it creates the tenant and its domain,
registers the tenant's redirect URIs with the provider, creates the owner's provider account with the
required actions (verify email, set password, configure MFA), links the identity to an `OWNER`
membership and asks the provider to send the setup email. It never accepts a password and is idempotent
per slug.
```
npm run tenant:provision -- --slug sadara --name "Sadara Sports Agency" --domain sadara.example --owner-email owner@sadara.test
```
The slug and domain are stored in lower case (DB-55).
As built: the command is the third context minter `0.4.3` allows, listed in `eslint.config.mjs`; its work
is `ProvisionTenantUseCase` in a `platform` module, which `ProvisioningModule` composes with the database
and the provider's administration only — no routes, sessions or Valkey. Arguments are parsed strictly:
an option naming a password, a secret or a credential is refused (exit 2) before anything is read, its
value never repeated, and every other unknown option or stray value is refused too. Beyond the plan,
`--locale ar|en` sets the tenant's language and the setup email's, `--resend-setup-email` sends it again,
and `--domain` is optional when `APEX_DOMAIN` gives the host `{slug}.APEX_DOMAIN`. A membership already
holding the owner's address must be the owner's identity's, as `OWNER`, checked before the provider is
touched so that a refusal leaves nothing there; one with no identity is never linked by address alone
(`0.5.3`). Each host is registered on `sadara-api` by its exact callback and post-logout address, never a
wildcard, by read-and-replace as Keycloak's admin API requires (two runs at once could race; a rerun
repairs it). That needs `manage-clients`, which the API's account deliberately lacks, so the umbrella
adds `sadara-provisioner`, a service account holding only that role, which the command alone uses
(`OIDC_PROVISIONER_CLIENT_ID`, `OIDC_PROVISIONER_CLIENT_SECRET`; the API neither reads nor requires them);
`test-realm.sh` proves its reach. The role reaches every client in the realm; fine-grained admin
permissions could narrow it later. The admin-API plumbing — token, one renewal, 10 s timeout, no redirect
— is `KeycloakAdminApi`, shared with `sadara-admin`. The owner's account is found by exact address or
created with verify email, set password and configure OTP, never a credential; the identity, the
membership and one `tenant.provisioned` audit entry (what changed; no address, no name) are written in
one transaction, and only when something changed. The setup email goes when the account is made, or on
request. The report is JSON without the address; exit 1 is a failed operation, whose message holds no
value, and a rerun finishes what it left. The Done-when needs the compose Keycloak, which CI does not
have, so the tests are a `keycloak` project spec, which now has a schema of its own; a fourth,
`provisioning_never_links_a_membership_by_address_alone`, covers the membership check. Keycloak's
default profile asks the new owner for a name at their first sign-in (`0.5.10`).
**Tests:** `provisioning_creates_a_tenant_and_an_invited_owner` · `provisioning_is_idempotent_per_slug` · `provisioning_never_accepts_a_password`
**Verify:** with the stack up, `bash -c 'source ./scripts/test-database.sh && npx vitest run --project keycloak test/cli'`
**Done when:** the three tests pass against the compose Keycloak.

### 0.5.10 — Invitations
**Repo:** backend · **Size:** M · **Depends on:** `0.5.9`, `0.5.6`, `0.5.8` · **Requirements:** —
**Files:** `prisma/schema.prisma` + migrations `…_invitations` and `…_invite_permission`,
`src/modules/users/{users.module,application/role-grants.policy{,.spec},application/ports/invitation-records.port,application/use-cases/{invite-member,manage-invitations,issue-invitation-token}.usecase,domain/invitation{,.spec},domain/email{,.spec},infrastructure/repositories/invitation.repository,presentation/invitations.controller,presentation/dto/invitation.dto}.ts`
(new or changed), `src/modules/users/application/services/permission.service.ts`, `src/shared/constants/permissions.constants.ts`,
`src/common/tenancy/auth-bootstrap.ts`, `src/modules/identity/{application/ports/sign-in-attempts.port,application/use-cases/sign-in.usecase,infrastructure/valkey/valkey-sign-in-attempts,presentation/auth.controller,presentation/dto/sign-in.dto}.ts`,
`src/infrastructure/prisma/model-classification.ts`, `scripts/generate-rls.ts`, `openapi/openapi.json`,
`test/db/{invitations,constraints,rls,time}.integration-spec.ts` (the first new), `test/legacy-modules/tenant-transaction.e2e-spec.ts`,
`test/users/invitations.e2e-spec.ts` (new)
`POST /api/v1/users/invitations` (`user.invite`, recent authentication) creates or finds the invitee's
provider account and an `Invitation` — email, role, seven-day expiry. Its single-use token is generated
**by the delivery handler at send time** (`0.7.8`), which stores only its hash and puts the raw value only
in the email — so no outbox payload, log or table ever holds a usable link; a resend issues a new token;
the inviter cannot grant a role above their own. The emailed link starts a sign-in that carries the
invitation; the callback binds the membership only when **both** the token matches **and** the provider
asserts that verified email — proof of mailbox and identity, never email alone. Acceptance is in the `auth`
rate-limit category (`0.3.8`), counted by address and, once the invitation names it, by account. `DELETE` revokes; the
list shows pending, accepted, expired and revoked.
The invitation records the locale its email is written in: the inviter's choice, else the tenant's
default (DB-68).
As built: the plan gives no order for "above their own", and `ROLE_HIERARCHY` goes in `0.6.2` (DB-58
forbids comparing by enum order), so `role-grants.policy.ts` writes one out: an owner grants any tenant
role, another owner included; an administrator any but ownership; every other role nothing; nobody
`SUPER_ADMIN`, which the request schema, the policy and a CHECK each refuse. The invitation stores a typed
`role` where the schema contract wrote `rolePolicyKey`, until per-tenant roles (`4.1.4`). Inviting checks
the grant, that no membership (archived ones included, `0.4.9`) holds the address and that no pending
invitation names it, before the provider is asked for anything and again as the row is written; it finds
or makes the invitee's provider account with verify email and set password, and a second factor for a
privileged role (`0.5.8`), never a password. An expired open invitation is revoked when its address is
invited again, and one open invitation per address is a partial unique index. `IssueInvitationToken` is
what `0.7.8`'s delivery calls: 256 random bits at send time, only the SHA-256 digest stored, a new one
replacing the last, and only for a pending invitation. Acceptance is a sign-in, so it lives in the
identity module and `AuthBootstrap`, not only `src/modules/users/**`: `GET /api/v1/auth/login?invitation=`
starts one only while the invitation is pending (else `404`), with `login_hint` and the invitation's
language, the attempt keeping the digest, never the token; the callback counts the proven account
(`0.5.5`'s count) and then `acceptInvitation` holds the row and binds the membership in one audited
transaction only with the token, the provider's verified address and the inviter's authority, which is
checked again at acceptance — an administrator demoted before their invitation is used no longer grants
`ADMIN` ("active inviter authority", `domain-workflows.md`). A refusal changes nothing and answers `401`
as any refused sign-in does. Two migrations, since PostgreSQL cannot use an enum value in the transaction
that adds it: `…_invitations` adds `permission_action` `INVITE` and the table, and `…_invite_permission`
writes `user.invite` for `OWNER` and `ADMIN`, the only permission row until `0.6.1` syncs the catalog.
The row records the member it made as well as the identity, through the composite key to
`users(id, tenant_id, identity_id)`; the runtime role cannot delete invitations, which the model
classification now says with a `kept` class that `generate-rls` and the catalog tests read. Beyond the
plan: a status filter on the list, and six more tests — the second factor, the inviter's authority, the
token and verified address each required, the list and revoking, a taken address, recent authentication
— with `invitations_hold_their_rules_in_the_database` for the CHECKs. CodeQL found `normalizeEmail`'s
anchored trim quadratic on a run of spaces, which invitations now feed with untrusted input; it is a
linear scan from each end with PostgreSQL's result. No email is sent yet: the invitation notice and the
provider's setup email for a new invitee are both `0.7.8`'s, so until then an invitee is told nothing.
The invitation carries no name, so Keycloak's default profile asks the invitee for one at the first
sign-in, as it asks a provisioned owner (`0.5.9`).
**Tests:** `accepting_binds_the_invited_role_to_the_signed_in_identity` · `an_invitation_works_once` · `an_expired_invitation_is_refused` · `an_admin_cannot_invite_above_their_role` · `invitation_tokens_are_stored_hashed`
**Verify:** `just test-e2e -- test/users/invitations.e2e-spec.ts`
**Done when:** the five tests pass.

### 0.5.11 — Development identities and the synthetic seed
**Repo:** backend + umbrella + frontend · **Size:** M · **Depends on:** `0.5.10`, `0.4.7`, `0.4.8`, `0.2.4` · **Requirements:** —
**Files:** umbrella `infra/keycloak/realm-sadara.json` (development users), `infra/keycloak/README.md` (the development members),
`infra/keycloak/test-realm.sh`, `infra/{.env.example,compose.yaml,README.md}`, `justfile` (`dev-cookie`); backend `src/database/seed.ts`,
`src/database/{development-data,seed-development-data}.ts` (new), `src/database/{development-data,seed}.spec.ts` (new),
`test/database/seed.integration-spec.ts` (new), `eslint.config.mjs`, `package.json` (`seed`), `justfile` (`seed`), `scripts/preflight.sql`;
frontend `scripts/dev-cookie.mts` (new)
Two fictional tenants (`sadara`, `northwind`), one member per role in each, linked to development
identities in the realm (documented development-only passwords; privileged members pre-enrolled in
MFA), and synthetic players with Arabic and Latin names. Every address is on the reserved `.test`
domain; today's seed names tenants after real clubs on a real-looking domain (`seed.ts:81–91`) and seeds
a `SUPER_ADMIN` with a known address (`seed.ts:42`) — both go. The seed is idempotent and grows with each
phase. `just dev-cookie <member>` signs a development member in headlessly (Playwright against the local
Keycloak) and prints a curl cookie jar, for manual API testing.
As built: 34 members, one for each tenant role (`UserRole` less `SUPER_ADMIN`) in each tenant, at
`<role>@<tenant>.test`, named for their role and tenant so the first sign-in asks for nothing, and five
players in each tenant. Every seeded id, and every development account's id in the realm, is RFC 9562's
name-based UUIDv8 over SHA-256 (its Appendix B.2) in one namespace: `development-data.ts` and
`test-realm.sh` derive the same values, so a membership is linked to its account's identity by issuer and
subject, never by address (ADR-0002). The passwords are not in the realm file: one development password
for all 34 accounts, and one authenticator secret for the 14 privileged ones (`0.5.8`), are
`SADARA_DEV_MEMBER_PASSWORD` and `SADARA_DEV_OTP_SECRET` in `infra/.env`, which the realm reads through
placeholders as it reads the client secrets; `.env.example` and the Keycloak README document both, and the
README says no staging or production realm is made from the file. The data (`development-data.ts`) and
the writing (`seed-development-data.ts`) are their own files, tested apart. The seed writes each tenant in
its own tenant transaction, makes what is missing, brings back only the fields that differ, and writes
nothing on a second run, `updatedAt` included; it refuses a tenant of its slug that it did not make and a
membership linked to another identity, and writes no audit entry, since this is development data. The
command refuses any argument and any `NODE_ENV` but `development` or `test`, composes only the
configuration and the database, and mints its own contexts, so it is a fourth context minter in
`eslint.config.mjs`. The old seed's call to `seedDefaultPermissions`, which crashes, goes with its tenants:
`0.6.1` writes the catalog by migration, and until then `user.invite` (`0.5.10`'s migration) is the only
permission row. A database seeded before this keeps the old rows until `just reset`. The frontend script
is `dev-cookie.mts`, not `.ts`: the package declares no module type, so Node warned about a `.ts` file on
every run. It requests the API's two legs from Node, verified against the proxy's certificate authority,
and fills only Keycloak's forms in a browser; the callback is caught there through Chromium's Fetch
interception, because Playwright's `route()` sees only a redirect chain's first request, and redeemed from
Node. Beyond the plan: `test-realm.sh` checks every account (`development_members_one_per_role_in_each_tenant`)
and signs an ordinary and a privileged member in with `infra/.env`'s values
(`a_development_member_signs_in_with_infra_env_credentials`), and the backend adds
`the_seed_never_takes_a_tenant_or_relinks_a_member_it_did_not_make`. All 34 members signed in through
`just dev-cookie`, the privileged roles only at the second level of assurance.
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
**Files:** `src/modules/users/domain/{permission-catalog,default-role-matrix,catalog-differences}{,.spec}.ts` (new),
`src/modules/users/application/services/permission.service.ts`, `src/shared/constants/permissions.constants.ts` (delete),
`prisma/schema.prisma` + migrations `…_permission_catalog_types` and `…_permission_catalog`,
`scripts/generate-permission-sync.ts` (new), `src/common/authz/permission-catalog-check.ts` (new), `src/app.module.ts`,
`src/modules/users/{users.module,application/ports/permission-records.port,infrastructure/repositories/permission.repository}.ts`
(new or changed), `src/common/{guards/roles.guard,decorators/permissions.decorator}.ts`, the medical, scouting and
invitations controllers, `test/legacy-modules/tenant-transaction.e2e-spec.ts`, `eslint-suppressions.json`,
`scripts/smoke-start.sh`, `test/authz/catalog.integration-spec.ts` (new)
The seeding splits each name into enums that have no `REJECT`, `SUBMIT`, `VIEW`, `UPLOAD`, `SEND`,
`ASSIGN_ROLE`, `SCOUTING.REPORT` or `PERFORMANCE` (`permission.service.ts:46–54`, called from
`seed.ts:18`). Each catalog entry now declares its key, category, action and confidentiality explicitly
— nothing is parsed from a name — and all of today's permissions exist, deduplicated. The catalog and
the default matrix sync in one transaction, idempotently; the API refuses to boot if the database
disagrees with the code. `SUPER_ADMIN: Object.values(PERMISSIONS)` (`permission.service.ts:93`) is gone.
`role_permissions` stops deleting with its permission (`RESTRICT`), and nothing sorts or compares roles
by enum order, which differs between the database and the schema (DB-53, DB-58).
As built: the catalog is an object literal of the 64 legacy names, `user.invite` included, so no key can
appear twice; each declares its category, its action, a short description and whether it is a confidential
grant — the explicit permission `security-privacy.md`'s matrix requires before a confidential class is read,
of which only `medical.view_confidential` exists yet. Viewing is `READ`, uploading and sending are `CREATE`
and `user.assign_role` is `ASSIGN`; `REJECT`, `SUBMIT` and the `PERFORMANCE` category are new, in a
migration of their own, since PostgreSQL cannot use an enum value in the transaction that adds it, which
also makes `role_permissions → permissions` `RESTRICT`. The matrix is the legacy seed's, stored for the
first time, less `SUPER_ADMIN`'s every permission and the owner's `medical.view_confidential`; the other
medical cells are `0.6.8`'s. The sync is not the seed's: permissions are reference data that only the
migrations write (`0.4.5`), so `scripts/generate-permission-sync.ts` prints the SQL that makes both tables
the code's — upserting only what differs, granting the matrix and no more, removing an undeclared permission
once nothing holds it — and `…_permission_catalog` carries it as printed, in its migration's transaction; a
later catalog or matrix change ships a new migration with the script's output. The seed no longer touches
permissions, so two seeds succeed on a fresh database. `PermissionCatalogCheck` reads both tables as the
runtime role at boot and refuses to start the API on any difference, naming each; it fails closed, so an API
that cannot read its database at boot does not start either. Permission checks read the stored matrix
through a port and repository inside the member's tenant transaction, so no module reaches the root client
and two ESLint bulk suppressions went; routes name catalog keys, so an undeclared permission does not
compile. Nothing sorted or compared roles by enum order; `ROLE_HIERARCHY` numbers them explicitly and goes in
`0.6.2`. CI's image test started the API on a database it never migrated, so `scripts/smoke-start.sh` now
migrates it as the migrator (approved by the maintainer). Beyond the plan:
`the_api_refuses_to_boot_when_the_database_is_not_the_code`, `the_runtime_role_cannot_change_the_catalog`
and `a_permission_never_takes_its_grants_with_it`. The legacy scouting routes guard report reads with
`report.view` though `scouting.report.read` exists; the rebuild (`1.11`) replaces those routes.
**Tests:** `every_catalog_entry_can_be_stored` · `the_database_matrix_equals_the_code_matrix` · `the_permission_sync_is_idempotent`
**Verify:** `just test-int -- catalog && just seed && just seed`
**Done when:** the three tests pass and two consecutive seeds succeed on a fresh database.

### 0.6.2 — Deny by default: every route declares its permission
**Repo:** backend · **Size:** M · **Depends on:** `0.6.1`, `0.5.6` · **Requirements:** SR-AUTH-009, SR-API-001
**Files:** `src/common/guards/roles.guard.ts` → `permission.guard{,.spec}.ts`, `src/common/decorators/permissions.decorator.ts`,
`src/common/decorators/signed-in.decorator.ts` (new), `src/common/decorators/roles.decorator.ts` (delete),
`src/shared/types/user.types.ts` (delete), `src/common/authz/{route-access,route-access-check}.ts` (new), `src/app.module.ts`,
the identity, medical, scouting and invitations controllers, the test controllers in `test/{auth,platform}/*`,
`test/harness/app.ts`, `test/authz/route-coverage.e2e-spec.ts` (new)
The global `RolesGuard` (`app.module.ts:53`) lets through any route that declares nothing
(`roles.guard.ts:27`). The permission guard enforces `@RequirePermission('contract.approve')` and the
application **refuses to start** if any route has neither a permission nor `@Public()`. The unused
`@Roles` decorator and `ROLE_HIERARCHY` go — two authorization systems invite the wrong one.
As built: a route declares exactly one of three rules, not two. Six routes are neither a permission nor
public — step-up, the session, signing out, signing out everywhere, and listing or ending one's own
sessions — and any signed-in member uses them on their own session; the maintainer chose a third marker,
`@SignedIn()`, over a permission every role would hold ([ADR-0027](../adr/0027-a-members-own-session-is-signed-in.md),
which supersedes ADR-0005's route declarations; I-3 and the backend rules name all three). Today's routes are
5 public, 6 signed-in and 38 behind a permission. `@RequirePermission` takes one catalog key, where
`@Permissions` took a list that no route used as one. `route-access.ts` reads a route's declarations, the
handler's over its controller's, for both the boot check and the guard: `RouteAccessCheck` reads every
controller's routes through Nest's discovery service at boot and refuses to start the API, naming each route
that declares none or more than one; `PermissionGuard` takes `RolesGuard`'s place among the global guards,
fails closed on a route without a single rule, and refuses a role without the route's permission with `403`,
as a typed error. Nothing imported `user.types.ts`, `ROLE_HIERARCHY`'s file, so all of it went. The
test-only controllers declare their rules too, and the test harness closes an application that refuses to
start before the refusal reaches the test. Beyond the plan: `every_route_declares_exactly_one_access_rule`
and `a_signed_in_route_needs_a_session_and_no_permission`.
**Tests:** `a_route_without_a_permission_or_public_fails_startup` · `each_route_refuses_a_member_without_its_permission`
**Verify:** `just test-e2e -- test/authz/route-coverage.e2e-spec.ts`
**Done when:** every route carries an explicit decorator and both tests pass.

### 0.6.3 — Object policies in the use cases
**Repo:** backend · **Size:** M · **Depends on:** `0.6.2` · **Requirements:** SR-ACL-005, SR-API-002, BR-RULE-02
**Files:** `src/common/policy/{policy,policy.spec,direct-calls.spec}.ts` (new), `src/modules/{scouting,medical,users}/application/policies/*.policy{,.spec}.ts`
and `medical/application/policies/medical-staff.ts` (new), the use cases that load a resource and the medical and scouting
controllers, `src/common/tenancy/tenant-context.ts`, `src/common/guards/session.guard.ts`, `test/harness/fixtures.ts`,
`test/authz/object-policies.integration-spec.ts` (new), and three tests that mint a member's context
A policy is a pure function evaluated **inside the use case**, after the resource is loaded and before
it is returned or changed — so it holds for every caller, not only HTTP. Relationship, sensitivity and
state are inputs; an id is never authorization. A read denied by policy is `404`, indistinguishable from
absence.
```ts
export type Decision = { allow: true } | { allow: false; reason: DenyReason };
export function authorize(ctx: AuthorizedTenantContext, action: Action, resource: ResourceView): Decision;
```
As built: the tenant context's member actor carries their role, which the session guard mints from the
membership it verified on that request, so a policy decides from the context alone and no controller passes a
role into a use case. `definePolicy` takes one rule per action, `read` among them, and denies a job
(`NOT_A_MEMBER`) and any action it has no rule for; `authorize` is each policy's own function —
`scoutingReportPolicy.authorize(ctx, action, resource)` — since `src/common` cannot import the modules' policies.
`authorizeRead` answers a denied read with the not-found of absence; `authorizeChange` answers a change by
someone who cannot read the resource the same way, and otherwise refuses for the policy's reason, with the use
case's own error. Six policies — scouting reports and assignments, medical records and treatment sessions,
invitations and memberships — hold the decisions the use cases made inline, unchanged in meaning, so the
defects their owners close stay named in them: who reads which medical records (`0.6.8`, after `0.6.5`), and
scouting's draft editing and self-approval (`1.11`). One tightening: `SUPER_ADMIN` is no longer medical staff
(I-2). Archiving a record or a report, a treatment session's status and removal, and reactivating a membership
acted by id; they now load the resource first, so they pass the policy too. Lists and own-scoped queries call
no object policy: today's read rules restrict no one, and a restriction belongs in the query before pagination
(`0.6.4`, `0.6.8`). Beyond the plan: each policy's decision table,
`a_report_is_submitted_by_its_author_however_the_use_case_is_called` and
`a_confidential_record_is_changed_by_medical_staff_however_the_use_case_is_called` against PostgreSQL with two
tenants.
**Tests:** `a_read_denied_by_policy_is_not_found` · `policies_apply_to_direct_use_case_calls`
**Verify:** `npx vitest run src/common/policy`
**Done when:** both tests pass and every existing use case that loads a resource calls `authorize`.

### 0.6.4 — Confidential projections, checked against an independent classification
**Repo:** backend · **Size:** L · **Depends on:** `0.6.3` · **Requirements:** SR-ACL-008, BR-OBJ-05
**Files:** `src/common/policy/{confidential-class,projection,projection.spec}.ts` (new), `src/common/policy/{policy,policy.spec}.ts`,
`src/modules/users/domain/confidential-grants{,.spec}.ts` (new), `src/modules/users/application/services/permission.service.ts`,
`test/fixtures/field-classification.ts` (new), `test/authz/confidential-fields.e2e-spec.ts` (new)
Repositories **select** the fields a response needs — never `include` a whole related record — and the
response carries a confidential field only when the caller's permission and the policy allow it. The
test does not trust the code's own markers: an **independent fixture** classifies every response field
(`PUBLIC`, and [security-privacy](../reference/security-privacy.md)'s `OPERATIONAL`, `IDENTITY`, `MEDICAL`,
`LEGAL_INTERNAL`, `FINANCE` and `MINOR_POLICY`), and the suite compares real payloads for every role against
it — so a removed marker, a new unclassified field or a widened select fails.
As built: a response is built from its Zod schema by `project(schema, value, disclosed)`
(`src/common/policy/projection.ts`), an allowlist — only the fields the schema names leave, at every depth,
so a widened select or a row passed whole reaches nobody; a value without its schema's shape is withheld,
and an object under a scalar's schema is refused rather than passed on. `confidential(class, field)` is the
code's marker: the field becomes optional, and is absent — never `null` — unless its class is disclosed.
`disclosedClasses(ctx, policy, resource, granted)` keeps a class only when the member's role holds its grant
**and** the resource's policy discloses it; `definePolicy` takes an optional disclosure rule per class, and a
class without one is disclosed to nobody. `CONFIDENTIAL_GRANTS` names each class's grant: only `MEDICAL`
has one, `medical.view_confidential`, so the other four reach nobody yet. `PermissionService.grantedClasses(ctx)`
reads the grants from the stored matrix; a job holds none. The fixture imports nothing from `src/`: it
classifies every field of every live answer — successes, pages and problems — and names who may receive
each confidential class (a role the matrix calls eligible that holds the class's permission); it is the
engineering default while field-level classification is OPEN. The suite calls every route the app serves
as each of the 17 tenant roles in both tenants, and signed out, and fails on an unclassified field, a
classified field no answer carries, a confidential field to a role the fixture does not entitle, or
anything but a `PUBLIC` field to someone signed out. No route the app serves carried a confidential field —
they are in the medical and scouting modules, which stay off — so no live response or repository changed,
nor the contract. A test-only route carries a clinical note's diagnosis through the real marker, grant,
policy and projection: that is where deleting a marker fails the suite until `0.6.8` puts the medical
module's fields under it (scouting's embedded player record is `1.11.1`'s). Each of eleven planted faults —
among them a lost marker, a widened select and the medical module switched on unclassified — failed the
suite. Beyond the plan: `a_projection_carries_only_the_fields_its_schema_names`,
`a_confidential_field_leaves_only_when_its_class_is_disclosed`, `a_value_without_its_schemas_shape_does_not_leave`,
`marking_a_field_leaves_the_schema_it_marks_unmarked`, `a_class_is_disclosed_only_with_its_grant_and_the_policys_rule`
and `each_confidential_permission_grants_exactly_one_class`.
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
`PlayerStaffAssignment(playerId, userId, function, startsOn, endsOn?, assignedById)` records who is
assigned to which player — the agent who looks after them, their coach, medical and legal staff — with
history kept: the role matrix's "assigned" cells read it, and no live assignment means deny (DB-60).
**Tests:** `own_record_access_requires_a_live_link` · `an_expired_guardian_link_denies_access` · `assigned_access_requires_a_live_staff_assignment`
**Verify:** `just test-int -- relationships`
**Done when:** the three tests pass under RLS.

### 0.6.6 — Effective permissions for the web app
**Repo:** backend · **Size:** S · **Depends on:** `0.6.2` · **Requirements:** —
**Files:** `src/modules/users/permissions.module.ts` (new), `src/modules/users/users.module.ts`,
`src/modules/users/application/{services/permission.service,services/permission.service.spec,ports/permission-records.port}.ts`
(the spec new), `src/modules/users/infrastructure/repositories/permission.repository.ts`,
`src/modules/identity/{identity.module,application/use-cases/read-session.usecase,presentation/dto/session.dto}.ts`,
`openapi/openapi.json`, `test/fixtures/field-classification.ts`, `test/auth/sessions.e2e-spec.ts`,
`test/authz/effective-permissions.e2e-spec.ts` (new)
`GET /api/v1/auth/session` adds the member's effective permissions, computed per request from the
database, so the web app can shape navigation. Display only: the API still decides every call.
As built: the session answers `permissions`, the catalog keys the member's role holds in the catalog's
order. `PermissionService.effectivePermissions(ctx)` reads them from the stored matrix for the role the
session guard minted on this request — the role `hasPermission` decides with — and a job holds none.
`ReadSessionUseCase` adds them, so the controller is unchanged. The contract declares the field as an array
of the catalog's keys, and the field classification classes it `OPERATIONAL`: the member's own role's
permissions are the product's matrix, not a confidential fact. Users imports identity, so identity could
not import users: `PermissionService` and its stored matrix moved into `PermissionsModule`, which depends
on nothing but the tenant transaction; users re-exports it for the permission guard, and identity imports
it. The role change in the test is written to the database between two requests of one session, until a
role-change use case exists (`1.1.x`). Beyond the plan: for every tenant role in two tenants the list
agrees with what the API answers on a route behind a permission, seen both ways;
`effective_permissions_follow_the_catalogs_order` and `a_job_holds_no_effective_permission`. Each of seven
planted faults — among them a list remembered from a member's first request — failed the suite.
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

### 0.6.8 — The existing medical routes obey the rules
**Repo:** backend · **Size:** M · **Depends on:** `0.6.4`, `0.6.5` · **Requirements:** BR-RULE-07
**Files:** `src/modules/medical/**`, `src/modules/users/domain/default-role-matrix.ts`, `test/legacy-modules/*.e2e-spec.ts`
They stay flagged off (`0.1.8`) but must be safe when switched on. Medical: `medical.view_confidential`
is defined and never checked (`permissions.constants.ts:28`); the player role holds `medical.read`
(`permission.service.ts:227`) and the caller picks the confidentiality filter
(`medical.controller.ts:70–74`) — enforce the medical policy, limit players to their own record through
`0.6.5`, and take the filter away from the caller; treatment sessions are archived, not hard-deleted
(`treatment-session.repository.ts:202`). The legacy scouting module is not patched here: the demo
milestone rebuilds scouting (`1.11.1`–`1.11.8`), and its defects — a `status` writable through `PATCH`,
an edit check that lets anyone edit a draft, reports that embed the whole player — are closed by that
rebuild, which takes over their three tests (`1.11.1`, `1.11.3`).
**Tests:** `a_coach_cannot_read_a_medical_record` · `a_player_reads_only_their_own_medical_record` · `the_confidentiality_filter_is_not_caller_controlled` · `treatment_sessions_are_archived_not_deleted`
**Verify:** `FEATURE_MEDICAL=true just test-e2e -- test/legacy-modules`
**Done when:** the four tests pass.

### 0.6.9 — The two-tenant isolation suite over every route
**Repo:** backend · **Size:** L · **Depends on:** `0.6.2`, `0.4.12` · **Requirements:** SR-NFR-SEC-003, TEST-003
**Files:** `test/isolation/isolation.e2e-spec.ts`, `test/isolation/route-inventory.ts` (new)
Introspect every registered route (flags on). For each route that takes an object id, create the object
in tenant B and call it as every role of tenant A: the answer is `404` (or `403` for a function-level
denial), never `2xx`, and nothing in B changed. Lists, counts and search never include B's rows. A route
missing from the inventory fails the suite, so a new route cannot ship unexamined.
**Tests:** `no_route_reads_another_tenants_object` · `no_route_mutates_another_tenants_object` · `every_route_is_in_the_isolation_inventory`
**Verify:** `FEATURE_MEDICAL=true FEATURE_SCOUTING=true just test-e2e -- test/isolation`
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
The client address is stored as `inet` and an over-long user agent is truncated before the insert, so
request metadata can never abort a business change (DB-56).
**Tests:** `a_rolled_back_change_leaves_no_audit_row` · `a_failed_audit_insert_aborts_the_change` · `audit_payloads_carry_no_confidential_values` · `role_changes_record_before_and_after`
**Verify:** `just test-int -- audit`
**Done when:** the four tests pass, the failure case by injected fault.

### 0.7.3 — Security events that have no tenant
**Repo:** backend · **Size:** S · **Depends on:** `0.7.1`, `0.5.5` · **Requirements:** SR-AUD-001
**Files:** `prisma/schema.prisma` + migration `…_security_events`, `src/infrastructure/audit/security-events.ts` (new)
A refused sign-in on an unknown host has no tenant to belong to, and inventing one would falsify the
record. `SecurityEvent` — global, UUIDv7, append-only by the same grants and triggers — records sign-in
success and refusal, step-up, logout, back-channel events and session revocations, with the tenant when
it is known and hashed network data; this step wires those events into the sign-in callback (`0.5.5`),
step-up (`0.5.8`) and session revocation (`0.5.7`). Reading it is restricted (the tenant's own view
arrives in `1.7.1`).
It also imports the identity provider's own login and admin events — failed sign-ins, lockouts, MFA
changes, none of which reach Sadara — through the provider adapter (`0.5.4`) and its authenticated admin
API, deduplicated by the provider's event id (DB-61).
**Tests:** `a_refused_sign_in_is_recorded_without_a_tenant` · `security_events_are_append_only` · `provider_sign_in_failures_reach_security_events`
**Verify:** `just test-int -- security-events`
**Done when:** the three tests pass.

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
A second entry point runs BullMQ on Valkey. It finds work without a privileged client: a registry role,
which this step's migration creates and grants `SELECT` on it, may read only the `tenant_directory` view
(`0.4.5`); for each active tenant the relay opens a tenant
transaction and claims due events `FOR UPDATE SKIP LOCKED`, then publishes them. Every job carries its tenant and a
business reference; its handler restores that tenant's context and runs in its own tenant transaction, inside
the correlation the job carries (`runCorrelatedJob`, `0.10.1`).
Retries back off exponentially to a bound, then mark `DEAD` with the last error; shutdown drains
in-flight jobs.
Valkey runs with append-only persistence and `maxmemory-policy noeviction`, as BullMQ requires — in the
local stack already (`infra/compose.yaml`) and in every hosted environment.
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
`FileObject` also keeps the quarantined object's version (`quarantineVersionId`) beside the final one; the
upload session's owner is a declared intent, `(ownerKind, ownerId)`, checked by the owner's policy at upload
and at binding and never joined — the typed binding is the only reference (DB-69).
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
**Repo:** backend · **Size:** S · **Depends on:** `0.8.4`, `0.7.4` · **Requirements:** SR-DOC-002
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
**Files:** `app/page.tsx` and the starter images (delete), `app/(dashboard)/**` → `app/[locale]/(app)/**`,
`app/[locale]/(public)/**`, `app/[locale]/layout.tsx` (refuses an unsupported locale), `app/not-found.tsx`,
`src/i18n/locales.ts`, `src/shared/ui/route-states.tsx`, `src/shared/lib/constants.ts` (delete the route table),
`next.config.ts`, `proxy.ts` (a path without a locale gains the default), `justfile` and `ci.yml` (`next typegen`
before the type-check), `loading.tsx` / `error.tsx` / `not-found.tsx` per segment, `tests/e2e/routes.spec.ts` (new)
One tree under the locale: `/{locale}` (home), `/{locale}/sign-in`, and features by noun —
`/{locale}/players`, `/{locale}/contracts`, `/{locale}/legal`, `/{locale}/settings` — with no `/dashboard`
prefix. `typedRoutes` is on, so a link to a route that does not exist fails the type-check; every segment
has its loading, error and not-found state. The root layout stays at `app/`, so `app/not-found.tsx` answers
every unmatched address: a catch-all under `[locale]` would match every link and disarm `typedRoutes`.
**Tests:** `every_internal_link_resolves` · `an_unknown_route_renders_not_found`
**Verify:** `npx tsc --noEmit && npm run build && npx playwright test routes`
**Done when:** the build lists no route outside `/[locale]` and no starter content remains.

### 0.9.2 — Arabic and English, RTL and LTR
**Repo:** frontend · **Size:** M · **Depends on:** `0.9.1` · **Requirements:** SR-CORE-007, SR-NFR-I18N-001, UX-008, TEST-010
**Files:** `src/i18n/**` (routing, request config, typed message keys), `messages/{ar,en}.json` (new),
`app/[locale]/layout.tsx`, `app/layout.tsx`, `app/globals.css` (the font stack), `next.config.ts` (the
next-intl plugin), `proxy.ts`, every component with a user-facing string, `tests/e2e/i18n.spec.ts` (new)
`next-intl` with locale routing; `<html lang dir>` rendered on the server (no flash of the wrong
direction); an Arabic-capable, licensed typeface beside the Latin one; every string in the catalogs, with
ICU plurals that cover Arabic's categories; numbers, dates and money through `Intl` with the locale.
Switching language never changes a business value. The typefaces are IBM Plex Sans Arabic and Geist,
both under the SIL Open Font License 1.1 and self-hosted by `next/font`; the font stack names each face
before its metric-matched fallback, which is local Arial and would otherwise draw Arabic text. The
home page's placeholder metrics and inert quick actions were removed rather than translated.
**Tests:** `the_catalogs_have_identical_keys` · `the_arabic_layout_renders_rtl_on_the_server` · `no_user_facing_literal_remains`
**Verify:** `npx vitest run src/i18n && npx playwright test i18n`
**Done when:** the sign-in page renders in Arabic with `dir="rtl"` and in English with `dir="ltr"` from
the server, the literal check passes, and the sign-in journey of `0.2.4` asserts Arabic text in the `ar`
project (today it finds the English "Sign In" in both).

### 0.9.3 — Logical CSS and bidirectional isolation
**Repo:** frontend · **Size:** S · **Depends on:** `0.9.2` · **Requirements:** —
**Files:** `eslint.config.mjs` (a rule), components with physical utilities, `src/shared/ui/bidi.tsx` (new)
A lint rule refuses physical-direction utilities (`ml-`, `pr-`, `left-`, `text-right`, `rounded-l-`, …);
the existing ones move to logical equivalents — 17 in seven files on 28 September, four in three files
once `0.1.7` had deleted the old pages — and the mobile sidebar slides in from the start side in both
directions. Identifiers, emails, URLs and mixed
Latin numbers render inside a bidi-isolating component so they never reorder in Arabic text;
directional icons mirror, media controls do not.
**Tests:** `the_lint_refuses_a_physical_margin` · `a_mixed_identifier_does_not_reorder_in_arabic`
**Verify:** `npm run lint && npx vitest run src/shared/ui`
**Done when:** lint passes with the rule on and the isolation test passes.

### 0.9.4 — A typed client generated from the contract, on the same origin
**Repo:** frontend · **Size:** M · **Depends on:** backend `0.3.9`, `0.9.1`, umbrella `0.2.1` · **Requirements:** —
**Files:** `src/shared/api/{client,problem}.ts` (new), `src/shared/api/schema.d.ts` (generated),
`src/server/api/{client,internal-url}.ts` (new), `openapi/{openapi,source}.json` (new), `scripts/contract.mjs`
(new), `scripts/test-policy.sh`, `.env.example` (new), `.prettierignore` (new), `src/shared/lib/api-client.ts`
and the modules that used it (delete), `src/features/auth/hooks/use-auth.ts`, `src/components/layout/sidebar.tsx`,
`package.json`, `justfile`, `.github/workflows/ci.yml`, `CONTRIBUTING.md`
`openapi/openapi.json` is the backend's committed contract, byte for byte, at the backend commit
`openapi/source.json` records (`npm run api:sync -- <commit>`, a full SHA); `openapi-typescript` generates
the types from it, and `openapi-fetch` calls **`/api/v1` on the web app's own origin** — the local HTTPS
proxy (`0.2.1`) in development, the same path routing in every hosted environment — so the session cookie is
never cross-site. A step that needs a newer contract syncs it; the backend's breaking-change check keeps an
older copy valid meanwhile. Reads go through a server-only layer, `src/server/api/` (`import 'server-only'`),
which calls the API's internal address (`API_INTERNAL_URL`) with the session cookie, nothing else of the
request, and `cache: 'no-store'`; the browser uses the same generated client against `/api/v1` for writes
and interactive reads, and no Server Action carries a business write
([ADR-0025](../adr/0025-the-web-app-data-path.md)). Every call asks for the page's language
(`Accept-Language`), so the API's messages match the page. Problem details become a typed `ApiProblem`; a
failure that is not one becomes `INTERNAL_ERROR` with its status. The client never sends a tenant header —
it refuses one — and `axios` goes, with the medical and scouting wrappers that called routes outside the
contract; the sign-out request, to a route `0.1.6` retired, gives way to clearing the cache until `0.9.5`.
CI and `just contract` verify the copy against the backend at the recorded commit and refuse types that
differ from the generator's.
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
to the provider's sign-out. The authenticated layout checks the session on the server through
`src/server/api/` and renders nothing protected without it; a server read also tells the API the public
host it serves, which the API believes only because it lists the web app among its trusted proxies
(`0.3.8`, `0.5.2`); TanStack Query serves interactive screens
only, prefetched on the server and hydrated; nothing tenant-scoped is cached by Next
([ADR-0025](../adr/0025-the-web-app-data-path.md)). `proxy.ts` looks at cookie presence only to route,
never to decide.
**Tests:** `no_session_secret_is_readable_by_javascript` · `an_expired_session_returns_to_sign_in_with_the_return_path` · `logout_clears_every_cached_query`
**Verify:** `npx playwright test tests/e2e/session.spec.ts`
**Done when:** a seeded member signs in through the local Keycloak in Arabic and English, and the three
tests pass.

### 0.9.6 — The application shell
**Repo:** frontend · **Size:** M · **Depends on:** `0.9.3`, `0.9.5` · **Requirements:** UX-010, UX-011, UX-012, SR-NFR-A11Y-001
**Files:** `src/components/shell/**`, `src/shared/ui/**`, `src/shared/ui/states/**` (new), `components.json` (new), `app/globals.css`, `PRODUCT.md` and `DESIGN.md` (new)
Components from shadcn/ui through its CLI in right-to-left mode (`rtl: true`), regenerating today's
hand-copied primitives ([ADR-0025](../adr/0025-the-web-app-data-path.md)); design tokens; navigation built from the member's effective permissions (display only); shared empty,
loading, error, offline and retry states; light and dark themes with the `dark:` variant bound to the
theme class (`@custom-variant dark`) — today `globals.css:49` styles `.dark` while `dark:` follows the
operating system. Landmarks, headings, visible focus and keyboard operation from the start. The first
[design pass](../reference/visual-design.md#the-design-pass-in-every-ui-step): `impeccable init` and
`impeccable document` write `PRODUCT.md` and `DESIGN.md` from the visual-design reference and the tokens,
for every later design command to read ([ADR-0026](../adr/0026-interface-design-with-skills-and-references.md)).
**Tests:** `navigation_hides_what_the_member_cannot_open` · `empty_states_name_the_next_action` · `a_failed_request_offers_retry`
**Verify:** `npx vitest run src/components && npx playwright test shell`
**Done when:** the three tests pass and axe reports no serious violation on the shell in either locale.

---

## Group 0.10 — Operational proof and local recovery

### 0.10.1 — Structured logs with request correlation
**Repo:** backend · **Size:** M · **Depends on:** `0.3.1` · **Requirements:** SR-CORE-008, SYS-TEN-007
**Files:** `src/infrastructure/logging/{logging.module,logger-options,correlation}.ts` (new), `src/main.ts`,
`src/app.setup.ts`, `src/app.module.ts`, `src/common/interceptors/logging.interceptor.ts` (delete),
`src/common/logging/{request-id,route-template}.ts`, `src/common/filters/problem-details.filter.ts`,
`src/infrastructure/events/event.service.ts`, `test/harness/{app,log-capture}.ts`,
`test/platform/logging.integration-spec.ts` (new)
`nestjs-pino` writes one JSON object per line with the [safe event contract](../reference/observability.md#safe-event-contract)'s
fields — an ISO `timestamp`, the `level` by name, `service`, `environment` — Nest's own lines included; the
level is `debug` in development, `info` where deployed, errors only in tests. pino-http writes the access
log in place of the hand-rolled interceptor: `requestId`, `method`, the **route template** (`route`; a path
no route serves, Nest's `*path` catch-all included, is `(unmatched route)`), `status`, `durationMs`, and the
opaque `tenantId` and `actorId` of a verified session — never the URL, a header, a body or an address; a
refusal at `warn`, a failure at `error`. The request id is a UUIDv7, or the canonical UUID a trusted proxy
sent in `X-Request-Id` — believed only from a peer `TRUSTED_PROXIES` names, as `X-Forwarded-For` is
(`0.3.8`) — returned as before and handed over to the logger. The rest of the request runs inside it
(AsyncLocalStorage, log correlation only): `jobCorrelation()` stamps it on a job, `runCorrelatedJob()` runs
a handler inside it with `jobId` and `attempt`, and the jobs it enqueues carry it on, so one id follows a
request through the worker; `EventService` stamps its jobs. Tests read the log with `bootApp({ logs })`;
nestjs-pino keeps one logger per process, built by the first app.
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

## Group 0.11 — The gates: the foundation, then production

### 0.11.0 — The foundation gate: what every product feature builds on
**Repo:** umbrella + backend + frontend · **Size:** M · **Depends on:** `0.1.2`, `0.1.3`, `0.2.10`, `0.2.6`, `0.2.8`, `0.2.9`, `0.3.6`, `0.4.6`, `0.4.9`, `0.4.10`, `0.4.11`, `0.5.7`, `0.5.11`, `0.6.7`, `0.6.9`, `0.7.3`, `0.7.7`, `0.7.8`, `0.8.5`, `0.9.6`, `0.10.2` · **Requirements:** BR-OBJ-09
**Files:** umbrella `docs/implementation/progress.md`, `docs/implementation/handoff.md`, the gate PR's body
Product features start here, not after the production gate ([ADR-0021](../adr/0021-a-product-built-to-sell.md)).
Run the exit-gate commands below except `just drill`, on `development` in each repository, and perform
demonstrations 1–10 by hand on a freshly seeded stack. Record the application commits, the CI
runs and the results in the gate PR; move the pins; regenerate the frontier; re-forecast the
[demo milestone](demo-milestone.md#forecast-and-checkpoints) from the measured hours. What this gate
leaves out stays in `0.11.1`, before anything reaches staging or production.
**Verify:** the exit-gate commands below, without `just drill`
**Done when:** the gate PR is merged with those commands green and demonstrations 1–10 recorded.

### 0.11.1 — Run the Phase-0 production gate and record the evidence
**Repo:** umbrella + backend + frontend · **Size:** M · **Depends on:** `0.11.0`, `0.6.8`, `0.10.3`, `0.10.4` · **Requirements:** BR-OBJ-09, TEST-006
**Files:** umbrella `docs/implementation/progress.md`, `docs/implementation/handoff.md`, the gate PR's body
The production gate: the foundation gate (`0.11.0`) has already opened the product's features; this one
adds guardian relationships, the legacy medical routes and the restore and failure drills, and nothing reaches staging or production without it
(`1.10.1` onwards). Run every command of the exit gate below on `development` in each repository and
perform every demonstration by hand on a freshly seeded stack; record the application commits, the CI
runs and the results in the gate PR; move the pins; regenerate the frontier; review the risk and
long-lead registers and re-forecast what remains from the measured hours. A demonstration that fails
keeps the gate open.
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

**Demonstrations**, by hand on a freshly seeded stack, recorded in the gate PR. The foundation gate
(`0.11.0`) records 1–10; the production gate (`0.11.1`) records all eleven.

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
