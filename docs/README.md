# Sadara documentation

Everything needed to build the Sadara player-management platform: what it must do, the plan to build
it, the rules every change follows, and where the work stands. People and AI agents use the same set.

| Folder | Holds | Start with |
|---|---|---|
| [`requirements/`](requirements/README.md) | the owner's four frozen requirement documents (BRD, PRD, SysRD, SRS) — **what** Sadara must be | the README, then the BRD |
| [`implementation/`](implementation/README.md) | the plan — master plan, engineering law, workflows, one file per phase, progress and handoff — **what to build next and how to prove it** | the README: it shows the live frontier |
| [`reference/`](reference/) | the contracts every microstep relies on: architecture, API, database, security, observability, UI, domain workflows, the verified current state, the test catalog and requirement traceability | whichever the microstep names |
| [`adr/`](adr/README.md) | architecture decisions: context, decision, alternatives rejected, consequences, when to revisit | the index |

**Where to begin.** New to the project: [`implementation/README.md`](implementation/README.md), then
[`implementation/00-master-plan.md`](implementation/00-master-plan.md). About to change code: the
microstep, [`implementation/01-conventions.md`](implementation/01-conventions.md) and
[`implementation/02-development-workflow.md`](implementation/02-development-workflow.md). An AI agent:
[`../AGENTS.md`](../AGENTS.md) first.

**One authority per subject.** If two documents disagree, the more specific one wins — a microstep over
a reference, a reference over the master plan — and the disagreement is a bug to fix in the same pull
request. The code is the fact: when a document and the code disagree about what exists, fix the
document. `python3 scripts/check-plan.py` keeps the plan, the progress record, the requirement
traceability and every link consistent, and runs in CI.

## Decisions

The architecture decision records in [`adr/`](adr/README.md), with their current status. Records are
immutable; a change of decision is a new record that supersedes an old one, and this table is updated in
the same pull request.

| ADR | Decision | Status |
|---|---|---|
| [0001](adr/0001-modular-monolith.md) | A modular monolith in three processes | Accepted |
| [0002](adr/0002-identity-oidc.md) | Identity through an external OIDC provider; the local credential system retired | Accepted · name superseded by 0018 |
| [0003](adr/0003-browser-sessions.md) | Browser sessions owned by the API, on one origin | Accepted · name superseded by 0018 |
| [0004](adr/0004-tenancy-defense-in-depth.md) | Tenancy in depth, enforced by the database | Accepted · name superseded by 0018 |
| [0005](adr/0005-authorization.md) | A permission catalog, object policies, confidential projections | Accepted |
| [0006](adr/0006-money.md) | Money as NUMERIC(19,4) with currency rules | Accepted |
| [0007](adr/0007-time.md) | Calendar dates and instants | Accepted |
| [0008](adr/0008-i18n.md) | Arabic and English, equal, from the first screen | Accepted |
| [0009](adr/0009-object-storage.md) | Private objects: quarantine, scan, immutable versions | Accepted |
| [0010](adr/0010-api-contract.md) | Versioned REST, problem details, one envelope | Accepted |
| [0011](adr/0011-e-signature-evidence-policy.md) | Signature evidence under an approved policy | Accepted · approval authority superseded by 0019 |
| [0012](adr/0012-hosting.md) | Hosting | Proposed — decided at `1.10.1` |
| [0013](adr/0013-postgresql-18.md) | PostgreSQL 18 from Phase 0 | Accepted |
| [0014](adr/0014-async-outbox.md) | Side effects through a transactional outbox | Accepted |
| [0015](adr/0015-documentation-as-plan.md) | The documentation is the plan of record | Accepted |
| [0016](adr/0016-observability.md) | Observability | Accepted |
| [0017](adr/0017-sql-managed-database-objects.md) | Partial indexes, checks, policies, triggers and grants live in SQL | Accepted |
| [0018](adr/0018-product-name-sadara.md) | The product is named Sadara | Accepted |
| [0019](adr/0019-owner-approves-signature-policy.md) | The owner approves the signature evidence policy | Accepted · default policy awaits the owner's approval |
| [0020](adr/0020-local-object-store.md) | The local object store is Versity S3 Gateway | Accepted |
