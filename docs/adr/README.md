# Architecture decision records

One file per load-bearing decision: context, decision, alternatives rejected, consequences, and when to
revisit. Several were **negotiated** between the plan's two authors; each records who proposed what and
why the outcome won.

**Records are immutable once committed** — the umbrella's `protected-paths` check refuses an edit to
anything under `docs/adr/`. A decision changes through a **new** ADR, numbered next, that says which
record it supersedes; a proposal becomes a decision the same way. The history of *why* is the point.

The list of decisions and their current status is kept in [`../README.md`](../README.md#decisions),
which — unlike this folder — is updated whenever a record is added or superseded.
