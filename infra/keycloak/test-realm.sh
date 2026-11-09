#!/usr/bin/env bash
# The sadara realm, proved from the running server (0.5.1, 0.5.4, 0.5.9, 0.5.11; SR-AUTH-004, SR-AUTH-008).
# Every setting is read back through Keycloak's admin API, never from
# realm-sadara.json, and the rules that can be exercised are: an authorization
# request without PKCE, passwords the policy must refuse, the Arabic login page,
# a development member's sign-in, with and without a second factor.
# The expected values are the plan's, so a file that drifts from them fails here.
#
#   just up && bash infra/keycloak/test-realm.sh
#   KEYCLOAK_URL=http://localhost:8181 bash infra/keycloak/test-realm.sh   another server
#
# It signs in to the master realm as the bootstrap admin, with the password in
# infra/.env, which it never prints, nor the development members' password and
# authenticator secret. It creates one throwaway user to try passwords on, and
# deletes it again.
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -f infra/.env ] || { echo "test-realm: infra/.env is missing — run just up" >&2; exit 2; }
exec python3 -I - <<'PY'
import base64, hashlib, hmac, http.cookiejar, json, os, re, secrets, struct, sys, time, urllib.error, urllib.parse, urllib.request, uuid

def setting(name, default=None):
    """The last assignment of `name` in infra/.env, as Compose reads it."""
    value = default
    for line in open("infra/.env", encoding="utf-8"):
        if line.startswith(name + "="):
            value = line.rstrip("\n").split("=", 1)[1]
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
    return value

BASE = os.environ.get("KEYCLOAK_URL") or "http://localhost:%s" % setting("KEYCLOAK_PORT", "8080")
REALM = "sadara"
CLIENT = "sadara-api"
HOSTS = re.findall(r"^([a-z0-9.-]+(?:, [a-z0-9.-]+)*) \{", open("infra/proxy/Caddyfile").read(), re.M)
HOSTS = sorted(h.strip() for line in HOSTS for h in line.split(","))

# The development members (0.5.11): one per tenant role — the backend's
# UserRole, less the platform's SUPER_ADMIN — in each tenant the proxy serves.
# Each account's id is derived from its address, as the backend's seed derives
# it too (src/database/development-data.ts), so the two agree without either
# reading the other: RFC 9562's name-based UUIDv8, SHA-256 (its Appendix B.2).
DEVELOPMENT_NAMESPACE = uuid.UUID("b17a1124-e87a-42a1-8686-85b091391c55")

def development_id(name):
    digest = bytearray(hashlib.sha256(DEVELOPMENT_NAMESPACE.bytes + name.encode()).digest()[:16])
    digest[6] = (digest[6] & 0x0F) | 0x80
    digest[8] = (digest[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(digest)))
ROLES = [r for r in re.findall(r"^\s*([A-Z_]+)\b", re.search(
    r"^enum UserRole \{(.*?)^\}", open("backend/prisma/schema.prisma").read(), re.S | re.M).group(1), re.M)
         if r != "SUPER_ADMIN"]
# The roles that hold no session without a second factor (0.5.8): their
# accounts come with one, an authenticator already enrolled.
PRIVILEGED = {"OWNER", "ADMIN", "LEGAL", "FINANCE_MANAGER", "MEDICAL", "PHYSIOTHERAPIST", "SPORTING_DIRECTOR"}
MEMBERS = {"%s@%s.test" % (role.lower().replace("_", "-"), host.split(".")[0]): role
           for host in HOSTS for role in ROLES}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

opener = urllib.request.build_opener(NoRedirect)

def call(method, path, token=None, body=None, form=None):
    """(status, headers, parsed body or text) for one request; never raises on an HTTP status."""
    data, headers = None, {}
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        response = opener.open(request, timeout=30)
        status, header, raw = response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        status, header, raw = error.code, error.headers, error.read()
    text = raw.decode("utf-8", "replace")
    try:
        return status, header, json.loads(text) if text else None
    except ValueError:
        return status, header, text

status, _, grant = call("POST", "/realms/master/protocol/openid-connect/token", form={
    "client_id": "admin-cli", "grant_type": "password", "username": "admin",
    "password": setting("KEYCLOAK_ADMIN_PASSWORD")})
