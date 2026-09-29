<!-- Frozen baseline: faithful Markdown conversion of source/02_Sadara_PRD.docx (converted 28 September 2026;
     product name corrected to Sadara on 29 September 2026). Do not edit — change control is in README.md. -->

SADARA PLATFORM

Product Requirements Document (PRD)

Sadara Player Management Platform

Version 1.0 | Requirements Baseline | 28 September 2026

Status: Draft for stakeholder validation and architecture sign-off

## 0. Document Control

| Field | Value |
|---|---|
| Document | Sadara Platform - Product Requirements Document (PRD) |
| Version | 1.0 |
| Date | 28 September 2026 |
| Status | Draft baseline |
| Language | English |
| Primary objective | Translate business outcomes into a coherent product experience, user journeys, capabilities, priorities, UX behavior, measurable outcomes and release criteria. |
| Primary audience | Product owner, UX/UI, engineering, QA, business stakeholders, domain owners. |
| Source baseline | Sadara concept brief + supplied Prisma/PostgreSQL schema |
| Requirement method | ISO/IEC/IEEE 29148-aligned structure with explicit identifiers and acceptance intent |

Traceability rule: business requirements are refined into product requirements, then system requirements, then software requirements. Requirement IDs are stable and must not be reused after baseline approval.

## 1. Product Vision

Make Sadara the operational command center for every player relationship: one profile, one timeline, one controlled document space, one communication layer, and one evidence-based view of sporting, legal, medical, training and commercial status.

## 2. Product Principles

- Player-centric: the player is the primary business object and cross-module navigation should start from the player journey.
- One source of truth: derived dashboards must trace to authoritative records.
- Privacy by design: sensitive information is hidden by default and revealed only by policy.
- Workflow over free-form status changes: approvals, signatures, tickets and attendance follow explicit state models.
- Fast daily operations: common tasks should take seconds, not complex navigation.
- API-first and mobile-ready: web experience is the first client, not the only future client.
- Bilingual and RTL-native: Arabic is a first-class locale, not a translated afterthought.
- Progressive disclosure: expert workflows expose complexity only when needed.
- Human-in-the-loop intelligence: AI may assist, summarize or flag; authorized staff remain decision makers.

## 3. Personas and Primary Jobs

| Persona | Top jobs-to-be-done | Key product surface |
|---|---|---|
| Executive/Owner | Understand portfolio health and approve critical actions | Executive dashboard, approvals, player portfolio, reports |
| Administrator | Maintain users/data and resolve routine operational work | Admin center, players, documents, notifications, audit |
| Sporting Director | Recruit, evaluate and manage player development | Player 360, scouting, watchlists, performance, ratings |
| Scout | Find and evaluate prospects | Assignments, reports, watchlists, media |
| Coach/Staff | Deliver and evaluate sporting development | Training, attendance, player performance and ratings |
| Medical/Physio | Track injury and rehabilitation safely | Restricted medical workspace, treatments, RTP |
| Legal | Control contracts and legal cases | Contract workspace, approvals, tickets, document evidence |
| Finance | Track compensation and payments | Finance workspace and contract economics |
| Training Manager | Plan programs and measure participation | Training calendar, enrollment, attendance, certificates |
| Player | Maintain approved personal data and receive services | Player portal, profile, contracts, training, messages |
| Guardian | Support academy player within assigned permissions | Restricted player portal |

## 4. Information Architecture

| Navigation area | Major destinations |
|---|---|
| Home | Personalized dashboard, tasks, alerts, upcoming events |
| Players | Directory, player 360, profiles, media, documents, medical (permission gated), timeline |
| Contracts | Contracts, expiring, approvals, versions, signature status |
| Scouting | Assignments, prospects, reports, watchlists |
| Performance | Matches/records, KPIs, ratings, comparisons |
| Training | Programs, sessions, calendar, enrollment, attendance, certificates |
| Legal | Tickets, queues, due dates, notes, attachments |
| Communication | Conversations, unread, search, archived |
| Reports | Operational reports, exports, scheduled reports |
| Administration | Users, roles, permissions, tenant settings, audit, feature flags |

