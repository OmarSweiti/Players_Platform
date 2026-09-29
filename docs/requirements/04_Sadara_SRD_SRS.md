<!-- Frozen baseline: faithful Markdown conversion of source/04_Sadara_SRD_SRS.docx (converted 28 September 2026;
     product name corrected to Sadara on 29 September 2026). Do not edit — change control is in README.md. -->

SADARA PLATFORM

Software Requirements Document (SRD / SRS)

Sadara Platform - Software Requirements Baseline

Version 1.0 | Requirements Baseline | 28 September 2026

Status: Draft for stakeholder validation and architecture sign-off

## 0. Document Control

| Field | Value |
|---|---|
| Document | Sadara Platform - Software Requirements Document (SRD / SRS) |
| Version | 1.0 |
| Date | 28 September 2026 |
| Status | Draft baseline |
| Language | English |
| Primary objective | Define implementation-testable software requirements with identifiers, functional behavior, data rules, API expectations, security controls and acceptance conditions. |
| Primary audience | Software engineers, QA, security, DevOps/SRE, technical leads, product and domain owners. |
| Source baseline | Sadara concept brief + supplied Prisma/PostgreSQL schema |
| Requirement method | ISO/IEC/IEEE 29148-aligned structure with explicit identifiers and acceptance intent |

Traceability rule: business requirements are refined into product requirements, then system requirements, then software requirements. Requirement IDs are stable and must not be reused after baseline approval.

## 1. Requirement Conventions

Requirement language: “shall” means mandatory for the baseline; “should” is a recommended design constraint; “may” is optional. Priorities: P0 critical for the intended release, P1 important, P2 later/optional. Each requirement is uniquely identified.

## 2. System Software Requirements - Core

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-001 | P0 | The system shall support isolated tenant contexts for all tenant-owned operations. | Tenant context established from authenticated identity; cross-tenant object access fails. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-002 | P0 | The system shall expose versioned HTTP APIs using REST and an OpenAPI contract. | All supported endpoints appear in the approved OpenAPI document. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-003 | P0 | The system shall return consistent machine-readable error responses containing code, message, request ID and field errors where applicable. | Negative tests verify schema and no stack traces. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-004 | P0 | The system shall support cursor or page-based pagination for collection endpoints with explicit maximum page size. | Requests above configured maximum are rejected or capped predictably. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-005 | P0 | The system shall enforce server-side validation regardless of client-side validation. | Tampered requests fail validation. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-006 | P0 | The system shall store timestamps in UTC and render them in the tenant/user locale according to configuration. | Cross-timezone test cases pass. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-007 | P0 | The system shall support Arabic and English locales and RTL/LTR rendering. | Key workflows pass localized UI acceptance tests. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-008 | P0 | The system shall expose request/correlation identifiers across HTTP, websocket, jobs and logs. | A single transaction can be correlated across services. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-009 | P0 | The system shall prevent sensitive secrets and tokens from appearing in application logs, telemetry or error responses. | Secret-scanning tests and log inspection pass. |

| ID | Pri | Requirement | Acceptance |
|---|---|---|---|
| SR-CORE-010 | P1 | The system should provide idempotency support for externally retried commands such as payments, signatures and webhook processing. | Duplicate command produces one business outcome. |

## 3. Identity, Authentication and Session Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-AUTH-001 | P0 | The system shall authenticate users through an approved identity provider or secure application-managed authentication implementation. |
| SR-AUTH-002 | P0 | Privileged roles shall require MFA; the policy shall be configurable by tenant/platform. |
| SR-AUTH-003 | P0 | Refresh tokens shall rotate and be revocable per session/device. |
| SR-AUTH-004 | P0 | Repeated failed authentication shall trigger adaptive throttling and temporary lockout according to security policy. |
| SR-AUTH-005 | P0 | Password reset and verification tokens, if application-managed, shall be random, short-lived, single-use and stored only as hashes. |
| SR-AUTH-006 | P0 | MFA secrets, if stored by the application, shall be encrypted and access-restricted. |
| SR-AUTH-007 | P0 | Logout shall revoke or invalidate the appropriate session/token state. |
| SR-AUTH-008 | P1 | The system should support passkeys/WebAuthn as a future authentication factor without changing business authorization APIs. |
| SR-AUTH-009 | P0 | Authorization checks shall be performed on every protected resource and action; UI hiding alone shall never constitute authorization. |

