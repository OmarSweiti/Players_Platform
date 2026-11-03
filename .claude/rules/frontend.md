---
paths:
  - "frontend/**"
---

# Frontend rules

**Read `frontend/AGENTS.md` first: this Next.js version has breaking changes from your training data.
Read the relevant guide in `frontend/node_modules/next/dist/docs/` before writing Next.js code.**
The UI contract is `docs/reference/ui-ux.md`; how it looks is `docs/reference/visual-design.md` (ADR-0026).

- **Routes** live under `app/[locale]/…`, named by noun (`/players`, `/contracts`) — no `/dashboard`
  prefix; `typedRoutes` is on; every segment has loading, error and not-found states.
- **Language.** No user-facing literal in code: every string is a key in both `messages/ar.json` and
  `messages/en.json`, with ICU plurals. Logical CSS only (`ms-`, `pe-`, `start-`, `text-start`) — lint
  refuses physical directions. Identifiers, emails and mixed-script numbers go inside the bidi-isolating
  component.
- **Data** (ADR-0025). Read on the server through the server-only layer `src/server/api/`; call the API
  only through the client generated from the committed OpenAPI contract, on the same origin (`/api/v1`,
  served by the local HTTPS proxy in development). Writes go only through the API — never a Server
  Action. Never send a tenant header; never read or store a session secret in JavaScript or web storage;
  attach the CSRF token to writes. TanStack Query only on interactive screens, prefetched on the server;
  its keys include the tenant and the projection; logout and tenant change clear the cache. Nothing
  tenant-scoped is cached by Next (`use cache`, fetch caching, static rendering).
- **Authorization is the API's.** Navigation built from effective permissions is display only; never
  hide a field instead of the API omitting it.
- **Forms:** React Hook Form with zod for feedback; the server still validates. Money is a decimal
  string with its currency; dates are `YYYY-MM-DD` or an instant with its zone.
- **Design.** Sadara is a football (soccer) platform, and the interface is sporty all through. Its
  visual language is football's ("The football in it": the pitch, the line-up card, match day), with
  work screens energetic but exact. Every UI change
  runs the design pass in `docs/reference/visual-design.md`: shape with
  impeccable; build on shadcn/ui and the tokens through its skill; look with Playwright CLI at 360/768/1440
  in `ar` and `en`, light and dark; review with impeccable `critique` and `audit` and its detector, and
  fix every P0 and P1 before the evidence. Workspaces stay quiet; art direction (design-taste-frontend),
  3D (three.js, img2threejs) and particles only in the moments the reference names. References inspire and
  are never copied: an adapted snippet is rewritten to the tokens, logical CSS and accessibility rules and
  keeps its licence notice, and no dependency, CDN or real person's likeness enters through one.
- **Tests:** Vitest and Testing Library beside the code as `src/**/*.test.{ts,tsx}`; Playwright journeys
  as `tests/**/*.spec.ts`, run in the `ar` and `en` projects with axe. The title contains the plan's test name verbatim.
- Gate: `just check` — it builds, then runs the unit tests and the journeys; `just test` runs the unit tests alone.
