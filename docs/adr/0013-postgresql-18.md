# ADR-0013 — PostgreSQL 18 from Phase 0

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-DB-001, SR-DB-005, SysRD §2 ·
**Owner:** `0.2.2` · **Negotiated:** Codex first proposed staying on 17 for the MVP and conceded on the
evidence

## Context
The requirements specify PostgreSQL 18. CI's migration replay used `postgres:17`, introduced on
28 September 2026 with the delivery flow (backend `68be90a`) — a default, not a qualification.

## Evidence
Executed 28 September 2026: `postgres:18` → PostgreSQL 18.6; Prisma CLI and client 7.10.0;
`prisma migrate deploy` applied all six migrations; `prisma migrate diff --from-config-datasource
--to-schema prisma/schema.prisma --exit-code` → "No difference detected"; native `uuidv7()` available.

## Decision
PostgreSQL 18, pinned by digest, in compose, CI and every hosted environment, from Phase 0. The
row-level-security policies, grants and triggers of Phase 0 are written and tested on 18.

## Alternatives rejected
PostgreSQL 17 now and an upgrade later — a major-version upgrade and requalification bought for no
demonstrated benefit, while no production data exists.

## Consequences
The hosting decision requires managed PostgreSQL 18. A read-only preflight still precedes changes to any
database that might hold real data (OPEN-11).

## Revisit when
The next major version is due (plan its qualification as a microstep).
