# Progress

One row per microstep, in plan order. **This file is the only place a status changes.**

| Status | Means |
|---|---|
| `todo` | not started |
| `in-progress` | a branch or PR exists; remaining acceptance is in the PR |
| `blocked` | cannot proceed — the evidence cell says by what (an OPEN item, an environment, another step) |
| `done` | merged **and** its Done-when held: the evidence cell cites the merged PR (both PRs for a two-repository step) |
| `superseded` | retired by a split or a replan; its replacement is named in the phase file |

**Rules.** A step is `done` only when every dependency is `done`, its PR is merged, and every test on its
**Tests** line exists — and is not skipped — in the application it changes, at the commit the umbrella
pins. "Verified locally" is `in-progress`, never `done`. Statuses change in the umbrella PR that moves
the pins (see [`03-github-workflow.md`](03-github-workflow.md#the-umbrella-pins-and-progress)); run
`just plan` afterwards to regenerate the frontier, the test catalog and the traceability table, and
`just check` before pushing. The Title and Repo columns are copied from the phase files by `just plan`;
edit only Status and Evidence.

<!-- plan:progress:begin -->
| Step | Title | Repo | Status | Evidence |
|---|---|---|---|---|
| 0.1.1 | The documentation set lands; the legacy documents are retired | umbrella + backend + frontend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/19 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/20 · https://github.com/OmarSweiti/Players_Platform/pull/6 |
| 0.1.2 | Agent entry files and scoped rules | umbrella + backend + frontend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/19 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/20 · https://github.com/OmarSweiti/Players_Platform/pull/6 |
| 0.1.3 | The plan checks itself in CI | umbrella | done | https://github.com/OmarSweiti/Players_Platform/pull/6 |
| 0.1.4 | Stop secrets and personal data reaching logs and error responses | backend + frontend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/43 · https://github.com/OmarSweiti/Players_Platform_Backend/pull/45 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/38 |
| 0.1.5 | Refuse to boot without real configuration | backend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/44 |
| 0.1.6 | Retire the local credential system | backend | todo |  |
| 0.1.7 | Retire the local sign-in pages | frontend | todo |  |
| 0.1.8 | Quarantine unfinished modules behind server-side flags | backend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/46 |
| 0.2.1 | The local stack: PostgreSQL 18, S3-compatible storage, Valkey, ClamAV, Mailpit, Keycloak | umbrella + frontend | done | https://github.com/OmarSweiti/Players_Platform/pull/11 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/31 |
| 0.2.2 | PostgreSQL 18 in CI and in the replay recipe | backend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/31 |
| 0.2.3 | The API test harness on a real database | backend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/39 |
| 0.2.4 | The web test harness: Vitest, Testing Library, MSW, Playwright in Arabic and English, axe | frontend | done | https://github.com/OmarSweiti/Players_Platform_Frontend/pull/23 |
| 0.2.5 | Lint and format gates in both applications | backend + frontend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/32 · https://github.com/OmarSweiti/Players_Platform_Backend/pull/33 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/22 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/27 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/29 |
| 0.2.6 | A production build that starts, in a container | backend | todo |  |
| 0.2.7 | Declared dependencies only; one naming scheme | backend + frontend | todo |  |
| 0.2.8 | Integration and end-to-end tests in CI | backend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/41 |
| 0.2.9 | NestJS 12, TypeScript 6 and an ES-module test setup, together | backend | todo |  |
| 0.2.10 | Module boundaries, checked from the first module | backend + frontend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/47 · https://github.com/OmarSweiti/Players_Platform_Frontend/pull/39 |
| 0.3.1 | One error format: RFC 9457 problem details | backend | todo |  |
| 0.3.2 | Strict validation, registered once | backend | todo |  |
| 0.3.3 | Versioned routes under /api/v1 | backend + frontend | todo |  |
| 0.3.4 | One success envelope, registered once | backend | todo |  |
| 0.3.5 | Cursor pagination and allowlisted filters | backend | todo |  |
| 0.3.6 | Optimistic concurrency: revisions, ETag, If-Match | backend | todo |  |
| 0.3.7 | Liveness and real readiness | backend | todo |  |
| 0.3.8 | Rate limits by category, shared through Valkey | backend | todo |  |
| 0.3.9 | The committed OpenAPI contract and the breaking-change check | backend | todo |  |
| 0.4.1 | Preflight: report every integrity violation before constraining anything | backend | todo |  |
| 0.4.2 | Database roles: owner, migrator, runtime | backend + umbrella | todo |  |
| 0.4.3 | Explicit tenant context and the tenant transaction | backend | todo |  |
| 0.4.4 | Composite and same-parent foreign keys | backend | todo |  |
| 0.4.5 | Row-level security on every tenant-owned table; tenant ids immutable | backend | todo |  |
| 0.4.6 | Tenant-leading indexes; duplicate indexes dropped | backend | todo |  |
| 0.4.7 | Money: NUMERIC(19,4) with currency rules | backend | todo |  |
| 0.4.8 | Calendar dates, instants and tenant time zones | backend | todo |  |
| 0.4.9 | Normalised emails; lifetime uniqueness with audited reactivation | backend | todo |  |
| 0.4.10 | Integrity constraints in SQL: checks, partial uniques, safe defaults, bounded JSON | backend | todo |  |
| 0.4.11 | UUIDv7 for high-ingest tables | backend | todo |  |
| 0.4.12 | The existing modules on the tenant transaction | backend | todo |  |
| 0.5.1 | The Keycloak realm as code | umbrella | todo |  |
| 0.5.2 | Resolve the tenant from the host | backend | todo |  |
| 0.5.3 | Identities, memberships and sessions in the schema | backend | todo |  |
| 0.5.4 | The identity-provider port and the Keycloak adapter | backend | todo |  |
| 0.5.5 | Sign-in through the API: authorization code with PKCE | backend | todo |  |
| 0.5.6 | Server sessions, the session cookie and CSRF | backend | todo |  |
| 0.5.7 | Sign-out, back-channel logout and session management | backend | todo |  |
| 0.5.8 | MFA assurance for privileged roles; recent authentication for sensitive actions | backend | todo |  |
| 0.5.9 | The tenant provisioning command | backend | todo |  |
| 0.5.10 | Invitations | backend | todo |  |
| 0.5.11 | Development identities and the synthetic seed | backend + umbrella + frontend | todo |  |
| 0.6.1 | The permission catalog is code; the seed cannot crash | backend | todo |  |
| 0.6.2 | Deny by default: every route declares its permission | backend | todo |  |
| 0.6.3 | Object policies in the use cases | backend | todo |  |
| 0.6.4 | Confidential projections, checked against an independent classification | backend | todo |  |
| 0.6.5 | Player-account and guardian relationships | backend | todo |  |
| 0.6.6 | Effective permissions for the web app | backend | todo |  |
| 0.6.7 | No implicit platform access | backend | todo |  |
| 0.6.8 | The existing medical routes obey the rules | backend | todo |  |
| 0.6.9 | The two-tenant isolation suite over every route | backend | todo |  |
| 0.7.1 | Audit evidence is append-only in the database | backend | todo |  |
| 0.7.2 | Audit inside the business transaction, redacted; a failed audit aborts the change | backend | todo |  |
| 0.7.3 | Security events that have no tenant | backend | todo |  |
| 0.7.4 | Access audit for confidential reads | backend | todo |  |
| 0.7.5 | The transactional outbox and the consumer inbox | backend | todo |  |
| 0.7.6 | The worker process, with tenant-safe job discovery | backend + umbrella | todo |  |
| 0.7.7 | Idempotency keys for retried commands | backend | todo |  |
| 0.7.8 | Transactional email with honest delivery semantics | backend | todo |  |
| 0.8.1 | The storage port and an S3 adapter; local-disk storage removed | backend | todo |  |
| 0.8.2 | File objects and upload sessions | backend | todo |  |
| 0.8.3 | Upload: authorize, presign into quarantine, finalize with content checks | backend | todo |  |
| 0.8.4 | Scan, then promote to an immutable version | backend + umbrella | todo |  |
| 0.8.5 | Download: version-pinned, authorized, short-lived | backend | todo |  |
| 0.9.1 | The route map | frontend | todo |  |
| 0.9.2 | Arabic and English, RTL and LTR | frontend | todo |  |
| 0.9.3 | Logical CSS and bidirectional isolation | frontend | todo |  |
| 0.9.4 | A typed client generated from the contract, on the same origin | frontend | todo |  |
| 0.9.5 | Sessions in the browser | frontend | todo |  |
| 0.9.6 | The application shell | frontend | todo |  |
| 0.10.1 | Structured logs with request correlation | backend | todo |  |
| 0.10.2 | Redaction by allowlist, proven by canaries | backend | todo |  |
| 0.10.3 | Local backup and restore, drilled | umbrella + backend | todo |  |
| 0.10.4 | Failure drills: worker crash, database loss, storage loss | backend | todo |  |
| 0.11.0 | The foundation gate: what every product feature builds on | umbrella + backend + frontend | todo |  |
| 0.11.1 | Run the Phase-0 production gate and record the evidence | umbrella + backend + frontend | todo |  |
| 1.1.1 | Users: list, invite, deactivate and change role | backend | todo |  |
| 1.1.2 | Tenant settings and private branding | backend + frontend | todo |  |
| 1.1.3 | Own profile, locale and identity security links | backend + frontend | todo |  |
| 1.1.4 | Per-tenant release flags | backend | todo |  |
| 1.1.5 | The permission matrix, visible | backend + frontend | todo |  |
| 1.1.6 | The user administration workspace | frontend | todo |  |
| 1.1.7 | Keycloak Arabic and English journey theme | umbrella + frontend | todo |  |
| 1.1.8 | Private membership avatars | backend + frontend | todo |  |
| 1.2.1 | The player record and lifecycle | backend | todo |  |
| 1.2.2 | Organizations and club history | backend | todo |  |
| 1.2.3 | Player and guardian account workspace | backend + frontend | todo |  |
| 1.2.4 | Player directory, search and filters | backend + frontend | todo |  |
| 1.2.5 | Profile completeness by lifecycle stage | backend + frontend | todo |  |
| 1.2.6 | Duplicate detection before player creation | backend + frontend | todo |  |
| 1.2.7 | Player 360 | frontend | todo |  |
| 1.2.8 | Player creation, editing and archive forms | frontend | todo |  |
| 1.3.1 | Typed document ownership and legacy URL retirement | backend | todo |  |
| 1.3.2 | Document scan operations and recovery | backend + frontend | todo |  |
| 1.3.3 | Player images and private media bindings | backend + frontend | todo |  |
| 1.3.4 | Retention classification and hold-aware cleanup | backend | todo |  |
| 1.3.5 | Shared document upload and history component | frontend | todo |  |
| 1.4.1 | Contracts: counterparties, terms and current version | backend | todo |  |
| 1.4.2 | The contract state machine | backend | todo |  |
| 1.4.3 | Drafting and immutable version commands | backend | todo |  |
| 1.4.4 | Expiry monitoring and reminders | backend | todo |  |
| 1.4.5 | Signature evidence under an approved manual policy | backend | todo |  |
| 1.4.6 | Termination | backend + frontend | todo |  |
| 1.4.7 | The contract workspace | frontend | todo |  |
| 1.4.8 | Immutable contract versions and file migration | backend | todo |  |
| 1.4.9 | Ordered approval rounds and immutable decisions | backend | todo |  |
| 1.4.10 | Draft editor, version history and approval actions | frontend | todo |  |
| 1.5.1 | Ticket schema and state machine | backend | todo |  |
| 1.5.2 | SLA and overdue monitoring | backend | todo |  |
| 1.5.3 | Notes, internal notes and attachments | backend | todo |  |
| 1.5.4 | The legal queue and requester journey | frontend | todo |  |
| 1.5.5 | Ticket commands and assignment API | backend | todo |  |
| 1.5.6 | Legal on the shared surfaces: Player 360, timeline, search and dashboards | backend + frontend | todo |  |
| 1.6.1 | Templated, localized, tracked notifications | backend | todo |  |
| 1.6.2 | The notification center | backend + frontend | todo |  |
| 1.6.3 | Production email provider and preferences | backend | todo |  |
| 1.6.4 | Notification preference controls | frontend | todo |  |
| 1.7.1 | Restricted audit search API | backend | todo |  |
| 1.7.2 | The permission-filtered player timeline | backend | todo |  |
| 1.7.3 | Audit investigation workspace | frontend | todo |  |
| 1.8.1 | Authorized global search API | backend | todo |  |
| 1.8.2 | The home dashboard | backend + frontend | todo |  |
| 1.8.3 | The executive summary | backend + frontend | todo |  |
| 1.8.4 | Global search interaction | frontend | todo |  |
| 1.9.1 | Permission-gated, audited export jobs | backend | todo |  |
| 1.9.2 | Export progress and download interface | frontend | todo |  |
| 1.10.1 | Hosting, provider operation and residency decision | umbrella | todo |  |
| 1.10.2 | Reproducible application images | umbrella + backend + frontend | todo |  |
| 1.10.3 | Production secrets and configuration lifecycle | umbrella + backend | todo |  |
| 1.10.4 | OpenTelemetry and bounded operational metrics | backend + frontend + umbrella | todo |  |
| 1.10.5 | Backups, retention and recovery runbook | umbrella | todo |  |
| 1.10.6 | Load test at the declared capacity envelope | backend + umbrella | todo |  |
| 1.10.7 | Security scanning and evidence collection | umbrella + backend | todo |  |
| 1.10.8 | Accessibility and responsive browser acceptance | frontend + umbrella | todo |  |
| 1.10.9 | Accept, promote and launch | umbrella + backend + frontend | todo |  |
| 1.10.10 | Enforce module and process boundaries | backend + frontend | superseded | moved into the foundation as 0.2.10 (3 October 2026) |
| 1.10.11 | Staging deployment and forward migration orchestration | umbrella | todo |  |
| 1.10.12 | Alerting, availability and operational response | umbrella | todo |  |
| 1.10.13 | Independent restore and incident rehearsal | umbrella + backend | todo |  |
| 1.10.14 | Security review and abuse-case acceptance | umbrella | todo |  |
| 1.10.15 | Arabic language and domain-owner acceptance | umbrella + frontend | todo |  |
| 1.11.1 | Unify prospects with the player lifecycle | backend | todo |  |
| 1.11.2 | Control scouting assignments and reassignment | backend | todo |  |
| 1.11.3 | Make report review preserve the submitted evidence | backend | todo |  |
| 1.11.4 | Provide private watchlists with deliberate sharing | backend | todo |  |
| 1.11.5 | Convert an approved prospect through an explicit onboarding action | backend | todo |  |
| 1.11.6 | Build the scouting workspace and review experience | frontend | todo |  |
| 1.11.7 | Authorize scouting activation with an abuse gate | backend + umbrella | todo |  |
| 1.11.8 | Scouting on the shared surfaces: Player 360 and the home dashboard | backend + frontend | todo |  |
| 1.12.1 | The demo dataset: two fictional agencies at work | backend + umbrella | todo |  |
| 1.12.2 | The laptop demo: one command, production images | umbrella + backend + frontend | todo |  |
| 1.12.3 | Demo acceptance: rehearse the pitch, record the evidence | umbrella + frontend | todo |  |
| 1.12.4 | The hosted demo: a small server, a sandbox per prospect | umbrella + backend | todo |  |
| 2.1.0 | Approve the medical activation policy | umbrella + backend | todo |  |
| 2.1.1 | Type medical records without losing legacy provenance | backend | todo |  |
| 2.1.2 | Enforce purpose and immutable clinical amendments | backend | todo |  |
| 2.1.3 | Implement treatment session transitions | backend | todo |  |
| 2.1.4 | Record human return-to-play decisions | backend | todo |  |
| 2.1.5 | Publish a minimal availability projection | backend | todo |  |
| 2.1.6 | Reprove medical database isolation and key recovery | backend | todo |  |
| 2.1.7 | Build the medical workspace | frontend | todo |  |
| 2.1.8 | Gate medical activation against every disclosure channel | backend + umbrella | todo |  |
| 2.2.1 | Model training programs and governed pricing | backend | todo |  |
| 2.2.2 | Generate recurrence instances and explicit exceptions | backend | todo |  |
| 2.2.3 | Make enrollment and waitlist capacity concurrency-safe | backend | todo |  |
| 2.2.4 | Record operational payment observations honestly | backend | todo |  |
| 2.2.5 | Build the calendar and enrollment experience | frontend | todo |  |
| 2.3.1 | Record attendance against the correct enrollment and session | backend + frontend | todo |  |
| 2.3.2 | Version program completion rules | backend | todo |  |
| 2.3.3 | Issue immutable bilingual certificates | backend | todo |  |
| 2.3.4 | Expose minimal certificate verification | backend + frontend | todo |  |
| 2.4.1 | Validate performance records and metric units | backend | todo |  |
| 2.4.2 | Provide authorized trends and period comparison | backend + frontend | todo |  |
| 2.4.3 | Import performance with preview and deterministic row outcomes | backend | todo |  |
| 2.4.4 | Introduce matches and structured sporting references | backend | todo |  |
| 2.4.5 | Build the import preview and recovery UI | frontend | todo |  |
| 2.5.1 | Version rating schemes and deterministic totals | backend | todo |  |
| 2.5.2 | Build rating entry and historical comparison | frontend | todo |  |
| 2.5.3 | Support approved position-specific rating criteria | backend | todo |  |
| 2.6.1 | Run an independently authenticated realtime gateway | backend + umbrella | todo |  |
| 2.6.2 | Model explicit conversation membership and private images | backend | todo |  |
| 2.6.3 | Persist ordered messages before acknowledgment | backend | todo |  |
| 2.6.4 | Use monotonic read cursors and reconnect synchronization | backend | todo |  |
| 2.6.5 | Bind chat files and enforce abuse limits | backend | todo |  |
| 2.6.6 | Build durable chat and reconnect UX | frontend | todo |  |
| 2.7.1 | Add approved push delivery and device lifecycle | backend | todo |  |
| 2.7.2 | Synchronize the notification center in realtime | frontend | todo |  |
| 2.8.1 | Bound multipart video uploads and cleanup | backend | todo |  |
| 2.8.2 | Transform verified video in a sandboxed worker | backend | todo |  |
| 2.8.3 | Expose resumable video processing states | frontend | todo |  |
| 2.9.1 | Provide shared audited import and export job contracts | backend | todo |  |
| 2.9.2 | Build policy-scoped department report services | backend | todo |  |
| 2.9.3 | Build operational reports and job recovery UI | frontend | todo |  |
| 2.10.1 | Measure operational load and isolation under contention | backend + umbrella | todo |  |
| 2.10.2 | Restore operational data and immutable files on staging | backend + umbrella | todo |  |
| 2.10.3 | Accept and promote operational depth | umbrella + backend + frontend | todo |  |
| 2.10.4 | Verify operational accessibility and bilingual journeys | frontend + umbrella | todo |  |
| 3.2.1 | Complete organization, team and competition history | backend | todo |  |
| 3.2.2 | Build traceable player and cohort comparisons | backend | todo |  |
| 3.2.3 | Present accessible comparisons and analytical uncertainty | frontend | todo |  |
| 3.3.1 | Render approved dossier snapshots and archival copies | backend | todo |  |
| 3.3.2 | Issue scoped expiring share grants | backend | todo |  |
| 3.3.3 | Isolate the public dossier portal | frontend + backend | todo |  |
| 3.3.4 | Build dossier approval and share management screens | frontend | todo |  |
| 3.4.1 | Model finance documents and append-only balanced entries | backend | todo |  |
| 3.4.2 | Integrate a payment provider with durable verified callbacks | backend | todo |  |
| 3.4.3 | Settle training balances through finance allocations | backend | todo |  |
| 3.4.4 | Build the restricted finance workspace | frontend | todo |  |
| 3.4.5 | Approve the finance operating scope before integration | umbrella + backend | todo |  |
| 3.4.6 | Reconcile provider statements and controlled discrepancies | backend | todo |  |
| 3.5.0 | Approve the signature provider and evidence policy | umbrella + backend | todo |  |
| 3.5.1 | Connect signature envelopes to the approved version | backend | todo |  |
| 3.5.2 | Retain provider evidence and enforce completion | backend | todo |  |
| 3.6.1 | Schedule reports without persisting excess disclosure | backend | todo |  |
| 3.6.2 | Build report scheduling and delivery administration | frontend | todo |  |
| 3.7.1 | Attack the public portal and provider integration boundaries | backend + umbrella | todo |  |
| 3.7.2 | Accept and promote the agency intelligence release | umbrella | todo |  |
| 3.7.3 | Measure analytics, dossier and provider workload capacity | backend + umbrella | todo |  |
| 3.7.4 | Recover immutable dossiers, signature and finance evidence | backend + umbrella | todo |  |
| 4.1.1 | Complete the separate platform operator control plane | backend | todo |  |
| 4.1.2 | Implement explicit time-limited support elevation | backend | todo |  |
| 4.1.3 | Turn tenant provisioning into a recoverable operator workflow | backend | todo |  |
| 4.1.4 | Allow tenant roles within an approved permission ceiling | backend | todo |  |
| 4.1.5 | Measure entitlements and tenant usage | backend | todo |  |
| 4.1.6 | Offboard tenants while preserving required evidence | backend | todo |  |
| 4.1.7 | Enforce fair quotas under noisy-neighbor load | backend | todo |  |
| 4.1.8 | Build the operator and tenant administration workspace | frontend | todo |  |
| 4.2.1 | Prove enterprise SSO and identity-provider portability | backend + umbrella | todo |  |
| 4.2.2 | Qualify provider-managed passkeys and recovery assurance | backend + frontend | todo |  |
| 4.3.1 | Keep RLS coverage complete as the schema grows | backend | todo |  |
| 4.3.2 | Complete governed legal-hold administration | backend | todo |  |
| 4.3.3 | Scale only the measured bottleneck | backend + umbrella | todo |  |
| 4.3.4 | Rehearse platform upgrades and full recovery | backend + umbrella | todo |  |
| 4.4.1 | Deliver signed outbound webhooks safely | backend | todo |  |
| 4.4.2 | Expose a narrow partner API with current authorization | backend | todo |  |
| 4.4.3 | Integrate calendars through explicit limited consent | backend | todo |  |
| 4.4.4 | Build integration consent and delivery administration | frontend | todo |  |
| 4.5.1 | Approve AI data, model and human-review governance | umbrella + backend | todo |  |
| 4.5.2 | Offer attributable draft summaries under human control | backend + frontend | todo |  |
| 4.5.3 | Evaluate source faithfulness and disclosure before activation | backend + umbrella | todo |  |
| 4.6.1 | Review a native client session profile without weakening web sessions | backend + umbrella | todo |  |
| 4.6.2 | Verify responsive workflows under constrained networks | frontend | todo |  |
| 4.7.1 | Accept a second agency through the complete operating model | umbrella | todo |  |
| 4.7.2 | Attack and load-test the full multi-tenant platform | backend + umbrella | todo |  |
<!-- plan:progress:end -->
