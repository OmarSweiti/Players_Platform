<!-- Frozen baseline: faithful Markdown conversion of source/01_Sadara_BRD.docx (converted 28 September 2026;
     product name corrected to Sadara on 29 September 2026). Do not edit — change control is in README.md. -->

SADARA PLATFORM

Business Requirements Document (BRD)

Sadara Sports Agency - Player Management Platform

Version 1.0 | Requirements Baseline | 28 September 2026

Status: Draft for stakeholder validation and architecture sign-off

## 0. Document Control

| Field | Value |
|---|---|
| Document | Sadara Platform - Business Requirements Document (BRD) |
| Version | 1.0 |
| Date | 28 September 2026 |
| Status | Draft baseline |
| Language | English |
| Primary objective | Define the business problem, outcomes, capabilities, stakeholders, business rules, KPIs, risks, and operating model for the Sadara Platform. |
| Primary audience | Agency leadership, business owners, legal, sporting, medical, finance, training, product, technology, implementation partner. |
| Source baseline | Sadara concept brief + supplied Prisma/PostgreSQL schema |
| Requirement method | ISO/IEC/IEEE 29148-aligned structure with explicit identifiers and acceptance intent |

Traceability rule: business requirements are refined into product requirements, then system requirements, then software requirements. Requirement IDs are stable and must not be reused after baseline approval.

## 1. Executive Summary

Sadara Platform is a digital operating platform for a sports agency to manage players across the player lifecycle: onboarding, profile management, contracts, legal support, scouting, performance, training and development, medical/rehabilitation, communication, notifications, evaluation, documents, and management reporting. The target operating model is a controlled multi-tenant SaaS foundation, while the initial deployment may serve Sadara as the first tenant.

The business case is not simply digitizing records. The platform should create a single operational record for each player, reduce manual coordination between departments, improve contract and legal control, turn performance data into actionable insight, and produce a professional player dossier that can be shared with authorized external parties.

## 2. Business Context and Problem Statement

Sports-agency operations often span multiple specialist functions that each hold partial player information. Without a shared operating model, the agency is exposed to duplicated data entry, missed deadlines, inconsistent player profiles, unmanaged documents, fragmented communication, weak auditability, and slow preparation of player presentations.

The supplied data model confirms that the intended scope extends beyond the initial seven modules. It already includes 29 domain models and 26 enums covering scouting, medical treatment, contract approvals and versions, attendance, legal tickets, messaging, permissions, notifications and audit logs. The business requirements therefore treat these as first-class capabilities, not future-only ideas.

## 3. Business Objectives

| ID | Objective |
|---|---|
| BR-OBJ-01 | Create one authoritative digital player record across all agency departments. |
| BR-OBJ-02 | Reduce manual contract, legal and document administration and improve deadline visibility. |
| BR-OBJ-03 | Create a repeatable process for training, camps, attendance and player development. |
| BR-OBJ-04 | Provide reliable performance and evaluation history across seasons and periods. |
| BR-OBJ-05 | Protect sensitive medical, legal and financial information through role and context based access. |
| BR-OBJ-06 | Provide auditable internal communication and operational notifications. |
| BR-OBJ-07 | Enable generation of professional player profiles/dossiers for authorized club-facing use. |
| BR-OBJ-08 | Create a scalable product foundation that can later support additional agencies/tenants. |
| BR-OBJ-09 | Establish reliable data, security and operational governance suitable for commercial operation. |

## 4. Stakeholders

| Stakeholder | Interest / responsibility | Primary information need |
|---|---|---|
| Agency Owner / Executive | Strategy, commercial outcomes, approvals | Portfolio health, contracts, player status, performance, risks, financial and operational dashboards |
| General/Admin | Daily operations and administration | Player records, tasks, documents, users, notifications, audit |
| Sporting Director | Squad planning and recruitment | Players, contracts, scouting, watchlists, development, performance |
| Scout | Talent discovery and evaluation | Assignments, prospects, reports, recommendations, watchlists |
| Coach / Assistant / GK / Fitness | Sporting development | Performance, ratings, training, attendance, development notes |
| Medical / Physiotherapist | Health and rehabilitation | Restricted medical records, injuries, treatment sessions, return-to-play |
| Legal | Contracts and casework | Contract versions, approvals, tickets, notes, deadlines, evidence |
| Finance Manager | Commercial/financial operations | Compensation terms, payments, invoices and financial transactions |
| Training Manager | Courses/camps/events | Training programs, sessions, enrollments, attendance, certificates |
| Player | Own profile and assigned services | Profile, agreements, training, messages, notifications, selected reports |
| Guardian | Academy-age player support when applicable | Limited child/player records and administrative actions |
| Platform Super Admin | SaaS operation | Tenants, platform health, support, security, configuration |

