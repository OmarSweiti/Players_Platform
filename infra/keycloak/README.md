# Keycloak — the development identity provider

`just up` starts Keycloak 26.7.4, pinned by digest, in **development mode** (`start-dev`) at
<http://localhost:8080>. Development mode has insecure defaults (plain HTTP, a file database, relaxed
hostname checks), so it runs only on this machine, bound to 127.0.0.1, and never anywhere else
([ADR-0002](../../docs/adr/0002-identity-oidc.md)). Staging runs Keycloak's production configuration with TLS.

| | |
|---|---|
| Admin console | <http://localhost:8080/admin>. User `admin`; the password is `KEYCLOAK_ADMIN_PASSWORD` in `infra/.env` |
| Health | `/health/ready` on the management port, 9000, inside the container only; the compose health check asks it |
| State | the `sadara_keycloak` volume; `just reset` removes it |

## What arrives later

| Step | What |
|---|---|
| `0.5.1` | the `sadara` realm as code (`realm-sadara.json`, imported at start): client `sadara-api`, PKCE S256, MFA as assurance level 2, Arabic and English, mail to Mailpit; `test-realm.sh` proves each setting from the running server |
| `0.5.11` | the development members, one per role in each tenant, listed here with their development-only passwords |
| `1.1.7` | the bilingual login theme |
