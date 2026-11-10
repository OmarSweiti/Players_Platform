---
paths:
  - "backend/src/**"
  - "backend/test/**"
---

# Backend rules

The law is `docs/implementation/01-conventions.md`; the contracts are `docs/reference/api.md`,
`docs/reference/architecture.md` and `docs/reference/security-privacy.md`.

- **Tenancy.** A use case receives an `AuthorizedTenantContext` and does its database work inside
  `withTenantTransaction(ctx, tx => …)`, passing `tx` and `ctx` to repositories, which still write
  `tenantId: ctx.tenantId` into their predicates. Never import the root Prisma client in a module; never
  read a tenant id from a body, header or query, or accept one from a caller.
- **Authorization.** Every route has exactly one of `@RequirePermission(…)`, `@SignedIn()` (the caller's
  own session only; ADR-0027) or `@Public()`. A use case that loads a resource passes it to its policy
  (`src/common/policy`: `authorizeRead`, or `authorizeChange` for an action) before returning or changing
  it; a denied read is `404`, the same as absence. A policy decides from the context alone — never from a
  role or id the caller passes in.
  Repositories **select** fields — never `include` a whole relation into a response. A confidential
  field is marked `confidential(class, …)` in its response schema, and the use case builds that response
  with `project(schema, value, disclosedClasses(ctx, policy, resource, granted))` (`src/common/policy`),
  where `granted` is `PermissionService.grantedClasses(ctx)`. A response that may carry an `IDENTITY`,
  `MEDICAL`, `LEGAL_INTERNAL` or `FINANCE` field is released instead with
  `accessAudit.release(tx, ctx, { action: '<entity>.read', id }, { schema, value }, disclosed)`
  (`src/infrastructure/audit/access-audit.ts`), inside the read's transaction, which records the access
  first; `project` refuses those classes. A new response field goes into the field-classification fixture
  (`test/fixtures/field-classification.ts`) in the same PR.
- **Shape.** Controllers are thin: validate (Zod schemas, strict objects — ADR-0024), call one use
  case, return a response DTO — never a Prisma row. Errors are typed domain errors mapped to RFC 9457;
  never `throw new Error`. Workflow state changes only through transition commands. Generic create and
  update DTOs never carry `status`, `role`, `tenantId`, actors or evidence state; a dedicated command DTO
  takes exactly its validated input, and the server sets the actor and the resulting state.
- **Effects.** Audit with `audit.record(tx, ctx, …)` and side effects with `outbox.enqueue(tx, ctx, …)`,
  inside the business transaction; never call an external service inside a transaction.
- **Values.** Money is `Money` (`NUMERIC(19,4)` + currency); days are `DATE`; instants are
  `timestamptz`; the clock is injected.
- **Configuration** comes from `src/config/` only — no `process.env` elsewhere, no default for a secret.
- **Logs** never contain bodies, query strings, tokens, cookies or emails; use the logger, never
  `console`.
- **Tests** live with the feature: unit beside the code (`src/**/*.spec.ts`), integration tests as
  `test/**/*.integration-spec.ts`, API tests as `test/**/*.e2e-spec.ts`. The title contains the plan's lower_snake test name verbatim. Integration tests run as
  the runtime role against real PostgreSQL 18 and always use two tenants.
- Use-case files are `*.usecase.ts`. Gate: `just check`, plus `just test-int` / `just test-e2e` for
  the area you changed.