if status != 200:
    sys.exit("test-realm: cannot sign in to %s as the bootstrap admin (HTTP %s): is the stack up?" % (BASE, status))
TOKEN = grant["access_token"]

def admin(path):
    status, _, body = call("GET", "/admin/realms/%s%s" % (REALM, path), TOKEN)
    if status != 200:
        raise AssertionError("GET %s answered %s" % (path, status))
    return body

def expect(condition, message):
    if not condition:
        raise AssertionError(message)

def api_client():
    clients = admin("/clients?clientId=" + CLIENT)
    expect(len(clients) == 1, "the realm has no client %s" % CLIENT)
    return clients[0]

def authorize(redirect_uri, **pkce):
    query = dict(client_id=CLIENT, response_type="code", scope="openid", state="test-realm",
                 redirect_uri=redirect_uri, **pkce)
    return call("GET", "/realms/%s/protocol/openid-connect/auth?%s" % (REALM, urllib.parse.urlencode(query)))

# ── The tests ───────────────────────────────────────────────────────────────

def the_api_client_requires_pkce():
    client = api_client()
    expect(client["attributes"].get("pkce.code.challenge.method") == "S256", "PKCE is not S256")
    expect(not client["publicClient"] and client["clientAuthenticatorType"] == "client-secret",
           "the client is not confidential")
    flows = {k: client[k] for k in ("standardFlowEnabled", "implicitFlowEnabled",
                                    "directAccessGrantsEnabled", "serviceAccountsEnabled")}
    expect(flows == {"standardFlowEnabled": True, "implicitFlowEnabled": False,
                     "directAccessGrantsEnabled": False, "serviceAccountsEnabled": False},
           "not the standard flow alone: %s" % flows)
    # The server itself refuses a request without S256, and serves one with it.
    callback = "https://%s/api/v1/auth/callback" % HOSTS[0]
    challenge = secrets.token_urlsafe(43)
    for pkce, refusal in (({}, "Missing parameter: code_challenge_method"),
                          ({"code_challenge": challenge, "code_challenge_method": "plain"},
                           "code challenge method is not matching")):
        status, headers, _ = authorize(callback, **pkce)
        location = urllib.parse.unquote_plus(headers.get("Location") or "")
        expect(status == 302 and "error=invalid_request" in location and refusal in location,
               "a request with %s was not refused (%s)" % (pkce.get("code_challenge_method", "no PKCE"), status))
    status, _, _ = authorize(callback, code_challenge=challenge, code_challenge_method="S256")
    expect(status == 200, "a request with S256 did not reach the sign-in page (%s)" % status)

def the_client_secret_comes_from_the_environment():
    # Compared, never printed: the realm file holds a placeholder, and the
    # server holds infra/.env's value.
    status, _, secret = call("GET", "/admin/realms/%s/clients/%s/client-secret" % (REALM, api_client()["id"]), TOKEN)
    expect(status == 200, "cannot read the client secret (%s)" % status)
    value = secret.get("value") or ""
    expect("${" not in value, "the server holds the placeholder, not a secret")
    expect(secrets.compare_digest(value, setting("SADARA_API_CLIENT_SECRET") or ""),
           "the server's secret is not infra/.env's SADARA_API_CLIENT_SECRET")

def exact_redirect_and_logout_uris_per_tenant_host():
    client = api_client()
    expect(sorted(client["redirectUris"]) == ["https://%s/api/v1/auth/callback" % h for h in HOSTS],
           "redirect URIs %s are not the proxy's hosts %s" % (client["redirectUris"], HOSTS))
    logout = sorted(client["attributes"].get("post.logout.redirect.uris", "").split("##"))
    expect(logout == ["https://%s/" % h for h in HOSTS], "post-logout URIs %s" % logout)
    expect(client["attributes"].get("backchannel.logout.url", "").endswith("/api/v1/auth/backchannel-logout")
           and client["attributes"].get("backchannel.logout.session.required") == "true"
           and not client["frontchannelLogout"], "back-channel logout is not set, with the session required")
    status, _, _ = authorize("https://elsewhere.test/api/v1/auth/callback",
                             code_challenge=secrets.token_urlsafe(43), code_challenge_method="S256")
    expect(status == 400, "an unregistered redirect URI was not refused (%s)" % status)

