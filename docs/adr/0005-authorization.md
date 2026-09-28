# ADR-0005 — Authorization: a permission catalog, object policies, confidential projections

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-AUTH-009, SR-ACL-003…008, SR-API-001/002,
BR-RULE-02/07/12 · **Owners:** `0.6.1`–`0.6.9`, `0.7.4`

## Context
The permission seed crashes on 20 of its 63 names; routes that declare nothing are allowed; a player holds
`medical.read`; confidential filtering is chosen by the caller; `SUPER_ADMIN` is seeded with everything.

## Decision
- **RBAC for the baseline:** an explicit catalog — key, category, action and confidentiality declared,
  never parsed from a name — and a default role matrix, both code, synced to the database and checked at
  boot. `SUPER_ADMIN` holds nothing in a tenant; support access is an audited, time-boxed grant (Phase 4).
- **Deny by default:** every route declares a permission or `@Public()`, or the application does not start.
- **ABAC in the use case:** a pure `authorize(ctx, action, resource)` after loading and before returning or
  changing, so it holds for jobs and direct calls; relationships (a player's own record, a guardian's
  scoped link) are data, and no live link means deny. A denied read is a 404.
- **Confidential projections:** repositories select only permitted fields; an **independent** field
  classification — not the code's own markers — is the test oracle; confidential reads leave an access
  event.

## Alternatives rejected
- **Roles only** — cannot express "own record", "linked guardian" or "the approver of this contract".
- **Hiding fields in the UI** — the payload still carries them.
- **Testing projections against the decorators that implement them** — a removed marker would pass.

## Consequences
Every new field is classified in the fixture or the suite fails; every use case that loads a resource
calls `authorize`. The default matrix is marked OPEN until the agency confirms it (OPEN-17).

## Revisit when
Tenants need custom roles (Phase 4), or policy logic outgrows plain functions.