## 5. Business Scope

| Capability | In scope | Business outcome |
|---|---|---|
| Player Management | Profiles, media, documents, statuses, identity and player dossier | Single source of truth and professional player representation |
| Contract Management | Draft/review/approval/sign/archive/version/expiry | Controlled lifecycle and fewer missed obligations |
| Legal Support | Tickets, assignment, notes, attachments, SLA visibility | Centralized legal case management |
| Scouting | Prospects, reports, assignments, watchlists, recommendations | Structured talent pipeline and institutional scouting knowledge |
| Performance | Match records, KPIs, ratings, trends, imports | Evidence-based performance reviews |
| Training & Development | Programs, sessions, enrollment, payments, attendance, certificates | Operationalized player development |
| Medical & Rehab | Injuries, records, treatments, return-to-play | Restricted and auditable health workflow |
| Communication | 1:1/group chat, files, read states, notifications | Faster coordination and traceable communication |
| Documents | Centralized tenant-scoped document storage | Consistent evidence and retrieval |
| Access & Audit | Roles, permissions, audit trail | Controlled data access and accountability |
| Reporting | Operational dashboards and exports | Management visibility and decision support |

## 6. Out of Scope for Initial Release

- Public marketplace or unrestricted player registration
- Automated contract negotiation by AI
- Medical diagnosis or autonomous clinical decision-making
- Automated player valuation presented as factual without human review
- Full accounting/payroll ERP replacement
- Club-side portal with reciprocal workflow unless explicitly approved
- Native mobile applications as a hard dependency for web launch
- High-scale microservices decomposition before scale evidence exists

## 7. Business Processes

### 7.1 Player onboarding

Lead/prospect identified -> duplicate check -> player profile created -> required documents collected -> initial sporting/medical/legal data entered -> profile completeness review -> player activated.

### 7.2 Contract lifecycle

Draft -> legal review -> approval workflow -> signature -> signed evidence stored -> active monitoring -> expiry notification -> renewal/termination -> archive.

### 7.3 Scouting

Assignment -> scout observes -> draft report -> submit -> sporting review -> approve/reject -> watchlist or player onboarding.

### 7.4 Training

Program created -> sessions scheduled -> publication -> registration -> capacity/payment checks -> attendance -> completion -> certificate.

### 7.5 Legal case

Ticket created -> priority/SLA -> assigned -> notes/evidence -> review -> resolved -> closed -> archive.

### 7.6 Medical/rehab

Record created -> treatment sessions -> progress notes -> return-to-play assessment -> closure; confidentiality enforced throughout.

### 7.7 Performance evaluation

Match/stat import or entry -> validation -> aggregate -> review -> rating -> periodic comparison -> report.

## 8. Business Rules

- BR-RULE-01: Every business record belongs to exactly one tenant unless explicitly designated platform-global reference data.
- BR-RULE-02: Sensitive records (medical, legal-confidential, compensation/finance) require explicit role/policy authorization beyond basic tenant membership.
- BR-RULE-03: Contract state changes are workflow-controlled and auditable; direct state mutation is not permitted for ordinary users.
- BR-RULE-04: A contract cannot be considered signed unless the signature evidence meets the configured signature policy.
- BR-RULE-05: Audit evidence must be append-only at the application level and must capture who, what, when, tenant, source context, and relevant before/after values where lawful.
- BR-RULE-06: A player profile can only be shared externally through an explicit sharing operation with an approved data subset and expiry/revocation controls.
- BR-RULE-07: Medical access is purpose-limited; non-medical users must never receive medical detail through ordinary player endpoints, exports, search, chat, logs or notifications.
- BR-RULE-08: Training attendance is linked to a specific enrollment and session and cannot be duplicated for the same pair.
- BR-RULE-09: Ratings are versioned against an approved rating scheme so historical scores remain interpretable after scoring changes.
- BR-RULE-10: Notifications are advisory; business state is always determined by the authoritative workflow record, not by notification delivery state.
- BR-RULE-11: Deleted/archived records remain recoverable according to retention policy, while audit records follow stricter immutability controls.
- BR-RULE-12: The agency remains the owner/controller of its operational data; platform support personnel must use least-privilege support access with auditable elevation.

