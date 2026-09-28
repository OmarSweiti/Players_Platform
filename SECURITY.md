# Security

## Status

The Players Platform (Sodara) is in development and has no production
deployment. Nothing here claims a certification, an audit, or a compliance
standard, and nothing should — not in code, docs, UI copy, or a commit message
— until it has actually been completed.

This repository holds the platform plan and pins one commit of each
application. The code, and most of the attack surface, live in
[Players_Platform_Frontend](https://github.com/OmarSweiti/Players_Platform_Frontend)
and [Players_Platform_Backend](https://github.com/OmarSweiti/Players_Platform_Backend),
each with its own `SECURITY.md`.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting, in the repository the flaw lives in —
[platform](https://github.com/OmarSweiti/Players_Platform/security/advisories/new),
[frontend](https://github.com/OmarSweiti/Players_Platform_Frontend/security/advisories/new),
[backend](https://github.com/OmarSweiti/Players_Platform_Backend/security/advisories/new).
If you are unsure which, use the platform link.

- **Do not open a public issue**, and do not describe the flaw in a PR title.
- Include the affected version or commit and the smallest reproduction you have.
- Never paste a real credential or personal record into the report.

Expect an acknowledgement within a few working days.

## What is enforced by a machine

| Enforced | By |
|---|---|
| No secret in a commit | Gitleaks in `pre-commit`, `pre-push`, CI (`supply-chain`), and a weekly full-history scan; GitHub secret scanning + push protection |
| Every application pin is a commit the application's flow branches keep; platform `staging`/`main` pin only what the applications promoted | `scripts/check-submodules.sh`, the `test` required check |
| Changes arrive through pull requests only, on legal routes | rulesets on `development`, `staging`, `main`; the `topology` required check |
| Release tags never move or disappear | the `tags-v-append-only` ruleset, which binds the admin too |
| Workflow security | SHA-pinned actions (enforced repository-wide), read-only default token, zizmor + actionlint |

## Known gaps

| Gap | What closes it |
|---|---|
| No required approvals: a sole maintainer cannot approve their own PR | `required_approving_review_count: 1` when a second developer arrives |
| The admin can bypass the branch rulesets (through a PR only, and logged) | remove the bypass when a second maintainer exists |
