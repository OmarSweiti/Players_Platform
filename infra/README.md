# The local stack

Everything the applications need on a development machine, from one command. The API and the web app
run on the host (`npm run start:dev` in `backend/`, `npm run dev` in `frontend/`), and the proxy puts
both behind one HTTPS origin per tenant, exactly as production routes them. The backend's worker runs
in the stack, built from the pinned backend (`0.7.6`): a process apart from the API, as it is deployed.

```bash
just up             # start everything and wait until every service is healthy; creates infra/.env on the first run
just trust-dev-ca   # once per machine: trust the proxy's certificate authority
just logs [service] # follow the logs
just down           # stop; every volume is kept
just reset          # destroy the local state; keeps the certificate authority and the virus signatures
just realm-reset    # start Keycloak fresh, importing infra/keycloak/realm-sadara.json again (its users go too)
just dev-cookie coach@sadara.test > jar   # sign a development member in, headlessly: a curl cookie jar for the API
```

| Service | Image (pinned by digest) | On this machine | For |
|---|---|---|---|
| `postgres` | PostgreSQL 18.6 | `127.0.0.1:5432`, databases `sadara` and `sadara_test` | the application database; the digest is the one the backend's CI replays migrations on ([ADR-0013](../docs/adr/0013-postgresql-18.md)) |
| `valkey` | Valkey 9.1.2 | `127.0.0.1:6379` | queues, rate limits, short-lived sign-in state |
| `objectstore` | Versity S3 Gateway 1.8.0 | `127.0.0.1:7070`, buckets `sadara` and `sadara-test` | private, versioned files ([ADR-0009](../docs/adr/0009-object-storage.md), [ADR-0020](../docs/adr/0020-local-object-store.md)) |
| `clamav` | ClamAV 1.5.4 | `127.0.0.1:3310` | the malware scan before a file is promoted (`0.8.4`); a file it cannot scan whole is reported, never passed |
| `mailpit` | Mailpit 1.31.2 | SMTP `127.0.0.1:1025`, <http://localhost:8025> | every email the stack sends: the worker's (an invitation's notice, `0.7.8`) and Keycloak's (an account's setup) |
| `keycloak` | Keycloak 26.7.4 | <http://localhost:8080> | the development identity provider, with the `sadara` realm as code ([keycloak/README.md](keycloak/README.md)) |
| `proxy` | Caddy 2.11.4 | <https://sadara.localhost>, <https://northwind.localhost>; <https://storage.localhost> | `/api/` → the API on `:3000`, everything else → the web app on `:3001`; `storage.localhost` → the object store, where a browser sends an upload (`0.8.3`) |
| `worker` | built from `backend/` (its Dockerfile pins every base image by digest) | no port; `just logs worker` | relays the transactional outbox to Valkey and runs the queue's jobs, each in its own tenant's transaction (`0.7.6`), sends their email to Mailpit (`0.7.8`), and scans each completed upload's file with ClamAV, promoting a clean one to an immutable copy in the object store (`0.8.4`); healthy while its relay's loop turns |

The development credentials are in `infra/.env`, copied from [`.env.example`](.env.example). They open
services bound to 127.0.0.1 and nothing else.

**PostgreSQL's roles (`0.4.2`).** When its volume is created, the database runs
[`postgres/init/10-roles.sql`](postgres/init/10-roles.sql), which applies the backend's one definition
(`backend/scripts/database-roles.sql`, the file CI and `just migrations` run too) in `sadara` and
`sadara_test`:

| Role | Logs in | What it is for |
|---|---|---|
| `sadara_owner` | never | owns both databases' schemas and everything in them |
| `sadara_migrator` | with `SADARA_MIGRATOR_PASSWORD` | `just migrate` and the test harness's migrations; it becomes the owner at login |
| `sadara_app` | with `SADARA_APP_PASSWORD` | the API, the worker and the tests: data only, never the schema, never past row-level security; statements 15 s, lock waits 5 s, idle in a transaction 60 s |
| `sadara_registry` | with `SADARA_REGISTRY_PASSWORD` | the worker's discovery: it reads `tenant_directory`'s `id` and `is_active` and nothing else (`0.7.6`); statements 5 s |

