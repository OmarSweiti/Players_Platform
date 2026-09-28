# ADR-0001 — A modular monolith in three processes

**Status:** Accepted · 28 September 2026 · **Requirements:** SYS-ARC-001…005 · **Owners:** `0.7.6`, Phase 2 realtime

## Context
One developer with AI agents, one tenant at launch, a dozen business domains, and requirements that
forbid microservices before a measured need (SYS-ARC-004) while requiring jobs and sockets to run apart
from HTTP (SYS-ARC-005).

## Decision
One NestJS codebase, one module per domain, deployed as three processes: `api` (HTTP), `worker` (jobs,
outbox relay, schedules — from `0.7.6`) and `realtime` (sockets — Phase 2). Modules own their tables and
talk through application services or events, never through each other's repositories or tables.

## Alternatives rejected
- **Microservices** — the operational cost of distributed transactions, deployments and tracing, with no
  evidence of need.
- **A single process** — long jobs and sockets would share the HTTP event loop, and a media failure
  would take down the API.

## Consequences
One unit to build, test and version; transactions stay local; boundaries stay extractable. Module
discipline is enforced by a lint rule on imports as well as review.

## Revisit when
A module needs independent scaling, fault isolation or a separate team — **measured**, not predicted.
