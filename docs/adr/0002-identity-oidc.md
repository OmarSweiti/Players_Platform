# ADR-0002 — Identity through an external OIDC provider

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-AUTH-001…008, SR-ACL-002, SysRD §2 ·
**Owners:** `0.1.6`, `0.5.1`–`0.5.10` · **Negotiated:** both authors; Claude first proposed repairing the
local system and conceded

## Context
SysRD §2 places an "OIDC provider (Keycloak or managed provider)" in the architecture, responsible for
authentication, MFA and the credential lifecycle; SR-AUTH-001 also permits a secure application-managed
implementation. The existing local sign-in does not work end to end and carries more than a dozen
verified defects ([`current-state.md`](../reference/current-state.md#defects-each-with-its-owner) A-1…A-22).
Repairing it would make a solo developer the owner of a security product: password storage, MFA,
recovery, lockout, breached-password checks, verification and reset flows.

## Decision
- **An external OpenID Connect provider authenticates; Sodara authorizes.** Keycloak — an exact release,
  pinned by image digest — in development and staging; the production provider (self-hosted Keycloak or
  a managed one) is chosen with hosting (`1.10.1`, OPEN-01).
- **`Identity(issuer, subject)`** is global; the tenant **`User` is the membership**, unique per
  `(tenantId, identityId)`, and keeps its id so every business foreign key survives. Email is contact
  data and never links an identity; an invitation binds a membership only with its token **and** the
  provider's verified email.
- **Privileged roles require MFA assurance** (level of assurance 2 from `acr`, with `amr` and
  `auth_time`), with step-up when it is missing; sensitive actions require authentication within five
  minutes. Roles, membership and policy stay in Sodara — never taken from provider claims.
- **The local credential system is retired, not repaired** (`0.1.6`, `0.1.7`): routes, code and
  credential columns are removed.
- Development-mode Keycloak (`start-dev`) never leaves an isolated machine; staging runs the production
  configuration with TLS and restricted administration.

## Alternatives rejected
- **Repair the application-managed sign-in** — permitted by SR-AUTH-001, but it keeps the whole credential
  lifecycle in-house and contradicts the SysRD architecture.
- **A single-page app holding provider tokens in JavaScript** — avoidable credential exposure.
- **A synthetic issuer as the only development provider** — it cannot exercise MFA, recovery, lockout or
  the Arabic sign-in pages; it remains for malformed-token tests.
- **Linking identities by email** — account takeover through a re-registered or recycled address.

## Consequences
An extra service to run (a JVM and its database) in exchange for a certified OIDC stack with MFA, WebAuthn
and passkeys (SR-AUTH-008), brute-force protection and recovery; realm configuration becomes code and is
tested (`0.5.1`). SR-AUTH-005 and SR-AUTH-006 ("if application-managed") no longer apply to Sodara's own
tables. The Keycloak login theme needs Arabic and English work (Phase 1).

## Revisit when
The production provider cannot meet the MFA, recovery, revocation or residency criteria; or a second
agency needs its own identity provider (Phase 4 federation).
