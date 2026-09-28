# Domain workflows and business invariants

This is the target behavior, not a claim that the inspected application implements it. Microsteps are the execution authority; their named tests feed the [test catalog](test-catalog.md) and [traceability matrix](traceability.md). Current code findings belong to [current state](current-state.md) and [database review](database.md). Cross-cutting contracts are in [API](api.md), [security](security-privacy.md), [architecture](architecture.md) and the [OPEN register](../implementation/00-master-plan.md#open-register).

## Shared command contract

Every tenant business use case receives an authenticated current principal, explicit `TenantContext` and a transaction client from `withTenantTransaction`. Browser cookie identity is established by Nest's confidential OIDC client; tenant-user requests check the opaque application session and active membership against PostgreSQL every time. The Phase-4 platform control plane instead checks its global PlatformSession/operator; approved support establishes a tenant context with the explicit PLATFORM actor described below. A frontend capability, room name, file key, provider claim, archived invitation or stale cached role never supplies business authority.

```ts
type CommandContext = {
  tenant: TenantContext;
  principal: Principal; // current session, membership and assurance
  requestId: string;
};
type MutationPrecondition = {
  expectedRevision: number; // from the authorized strong ETag / If-Match
  idempotencyKey: string;
};
```

Authenticate and validate the request, then authorize the current action, same-tenant object and field projection. A matching terminal idempotency receipt is replayed under current authorization before reevaluating the original revision or lifecycle precondition: its successful first execution may already have advanced that revision. A different payload/path/precondition conflicts with the receipt. Only a new or reclaimed execution checks the current expected revision and domain guards, locks rows needed for cross-record invariants, and atomically persists mutation, audit, outbox and terminal command receipt in the tenant transaction. Mutable aggregates use `revision`, independently of immutable business `version`. Missing required `If-Match` returns 428; stale authorized state returns 412; invalid domain transition returns 409. A foreign/unreadable object returns the scoped 404 before any revision or state detail.

The idempotency receipt moves `IN_PROGRESS → SUCCEEDED | REJECTED` under a lease and fencing generation; an expired lease requires durable outcome inspection before reclaim. Same key with different validated payload/path/preconditions is rejected. Current authorization is checked before replaying a minimal receipt. Remote delivery has a separate `QUEUED → SENDING → ACCEPTED | FAILED | UNKNOWN → RECONCILED` lifecycle: an accepted provider request is not a completed business workflow, and a timeout does not prove failure. Provider callbacks first persist an authenticated WebhookReceipt unique by provider/account/remoteEventId and atomically create a local tenant-bound OutboxEvent UUID. A duplicate remote event ID with a changed payload hash is rejected as a security conflict. ConsumerInbox references that local event UUID, never an arbitrary provider event string. Workers recheck tenant/actor policy where applicable and deduplicate local processing with `UNIQUE(consumer,eventId)`. The PostgreSQL outbox/inbox is authoritative; BullMQ/Valkey transports work and may redeliver it.

Every new tenant table includes a direct `tenantId`, same-tenant and same-parent FKs, ENABLE/FORCE RLS, least-privilege runtime grants and SQL catalog tests in its owning migration. UUIDv4 is the default; UUIDv7 is restricted to justified append-heavy records. Civil birthdays/contract dates use SQL DATE; instants use timestamptz(3); recurrence stores an IANA timezone. Money uses `NUMERIC(19,4)` with enabled `CurrencyDefinition(code,minorUnitExponent,enabled)`, validated payable scale and string API amounts. No domain rounds through JavaScript Number or treats NaN/Infinity as money.

## Identity, memberships and owned-player access

Owners: `0.5.3`–`0.5.10`, `0.6.5`, `1.1.1`, `1.2.3`; enterprise identity assurance extends these in `4.2.1`/`4.2.2`.

Global `Identity(issuer,subject)` identifies the verified external principal. Tenant `User` is the membership, unique by `(tenantId,identityId)`; memberships and business FKs preserve existing IDs during migration. An email address is contact data and invitation targeting, never sufficient account-link proof. Lifetime tenant-email reservation remains in force when a membership is archived. Reactivation is an explicit audited action on the existing record; it is not delete-and-recreate.

Invitation consumption checks tenant, verified provider identity, target policy, single-use receipt, expiry and active inviter authority where required; acceptance cannot promote the invitee beyond approved scope. Deactivation, role restriction or local session revocation affects the next request/event/job check. IdP-side changes affect Sodara when a validated event arrives or the app session expires; that residual window remains documented and owner-approved, not described as immediate IdP revocation.

`PlayerAccountLink` and `GuardianLink` are explicit same-tenant links. A player sees only the approved own-record projection; a guardian additionally needs current approved authority, validity and scope. A role name or matching email does not establish the relationship. Unknown guardian/minor policy defaults to denial pending the agency/counsel decision. A guardian never automatically receives clinical, legal or compensation details.

## Players, affiliations and lifecycle

Owners: `1.2.1`–`1.2.8`; structured matches `2.4.4`; prospects and onboarding `3.1.1`/`3.1.5`; affiliation analytics `3.2.1`.

Player identity is stable through `PROSPECT → ONBOARDING → ACTIVE → ARCHIVED`. Exact allowed transitions and restoration rules are explicit policy; an ordinary PATCH cannot set stage. Store stage-specific completeness configuration/version and return missing requirements rather than inventing values. PROSPECT permits minimal recruitment information; ONBOARDING collects required identity, documents and relationship evidence. ACTIVE requires the approved completeness and agency admission guards, never a medical inference or the mere existence of a scouting approval.

Duplicate suggestions are scoped to authorized same-tenant records and never auto-merge on name, birthday or email. Any approved merge requires a separate reviewed operation preserving source IDs/evidence and referential integrity. Archival removes ordinary operational visibility but preserves retention-governed relationships and immutable evidence.

Organization, Team, Competition, Match and player affiliation are distinct concepts. Competition is not an organization type. Affiliation periods and source provenance support historical reporting; unknown clubs/opponents/dates remain unresolved instead of being guessed. Player 360 composes permitted module projections and does not directly join confidential module tables. Counts, recent activity and completeness hints must not reveal hidden records.

## Files, immutable versions and evidence

Owners: `0.8.1`–`0.8.5`, `1.3.1`–`1.3.5`, `2.8.1`–`2.8.3`; each domain owns its typed binding.

```text
FileObject.status: CREATED → UPLOADING → UPLOADED → SCANNING → PROCESSING → READY
Terminal failures: FAILED | REJECTED | ABORTED
FileObject.scanVerdict: PENDING | CLEAN | INFECTED | ERROR
Download eligibility: READY + CLEAN + current typed-owner authorization
Immutable content identity: exact object version + SHA-256 + byte length
```

UploadSession tracks expiry/finalization/abort timestamps and revision around this FileObject lifecycle; it does not define a competing scan-state machine. The browser receives a short-lived PUT for a quarantine location only. Completion locks the upload session and pins the exact submitted storage version before validation/scanning; all reads by validator, ClamAV and promotion refer to that version. Validate declared and actual size, permitted MIME/magic bytes, safe filename and bounded content characteristics. Scan errors/timeouts/signature-database unavailability leave content unavailable; CLEAN is a scan verdict, and only READY with CLEAN can pass the download gate. Promotion writes a new worker-only immutable destination/version and records SHA-256, storage version ID, size and scanner result. Downloads read that same pinned immutable version. A still-valid old PUT can replace quarantine bytes but cannot replace READY+CLEAN content or change the version that was scanned and approved.

Do not assume a presigned PUT is single-use. A download URL is also a bearer capability until expiry; revocation prevents new authorization immediately but does not recall an already-issued URL. Set a short bounded TTL, keep confidential classes behind an authorized proxy when the approved policy requires stronger revocation, and record the limitation. Object keys never substitute for tenant/object policy.

`DocumentVersion`/business evidence refers to immutable `FileObject` identity, not a mutable URL. Owner bindings use typed composite FKs and classification checks. A public or ordinary chat context cannot declassify a medical/legal/finance file. Generated variants bind source file ID/version/hash and retain the owner's classification. Malware or decoder rejection blocks downstream processing and access; no fallback reads arbitrary quarantine paths.

| Legacy URL retirement target | Owning microstep | Replacement |
|---|---|---|
| `Document.fileUrl` (`backend/prisma/schema.prisma:448`) | `1.3.1` | Reconcile/backfill/retire the URL using the FileObject schema expanded in `0.8.2`. |
| `Tenant.logoUrl` (`backend/prisma/schema.prisma:280`) | `1.1.2` | Tenant branding binding with an explicitly safe logo projection. |
| `User.avatarUrl` (`backend/prisma/schema.prisma:334`) | `1.1.8` | Tenant membership avatar binding; no global cross-tenant leak. |
| `PlayerMedia.fileUrl` (`backend/prisma/schema.prisma:538`) | `1.3.3` | Player media binding, variant lineage and featured-image policy. |
| `Contract.fileUrl` (`backend/prisma/schema.prisma:624`) | `1.4.1` | Map and constrain the current-version reference, then retire this column; `1.4.8` first establishes immutable versions and their parent key. |
| `ContractVersion.fileUrl` (`backend/prisma/schema.prisma:670`) | `1.4.8` | Immutable FileObject ID, exact object version and digest. |
| `Conversation.imageUrl` (`backend/prisma/schema.prisma:1029`) | `2.6.2` | ConversationImage→FileObject under current membership. |
| `Message.fileUrl` (`backend/prisma/schema.prisma:1270`) | `2.6.5` | MessageAttachment→FileObject under conversation and source policy. |

This is the migration disposition for the inspected URL columns; [database](database.md) contains their current-schema evidence. Import legacy blobs only from approved sources with provenance, SSRF protections and rescan. Unresolved URLs remain quarantined; no empty digest, fabricated owner or unchecked remote fetch makes them valid.

## Contracts, approvals and signatures

Owners: `1.4.1`–`1.4.10`; provider integration `3.5.0`–`3.5.2`. Implements SR-CT-001..012 and BR-RULE-03/04.

```text
DRAFT → IN_REVIEW → APPROVED → SIGNED → EXPIRED | TERMINATED
             └→ REJECTED
REJECTED → new DRAFT version/review round, preserving earlier evidence
```

The policy explicitly defines any additional permitted transition; generic status mutation is forbidden. Contract civil start/end dates must be ordered. Contract types and compensation periods are approved dictionaries; compensation uses exact Money and a separate confidential projection. Contract reads as well as lifecycle mutations are audited.

`ContractVersion` is an immutable snapshot of terms, approved source FileObject/version/hash, author and change note, unique `(contractId,version)`. Editing produces a new version. `ApprovalRound` snapshots approval policy for one contract version; ordered `ApprovalStep` coordination is mutable under revision, while `ApprovalDecision` is append-only. Same-contract/tenant references forbid attaching decisions to another contract's version. Submitting a replacement supersedes the pending round; old decisions remain evidence and do not approve the new bytes.

`decide(ctx,stepId,decision,comment,expectedRevision)` checks active approver eligibility, order, version, separation of duties and current assurance while locking round coordination. Default chain is legal then owner with no requester self-approval until an approved policy settles alternatives. Concurrent decisions cannot both consume the same step. A rejection never erases prior approvals.

Phase 1 introduces `SignatureEvidence`, `Signatory` and `SignatureEvent`. Evidence binds the approved source version/hash, required signatories, verification method, policy version, attester and any signed-result FileObject/hash. Signing may change PDF bytes: keep `sourceSha256` and `signedArtifactSha256` distinct and retain policy-verifiable binding between them. Uploading a file, checking a UI box or hashing bytes is insufficient to declare legal validity.

`SIGNED` requires every required approval and complete evidence accepted under the approved counsel/agency policy. An approved manual method may satisfy SR-CT-008 in Phase 1; if that policy is unresolved, collect pending evidence but deny SIGNED. SR-CT-011 provider integration is explicitly delivered in Phase 3. `SignatureEnvelope` extends the existing evidence truth with provider account/envelope mapping; callbacks validate authentic raw bytes, account, timestamp and stable event ID before tenant-bound inbox processing. Out-of-order/duplicate callbacks cannot regress state or approve a superseded source. Query/reconcile unknown remote outcomes before retrying.

ContractVersion, ApprovalDecision, SignatureEvent and audit records deny ordinary UPDATE/DELETE/TRUNCATE with grants, row triggers and statement-level TRUNCATE protection. Signature evidence and signatory attestation changes append new evidence instead of overwriting approved facts. Restoring artifacts, keys and database evidence must preserve source/result binding and verification.

Expiry/reminders are advisory projections of the authoritative civil end date and status. A failed notification cannot keep an expired contract active. Termination records its effective DATE, actor, reason and approved evidence; it does not edit the original signed version or erase accrued finance facts.

## Legal tickets and confidentiality

Owners: `1.5.1`–`1.5.5`; retention extension `4.3.2`. Implements SR-LE-001..009.

Use explicit `OPEN → IN_PROGRESS → PENDING_REVIEW → RESOLVED → CLOSED` transitions with policy-defined reopening; each transition records actor/reason/revision. Assignment requires an active authorized legal membership. Priority and due dates drive SLA calculations and committed outbox reminders; notification acceptance never changes ticket state.

Legal notes/attachments carry classification and author/time. Internal notes are absent from requester/player/ordinary admin projections, search, counts, activity snippets and notifications unless explicit permission plus relationship/purpose permits them. Do not hide text while exposing its filename, count or author as a side channel. Sensitive narratives use the approved encrypted boundary; append amendments with restricted history rather than destroying disputed content. Access audits record safe identifiers/purpose, not confidential narrative.

## Medical and rehabilitation

Owners: `2.1.0`–`2.1.8`; existing routes remain server-disabled before that activation gate. Implements SR-MED-001..008 and BR-RULE-07.

Medical policy is approved before real clinical data: purpose, patient relationship, eligible practitioners, recipient/guardian exceptions, retention, hosting, encryption/key recovery and a minimal availability projection. The default remains confidential and disabled with synthetic fixtures. An owner or ordinary administrator does not inherit clinical authority.

Medical records support injury, illness, treatment, vaccination, examination and rehabilitation with type-appropriate fields. Controlled dictionaries have explicit unresolved legacy provenance. `readRecord(ctx,id,purpose)` requires confidential permission plus current relationship/recipient scope and permitted purpose; an audit write must succeed before releasing clinical content. `amendRecord` appends attributable corrected evidence while preserving prior clinical values under restricted protection.

Treatment is `SCHEDULED → IN_PROGRESS → COMPLETED` or `CANCELLED` according to the approved policy. Responsible practitioner eligibility and same-player record/session references are required. Completed narrative corrections become amendments. Human return-to-play assessments record author, date, rationale and policy version; estimated recovery dates never automatically clear a player.

Coaches receive only the policy-approved availability status/effective date. They receive no diagnosis, treatment, narrative, hidden-record count or unexplained confidential-source hint. A medical canary must remain absent from ordinary Player 360, search/export, chat files, notifications, logs/traces, caches and object URLs before `2.1.8` activation. Explicitly approved exceptional recipients need their own tested projection rather than receiving the clinician DTO.

## Training, attendance and certificates

Owners: `2.2.1`–`2.3.4`; verified settlement `3.4.3`. Implements SR-TR-001..010 and BR-RULE-08.

Programs store civil range, IANA timezone, capacity, exact Money, controlled recurrence and completion rules. Each generated session has concrete instants and a stable occurrence key. Recurrence expansion is idempotent; DST gap/fold handling is explicit; cancellations/reschedules preserve completed session and attendance history.

Enrollment is `PENDING → APPROVED | REJECTED | WAITLISTED`, with controlled cancellation/reactivation. One lifetime player/program membership exists; reenrollment uses an audited reactivation. Capacity-bearing approval locks the program/capacity record or uses a proved serializable retry strategy. Two concurrent requests for the last seat have one winner. The waitlist has deterministic ordering and promotion rechecks current eligibility.

Attendance stores one status per enrollment/session: Present, Absent, Late or Excused. Composite relationships ensure the session and enrollment belong to the same program and tenant. Corrections require reason, revision and audit; duplicate retries cannot inflate attendance. Completion evaluation records the exact rule version and source attendance; later changes do not silently rewrite an issued certificate.

A certificate references the eligible completion result, immutable rendered FileObject and unique high-entropy verification identifier. Rendering is a worker job; QR/public verification is independently throttled and returns only policy-approved minimal validity information. Player name/program detail is not published merely because it exists in the certificate; identity disclosure requires an approved policy. Revocation/reissue preserves original issuance evidence and verification reflects current validity.

Phase-2 payment statuses are attributed operational observations marked unverified where no settlement source exists. They cannot create receipts or ledger truth. Phase 3 derives verified Unpaid/Partial/Paid/Refunded/Waived status from finance allocations, while preserving earlier observations as provenance and highlighting disagreement.

## Performance, rating schemes and analytics

Owners: `2.4.1`–`2.5.3`, `3.2.1`–`3.2.3`. Implements SR-PF-001..005, SR-RT-001..005 and BR-RULE-09.

Performance observations have player, date, optional season/match, source and bounded metrics. Validate impossible negatives and known metric limits; unknown is null/explicit missing, never zero. Imports bind source hash, mapping version and stable row identity. Preview precedes confirmed execution; accepted/rejected rows and safe error counts reconcile, retry resumes unfinished work and invalid rows do not erase prior accepted results.

`RatingSchemeVersion` fixes dimensions, scales, weights, rounding and eligibility. Calculate totals server-side from validated observations, preserving scheme version and evaluated position. New weights never reinterpret historical scores. Legacy totals whose formula is unknown remain explicitly unverified; do not invent past schemes. Unlike schemes are shown as discontinuous or normalized only through an approved, versioned method.

Comparisons identify period, sample size, missing data, units and source IDs. Cohort membership and aggregates obey current object and field policy; hidden records cannot inflate counts or appear through benchmarks. Charts have equivalent accessible tables. Export uses the same permitted projection and audited job path, not a privileged analytics database view.

## Chat and notifications

Owners: `2.6.1`–`2.7.2`; base notifications `1.6.1`–`1.6.4`. Implements SR-CH-001..010, SR-NF-001..007 and BR-RULE-10.

Conversation membership is explicit and tenant-bound. A canonical direct pair prevents duplicate 1:1 threads; group admin actions are audited. Removed members cannot read/send/sync attachments or receive later deliveries. `sendMessage(ctx,conversationId,clientMessageId,body)` allocates a monotonically increasing conversation sequence and commits the message, audit and outbox before successful acknowledgment. Stable client IDs prevent duplicate messages; only trusted application services emit System messages.

Read state is `lastReadSequence` per member, advanced monotonically to an existing authorized message. Reconnect fetches bounded sequence gaps from durable storage; an event timestamp is not a reliable cursor. The separate gateway validates same-origin handshake, opaque session, tenant and conversation policy; protected events and outbound delivery authorization honor current PostgreSQL session/membership checks. Revocation disconnects or denies subsequent use; a Valkey room subscription is not authorization.

Edits retain edit state/timestamp; recall removes ordinary visibility according to policy while preserving required restricted evidence. Message attachments and conversation images use typed immutable FileObject links. Chat cannot forward a confidential source file to a recipient who lacks that source authority simply by creating a new chat link.

Notifications contain safe localized templates and authorized references. Preferences govern optional channels, while approved security notices may be mandatory. In-app state is durable; realtime is a hint to refetch. Email/push delivery distinguishes queued, provider-accepted, failed and unknown/retry; provider acceptance cannot prove display or business completion. Duplicate external email is possible after a provider-accept/crash boundary, so never promise exactly-once external sending. Device tokens are tenant/identity-bound, revocable and excluded from telemetry.

## Scouting and prospect onboarding

Owners: `3.1.1`–`3.1.7`; server flag remains off until sporting policy and abuse acceptance.

Assignments capture scout, assigner, region, competition, target position, age range, due date and controlled status. Existing players and external prospects share Player identity at different stages. Report review is `DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED | REJECTED`. Submission freezes the revision; corrections create another revision/round. Recommendation and score scales are governed, with immutable submitted narrative and attributable review decisions.

Watchlists are private to the owner by default; deliberately shared lists have explicit policy. Another scout’s draft, protected identity fields and file attachments remain inaccessible despite broad scout role membership. Approved recruitment review permits an authorized onboarding action, not automatic player admission, consent, contract signing or clinical eligibility. Idempotent onboarding advances the same prospect identity and records missing information rather than creating duplicates.

## Finance, sharing and scheduled reports

Finance owners: `3.4.1`–`3.4.6`. Before activation the owner/accountant approves chart of accounts, jurisdictions/tax responsibilities, currencies, payment/refund providers, segregation and reconciliation. Default sandbox only; the documentation asserts no accounting or legal compliance result.

Invoices, payments, compensation components and allocations use exact Money. Posting requires balanced entries within each currency and an attributable source; cross-currency conversion requires a separately approved rate/source policy. Posted facts are immutable; corrections are reversals/adjustments, not UPDATE of settled money. Browser success redirects do not prove payment. Signed callbacks enter a tenant-bound inbox; mismatched account/currency/amount, duplicates and out-of-order events are reconciled. An unknown remote outcome is investigated with provider identity before another charge/refund attempt. Reconciliation preserves source statement batches and requires approval for write-offs or discrepancies.

Dossier/sharing owners: `3.3.1`–`3.3.4`. An approver selects a template and resolved permitted fields/media to create an immutable snapshot. Sharing never points to the latest unrestricted player record. High-entropy grant tokens are stored as hashes, scoped to that snapshot, independently throttled, expiring and revocable. Tokens stay out of URLs/logs/third-party analytics where technically possible; no-referrer and no-store apply. Public endpoints cannot create internal sessions or fetch arbitrary files. PDF/A is a policy-selected output with a successful validator result, not an extension or a renderer option that implies conformance.

Scheduled-report owners: `3.6.1`/`3.6.2`. Each occurrence has stable schedule identity and IANA-timezone semantics; retries create one local report occurrence. Recheck owner/recipient policy at generation and download. Default email contains a safe in-app link, not confidential attachments. Recipients who lose authority cannot receive fresh access, even if they were eligible when the schedule was created.

## Retention, support, integrations and assistance

Retention owners: `1.3.4`, `4.3.2`; offboarding `4.1.6`. Unresolved retention policy disables automatic purge. Hold-aware cleanup is required from Phase 1; Phase 4 adds formal case/approval/release administration. A hold covers related immutable versions/variants/evidence and approved backup retention behavior. Releasing a hold recalculates ordinary eligibility and does not itself delete evidence. Restores reapply tombstones/revocation so a restored historical snapshot does not reactivate revoked access.

Support owners: `4.1.1`/`4.1.2`. Platform operators have no implicit business authority. A global PlatformSession references PlatformOperator/Identity because a tenant-bound UserSession cannot represent an operator without a membership. It uses the same opaque-cookie, CSRF, derived assurance, expiry/revocation semantics and current PostgreSQL checks, without hidden tenant memberships. Time-limited grants bind actual actor, tenant, reason/case, approved actions/resources, purpose and current assurance; a distinct approver authorizes them. Every action checks the current PostgreSQL grant and uses the normal explicit tenant transaction with actor kind PLATFORM {operatorId,sessionId,supportGrantId}, never a fabricated User actor. No blanket bypass-RLS credential or hidden impersonation supplies support access.

Integration owners: `4.4.1`–`4.4.4`. Outbound hooks have signed timestamped minimal payloads, stable event identity, bounded retries and SSRF-safe destinations. Partner credentials are explicit scoped/expiring/revocable service principals on separate endpoints with current database authorization. Approved calendar connector credentials are separately encrypted integration secrets, never a reason to persist OIDC login tokens. Calendar consent and data policy default off; medical/confidential events are excluded unless an explicit approved policy is implemented and tested.

Assistance owners: `4.5.1`–`4.5.3`. Default disabled pending data/provider/evaluation policy. Source material is untrusted data and grants no tool authority. A generated suggestion retains source/version provenance and requires explicit authorized human review; it cannot change medical clearance, ratings, contract state or posted finance. Evaluate unsupported claims, prompt injection and disclosure canaries in Arabic and English before activation. This feature is not a claim of fair, compliant or clinically valid automated decision-making.

Mobile readiness owners: `4.6.1`/`4.6.2`. Responsive web journeys and transport-contract fixtures are the deliverable. A native session profile remains disabled until its own reviewed ADR; it must retain current app-session/membership revocation, object policy and tenant context. No native application or provider-bearer bypass is implied by this readiness work.
