# Requirements baseline

The four documents that say **what** Sadara must be. They are the input to the plan, not the plan:
[`../implementation/`](../implementation/README.md) says what to build, in what order, and how you know
it worked.

| File | Answers | Primary audience |
|---|---|---|
| [`01_Sadara_BRD.md`](01_Sadara_BRD.md) | the business problem, objectives, stakeholders, scope, business rules, KPIs, risks, release strategy | agency leadership, domain owners |
| [`02_Sadara_PRD.md`](02_Sadara_PRD.md) | personas, information architecture, prioritised features, journeys, UX rules, notifications, product acceptance | product, UX, engineering, QA |
| [`03_Sadara_SysRD.md`](03_Sadara_SysRD.md) | architecture, multi-tenancy, identity, data, storage, integrations, realtime, async, security, resilience, observability, environments | architecture, DevOps, security |
| [`04_Sadara_SRD_SRS.md`](04_Sadara_SRD_SRS.md) | implementation-testable requirements with stable IDs, API and database rules, NFRs, test requirements, traceability, definition of done | engineering, QA, security |

## Status and provenance

**Version 1.0 — draft baseline, 28 September 2026**, pending stakeholder validation and architecture
sign-off. **Revision 1, 29 September 2026:** the product and agency name corrected from "Sodara" to
**Sadara** by the owner, in the `.docx` originals and their conversions alike — no other change (a
re-conversion of the corrected originals is identical to the previous text with only the name replaced). Until the owner signs it off, treat it as the best current statement of intent: build to it,
and raise disagreements through change control rather than by silently diverging.

`source/` holds the owner's original `.docx` files. Each Markdown file is a faithful conversion made
on 28 September 2026 (headings, lists and tables preserved; formatting runs flattened) so people and
agents can read, search and cite it. Checksums of what is committed:

| Original | SHA-256 | Conversion | SHA-256 |
|---|---|---|---|
| `source/01_Sadara_BRD.docx` | `288a60b65941ebc9b8d720cedb7d759dca04e9799423893efb5e6e6d033ff94e` | `01_Sadara_BRD.md` | `58856e83b1f083f378f8dd926da78d53b57925b64a035df246453d37bed621e9` |
| `source/02_Sadara_PRD.docx` | `2dba1e9b64f337d2bfba22263bfde35a3588ae73eb709b89f5b3f9841ec8412b` | `02_Sadara_PRD.md` | `21c56fbf5020b9d54edc4d38a62ee5f10bec9042773c9c8b22d27d99dc2d8292` |
| `source/03_Sadara_SysRD.docx` | `21451fd87a0d69a976d90514d7aab510460e673b405c0c5c3a8ae440c58a496c` | `03_Sadara_SysRD.md` | `a18d895e6ec971af022646b86aa20f732ca8585c77044c8f8c426376db10db77` |
| `source/04_Sadara_SRD_SRS.docx` | `10267642c61c5fe7b8476b68ecea65abf9ec18063206d4f6024958d82e8ac70a` | `04_Sadara_SRD_SRS.md` | `f5464b1a82c5a6c77b7f02daeb07f6c59dcc72b08eb29838225d905f82a71aac` |

`python3 ../../scripts/check-plan.py` verifies these checksums, so an edit to a frozen file fails CI.

## How requirement IDs work

Each document refines the one before it, and every requirement carries a stable ID that is **never
reused**:

```
BR-OBJ-nn / BR-RULE-nn      business objectives and rules              01_Sadara_BRD.md
PRD-<AREA>-nnn, UX-nnn      product features and UX rules               02_Sadara_PRD.md
SYS-<AREA>-nnn              system and architecture requirements        03_Sadara_SysRD.md
SR-<AREA>-nnn, SR-DB-nnn,   testable software requirements              04_Sadara_SRD_SRS.md
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
