# ADR-0027 — A member's own session is `@SignedIn()`

**Status:** Accepted · 7 November 2026 · **Requirements:** SR-AUTH-009, SR-API-001 · **Owners:** `0.6.2` ·
**Supersedes:** the route declarations of [ADR-0005](0005-authorization.md)'s "deny by default"

## Context
[ADR-0005](0005-authorization.md) decided deny by default: "every route declares a permission or
`@Public()`, or the application does not start". Building it (`0.6.2`) showed a third kind of route that
the rule did not name. Six routes act only on the caller's own session:
- re-authenticating (step-up);
- reading one's session (`GET /auth/session`);
- signing out, and signing out everywhere;
- listing one's own sessions, and ending one of them.

Every signed-in member needs them, whatever their role, and they read or change no one else's data.

Under ADR-0005's wording each would need a catalog permission granted to every tenant role. That has two
costs:
- **Leaving depends on a permission.** A member could sign out only while their role held it. Per-tenant
  roles (`4.1.4`) would then need a rule that this permission can never be removed.
- **A permission that is not one.** It authorizes nothing, yet it would sit in the catalog, in the
  effective permissions the web app reads (`0.6.6`), and in every custom role.

## Decision
1. **Every route declares exactly one access rule, or the API does not start:**
   - **`@RequirePermission(key)`:** a catalog permission the member's role must hold;
   - **`@SignedIn()`:** any signed-in member, acting only on their own session;
   - **`@Public()`:** anyone, with no session.

   A route that declares none, or more than one (on its handler, its controller, or both), stops the
   API at boot and is named in the log.
2. **`@SignedIn()` is for the caller's own session only.** A route that reads or changes any other
   member's data, or any tenant data, requires a permission.
3. **The session guard decides `@SignedIn()`**, as it does for every route that is not `@Public()`.
   The permission guard lets it through without asking for a permission, and fails closed on a route
   that declares no single rule, even though the boot check makes one impossible.

The maintainer chose this over a permission held by every role, on 7 November 2026, during `0.6.2`.

## Alternatives rejected
- **A catalog permission for one's own session, granted to every tenant role.** It follows ADR-0005's
  wording, but signing out would depend on a role's grants (above).
- **`@Public()` with a session check inside the handler.** Public routes skip the session guard and the
  CSRF check, so signing out would lose its CSRF protection, and the session check would be done by hand.

## Consequences
- Invariant I-3 in `01-conventions.md` and the backend rules name all three declarations.
- `0.6.2`'s tests prove each kind:
  - every route declares exactly one;
  - an undeclared or doubly declared route stops the boot;
  - each permission route refuses a member whose role lacks its permission;
  - each `@SignedIn()` route refuses an anonymous caller (`401`) and serves the member with the fewest
    permissions.
- The isolation suite (`0.6.9`) reads the same declarations.

## Revisit when
Per-tenant roles (`4.1.4`) or platform operators (`4.1.1`) need routes of their own. A platform session
is not a tenant member's, and a platform operator's own-session routes may need a declaration of their own.
