<!-- Frozen baseline: faithful Markdown conversion of source/03_Sodara_SysRD.docx (converted 28 September 2026).
     Do not edit. Changes go through change control in README.md; the .docx is the original. -->

SODARA PLATFORM

System Requirements Document (SysRD)

Sodara Platform - System Architecture and Operational Requirements

Version 1.0 | Requirements Baseline | 28 September 2026

Status: Draft for stakeholder validation and architecture sign-off

## 0. Document Control

| Field | Value |
|---|---|
| Document | Sodara Platform - System Requirements Document (SysRD) |
| Version | 1.0 |
| Date | 28 September 2026 |
| Status | Draft baseline |
| Language | English |
| Primary objective | Define the complete system boundary, architecture, deployment, security, data, integration, operational, resilience and platform requirements needed to realize the product. |
| Primary audience | Solution architect, system architect, security architect, DevOps/SRE, engineering leads, QA, product and domain owners. |
| Source baseline | Sodara concept brief + supplied Prisma/PostgreSQL schema |
| Requirement method | ISO/IEC/IEEE 29148-aligned structure with explicit identifiers and acceptance intent |

Traceability rule: business requirements are refined into product requirements, then system requirements, then software requirements. Requirement IDs are stable and must not be reused after baseline approval.

## 1. System Purpose and Boundary

The Sodara system consists of a responsive web client, API/application services, realtime communication gateway, asynchronous worker services, relational data store, object storage, identity provider, notification providers, observability stack, and external integration adapters. The system is designed as a modular monolith initially, with clear domain boundaries that permit later service extraction.

## 2. Recommended Architecture

| Layer | Recommended technology | Responsibility |
|---|---|---|
| Web experience | Next.js 16.3 + React 19 + TypeScript | Responsive UI, SSR/RSC where beneficial, forms, localization, dashboards, client state for interactive components |
| API/application | NestJS 11 + TypeScript | Domain modules, validation, authorization, REST/OpenAPI endpoints, orchestration |
| Realtime | Socket.IO/WebSocket gateway | Chat events, notifications, presence/read state where enabled |
| Identity | OIDC provider (Keycloak or managed provider) | Authentication, MFA, session/credential lifecycle; application receives verified identity claims |
| Data access | Prisma ORM 7 | Typed persistence, migrations, transaction boundary |
| Database | PostgreSQL 18 | Authoritative business data, transactional consistency, indexes, reporting queries |
| Cache / queue | Redis or Valkey + BullMQ | Caching, rate limits, background work and retry queues |
| File storage | S3/MinIO | Documents, images, video objects; private by default |
| Media pipeline | FFmpeg worker | Transcoding, thumbnails, metadata extraction, optional waveform generation |
| Search | PostgreSQL FTS/trigram; OpenSearch later | Cross-module search within authorization scope |
| Observability | OpenTelemetry + Prometheus/Grafana + logs + Sentry | Traces, metrics, logs, errors, alerts |
| Edge | Nginx/Traefik/Caddy or managed ingress | TLS, routing, rate limiting/WAF integration, compression |

## 3. Architecture Style and Evolution

- SYS-ARC-001: Use a modular monolith for the initial product. Each domain has its own application module, persistence access pattern and policy boundary.
- SYS-ARC-002: Avoid direct cross-module table manipulation. Modules communicate through application services, commands/events or stable interfaces.
- SYS-ARC-003: Keep the API contract independent of the persistence schema. Database refactors must not automatically become API breaking changes.
- SYS-ARC-004: Introduce microservices only where a measurable requirement exists, such as independent scaling, fault isolation or organizational ownership.
- SYS-ARC-005: Background jobs and realtime gateways are separate runtime processes from the main HTTP process even if they share the same codebase.

## 4. Multi-Tenancy and Isolation

The authoritative tenant model is Tenant. The supplied schema places tenantId on the core domain models and uses several composite relationships. The system shall use defense-in-depth rather than relying on a single middleware check.