def brute_force_detection_is_enabled():
    realm = admin("")
    expect(realm["bruteForceProtected"], "brute-force detection is off")
    expect(not realm["permanentLockout"], "the lockout is permanent, not temporary")
    # NIST SP 800-63B: no more than 100 consecutive failures before throttling.
    expect(0 < realm["failureFactor"] <= 100, "failure factor %s" % realm["failureFactor"])
    expect(realm["waitIncrementSeconds"] > 0 and realm["maxFailureWaitSeconds"] > 0, "no wait between attempts")

def the_password_policy_refuses_short_and_blocked_passwords():
    policy = admin("")["passwordPolicy"]
    for rule in ("length(12)", "passwordBlacklist(blocked-passwords.txt)"):
        expect(rule in policy, "the policy %r has no %s" % (policy, rule))
    for composition in ("upperCase", "lowerCase", "digits", "specialChars", "regexPattern"):
        expect(composition + "(" not in policy, "a composition rule: %s" % composition)
    username = "test-realm-%s" % secrets.token_hex(4)
    status, headers, _ = call("POST", "/admin/realms/%s/users" % REALM, TOKEN, body={
        "username": username, "email": username + "@agency.test", "enabled": True, "emailVerified": True})
    expect(status == 201, "cannot create a throwaway user (%s)" % status)
    user = headers["Location"].rsplit("/", 1)[1]
    try:
        for password, refusal in (("short-pass1", "invalidPasswordMinLengthMessage"),
                                  ("QWERTY123456", "invalidPasswordBlacklistedMessage"),
                                  (username + "@agency.test", "invalidPasswordNotEmailMessage"),
                                  ("a long passphrase of plain words", None)):
            status, _, body = call("PUT", "/admin/realms/%s/users/%s/reset-password" % (REALM, user), TOKEN,
                                   body={"type": "password", "value": password, "temporary": False})
            got = (body or {}).get("error") if isinstance(body, dict) else None
            expect((status, got) == ((400, refusal) if refusal else (204, None)),
                   "password %d chars: %s %s" % (len(password), status, got))
    finally:
        call("DELETE", "/admin/realms/%s/users/%s" % (REALM, user), TOKEN)

def email_is_verified_and_sent_to_mailpit():
    realm = admin("")
    expect(realm["verifyEmail"], "email verification is off")
    smtp = realm.get("smtpServer") or {}
    expect((smtp.get("host"), str(smtp.get("port"))) == ("mailpit", "1025"), "mail goes to %s" % smtp)

def mfa_maps_to_assurance_level_2():
    realm = admin("")
    expect(realm["browserFlow"] == "sadara browser", "the browser flow is %r" % realm["browserFlow"])
    executions = admin("/authentication/flows/sadara%20browser/executions")
    levels = {}
    for i, step in enumerate(executions):
        if step.get("providerId") == "conditional-level-of-authentication":
            config = admin("/authentication/config/%s" % step["authenticationConfig"])["config"]
            depth = step["level"]
            below = []
            for later in executions[i + 1:]:
                if later["level"] < depth:
                    break
                below.append(later)
            levels[config["loa-condition-level"]] = (config, below)
    expect(set(levels) == {"1", "2"}, "levels of assurance %s" % sorted(levels))
    _, first = levels["1"]
    expect(any(s.get("providerId") == "auth-username-password-form" and s["requirement"] == "REQUIRED"
               for s in first), "level 1 does not ask for the password")
    config, second = levels["2"]
    factors = {s.get("providerId"): s["requirement"] for s in second if s.get("providerId")}
    expect(factors.get("auth-otp-form") == "ALTERNATIVE" and factors.get("webauthn-authenticator") == "ALTERNATIVE",
           "level 2 is not OTP or WebAuthn: %s" % factors)
    expect(int(config["loa-max-age"]) == 300, "level 2 lasts %ss, not the five-minute step-up window" %
           config["loa-max-age"])
    expect("acr" in api_client()["defaultClientScopes"], "the client's tokens carry no acr claim")

