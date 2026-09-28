# ADR-0012 — Hosting

**Status:** Proposed — decided at `1.10.1` · **Requirements:** SR-NFR-REL-001/002, SysRD §13

## Context
No hosting exists. The medical-data and residency answers (OPEN-04), the production identity provider
(OPEN-01) and the same-origin rule (ADR-0003) all constrain the choice.

## Constraints the decision must meet
Managed PostgreSQL 18 with point-in-time recovery; private, versioned S3-compatible storage; containers
for `api`, `worker` and `realtime`; a reverse proxy that routes `/api/` to the API on the web app's
origin; a secret store and key custody; region and data-transfer terms acceptable to counsel; restore
drills that meet the approved RPO and RTO.

## Default until decided
Stay portable: containers, the S3 API, standard PostgreSQL, OpenTelemetry — no provider-specific service
in the code.

## Revisit when
Decided at `1.10.1` by a new ADR that supersedes this proposal and records the alternatives considered.
