# Master plan

The spine of the plan: what the requirements get right and wrong, where the code stands, the phases,
the effort, the risks, the decisions only the owner can make, and every place the plan
departs from the frozen requirements.

| Document | Answers |
|---|---|
| [`../requirements/`](../requirements/README.md) | **what** Sadara must be, and why — frozen |
| [`../adr/`](../adr/README.md) | the load-bearing **how** decisions, with the alternatives rejected |
| [`../reference/`](../reference/) | the contracts every microstep relies on |
| this folder | **what to build next**, in what order, exactly how, and how you know it worked |

Two independent authors produced this plan — Claude and Codex (GPT-6 Astra) — each from the four
requirement documents and a full audit of the three repositories, and then negotiated every
disagreement on evidence. The outcome of each contested point is recorded in the ADR it produced.

**A product built to sell (1 October 2026).** There is no client agency and no data yet: Sadara is built
to show sports agencies and to sell, then handed over in production. The first milestone is a sales
demo built as the real product, and [`demo-milestone.md`](demo-milestone.md) is the build order; the
questions this plan once left to "the agency" are product decisions, shipped as configurable defaults
([ADR-0021](../adr/0021-a-product-built-to-sell.md)).

---

## Verdict on the requirements

**Build on them.** The four documents are separated by purpose the way a professional delivery needs,
carry stable IDs from business objective to testable requirement, and get right the things a
player-management product usually gets wrong:

1. **Tenant isolation as defense in depth**, not a middleware flag (SYS-TEN-001…008).
2. **Confidential by default** — medical, legal-internal, compensation — and absent from search,
   exports, notifications and logs, not merely from screens (BR-RULE-02, BR-RULE-07, SR-MED-007).
3. **Workflow over free-form status** — contracts, tickets, enrollment and reports move through
   controlled, audited transitions (BR-RULE-03, BR-RULE-05).
4. **Honest scope** — a modular monolith first, AI only with a human in the loop, and an explicit list
   of what the schema does not yet model.