## 4. Tenant, User, Role and Permission Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-ACL-001 | P0 | Tenant shall be represented by a unique immutable identifier. |
| SR-ACL-002 | P0 | User email shall be unique within a tenant and normalized consistently. |
| SR-ACL-003 | P0 | Platform-level super administrators shall not automatically receive all tenant confidential data; support elevation shall be explicit and auditable. |
| SR-ACL-004 | P0 | The permission model shall support category + action permissions, including CREATE, READ, UPDATE, DELETE, APPROVE, EXPORT, IMPORT, ASSIGN, VIEW_CONFIDENTIAL and MANAGE. |
| SR-ACL-005 | P0 | RBAC shall establish baseline role permissions; ABAC/policy checks shall evaluate relationship and sensitivity constraints. |
| SR-ACL-006 | P0 | Permission changes shall be audited with actor, target, previous state and new state. |
| SR-ACL-007 | P0 | Inactive/locked users shall not access protected APIs or websocket resources. |
| SR-ACL-008 | P0 | A role with no explicit confidential-data permission shall not receive confidential fields by omission or default. |
| SR-ACL-009 | P0 | Every export operation shall verify export permission and produce an audit event. |

## 5. Player Management Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-PL-001 | P0 | The system shall create, read, update and archive player profiles with tenant ownership. |
| SR-PL-002 | P0 | The player profile shall support name, date of birth, nationality, secondary nationality, position, secondary position, preferred foot, status, current club, jersey number, height, weight, passport details where authorized, agent contact, emergency contact, biography and metadata. |
| SR-PL-003 | P0 | The system shall prevent unauthorized users from reading passport, emergency-contact or other protected identity fields. |
| SR-PL-004 | P0 | The system shall maintain a profile completeness calculation against configurable required fields. |
| SR-PL-005 | P1 | The system shall support player media with featured-media designation, captions and metadata. |
| SR-PL-006 | P1 | The system shall support large video upload using multipart/chunked transfer and asynchronous processing. |
| SR-PL-007 | P1 | The system shall generate media metadata/thumbnail variants asynchronously where applicable. |
| SR-PL-008 | P0 | The system shall expose a player timeline/summary composed only of events the current user is authorized to view. |
| SR-PL-009 | P1 | The system shall generate an approved player dossier using a configurable template and selected fields/media. |
| SR-PL-010 | P1 | External player-dossier sharing shall be explicit, scoped, revocable and optionally time-limited. |
| SR-PL-011 | P0 | Player deletion shall be soft deletion/archival subject to retention and legal requirements. |

## 6. Document and File Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-DOC-001 | P0 | All uploaded files shall be associated with a tenant and an authorized business entity. |
| SR-DOC-002 | P0 | Storage shall be private by default; downloads shall use authorization checks and short-lived signed URLs. |
| SR-DOC-003 | P0 | The system shall validate file size, permitted type, content signature/magic bytes and filename safety. |
| SR-DOC-004 | P1 | Malware scanning shall be supported before a file is marked safe for downstream use. |
| SR-DOC-005 | P1 | The system shall support file versioning where the business entity requires evidence of historical versions. |
| SR-DOC-006 | P0 | File access shall not reveal objects across tenants even when object keys or IDs are guessed. |
| SR-DOC-007 | P1 | Document retention classification shall be configurable by document type. |
| SR-DOC-008 | P1 | The system shall support PDF/A generation for archival copies where required by document policy. |

