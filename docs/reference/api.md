# API contract

Target contract for SR-CORE-001..010 and SR-API-001..009. Owners: `0.3.1`–`0.3.9`, `0.5.5`–`0.5.8`, `0.6.2`–`0.6.4`, `0.7.7`, `0.9.4`; each domain owns its endpoints. [ADR](../adr/0010-api-contract.md), [authorization](security-privacy.md), [workflow states](domain-workflows.md), [generated test catalog](test-catalog.md).

## Current evidence and migration boundary

The current API defaults to prefix `api` (`backend/src/main.ts:40`), registers a response interceptor in bootstrap (`:19`) and again in the module (`backend/src/app.module.ts:54`), and has separate global validation registrations (`backend/src/main.ts:45`; `backend/src/app.module.ts:56`). The browser sends `X-Tenant-ID` and contains automatic token-refresh logic (`frontend/src/shared/lib/api-client.ts:58`, `:94`). These observations describe the inspected baseline, not the target. Phase 0 replaces those mechanisms and tests the actual old routes before introducing `/v1`.

## Route and request rules

All product routes use `/api/v1`. Operational probes are unversioned `/health/live` and `/health/ready`; ingress routes them directly to Nest and exposes only minimal status. OIDC callback/logout protocol endpoints remain under `/api/v1/auth`. No compatibility alias silently preserves a retired credential or unversioned business route.

Use plural resource nouns: `GET /players`, `POST /players`, `GET /players/{id}`, `PATCH /players/{id}`. Use explicit action endpoints for controlled transitions: `POST /contracts/{id}/submit`, `/approvals/{id}/decide`, `/legal-tickets/{id}/assign`, `/enrollments/{id}/cancel`. A generic patch cannot assign tenant, actor, permission, computed total, scan verdict or lifecycle state. Archive is an explicit command; destructive purge is a separately authorized retention process.

Each controller operation declares authentication/public classification, permission, response DTO, errors, pagination/filter limits, idempotency and audit behavior in OpenAPI. Route introspection rejects unclassified routes. Resource policies still execute inside the use case; a decorator does not prove ownership. Public callbacks and shares have independent scopes, validation and rate limits.

One global validation pipeline enforces DTO allowlists, unexpected-property rejection, bounded nested objects/arrays, length/type/range checks and explicit UUID parsing. Do not implicitly coerce arbitrary truthy strings into booleans. Normalize each field according to its meaning: trim identifiers/search input, preserve meaningful narrative whitespace, normalize email consistently, and never silently rewrite evidence. JSON bodies default to a bounded 1 MiB limit, with smaller per-endpoint limits where appropriate; files use the upload pipeline. The threshold is an initial engineering default, reviewed against measured payloads.

## Authentication, cookies and CSRF

Browser sign-in redirects to `GET /api/v1/auth/login`; its `returnTo` accepts only validated same-origin application paths. Nest handles authorization code + PKCE, state, nonce and validated ID-token claims (`0.5.5`). Each attempt is bound to the initiating browser by a short-lived `__Host-sodara_preauth` cookie (HttpOnly, Secure, SameSite=Lax) that grants no access to any business route; a step-up binds to the existing session instead. A valid state alone is insufficient: the callback requires the matching binding, consumes the attempt once and sets a new `__Host-sodara_session`. The browser never receives a provider token. Protected requests recheck the session and membership against primary PostgreSQL.

`GET /api/v1/auth/session` returns the member, the selected tenant, locale, effective permissions (`0.6.6`), an assurance summary and the session's CSRF token, with `Cache-Control: no-store` (`0.5.6`). The CSRF token is **derived, not stored** — an HMAC of the session-token digest under a keyed, rotatable secret — so every tab receives the same value until the session rotates. Unsafe browser requests require `X-CSRF-Token` and an exact allowed `Origin`; neither CORS nor SameSite alone is CSRF protection. Logout is a POST that revokes the database session before clearing the cookie. OIDC back-channel logout authenticates with the verified logout token instead of a CSRF token; that exemption is explicit and covered by negative tests.

Next server components forward the incoming session cookie only to the fixed trusted internal API origin and preserve the validated public host context; they never forward it to a URL selected by the browser. Authenticated server fetches use `no-store`. Mutating operations use the browser's same-origin API path and CSRF contract. A 401 clears confidential UI/query state and offers sign-in; it does not invoke a retired refresh endpoint or endlessly replay a write. Provider-session renewal occurs through the OIDC flow.

