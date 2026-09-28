# ADR-0011 — Signature: evidence under an approved policy

**Status:** Accepted, pending counsel · 28 September 2026 · **Requirements:** BR-RULE-04, SR-CT-008,
SR-CT-011 · **Owners:** `1.4.5`, Phase 3 provider integration · **Negotiated:** both authors changed
position — Claude had allowed manual evidence to reach `SIGNED` before approval; Codex had required a
provider first

## Context
BR-RULE-04: a contract is signed only when its evidence "meets the configured signature policy".
Nobody has yet approved a policy, and the legal sufficiency of any method depends on jurisdiction.

## Decision
Evidence may be collected in Phase 1 — the signed document bound by hash to the approved version, the
signatories, the method and attestations. **The transition to `SIGNED` requires an approved evidence
policy**, configured per tenant after counsel approves it (OPEN-03); until then contracts stop at
`APPROVED`. An approved manual method may satisfy SR-CT-008; **SR-CT-011, provider integration, is
delivered in Phase 3**, and that release deferral is recorded in the errata (E-07).

## Alternatives rejected
Treating an uploaded scan as signed by default (it may not meet any policy); blocking all signature work
until a provider exists (evidence collection is useful and safe now).

## Consequences
No production contract reaches `SIGNED` without counsel's policy; the state machine checks the policy,
the approved version and the evidence hash.

## Revisit when
Counsel approves a policy, or the provider integration lands — each recorded in a new ADR that supersedes this one.