## 7. Medical and Rehabilitation Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-MED-001 | P1 | Only authorized medical/physiotherapy users and explicitly authorized recipients shall access full medical records. |
| SR-MED-002 | P1 | The system shall support medical record types including injury, illness, treatment, vaccination, medical examination and rehabilitation. |
| SR-MED-003 | P1 | The system shall capture injury type/body part/severity/description/treatment/injury date/recovery date/return-to-play date as applicable. |
| SR-MED-004 | P1 | Medical records shall default to confidential unless the policy explicitly permits broader visibility. |
| SR-MED-005 | P1 | Treatment sessions shall support scheduled, in-progress, completed and cancelled states. |
| SR-MED-006 | P1 | Treatment sessions shall record date, duration, type, description, exercises, progress notes and responsible medical user. |
| SR-MED-007 | P0 | Medical data shall be excluded from ordinary exports, global search, notifications and logs unless the authorization policy explicitly allows it. |
| SR-MED-008 | P1 | Return-to-play fields shall be auditable and shall not be treated as an automated medical decision. |

## 8. Contract Management Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-CT-001 | P0 | The system shall support contract statuses Draft, In Review, Approved, Signed, Expired, Terminated and Rejected with controlled transitions. |
| SR-CT-002 | P0 | Contract records shall reference a player and tenant and may reference a season. |
| SR-CT-003 | P0 | The system shall store start/end dates and validate that end date is not before start date. |
| SR-CT-004 | P0 | The system shall support contract types including Professional, Amateur, Loan, Sponsorship, Coaching and Other, subject to configured domain policy. |
| SR-CT-005 | P0 | Compensation shall support amount, currency and period; sensitive compensation fields require explicit authorization. |
| SR-CT-006 | P0 | The system shall maintain immutable historical contract versions with version number, file, creator and change note. |
| SR-CT-007 | P0 | Approval workflows shall support ordered approval steps and capture status, approver, comment and response timestamp. |
| SR-CT-008 | P0 | A contract shall not transition to Signed until all required approvals and signature evidence are complete. |
| SR-CT-009 | P1 | The system shall support configurable expiry reminders and record notification state. |
| SR-CT-010 | P1 | Contract termination shall capture termination date and reason and shall be auditable. |
| SR-CT-011 | P1 | The system shall support signature-envelope integration and persist provider, document hash, signatory and event evidence needed for verification. |
| SR-CT-012 | P0 | All contract access and lifecycle mutations shall be audited. |

## 9. Performance, Match and Rating Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-PF-001 | P1 | The system shall record performance records by player and match date, with optional season linkage. |
| SR-PF-002 | P1 | Performance records shall support opponent, venue, competition, starting status, goals, assists, minutes, cards, shots, shots on target, pass accuracy, rating and extensible extra statistics. |
| SR-PF-003 | P1 | The system shall validate metric ranges and reject impossible values such as negative minutes. |
| SR-PF-004 | P1 | The system shall support CSV import with column mapping, preview, validation errors and partial-failure handling. |
| SR-PF-005 | P1 | The system shall provide player/season trend aggregation and period comparison. |
| SR-RT-001 | P1 | The rating subsystem shall support technical, physical and mental scores plus extensible dimensions. |
| SR-RT-002 | P1 | Each rating shall reference a rating scheme/version used to calculate the total score. |
| SR-RT-003 | P1 | The system shall calculate total score deterministically from the active scheme rather than relying on user-entered totals. |
| SR-RT-004 | P1 | Rating history shall preserve prior scores even after scheme changes. |
| SR-RT-005 | P2 | The system may support position-specific rating criteria with separate weights. |

## 10. Training, Enrollment and Attendance Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-TR-001 | P1 | The system shall support training programs with title, description, start/end, location, capacity, price, currency and recurrence metadata. |
| SR-TR-002 | P1 | Recurring training shall generate or represent individual sessions with date/time/location and cancellation state. |
| SR-TR-003 | P1 | Enrollment shall support pending, approved, rejected, cancelled and waitlisted states. |
| SR-TR-004 | P1 | Enrollment shall prevent duplicate player enrollment in the same training program. |
| SR-TR-005 | P1 | Capacity constraints shall be enforced according to configured policy. |
| SR-TR-006 | P1 | Payment status shall support unpaid, paid, partial, refunded and waived, but financial settlement shall be delegated to a dedicated payment/finance domain when full finance is introduced. |
| SR-TR-007 | P1 | Attendance shall support present, absent, late and excused states and link an enrollment to a specific session. |
| SR-TR-008 | P1 | The system shall prevent duplicate attendance for an enrollment/session pair. |
| SR-TR-009 | P1 | The system shall calculate program completion eligibility from configured completion rules. |
| SR-TR-010 | P1 | The system shall generate a certificate with unique verification identifier for eligible participants. |