## Successful responses

```ts
export type Success<T> = { data: T };
export type Collection<T> = {
  data: T[];
  page: { nextCursor: string | null; hasMore: boolean };
};
export type MoneyDto = { amount: string; currency: string };
export type CivilDate = string; // strictly YYYY-MM-DD, validated calendar date
```

Return 200 for reads/updates, 201 plus `Location` for created resources, 202 plus a job location for durable asynchronous acceptance. Successful commands without a useful resource return `{ "data": null }` with 200. A deliberately documented 204 has no JSON body and bypasses wrapping. OIDC redirects and binary downloads are also explicit transport exceptions. Exactly one interceptor applies the success envelope; controllers do not prewrap it. Errors never pass through that interceptor.

Decimal money uses canonical non-exponent strings and ISO currency codes; callers must not convert through JavaScript Number. Civil dates have no offset or time. Instants use RFC3339 UTC with millisecond precision. Byte counts that exceed safe integer bounds use bounded decimal strings. IDs are opaque UUIDs; ordering comes from documented sort keys, not the assumed UUID version. Sensitive DTOs return only authorized fields; hidden values are absent, not included as masked originals.

## Problem details

Use `application/problem+json` following [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457). The extensions and status mapping below are Sodara's contract. Standard HTTP status semantics remain authoritative; the JSON `status` equals the actual response status.

```json
{
  "type": "urn:sodara:problem:validation-failed",
  "title": "Validation failed",
  "status": 400,
  "detail": "Check the highlighted fields.",
  "instance": "urn:uuid:8c22c808-fab2-4b88-988b-56cf1fe34f09",
  "code": "VALIDATION_FAILED",
  "message": "Check the highlighted fields.",
  "requestId": "8c22c808-fab2-4b88-988b-56cf1fe34f09",
  "fieldErrors": [{ "field": "/dateOfBirth", "code": "INVALID_DATE", "message": "Enter a valid date." }]
}
```

`code` and field codes are stable machine identifiers. `type` is a stable problem-type URI; `title` identifies that type. `message` is localized and mirrors safe `detail` when detail is provided. `fieldErrors` is an empty array when no field is implicated. Fields use JSON Pointer paths; errors never echo submitted values. Unknown exceptions become a generic internal error with a request ID, without raw Prisma errors, SQL, paths, cookies, token queries or stack traces. `instance` identifies the occurrence without a sensitive URL.

| HTTP | Stable code | Meaning / client behavior |
|---|---|---|
| 400 | `VALIDATION_FAILED`, `INVALID_CURSOR` | Invalid shape/type/query; focus the relevant form fields. |
| 401 | `AUTHENTICATION_REQUIRED`, `SESSION_EXPIRED` | No valid application session; clear confidential state and sign in. |
| 403 | `FORBIDDEN`, `CSRF_FAILED`, `STEP_UP_REQUIRED` | Known authorized context lacks action/assurance; step-up only to an allowlisted auth route. |
| 404 | `NOT_FOUND` | Missing or unreadable scoped object; do not reveal foreign ownership. |
| 409 | `CONFLICT`, `INVALID_TRANSITION`, `IDEMPOTENCY_IN_PROGRESS`, `IDEMPOTENCY_KEY_REUSED` | Business conflict or retry-key conflict; no blind resubmit with a new key. |
| 412 | `REVISION_MISMATCH` | Supplied entity tag is stale; reload and reconcile edits. |
| 413 | `PAYLOAD_TOO_LARGE` | Reject before costly parsing or storage allocation. |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Request/file type not accepted. |
| 428 | `PRECONDITION_REQUIRED` | Required `If-Match` absent. |
| 429 | `RATE_LIMITED` | Include bounded `Retry-After`; do not expose victim account existence. |
| 500 | `INTERNAL_ERROR` | Unexpected failure; show request ID and safe retry guidance. |
| 503 | `DEPENDENCY_UNAVAILABLE` | Required dependency prevents safe service; readiness and retries reflect this. |

