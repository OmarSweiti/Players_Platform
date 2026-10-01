# ADR-0022 — The SysRD's stack, kept current

**Status:** Accepted · 1 October 2026 · **Decided by:** the owner · **Requirements:** SysRD §2 (the
technology stack) · **Relates to:** erratum E-03

## Context
The SysRD names the stack:
- Next.js 16.3 with React 19 and TypeScript;
- NestJS 11;
- Prisma ORM 7;
- PostgreSQL 18;
- Redis or Valkey, with BullMQ;
- S3-compatible object storage;
- Socket.IO;
- PostgreSQL full-text search;
- OpenTelemetry, Prometheus/Grafana and Sentry.

It says exact production versions are pinned during implementation. On 1 October 2026 the owner
confirmed that the SysRD is the stack to keep, and that newer releases must be allowed as they are
published: the platform should stay on the most modern versions of that stack.

## Decision
1. **The SysRD's technologies are the stack.** Changing a technology, as opposed to its version, takes a
   new ADR. Two choices are already recorded: Valkey, which the SysRD allows as one of "Redis or Valkey";
   and Versity S3 Gateway as the local S3-compatible store, since MinIO has no image left to pin
   ([ADR-0020](0020-local-object-store.md)).
2. **Versions named in the SysRD are floors, not ceilings.** Newer stable releases are allowed and
   preferred: NestJS 12 over 11, TypeScript 6 and then 7 as the toolchain supports them, Prisma 8 once it
   is stable, and the next PostgreSQL major once it is qualified. The SysRD itself stays frozen; this
   record says how to read its version numbers. The versions in use are the ones in the lockfiles,
   `.nvmrc` and `infra/compose.yaml`.
3. **How the stack stays current:**
   - **Patch and minor releases** arrive monthly through Dependabot, grouped, after a seven-day cooldown,
     and merge when every check is green.
   - **Major releases** move one at a time, deliberately: the migration notes are read and the app is
     exercised. When code must change, the upgrade is a planned microstep; NestJS 12 and TypeScript 6 are
     `0.2.9`, which is now in the [demo milestone](../implementation/demo-milestone.md).
   - **A major the toolchain cannot support yet** is held in `dependabot.yml`, with its blocking error
     quoted, until the blocker is gone. Today that means TypeScript 7 and ESLint 10 in the frontend, and
     NestJS 12 and the TypeScript majors in the backend until `0.2.9`. A hold is never a reason to stay
     behind once the ecosystem has moved.
   - **Runtime and service images** (Node, PostgreSQL, Valkey, Keycloak, ClamAV, Caddy, the object
     store) are pinned by digest and move to new releases the same way. A PostgreSQL major gets a
     qualification step, as [ADR-0013](0013-postgresql-18.md) did.
   - **Pre-releases** (release candidates, betas, previews) never ship; at most they are tried on a
     branch.
   - **Security fixes** are taken as soon as they are published, outside the monthly rhythm.
   - **A monthly currency review**, run with the Dependabot round, checks every held major and every
     SysRD component for a new major or line, and records what moved, what is held and why.

## Alternatives rejected
- **Pinning the SysRD's versions.** The stack would start ageing on day one. The SysRD asks for pins only
  of exact production patch versions.
- **Taking every release immediately.** The cooldown exists because bad releases get pulled, and majors
  merged blind break the build: two Dependabot majors did so on 28 September 2026.

## Consequences
- Upgrade steps stay small because the moves are frequent; a major left for a year turns into a project.
- The risk register's dependency-churn row follows this record.

## Revisit when
A SysRD technology is discontinued, changes its licence, or stops being the best fit. A new ADR then
names its replacement.