**They are a draft, with gaps.** Priority labels are not a release order; the medical workspace
appears in no release; several "current technology" paragraphs are assertions rather than
compatibility evidence; and signature sufficiency, retention, guardian authority, capacity and provider
choices are unanswered. Every departure and gap is in [errata and concordance](#errata-and-concordance);
every unanswered question is in the [OPEN register](#open-register) with the default the code follows
meanwhile.

---

## Where the code stands

**Pre-production: real foundations, broken flows, real holes.** Verified against the code on
28 September 2026 by independent audits of the backend, the frontend, the schema and the legacy
documents; nothing is taken from the legacy status documents, which claimed "95% complete, production
ready" for work that does not run. The full inventory, with evidence for every line and an owning
microstep for every defect, is [`../reference/current-state.md`](../reference/current-state.md).

| Area | State |
|---|---|
| Delivery flow | **Live** in all three repositories: branches, rulesets, five required checks, Dependabot, CodeQL, secret scanning, hooks — [`03-github-workflow.md`](03-github-workflow.md) |
| Schema | 29 models, 26 enums, six migrations; sound tenancy foundations with serious gaps — [`../reference/database.md`](../reference/database.md) |
| Backend | 53 routes. The local sign-in **does not work end to end** and hides exploitable defects behind the failure; medical and scouting are partial; players, contracts, legal, training, chat and notifications are **empty module shells**; the permission seed crashes, so every permission-guarded route answers 403; the production build does not start |
| Frontend | sign-in pages in front of routes that do not exist; `/` is the Next.js starter; **no internationalisation or RTL**; no tests |
| Quality | the backend builds and its one starter test passes; lint is not yet a gate (748 backend problems, 21 frontend); npm audit is clean and gated in both applications |

**The defects that make Phase 0 non-negotiable** (the complete list is in current-state):

| Defect | Evidence | Owner |
|---|---|---|
| Tokens can be forged: the signing key falls back to the literal `'default-secret'` | `auth.module.ts:35`, `jwt.strategy.ts:36` | `0.1.5`, `0.1.6` |
| Reset and verification links, whole emails and — in the browser — passwords are written to logs | `mail.service.ts:21–22`, `logging.interceptor.ts:24`, `api-client.ts:64–70` | `0.1.4` |
| Anyone can register with any role, `SUPER_ADMIN` included | `register.dto.ts:40–46`, `register.usecase.ts:45` | `0.1.6` |
| Sign-in resolves every tenant to the literal `'default-tenant'`; refresh reads a body the browser never sends; sessions and revocation are placeholders; 2FA is never asked for and stored in plaintext | `auth.controller.ts:117, 200–204, 358`; `enable-2fa.usecase.ts:24–27` | `0.1.6` (retired) → `0.5.5`–`0.5.8` (rebuilt on OIDC) |
| No database tenant enforcement; six foreign keys can cross tenants | `prisma.service.ts:98–120`; `schema.prisma:638, 756, 834, 975, 1287, 1358` | `0.4.3`–`0.4.5` |
| Authorization fails open for routes that declare nothing; the permission seed crashes | `roles.guard.ts:27`; `permission.service.ts:46–54` | `0.6.1`, `0.6.2` |
| A player can read any medical record; a scout can approve their own report; reports expose the player's passport | `permission.service.ts:227`; `update-scouting-report.dto.ts:8`; `scouting-report.repository.ts:56` | `0.6.8` (medical); `1.11.1`, `1.11.3` (scouting, released by `1.11.7`) |
| Audit is an ordinary, deletable table written through a queue | `schema.prisma:1361`; `event.service.ts:37` | `0.7.1`, `0.7.2` |

---

## Phase map

| Phase | Delivers | Ends when the agency can… | BRD release |
|---|---|---|---|
| [**0 — Foundation & hardening**](phase-0-foundation.md) | the local sign-in retired and rebuilt on an external identity provider; tenant transactions under row-level security; deny-by-default authorization with confidential projections; append-only audit, outbox and worker; the private file pipeline with scanning; the API contract; the bilingual shell; runtimes, harnesses and local recovery | …trust that nothing existing leaks or can be abused, and that every feature has rails to land on | enabler |
| [**1 — MVP**](phase-1-mvp.md) | tenant and user administration; players (360, completeness, organisations and club history, documents, media); contracts (lifecycle, representation agreements, immutable versions, approvals bound to a version, signature evidence under an adopted policy, expiry reminders); **scouting** (moved from Phase 3); legal tickets with SLA; notifications; audit search and timeline; search and dashboards; exports; **the first sales demo**; **production launch for the first tenant** | …run its player, contract, scouting and legal work in production, in Arabic and English | R1 |
| [**2 — Operations**](phase-2-operations.md) | medical and rehabilitation; training, sessions, enrollment, attendance, certificates; performance records and imports; versioned rating schemes; chat on a realtime process; push; media processing; job-based imports and exports; department dashboards | …run training, medical and performance in the platform | R2 |
| [**3 — Intelligence**](phase-3-intelligence.md) | clubs, competitions and matches; dossiers and a sharing portal; finance; e-signature provider integration; scheduled reports; mobile readiness | …recruit and present players to clubs from the platform | R3 |
| [**4 — Scale**](phase-4-scale.md) | platform operators and audited support access; tenant onboarding and entitlements; integrations and webhooks; governed AI assistance; capacity, upgrade and recovery at scale | …onboard a second agency without a code change | R4 |

**Why this order.** Phase 0 front-loads what cannot be retrofitted once real data exists — tenancy in
the database, audit immutability, money, dates, identity — and replaces a broken sign-in instead of
repairing it. Phase 1 ends in production, because a release no real user has run has not been tested
by one. Medical waits for Phase 2, behind a proven confidentiality framework; the partial medical code
stays in the tree, quarantined until then, and the partial scouting code until its rebuild replaces it.

**The build order is the [demo milestone](demo-milestone.md).** The phases still say what each release
contains; the milestone says what to build first ([ADR-0021](../adr/0021-a-product-built-to-sell.md)):
78 Phase-0 steps through the **foundation gate** (`0.11.0`), then 46 Phase-1 steps — the features a
pitch shows, scouting, and the demo itself (`1.12.1`–`1.12.3`). The **production gate** (`0.11.1`),
legal tickets, exports and production readiness follow, before anything is hosted for real users.

---

## Effort model

**Engineering hours, not calendar promises.** Assume one experienced TypeScript developer with AI
agents, **25 focused delivery hours a week** after operations and review, and add an explicit **30%
reserve** for integration and rework. Every microstep carries a size — **S ≤ 4 h, M ≤ 8 h, L ≤ 16 h**;
anything larger is split before it starts. Sizes are ceilings, so the honest estimate is a range from
half the weighted total to the full total. Do **not** divide by an assumed AI speed-up: measure it.

| Phase | Microsteps | S · M · L | Hours before reserve | With 30% reserve, at 25 h/week |
|---|---:|---|---:|---:|
| 0 | 83 | 22 · 50 · 11 | 332–664 | 17–35 weeks |
| 1 | 77 | 0 · 22 · 55 | 528–1056 | 27–55 weeks |
| 2 | 44 | 0 · 13 · 31 | 300–600 | 16–31 weeks |
| 3 | 22 | 0 · 5 · 17 | 156–312 | 8–16 weeks |
| 4 | 25 | 0 · 3 · 22 | 188–376 | 10–20 weeks |
| **All** | **251** | 22 · 93 · 136 | 1504–3008 | 78–156 weeks |
| *[Demo milestone](demo-milestone.md)* | *124 (7 done)* | *20 · 53 · 44 left* | *604–1208 left* | *31–63 weeks by this model; about 19 at the measured pace* |

Phase 0's sizes were set step by step against the code; the later phases were sized conservatively —
almost every full-stack step as L — and will come down as their phase-entry refinement splits and
re-sizes them. Treat the upper figures as a capacity bound, not a forecast.

**Make it falsifiable.** From the first microstep, record active hours, elapsed days, review and rework
time and the cause of any wait in each PR. The first measurement, on 1 October 2026, is in the [demo
milestone's forecast](demo-milestone.md#forecast-and-checkpoints): four steps at a median of 0.3 of their
ceilings — thin evidence, re-forecast at every checkpoint. After five completed steps, and weekly from then:
*remaining forecast = remaining weighted size × (median actual hours ÷ weight) × observed reserve ÷
actual weekly capacity.* If the median runs above 1.5× the weights, or two weeks deliver under 60% of
planned capacity, re-forecast the phase and reduce scope only by the owner's decision. Waiting on
owner decisions, providers or hosting is queue time, not effort — it is in the [long-lead
register](#long-lead-register), not in these numbers.

---

## Risk register

| Risk | Trigger — observable | Response · owner |
|---|---|---|
| **A cross-tenant leak** | any foreign-id response, count, job or file path succeeds; the runtime role bypasses RLS | stop exposure, reproduce, fix, add the case to the isolation suite · `0.4.5`, `0.6.9` |
| **Confidential data in the wrong place** | a medical, legal or finance canary appears in an ordinary response, log, export, cache or notification | disable the surface, investigate copies, fail the release · `0.6.4`, `0.10.2` |
| **Identity provider not ready for production** | the production provider is undecided at the hosting decision, or cannot meet the revocation, MFA or residency criteria | real users wait; development and staging continue on Keycloak · `1.10.1` |
| **A contract marked signed without sufficient evidence** | a transition to `SIGNED` without an approved evidence policy, or evidence whose hash does not match the approved version | keep `APPROVED`; no production signing until the owner approves an evidence policy (ADR-0019) · `1.4.5` |
| **Data migration loss** | the preflight finds mismatches or timestamps of unknown provenance; a backup does not restore | stop, get an owner-approved mapping, never delete to make a constraint pass · `0.4.1`, `0.10.3` |
| **Lost or duplicated async work** | the oldest pending outbox event exceeds its alert threshold; a retry changes a business outcome | stop replay, reconcile by dedup keys and provider state · `0.7.5`, `0.7.6` |
| **A missing test gives a false green** | an empty suite, a skipped named test, a stale configuration | the gate fails; fix the harness · `0.1.3`, `0.2.3` |
| **AI-written code drifts from the conventions** | a convention violated in a merged PR | turn the convention into a CI check; path-scoped agent rules · `0.1.2`, `0.2.5` |
| **Solo overload, bus factor** | measured cycle time above 1.5× the weights; two weeks under 60% of capacity | re-forecast, split, move approved scope; this documentation and the restore-from-runbook drill · every gate |
| **A buying agency's requirements differ from the product defaults** — signature evidence, retention, minors, medical, approval chains | a prospect's policy, contract or jurisdiction needs something the defaults do not do | configure it per tenant where the steps allow; anything beyond configuration becomes an erratum or a microstep, scoped and priced with the sale · owner |
| **Scope creep from the four-release vision** | a PR with no microstep reference | a new ask becomes an erratum or a later microstep, never an unplanned branch · weekly |
| **The demo date slips** | a checkpoint forecast passes 26 weeks for the [demo milestone](demo-milestone.md) | cut from the milestone in the order of its cut list, by the owner's decision; never cut a foundation step, a test or an invariant · owner, at each checkpoint |
| **Dependency churn** — Next.js, NestJS, Prisma, TypeScript, ESLint majors | a major release, or a Dependabot PR whose `test` is red | grouped monthly Dependabot; majors one at a time, migration notes read, the app exercised; a major the toolchain cannot support yet is held in `dependabot.yml` with its blocking error quoted (TypeScript 7, ESLint 10, NestJS 12) and moved by a planned step (`0.2.9` for the backend) as soon as it can; a red Dependabot PR is never merged through the bypass; a monthly currency review keeps the SysRD's stack current ([ADR-0022](../adr/0022-the-sysrd-stack-kept-current.md)) · monthly |
| **Unstaffed reliability target** | a restore misses its RPO/RTO; a critical alert goes unacknowledged | delay the release, revise operating support, repeat the drill · `1.10.12`, `1.10.13` |

---

## Long-lead register

Queue time, not effort. **Start** is when the request goes out; the default holds until the answer
arrives.

| Start | Question or artifact | Latest safe point | Default while waiting |
|---|---|---|---|
| Phase 1 | Before the first sale: the buying agency's own policies — signature evidence, retention, approval chains — adopted in its tenant over the product defaults ([ADR-0021](../adr/0021-a-product-built-to-sell.md)) | the sale | the product defaults, labeled as defaults |
| Before Phase 2 | The owner, with a medical advisor: who may see medical records, player and guardian consent, hosting region — the product's default medical policy | Phase 2 medical entry | medical stays quarantined |
| Before `1.12.3` | The owner rehearses the demo and reviews every Arabic screen | `1.12.3` | the demo is not shown |
| Before `1.10.1` | The small server: provider, region and size, chosen by the owner when renting it — the first hosting target ([ADR-0021](../adr/0021-a-product-built-to-sell.md)); managed PostgreSQL 18 and storage remain the alternative | `1.10.1` | local only; staging and the hosted demo wait |
| Phase 1 start | Email provider and sending domain (SPF, DKIM, DMARC) | `1.6.3` | Mailpit only |
| Phase 1 | The owner: retention per record class, legal hold (legal advice optional) | `1.3.4` | archive only; nothing is purged |
| Phase 1 | A native-speaker Arabic review; representative users | `1.10.15` | Arabic ships reviewed by the team only |
| Phase 1, before launch | An independent security review against ASVS Level 2 | `1.10.14` | launch waits |

---

## OPEN register

One shape for every open question: **the question · the default the code follows meanwhile · the
owning microstep · what settles it.** A default is what the code does, not an answer, and elapsed time
never turns a default into a decision. When an item is settled, record the date, the person, the
evidence and the affected requirement and test IDs here, and update the owning microstep.

| # | Question | Default meanwhile | Owner | Settled by |
|---|---|---|---|---|
| OPEN-01 | Which identity provider runs in production — self-hosted Keycloak or a managed provider — and in which region? | Keycloak in development and staging; the first production target is self-hosted Keycloak on the small server ([ADR-0021](../adr/0021-a-product-built-to-sell.md)) | `1.10.1` | the owner, when renting the server, with the provider's MFA, recovery, revocation and residency evidence |
| OPEN-02 | Session lifetimes and the provider-change exposure window | idle 30 min, absolute 12 h; provider-side changes apply at the next back-channel event or session expiry; offboarding is done in Sadara, which is immediate | `0.5.6`, `0.5.7` | **decided as the product default (ADR-0021, 1 October 2026)**; a buying agency may require stricter limits |
| OPEN-03 | What evidence makes a contract signed; who may sign; contracts with minors | evidence may be collected; `SIGNED` requires a tenant whose owner has adopted an evidence policy | `1.4.5` | **decided 1 October 2026 (ADR-0021): [ADR-0019](../adr/0019-owner-approves-signature-policy.md)'s default ships as the product default**; each agency's owner adopts or tightens it for its tenant, and the demo agencies adopt the default; a lawyer's review stays optional |
| OPEN-04 | Who owns the medical workflow; its purposes, permitted recipients and summaries; where medical data may be hosted and on what legal basis | medical quarantined; no clinical narrative outside the medical workspace; no automated return-to-play | Phase 2 medical entry | the owner and a named medical lead — a lawyer's review optional (owner, 29 September 2026) |
| OPEN-05 | Child protection: how minors, guardians and a player's own access are verified and scoped | no inferred guardian permission; links inactive until verified; minors' data confidential by default | `0.6.5`, `1.2.3` | **decided as the product default (ADR-0021)**, within FIFA's rules on minors; a buying agency adopts its own policy |
| OPEN-06 | Retention per record class, erasure, legal hold, archival PDF/A | archive, never purge; no retention period invented | `1.3.4` | the owner (legal advice optional) |
| OPEN-07 | Legal SLA: business hours, pauses, holiday calendar | elapsed-time deadlines in the tenant's zone, visible and manually overridable | `1.5.2` | **decided as the product default (ADR-0021)**; each agency configures its calendar |
| OPEN-08 | The real capacity envelope | 1 tenant · 50 members · 500 players · 20,000 documents · 200 GB media — the design target for one small server | `1.10.6` | **decided as the design target (ADR-0021)**; revisited with the first customer's volumes |
| OPEN-09 | Rounding, settlement, exchange rates, tax and the payment provider | **currencies decided 29 September 2026 (owner): every active ISO 4217 currency**, each with its official decimals; the tenant's default is JOD; no real payments yet; amounts in different currencies are never added without a recorded exchange rate; unknown settlement is unresolved, never paid | `0.4.7`, Phase 3 finance | the owner: the exchange-rate source, settlement and tax rules, the payment provider |
| OPEN-10 | Permitted AI uses, providers, data disclosure and evaluation thresholds | AI disabled | Phase 4 AI governance | the owner, domain leads and a privacy review, with evaluation results |
| OPEN-11 | Does any database hold real data, and of what provenance? | **closed 1 October 2026: no database anywhere holds real data (owner)** — databases may be dropped and reseeded until the first customer; `0.4.1` still reports integrity violations, without owner-approved mappings | `0.4.1` | settled ([ADR-0021](../adr/0021-a-product-built-to-sell.md)) |
| OPEN-12 | Email and push channels, sender identity, mandatory notices, device policy | in-app notifications and Mailpit; push off; no confidential content in any message | `1.6.3` | the owner and the provider's deliverability setup |
| OPEN-13 | One current season per tenant, or parallel competition seasons? | one current season per tenant (`0.4.10`) | `1.2.1` | **decided as the product default (ADR-0021)** |
| OPEN-14 | Do coaching contracts need subjects other than players? Is the agency's own representation agreement a contract type, and who is the counterparty? | player contracts and **REPRESENTATION**, whose counterparty is the tenant's agency organization; coaching disabled until a reviewed model extension | `1.4.1` | **decided 1 October 2026 (ADR-0021)** |
| OPEN-15 | Do watchlists include external prospects, and are they shared among staff? | private lists of existing players and prospects; sharing is an explicit authorized resource; prospect conversion explicit | `1.11.4` | **decided as the product default (ADR-0021)** |
| OPEN-16 | Is break-glass emergency access needed, and who approves it? | disabled; scoped, time-boxed support grants only, never self-approved | Phase 4 support access | the owner, with a security review |
| OPEN-17 | The default role matrix and approval chains | the seeded defaults in [`../reference/security-privacy.md`](../reference/security-privacy.md) | `1.1.5` | **decided as the product default (ADR-0021)**; per-tenant customization is later work |
| OPEN-18 | The licence of the code | **decided 29 September 2026 (owner): proprietary, all rights reserved** — `LICENSE` in all three repositories, `UNLICENSED` in both `package.json` files. The repositories stay publicly *visible*: GitHub's terms let anyone view and fork a public repository on GitHub, and only a private repository stops that | — | settled; versions published earlier under GPL-3.0 keep that licence for those versions |

---

## Errata and concordance

The requirement documents are frozen ([`../requirements/README.md`](../requirements/README.md)).
Where the plan departs from them or fills a gap, the entry is here; the frozen text stays as written,
and the right-hand columns are what the code implements.

| # | Requirement | Says or omits | The plan | Why · owner |
|---|---|---|---|---|
| E-01 | BRD §13, PRD-ME-001, SR-MED-* | medical is in scope and in no release | Phase 2, quarantined until then; denial tests from Phase 0 | needs the confidentiality framework first · `0.1.8`, Phase 2 |
| E-02 | SysRD §2 vs SR-AUTH-001 | an OIDC provider in the architecture; either OIDC or application-managed in the SRS | external OIDC; the local credential system is retired, not repaired | [ADR-0002](../adr/0002-identity-oidc.md) · `0.1.6`, `0.5.1`–`0.5.8` |
| E-03 | the "current technology" paragraphs; SysRD §2 | version and support claims asserted, not evidenced | the lockfiles and `.nvmrc` govern; PostgreSQL 18 is qualified by an executed replay; the SysRD's versions are floors, and newer stable releases are preferred | [ADR-0013](../adr/0013-postgresql-18.md) · [ADR-0022](../adr/0022-the-sysrd-stack-kept-current.md) · `0.2.2` |
| E-04 | SYS-TEN-005 | "consider" RLS for the highest-risk tables once patterns are validated | RLS forced on **every** tenant-owned table in Phase 0 | the audit found no database enforcement at all · `0.4.5` |
| E-05 | SR-CORE-006, UX-007 | "store timestamps in UTC" | civil `DATE` for birthdays and contract days; `timestamptz` for instants; IANA zones for schedules | a birthday is not an instant · `0.4.8` |
| E-06 | SR-CT-005, SR-TR-006 | amounts and currencies, without scale, rounding or settlement | `NUMERIC(19,4)` with the currency's exponent enforced on payable amounts; settlement in Phase 3 | JOD has three decimals · `0.4.7` |
| E-07 | BR-RULE-04, SR-CT-008 vs SR-CT-011 | signed means "meets the configured signature policy"; provider integration is P1 | `SIGNED` only under an approved evidence policy; an approved manual method may satisfy SR-CT-008; **SR-CT-011 (provider integration) is deferred to Phase 3** | the owner has not yet approved a policy ([ADR-0019](../adr/0019-owner-approves-signature-policy.md)); the provider waits for it · `1.4.5`, Phase 3 |
| E-08 | SR-DOC-004 (P1) | malware scanning "supported" | scanning in Phase 0; an unscanned file cannot be used or downloaded | unsafe files cannot be made safe later · `0.8.4` |
| E-09 | SR-ACL-002, SysRD player link | a tenant-unique email | `Identity(issuer, subject)` plus tenant memberships; email never links an identity | email is contact data · `0.5.3` |
| E-10 | SR-AUD-007, BR-RULE-11 | recoverability, retention and legal hold | archive; no scheduled purge until a retention policy exists; audit has its own stricter retention | the rules conflict without a policy · OPEN-06 |
| E-11 | SR-NFR-PERF-001 | p95 targets without a capacity envelope | a provisional envelope, declared hardware and mix, falsified by load tests | the target is unmeasurable without one · `1.10.6` |
| E-12 | SysRD §7.10, SR-RT-004 | ratings versioned against schemes | existing scores are labelled with a legacy scheme; no historical weights are invented | provenance cannot be recovered · Phase 2 |
| E-13 | SR-CT-002, SR-CT-004 | no counterparty; no representation agreement type | an `Organization` counterparty and a `REPRESENTATION` type — **confirm with the agency** | a contract has two parties · `1.4.1`, OPEN-14 |
| E-14 | SR-DB-002 | UUIDs; v7 "may" be used where justified | v4 by default; v7 for high-ingest append tables | as written · `0.4.11` |
| E-15 | (gap) onboarding | unrestricted registration excluded (BRD §6); no onboarding defined | provisioning command and invitations | a closed product needs a way in · `0.5.9`, `0.5.10` |
| E-16 | (gap) guardians | a guardian persona with no relation to a player | explicit, scoped, verified guardian links | cannot authorize without one · `0.6.5`, `1.2.3` |
| E-17 | (gap) bilingual data | UI localisation only | Arabic and Latin-script names on players and organisations; Arabic-normalised search | typing "Mohammad" must find "محمد" · `1.2.1`, `1.2.4` |
| E-18 | (gap) home-dashboard tasks | the BRD names tasks; no requirement defines them | actions derived from workflow state; a task entity waits for demand | · `1.8.2` |
| E-19 | the standards references | ASVS, OWASP API Top 10, ISO 27001/27701, WCAG listed | verification targets with evidence per release; never a compliance claim | the owner settles applicability, with legal advice if wanted · `1.10.7`, `1.10.8`, `1.10.14` |
| E-20 | the legacy documents | "never filter by tenant — middleware does it"; "HttpOnly prevents CSRF"; "fake revocation is fine for an MVP"; "delete the lockfile" | all superseded | [`../reference/consolidation.md`](../reference/consolidation.md) · `0.1.1` |
| E-21 | SR-AUTH-003 | refresh tokens rotate and are revocable per device | no refresh tokens: the provider's token is never stored; an opaque, database-checked application session per device is rotated and revocable instead | [ADR-0003](../adr/0003-browser-sessions.md) · `0.5.6`, `0.5.7` |
| E-22 | SR-DOC-008 | PDF/A archival copies "where required by document policy" | delivered with dossier generation in Phase 3; no earlier policy requires it | revisit if the retention policy (OPEN-06) requires archival copies sooner · `3.3.1` |
| E-23 | SR-TR-006 | training price and payment status | Phase 2 records payment *observations*; verified settlement arrives with Phase 3 finance | an operational "paid" flag is not settlement evidence · Phase 2, Phase 3 |
| E-24 | SR-AUTH-008 | passkeys as a future factor without an API change | the provider offers them from `0.5.1`; the journeys are qualified in Phase 4 | a provider capability is not an accepted journey · `4.2.2` |

---

## Deferred requirements

Requirement IDs that no microstep owns, each with its reason. The plan check fails for any other
unowned ID. The target is an empty table.

<!-- plan:deferred:begin -->
<!-- plan:deferred:end -->

---

## Product definition of done

Each item is a passing test, a signed checklist or a named reviewer — **never an intention**.

1. **Tenants are isolated.** The two-tenant suite covers every route, job and file path, raw SQL as the
   runtime role returns nothing across tenants, and both pass (SR-NFR-SEC-003).
2. **Confidential data stays confidential.** For every confidential field, a test against an independent
   classification proves it absent for every role without the permission — in responses, search,
   exports, notifications and logs.
3. **Workflows are controlled.** No endpoint writes a workflow status directly; every transition is
   audited (BR-RULE-03).
4. **Evidence cannot be edited.** The database refuses `UPDATE`, `DELETE` and `TRUNCATE` on audit and
   on immutable evidence, for every role.
5. **Arabic and English are equivalent.** Every P0 journey passes in both, RTL and LTR, under axe and a
   keyboard walk-through.
6. **The contract holds.** The deployed API matches the committed OpenAPI document.
7. **Data survives.** A restore into a clean staging environment, performed from the runbook by someone
   who did not write it, meets the approved RPO and RTO — identity configuration and keys included
   (`1.10.13`).
