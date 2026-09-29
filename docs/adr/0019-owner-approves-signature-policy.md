# ADR-0019 — The owner approves the signature evidence policy

**Status:** Accepted · 29 September 2026 · **Decided by:** the owner · **Supersedes:** the approval
authority in [ADR-0011](0011-e-signature-evidence-policy.md) ("configured per tenant after counsel
approves it") · **Requirements:** BR-RULE-04, SR-CT-008 · **Owner step:** `1.4.5`

## Context
BR-RULE-04 says a contract is signed only when its evidence "meets the configured signature policy".
ADR-0011 kept that rule and named counsel as the approver of the policy. The owner has decided that the
business approves it: a lawyer's review is advice the owner may seek, not a gate in the system.

## Decision
- **The tenant's owner approves the evidence policy.** In the product it is an audited setting, changed
  only by an `OWNER` with recent authentication (`1.4.5`); before the product exists, an approval recorded
  in this plan counts. Until a policy is approved, contracts stop at `APPROVED`, exactly as before.
- **The rule that matters is unchanged:** `SIGNED` requires evidence that satisfies the approved policy
  for the exact approved version — never a timestamp, a checkbox or an unreviewed upload.
- **Default policy, offered for the owner's approval** — the "manual evidence" policy:
  1. *The document:* the final contract as a PDF signed by every required signatory — a scan of wet-ink
     signatures, or the signed PDF exported from an e-signature service — uploaded through the private
     file pipeline, so it is scanned and stored as an immutable version with its SHA-256.
  2. *The right version:* its hash is bound to the approved contract version; any change to the text is a
     new version with new approvals.
  3. *The signatories:* the player — and a parent or guardian when the player is under 18 — the
     counterparty's authorised representative, and the agency's authorised signatory, each recorded by
     name and role.
  4. *Attestation:* the member who records the evidence attests that the signatures are genuine and
     complete (recent authentication; audited).
  5. *Four eyes:* a second member with the legal role confirms the evidence before the contract becomes
     `SIGNED`.
  6. *Retention:* signed evidence is kept at least for the life of the contract plus the retention
     period the owner sets (OPEN-06), and is never deleted while the contract is active.

## Alternatives rejected
- **A lawyer's approval as a system gate** (ADR-0011's wording) — the owner's choice.
- **Treating any upload as signed** — BR-RULE-04 requires a policy, and the risk of a wrong "signed" status
  is a contract nobody can enforce.

## Consequences
The legal risk of the chosen method rests with the owner's decision. The plan still recommends a lawyer's
look at three cases the default does not settle: cross-border transfers (another country's formalities),
contracts with minors (guardian consent and FIFA's rules on minors), and unusually high-value deals.
Provider integration (SR-CT-011) remains Phase 3.

## Revisit when
The owner approves or changes the policy (recorded by a new ADR or the product's audited setting), or the
Phase 3 e-signature provider is chosen.
