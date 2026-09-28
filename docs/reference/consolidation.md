# What happened to the old documents

Before 28 September 2026 the three repositories held 25 hand-written guides, status reports, prompt
templates and an always-on AI rule file. They contradicted each other and the code, and several
instructed agents to do unsafe things. They were **retired**: their valid content was merged into
this documentation set, the files were deleted, and each subject now has **one** active authority.

Nothing is lost. Every file is recoverable from git history at the commit shown:

```bash
git show 3403e0a:AUTH_IMPLEMENTATION_AUDIT.md          # umbrella files: run in the umbrella
git -C frontend show ac37f1c:QUICK_START.md            # application files: run in that repository
```

**No legacy claim earned completion credit.** "Complete", percentages, checkboxes, test counts,
estimates and security or compliance verdicts were not imported; what the code actually does is in
[`current-state.md`](current-state.md), verified against the code.

---

## File by file

Line ranges cite the file at its last commit. *Kept* is what moved into the new set; *dropped* is
what did not, and why.

### Umbrella

| File (lines) · last commit | Went to | Kept · dropped |
|---|---|---|
| `AUTH_ACTION_ITEMS.md` (459) · `3403e0a` | [phase 0](../implementation/phase-0-foundation.md) identity group; [security](security-privacy.md) | *Kept:* the MFA-enrolment, recovery, session-persistence and cross-tenant-test intent (`:8–19`, `:347–419`). *Dropped:* the "low priority" ranking of sessions and recovery — they are security work — and the estimates. |
| `AUTH_IMPLEMENTATION_AUDIT.md` (663) · `3403e0a` | [current-state](current-state.md) | *Kept:* its inventory, as a checklist to verify. *Dropped:* "FULLY IMPLEMENTED (95% Complete)" (`:4`), the isolation and production-readiness verdicts — no test supports them — and two wrong claims: that uniqueness is tenancy enforcement (`:161`) and that HttpOnly prevents CSRF (`:405`). |
| `AUTH_PHASE_SUMMARY.md` (309) · `3403e0a` | [phase 0](../implementation/phase-0-foundation.md); [ADR-0002](../adr/0002-identity-oidc.md) | *Kept:* the session and revocation gaps (`:55–65`, `:188–215`). *Dropped:* "all items complete", automatic tenancy, and the claim that fake revocation is acceptable for an MVP (`:278–290`). |
| `AUTH_SUMMARY.md` (276) · `3403e0a` | — | A duplicate summary. *Dropped:* "95% COMPLETE – PRODUCTION READY" (`:4`), contradicted by its own missing-tests section. |
| `AUTH_TESTING_GUIDE.md` (596) · `3403e0a` | [development workflow](../implementation/02-development-workflow.md) manual-testing playbook; [test catalog](test-catalog.md) | *Kept:* the role, tenant, lockout, refresh, MFA and error journeys as test cases (`:177–224`, `:364–383`, `:469–519`). *Dropped:* shared credentials, hand-copied tokens, direct database edits to verify accounts, and "if implemented" pass conditions. |
| `DEVELOPMENT_GUIDE.md` (698) · `9378447` | [development workflow](../implementation/02-development-workflow.md) bring-up and troubleshooting | *Kept:* separate terminals per app, Prisma client generation, the debug loop and request inspection (`:266–306`, `:577–582`). *Dropped:* Node "v18 or higher" (`:21`; the apps pin 24.19.0), PostgreSQL 14, Windows commands (`:371`), tenant ids pasted into localStorage, and "delete the lockfile" fixes. |
| `FEATURE_IMPLEMENTATION_PROMPT_TEMPLATE.md` (875) · `3403e0a` | [conventions](../implementation/01-conventions.md); the microstep format | *Kept:* explicit acceptance, typed boundaries, thin controllers, validated input, UI states (`:7–43`, `:78–110`). *Dropped:* the 875-line prompt itself — one microstep is the contract now — and its unsafe rules: "never manually filter by tenant", events as durable delivery, the untested auth module as the golden example (`:96`). |
| `IMPLEMENTATION_CHECKLIST.md` (1,827) · `3403e0a` | the phase files; [security](security-privacy.md) role matrix; [domain workflows](domain-workflows.md) | *Kept:* the role intentions and the module and edge-case inventory, reconciled to requirement IDs (`:180–618`, `:1700–1809`). *Dropped:* "95% Complete" (`:8`), its own phase order and completion marks; payroll, match-day operations and tax invoicing do not become commitments without a requirement. |
| `IMPLEMENTATION_STATUS.md` (289) · `3403e0a` | [observability](observability.md) | *Kept:* request correlation, slow-call visibility, the audit-versus-log distinction (`:162–173`). *Dropped:* "100% logging", "no sensitive data logged" — the code logs tokens — and the compliance claims. |
| `LOGGING_IMPLEMENTATION_GUIDE.md` (732) · `3403e0a` | [observability](observability.md); invariant I-12 | *Kept:* the security-event taxonomy, severity, correlation, redaction and alert ownership (`:28–47`, `:497–551`). *Dropped:* copy-paste logging per use case, examples that log emails and tokens, local log files, vendor shopping lists, unsourced regulatory claims. |
| `QUICK_FIX_REFERENCE.md` (230) · `9378447` | [development workflow](../implementation/02-development-workflow.md) troubleshooting | *Kept:* read the exact error, check the ports, regenerate Prisma. *Dropped:* deleting lockfiles (`:196`), killing processes broadly, API docs at `/api/docs` (`:139`; they are at `/docs`). |
| `QUICK_REFERENCE_LOGGING_SWAGGER.md` (179) · `3403e0a` | [API](api.md); [observability](observability.md) | *Kept:* the no-secrets rule and the contract-and-generated-client intent. *Dropped:* the duplicate content and hard-coded URLs. |
| `SWAGGER_COMPLETE_GUIDE.md` (802) · `3403e0a` | [API](api.md); OpenAPI microsteps in phase 0 | *Kept:* operation, DTO and error examples; contract export; client generation (`:22–26`, `:536–558`). *Dropped:* the idea that annotations validate responses, the stale URLs and line references, and the wrong security-scheme wiring. |
| `.lingma/plans/Football_Platform_Architecture_66b64a68.md` (1,137) · `d325b40` | [architecture](architecture.md); [database](database.md); ADRs | *Kept:* explicit tenant predicates (`:1042–1049`, which contradict the later rule), the storage port, module boundaries, the need for a queue (`:18–35`, `:428–547`). *Dropped:* starter instructions, week estimates, templates, local and public file storage, microservices without a measured need. |
| `.lingma/plans/Football_ERP_Platform_Implementation_be4464ba.md` (1,866) · `9378447` | phases 2–3; [traceability](traceability.md) | *Kept:* the permission-matrix intent and the scouting, finance, reporting and automation topics where the requirements support them (`:3–31`, `:1773–1835`). *Dropped:* "70–75% foundation", claims that modules exist, the eight-to-nine-week schedule. |
| `.lingma/rules/feature-implementation-standards.md` (782) · `3403e0a` | [conventions](../implementation/01-conventions.md); `AGENTS.md`; `.claude/rules/` | **Harmful and always on.** It told every AI session "NEVER manually add `tenantId` to queries - middleware handles it" (`:15`, `:27`); no such middleware exists, so an agent obeying it writes cross-tenant queries. *Kept:* typed boundaries, validation, UI consistency. *Dropped:* the rule file and the whole `.lingma/` folder. |

