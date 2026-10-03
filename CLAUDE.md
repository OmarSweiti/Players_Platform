# Sadara Players Platform — read this before you touch anything

A multi-tenant platform for sports agencies — players, documents, contracts, legal, training,
performance, medical, chat, scouting, notifications and audit — in **Arabic and English**. It is built
to show and to sell: there is no client and no real data yet, and the first milestone is a sales demo
built as the real product ([ADR-0021](docs/adr/0021-a-product-built-to-sell.md)).

```
Players_Platform/     ← the umbrella: the plan (docs/), the local stack (infra/), one pinned commit of each app
├── docs/                requirements · implementation plan and progress · references · ADRs
├── backend/             submodule → Players_Platform_Backend    NestJS 12 · Prisma 7 · PostgreSQL 18
├── frontend/            submodule → Players_Platform_Frontend   Next.js 16 · React 19 · TypeScript
└── infra/               compose: PostgreSQL, Valkey, object store, ClamAV, Mailpit, Keycloak, HTTPS proxy
```

## Start here

| Read | For |
|---|---|
| [`docs/implementation/README.md`](docs/implementation/README.md) | **the frontier — what to do next** — and how to read a microstep |
| [`docs/implementation/demo-milestone.md`](docs/implementation/demo-milestone.md) | **the build order**: Sadara is built to show and to sell; the first milestone is a sales demo built as the real product ([ADR-0021](docs/adr/0021-a-product-built-to-sell.md)) |
| [`docs/implementation/handoff.md`](docs/implementation/handoff.md) | whether someone stopped mid-step |
| [`docs/implementation/01-conventions.md`](docs/implementation/01-conventions.md) | the engineering law: fifteen invariants — keep it open |
| [`docs/implementation/02-development-workflow.md`](docs/implementation/02-development-workflow.md) | every command, the nine-station microstep lifecycle, the rules for agents |
| [`docs/implementation/03-github-workflow.md`](docs/implementation/03-github-workflow.md) | branches, titles, PRs, pins and progress |
| [`docs/requirements/`](docs/requirements/README.md) | the frozen BRD, PRD, SysRD and SRS — departures are in the master plan's errata |

## The flow, in one screen

- One microstep per PR, in the repository the step names; `just branch feat/<slug>` from a fresh `development`.
- Titles: `type(scope): summary  [N.N.N]`. The PR title becomes the squash commit.
- `just pr '<title>' <body>` → `just merge <the URL it printed>`. **Never guess a PR number.**
- **Never** add coding-assistant attribution — no `Co-Authored-By:` a tool, no "Generated with" — in any
  commit, title or PR body. Hooks and CI refuse it.
- Status changes only in `docs/implementation/progress.md`, in the umbrella PR that moves the pins; then `just plan`.

## The invariants (reminders — the law is `01-conventions.md`)

1. The tenant comes from the session, job or audited platform context — never from a request; database
   work runs in `withTenantTransaction`; row-level security is forced on every tenant table.
2. Confidential by policy: select only permitted fields; tested against an independent classification.
3. Every route declares its permission or `@Public()`; object policies run inside use cases.
4. Workflow state changes only through transitions; `SIGNED` needs an approved evidence policy.
5. Audit, evidence and outbox commit with the change; audit is append-only, even against `TRUNCATE`.
6. Money is `NUMERIC(19,4)` + currency; never a JavaScript `number`.
7. Days are `DATE`; instants are `timestamptz`; schedules carry an IANA zone.
8. Arabic and English ship together; logical CSS; bidi isolation.
9. The committed OpenAPI document is the contract; RFC 9457 errors; `{ data }` once.
10. Retries are safe: idempotency keys, an at-least-once outbox, idempotent consumers.
11. Files: quarantine → scan → immutable version; downloads pinned to it.
12. Migrations move forward only; SQL-managed objects have catalog tests.
13. No secrets or personal data in logs, telemetry or errors.
14. Work is bounded; slow work is a job.
15. Done means proven: named tests exist, run and pass; nothing skipped.

## Quality gates

```bash
just check          # in each repository: what CI's required `test` check runs (the umbrella's includes the plan check)
just migrations     # backend: replay every migration on a throwaway PostgreSQL 18, no drift
just guards         # every policy checker and hook proves it still refuses
just pre-push       # the complete local gate (just pr runs it for you)
```

## Safety layers, honestly

Server rulesets refuse direct pushes, force pushes and unreviewed merges on `development`, `staging` and
`main`, with five required checks. Local hooks refuse bad titles, attribution, secrets, sensitive files
and edits to committed migrations — `--no-verify` bypasses them, which is why CI and the rulesets repeat
every rule that matters. The admin can bypass a ruleset only through a pull request, and GitHub logs it.

## Scoped rules

`.claude/rules/` loads by path: `backend.md` (backend source and tests), `migrations.md` (the Prisma
schema and migrations), `frontend.md` (the web app), and `security.md` (always). Each application's own
`AGENTS.md` routes back here.