## 11. Legal Support Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-LE-001 | P0 | The system shall create legal tickets linked to a player and tenant. |
| SR-LE-002 | P0 | Legal tickets shall support open, in-progress, pending-review, resolved and closed states. |
| SR-LE-003 | P0 | Legal tickets shall support low, medium, high and urgent priorities. |
| SR-LE-004 | P0 | Tickets shall support assignment to authorized legal users and due dates. |
| SR-LE-005 | P0 | Legal notes shall record author, creation time and confidentiality flag. |
| SR-LE-006 | P0 | Internal/confidential legal notes shall never appear to users without the corresponding permission. |
| SR-LE-007 | P0 | Ticket, assignment, priority, status and due-date changes shall be audited. |
| SR-LE-008 | P1 | The system shall support attachments associated with the ticket and apply document security requirements. |
| SR-LE-009 | P1 | SLA monitoring shall expose overdue tickets and trigger configured notifications. |

## 12. Scouting Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-SC-001 | P1 | The system shall support scouting assignments with scout, assigner, region, competition, target position, age range, due date, status and notes. |
| SR-SC-002 | P1 | Scouting reports shall support existing players and external prospects not yet onboarded. |
| SR-SC-003 | P1 | Reports shall support draft, submitted, under review, approved and rejected states. |
| SR-SC-004 | P1 | Reports shall support recommendation levels strong sign, sign, monitor and not suitable. |
| SR-SC-005 | P1 | Reports shall support technical, physical, tactical, mental, overall and potential ratings plus narrative fields. |
| SR-SC-006 | P1 | Watchlists shall link users to players and preserve priority and notes. |
| SR-SC-007 | P1 | Scout assignment/report transitions shall be auditable. |

## 13. Communication and Realtime Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-CH-001 | P1 | The system shall support one-to-one and group conversations. |
| SR-CH-002 | P1 | Conversation membership shall be explicit; membership is required to read or send messages. |
| SR-CH-003 | P1 | Messages shall support text, file, image and system message types. |
| SR-CH-004 | P1 | Messages shall persist before successful send acknowledgement is returned. |
| SR-CH-005 | P1 | Edited messages shall retain edit state and timestamp. |
| SR-CH-006 | P1 | Message recall/deletion shall follow policy and preserve audit/evidence where required. |
| SR-CH-007 | P1 | Read state shall be persisted per conversation member. |
| SR-CH-008 | P1 | Websocket events shall be authorization checked and tenant scoped. |
| SR-CH-009 | P1 | Messaging shall be rate limited and support abuse/spam controls. |
| SR-CH-010 | P1 | File sharing in chat shall use the same secure object-storage pipeline as other documents. |

## 14. Notification Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-NF-001 | P0 | The system shall create in-app notifications for configured business events. |
| SR-NF-002 | P1 | Push notifications shall be sent through an approved provider with device/token lifecycle management. |
| SR-NF-003 | P1 | Email notification dispatch shall be asynchronous. |
| SR-NF-004 | P1 | Users shall configure supported notification preferences subject to mandatory security/compliance notifications. |
| SR-NF-005 | P1 | Notification delivery attempts shall be tracked per channel, including queued, sent/accepted, failed and retry state. |
| SR-NF-006 | P0 | Notification payloads shall not include confidential medical/legal/finance details unless explicitly authorized and policy-approved. |
| SR-NF-007 | P1 | Notifications shall deep-link only to resources the user is authorized to access. |

