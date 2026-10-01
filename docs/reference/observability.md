# Observability and recovery

Target operations contract; this document makes no claim that production monitoring, recovery or service levels have been demonstrated. Requirements: SR-CORE-008/009, SR-NFR-OBS-001, SR-NFR-PERF-001/003, SR-NFR-REL-001/002, SYS-TEN-007, SYS-ASY-004/005, TEST-007/008. Owners: `0.3.7`, `0.10.1`–`0.10.4`, `1.10.4`–`1.10.6`, `1.10.12`, `1.10.13`; later release gates repeat the relevant evidence. [Observability ADR](../adr/0016-observability.md), [hosting ADR](../adr/0012-hosting.md), [security and privacy](security-privacy.md).

## Current evidence

| Inspected behavior | Evidence | Repair owner |
|---|---|---|
| Access logging uses raw URL, a caller-supplied tenant header and raw error message/stack. | `backend/src/common/interceptors/logging.interceptor.ts:14`, `:17`, `:24`, `:50` | `0.1.4`, `0.10.1`, `0.10.2` |
| Mail is a placeholder that logs recipients and full HTML; reset URLs embed a raw token. | `backend/src/infrastructure/mail/mail.service.ts:16`, `:22`, `:43` | `0.1.4`, `0.1.6`, `0.7.8` |
| The exception filter prints unknown exceptions and returns request.url. | `backend/src/common/filters/http-exception.filter.ts:41`, `:49` | `0.1.4`, `0.3.1` |
| The browser logs request and response bodies in development. | `frontend/src/shared/lib/api-client.ts:65`, `:83` | `0.1.4`, `0.9.4` |
| Readiness always returns ready. | `backend/src/health/health.controller.ts:22` | `0.3.7` |
| Prisma uses a pool maximum of ten and prints query text. | `backend/src/infrastructure/prisma/prisma.service.ts:26`, `:65` | `0.10.2`, `1.10.4`, `1.10.6` |
| Audit submission goes directly to a queue. | `backend/src/infrastructure/events/event.service.ts:37` | `0.7.1`, `0.7.2` |

These are source observations at backend `b5f32a4` and frontend `31aeb9a`. No source declaration establishes that a deployed monitoring service exists.

## Delivery boundary

Phase 0 installs pino JSON logging, allowlisted fields, secret canaries, request IDs propagated into outbox/worker work, real readiness and local failure/restore drills. These require no external telemetry vendor. Phase 1 adds OpenTelemetry, service metrics, error tracking, dashboards and owner-routed alerts after hosting/data-flow approval. Realtime extends instrumentation in `2.6.1`; it does not create a second correlation format.

Initialize instrumentation before importing instrumented application clients. A telemetry exporter outage must not erase committed domain/audit data or exhaust an unbounded in-memory queue. Bound buffers and record dropped-telemetry counts. Mandatory business audit has different availability semantics: failure to persist it aborts the protected operation.

## Safe event contract

```ts
export type SafeLogEvent = {
  timestamp: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  service: 'web' | 'api' | 'worker' | 'realtime';
  environment: string; release: string; event: string;
  requestId?: string; traceId?: string; spanId?: string;
  tenantId?: string; actorId?: string;
  route?: string; method?: string; status?: number; durationMs?: number;
  errorCode?: string; errorFingerprint?: string;
  eventId?: string; jobId?: string; attempt?: number;
  outcome?: 'success' | 'denied' | 'failed' | 'unknown';
};
```

Emit one JSON object per line. Build an allowlisted object rather than serializing requests, responses, exception objects or domain entities and trying to redact them afterward. Redaction patterns are a second defense. Log stable error code/type and a safe fingerprint; raw ORM validation messages may contain submitted values. Any stack collection requires a sanitizer and no attached request payload. Development does not relax confidentiality.

Never record passwords, cookies, authorization headers, provider tokens, OIDC codes/state, CSRF tokens, invitation links, signed URLs, medical/legal narrative, passport numbers or compensation. Do not log query strings or bodies. Route labels are templates such as `/players/:id`, not raw paths. IP/user-agent persistence is an OPEN privacy choice; default omit these fields from application telemetry and business audit until approved. Retain a narrowly scoped security signal only under its explicit policy.

