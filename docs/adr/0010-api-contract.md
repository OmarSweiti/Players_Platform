# ADR-0010 — The API contract: versioned REST, problem details, one envelope

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-CORE-002…005/010, SR-API-001…009,
SYS-ARC-003 · **Owners:** `0.3.1`–`0.3.9`, `0.7.7`, `0.9.4`

## Context
Responses are wrapped two or three times, errors come back as 200s, validation runs twice, and there is
no committed contract; the frontend hand-writes its types.

## Decision
REST under `/api/v1`; errors are RFC 9457 problem details with stable `code`, `message`, `requestId` and
`fieldErrors`; success is `{ data }` and collections `{ data, page: { nextCursor, hasMore } }`, applied
once; keyset pagination with a maximum of 100; allowlisted filters; `revision` with `ETag` and `If-Match`
(412 stale, 428 missing); idempotency records for retried commands; the OpenAPI document is committed,
regenerated and diffed in CI, and a breaking change needs a new version; the frontend uses only a client
generated from it. Details: [`../reference/api.md`](../reference/api.md).

## Alternatives rejected
GraphQL (authorization per field is exactly our hardest problem, made harder); unversioned routes; plain
resources without an envelope (reasonable — the envelope won because the current code is closest to it);
a custom error format where a standard exists.

## Consequences
Contract changes are visible diffs in both repositories; the breaking-change check gates PRs.

## Revisit when
A public partner API (Phase 4) needs its own versioning and rate plans.
