# ADR-0003 — Browser sessions owned by the API, on one origin

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-AUTH-003, SR-AUTH-007, SR-ACL-007 ·
**Owners:** `0.5.5`–`0.5.7`, `0.9.4`, `0.9.5` · **Negotiated:** Codex first proposed a Next.js BFF with an
encrypted token vault and signed one-use session assertions, and conceded; the synthesis added
database-checked sessions and a stated exposure window

## Context
With identity at an external provider (ADR-0002), something must turn a provider sign-in into a browser
session. The browser must never hold a credential readable by JavaScript, revocation must be real, and
cross-site request forgery must be impossible.

## Decision
- **The API is the confidential OIDC client** — authorization code with PKCE, `state` and `nonce`. On the
  callback it verifies the ID token, finds the membership, and creates a `UserSession`.
- **Sign-in is bound to the browser that started it** by a short-lived `__Host-sodara_preauth` cookie,
  so a callback completed elsewhere creates nothing (login CSRF).
- **One opaque cookie**: `__Host-sodara_session` — 256 random bits, HttpOnly, Secure, SameSite=Lax,
  Path=/. PostgreSQL stores only its hash, the provider's `sid`, and the `acr`, `amr` and `auth_time` it
  asserted. **No provider token is stored**: Sodara needs the identity, never to call the provider as
  the user.
- **One origin.** The web app and the API share it by path routing (`/` → Next.js, `/api/` → Nest): a
  local HTTPS proxy in development (so the `__Host-` cookie is tested as specified), the same path routing
  in every hosted environment. No cookie is ever cross-site.
- **CSRF:** a synchronizer token bound to the session — derived as an HMAC of the session-token digest, so
  nothing is stored and every tab gets the same value — sent as `X-CSRF-Token`, **plus** an `Origin` check
  on every write; non-JSON bodies are refused.
- **Every request checks the session, the membership and the tenant in PostgreSQL** — so logout,
  revocation and deactivation take effect on the next request. A cache may come later only with a tested
  consistency protocol; a failed cache invalidation must never keep a revoked session alive.
- **Lifetimes:** idle 30 minutes, absolute 12 hours (provisional, OPEN-02).
- **The exposure window, stated:** app-side revocation is immediate; a provider-side change (an account
  disabled at the provider, a reset) reaches Sodara through a validated back-channel logout, or — if that
  event is lost — at the session's idle or absolute expiry. Offboarding is therefore done in Sodara. The
  owner accepts the window (OPEN-02).

## Alternatives rejected
- **A Next.js BFF holding encrypted provider tokens and minting signed one-use assertions for the API** —
  solves problems this topology does not have, at the price of a token vault, refresh leases and a replay
  store.
- **Tokens in `localStorage`** — readable by any injected script.
- **Checking sessions only in Valkey** — a commit followed by a failed invalidation leaves access alive.
- **`SameSite=None` cookies across origins** — the defect found in the current code (A-20).

## Consequences
One session table, read on every request (indexed by token hash; measured under the capacity envelope);
the same-origin rule constrains hosting (a path-routing proxy is required). Server-rendered pages forward
the cookie to the API server-side.

## Revisit when
Session lookups show up in the latency budget, or a non-browser client needs access (it would receive its
own scoped credentials, never the browser session).
