# ADR-0004 — Tenancy in depth, enforced by the database

**Status:** Accepted · 28 September 2026 · **Requirements:** BR-RULE-01, SYS-TEN-001…007, SR-DB-004,
SR-NFR-SEC-002/003 · **Owners:** `0.4.2`–`0.4.5`, `0.6.9` · **Negotiated:** Claude first proposed an
implicit query-injecting Prisma extension with row-level security only on confidential tables in Phase 2,
and conceded

## Context
Today every repository adds `tenantId` by hand, nothing fails when one forgets, the database enforces
nothing, and six foreign keys can cross tenants. SYS-TEN-005 asks only to "consider" row-level security
for the riskiest tables.

## Decision
Four layers, each able to stop a leak the others miss:
1. **Explicit context.** Use cases receive an `AuthorizedTenantContext`, minted only from a verified
   session, a job or an audited platform operation.
2. **The tenant transaction.** `withTenantTransaction(ctx, fn)` sets `app.tenant_id` with
   `set_config(…, true)` — transaction-local, on the same connection that runs `fn`. Repositories take the
   transaction client; modules cannot import the root client.
3. **The database.** Row-level security **enabled and forced on every tenant-owned table** — outbox and
   inbox included — for `sodara_app`, a non-owner NOBYPASSRLS runtime role; migrations run as a separate
   role; composite and same-parent foreign keys; tenant ids immutable. Missing context means no rows.
4. **Proof.** A two-tenant suite over every route and job, raw SQL as the runtime role, and pool-reuse tests.

Cross-tenant work discovery (the outbox relay) uses a registry role that can read only tenant ids, then
claims work inside each tenant's transaction — never a BYPASSRLS client.

## Alternatives rejected
- **Middleware or an ORM extension alone** — an omitted predicate is a leak.
- **RLS alone** — it does not separate roles inside a tenant, and a mistake in context setting would go
  unnoticed without the explicit layer.
- **A database per tenant** — operational cost unjustified for one to a handful of tenants.

## Consequences
Every query runs inside a short transaction; every new tenant table ships with its policy, grants and
tests; the policies are SQL that Prisma's drift check cannot see, so catalog tests assert them
(ADR-0017). RLS does not replace confidential-field policy (ADR-0005).

## Revisit when
Tenant count or size justifies partitioning or database-per-tenant, measured.
