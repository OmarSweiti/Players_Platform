# ADR-0014 — Side effects through a transactional outbox

**Status:** Accepted · 28 September 2026 · **Requirements:** SYS-ASY-001…005, BR-RULE-10, SR-CORE-010 ·
**Owners:** `0.7.5`–`0.7.8`

## Context
Audit and events are queued directly today (`event.service.ts:37`): a crash between the database commit
and the queue loses them, and a retry can duplicate them.

## Decision
The business transaction writes an `OutboxEvent` (identifiers only, a unique dedup key, under RLS); a
worker relay discovers tenants through a registry role, claims due events per tenant with `FOR UPDATE
SKIP LOCKED`, and publishes to BullMQ on Valkey; handlers run in their tenant's transaction and record a
`ConsumerInbox(consumer, eventId)` row — tenant-owned, under forced RLS — so each effect commits once; retries back off to a bound, then `DEAD`.
External effects promise what they can: the intent is durable and local processing is deduplicated, but
a crash after the provider accepted a message can send it again — repeatedly, if crashes repeat — unless
the provider offers idempotency keys; bounded retries end in an explicit, alerted failure, never silence.

## Alternatives rejected
Queue-only publishing (loses events on a crash); Kafka (unneeded at this scale); a polling-only database
queue (viable, kept as the fallback if Valkey becomes a burden).

## Consequences
A worker process to run; every side effect is at-least-once and every consumer idempotent.

## Revisit when
Throughput or ordering needs exceed what BullMQ on Valkey provides, measured.
