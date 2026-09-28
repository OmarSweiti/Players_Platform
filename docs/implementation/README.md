# The implementation plan

What to build next, in what order, exactly how, and how you know it worked. Start here — person or
agent.

## Frontier

<!-- plan:frontier:begin -->
**Phase 0** — 0 of 81 microsteps done (0 of 243 across all phases).
In progress: none.
Ready now (every dependency done): `0.1.1`, `0.2.1`, `0.2.2`, `0.2.4`, `0.2.5`.
Blocked: none.
<!-- plan:frontier:end -->

*Generated from [`progress.md`](progress.md) by `just plan`; the plan check fails if it is stale. The
next step is a **ready** one — every dependency done — in the current phase; when several are ready,
follow the phase file's build order. Read [`handoff.md`](handoff.md) first in case someone stopped
mid-step.*

**Long-lead work starts now**, alongside Phase 0: counsel on signature evidence and medical data, the
agency's answers on roles, approval chains and currencies, and the licence question —
[master plan](00-master-plan.md#long-lead-register).

## Read in this order

1. [`00-master-plan.md`](00-master-plan.md) — the verdict on the requirements, where the code stands,
   the phases, the effort model, the risks, the OPEN register and the errata.
2. [`01-conventions.md`](01-conventions.md) — the engineering law: fifteen invariants, architecture,
   naming, testing, the microstep definition of done, budgets, migrations.
3. [`02-development-workflow.md`](02-development-workflow.md) — bring-up, every command, the nine-station
   microstep lifecycle, rules for AI agents, manual testing, debugging.
4. [`03-github-workflow.md`](03-github-workflow.md) — branches, titles, the daily loop, pins and
   progress, releases.
5. The current phase file, and the references its microsteps link.

| Phase | File | Status |
|---|---|---|
| 0 — Foundation & hardening | [`phase-0-foundation.md`](phase-0-foundation.md) | fully specified |
| 1 — MVP | [`phase-1-mvp.md`](phase-1-mvp.md) | fully specified |
| 2 — Operations | [`phase-2-operations.md`](phase-2-operations.md) | specified; refined at phase entry |
| 3 — Intelligence | [`phase-3-intelligence.md`](phase-3-intelligence.md) | specified; refined at phase entry |
| 4 — Scale | [`phase-4-scale.md`](phase-4-scale.md) | specified; refined at phase entry |

References: [architecture](../reference/architecture.md) · [API](../reference/api.md) ·
[database](../reference/database.md) · [security and privacy](../reference/security-privacy.md) ·
[observability](../reference/observability.md) · [UI and UX](../reference/ui-ux.md) ·
[domain workflows](../reference/domain-workflows.md) · [current state](../reference/current-state.md) ·
[test catalog](../reference/test-catalog.md) · [traceability](../reference/traceability.md) ·
[what happened to the old documents](../reference/consolidation.md). Decisions: [ADRs](../adr/README.md).

## How to read a microstep

```markdown
### 0.4.5 — Row-level security on every tenant-owned table; tenant ids immutable
**Repo:** backend · **Size:** L · **Depends on:** `0.4.3`, `0.4.4` · **Requirements:** SYS-TEN-005, BR-RULE-01, SR-ACL-001
**Files:** what changes — the boundary of the work
(why, what exactly, signatures and schema — enough to implement without guessing)
**Tests:** `rls_missing_context_denies_reads_and_writes` · …
**Verify:** `just migrations && just test-int -- rls`
**Done when:** one objectively checkable sentence.
```

- **`N.N.N`** is phase · group · step. IDs are **stable identities, not build order** — never renumbered.
  A step too big to start is split with a letter suffix (0.4.5a, 0.4.5b): the children take over the
  parent's tests (each name moves to exactly one child), every step that depended on the parent is rewired
  to the child it actually needs, and the parent is marked `superseded` with its children named. A new
  step takes the next free number in its group.
- **Repo** says where the PRs go; two repositories means two PRs with the same ID, backend first.
- **Size** is a ceiling: S ≤ 4 h, M ≤ 8 h, L ≤ 16 h. Nothing larger exists; if it turns out larger, split it.
- **Depends on** is authoritative; the phase's graph and build order summarise it.
- **Requirements** are the IDs this step delivers; [traceability](../reference/traceability.md) shows every
  requirement's owners.
- **Tests** are exact names; each test's title contains its name verbatim, and the name is unique across
  the plan. They live with the feature, never in a file named after the step.
- **Verify** is runnable; **Done when** is true or false, never "mostly".

## How progress is recorded

[`progress.md`](progress.md) is the only place a status changes: `todo`, `in-progress`, `blocked`
(with what blocks it), `done` (with the merged PR) or `superseded`. A step is `done` when its PR is
merged, every dependency is done, and every named test exists — and is not skipped — at the commit the
umbrella pins; a merged PR means the application's required `test` check ran them. Statuses change in
the umbrella PR that moves the pins; `just plan` regenerates the frontier above, the test catalog and
the traceability table; `scripts/check-plan.py` fails CI when any of them disagree.

The plan is maintained, not admired: when a microstep is wrong against the code, fix the microstep
first, in its own `docs(plan)` PR.