The API connects as `postgresql://sadara_app:<SADARA_APP_PASSWORD>@127.0.0.1:5432/sadara` and refuses to
boot as `postgres`. Both databases collate with PostgreSQL's builtin `C.UTF-8` provider (DB-51). The
collation takes effect only when the volume is created. The roles are applied again on every `just up`,
in both databases, from the passwords in the database container's environment: a volume made before a
role existed gains it (the registry role). `just up` adds missing settings to an existing `infra/.env`,
and warns when the volume predates the roles altogether; `just reset`, then `just up`, creates it again.

**The worker (`0.7.6`).** `just up` builds it from `backend/` whenever the backend changed, and starts it
once PostgreSQL, Valkey and Mailpit are healthy. It connects as `sadara_app` for its tenant transactions and
as `sadara_registry` to find the active tenants, and holds none of the API's identity-provider or session
settings. Its email goes to Mailpit, unencrypted — which it accepts only in development and test — from
`no-reply@sadara.localhost`, with links to `{slug}.localhost` (`0.7.8`). A stack whose database is not migrated yet runs it all the same: its relay's passes fail,
are logged and tried again, so `backend/`'s `just migrate` is all it waits for. `docker compose stop
worker` drains the jobs it is running before it stops.

## The rules, and what enforces them

- **Every image is pinned by digest**, and **every port binds to 127.0.0.1**. **Every service has a health
  check**, so `just up` can wait for it. **PostgreSQL runs the backend CI's digest.** A service built here
  (the worker) is built from the pinned backend alone, whose Dockerfile pins every base image by digest,
  and is never pulled. `scripts/check-stack.py` refuses anything else, in `just check` and CI.
- **The object store proves itself on every `just up`.** `objectstore/bootstrap.py` makes sure both
  buckets exist, are private and are versioned. It then shows, in a throwaway bucket, that the store does
  everything the storage port needs:
  - version ids;
  - reads pinned to a version;
  - presigned PUT and GET;
  - a presigned PUT refused at another length than it signed (`0.8.3`);
  - a server-side copy of one exact version;
  - refused anonymous reads;
  - CORS rules that admit a tenant's page and no other (`0.8.3`).

  It also sets the `sadara` bucket's CORS rules: the pages of the tenant hosts — the proxy's sites that
  route the API — may send uploads through the links the API signs for `https://storage.localhost`
  (the backend's `S3_PUBLIC_ENDPOINT`), and no other page may.
- **`just reset` destroys only this project's state volumes** (those labelled `org.sadara.state`), and only
  on a Docker engine on this machine. It asks first; `just reset yes` confirms without the prompt.

## Moving an image

1. Take the new version's multi-architecture digest from its registry.
   - Let a release age seven days first: that's the repository's Dependabot cooldown.
   - PostgreSQL moves together with the backend's CI and `just migrations`. `check-stack.py` fails while
     the two differ.
2. Run `just up`, then `just check`.

## This machine

- **Memory: give Docker at least 4 GB.** Measured on 29 September 2026:
  - ClamAV holds its signature database in memory, about 1 GB.
  - Keycloak uses about 0.5 GB and is capped at 1 GB.
  - Everything else together uses about 0.2 GB.

  In a 2 GB colima VM, the kernel killed clamd while it loaded its signatures, and `just up` timed out on
  ClamAV's health check. With colima, run `colima stop && colima start --memory 6`. Docker Desktop sets it
  under Settings → Resources.
- **Bind mounts** (`postgres/init`, `backend/scripts/database-roles.sql`, `proxy/Caddyfile`) need the
  repository in a directory Docker shares, and the backend checked out (`just setup`). colima shares your
  home directory by default.
- **`*.localhost` names.** Browsers and curl resolve `*.localhost` to both loopback addresses themselves.
  - Node.js and Python ask the operating system instead. macOS answers `::1` only, and colima forwards
    only `127.0.0.1`.
  - For a Node or Python client, add `127.0.0.1 sadara.localhost northwind.localhost storage.localhost` to `/etc/hosts`.
  - Point Node at the certificate authority with `NODE_EXTRA_CA_CERTS="$(just dev-ca-path)"`.
