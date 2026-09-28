---
paths:
  - "frontend/**"
---

# Frontend rules

**Read `frontend/AGENTS.md` first: this Next.js version has breaking changes from your training data.
Read the relevant guide in `frontend/node_modules/next/dist/docs/` before writing Next.js code.**
The UI contract is `docs/reference/ui-ux.md`.

- **Routes** live under `app/[locale]/…`, named by noun (`/players`, `/contracts`) — no `/dashboard`
  prefix; `typedRoutes` is on; every segment has loading, error and not-found states.
- **Language.** No user-facing literal in code: every string is a key in both `messages/ar.json` and
  `messages/en.json`, with ICU plurals. Logical CSS only (`ms-`, `pe-`, `start-`, `text-start`) — lint
  refuses physical directions. Identifiers, emails and mixed-script numbers go inside the bidi-isolating
  component.
- **Data.** Call the API only through the client generated from the committed OpenAPI contract, on the
  same origin (`/api/v1`, served by the local HTTPS proxy in development). Never send a tenant header; never read or store a session secret in
  JavaScript or web storage; attach the CSRF token to writes. TanStack Query keys include the tenant and
  the projection; logout and tenant change clear the cache.
- **Authorization is the API's.** Navigation built from effective permissions is display only; never
  hide a field instead of the API omitting it.
- **Forms:** React Hook Form with zod for feedback; the server still validates. Money is a decimal
  string with its currency; dates are `YYYY-MM-DD` or an instant with its zone.
- **Tests:** Vitest and Testing Library beside the code as `src/**/*.test.{ts,tsx}`; Playwright journeys
  as `tests/**/*.spec.ts`, run in the `ar` and `en` projects with axe. The title contains the plan's test name verbatim.
- Gate: `just check`, and `npx playwright test` for journeys you touched.
