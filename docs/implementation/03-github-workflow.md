# GitHub workflow

How work is tracked and shipped. The delivery flow is **live** in all three repositories and was
proven with negative canaries on 28 September 2026. This file says how to use it; each repository's
`CONTRIBUTING.md`, `SECURITY.md` and `.github/rulesets/README.md` say what it enforces, and the scripts
themselves are the final authority.

## Three repositories, one plan

| Repository | Holds | Its `test` check proves |
|---|---|---|
| [`Players_Platform`](https://github.com/OmarSweiti/Players_Platform) (umbrella) | this documentation, the progress record, the local stack, and one **pinned commit** of each application (git submodules) | every pin is a commit its application's flow branches keep; platform `staging`/`main` pin only what the applications already promoted; the plan, progress, traceability and links agree (`scripts/check-plan.py`) |
| [`Players_Platform_Backend`](https://github.com/OmarSweiti/Players_Platform_Backend) | the NestJS API, worker and realtime processes; the Prisma schema | the schema validates, the build compiles, the unit, integration and API tests pass (from `0.2.8`), every migration replays on PostgreSQL 18 and matches the schema |
| [`Players_Platform_Frontend`](https://github.com/OmarSweiti/Players_Platform_Frontend) | the Next.js web app | the code type-checks, lints, its unit and browser tests pass (from `0.2.4`), and the production build succeeds |

Code changes land in the application that owns them; the umbrella moves its pins afterwards and
records the progress in the same PR ([pins and progress](#the-umbrella-pins-and-progress)). A microstep
that touches two repositories is two PRs — backend first — carrying the same microstep ID.

## Branches

```text
feat/<slug> ──squash──► development ──merge commit──► staging ──merge commit──► main
                         (default)                     candidate vX.Y.Z-rc.N      release vX.Y.Z
hotfix/<slug> ◄── cut from main, merged back with merge commits, then back-merged main → staging → development
```

- Work branches: `feat|fix|chore|docs|refactor|perf|test/<kebab-slug>`, always from a fresh
  `development` (`just branch feat/player-profile`), always into `development`.
- Only `development`, `staging` and `main` live on the remote; merged branches are deleted.
- **Promotions and back-merges use merge commits, never squash** — a squash forks the branches
  permanently, and the rulesets refuse it on `staging` and `main`.

## Titles

```
<type>(<scope>): <summary>  [<ref>]
feat(contracts): add ordered approval steps  [1.4.3]
fix(auth): retire the local credential system  [0.1.6]
docs(plan): record the phase-0 exit criteria  [—]
```

- `type` ∈ `feat fix test docs chore refactor perf`; `scope` from the repository's closed list in
  `scripts/validate-change-title.sh` (the backend and frontend share the product-domain words).
- `ref` is **the microstep ID** (`N.N.N`, a split step `N.N.Nx`, or an en-dash range `N.N.N–N.N.N`),
  `#123` for an issue, or `—` for work outside the plan.
- The PR title becomes the squash commit, so CI checks it. No coding-assistant attribution — no
  `Co-Authored-By:` for a tool and no "Generated with" line — in any commit, title or PR body.

## The daily loop

```bash
just branch feat/player-directory            # validates the name, fresh development, new branch
git commit -m "feat(players): add the player directory  [1.2.4]"
just pr 'feat(players): add the player directory  [1.2.4]' notes/pr.md   # gate → push → PR → waits for checks
just merge <the PR URL that just pr printed>  # route, title, attribution, checks, clean merge state
```

- `just pr` runs `just pre-push` (the complete local gate) first. Use the **URL it prints** for
  `just merge`; never guess a PR number — another PR (often Dependabot's) may have taken it.
- `just merge` refuses unless every required check passed **and** GitHub reports the PR as cleanly
  mergeable. A `BEHIND` PR prints the fix: `gh pr update-branch <PR>`, then merge again. This matters:
  the admin's pull-request bypass is applied silently by the API, so a recipe that only asked GitHub
  to refuse would merge a behind PR as a logged bypass (it happened once, on Players_Platform#3).

## What is enforced, and by what

| Layer | Enforces | Bypassable by |
|---|---|---|
| **Rulesets** (server) | PR required on all three flow branches; no force-push or deletion; squash or merge into `development`, merge only into `staging`/`main`; five required checks; `v*` tags append-only | the admin, **through a PR only**, logged — and never for tags |
| **Required checks** (CI) | `test`, `guards`, `supply-chain` (secrets, attribution, npm advisories), `protected-paths` (committed migrations are immutable), `topology` (legal route, title grammar) | the logged admin bypass |
| **Hooks** (local) | commit subject grammar, attribution, secrets, sensitive files, immutable paths, direct pushes to flow branches, tag rules | `--no-verify`, or a clone that never ran `just setup` |
| **Recipes** | `just merge` / `just promote-merge` refuse illegal routes, bad titles, red checks and unclean merge states | calling `gh pr merge` directly |

Run `./scripts/gh-audit.sh` in any repository to diff the live settings and rulesets against the
files — it must report `no drift`.

## The umbrella: pins and progress

The umbrella pins one commit of each application. After application PRs merge:

```bash
cd Players_Platform
just branch chore/pin-applications
just pin                     # both pins → their development tips; refuses a rewind; prints the adopted commits
# set those microsteps to done in docs/implementation/progress.md, each with its merged PR URL
just plan                    # regenerate the frontier, test catalog and traceability; then check
git commit -am "chore(repo): pin the applications and record 1.2.1–1.2.3  [1.2.1–1.2.3]"
just pr 'chore(repo): pin the applications and record 1.2.1–1.2.3  [1.2.1–1.2.3]'
```

- The plan check verifies every `done` row against the pinned commits: its named tests must exist there
  and must not be skipped.
- `just pin` follows `branch = development` in `.gitmodules`; it never trusts a clone's stale
  `origin/HEAD` (which once "pinned" the old `main` — a rewind the recipe now refuses).
- `just setup` initialises only submodules that are not initialised, so it never detaches an
  application you are working in.
- A platform release follows the application releases: platform `staging` may pin only application
  commits on their `staging` or `main`; platform `main` only commits on their `main`.

## Releases

1. Bump the version in every file that carries it (`package.json` and `package-lock.json`; the
   umbrella's `VERSION`) through a normal PR.
2. `just promote-staging` → fill the promotion template (both SHAs, what is in it, evidence) →
   `just promote-merge <PR>`.
3. Tag the staging head, signed: `git tag -s v1.2.0-rc.1 -m "…" && git push origin refs/tags/v1.2.0-rc.1`.
   The release workflow verifies the signature, the head and the version, then builds a **draft**.
4. Use the candidate for real; then `just promote-main`, tag `v1.2.0` on `main`, inspect the draft,
   publish. Published releases and `v*` tags are immutable: a bad build is a new patch.
5. Release the applications first, then the umbrella ([pins and progress](#the-umbrella-pins-and-progress)).

## Dependabot

Monthly grouped version updates (patch and minor separately; majors one by one, for deliberate
review) and immediate security updates, all against `development`, all titled `chore(repo): …  [—]`.
Read every one before merging it; a major needs its migration notes read and the app exercised.
