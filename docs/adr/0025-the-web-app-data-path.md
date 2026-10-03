# ADR-0025 — The web app reads on the server, writes through the API, and caches nothing tenant-scoped

**Status:** Accepted · 3 October 2026 · **Requirements:** SR-CORE-001, SR-NFR-SEC-002, UX-009,
TEST-009 · **Owners:** `0.9.4`, `0.9.5`, `0.9.6`, `0.2.10` · **Relates to:**
[ADR-0003](0003-browser-sessions.md), [ADR-0008](0008-i18n.md), [ADR-0010](0010-api-contract.md)

## Context
The NestJS API owns the domain, authorization and the session ([ADR-0003](0003-browser-sessions.md));
the Next.js app is its client. Next 16's data-security guide offers three approaches and asks a project
to pick one. One of them is calling a separate HTTP API under a zero-trust model. The architecture audit
of 3 October 2026 found that today's app does none of this:
- it is rendered entirely in the browser, and every route is prerendered as a static page;
- the server never checks the session;
- a hand-written client calls the API on another origin.

Two Next.js security releases in September 2026 included cache leaks across route parameters.

## Decision
1. **Reads happen on the server first.**
   - Pages are Server Components by default.
   - A server-only API layer in `src/server/api/` (guarded by `import 'server-only'`) calls the API with
     the generated `openapi-fetch` client (`0.9.4`). It forwards the session cookie and uses
     `cache: 'no-store'`.
   - It returns the API's DTOs unchanged.
   - It holds no authorization logic: the API decides.
   - `'use client'` goes only on interactive leaves.
2. **TanStack Query only where a screen is interactive** (filters that refetch, polling, optimistic
   updates). Such data is prefetched on the server and handed over with `HydrationBoundary`. Query keys
   include the tenant and the projection (ADR-0003).
3. **One write path.** The browser writes to `/api/v1` on the same origin through the generated client,
   with the CSRF token ([ADR-0023](0023-session-cookies-per-rfc-10017.md)). There are no Server Actions
   for business writes: they would add a second path into the system that would need securing as well.
4. **Nothing tenant-scoped is cached by Next.** No `use cache`, no shared fetch cache and no static
   rendering of authenticated routes.
5. **Feature folders, not Feature-Sliced Design.** The layout is `app/[locale]/…` routes,
   `src/features/<feature>/{components,server,hooks,schemas}`, `src/shared/ui` and `src/server`. A
   feature is imported only through its `index.ts`, which `0.2.10` enforces.
6. **The component system is shadcn/ui, installed through its CLI in right-to-left mode** (`rtl: true`
   writes logical classes) on its default primitives. It is themed by the design tokens of `0.9.6`, and
   today's hand-copied primitives are regenerated.

## Alternatives rejected
- **A browser-only app calling the API** (today's design). The server never sees the session, nothing
  renders before JavaScript arrives, and every page is a static shell.
- **Server Actions as a second backend.** They would put business logic in Next and add a second path to
  authorize and audit.
- **Next as a full backend-for-frontend** (Route Handlers proxying every call). The reverse proxy already
  routes `/api` to Nest on the same origin, and Next's guide advises against calling one's own Route
  Handlers from Server Components.
- **Feature-Sliced Design.** It's more structure than one product team needs, and with Next it requires
  renaming its layers.

## Consequences
- Pages render with data on the first response, in the right language and direction.
- The browser never holds a token.
- Every write is authorized, audited and idempotent in exactly one place: the API.

## Revisit when
The product gains a client that cannot use the API's session, or Next.js changes its server/client model
enough to need a new pattern.