def webauthn_and_passkeys_are_available_not_required():
    actions = {a["alias"]: a for a in admin("/authentication/required-actions")}
    for alias in ("CONFIGURE_TOTP", "webauthn-register", "webauthn-register-passwordless"):
        action = actions.get(alias) or {}
        expect(action.get("enabled") and not action.get("defaultAction"),
               "%s is not available, or is required of everyone" % alias)
    realm = admin("")
    expect(realm["webAuthnPolicyPasswordlessResidentKey"] == "required", "passwordless keys are not discoverable")

def arabic_and_english():
    realm = admin("")
    expect(realm["internationalizationEnabled"] and realm["supportedLocales"] == ["ar", "en"]
           and realm["defaultLocale"] == "ar", "locales %s, default %s" % (realm["supportedLocales"],
                                                                              realm["defaultLocale"]))
    query = urllib.parse.urlencode(dict(client_id=CLIENT, response_type="code", scope="openid", ui_locales="ar",
                                        redirect_uri="https://%s/api/v1/auth/callback" % HOSTS[0],
                                        code_challenge=secrets.token_urlsafe(43), code_challenge_method="S256"))
    status, _, page = call("GET", "/realms/%s/protocol/openid-connect/auth?%s" % (REALM, query))
    expect(status == 200 and re.search(r'<html[^>]*lang="ar"[^>]*dir="rtl"', page or ""),
           "the sign-in page is not served in Arabic, right to left")

def sign_in_events_are_stored():
    events = admin("/events/config")
    expect(events["eventsEnabled"] and events["adminEventsEnabled"], "login or admin events are off")
    expect(not events["adminEventsDetailsEnabled"], "admin events store representations")
    needed = {"LOGIN", "LOGIN_ERROR", "LOGOUT", "USER_DISABLED_BY_TEMPORARY_LOCKOUT", "UPDATE_CREDENTIAL",
              "REMOVE_CREDENTIAL", "UPDATE_TOTP", "REMOVE_TOTP"}
    missing = needed - set(events["enabledEventTypes"])
    expect(not missing, "events not stored: %s" % sorted(missing))
    # Kept, as 0.7.3 imports them, until a retention policy exists (OPEN-06).
    expect(not events.get("eventsExpiration"), "events expire after %ss" % events.get("eventsExpiration"))

def the_admin_account_manages_users_only():
    # 0.5.4: the API manages accounts as sadara-admin's service account, which
    # holds realm-management's manage-users and nothing else.
    clients = admin("/clients?clientId=sadara-admin")
    expect(len(clients) == 1, "the realm has no client sadara-admin")
    client = clients[0]
    flows = {k: client[k] for k in ("publicClient", "standardFlowEnabled", "implicitFlowEnabled",
                                    "directAccessGrantsEnabled", "serviceAccountsEnabled")}
    expect(flows == {"publicClient": False, "standardFlowEnabled": False, "implicitFlowEnabled": False,
                     "directAccessGrantsEnabled": False, "serviceAccountsEnabled": True},
           "not a confidential service account alone: %s" % flows)
    status, _, secret = call("GET", "/admin/realms/%s/clients/%s/client-secret" % (REALM, client["id"]), TOKEN)
    expect(status == 200 and "${" not in (secret.get("value") or ""), "the server holds no secret, or the placeholder")
    expect(secrets.compare_digest(secret.get("value") or "", setting("SADARA_ADMIN_CLIENT_SECRET") or ""),
           "the server's secret is not infra/.env's SADARA_ADMIN_CLIENT_SECRET")
    account = admin("/clients/%s/service-account-user" % client["id"])
    roles = admin("/users/%s/role-mappings" % account["id"])
    granted = {name: sorted(r["name"] for r in mapping["mappings"])
               for name, mapping in roles.get("clientMappings", {}).items()}
    expect(not roles.get("realmMappings") and granted == {"realm-management": ["manage-users"]},
           "the service account holds %s and realm roles %s" % (granted, [r["name"] for r in roles.get("realmMappings", [])]))
    # Exercised: its token reads users, and is refused the realm's clients,
    # roles and events and every other realm.
    status, _, grant = call("POST", "/realms/%s/protocol/openid-connect/token" % REALM, form={
        "client_id": "sadara-admin", "client_secret": setting("SADARA_ADMIN_CLIENT_SECRET"),
        "grant_type": "client_credentials"})
    expect(status == 200, "the service account cannot sign in (%s)" % status)
    answers = {path: call("GET", path, grant["access_token"])[0] for path in (
        "/admin/realms/%s/users?max=1" % REALM, "/admin/realms/%s/clients" % REALM,
        "/admin/realms/%s/roles" % REALM, "/admin/realms/%s/events" % REALM, "/admin/realms/master/users")}
    expect(answers == {"/admin/realms/%s/users?max=1" % REALM: 200, "/admin/realms/%s/clients" % REALM: 403,
                       "/admin/realms/%s/roles" % REALM: 403, "/admin/realms/%s/events" % REALM: 403,
                       "/admin/realms/master/users": 403}, "the service account's reach: %s" % answers)
    # And the sign-in client has no service account to sign in as.
    status, _, _ = call("POST", "/realms/%s/protocol/openid-connect/token" % REALM, form={
        "client_id": CLIENT, "client_secret": setting("SADARA_API_CLIENT_SECRET"), "grant_type": "client_credentials"})
    expect(status in (400, 401), "%s signed in by client credentials (%s)" % (CLIENT, status))

