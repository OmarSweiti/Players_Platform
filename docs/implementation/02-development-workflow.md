# Development workflow

How the work actually gets done — for a person and for an AI agent alike. The engineering law is
[`01-conventions.md`](01-conventions.md); how work ships is [`03-github-workflow.md`](03-github-workflow.md).
A command marked *from N.N.N* arrives with that microstep; `just --list` in each repository is the
authority on what exists today.

---

## Bring-up

Once per machine, from the umbrella root:

```bash
git clone --recurse-submodules git@github.com:OmarSweiti/Players_Platform.git
cd Players_Platform
just setup-all        # hooks, identity, tag signing, submodules; npm ci in both applications
just up               # PostgreSQL 18, Valkey, object store, ClamAV, Mailpit, Keycloak, HTTPS proxy   (from 0.2.1)
just trust-dev-ca     # trust the local proxy's certificate authority, once                          (from 0.2.1)
```

Then two terminals, each starting at the umbrella root:

```bash
# terminal 1 — the API (on :3000, served at https://<tenant>.localhost/api/ by the proxy)
cd backend && cp .env.example .env && just migrate && just seed && npm run start:dev
# terminal 2 — the web app (on :3001, served at https://<tenant>.localhost/ by the proxy)
cd frontend && npm run dev
```

`just migrate` applies migrations as the migrator role (from `0.4.2`); `just seed` loads the synthetic
tenants and members (from `0.5.11`). Open **`https://sadara.localhost`** — the host selects the tenant —
and sign in as a development member from the realm (the list is in `infra/keycloak/README.md`). The
browser only ever talks to one origin, over HTTPS, so the session cookie behaves exactly as in production.