At ingress create a server request UUID; accept an upstream ID only from a trusted proxy and after syntax/length validation. Return it as `X-Request-Id` and in problem details. Record actual trusted tenant/actor only after authentication; anonymous attempts have no guessed tenant attribution. Propagate request ID and originating trace context in the outbox envelope, never a user credential. Worker retries retain event/request correlation and add attempt/span identifiers.

Use W3C trace context with bounded validated inputs. Do not copy arbitrary baggage from browsers into downstream services. Long-running jobs start a new span linked to the originating trace when appropriate. OIDC and webhook routes suppress sensitive URL/query attributes. Instrumentation defaults must be reviewed: automatic capture can bypass an application logger's allowlist.

Frontend errors carry route template, application release, request ID, stable error code and a coarse browser category. Disable session replay, DOM capture, form capture and confidential screenshots by default. A synthetic sentinel suite captures stdout, browser console, exception reports and exported spans and proves prohibited values absent. Run it whenever telemetry instrumentation or serializers change.

## Health, failure and shutdown

`GET /health/live` reports process liveness only. `GET /health/ready` performs bounded probes of PostgreSQL and other dependencies required by that process, returning 503 when it cannot serve its declared workload. Neither endpoint reveals hosts, versions, data counts, keys or detailed failures. Private diagnostics may carry safe component statuses.

API readiness includes PostgreSQL and required shared rate-limit storage; if protection cannot be enforced, fail affected requests closed. Worker readiness includes database, broker and required worker capabilities. Scanner failure leaves files quarantined. Storage failure prevents upload/download without corrupting domain metadata. A remote mail outage permits durable intent to queue, with age-based alerting. Each capability documents degraded behavior; do not infer that a failed notification provider must take down unrelated reads.

Before shutdown, stop accepting traffic/jobs, mark readiness false, drain within a bounded grace period, close connections and release or expire leases safely. API termination after commit but before response must be recoverable through idempotency. Worker termination after provider acceptance may leave an unknown external outcome; do not assert exactly-once external delivery. Socket shutdown/reconnect must recover from persisted message sequence state.

## Metrics and provisional alerts

Labels are bounded: service, environment, route template, outcome, job type and provider adapter. Do not label metrics by tenant, user, document, request or message ID. Authorized tenant-level usage reporting belongs in application projections. Restrict operators' access to tenant-correlated logs and traces.

| Signal | Initial trigger to calibrate on staging | Runbook first action |
|---|---|---|
| Outside-in login/read/download probes | Three consecutive failures | Check ingress, current release and dependency readiness. |
| HTTP failures | 5xx above 2% for five minutes with at least 20 requests/minute | Compare release and route; inspect safe error fingerprints. |
| Simple operation latency | p95 above 500 ms for fifteen minutes at the accepted load | Separate database wait, policy, CPU and external latency. |
| Complex dashboard latency | p95 above 2 seconds for fifteen minutes | Inspect bounded query count and projection fan-out. |
| Database connection utilization | Above 80% for ten minutes or sustained acquisition timeouts | Sum API/worker/realtime pools, inspect leaked transactions and concurrency. |
| Oldest eligible outbox event | Above 60 seconds for five minutes | Inspect tenant claim lease, broker and worker health. |
| Failed/dead jobs | Any exhausted critical job; notification age above five minutes | Inspect durable receipt and remote outcome before replay. |
| Scan quarantine age | Above fifteen minutes for supported file sizes | Check scanner capacity and signatures; keep release denied. |
| Security boundary | Any confirmed cross-tenant success | Contain the capability, revoke affected access, preserve evidence. |
| Backup freshness | Successful recoverable point older than approved RPO | Stop risky release and verify independent backup access. |
| Certificate/credential expiry | Thirty, fourteen and seven days remaining | Rotate with overlap and run protocol regression tests. |

Thresholds are engineering starting values, not observed production performance. Each alert has a named owner, escalation contact, severity, dashboard query, runbook and tested delivery route. `1.10.12` owns actual delivery, acknowledgment and recovery evidence. A solo developer must agree coverage and backup contact before promising round-the-clock response. Telemetry vendor, region, retention and data processing remain OPEN until `1.10.1`/`1.10.4` settle them.

## SLO and capacity evidence