## 15. Audit and Compliance Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-AUD-001 | P0 | The system shall audit authentication events including successful login, failed login, lockout, logout and MFA changes. |
| SR-AUD-002 | P0 | The system shall audit creation, update, approval, assignment, export and deletion/archive of sensitive business records. |
| SR-AUD-003 | P0 | Audit entries shall contain actor, tenant, action, entity type, entity identifier and timestamp; IP/user-agent may be stored subject to privacy policy. |
| SR-AUD-004 | P0 | Where appropriate, audit records shall capture before/after values with sensitive fields redacted or encrypted according to policy. |
| SR-AUD-005 | P0 | Audit records shall not be editable/deletable through ordinary business APIs. |
| SR-AUD-006 | P1 | Audit search shall be restricted and support filters by actor, entity, action and date. |
| SR-AUD-007 | P0 | The system shall retain evidence required by approved retention policies and support legal hold where required in later releases. |

## 16. API Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-API-001 | P0 | All protected resource endpoints shall enforce authentication and authorization before data access. |
| SR-API-002 | P0 | Object identifiers shall never be treated as sufficient authorization; resource ownership/tenant scope shall be verified. |
| SR-API-003 | P0 | Endpoints shall reject unexpected or unauthorized object properties to prevent mass assignment. |
| SR-API-004 | P0 | Collection endpoints shall support filters only from an allowlist of fields/operators. |
| SR-API-005 | P1 | Write endpoints shall support optimistic concurrency/version checks for workflows where simultaneous edits are likely. |
| SR-API-006 | P1 | Bulk imports/exports shall be job-based and auditable. |
| SR-API-007 | P1 | Webhook receivers shall validate authenticity, timestamp/replay constraints and idempotency. |
| SR-API-008 | P0 | API rate limits shall be configured by category, with stricter limits for authentication, messaging, upload initiation, exports and privileged actions. |
| SR-API-009 | P1 | Public/shared endpoints, if introduced, shall be isolated from privileged internal endpoints and have independent throttling and token scope. |

## 17. Non-Functional Requirements

| ID | Pri | Requirement |
|---|---|---|
| SR-NFR-PERF-001 | P0 | For normal read/write API operations under the agreed capacity envelope, p95 latency shall be <= 500 ms for simple operations and <= 2 s for complex dashboard/report operations, excluding third-party network latency. |
| SR-NFR-PERF-002 | P1 | The system shall process large file uploads asynchronously without holding an HTTP request open for the full processing duration. |
| SR-NFR-PERF-003 | P1 | Database connection pool utilization shall be monitored and shall not routinely operate at exhaustion. |
| SR-NFR-SEC-001 | P0 | Security requirements shall be verified against OWASP ASVS 5.0 and relevant OWASP API Security Top 10 risks. |
| SR-NFR-SEC-002 | P0 | The application shall use least privilege for users, services and database roles. |
| SR-NFR-SEC-003 | P0 | No tenant may retrieve another tenant data through IDs, search, exports, websocket events, caches, queued jobs or file paths. |
| SR-NFR-A11Y-001 | P1 | The web interface shall target WCAG 2.2 Level AA. |
| SR-NFR-I18N-001 | P0 | The system shall support Arabic and English including RTL/LTR layouts and locale-aware formatting. |
| SR-NFR-REL-001 | P0 | Production availability target shall be 99.9% monthly. |
| SR-NFR-REL-002 | P0 | Backup and restore processes shall meet approved RPO/RTO targets and be tested periodically. |
| SR-NFR-OBS-001 | P0 | Production services shall expose health, readiness, metrics, structured logs and distributed trace context. |
| SR-NFR-MNT-001 | P1 | Critical business modules shall have automated unit, integration, authorization and end-to-end tests. |
| SR-NFR-MNT-002 | P1 | API and database migrations shall be backward compatible where practical and version-controlled. |

## 18. Database Requirements

