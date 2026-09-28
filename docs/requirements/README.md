# Requirements baseline

The four documents that say **what** Sodara must be. They are the input to the plan, not the plan:
[`../implementation/`](../implementation/README.md) says what to build, in what order, and how you know
it worked.

| File | Answers | Primary audience |
|---|---|---|
| [`01_Sodara_BRD.md`](01_Sodara_BRD.md) | the business problem, objectives, stakeholders, scope, business rules, KPIs, risks, release strategy | agency leadership, domain owners |
| [`02_Sodara_PRD.md`](02_Sodara_PRD.md) | personas, information architecture, prioritised features, journeys, UX rules, notifications, product acceptance | product, UX, engineering, QA |
| [`03_Sodara_SysRD.md`](03_Sodara_SysRD.md) | architecture, multi-tenancy, identity, data, storage, integrations, realtime, async, security, resilience, observability, environments | architecture, DevOps, security |
| [`04_Sodara_SRD_SRS.md`](04_Sodara_SRD_SRS.md) | implementation-testable requirements with stable IDs, API and database rules, NFRs, test requirements, traceability, definition of done | engineering, QA, security |

## Status and provenance

**Version 1.0 — draft baseline, 28 September 2026**, pending stakeholder validation and architecture
sign-off. Until the owner signs it off, treat it as the best current statement of intent: build to it,
and raise disagreements through change control rather than by silently diverging.

`source/` holds the owner's original `.docx` files. Each Markdown file is a faithful conversion made
on 28 September 2026 (headings, lists and tables preserved; formatting runs flattened) so people and
agents can read, search and cite it. Checksums of what is committed:

| Original | SHA-256 | Conversion | SHA-256 |
|---|---|---|---|
| `source/01_Sodara_BRD.docx` | `fc13fb89d1b29cfcd451aa78c95451d5d53f519e039657c51bac3f284e2c65f1` | `01_Sodara_BRD.md` | `64ebb2af5fb8141e7aa056ec24a9d22ba4c84cb0c5e02380c3100847579932bc` |
| `source/02_Sodara_PRD.docx` | `46b8130c4617063d63cfef0cf855ba559d365794a313d9102a7164448f3f3e24` | `02_Sodara_PRD.md` | `0f78ab597c1fb787c4a3672c8820dfaba9913fac519d57fad6edf63638e0fbd8` |
| `source/03_Sodara_SysRD.docx` | `ab3c418bf0d8fe46e7b2705a539f331239d9c0436de7cf4bb783b992868d4bd4` | `03_Sodara_SysRD.md` | `af8d654cb890b992d25e0236bed1d15451d186f62f4551fa3b6a707920c3ed47` |
| `source/04_Sodara_SRD_SRS.docx` | `a121a1d086bdecf726fdb03c72ec017b62e7819c87bbaf9e4206d1965655365f` | `04_Sodara_SRD_SRS.md` | `620c50a78dae055fb386608382b55506539fe48a2db359ed1f144a24e2b388e1` |

`python3 ../../scripts/check-plan.py` verifies these checksums, so an edit to a frozen file fails CI.

## How requirement IDs work

Each document refines the one before it, and every requirement carries a stable ID that is **never
reused**:

```
BR-OBJ-nn / BR-RULE-nn      business objectives and rules              01_Sodara_BRD.md
PRD-<AREA>-nnn, UX-nnn      product features and UX rules               02_Sodara_PRD.md
SYS-<AREA>-nnn              system and architecture requirements        03_Sodara_SysRD.md
SR-<AREA>-nnn, SR-DB-nnn,   testable software requirements              04_Sodara_SRD_SRS.md
SR-NFR-<Q>-nnn, TEST-nnn
```

The chain continues into the plan: every microstep cites the requirement IDs it satisfies, and
[`../reference/traceability.md`](../reference/traceability.md) — generated from the phase files — maps
every ID to its owning microsteps. An ID that no microstep owns fails the plan check unless it is listed
as deliberately deferred, with a reason.

## Change control

These files are **frozen**. Do not edit them to make the code look right.

1. A disagreement found while building — a requirement that is wrong, contradictory, missing or
   unbuildable — goes into the errata ledger in
   [`../implementation/00-master-plan.md`](../implementation/00-master-plan.md#errata-and-concordance),
   with the requirement ID, what the plan does instead, and why.
2. A change the owner approves produces a **new version** of the affected source document, with an
   impact assessment across all four (BRD §11 requires one once the baseline is approved). The new
   version replaces the old one here, with new checksums, in the same pull request that updates the plan.
3. Until then, the ledger entry — not the frozen text — is what the code implements.

The documents say it themselves: their standards references are baselines, **not legal advice**.
Anything that depends on jurisdiction (e-signature validity, medical-data law, retention periods,
child protection) is an OPEN item in the plan until counsel answers it.