def the_provisioning_account_manages_clients_only():
    # 0.5.9: the provisioning command registers a tenant's hosts on the sign-in
    # client as sadara-provisioner's service account, which holds
    # realm-management's manage-clients and nothing else. The API never holds it.
    clients = admin("/clients?clientId=sadara-provisioner")
    expect(len(clients) == 1, "the realm has no client sadara-provisioner")
    client = clients[0]
    flows = {k: client[k] for k in ("publicClient", "standardFlowEnabled", "implicitFlowEnabled",
                                    "directAccessGrantsEnabled", "serviceAccountsEnabled")}
    expect(flows == {"publicClient": False, "standardFlowEnabled": False, "implicitFlowEnabled": False,
                     "directAccessGrantsEnabled": False, "serviceAccountsEnabled": True},
           "not a confidential service account alone: %s" % flows)
    status, _, secret = call("GET", "/admin/realms/%s/clients/%s/client-secret" % (REALM, client["id"]), TOKEN)
    expect(status == 200 and "${" not in (secret.get("value") or ""), "the server holds no secret, or the placeholder")
    expect(secrets.compare_digest(secret.get("value") or "", setting("SADARA_PROVISIONER_CLIENT_SECRET") or ""),
           "the server's secret is not infra/.env's SADARA_PROVISIONER_CLIENT_SECRET")
    account = admin("/clients/%s/service-account-user" % client["id"])
    roles = admin("/users/%s/role-mappings" % account["id"])
    granted = {name: sorted(r["name"] for r in mapping["mappings"])
               for name, mapping in roles.get("clientMappings", {}).items()}
    expect(not roles.get("realmMappings") and granted == {"realm-management": ["manage-clients"]},
           "the service account holds %s and realm roles %s" % (granted, [r["name"] for r in roles.get("realmMappings", [])]))
    # Exercised: its token reads the sign-in client, and is refused the
    # realm's users, roles and events and every other realm.
    status, _, grant = call("POST", "/realms/%s/protocol/openid-connect/token" % REALM, form={
        "client_id": "sadara-provisioner", "client_secret": setting("SADARA_PROVISIONER_CLIENT_SECRET"),
        "grant_type": "client_credentials"})
    expect(status == 200, "the service account cannot sign in (%s)" % status)
    api = api_client()
    answers = {path: call("GET", path, grant["access_token"])[0] for path in (
        "/admin/realms/%s/clients/%s" % (REALM, api["id"]), "/admin/realms/%s/users?max=1" % REALM,
        "/admin/realms/%s/roles" % REALM, "/admin/realms/%s/events" % REALM, "/admin/realms/master/clients")}
    expect(answers == {"/admin/realms/%s/clients/%s" % (REALM, api["id"]): 200,
                       "/admin/realms/%s/users?max=1" % REALM: 403, "/admin/realms/%s/roles" % REALM: 403,
                       "/admin/realms/%s/events" % REALM: 403, "/admin/realms/master/clients": 403},
           "the service account's reach: %s" % answers)