- SR-DB-001: PostgreSQL shall be the system of record for transactional business data.
- SR-DB-002: Primary keys shall be UUID-based; time-sortable UUIDv7 may be used for high-ingest entities where supported and justified.
- SR-DB-003: Foreign keys and unique constraints shall enforce business identity and referential integrity.
- SR-DB-004: Tenant-owned entities shall carry tenant scope directly or through an unambiguous tenant-owned parent; security-critical repository queries shall enforce tenant scope.
- SR-DB-005: Database migrations shall be deterministic, reviewed and executed through CI/CD tooling rather than ad-hoc production changes.
- SR-DB-006: Indexes shall reflect tenant + common filter patterns; unused/duplicate indexes shall be monitored.
- SR-DB-007: JSON fields shall be used for genuinely extensible/metadata data, not as a substitute for frequently queried relational attributes.
- SR-DB-008: The schema shall not use polymorphic entity IDs for high-value referential-integrity paths without an explicit authorization and consistency mechanism.
- SR-DB-009: Audit tables shall be protected from ordinary delete/update operations.
- SR-DB-010: Sensitive secrets such as password-reset tokens and MFA secrets shall not be stored in recoverable plaintext.

## 19. Testing Requirements

| Test ID | Area | Coverage |
|---|---|---|
| TEST-001 | Unit | Domain services, validators, policy decisions, score calculations, state-transition logic |
| TEST-002 | Integration | Database constraints, repositories, transactions, object storage adapters, queue/outbox |
| TEST-003 | Authorization | BOLA/BFLA/property authorization, tenant isolation, confidential data leakage |
| TEST-004 | API contract | OpenAPI schema, status codes, error format, pagination, idempotency, webhook verification |
| TEST-005 | E2E | Player onboarding, contract lifecycle, legal ticket, training, chat, scouting, ratings |
| TEST-006 | Security | SAST, dependency scan, container scan, secret scan, DAST and penetration test |
| TEST-007 | Performance | Baseline load, p95 latency, concurrent websocket connections, upload throughput, queue behavior |
| TEST-008 | Recovery | Backup restore, point-in-time recovery where configured, object recovery, DR runbook |
| TEST-009 | Accessibility | Keyboard, focus, screen reader semantics, contrast, forms, RTL |
| TEST-010 | Localization | Arabic/English layout, formatting, translated states/errors and no hard-coded LTR assumptions |

## 20. Requirement Traceability

| Business ID | Objective | Product trace | Software trace |
|---|---|---|---|
| BR-OBJ-01 | Single authoritative player record | PRD-PL-001/002 | SR-PL-001..011 |
| BR-OBJ-02 | Contract/legal control | PRD-CT-* / PRD-LE-* | SR-CT-* / SR-LE-* |
| BR-OBJ-03 | Training and development | PRD-TR-* | SR-TR-* |
| BR-OBJ-04 | Performance and evaluation | PRD-PF-001 / PRD-RT-001 | SR-PF-* / SR-RT-* |
| BR-OBJ-05 | Sensitive-data protection | PRD product principles | SR-ACL-* / SR-MED-* / SR-NFR-SEC-* |
| BR-OBJ-06 | Communication and alerts | PRD-CH-* / PRD-NF-* | SR-CH-* / SR-NF-* |
| BR-OBJ-07 | Professional dossier | PRD-PL-003 | SR-PL-009/010 |
| BR-OBJ-08 | Scalable multi-tenant foundation | PRD roadmap | SR-CORE-* / SYS-TEN-* |
| BR-OBJ-09 | Governance/security/operations | PRD acceptance | SR-AUD-* / SR-NFR-* / SR-DB-* |

## 21. Implementation Notes for the Supplied Schema

The supplied schema is a strong starting point for the MVP domain model, but it should be treated as a baseline rather than a complete production schema. In particular, the implementation should resolve the player-to-user identity relationship, organization/match modeling, e-signature evidence, certificates, notification delivery state, finance domain, rating-scheme versioning, medical field typing, and tenant-safe nullable relationships before those workflows are declared production-ready.

