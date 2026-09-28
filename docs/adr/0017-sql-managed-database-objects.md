# ADR-0017 — Partial indexes, checks, policies, triggers and grants live in SQL

**Status:** Accepted · 29 September 2026 · **Requirements:** SR-DB-003, SR-DB-005, SR-DB-009 ·
**Owners:** `0.4.1`–`0.4.10`, `0.7.1` · **Negotiated:** both drafts had left the choice implicit

## Context
Prisma cannot model row-level-security policies, triggers, grants or CHECK constraints, and supports
partial indexes only behind the `partialIndexes` preview flag (verified on 7.10.0: accepted with the flag
and `where: raw(…)`, refused without it).

## Evidence
Probe on 29 September 2026, Prisma 7.10.0 and PostgreSQL 18.6: after `migrate deploy`, a raw partial
unique index, a CHECK constraint, an RLS policy and a trigger were added by hand; `prisma migrate diff
--from-config-datasource --to-schema prisma/schema.prisma --exit-code` still reported no difference.

## Decision
These objects are hand-written in migration SQL, commented in `schema.prisma`, and asserted by **catalog
tests** (they query `pg_policies`, `pg_trigger`, `pg_constraint`, `pg_indexes` and the grants). The preview
flag stays off: a preview feature does not belong in the schema's security layer.

## Consequences
The drift check neither breaks on these objects nor proves they exist — the catalog tests do. A Prisma
upgrade re-runs the probe: if Prisma starts modelling one of them, the drift check will say so loudly.

## Revisit when
Prisma's partial-index support leaves preview and the team chooses to model them in the schema.