def the_event_reader_reads_events_only():
    # 0.7.3: the security-event import reads the realm's login and admin events
    # as sadara-events' service account, which holds realm-management's
    # view-events and nothing else. The API never holds it.
    clients = admin("/clients?clientId=sadara-events")
    expect(len(clients) == 1, "the realm has no client sadara-events")
    client = clients[0]
    flows = {k: client[k] for k in ("publicClient", "standardFlowEnabled", "implicitFlowEnabled",
                                    "directAccessGrantsEnabled", "serviceAccountsEnabled")}
    expect(flows == {"publicClient": False, "standardFlowEnabled": False, "implicitFlowEnabled": False,
                     "directAccessGrantsEnabled": False, "serviceAccountsEnabled": True},
           "not a confidential service account alone: %s" % flows)
    status, _, secret = call("GET", "/admin/realms/%s/clients/%s/client-secret" % (REALM, client["id"]), TOKEN)
    expect(status == 200 and "${" not in (secret.get("value") or ""), "the server holds no secret, or the placeholder")
    expect(secrets.compare_digest(secret.get("value") or "", setting("SADARA_EVENTS_CLIENT_SECRET") or ""),
           "the server's secret is not infra/.env's SADARA_EVENTS_CLIENT_SECRET")
    account = admin("/clients/%s/service-account-user" % client["id"])
    roles = admin("/users/%s/role-mappings" % account["id"])
    granted = {name: sorted(r["name"] for r in mapping["mappings"])
               for name, mapping in roles.get("clientMappings", {}).items()}
    expect(not roles.get("realmMappings") and granted == {"realm-management": ["view-events"]},
           "the service account holds %s and realm roles %s" % (granted, [r["name"] for r in roles.get("realmMappings", [])]))
    # Exercised: its token reads login and admin events, and is refused the
    # realm's users, clients and roles, the events' settings, and every other realm.
    status, _, grant = call("POST", "/realms/%s/protocol/openid-connect/token" % REALM, form={
        "client_id": "sadara-events", "client_secret": setting("SADARA_EVENTS_CLIENT_SECRET"),
        "grant_type": "client_credentials"})
    expect(status == 200, "the service account cannot sign in (%s)" % status)
    answers = {path: call("GET", path, grant["access_token"])[0] for path in (
        "/admin/realms/%s/events?max=1" % REALM, "/admin/realms/%s/admin-events?max=1" % REALM,
        "/admin/realms/%s/users?max=1" % REALM, "/admin/realms/%s/clients" % REALM,
        "/admin/realms/%s/roles" % REALM, "/admin/realms/master/events")}
    expect(answers == {"/admin/realms/%s/events?max=1" % REALM: 200,
                       "/admin/realms/%s/admin-events?max=1" % REALM: 200,
                       "/admin/realms/%s/users?max=1" % REALM: 403, "/admin/realms/%s/clients" % REALM: 403,
                       "/admin/realms/%s/roles" % REALM: 403, "/admin/realms/master/events": 403},
           "the service account's reach: %s" % answers)
    status, _, _ = call("PUT", "/admin/realms/%s/events/config" % REALM, grant["access_token"],
                        body={"eventsEnabled": False})
    expect(status == 403, "the service account may change the events' settings (%s)" % status)

def development_members_one_per_role_in_each_tenant():
    expect(len(ROLES) >= 17 and "OWNER" in ROLES, "the backend's roles were not read: %s" % ROLES)
    expect(development_id("tenant:sadara") == "0b8bcd4b-0465-8de0-ae58-1b5acbb6c58e",
           "the id rule is not the seed's: tenant:sadara gives %s" % development_id("tenant:sadara"))
    for address, role in sorted(MEMBERS.items()):
        found = admin("/users?exact=true&username=" + urllib.parse.quote(address))
        expect(len(found) == 1, "no development account %s" % address)
        user = found[0]
        expect(user["id"] == development_id("account:" + address), "%s's id is not derived from its address" % address)
        expect(user["email"] == address and user["emailVerified"] and user["enabled"],
               "%s is not enabled with its address verified" % address)
        expect(not user.get("requiredActions"), "%s must first %s" % (address, user.get("requiredActions")))
        expect(user.get("firstName") and user.get("lastName"), "%s has no name: the first sign-in would ask" % address)
        kinds = sorted(c["type"] for c in admin("/users/%s/credentials" % user["id"]))
        expect(kinds == (["otp", "password"] if role in PRIVILEGED else ["password"]),
               "%s, %s, holds %s" % (address, role, kinds))

