# Keycloak — the development identity provider

`just up` starts Keycloak 26.7.4, pinned by digest, in **development mode** (`start-dev`) at
<http://localhost:8080>. Development mode has insecure defaults (plain HTTP, a file database, relaxed
hostname checks), so it runs only on this machine, bound to 127.0.0.1, and never anywhere else
([ADR-0002](../../docs/adr/0002-identity-oidc.md)). Staging runs Keycloak's production configuration with TLS.

| | |
|---|---|
| Admin console | <http://localhost:8080/admin>. User `admin`; the password is `KEYCLOAK_ADMIN_PASSWORD` in `infra/.env` |
| Health | `/health/ready` on the management port, 9000, inside the container only; the compose health check asks it |
| State | the `sadara_keycloak` volume; `just reset` removes it, and `just realm-reset` removes it alone |

## The `sadara` realm, as code (0.5.1)

`realm-sadara.json` is the realm, reviewed like any other code. Keycloak imports it at start
(`--import-realm`) **when the realm does not exist**; an existing realm is left as it is, so after
changing the file run `just realm-reset` — it starts Keycloak fresh, removing only Keycloak's own volume
(the realm's users, sessions and events with it), and the file is imported again. `bash infra/keycloak/test-realm.sh` proves every setting from the running server's admin API,
and exercises what it can: an authorization request without PKCE, passwords the policy must refuse, the
Arabic sign-in page.

| Setting | Value | Why |
|---|---|---|
| Client `sadara-api` | confidential, standard flow only, **PKCE S256 required**; no implicit flow, direct grants or service account; refresh tokens off | the API is the OIDC client and stores no provider token ([ADR-0003](../../docs/adr/0003-browser-sessions.md)) |
| Its secret | `${SADARA_API_CLIENT_SECRET}`, from `infra/.env` | the file holds a placeholder, never a secret |
| Redirect URIs | exactly `https://{host}/api/v1/auth/callback`, per tenant host | the proxy's hosts (`infra/proxy/Caddyfile`); `test-realm.sh` holds the two lists equal |
| Post-logout URIs | exactly `https://{host}/`, per tenant host | the web app's root; `0.5.7` returns the browser there |
| Back-channel logout | `http://host.docker.internal:3000/api/v1/auth/backchannel-logout`, session required; no front-channel logout | the API on this machine (`0.5.7`) |
| Passwords | at least 12 characters, no composition rules, not the username or email, not on the blocked list | NIST SP 800-63B; SR-AUTH-004 |
| Blocked passwords | `blocked-passwords.txt`: the entries of 12 characters or more of the NCSC's 100,000 most-used passwords, lower-cased (Keycloak compares without case) — see below | shorter ones fail the length rule already |
| Brute force | temporary lockout with growing waits, after 30 failures; Keycloak's own defaults | SR-AUTH-004; within NIST SP 800-63B's limit of 100 consecutive failures. The owner's security policy may tighten them |
| Email | verified; mail goes to Mailpit | |
| Levels of assurance | the browser flow `sadara browser`: level 1 is the password; **level 2 adds a second factor, OTP or WebAuthn**; a client asks for 2 with `acr_values=2`, and tokens carry `acr` | `0.5.8` requires level 2 of privileged roles |
| How long a level lasts | level 1, 12 hours (the session's absolute lifetime, OPEN-02); level 2, five minutes | the step-up window of [security](../../docs/reference/security-privacy.md) |
| WebAuthn and passkeys | available, never required: a member may register an OTP app, a security key or a passkey (`webauthn-register-passwordless`, discoverable keys) | SR-AUTH-008; adopted later without any API change |
| Languages | Arabic (the default) and English | |
| Events | login and admin events stored, without expiry; admin events without representations | `0.7.3` imports them (DB-61); no retention period is invented (OPEN-06) |

**What this release provides, recorded rather than assumed.** Keycloak 26.7.4 has an `amr` claim mapper
(`oidc-amr-mapper`), but the realm does not use it: assurance is asserted through `acr` levels, which is
what `0.5.8` checks. Passkeys need no switch in this release: the passwordless WebAuthn policy and its
registration action are what make them available.

### The blocked-password list

`blocked-passwords.txt` is derived from the UK NCSC's list of the 100,000 most-used passwords, as published in
[SecLists](https://github.com/danielmiessler/SecLists) (MIT licence) at commit `1a7bb9127eca9e6ff2fc0301c597fe6e16a0cb56`:
`Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt`, SHA-256
`c2e5696882c603b76bb67a47ee970897e5a76fc4c3f5547abe3d0ca340c576e0`. Each entry is trimmed and lower-cased,
the ones shorter than 12 characters are dropped, and duplicates are dropped after the first: 1,197
entries remain. To make it again:

```bash
curl -fsSL https://raw.githubusercontent.com/danielmiessler/SecLists/1a7bb9127eca9e6ff2fc0301c597fe6e16a0cb56/Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt |
  python3 -c 'import sys; seen = set()
for p in (l.strip().lower() for l in sys.stdin):
    if len(p) >= 12 and p not in seen: seen.add(p); print(p)' > infra/keycloak/blocked-passwords.txt
```

## What arrives later

| Step | What |
|---|---|
| `0.5.11` | the development members, one per role in each tenant, listed here with their development-only passwords |
| `1.1.7` | the bilingual login theme |
