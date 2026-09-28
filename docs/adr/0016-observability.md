# ADR-0016 — Observability

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-CORE-008/009, SR-NFR-OBS-001, SYS-TEN-007
· **Owners:** `0.10.1`, `0.10.2`, `1.10.4`

## Context
Logs today carry tokens, emails and full URLs; request ids are random per interceptor; readiness is a
constant.

## Decision
Phase 0: `nestjs-pino` JSON logs with request id, opaque tenant and member ids, route template, status and
duration; serializers that **allowlist** fields, proven by canaries; request ids that travel into jobs;
real readiness. Phase 1, with hosting: OpenTelemetry traces and metrics, error tracking, dashboards and
alerts against the budgets in [`../implementation/01-conventions.md`](../implementation/01-conventions.md#budgets).
Details: [`../reference/observability.md`](../reference/observability.md).

## Alternatives rejected
Blocklist redaction (misses new fields); logging bodies "in development only" (development data leaks
too).

## Consequences
A new log field is added to the allowlist deliberately and the canary test guards it.

## Revisit when
The hosting choice brings a managed telemetry stack.