- SYS-TEN-001: Establish tenant context from a trusted authenticated principal, never from an arbitrary request body/query field.
- SYS-TEN-002: Every tenant-owned query path must be tenant-scoped; repositories/services must make tenant scope mandatory.
- SYS-TEN-003: Object-level authorization must verify both object identity and tenant membership.
- SYS-TEN-004: Database constraints should prevent accidental cross-tenant foreign-key relationships where practical; composite (id, tenantId) references are preferred.
- SYS-TEN-005: Consider PostgreSQL Row Level Security as an additional defense for the highest-risk tables once operational patterns are validated.
- SYS-TEN-006: Exports, search indexes, caches, queued jobs, object-storage prefixes and websocket rooms must carry tenant context.
- SYS-TEN-007: Tenant context must be included in correlation/trace attributes but never exposed to unauthorized users.
- SYS-TEN-008: Support/admin tooling must explicitly select an approved support context and produce an audit event for elevation.

## 5. Identity and Access Architecture

- Authentication: OIDC/OAuth-based identity provider; MFA required for privileged roles and configurable for all users.
- Session model: short-lived access token, rotating refresh tokens, device/session revocation, secure logout, passwordless or passkey support as an optional future capability.
- Authorization: RBAC determines baseline permissions; ABAC/policy layer evaluates tenant, user relationship, ownership, confidentiality level, lifecycle state and action.
- Service authorization: background workers use service identities and scoped credentials rather than user tokens copied into jobs.
- Privileged actions: contract approvals, signature initiation, exports, permission changes and support impersonation require stronger controls and audit.
- Emergency access: break-glass access is time-bound, reason-coded, and auditable.

## 6. Data Architecture

- The supplied Prisma schema uses PostgreSQL and contains 29 model definitions and 26 enums.
- The model set covers tenant/user management, players and media, medical records and treatment sessions, contracts/versioning/approvals, performance and ratings, training/sessions/enrollment/attendance, legal tickets/notes, realtime conversations/messages, notifications, audit logs, permissions, and scouting/watchlists/assignments.
- The schema therefore represents a broad agency management platform rather than a simple player CRM.

| Domain | Current schema entities | System responsibility |
|---|---|---|
| Core tenant/user | Tenant, User, Permission, RolePermission | Identity context, tenant settings, roles and permission catalog |
| Players | Player, PlayerMedia, Document | Player master record, media and evidence |
| Medical | MedicalRecord, TreatmentSession | Restricted health/rehab records |
| Contracts | Contract, ContractVersion, ContractApproval, Season | Lifecycle, approvals and historical versions |
| Performance | PerformanceRecord, Rating, Season | Match performance and evaluation |
| Training | Training, TrainingSession, Enrollment, Attendance | Programs, sessions and participation |
| Legal | LegalTicket, LegalNote | Casework and legal evidence |
| Communication | Conversation, ConversationMember, Message | Messaging and read states |
| Scouting | ScoutingReport, PlayerWatchlist, ScoutingAssignment | Recruitment pipeline |
| Platform services | Notification, AuditLog, Document | Notifications, audit and document abstraction |

## 7. Schema Hardening Requirements

### 7.1 Player identity link

Observed: Player exists as a domain entity, but User does not directly link to Player.

Recommended: Add explicit PlayerUser/Player.user relation and define account ownership.

### 7.2 Organizations / clubs

Observed: Player.currentClub is stored as free text; no Club/Team/Competition model exists.

Recommended: Add Club/Organization, Team, Competition and player affiliation/history entities for transfers and analytics.

### 7.3 Matches

Observed: PerformanceRecord stores opponent, venue and competition as strings.

Recommended: Add Match and PlayerMatchStat model(s) when advanced analytics, line-ups and match entities are required.

### 7.4 Finance

Observed: FinanceManager exists and contracts contain salary/bonus fields, while training enrollment contains payment state.

Recommended: Add invoices, payments, financial transactions, salary components and settlement records before full finance scope.

### 7.5 E-signature

Observed: Contract approval/versioning exists but no signature envelope/participant/provider audit model exists.

Recommended: Add SignatureEnvelope, Signatory, SignatureEvent and immutable evidence metadata.