def totp(secret, at):
    """RFC 6238 as Keycloak computes it: HMAC-SHA1 over the secret's UTF-8 bytes, 30 s, six digits."""
    digest = hmac.new(secret.encode(), struct.pack(">Q", int(at // 30)), hashlib.sha1).digest()
    offset = digest[-1] & 15
    return "%06d" % ((struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1000000)

def form_action(page):
    match = re.search(r'<form[^>]*\baction="([^"]+)"', page or "")
    expect(match, "no sign-in form on the page")
    return match.group(1).replace("&amp;", "&")

class LoopbackIsSecure(http.cookiejar.DefaultCookiePolicy):
    """A browser treats http://localhost as a secure context, so Keycloak's Secure cookies go there too."""
    def return_ok_secure(self, cookie, request):
        return (urllib.parse.urlsplit(request.get_full_url()).hostname in ("localhost", "127.0.0.1")
                or super().return_ok_secure(cookie, request))

def sign_in(address, level):
    """Through the realm's own forms, as a browser would: the redirect it ends with carries a code."""
    jar = http.cookiejar.CookieJar(LoopbackIsSecure())
    browser = urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(jar))
    def go(url, form=None):
        data = urllib.parse.urlencode(form).encode() if form is not None else None
        try:
            response = browser.open(urllib.request.Request(url, data=data), timeout=30)
            return response.status, response.headers, response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            return error.code, error.headers, error.read().decode("utf-8", "replace")
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    callback = "https://%s/api/v1/auth/callback" % HOSTS[0]
    query = dict(client_id=CLIENT, response_type="code", scope="openid", state="test-realm", redirect_uri=callback,
                 code_challenge=challenge, code_challenge_method="S256", acr_values=level)
    status, _, page = go("%s/realms/%s/protocol/openid-connect/auth?%s" % (BASE, REALM, urllib.parse.urlencode(query)))
    expect(status == 200, "the sign-in page answered %s" % status)
    status, headers, page = go(form_action(page), {"username": address,
                                                   "password": setting("SADARA_DEV_MEMBER_PASSWORD") or ""})
    for attempt in range(2):
        if status != 200 or 'name="otp"' not in page:
            break
        # A code is good once: one already used waits for the next window.
        status, headers, page = go(form_action(page), {"otp": totp(setting("SADARA_DEV_OTP_SECRET") or "", time.time())})
        if status == 200 and 'name="otp"' in page and attempt == 0:
            time.sleep(31 - time.time() % 30)
    location = headers.get("Location") or ""
    expect(status == 302 and location.startswith(callback + "?") and "code=" in location,
           "%s at level %s did not sign in (%s)" % (address, level, status))

def a_development_member_signs_in_with_infra_env_credentials():
    # The password and the authenticator secret are infra/.env's, which the
    # realm file reads: a placeholder left unresolved would fail here.
    plain = next(a for a, r in sorted(MEMBERS.items()) if r not in PRIVILEGED)
    privileged = next(a for a, r in sorted(MEMBERS.items()) if r in PRIVILEGED)
    sign_in(plain, "1")
    sign_in(privileged, "2")

TESTS = [the_api_client_requires_pkce, the_client_secret_comes_from_the_environment,
         exact_redirect_and_logout_uris_per_tenant_host,
         brute_force_detection_is_enabled, the_password_policy_refuses_short_and_blocked_passwords,
         email_is_verified_and_sent_to_mailpit, mfa_maps_to_assurance_level_2,
         webauthn_and_passkeys_are_available_not_required, arabic_and_english, sign_in_events_are_stored,
         the_admin_account_manages_users_only, the_provisioning_account_manages_clients_only,
         the_event_reader_reads_events_only,
         development_members_one_per_role_in_each_tenant, a_development_member_signs_in_with_infra_env_credentials]

failed = 0
for test in TESTS:
    try:
        test()
        print("  ok    %s" % test.__name__)
    except AssertionError as error:
        failed += 1
        print("  FAIL  %s: %s" % (test.__name__, error))
print("test-realm: %d passed, %d failed, against %s/realms/%s" % (len(TESTS) - failed, failed, BASE, REALM))
sys.exit(1 if failed else 0)
PY
