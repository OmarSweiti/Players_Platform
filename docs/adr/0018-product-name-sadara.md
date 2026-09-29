# ADR-0018 — The product is named Sadara

**Status:** Accepted · 29 September 2026 · **Decided by:** the owner · **Supersedes:** the product name,
and every identifier derived from it, in ADR-0001…0017

## Context
The requirement documents and the first version of this plan spelled the product — and the agency in
the requirement documents — "Sodara". The owner has confirmed the name is **Sadara**. Records in this
folder are immutable, so the correction is recorded here rather than edited into them.

## Decision
The product is **Sadara**, and so is the agency named in the requirement documents. Every identifier
derived from the name uses `sadara`:

| Where | Identifier |
|---|---|
| browser session and sign-in cookies | `__Host-sadara_session`, `__Host-sadara_preauth` |
| database roles and test schemas | `sadara_owner`, `sadara_migrator`, `sadara_app`, `sadara_registry`; `sadara_test_*` |
| identity provider | realm `sadara`, client `sadara-api`, theme `sadara` |
| API | the document title "Sadara API"; problem types `urn:sadara:problem:*` |
| development | tenant `sadara` on `https://sadara.localhost`; addresses on `sadara.test` |
| packages | `sadara-backend`, `sadara-frontend` |

Read "Sodara" and `sodara` in ADR-0002, ADR-0003 and ADR-0004 as "Sadara" and `sadara`. The
requirement documents were re-issued with the corrected name and no other change (their checksums are in
[`../requirements/README.md`](../requirements/README.md)). The repository names — `Players_Platform`,
`Players_Platform_Backend`, `Players_Platform_Frontend` — are unchanged.

## Consequences
Nothing that runs used the old identifiers: Phase 0 creates the cookies, roles, realm and packages, and
creates them with the new name. Git history keeps the old spelling.

## Revisit when
The repositories themselves are renamed, which would change their URLs, submodule paths and every clone.