## 5. Feature Requirements and Priorities

| ID | Feature | Priority | Definition of success |
|---|---|---|---|
| PRD-PL-001 | Player 360 profile | P0 | Authorized staff see identity, status, club, positions, media, contracts, performance, training, legal and activity summary from one page. |
| PRD-PL-002 | Profile completeness | P0 | System identifies missing required information by lifecycle stage. |
| PRD-PL-003 | Player dossier export/share | P1 | Generate an approved shareable profile package with configurable fields, media and expiry. |
| PRD-CT-001 | Contract lifecycle | P0 | Draft/review/approve/sign/archive is visible and auditable. |
| PRD-CT-002 | Expiry monitoring | P0 | Upcoming expiries appear on dashboard and generate configured notifications. |
| PRD-CT-003 | Version comparison | P1 | Users can see version history and change notes without overwriting prior versions. |
| PRD-LE-001 | Legal ticketing | P0 | Ticket creation, assignment, priority, SLA, notes, files and closure are controlled. |
| PRD-ME-001 | Medical workspace | P1 | Authorized medical staff manage records, injuries and treatment sessions; non-medical users see only allowed summary. |
| PRD-TR-001 | Training/camp management | P1 | Create programs, sessions, capacity, pricing, registration and attendance. |
| PRD-TR-002 | Certificate generation | P1 | Eligible participants receive digitally verifiable certificates. |
| PRD-PF-001 | Performance records | P1 | Capture/import match statistics and display trends by player/season. |
| PRD-RT-001 | Player rating | P1 | Periodic ratings use a governed scheme and preserve historical scores. |
| PRD-SC-001 | Scouting pipeline | P1 | Assignments, reports, prospects, recommendations and watchlists support recruitment workflow. |
| PRD-CH-001 | Internal communication | P1 | 1:1/group conversations support text/media/files, unread state and retention. |
| PRD-NF-001 | Notification center | P0 | Users see actionable in-app notifications with deep links and preference controls. |
| PRD-AD-001 | Admin and audit | P0 | Authorized administrators manage users/settings and audit critical actions. |

## 6. User Journeys

### 6.1 Player onboarding

Admin creates player -> system checks potential duplicates -> required profile fields shown -> documents/media uploaded -> sporting/medical/legal sections completed as allowed -> profile completeness reaches threshold -> player activated -> onboarding notifications sent.

### 6.2 Contract approval/signature

Authorized user drafts contract -> uploads or generates version -> legal reviews -> approval steps execute in order -> authorized signatories sign through approved provider -> signature evidence captured -> contract marked signed -> reminders scheduled.

### 6.3 Legal request

User selects player -> creates ticket -> priority/due date set -> legal assignee notified -> notes/files exchanged -> legal resolves -> requester confirms/closure -> full audit retained.

### 6.4 Training enrollment

Player or staff selects program -> eligibility/capacity check -> payment state recorded if applicable -> enrollment approved -> calendar/reminders created -> session attendance recorded -> completion checked -> certificate issued.

### 6.5 Scouting report

Scout opens assignment -> creates report for existing player or prospect -> scores dimensions -> writes strengths/weaknesses/fit -> submits -> sporting director reviews -> approves/rejects -> watchlist/onboarding action created.

### 6.6 Performance review

Analyst imports/enters records -> validation -> player trend view -> evaluator creates rating using current scheme -> report generated -> historical comparison available.

### 6.7 Player communication

User opens permitted conversation -> sends message/file -> recipient receives realtime event and notification -> read receipt updates -> conversation remains searchable and auditable under policy.

## 7. UX Requirements

