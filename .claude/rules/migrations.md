---
paths:
  - "backend/prisma/**"
---

# Migration rules

Read `docs/reference/database.md` and `docs/implementation/01-conventions.md#migrations` first.

- **Never edit a committed migration** — `protected-paths` refuses it. Always add a new one.
- Run `just preflight` before any constraint or data migration; a non-zero report stops the migration
  until the owner approves a correction. Never delete rows to make a constraint pass.
- **A new tenant-owned table** ships, in the same migration, with `ENABLE` and `FORCE ROW LEVEL SECURITY`,
  its tenant policy, the owner's read policy and the tenant-immutable trigger (`scripts/generate-rls.ts
  <Model>` prints them), runtime-role grants, composite `(id, tenantId)` foreign keys, and a
  classification entry in `model-classification.ts`.
- **A data migration that writes tenant rows** lifts `FORCE ROW LEVEL SECURITY` on its table inside its
  own transaction and restores it before the transaction ends: the owner otherwise reads every row and
  writes none (`docs/reference/database.md`, "Database identities, grants and RLS").
- Partial indexes, CHECKs, policies, triggers and grants are hand-written SQL: comment them in
  `schema.prisma` and assert them with a catalog test — Prisma's drift check neither sees nor protects
  them. Do not enable the `partialIndexes` preview.
- Large changes go expand → backfill → `NOT VALID` then `VALIDATE` → switch → contract, each stage
  compatible with the previous application version.
- Keys: UUID v4 by default; `uuid(7)` for high-ingest append tables. Money `Decimal(19, 4)`; days
  `@db.Date`; instants `@db.Timestamptz(3)`.
- Before the PR: `just migrations` — a throwaway PostgreSQL 18, full replay, no drift.