### 7.6 Certificates

Observed: Training supports enrollment and attendance but no certificate entity is modeled.

Recommended: Add Certificate and certificate template/verification data.

### 7.7 Notification delivery

Observed: Notification is in-app oriented; no per-channel delivery attempt state is present.

Recommended: Add NotificationDelivery/outbox records with provider IDs, status, retry count and timestamps.

### 7.8 Tenant-safe nullable relations

Observed: Some nullable/sender/assignee relations are intentionally single-field relations in the schema.

Recommended: Enforce tenant-aware authorization at service/repository boundaries and consider composite FK hardening.

### 7.9 Medical typing

Observed: MedicalRecord defines injury-related enums but the model currently stores injuryType and severity as strings.

Recommended: Use controlled enums/reference tables and validation; allow extensibility through coded dictionaries.

### 7.10 Rating governance

Observed: Rating stores technical/physical/mental plus average-derived total, while the product concept calls for weighted scoring.

Recommended: Introduce RatingScheme/Criteria/Version and store the applied scheme/version with each rating.

### 7.11 Currency and positions

Observed: Currency and PlayerPosition are fixed enums.

Recommended: Use reference data/configuration for extensibility if international growth is expected.

### 7.12 Audit immutability

Observed: AuditLog includes deletedAt.

Recommended: Audit evidence should be append-only from the application perspective, with restricted retention/purge procedures.

## 8. Document and Media Architecture

- Store object metadata in the relational database and binary content in private object storage.
- Use opaque object keys such as tenant/{tenantId}/entity/{entityId}/...; never construct storage paths directly from untrusted filenames.
- Generate signed URLs with short TTL for authorized downloads and uploads.
- Validate MIME type, extension, magic bytes, file size, content disposition and malware status before finalizing an object.
- Use multipart/chunked upload for large media. Complete uploads through an explicit upload session or callback.
- For videos, ingest -> virus/malware scan -> metadata extraction -> transcode -> thumbnail -> searchable/streamable variants.
- Use retention classes for contracts, medical evidence, legal evidence, ordinary media and temporary uploads.
- Preserve contract/legal evidence in immutable or WORM-capable storage when required by policy/regulation.

## 9. Integration Architecture

| Integration | Pattern | Failure strategy |
|---|---|---|
| Identity provider | OIDC | Fail closed for protected actions; cache public keys safely; support key rotation |
| Email | Provider API/SMTP adapter | Outbox + retries + dead-letter state; do not block business transaction on provider latency |
| Push | FCM | Queue delivery; track provider message ID and status |
| E-signature | Provider API + webhook | Idempotent callbacks; store evidence; verify signatures on webhook requests |
| Payment gateway | API + webhook | Idempotency keys; reconcile webhook events with payment records |
| Object storage | S3 API | Presigned operations; retry transient failures; orphan cleanup |
| Calendar (future) | OAuth/API | Least-privilege scopes; user consent |
| External club sharing (future) | Secure portal/API | Explicit per-player share consent, scope and expiration |

## 10. Asynchronous Processing

- SYS-ASY-001: Any operation expected to exceed normal request latency, including video processing, certificate rendering, large imports, bulk notifications and report generation, must execute asynchronously.
- SYS-ASY-002: Jobs must be idempotent or have a deterministic deduplication key.
- SYS-ASY-003: Job payloads must contain tenant context and a stable business reference, not confidential data copied unnecessarily.
- SYS-ASY-004: Retries use bounded exponential backoff and dead-letter/failed-job state.
- SYS-ASY-005: Critical workflows must not depend solely on an external queue; the database transaction creates an outbox/event record before a worker processes it.

## 11. Realtime Architecture

- Authenticate websocket connections using the same identity and tenant policy as REST.
- Authorize conversation membership for every message send/read operation.
- Use tenant-scoped rooms and conversation-scoped rooms.
- Persist message state before broadcasting success to clients.
- Use delivery/read timestamps as durable state; realtime events are only notifications of state changes.
- Rate-limit sends per user/conversation and enforce file size/type controls.
- Reconnect clients using last-known event/read timestamp or API synchronization instead of assuming no events were missed.