- UX-001: Every screen must expose tenant and user context implicitly and must never allow changing tenant through a client-controlled ID alone.
- UX-002: Destructive actions require clear confirmation and explain the consequence (delete/archive/terminate/reject).
- UX-003: Forms show field-level validation, server-side validation errors, and preserve non-sensitive user input after recoverable errors.
- UX-004: Long tables provide server-side pagination, filter chips, sort, saved views where useful, and keyboard accessibility.
- UX-005: Player 360 uses tabs or sections so sensitive medical/legal areas are visually and permission gated rather than mixed into the default summary.
- UX-006: Contract status and deadlines use a consistent visual language and calendar semantics.
- UX-007: All user-facing dates/times use tenant timezone; timestamps can reveal the exact absolute time where audit precision matters.
- UX-008: Arabic uses RTL layout; English uses LTR; switching language must not change underlying business data.
- UX-009: Mobile-responsive web is required from launch; complex video/media management remains optimized for desktop but remains usable on smaller screens.
- UX-010: Empty states explain why data is absent and provide the next available action.
- UX-011: Loading, error and offline/retry states are explicit; no silent failures.
- UX-012: WCAG 2.2 AA is the product accessibility target.

## 8. Search, Filters and Reporting

- Global search should locate players, contracts, legal tickets, trainings, conversations and documents only within the user authorization scope.
- Player search supports name, position, status, club, nationality and other approved indexed fields.
- Contract views support status, player, expiry range, season and owner/assignee filters.
- Legal queues support status, priority, assignee and due-date/SLA filters.
- Training views support date ranges, capacity, status and enrollment state.
- Reports must reveal source period and generation timestamp and should carry an export audit event.
- Exports must be permission gated and must exclude confidential fields unless explicitly allowed.

## 9. Notifications

| Trigger | In-app | Push | Email | Default timing |
|---|---|---|---|---|
| Contract approved/rejected | Yes | Yes | Configurable | Immediate |
| Contract expiring | Yes | Yes | Yes | Configurable reminders, e.g. 90/30/7 days |
| New message | Yes | Yes | Configurable | Immediate |
| Training reminder | Yes | Yes | Optional | Configurable |
| Enrollment state changed | Yes | Yes | Optional | Immediate |
| Legal ticket created/updated | Yes | Yes | Optional | Immediate |
| Medical record added | Permission gated | Permission gated | Usually off by default | Immediate only for authorized recipients |
| System/security alert | Yes | Yes | Yes for critical events | Immediate |

## 10. Product Analytics

- Activation: percentage of new users who complete profile and access key workflows.
- Operational adoption: daily/weekly active users by role and module.
- Workflow throughput: contracts, tickets, trainings and scouting reports completed per period.
- Time-to-action: median time from event creation to first responsible-user action.
- Data quality: validation failures, duplicates and incomplete profiles.
- Security telemetry: failed logins, MFA enrollment, privilege changes, export events, abnormal access patterns.
- User experience: task completion, error rate, response time and search success.

## 11. Product Acceptance Criteria

- All P0 features have positive and negative acceptance scenarios.
- All domain owners approve business-rule behavior for their module.
- Tenant-isolation tests demonstrate that object IDs from another tenant cannot be used to read, mutate, delete or export data.
- Confidential-data tests show medical/legal/finance data is absent from unauthorized responses, search, notifications and logs.
- Critical contract workflows produce a complete audit trail.
- Arabic/English UI is functionally equivalent for supported features.
- Core workflows meet defined performance, accessibility and reliability targets.
- Production readiness review confirms backup, restoration, monitoring, alerting, incident response and vulnerability management are operational.

## 12. Future Product Capabilities

- External club-facing secure player dossier portal.
- Player mobile apps for iOS/Android using the same API and identity system.
- AI-assisted scouting summaries, video tagging, report summarization and anomaly detection with human approval.
- Injury-risk analytics using approved and consented data; not a diagnosis engine.
- Market intelligence/valuation with transparent methodology and confidence intervals.
- Calendar and productivity integrations.
- Partner/agency ecosystem APIs and webhooks.

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