### Frontend

| File (lines) · last commit | Went to | Kept · dropped |
|---|---|---|
| `FEATURE_IMPLEMENTATION_TEMPLATE.md` (649) · `ac37f1c` | `.claude/rules/frontend.md`; [UI/UX](ui-ux.md) | *Kept:* typed API hooks, tenant-scoped query keys and cache clearing, form validation, loading/empty/error states, shared components (`:29–112`, `:512–555`). *Dropped:* hand-copied response types (the client is generated from the contract), "middleware proves authorization", arbitrary size limits. |
| `FRONTEND_IMPLEMENTATION.md` (372) · `ac37f1c` | [architecture](architecture.md); [UI/UX](ui-ux.md) | *Kept:* the feature/shared folder organisation. *Dropped:* "production-ready", lint-pass and auth-pass claims, and the description of client-selected tenant headers as harmless (`:254–278`). |
| `QUICK_START.md` (325) · `ac37f1c` | [development workflow](../implementation/02-development-workflow.md) | *Kept:* request inspection and cookie diagnosis. *Dropped:* Node 18, guessed tenant ids, the default port that collides with the API. |
| `README.md` (36) · `24529a1` | rewritten | The create-next-app boilerplate became a short page: what the app is, how to run it, where the plan lives. |
| `AGENTS.md` (5) · `24529a1` | rewritten | The Next.js block — "This is NOT the Next.js you know … read `node_modules/next/dist/docs/`" — is kept verbatim; routing to the plan was added. |
| `CLAUDE.md` (1) · `24529a1` | kept | Still `@AGENTS.md`. |

