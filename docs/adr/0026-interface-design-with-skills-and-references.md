# ADR-0026 — The interface speaks football's visual language, designed with named skills and references used for inspiration

**Status:** Accepted · 3 November 2026 · **Requirements:** UX-010, UX-011, UX-012, SR-NFR-A11Y-001 ·
**Owners:** `0.9.6` and every step that changes the web app · **Relates to:**
[ADR-0008](0008-i18n.md), [ADR-0021](0021-a-product-built-to-sell.md), [ADR-0025](0025-the-web-app-data-path.md)

## Context
Sadara is a football platform: the system a football (soccer) agency runs its players' careers on. It is built
to sell, and its first milestone is a sales demo built as the real product
([ADR-0021](0021-a-product-built-to-sell.md)). Prospective agencies judge it first by its interface, and
each agency sees it in its own branding (`1.1.2`).

The [interface contract](../reference/ui-ux.md) fixes how the interface behaves: its states, Arabic and
English, accessibility and data safety. `0.9.6` adopts shadcn/ui in right-to-left mode and a token
system. Nothing yet says how the interface should look, or how that is achieved and checked.

Coding agents, left to themselves, converge on the same generic interface. In November 2026, design
skills give an agent:
- a design vocabulary;
- an art direction;
- a reviewer that ranks problems;
- a deterministic detector of the generic tells.

Component galleries and design-system registries offer patterns to learn from. On 3 November 2026 the
maintainer asked two things:
- every piece of UI work uses a named set of these skills and references;
- the interface is tuned to football, the concept of the product, and draws its inspiration from it.

## Decision
1. **One visual reference, and its language is football's.** [`visual-design.md`](../reference/visual-design.md)
   takes its motifs, its ways of showing information and its moments from the game (association
   football, or soccer): the pitch, the line-up card, match day. The whole product is sporty: work
   screens energetic and exact, moments full match day. The reference also states the principles,
   where expression is allowed and where it is not, and the skills and references with their
   guardrails. [`ui-ux.md`](../reference/ui-ux.md) remains the behavioural contract and prevails
   in any conflict.
2. **The design skills are part of delivery.** Each machine installs them at the versions the reference
   records:
   - impeccable;
   - design-taste-frontend (taste-skill);
   - shadcn/ui's own skill;
   - Playwright CLI;
   - img2threejs.

   Every step that changes the web app runs the reference's design pass (shape, build, look, review)
   before it posts its evidence.
3. **References inspire; they are not copied.** uiverse, shadcn/ui's blocks and charts, three.js,
   particles.js, Refero Styles, the awesome-design-skills registry, and football's own products and
   broadcasts are studied for patterns and vocabulary. No brand's identity is reproduced, and no club's,
   league's or video game's. Code adapted from an MIT or Apache-2.0 source keeps its
   notice, and is rewritten to the tokens, logical CSS, right-to-left and accessibility rules.
4. **No dependency enters through a reference.**
   - three.js is the only 3D runtime. It is added by the first step that needs it, under the dependency
     policy, and loaded only where it is used.
   - A particle effect uses tsParticles or three.js. particles.js has had no release since 2015.
   - Nothing loads from a CDN at run time.
5. **Expression has a place.** Workspaces stay quiet: directories, contracts, legal, medical, documents
   and settings. Art direction, imagery, 3D and particles belong to the moments the reference names.

## Alternatives rejected
- **Design by habit, without skills or references.** It produces the generic interface the demo cannot
  afford.
- **Adopting a ready-made design system from a registry.** It conflicts with per-agency branding,
  right-to-left layout and the token system of `0.9.6`. The registries are read for vocabulary instead.
- **Vendoring the skills into the repositories.** Every update would be third-party code reviewed into
  each repository. A per-machine install at a recorded version gives the same reproducibility for one
  maintainer. Revisit when a second engineer joins: impeccable supports a pinned submodule.

## Consequences
- A UI step's evidence includes its design review (critique and audit, no P0 or P1 left) beside the
  screenshots in Arabic and English.
- Setting up a machine gains one step. Updating a skill is a reviewed change to the recorded versions,
  under the seven-day cooldown.
- The tools run locally, with the developer's permissions. The reference states their guardrails: no
  bypassed sandboxes, no real person's likeness, no product code or tenant data sent to a third-party
  service.
- The brand remains the owner's decision: the logo, the brand colour, and any typeface beyond the two
  licensed families (`0.9.2`).