## 9. Business KPIs and Success Measures

| KPI | Definition | Target direction |
|---|---|---|
| Player profile completeness | Required profile fields completed / total required fields | Increase; define threshold per lifecycle stage |
| Contract deadline compliance | Contracts with required actions completed before deadline | >= 98% internal target after stabilization |
| Legal SLA compliance | Tickets resolved within configured SLA | >= 95% by priority band |
| Training attendance visibility | Sessions with attendance recorded by end of day | >= 98% |
| Data quality | Validated records without critical integrity errors | >= 99.5% |
| Notification delivery success | Accepted provider/in-app deliveries / attempted deliveries | >= 99% for supported channels |
| Platform availability | Service availability excluding approved maintenance | >= 99.9% target |
| Search success | Users finding intended record within first attempt | >= 90% in usability testing |
| Time to produce player dossier | Median time to assemble current approved profile package | Reduce materially vs manual baseline |
| Security incidents | Confirmed tenant-isolation or unauthorized-access incidents | Zero tolerated |

## 10. Business Risks

| Risk | Business impact | Mitigation |
|---|---|---|
| Tenant data leakage | Critical reputational/legal impact | Defense in depth: tenant context, composite FKs, service/repository guards, policy tests, security testing |
| Sensitive medical/legal exposure | Privacy and trust risk | Field/endpoint permissions, encryption, audit, masked logs, restricted exports |
| Contract deadline failure | Financial/legal risk | Multiple alerts, dashboards, task ownership, calendar integration later |
| Poor data quality | Wrong decisions and reports | Validation, controlled vocabularies, duplicate detection, data stewardship |
| Over-engineering | Cost and slower delivery | Modular monolith first; evidence-driven service extraction |
| Vendor lock-in | Migration cost | OpenAPI, portable PostgreSQL, S3-compatible storage, provider abstraction |
| Unverified legal e-signature assumptions | Contract enforceability risk | Jurisdiction matrix and approved signature provider/legal review |
| Medical workflow ambiguity | Unsafe operational use | Medical owner defines required states and access rules; system is not a clinical decision engine |

## 11. Operating Model

- Product owner owns scope, priorities and acceptance criteria.
- Department owners own business rules for their domains: legal, sporting, medical, training and finance.
- System administrators operate tenant/user/configuration functions but do not automatically gain confidential domain access.
- Security and privacy responsibilities are shared across product, engineering and operations; no single role should bypass audit.
- Data stewardship includes duplicate resolution, controlled vocabularies, retention and export governance.
- A change control process is required once requirements are baselined: every material change receives impact assessment across BRD/PRD/SysRD/SRD.

## 12. Financial and Commercial Model

Initial commercial model: internal agency platform. Future SaaS commercialization may use tenant-based subscription tiers, seat-based pricing, feature entitlements, storage/media limits, and optional integrations. The requirements suite intentionally avoids hard-coding a final pricing model; the product should expose tenant feature flags and usage metrics that can support later packaging.

## 13. Release Strategy

| Release | Business purpose | Core scope |
|---|---|---|
| MVP / Phase 1 | Replace fragmented manual administration | Identity, tenant/user, player profiles, documents/media, contracts, approvals, legal tickets, basic notifications, audit |
| Phase 2 | Operational depth | Training/camps, attendance, performance, ratings, chat, richer dashboards, imports/exports |
| Phase 3 | Agency intelligence | Scouting, advanced analytics, sharing portal, stronger financial workflows, mobile readiness |
| Phase 4 | Scale and automation | External tenants, advanced integrations, AI-assisted analysis, market intelligence subject to governance |

## 14. Acceptance of Business Requirements

The BRD is accepted when agency leadership confirms scope, objectives, roles, business rules, priority model, key KPIs, operating responsibilities, and known exclusions. Approval of this document authorizes refinement into product/system/software requirements; it does not authorize production processing of real medical, legal or financial data until security and legal controls are approved.

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