### Backend

| File (lines) · last commit | Went to | Kept · dropped |
|---|---|---|
| `BACKEND_IMPLEMENTATION_STANDARDS.md` (276) · `4d86978` | `.claude/rules/backend.md`; [conventions](../implementation/01-conventions.md); [architecture](architecture.md) | *Kept:* thin controllers, explicit application boundaries, DTOs, dependency direction (`:33–46`). *Dropped:* the mandatory `domain/` layer with interfaces for every entity (`:20`, `:75`), middleware scoping, cross-module repository exports, "every model has tenantId". |
| `README.md` (98) · `1cbf4cc` | rewritten | The NestJS starter README became a short page. *Dropped:* the starter badges and the framework's licence text — the app is `UNLICENSED` (`package.json:7`). |
| `build_output.txt` (11) · `6fdf03f` | — | A committed terminal dump of an old `$use` compile error; not today's build. Build failures belong in CI logs. |

---

## Why the status claims were not imported

Representative contradictions, each checked against the code on 28 September 2026:

| Legacy claim | What the code shows |
|---|---|
| middleware scopes every Prisma query | `prisma.service.ts:75–77` delegates scoping to each service; `:98–120` only stores context that nothing reads |
| session listing and revocation are delivered | `get-active-sessions.usecase.ts:29–41` synthesises a session; `revoke-session.usecase.ts:20–31` returns a limitation message |
| email only needs SMTP settings | `mail.service.ts:13–23` is a logging placeholder that writes token-bearing HTML to the log |
| logging is confidential and compliance-ready | `logging.interceptor.ts:24` logs raw URLs, query strings included |
| the operational modules are built | `players`, `contracts`, `training`, `legal`, `chat`, `notifications` are empty module declarations |
| route protection proves authentication | `frontend/proxy.ts:36–44` maps cookie presence to "authenticated" — a navigation aid, not a check |

## Live references repaired when the files were removed

| Repository | File | Change |
|---|---|---|
| all three | `.github/ISSUE_TEMPLATE/config.yml:4` | the "plan" link now points at `docs/implementation/README.md` instead of `IMPLEMENTATION_CHECKLIST.md` |
| umbrella | `CONTRIBUTING.md:10` | "the plan" now names `docs/implementation/` |
| umbrella | `.github/labeler.yml` | the `area: plan` label's globs for the legacy files (`AUTH_*.md`, `IMPLEMENTATION_*.md`, `*_GUIDE.md`, `QUICK_*.md`, `FEATURE_*.md`, `SWAGGER_*.md`, `LOGGING_*.md`, `.lingma/**`, `docs/plan/**`) became `docs/**` |
