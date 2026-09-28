# Contributing

The Players Platform (Sodara): the plan, and one pinned commit of each
application.

| Path | What it is |
|---|---|
| `frontend/` | submodule → [Players_Platform_Frontend](https://github.com/OmarSweiti/Players_Platform_Frontend) (Next.js) |
| `backend/` | submodule → [Players_Platform_Backend](https://github.com/OmarSweiti/Players_Platform_Backend) (NestJS, Prisma, PostgreSQL) |
| `IMPLEMENTATION_CHECKLIST.md` and the other guides | the plan: what to build, and in what order |

Each of the three repositories has the same flow, the same gates, and its own
`just` recipes. Application code changes in the application's repository,
never through this one.

## Once per clone

```bash
git clone --recurse-submodules git@github.com:OmarSweiti/Players_Platform.git
cd Players_Platform
just setup-all   # this repository, then `just setup` inside frontend/ and backend/
just guards      # every guard proves it still refuses what it must
```

Needs `git`, `gh` (authenticated), `just`, `jq`, `gitleaks` ≥ 8.19, and Node
from each application's `.nvmrc`.

## The flow

```text
feat/<slug> ──squash──► development ──merge commit──► staging ──merge commit──► main
                         (default)                     (candidate: vX.Y.Z-rc.N)  (release: vX.Y.Z)
```

```bash
just branch docs/phase-one-exit
git commit -m "docs(plan): record the phase one exit criteria  [—]"
just pr 'docs(plan): record the phase one exit criteria  [—]'   # gate → push → PR → waits for checks
just merge                                                    # squash, bound to the checked head
```

- **Titles** are `type(scope): summary  [ref]`, scopes `frontend backend plan
  infra repo docs`. The PR title becomes the squash commit, so CI checks it.
- **Promotions** always use a **merge commit**: `just promote-staging`,
  `just promote-main`, then `just promote-merge <PR>`.
- **No assistant attribution.** `Co-Authored-By:` trailers for coding
  assistants and "Generated with…" lines are refused everywhere.

## Moving the application pins

```bash
just branch chore/pin-applications
just pin            # both pins → their development tips; prints the commits adopted
git commit -am "chore(repo): pin frontend and backend to their development tips  [—]"
just pr 'chore(repo): pin frontend and backend to their development tips  [—]'
```

The `test` check refuses any pin that the application's own flow branches do
not keep. A squash merge orphans work-branch commits, so never pin one. Platform
`staging` and `main` may pin only commits the applications have already
promoted, so a platform release always follows the application releases:

| Platform branch | May pin an application commit on its… |
|---|---|
| `development` | `development`, `staging` or `main` |
| `staging` | `staging` or `main` |
| `main` | `main` |

Dependabot also proposes a pin bump once a month.
