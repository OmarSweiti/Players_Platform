# Current state — the verified baseline

What the code actually does, established on **28 September 2026** against umbrella `eed4437`, backend
`b5f32a4` and frontend `31aeb9a`. Two independent authors audited the backend, the frontend, the schema
and the legacy documents, and cross-checked each other's findings against the code; every line below
carries its evidence (`file:line`, relative to the application's root) and was re-read before it was
written down. Nothing here is taken from the legacy status documents.

**How to use this file.** It is the *before* picture. Each defect names the microstep that removes it;
when that microstep merges, the defect is gone and this file is **not** edited — the progress record is
the *after*. The file is replaced wholesale only at a phase gate, by a fresh audit.

---

## Inventory

### Toolchain, as resolved

| Fact | Evidence |
|---|---|
| Node 24.19.0 in both applications | `frontend/.nvmrc`, `backend/.nvmrc` |
| Next.js 16.3.6, React 19.2.4 | `frontend/package.json`, `frontend/package-lock.json` |
| NestJS 11 (core 11.1.19 resolved) | `backend/package.json`, `backend/package-lock.json` |
| Prisma CLI, client and PostgreSQL adapter 7.10.0 | `backend/package-lock.json` |
| TypeScript 5.9.3 in both | both lockfiles |
| PostgreSQL 17 in CI's migration replay; **18.6 replay verified locally** — six migrations, no drift | `backend/.github/workflows/ci.yml`, `backend/justfile:64–77`; [ADR-0013](../adr/0013-postgresql-18.md) |

### Backend

| Module | State | Routes |
|---|---|---|
| `auth` | 31 files; **no flow works end to end** (A-*) | 16 |
| `medical` | partial, 12 files | 16 |
| `scouting` | partial, 18 files | 19 |
| `users` | a permission service and constants | 0 |
| `players`, `contracts`, `legal`, `training`, `chat`, `notifications` | **empty module declarations** | 0 |
| `health` | liveness and a readiness that always says "ready" | 2 |

53 registered routes (a 54th, the starter `AppController`, exists but is not registered). Tests: the
starter unit test and a starter e2e test that expects "Hello World" — nothing exercises the product.
Six migrations, all dated May 2026. No `.env.example`. Variables read: `NODE_ENV`, `PORT`, `API_PREFIX`,
`DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRES_IN`, `JWT_REFRESH_SECRET`, `JWT_REFRESH_EXPIRES_IN` (read,
unused), `REDIS_HOST`, `REDIS_PORT`, `CORS_ORIGIN`, `MAIL_FROM`.

### Frontend

Routes: `(auth)/login`, `register`, `forgot-password`, `reset-password`, `verify-email`;
`(dashboard)/` and `(dashboard)/settings/2fa`; the starter `app/page.tsx`. One feature folder (`auth`).
27 runtime dependencies, 12 never imported. No tests. 21 lint problems (13 errors).

### Schema

29 models, 26 enums, six migrations. Findings, ranked, with target models and the migration sequence:
[`database.md`](database.md).

---

## What is sound — keep it

- The layering in `auth`, `medical` and `scouting` — presentation, application use cases, infrastructure
  repositories — is the right shape.
- `tenantId` on every tenant-owned table and composite `(id, tenantId)` keys on most relations.
- Helmet and a strict whitelist validation pipe in the bootstrap; Argon2 hashing; password-reset tokens
  already hashed; Swagger kept out of production builds.
- The delivery flow in all three repositories.

---

## Defects, each with its owner

**S1** exploitable or data-exposing · **S2** a flow that cannot work · **S3** wrong but contained ·
**S4** hygiene. *Owner* is the microstep that removes the defect; "→" marks where a retired mechanism's
replacement is built.

### Authentication

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| A-1 | The signing key falls back to `'default-secret'`, so tokens can be forged; with only the refresh secret unset, access and refresh tokens are interchangeable | `auth.module.ts:35`, `jwt.strategy.ts:36` | S1 | `0.1.5`, `0.1.6` |
| A-2 | Whole emails, raw reset and verification links included, are logged at debug in every environment | `mail.service.ts:21–22` | S1 | `0.1.4` |
| A-3 | The access log records full URLs, so `?token=…` is logged | `logging.interceptor.ts:24` | S1 | `0.1.4` |
| A-4 | Unhandled exceptions are `console.error`'d raw; Prisma errors echo argument values, hashes and tokens included | `http-exception.filter.ts:41` | S1 | `0.1.4`, `0.3.1` |
| A-5 | 25 log lines identify users by email | `grep -rnE "logger\.\w+\(.*email" src` | S3 | `0.1.4` |
| A-6 | Public registration accepts any role, `SUPER_ADMIN` included | `register.dto.ts:40–46` → `register.usecase.ts:45` | S1 | `0.1.6` |
| A-7 | Every public auth route resolves the tenant to `'default-tenant'`, a non-UUID, so sign-in fails | `auth.controller.ts:117, 177, 249, 260, 279, 290` | S2 | `0.1.6` → `0.5.2` |
| A-8 | `req.tenantId` is read by eight routes and set by nothing — `TenantGuard`, its only setter, is never applied | `get-current-user.usecase.ts:13`, `auth.controller.ts:308, 322, 336` | S2 | `0.1.6` → `0.4.3`, `0.5.6` |
| A-9 | Refresh reads the token from the body, which browsers never send; no rotation, no reuse detection, no user re-check | `auth.controller.ts:200–204` | S2 | `0.1.6` → `0.5.6` |
| A-10 | The session list is synthesised; revoke returns an explanation and has an unbound `sessionId`; logout-everywhere writes a `passwordChangedAt` nothing reads | `get-active-sessions.usecase.ts:29–41`, `revoke-session.usecase.ts:20–31`, `auth.controller.ts:358` | S2 | `0.1.6` → `0.5.7` |
| A-11 | 2FA is never asked for at sign-in — `Verify2FAForLoginUseCase` exists and is registered nowhere | `verify-2fa-for-login.usecase.ts:12` | S1 | `0.1.6` → `0.5.8` |
| A-12 | The TOTP secret is stored in plaintext; calling enable again switches an active 2FA off without a code | `enable-2fa.usecase.ts:24–27` | S1 | `0.1.6` |
| A-13 | A verification request **without a token** reaches the lookup with an `undefined` filter, which Prisma drops. Today's broken tenant resolution blocks it; once tenants resolve, the repository would return an arbitrary user of the tenant, and the expiry check (`verify-email.usecase.ts:20`) would let the verification succeed whenever that user happened to hold an unexpired verification | `user.repository.ts:104–110`, `verify-email.usecase.ts:12, 20` | S3 (latent) | `0.1.6` |
| A-14 | Verification tokens are stored **raw** and sent as a GET query parameter | `register.usecase.ts:37, 50`, `resend-verification.usecase.ts:36` | S3 | `0.1.6` |
| A-15 | Resend-verification answers 404 for an unknown address — account enumeration | `resend-verification.usecase.ts:20` | S3 | `0.1.6` |
| A-16 | Sign-in ignores `isActive`, `deletedAt` and email verification | `login.usecase.ts` | S3 | `0.1.6` → `0.5.5` |
| A-17 | `@Throttle` decorates login but no `ThrottlerGuard` is registered | `app.module.ts:52–53` | S1 | `0.3.8` |
| A-18 | Lockout (5 failures → 30 min) never resets after expiry, and a locked account answers differently from bad credentials | `login.usecase.ts:30–34, 60, 118–121` | S3 | `0.1.6` → `0.5.1` |
| A-19 | Three copies of an 8-character composition rule; the DTOs allow 6 | `register.usecase.ts:80–102`, `change-password.usecase.ts`, `reset-password.usecase.ts` | S3 | `0.1.6` → `0.5.1` |
| A-20 | Production cookies are `SameSite=None` with credentialed CORS and no CSRF defence; form-encoded bodies are accepted | `auth.controller.ts:127, 136, 211` | S1 | `0.1.6` → `0.5.6` |
| A-21 | The web login form sends `rememberMe`, which the strict pipe refuses with 400 | frontend `app/(auth)/login/page.tsx:16`; backend `main.ts:45–50` | S2 | `0.1.7` |
| A-22 | `speakeasy`, unmaintained, for TOTP | `package.json` | S4 | `0.1.6`, `0.2.7` |

### Tenancy

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| T-1 | Six single-column foreign keys can reference another tenant's row | `schema.prisma:638, 756, 834, 975, 1287, 1358` | S1 | `0.4.4` |
| T-2 | Two composite `SET NULL` keys would null `tenantId` too, so the delete fails | `scouting_reports_playerId_tenantId_fkey`, `treatment_sessions_medicalRecordId_tenantId_fkey` | S3 | `0.4.4` |
| T-3 | Scoping is hand-written in every repository; nothing fails when one forgets; the database enforces nothing | all repositories; `migrations/20260506200624_init/migration.sql` | S1 | `0.4.3`, `0.4.5` |
| T-4 | A second, unused tenancy mechanism on `PrismaService` | `prisma.service.ts:98–120` | S4 | `0.4.3` |
| T-5 | A treatment session can cite another player's medical record | `schema.prisma:1207–1208` | S3 | `0.4.4` |
| T-6 | An attendance row can join an enrollment and a session of two different programs | `schema.prisma:931–932` | S3 | `0.4.4` |
| T-7 | Filter indexes on tenant tables do not lead with `tenantId`; `tenants.slug` is indexed twice | `schema.prisma:278, 318` and [`database.md`](database.md) | S4 | `0.4.6` |
| T-8 | The web client sends `X-Tenant-ID` from `localStorage` | frontend `src/shared/lib/api-client.ts:58–61` | S3 | `0.9.4` |

### API platform

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| P-1 | 46 plain `throw new Error(…)` in the modules become 500s | `grep -rn "throw new Error(" src/modules` | S2 | `0.3.1` |
| P-2 | Validation is registered twice with different options | `main.ts:45`, `app.module.ts:56` | S4 | `0.3.2` |
| P-3 | Untyped `@Query() query: any` | `medical.controller.ts:65, 92, 208` | S3 | `0.3.2` |
| P-4 | The response wrapper is registered twice, and 38 hand-built `{ statusCode, data }` bodies are wrapped again | `main.ts:19`, `app.module.ts:54`, `transform.interceptor.ts` | S3 | `0.3.4` |
| P-5 | "Not found" is returned as HTTP 200 with a 404 inside | `medical.controller.ts:123, 241`, `scouting.controller.ts:116` | S2 | `0.3.4` |
| P-6 | Routes live under `/api`, unversioned | `main.ts:40–41` | S4 | `0.3.3` |
| P-7 | Two controllers reference an unregistered `bearer` scheme; the API calls itself "Football Management Platform API" | `main.ts:56–69` | S4 | `0.3.9`, `0.2.7` |
| P-8 | Swagger is served whenever `NODE_ENV` is unset | `main.ts:54` | S3 | `0.1.5` |
| P-9 | Readiness always answers "ready" | `health.controller.ts:20–27` | S3 | `0.3.7` |

### Authorization

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| Z-1 | The permission seed crashes: 20 of 63 names cannot be stored (`contract.reject`, the `scouting.report.*` family, `user.assign_role`, `document.upload`, `performance.*`, …), so every `@Permissions` route answers 403 | `permission.service.ts:46–54` (from `seed.ts:18`), `permissions.constants.ts` | S2 | `0.6.1` |
| Z-2 | Authorization fails open: the global guard allows any route that declares nothing | `roles.guard.ts:27`, `app.module.ts:53` | S1 | `0.6.2` |
| Z-3 | `@Roles` and `ROLE_HIERARCHY` — a second authorization system nothing uses | `roles.decorator.ts`, `user.types.ts:3` | S4 | `0.6.2` |
| Z-4 | `SUPER_ADMIN` is seeded with every permission, confidential ones included, and with a known address | `permission.service.ts:93`, `seed.ts:42` | S1 | `0.6.1`, `0.6.7`, `0.5.11` |
| Z-5 | `medical.view_confidential` is defined and never checked; the player role holds `medical.read`; the caller chooses whether confidential records are filtered | `permissions.constants.ts:28`, `permission.service.ts:227`, `medical.controller.ts:70–74` | S1 | `0.6.8` |
| Z-6 | A scout can set their own report to `APPROVED` through `PATCH` | `update-scouting-report.dto.ts:8`, `update-assignment.dto.ts:8` | S1 | `1.11.3` |
| Z-7 | The edit check lets anyone edit any draft and the author edit an approved report | `update-scouting-report.use-case.ts:18` | S1 | `1.11.3` |
| Z-8 | Scouting reports embed the whole player, passport included | `scouting-report.repository.ts:56, 79, 158` | S1 | `1.11.1` |

### Data, audit and storage

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| D-1 | Audit is an ordinary table with `deletedAt`, written only by queuing a job — a crash loses it | `schema.prisma:1361`, `event.service.ts:37` | S1 | `0.7.1`, `0.7.2` |
| D-2 | `AuditLog.tenantId` is required, so a sign-in refused before a tenant is known cannot be recorded honestly | `schema.prisma:1340–1350` | S3 | `0.7.3` |
| D-3 | Treatment sessions are hard-deleted | `treatment-session.repository.ts:202` | S3 | `0.6.8` |
| D-4 | Money is `Decimal(…, 2)` although JOD has three decimals; enrollment payments have no currency | `schema.prisma:616, 621, 825, 898` | S3 | `0.4.7` |
| D-5 | Calendar dates and instants are both naive `TIMESTAMP(3)` | `schema.prisma:480, 611`; the initial migration | S3 | `0.4.8` |
| D-6 | Legal notes default to **not** internal; nothing enforces one current season or one featured image; no CHECK constraints anywhere | `schema.prisma:1001, 418, 543` | S3 | `0.4.10` |
| D-7 | Files would be written to the API's local disk under a caller-influenced path (a latent traversal — no route uses it yet); eight URL columns hold file references | `local.storage.service.ts:18–19, 33`; [`database.md`](database.md) | S3 | `0.8.1`, `0.8.2` |

### Build and hygiene

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| B-1 | `start:prod` runs `node dist/main`; the build emits `dist/src/main.js` | `package.json:14`, `tsconfig.json` | S2 | `0.2.6` |
| B-2 | Imported but undeclared: `@nestjs/mapped-types` (four DTOs), `dotenv` | `prisma.config.ts:3` | S3 | `0.2.7` |
| B-3 | Declared but never imported: `socket.io`, `@nestjs/websockets`, `@nestjs/platform-socket.io`, `redis`, `ioredis`, `multer`, `@types/multer`, `dayjs` | `package.json` | S4 | `0.2.7` |
| B-4 | Dead code: `AppController`, `LocalStrategy`, `TenantGuard`, `ThrottlerConfigModule`, `user.types.ts` | as named | S4 | `0.2.3`, `0.1.6`, `0.6.2` |
| B-5 | Use cases split between `*.usecase.ts` (16) and `*.use-case.ts` (11) | `find src -name '*use*case.ts'` | S4 | `0.2.7` |
| B-6 | The seed names tenants after real clubs on a real-looking domain | `seed.ts:81–91` | S3 | `0.5.11` |
| B-7 | 748 lint problems; lint is not a gate | `npx eslint .` | S4 | `0.2.5` |
| B-8 | CI replays migrations on PostgreSQL 17; the baseline is 18 | `.github/workflows/ci.yml` | S4 | `0.2.2` |

### Frontend

| # | Defect | Evidence | Sev | Owner |
|---|---|---|---|---|
| F-1 | Development logging prints request bodies, passwords included | `src/shared/lib/api-client.ts:64–70` | S1 | `0.1.4` |
| F-2 | `/` serves the Next.js starter, colliding with `(dashboard)/page.tsx`; eleven links to `/dashboard/…` routes that do not exist | `app/page.tsx`, `src/shared/lib/constants.ts:31–34` | S2 | `0.9.1` |
| F-3 | The current-user query waits for cookies JavaScript cannot read, so it never runs | `src/features/auth/hooks/use-auth.ts:86–88` | S2 | `0.1.7` → `0.9.5` |
| F-4 | `lang="en"`, a Latin-only typeface, no catalogs, no RTL | `app/layout.tsx:2, 29` | S2 | `0.9.2` |
| F-5 | 17 physical-direction utilities in seven files | `app/`, `src/` | S4 | `0.9.3` |
| F-6 | `dark:` follows the operating system while the theme styles `.dark` | `app/globals.css:49` | S4 | `0.9.6` |
| F-7 | 2FA "backup codes" are invented in the browser and never stored — a user who saves them is locked out | `app/(dashboard)/settings/2fa/page.tsx:59` | S2 | `0.1.7` |
| F-8 | The reset form's `.refine` returns an object on mismatch, which counts as valid | `app/(auth)/reset-password/reset-password-content.tsx:22–29` | S3 | `0.1.7` |
| F-9 | 12 of 27 dependencies never imported | `package.json` | S4 | `0.2.7` |
| F-10 | No tests; 21 lint problems; route protection is cookie presence (`proxy.ts:36–44`), a navigation aid mistaken for a check | as named | S4 | `0.2.4`, `0.2.5`, `0.9.5` |

---

## The legacy documents against the code

The 25 retired guides described a different system; what each claimed and where its valid content went
is in [`consolidation.md`](consolidation.md). Two claims matter most because agents obeyed them: an
always-on rule told every AI session "NEVER manually add `tenantId` to queries - middleware handles it"
(`.lingma/rules/feature-implementation-standards.md:15`) when no such middleware exists, and three status
reports called authentication "95% complete, production ready" when no sign-in works.