Needs: `git` ≥ 2.34, `gh` (authenticated, SSH), `just`, `jq`, `gitleaks` ≥ 8.19, Docker with at least 4 GB of
memory ([why](../../infra/README.md#this-machine)), Python 3, and
Node from each application's `.nvmrc` (24.19.0). Work **from the umbrella root** so the plan and both
applications are in view; an agent opened inside one application reaches the plan through that
repository's `AGENTS.md`.

| Local URL | What |
|---|---|
| `https://sadara.localhost` | the web app, tenant `sadara` (`https://northwind.localhost` is the second tenant) |
| `https://sadara.localhost/api/v1` | the API, through the proxy — the address the browser and your tests use |
| `http://localhost:3000/docs` | the API's OpenAPI UI, directly (development only) |
| `http://localhost:8080` | Keycloak (development admin; never exposed beyond this machine) |
| `http://localhost:8025` | Mailpit — every email the stack sends |

## Commands

| Where | Command | Does |
|---|---|---|
| umbrella | `just setup` · `just setup-all` | hooks and identity here · and in both applications |
| umbrella | `just up` · `just down` · `just logs` · `just reset` | the local stack ([`infra/README.md`](../../infra/README.md)); `reset` asks, then destroys only its state volumes |
| umbrella | `just trust-dev-ca` · `just dev-ca-path` | trust the proxy's local certificate authority, once · print its path for `curl --cacert` |
| umbrella | `just check` | pins, the plan check, links — CI's `test` |
| umbrella | `just plan` | regenerate the progress rows, frontier, test catalog and traceability, then check |
| umbrella | `just pin` | move both pins to their `development` tips; refuses a rewind |
| umbrella | `just backup` · `just restore` · `just drill` | local backup, restore into a fresh stack, and the verified drill *(from 0.10.3)* |
| any | `just branch <prefix>/<slug>` | a fresh `development`, a validated branch name |
| any | `just pr '<title>' [body.md]` | the local gate → push → PR → waits for the required checks |
| any | `just merge <PR URL>` | the verified, clean squash merge |
| any | `just guards` · `just pre-push` | every guard proves it still refuses · the complete local gate |
| any | `just flow` · `just gh-audit` | what waits between branches · live GitHub settings vs the files |
| backend | `just check` | Prisma validate and generate, lint and formatting, build, unit tests |
| backend | `just test-int` · `just test-e2e` | integration and API tests on a real database *(from 0.2.3)* |
| backend | `just migrations` | replay every migration on a throwaway PostgreSQL 18; no drift allowed |
| backend | `just preflight` | the read-only integrity report *(from 0.4.1)* |
| backend | `just seed` | synthetic data, idempotent *(from 0.5.11)* |
| backend | `npm run openapi` | regenerate the committed contract *(from 0.3.9)* |
| backend | `npm run tenant:provision -- …` | create a tenant and invite its owner *(from 0.5.9)* |
| frontend | `just check` | type-check, lint and formatting, production build, unit tests, the browser journeys |
| frontend | `just test` · `just test-e2e` | unit and component tests (Vitest, jsdom, MSW) · the browser journeys in Arabic and English, with axe, against a fresh build |
| frontend | `just format` | rewrite the application code in Prettier's format |
| frontend | `npm run api:generate` | regenerate the typed client from the backend contract *(from 0.9.4)* |

## The microstep lifecycle

Every change follows nine stations. An agent follows them literally.

1. **Pick.** Read the frontier at the top of [`README.md`](README.md). Take a *ready* step — every
   dependency done — in the current phase; prefer the build order in the phase file; go sideways to an
   independent group when blocked. Never start a step whose dependencies are open.
2. **Read.** The microstep in full, every file it names, the requirements it cites, the references it
   links, and the conventions it touches. If the microstep is wrong against the code as it stands, **fix
   the microstep first** (a `docs(plan)` PR): the plan is maintained, not admired.
3. **Branch** in the repository the step names: `just branch feat/<slug>`.
4. **Test first** where the step adds behaviour: write the tests on its **Tests** line — the title
   carries the exact name — and watch them fail for the right reason.
5. **Build** exactly the step — its **Files**, nothing else. A neighbouring problem becomes a line under
   "Not in this PR" or a new microstep, not a silent expansion.
6. **Verify.** Run the step's **Verify** command; confirm its **Done when** sentence is true; then
   `just check`.
7. **Ship.** Commit `type(scope): summary  [N.N.N]`; `just pr` with the template filled — the Verify
   output, what was tried by hand, the hours spent; `just merge <URL>` once green. No assistant
   attribution anywhere.
8. **Record.** When the umbrella next moves its pins, set the step to `done` in
   [`progress.md`](progress.md) with its PR URL, run `just plan`, and ship that with the pin bump.
9. **Hand off.** Stopping with work in flight? Overwrite [`handoff.md`](handoff.md): the step, its state,
   the next action, anything surprising. One page; history is git's job.

## Rules for AI agents

- Start at `AGENTS.md` (Codex and others) or `CLAUDE.md` (Claude), then this file, then the frontier.
- **One microstep per PR.** Do not bundle steps; do not start the next one on the same branch.
- **Never weaken a gate to get green:** no skipped or deleted tests, no `--no-verify`, no disabled lint
  rule, no edited migration, no loosened ruleset, no `passWithNoTests`. If a gate is wrong, stop and say so.
- **Never mark a step done on a claim.** Paste the Verify output into the PR; the plan check refuses a
  `done` step whose named tests are missing or skipped.
- **Never invent** requirements, legal or medical facts, compliance claims, provider capabilities or
  test results. A missing answer is an OPEN item with a safe default ([master
  plan](00-master-plan.md#open-register)).
- **Never use real personal data** in code, tests, fixtures, seeds, logs or screenshots.
- **Frontend:** read `frontend/AGENTS.md` first — this Next.js differs from training data; read the
  relevant guide in `node_modules/next/dist/docs/` before writing Next.js code.
- **Schema:** read [`../reference/database.md`](../reference/database.md) and [migrations](01-conventions.md#migrations)
  first; run `just preflight`; write a new migration; never edit an old one.
- **When the plan and the code disagree about what exists, the code is the fact** — fix the plan in the
  same PR or first.

## Manual testing playbook

Run against the local stack after `just seed`. Every feature PR records what was tried by hand, **in
Arabic and in English**, on a freshly seeded database — including at least one attempt that must fail:
another tenant's id, a missing permission, an illegal transition, a stale `If-Match`.

- **In the browser:** sign in on `https://sadara.localhost` as the member whose role you are testing;
  repeat the refusal case as a member of `northwind` and as a member without the permission.
- **Against the API:** `just dev-cookie <member>` *(from 0.5.11)* signs a development member in
  headlessly and writes a curl cookie jar:

```bash
API=https://sadara.localhost/api/v1; CA=$(just dev-ca-path)          # the proxy's local CA (from 0.2.1)
just dev-cookie coach@sadara.test > jar
CSRF=$(curl -s --cacert "$CA" -b jar "$API/auth/session" | jq -r .data.csrfToken)
curl -s --cacert "$CA" -b jar "$API/players?limit=5" | jq '.data[0].id'
ETAG=$(curl -s --cacert "$CA" -b jar -D - -o /dev/null "$API/players/<id>" | awk 'tolower($1)=="etag:"{print $2}' | tr -d '\r')
curl -i --cacert "$CA" -b jar -X PATCH -H "X-CSRF-Token: $CSRF" -H 'Origin: https://sadara.localhost' \
     -H 'Content-Type: application/json' -H "If-Match: $ETAG" -d '{"preferredFoot":"LEFT"}' "$API/players/<id>"
```

Always send back the `ETag` the API returned; a made-up one is simply stale.

- **Mail** arrives in Mailpit. **Files:** upload through the UI, watch the file move from quarantine to
  ready once ClamAV has scanned it; the EICAR test string must be rejected.
- **The database, as the application sees it:**

```bash
docker compose -f infra/compose.yaml exec postgres psql -U sadara_app sadara
BEGIN; SELECT set_config('app.tenant_id', '<tenant uuid>', true); SELECT count(*) FROM players; COMMIT;
SELECT count(*) FROM players;          -- outside a tenant transaction: 0, by design
```

## Debugging

From a symptom to a minimal reproduction:

1. **Read the exact error** — the problem-details `code` and `requestId`, then the API log line with the
   same `requestId`, in the terminal running the API (`just logs <service>` for the stack). Guessing costs
   more than reading.
2. **Check the stack:** `just up` reports every service healthy? ClamAV's first signature download takes
   minutes; Keycloak takes about a minute to import the realm.
3. **Empty results where data exists** → the query ran outside `withTenantTransaction`, so row-level
   security returned nothing. This is the design working; route the query through the tenant transaction.
4. **`403 CSRF_FAILED` or an `Origin` refusal** → the request did not carry the session's CSRF token or
   came from another origin; the web app must call `/api` on its own origin.
5. **Sign-in loops or "invalid redirect"** → the tenant host is not registered as a redirect URI in the
   realm; `npm run tenant:provision` registers it.
6. **Prisma types out of date** → `npx prisma generate`. **A migration fails locally** → `just migrations`
   on a throwaway database tells you whether it is the migration or your data.
7. **A framework behaves unlike its documentation** → read the installed version's docs
   (`node_modules/next/dist/docs/`, the package's changelog) before changing anything.

Never "fix" by deleting the lockfile, reinstalling arbitrary versions or killing every Node process:
find the cause.

## Rituals

| When | Do |
|---|---|
| each session | `git switch development && git pull --ff-only` in the repository you work in; `just setup` if the post-merge hook says so; read [`handoff.md`](handoff.md) |
| each microstep | the nine stations |
| weekly | read open Dependabot PRs; re-read the risk register's triggers; update the effort forecast from measured hours; `gh run list --event schedule` to confirm scheduled workflows still run |
| each phase entry | **refine the phase file**: bring every microstep of the phase to full Files, Build, Tests, Verify and Done-when against the code as it stands; restate or settle each OPEN item it depends on; record the date |
| each phase gate | run the exit gate and record it (`0.11.1` and its successors); review the risk and long-lead registers; re-forecast; `just gh-audit` in all three repositories |
| monthly | merge grouped Dependabot updates after reading them; rehearse a restore once staging exists |