- Player identity link: Player exists as a domain entity, but User does not directly link to Player. Recommended: Add explicit PlayerUser/Player.user relation and define account ownership.
- Organizations / clubs: Player.currentClub is stored as free text; no Club/Team/Competition model exists. Recommended: Add Club/Organization, Team, Competition and player affiliation/history entities for transfers and analytics.
- Matches: PerformanceRecord stores opponent, venue and competition as strings. Recommended: Add Match and PlayerMatchStat model(s) when advanced analytics, line-ups and match entities are required.
- Finance: FinanceManager exists and contracts contain salary/bonus fields, while training enrollment contains payment state. Recommended: Add invoices, payments, financial transactions, salary components and settlement records before full finance scope.
- E-signature: Contract approval/versioning exists but no signature envelope/participant/provider audit model exists. Recommended: Add SignatureEnvelope, Signatory, SignatureEvent and immutable evidence metadata.
- Certificates: Training supports enrollment and attendance but no certificate entity is modeled. Recommended: Add Certificate and certificate template/verification data.
- Notification delivery: Notification is in-app oriented; no per-channel delivery attempt state is present. Recommended: Add NotificationDelivery/outbox records with provider IDs, status, retry count and timestamps.
- Tenant-safe nullable relations: Some nullable/sender/assignee relations are intentionally single-field relations in the schema. Recommended: Enforce tenant-aware authorization at service/repository boundaries and consider composite FK hardening.
- Medical typing: MedicalRecord defines injury-related enums but the model currently stores injuryType and severity as strings. Recommended: Use controlled enums/reference tables and validation; allow extensibility through coded dictionaries.
- Rating governance: Rating stores technical/physical/mental plus average-derived total, while the product concept calls for weighted scoring. Recommended: Introduce RatingScheme/Criteria/Version and store the applied scheme/version with each rating.
- Currency and positions: Currency and PlayerPosition are fixed enums. Recommended: Use reference data/configuration for extensibility if international growth is expected.
- Audit immutability: AuditLog includes deletedAt. Recommended: Audit evidence should be append-only from the application perspective, with restricted retention/purge procedures.

## 22. Definition of Done for Production

- All P0 requirements implemented and accepted.
- P1 requirements for the target release implemented and accepted.
- Traceability shows each business objective has at least one product and software implementation path.
- Authorization and tenant-isolation tests are automated and included in release gates.
- Security baseline completed against ASVS/API risks with findings triaged.
- Database backup/restore and DR tested.
- Monitoring/alerting and incident runbooks are live.
- Accessibility and Arabic/English acceptance completed.
- OpenAPI and user documentation published for the release.
- Known limitations and deferred requirements are documented in the release notes and backlog.

## R. References and Standards

- ISO/IEC/IEEE 29148:2018 - Requirements engineering; use as the requirements-writing and traceability baseline.
- ISO/IEC/IEEE 12207:2026 - Software life cycle processes; use for lifecycle governance and development/operations process alignment.
- ISO/IEC 25010:2023 - Product quality model; use to structure non-functional and quality requirements.
- ISO/IEC 27001:2022 - Information security management system; use as the security governance target where certification is pursued.
- ISO/IEC 27701:2025 - Privacy information management system; use for PII governance and privacy accountability where applicable.
- OWASP ASVS 5.0.0 - Application security verification baseline.
- OWASP API Security Top 10 (2023) - API-specific security risk baseline.
- NIST SP 800-207 - Zero Trust Architecture principles for identity/resource-oriented access control.
- NIST SP 800-218 SSDF 1.1 - Secure software development practices integrated into the SDLC.
- WCAG 2.2 - Accessibility requirements; target Level AA.
- ISO 19005 / PDF/A - Consider archival PDF/A for long-term contractual/document preservation.
- FIFA Football Agent Regulations and applicable national regulations - domain/compliance inputs for agency operations; legal counsel must validate jurisdictional requirements.
- eIDAS Regulation (EU) No 910/2014, as amended - reference when serving EU users or relying on EU trust services/e-signatures; local laws govern other jurisdictions.

Current technology verification (28 September 2026): Next.js 16.3.x is an Active LTS line; Node.js 24 is LTS; PostgreSQL 18 is the current major line and PostgreSQL 18.6 was released 13 August 2026. Prisma ORM 7 is the stable baseline while Prisma ORM 8 is in release-candidate status. Exact production patch versions must be pinned during implementation.

These references are architecture and requirements baselines, not legal advice. Jurisdiction-specific contractual, employment, medical-data, privacy, payment, tax, child-protection, and electronic-signature obligations require legal/compliance review before production use.