## 12. Security Architecture

- Use TLS 1.2+ with modern configuration; HTTPS only in production.
- Use secure headers including CSP appropriate to the app, HSTS where safe, frame protections, content-type protections and referrer policy.
- Use CSRF protection where browser cookie credentials are used; avoid unsafe cross-origin credential patterns.
- Validate and normalize all inputs; use ORM parameterization and never concatenate SQL with user input.
- Apply object-level and function-level authorization at service boundaries, addressing OWASP API risks such as BOLA and BFLA.
- Rate-limit authentication, password reset, uploads, messaging, exports and sensitive workflows.
- Log security events without passwords, tokens, raw medical details or other restricted content.
- Encrypt secrets using a dedicated secret store; rotate keys and credentials.
- Encrypt sensitive application data where threat model and legal policy justify field-level encryption; protect encryption keys separately.
- Perform dependency, SAST, DAST, container, infrastructure and secret scanning in CI/CD.
- Conduct tenant-isolation and authorization abuse testing before production.

## 13. Operational Resilience

| Requirement | Baseline target | Implementation note |
|---|---|---|
| Availability | 99.9% monthly | Exclude approved maintenance only; measure externally and internally |
| RPO | <= 24 hours MVP; target <= 1 hour later | Depends on backup/PITR design and business criticality |
| RTO | <= 8 hours MVP; target <= 4 hours later | Depends on infrastructure recovery and runbooks |
| Backups | Daily full + continuous/WAL/PITR where supported | Encrypted, tested restore, cross-environment/cross-zone copy as justified |
| DR test | At least twice yearly | Restore database, object storage metadata and configuration |
| Monitoring | 24x7 alerting for production critical paths | Health, latency, errors, queue backlog, storage, database, auth, certificate expiry |
| Incident response | Defined severity levels and runbooks | Security incidents include tenant-isolation escalation path |

## 14. Observability

- Use OpenTelemetry for traces, metrics and logs; propagate W3C trace context where supported.
- Every request receives a correlation/request ID.
- Metrics include latency, error rate, throughput, DB pool saturation, queue latency/backlog, websocket connections, upload rates and notification delivery.
- Structured logs include timestamp, service, environment, tenant context (non-sensitive), actor ID where allowed, request ID and outcome.
- Sentry or equivalent captures application exceptions with PII scrubbing.
- Dashboards are role appropriate; operational dashboards must not expose restricted business data unnecessarily.

## 15. Deployment and Environments

| Environment | Purpose | Data policy |
|---|---|---|
| Local | Developer workflow | Synthetic/local data only |
| Development | Feature integration | Synthetic/anonymized data |
| Test/QA | Automated + manual acceptance | Synthetic test fixtures |
| Staging | Production-like release candidate | Anonymized or approved synthetic data |
| Production | Live service | Real data; strongest controls |

- Infrastructure must be reproducible through IaC or documented deployment manifests.
- Database migrations are forward-compatible when practical and automatically checked in CI.
- Feature flags allow controlled activation of risky or incomplete functionality.
- Secrets are environment-injected and absent from source control.

## 16. Capacity Planning

The initial capacity model should be expressed using tenants, users/tenant, players/tenant, documents/player, video GB/tenant/month, messages/day, performance records/player/season, training sessions/month, and concurrent websocket connections. The architecture should support horizontal application scaling while PostgreSQL remains the transactional system of record. Read replicas, partitioning or service extraction are optimization responses to measured load, not default complexity.

## 17. Technical Acceptance Criteria

- Cross-tenant access attempts fail consistently at API, websocket, storage and background-job boundaries.
- Critical data mutations produce audit evidence.
- Database constraints prevent known referential integrity failures.
- Recovery tests demonstrate the documented RPO/RTO targets.
- OpenAPI specification matches deployed endpoints for the approved version.
- Observability identifies a request across web -> API -> DB/queue -> worker -> external provider.
- Load tests demonstrate agreed performance at the capacity envelope.
- Security verification maps to OWASP ASVS and API Security risks.

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