For unreadable resource identifiers, authorization precedes detailed existence, revision and business-state errors. Do not turn a cross-tenant ID into a 412 or a uniqueness message that confirms its existence. Authentication, CSRF and validation failures do not enter the mutation transaction.

## Collections, filtering and search

Default `limit=25`, maximum 100; larger values fail validation. Default ordering is `(createdAt DESC, id DESC)` with lexicographic keyset pagination. The cursor encodes a versioned last sort tuple and a fingerprint of tenant, filter, sort and projection scope; sign it or validate it against trusted request state, and reject incompatible reuse. The cursor never grants access. Every page reruns authorization and field projection.

```http
GET /api/v1/players?limit=25&status=ACTIVE&sort=createdAt:desc&cursor=opaque
```

```json
{ "data": [], "page": { "nextCursor": null, "hasMore": false } }
```

Fetch at most `limit+1` authorized rows; set `hasMore` and generate a cursor from the final returned row. Alternate allowed sorts must include a unique tiebreaker and explicit null/collation behavior. Sorting by a mutable field has documented live-list semantics; exports use their own stable snapshot policy. Do not claim that any cursor creates a consistent database snapshot across requests.

Filters/operators are endpoint allowlists, including bounded date ranges, arrays and search length. No raw Prisma where/order JSON. Search operates on authorized projections and Arabic/Latin names/aliases; counts exclude hidden matches. Totals are omitted unless an endpoint explicitly authorizes and budgets them. Review bounded query counts and representative EXPLAIN plans; “every filter gets an index” and “every page requires exactly one SQL query” are not engineering laws.

## Revisions and conditional mutation

Mutable aggregate roots have integer `revision`, initially 1. GET returns it and a strong opaque `ETag` bound to the resource representation, revision and projection. Example notation is illustrative, not a license to accept a fabricated tag. PATCH and concurrent state-changing commands require the latest returned `If-Match`; missing gives 428, stale gives 412. Reject wildcard or multi-tag forms unless explicitly designed and tested. A confidential field change may increment the aggregate revision without revealing the field.

Within the authorized tenant transaction, use a compare-and-update predicate containing ID, tenant and expected revision; increment once with the accepted mutation. A zero-row update after authorization becomes a precondition failure. Required audit/outbox writes occur in the same transaction. For state transitions, capacity, approval order and other cross-row invariants, use appropriate row locks or isolation in addition to revision checks. Barrier-synchronized races prove that competing requests cannot both win. After 412 the UI preserves unsaved local work and asks the user to reconcile; it never silently overwrites.

## Idempotency state machine

Owner `0.7.7` installs this mechanism; domain steps declare where it is mandatory. Require `Idempotency-Key` for retried creates, approval/evidence commands, enrollment, export/import initiation and provider-facing commands. Bound key length to 128 printable safe characters. Namespace by tenant, actor, HTTP method, canonical resource/action path and key; hash a canonical validated request plus relevant preconditions. Route parameters are part of the path binding.

```text
ABSENT --claim lease--> IN_PROGRESS --atomic local commit--> SUCCEEDED
                         │                      └--> terminal REJECTED
                         └--lease expired--> retry/reconcile (never assume failure)
External delivery: QUEUED → SENDING → ACCEPTED | FAILED | UNKNOWN → RECONCILED
```

```ts
type IdempotentCommand<T> = {
  method: string; canonicalPath: string; key: string;
  requestHash: string; expectedRevision?: number;
  execute(tx: TenantTransaction): Promise<{ status: number; data: T; location?: string }>;
};
```

1. Authenticate, check current permission/resource visibility and validate the request shape. Look up the namespace/key and compare the request hash before evaluating a new execution's lifecycle or revision preconditions. Claim a new record with a bounded lease and fencing generation; duplicate active claims return 409 with `Retry-After`.
2. Same namespace/key with different request hash returns `IDEMPOTENCY_KEY_REUSED`. A fresh-key retry is not an acceptable client workaround for an unknown outcome.
3. The business mutation, audit, outbox intent and terminal idempotency outcome commit together under the claim's fencing generation. On transaction failure the mutation and terminal outcome roll back.
4. A matching completed retry returns the recorded status and stable receipt/resource identity without repeating the mutation, even though its original `If-Match` became stale because the first execution succeeded. Current authorization is still mandatory. Rebuild any sensitive projection; do not serve an old privileged response to a now-restricted member. Only a new execution evaluates lifecycle/revision guards before its mutation.
5. If a worker/request loses its lease, its old fencing generation cannot commit. An expired lease is reclaimed only after checking durable outcome; external unknown outcomes use provider reconciliation, not blind replay.
6. Retain ordinary command records for at least 24 hours initially; entity uniqueness and immutable decision/event IDs prevent duplicate effects beyond that window. Signature/payment/provider receipts follow evidence retention policy and are not erased by the generic TTL.

