# Agent guide — Sadara Players Platform

You are working on a multi-tenant, bilingual (Arabic and English) platform for sports agencies, built to
show and to sell; there is no client yet (`docs/adr/0021-a-product-built-to-sell.md`). This
repository is the **umbrella**: the plan in `docs/`, the local stack in `infra/`, and one pinned commit
of the backend and the frontend as submodules.

**Before any change**, read in this order:

1. `docs/implementation/README.md` — the frontier: the next ready microstep.
2. `docs/implementation/demo-milestone.md` — the build order: the first sales demo, built as the real product.
3. `docs/implementation/handoff.md` — work someone left in flight.
4. The microstep itself, and every file, requirement and reference it names.
5. `docs/implementation/01-conventions.md` — the fifteen invariants.
6. `docs/implementation/02-development-workflow.md` — commands, the microstep lifecycle, the agent rules.
7. The rules for the area you touch:

| You change | Also read |
|---|---|
| `backend/src/**`, `backend/test/**` | `.claude/rules/backend.md` |
| `backend/prisma/**` | `.claude/rules/migrations.md`, `docs/reference/database.md` |
| `frontend/**` | `.claude/rules/frontend.md`, then `frontend/AGENTS.md` — this Next.js differs from your training data |
| anything | `.claude/rules/security.md` |

**Non-negotiable:** one microstep per PR; titles `type(scope): summary  [N.N.N]`; never guess a PR
number (use the URL `just pr` prints); never weaken a gate (no skipped tests, no `--no-verify`, no edited
migration); never mark a step done without its named tests passing in CI; never invent requirements,
legal or medical facts, or test results — a missing answer is an OPEN item; never use real personal
data; never add coding-assistant attribution to a commit, title or PR body.

When the plan and the code disagree about what exists, the code is the fact: fix the plan first, in a
`docs(plan)` PR.
