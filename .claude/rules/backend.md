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
- **Authorization.** Every route has `@RequirePermission(…)` or `@Public()`. A use case that loads a
  resource calls `authorize(ctx, action, resource)` before returning or changing it; a denied read is
  `404`. Repositories **select** fields — never `include` a whole relation into a response. A new
  response field goes into the field-classification fixture in the same PR.
- **Shape.** Controllers are thin: validate (DTOs with `whitelist` + `forbidNonWhitelisted`), call one use
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
