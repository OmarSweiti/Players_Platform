# Arabic and English product interface

Target specification for UX-001..012, SR-CORE-007, SR-NFR-I18N-001, SR-NFR-A11Y-001 and TEST-009/010. The shell is delivered in `0.9.1`–`0.9.6`; every later feature ships its Arabic/English states with its API. Accessibility acceptance belongs to `1.10.8`, native Arabic/domain review to `1.10.15`, and subsequent releases repeat both. [i18n ADR](../adr/0008-i18n.md), [API behavior](api.md), [manual testing](../implementation/02-development-workflow.md#manual-testing-playbook).

## Baseline and target boundary

The inspected frontend uses `frontend/app/` with shared code under `frontend/src/`; the current root layout imports Geist and Geist Mono with Latin subsets and renders `lang="en"` (`frontend/app/layout.tsx:2`, `:9`, `:14`, `:29`). The API client currently sends a tenant header from browser storage and logs body data (`frontend/src/shared/lib/api-client.ts:58`, `:65`). These are baseline defects, not acceptable UI conventions. Preserve one App Router tree rooted at `frontend/app`; do not introduce a second competing `src/app` tree.

## Routes, navigation and context

Use next-intl locale routing under `frontend/app/[locale]/`, allowing only `ar` and `en`. Enable Next `typedRoutes`; compile-time route checking supplements browser tests but cannot prove authorization. Render `<html lang="ar" dir="rtl">` or English/LTR on the server before hydration. These choices follow the [next-intl setup](https://next-intl.dev/docs/routing/setup) and [Next typed-routes interface](https://nextjs.org/docs/app/api-reference/config/next-config-js/typedRoutes); use the pinned project versions when implementing.

| Route family | Purpose | Initial owner |
|---|---|---|
| `/{locale}` | Authorized home and actionable deadlines | `0.9.6`, `1.8.2` |
| `/{locale}/sign-in` | Explain agency context and redirect to `/api/v1/auth/login` | `0.1.7`, `0.9.5` |
| `/{locale}/settings/profile`, `/settings/sessions` | Preferences, IdP account/recovery links, real session list/revocation | `1.1.3` |
| `/{locale}/settings/users`, `/settings/tenant` | Invitations, membership changes, locale/zone/currency and feature settings | `1.1.1`, `1.1.2`, `1.1.4`, `1.1.6` |
| `/{locale}/players`, `/players/{id}` | Directory and permission-shaped Player 360 | `1.2.4`, `1.2.7` |
| `/{locale}/contracts`, `/contracts/{id}` | Version/approval/evidence workspace | `1.4.7` |
| `/{locale}/legal`, `/legal/{id}` | Ticket queue, restricted notes and attachments | `1.5.4` |
| `/{locale}/notifications`, `/audit` | Safe notifications and restricted evidence search | `1.6.2`, `1.7.1` |
| `/{locale}/training`, `/performance`, `/ratings`, `/medical`, `/chat` | Phase-2 workspaces | `2.2.5`, `2.4.2`, `2.5.2`, `2.1.7`, `2.6.6` |
| `/{locale}/scouting` | the scouting workspace (Phase 1, demo milestone) | `1.11.6` |
| `/{locale}/reports`, `/finance` | Phase-3 workspaces | `3.2.2`, `3.4.4` |

There is no `/dashboard` prefix. Public dossier/certificate verification routes are separate minimal surfaces defined by their domain steps, not copies of the authenticated shell. Navigation is built from released features and effective capabilities, while the API independently authorizes every request. No placeholder business metrics or fabricated live records.

Show active agency and signed-in person without making an editable tenant ID an authorization mechanism. Tenant selection requires a server-verified membership transition; a host change uses an approved destination, not a browser-assembled arbitrary URL. Support elevation, once implemented, has a persistent reason/scope/expiry banner. Changing locale preserves the resource and safe filters; changing tenant cancels requests and clears protected cached data.

## Session and identity experience

There is no local password, TOTP enrollment or browser-generated backup-code flow. Login, MFA, recovery and step-up happen at the IdP. Step `1.1.7` delivers an Arabic/English Keycloak login theme, approved vocabulary and keyboard/error-state tests. Theme assets are versioned alongside the pinned provider configuration; they do not replace the provider's protocol behavior.

On 401, clear protected state and offer sign-in with a validated return path. On `STEP_UP_REQUIRED`, send the user through the approved authentication flow and return to an explicit confirmation screen; do not silently repeat a signature, payment or privilege change. Show idle/absolute expiry warnings where useful, without promising that an expired session can always be renewed. Logout clears the cookie through the API and clears browser queries; merely navigating to login is insufficient.

`GET /api/v1/auth/session` is the user-state source. JavaScript never reads the HttpOnly cookie. Session management shows only actual persisted sessions and successful revocation. Account deactivation and role changes become effective at the next authorization check; the UI refreshes capabilities and removes stale protected values after a denial.

## Shared interaction contract

Every feature uses the same explicit states:

| State | UI behavior | Verification |
|---|---|---|
| Loading | Stable labeled skeleton/progress, no confidential stale placeholder | No layout trap or false empty state while request is pending. |
| Empty | Explain absence within authorized scope and offer a permitted next action | Does not reveal hidden record counts or disabled modules. |
| Validation failure | Field errors and summary; focus first invalid input | Same field codes map correctly in Arabic and English. |
| Recoverable request failure | Safe message/request ID and intentional retry | Preserve nonsensitive input and reuse the idempotency key where applicable. |
| Offline | Visible offline state; distinguish unsent from committed | No hidden queue for sensitive mutations in MVP. |
| Stale revision | Show reload/reconcile choice and preserve safe local edits | No automatic overwrite after 412. |
| Missing/forbidden object | Neutral not-found view and safe navigation | Does not confirm another tenant's object or confidential child existence. |
| Pending job | Queued/running/failed/complete/expired state from server | A successful queue submission is not displayed as completed processing. |
| Archive/termination/rejection | Entity, consequence, required reason and explicit confirmation | Keyboard-accessible cancel; authoritative server state after acceptance. |

Labels remain visible; placeholders are examples, not labels. Required and optional status is textual. Bound narrative and filename input, explain permitted file types/sizes, and associate errors/help with their fields. Client validation is convenience; server validation remains authoritative. Safe retries cannot generate a new business command merely because the first response was lost.

Data tables use server pagination, allowlisted sorting/filtering, accessible filter chips and URL-preserved safe state. Debounce search, cancel superseded requests, and include a stable row identity. No loading the entire tenant dataset into the browser to filter. Bulk actions display authorized selected counts and per-item outcomes without revealing forbidden rows. Saved views contain filter configuration, not copied records; verify filter permissions again when loading a view.

At 360px, keep identity/name, status and essential action reachable; use responsive summaries or a labeled horizontal table region for genuinely tabular detail. Test 360, 768 and 1440 CSS-pixel widths, 200% zoom and keyboard use. Complex media tooling may favor desktop but cannot block basic upload status, cancellation or viewing on smaller screens.

## Domain workspaces

| Workspace | Required presentation and actions | Negative/edge case |
|---|---|---|
| Player directory / 360 | Search names and approved aliases, profile completeness, archived state, authorized tabs/timeline | No passport/emergency-contact fields or legal/medical counts without permission. |
| Documents/media | Picker and drag alternative, upload progress, scan status, retry/cancel, version history, caption/featured marker | Pending/infected/error objects never appear as downloadable; expired URLs are reauthorized. |
| Contracts | Consistent status labels, civil start/end dates, version/change notes, ordered review, evidence status and deadlines | Compensation absent without grant; proposed evidence is distinct from policy-accepted Signed. |
| Legal | Priority/assignee/deadline queue, ticket history, internal-note audience label and restricted attachments | Requester sees neither confidential note text nor hidden-note count; no diagnosis in generic ticket previews. |
| Notifications | Safe title/action, unread state, mandatory vs optional preferences, authorized deep links | Permission revoked after creation produces a neutral denied destination. |
| Training | Calendar/list, local zone, recurrence exceptions, capacity/waitlist, attendance roster and completion | Seat race has an honest loser/waitlist state; late enrollment cannot rewrite past attendance. |
| Performance/ratings | Source period, match/date, units, scheme/version, trend with table alternative | Missing is distinct from zero; comparisons do not merge incompatible schemes without explanation. |
| Medical | Restricted purpose-aware workspace, typed record, treatments and clinician-entered availability/RTP | Non-medical surfaces receive only the approved minimal availability projection. |
| Chat | Persisted message state, sending/retry, edit/recall markers, unread and reconnect recovery | A local optimistic bubble is not a server acknowledgment; removed membership clears access. |
| Scouting | Assignment, prospect/player distinction, report review and onboarding action | Prospect age estimates are not silently converted into a fabricated birth date. |
| Dossier/sharing | Approved field checklist, rendered preview, recipient/expiry/revocation, safe external view | No confidential fields by default; revocation cannot recall a file a recipient already downloaded. |
| Finance | Restricted source documents, exact amount/currency, unknown settlement/reconciliation state | Unknown provider outcome never appears paid; refund/reversal requires policy and recent authentication. |

## Arabic, bidi and formatting

Use logical CSS (`margin-inline`, `padding-inline`, `inset-inline`, `text-align:start`) and logical utility classes. Lint physical directional utilities unless an explicitly reviewed physical-layout case requires them. Mirror navigational arrows where meaning changes with direction; do not mirror logos, media play controls, numeric content or strings. DOM focus/reading order must match the visual layout without arbitrary CSS reversal.

Isolate Latin IDs, email, URLs and mixed-script tokens with `<bdi>` or a labeled LTR span. Do not interpolate an untrusted directional-control sequence into a trusted status/amount label without isolation. Input normalization and evidence preservation are separate concerns: preserve original user text where needed, render it safely, and do not silently alter legal evidence.

Catalogs have typed key parity across `ar` and `en`, including empty/error/loading/conflict states. Use full messages with parameters/plural rules, not concatenated fragments. Store enum codes and canonical business values; localize only presentation. User-authored content is not automatically translated. Arabic and Latin names/aliases are separately preserved and searchable; searching a transliteration only works when an approved alias or search policy supports it.

Dates: civil `YYYY-MM-DD` values remain the same day in every locale/timezone. Instants default to the tenant's IANA zone (UX-007) and expose the exact absolute timestamp where audit precision matters. A secondary user-zone display requires explicit approval and an unambiguous zone label. Scheduled forms capture local date/time and zone, show the resolved instant, and explain DST ambiguity where relevant. Calendar display beyond the initial Gregorian representation is OPEN; storage semantics do not change with display preference.

Amounts: parse/format exact decimal strings using currency definitions, never JS Number arithmetic. Show the currency code where a symbol is ambiguous. Display payable precision according to the currency exponent; never silently round an entered charge. Locale-specific grouping and decimal separators require explicit parsing rules and confirmation. Use stable ASCII digits in identifiers and transport values; ordinary displayed numbers follow the approved locale/numbering preference.

Use an Arabic-capable font with documented licensing and tested shaping. The web app uses IBM Plex Sans Arabic beside Geist, both under the SIL Open Font License 1.1 and self-hosted (`0.9.2`); a browser test asks Chrome which fonts draw Arabic and Latin text. Font loading and fallback must not clip Arabic marks or materially shift critical controls. Browser, email and PDF rendering each need their own shaping/layout evidence; browser success does not qualify a certificate PDF. Theme, contrast and dark-mode behavior use one consistent token system, preserving existing suitable components rather than introducing an unrelated redesign.

## Accessibility acceptance

[WCAG 2.2](https://www.w3.org/TR/WCAG22/) Level AA is the product target, not a certification statement. Use semantic headings/landmarks, real buttons and links, named controls, text alternatives, visible focus, keyboard-operable dialogs with focus restoration, and status announcements that avoid repeated noise. Do not encode workflow state solely in color. Respect reduced motion and make essential actions available without drag, hover or precise pointer movement.

Playwright projects `ar` and `en` run axe on actual feature states. Automated checks are supplemented by manual keyboard and screen-reader journeys, reading/focus order, zoom/reflow, contrast, task clarity and native Arabic terminology review. Record accessibility findings in `1.10.8` and native-language/domain acceptance in `1.10.15`; do not mark language acceptance passed merely because catalogs have equal keys. Charts include a meaningful text/table alternative and source period.

Minimum Arabic fixture set: a long multipart name; mixed Arabic/Latin club abbreviation; an authorized synthetic passport-like identifier; negative/decimal/percent amounts; leap-day birthday; end-of-contract civil date; empty optional fields; plural attendance counts; multiline notes; long server validation messages; and keyboard-only file/approval dialogs. Artifacts contain synthetic values only.

## Browser data and verification

TanStack Query keys include tenant, projection/permission version, resource, filters and locale where rendered output depends on it. Role changes invalidate affected queries; logout/tenant switch cancels in-flight requests and clears protected caches before rendering new context. A late response from a previous tenant must not repopulate the new tenant's cache. Authenticated server rendering uses per-request fetches with `no-store`, and confidential fields must be absent from HTML, RSC payloads and hydration state as well as visible DOM.

Persist only non-sensitive UI preferences locally by default. No credentials, medical drafts, passport values, legal narrative or compensation in localStorage, sessionStorage, persistent query caches or service-worker caches. A future offline feature needs explicit encryption, revocation, recovery and device-policy design before activation.

For each UI step, execute its feature-local Playwright/Vitest commands and [manual testing playbook](../implementation/02-development-workflow.md#manual-testing-playbook). Inspect response payloads, HTML/RSC data, caches and exported files for forbidden fields; hiding a tab or using CSS is not confidentiality evidence. Required test titles are owned by the phase files and generated into the [test catalog](test-catalog.md), not duplicated as a second registry here.