Avoid storing arbitrary request/response bodies in the record. Store hashes and a minimal safe result reference; any bounded necessary payload has explicit classification. Tests cover simultaneous claims, different body/path/precondition, successful replay with the original now-stale `If-Match`, crash before and after commit, stale-lease fencing, revoked access on replay and expired-key behavior.

## Jobs, webhooks and realtime

Bulk imports/exports return 202 with `{data:{id,status}}` and an authorized job location. Polling supports progress/counts, safe row-error reports, cancellation before irreversible work and expired-result state. A job rechecks current membership, feature availability and export scope before processing and before issuing a download. Formula-safe CSV rendering and confidential-column projections are part of export acceptance (`1.9.1`, `2.9.1`).

Provider callbacks verify signatures on bounded raw bytes, configured issuer/account, timestamp and event ID before parsing business fields. Atomically persist a tenant-bound `WebhookReceipt`, unique by provider/account/remote event ID, and a local `OutboxEvent` UUID; `ConsumerInbox` then deduplicates processing of that local event. Reject mismatched envelope/payment ownership and process out-of-order or duplicate events through explicit state transitions. Never select tenant solely from an unauthenticated callback field. A valid callback acknowledgment means durable receipt, not necessarily completed business processing. Owners `3.5.1`, `3.4.2`; OIDC logout has its own protocol validation in `0.5.7`.

Realtime begins in `2.6.1`. Validate the session, Origin, tenant and conversation membership at connection/subscription and sensitive message operations. Membership/session revocation must disconnect or deny subsequent use; a room name is not authorization. Persist messages before acknowledging; use stable client command IDs and per-conversation sequence cursors for reconnect. Socket events carry safe references and request correlation, not confidential record snapshots. The same error codes apply in a documented event error payload, without pretending an event has an HTTP status.

## File endpoints

`POST /uploads` validates the typed owner, classification, quota and intended size/type, and returns a short-lived quarantine PUT plus upload ID. `POST /uploads/{id}/complete` verifies exact stored content and schedules scanning; it does not synchronously process video or mark it clean. `GET /uploads/{id}` exposes safe progress. `GET /files/{id}/download` reauthorizes the typed owner and returns a short-lived version-pinned download URL only for immutable content whose lifecycle is READY and scan verdict is CLEAN. Do not accept arbitrary storage keys in these requests. Confidential classes may require a streaming proxy for stronger revocation; an already-issued signed URL remains a bearer capability within its effective lifetime.

## OpenAPI and compatibility

Owner `0.3.9` commits `backend/openapi/openapi.json` generated from the same route/DTO composition as runtime, without contacting live providers. Include cookie security, required CSRF headers on writes, problem responses, revision headers, idempotency requirements, decimal strings, date formats and all discriminated states. Generation must fail on missing request/response metadata rather than emitting an empty generic object.

CI regenerates and rejects a diff, compares against the target development contract with the pinned breaking-change tool, and executes runtime response-contract tests. Removing a route/field, making a field required, changing semantics, narrowing an enum or changing authorization expectations requires compatibility analysis; a passing schema diff alone cannot classify every semantic break. A reviewed version/deprecation decision is explicit. Frontend generation uses the committed artifact at the selected backend revision, not a running developer's Swagger URL.

```bash
# From the adopted umbrella, after the owning Phase-0 steps exist:
(cd backend && npm run openapi && git diff --exit-code -- openapi/openapi.json)
(cd frontend && npm run api:generate && npx --no-install tsc --noEmit)
```

The frontend generation step also checks its generated artifact for drift in CI. No generic client type assertion may hide a breaking response change. Feature suites reside under module/feature paths and name the exact tests listed by their owning microsteps. This reference is not a second test registry.