SR-NFR-REL-001 sets a 99.9% monthly availability target. Define eligible requests/probes and successful outcomes before measurement; record maintenance exclusions explicitly rather than removing downtime after the fact. Keep outside-in evidence independent of the application. Report login, core API and authorized download availability separately so a healthy static page cannot hide failed business operations.

SR-NFR-PERF-001 requires p95 at most 500 ms for simple operations and at most 2 seconds for complex dashboards under the agreed capacity envelope. Record dataset size, concurrent users, read/write mix, file sizes, hardware, replica count, process pool budgets, test duration, cold/warm conditions, release/pins and error rate. Report end-to-end latency as well as dependency-excluded budgets. Include primary-database session checks in capacity tests; do not remove them to obtain a favorable result.

`1.10.6` owns the first accepted workload and load scripts; the envelope is the design target for one small server (ADR-0021), revisited with the first customer's volumes. A laptop result is a local experiment, not deployed capacity evidence. Follow-up phases expand the envelope with sockets, imports, media, public shares and additional tenants. Connection budget must reserve operational headroom and account for migrations and IdP database connections, not just the API pool.

## Backup and restore contract

`0.10.3` drills disposable local PostgreSQL and object services only. `1.10.5` builds the staging backup/restore path using the selected infrastructure and restricted credentials; `1.10.13` independently follows it and records the timed recovery and incident rehearsal. Initial targets are RPO at most 24 hours and RTO at most 8 hours, subject to owner approval for the actual business and data classes. Backup success alone cannot demonstrate either target.

The runbook must identify:

1. Database backup/PITR identifiers, object versions/manifests, encryption keys and independent access needed for recovery.
2. Application image digests, umbrella/app revisions, migration history and SQL-managed catalog objects.
3. Identity realm/configuration and approved recovery mechanism; no exported raw user credentials in public artifacts.
4. A clean isolated destination with all real email, signature, payment and outbound webhook dispatch disabled.
5. Restored tenant counts, foreign-key/catalog assertions, audit continuity, representative immutable object digests and denied cross-tenant probes.
6. Invalidation of restored application sessions and review of IdP/session recovery state before opening traffic.
7. Outbox/inbox/provider reconciliation so restored queues do not blindly repeat a remote effect.
8. Measured last recoverable point and elapsed recovery time, failures, operator, runbook revision and remaining remediation.

Never restore over a live environment during a drill. Production deletion, retention holds and backup expiration follow approved policy; “restore available” does not authorize indefinite sensitive-data retention. Keep a restricted drill report with synthetic examples in release evidence. Repeat before first production release, after material storage/identity/database changes, and on the approved periodic schedule; six months is the provisional maximum interval pending the operational owner.

## Debugging and incidents

Start with environment/release, UTC time, route template, safe request ID and observed status/problem code. Reproduce using synthetic data with the same role, relationship and tenant boundaries. Trace API → database/audit → outbox → worker → provider, and web/realtime where present. Never disable RLS, policy, audit or scanning to make a reproduction pass; never copy live payloads into an issue or coding-agent transcript. See the [debugging playbook](../implementation/02-development-workflow.md#debugging).

For suspected disclosure: disable the affected server capability, revoke implicated sessions/grants, preserve restricted evidence, record the incident timeline and notify the designated owner. The owner determines external notification duties, with legal advice recommended; this reference invents no statutory timeline. Restore exposure only after a reproducing regression test, reviewed containment scope and reconciliation of affected records/releases. Provider compromise requires provider-side recovery as well as local session invalidation.

## Verification and evidence

The owning phase steps define exact feature test names and scripts. Their Verify commands must exercise real dependency failures, capture canaries and assert durable state; matching a log string or listing a test file is insufficient. Required demonstrations include: one request correlated through a committed job, one controlled dependency outage, one audit failure rolling back a mutation, one worker crash/retry with honest external outcome, one delivered alert and one timed isolated restore.

Use `0.10.1`/`0.10.2` for logger/canary regression, `0.3.7` for readiness, `0.10.3`/`0.10.4` for local drills, `1.10.4`–`1.10.6` for staging instrumentation/recovery/capacity tooling, and `1.10.12`/`1.10.13` for delivered alerts and independent recovery. The [phase plan](../implementation/README.md) and [test catalog](test-catalog.md) are the command/name authority. Record actual outputs, unrun checks and limitations with the merged PR and pinned revisions.
