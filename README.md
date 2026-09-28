# Sodara — Players Platform

The player-management platform for Sodara Sports Agency: player records, contracts and approvals,
legal tickets, documents and media, training, performance, medical, communication and scouting — for
one agency first, built multi-tenant from the start, in Arabic and English.

This repository is the **umbrella**: the plan, and one pinned commit of each application.

| Path | What it is |
|---|---|
| [`docs/`](docs/README.md) | requirements, the implementation plan and its progress, references, decisions |
| `backend/` | submodule → [Players_Platform_Backend](https://github.com/OmarSweiti/Players_Platform_Backend) — NestJS API, worker and realtime processes; Prisma; PostgreSQL |
| `frontend/` | submodule → [Players_Platform_Frontend](https://github.com/OmarSweiti/Players_Platform_Frontend) — Next.js web app |
| `scripts/`, `justfile`, `.github/` | the delivery flow: hooks, guards, CI, rulesets |

**Where the work stands:** the live frontier at the top of
[`docs/implementation/README.md`](docs/implementation/README.md).

```bash
git clone --recurse-submodules git@github.com:OmarSweiti/Players_Platform.git
cd Players_Platform && just setup-all      # then: docs/implementation/02-development-workflow.md
```

How changes ship: [`CONTRIBUTING.md`](CONTRIBUTING.md). Reporting a vulnerability:
[`SECURITY.md`](SECURITY.md).
