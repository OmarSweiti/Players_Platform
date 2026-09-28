# ADR-0015 — The documentation is the plan of record

**Status:** Accepted · 28 September 2026 · **Owners:** `0.1.1`–`0.1.3` · **Negotiated:** Codex first
proposed JSON manifests (`progress.json`, `trace-map.json`), a step runner and per-application lock files,
and conceded; its evidence rule was adopted

## Context
Twenty-five legacy documents contradicted each other and the code, and claimed completion for work that
did not run. Plans rot when status lives apart from proof.

## Decision
The phase files are the single source of the plan: microsteps with stable IDs, sizes, dependencies,
requirement owners, exact test names, a runnable Verify and a checkable Done-when. `progress.md` is the
only place a status changes. `scripts/check-plan.py`, in CI, validates the graph, the progress record, the
requirement traceability, the frozen requirement checksums, every link and cited step, and — for a `done`
step — that every named test exists and is not skipped at the commit the umbrella pins. The frontier, the
test catalog and the traceability table are generated. Tests live with their features, never in files
named after plan steps. Legacy documents are deleted after their content is merged; git history keeps them.

## Alternatives rejected
JSON manifests duplicating the prose (they drift); a per-step test runner and cross-repository lock files
(a failure mode on every application PR for a solo developer); keeping the legacy guides "for reference"
(agents obey whatever they find).

## Consequences
A PR that changes the plan regenerates its derived blocks (`just plan`); a merged application PR means its
required tests ran; the plan check is part of the umbrella's required `test` job.

## Revisit when
More than one team works the plan concurrently.
