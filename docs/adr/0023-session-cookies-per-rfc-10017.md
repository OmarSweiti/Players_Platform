# ADR-0023 — The session cookies follow RFC 10017

**Status:** Accepted · 3 October 2026 · **Requirements:** SR-AUTH-001…008, SR-NFR-SEC-001 · **Owners:**
`0.5.5`, `0.5.6` · **Supersedes:** the cookie names in [ADR-0003](0003-browser-sessions.md) and
[ADR-0018](0018-product-name-sadara.md)

## Context
[ADR-0003](0003-browser-sessions.md) made the API a confidential OIDC client that keeps every token
server-side and gives the browser one opaque session cookie on one origin. In August 2026 the IETF
published **RFC 10017** ("OAuth 2.0 for Browser-Based Applications", BCP 212). It strongly recommends
this backend-for-frontend design "for business applications, sensitive applications, and applications
that handle personal data" — which is what ADR-0003 already chose. Nothing is implemented yet: sessions
arrive in `0.5.5`–`0.5.6`, so adjusting now costs nothing.

The RFC's cookie rules:
- **MUST:** `Secure` and `HttpOnly`.
- **SHOULD:** `SameSite=Strict`, `Path=/`, no `Domain`, and a name prefix showing the cookie was set
  over HTTP — for example `__Host-Http-`.

The `__Host-Http-` prefix makes the browser refuse any such cookie that a script tries to set. Chrome has
supported it since version 140, and Mozilla's position is positive. A browser that does not know the
prefix still applies the `__Host-` rules, because the name begins with `__Host-`.

## Decision
1. The cookies are named **`__Host-Http-sadara_session`** and **`__Host-Http-sadara_preauth`**. All
   other attributes stay as ADR-0003 set them: `Secure`, `HttpOnly`, `Path=/`, no `Domain`.
2. **`SameSite=Lax`, deliberately**, instead of the RFC's recommended `Strict`.
   - Browsers do not send a `Strict` cookie on a cross-site navigation, so a member who follows a link
     from an email or a chat message would arrive signed out, every time.
   - `Lax` withholds the cookie from cross-site requests other than top-level navigations, and every
     state-changing request needs more than the cookie:
     - the session-bound CSRF token in `X-CSRF-Token` (ADR-0003);
     - an `Origin` that matches the configured host;
     - **`Sec-Fetch-Site` of `same-origin` when present**. This is OWASP's fetch-metadata defence, and
       this record adds it.

   GET requests never change state.
3. The `0.5.6` tests prove each layer separately: a cross-site POST carrying the cookie and a correct
   token is still refused on `Sec-Fetch-Site`, and again on `Origin`.

## Alternatives rejected
- **`SameSite=Strict`.** It is the RFC's default, but it would break every deep link from email
  notifications, a core path of the product (reminders and approvals). The compensating controls above
  are the ones the RFC and OWASP name.
- **Keeping `__Host-` alone.** That loses the browser-enforced guarantee that no script ever set the
  cookie, for nothing in return.

## Consequences
- The identifiers table in [ADR-0018](0018-product-name-sadara.md) is read with these two names.
- No session exists yet, so nothing migrates.

## Revisit when
Browsers send `Strict` cookies on top-level cross-site navigations in a way that keeps deep links
working, or the prefix's browser support changes.
