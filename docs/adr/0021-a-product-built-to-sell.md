# ADR-0021 — Sadara is a product built to sell; its first milestone is a sales demo built as the real product

**Status:** Accepted · 1 October 2026 · **Decided by:** the owner · **Supersedes:** the Phase-0 gate as
the entry to Phase 1 (now the foundation gate `0.11.0`); "the agency" as the owner of product questions
in the OPEN register, including the default role matrix that [ADR-0005](0005-authorization.md) left open
until an agency confirmed it; Phase 3 as the home of scouting

## Context
The plan was written as if a client agency with real data already existed. On 1 October 2026 the owner
clarified: there is no client and no data. Sadara is being built to show sports agencies and sell to
them, then handed over in production when one buys. The first pitch is four to six months away, shown
from a laptop; a hosted link comes later, on a small server the owner will rent. The owner asked the
implementer to make the product decisions ("do everything"), within the plan and its workflow and to
professional standards, and asked that the project run locally now and on that server later.

## Decision
1. **The demo milestone is the build order.** [`demo-milestone.md`](../implementation/demo-milestone.md) lists
   the 124 steps the first demo needs, in order:
   - the foundation, through the new foundation gate `0.11.0`;
   - the four areas the demo shows: players and profiles, contracts and documents, dashboard and alerts,
     scouting;
   - a fictional demo dataset, a one-command laptop demo and a rehearsed acceptance (`1.12.1`–`1.12.3`).

   It is built as the real product: every invariant, test and review applies, and nothing is faked for
   the demo. The plan check verifies the list: each step's dependencies come earlier or are done.
2. **Two gates.** Product features build on `0.11.0`, which includes MFA and step-up for privileged
   roles, security events, the audit of confidential reads and the NestJS 12 upgrade. The production gate
   `0.11.1` adds guardian relationships, the legacy medical routes and the restore and failure drills.
   Nothing reaches staging, a hosted demo or production without it.
3. **Scouting moves into Phase 1** as group 1.11. Its steps keep their content under new IDs: 3.1.1–3.1.7
   became `1.11.1`–`1.11.7`. No PR, progress row or test had cited them, which is the only condition under
   which the plan renumbers. Legal tickets (group 1.5) follow
   the demo. A module that ships later adds its own panels to the shared surfaces (`1.11.8`, `1.5.6`), so
   Player 360, search and the dashboards no longer wait for legal tickets.
4. **The product decides its defaults.** The plan had left some questions for "the agency":
   - roles and approval chains;
   - required profile fields;
   - contract types;
   - SLA calendars;
   - capacity;
   - seasons.

   These are now product decisions. The plan's defaults ship as Sadara's, configurable per tenant where a
   step says so, and a buying agency adopts or tightens them in its own tenant. Representation agreements
   are a first-class contract type. [ADR-0019](0019-owner-approves-signature-policy.md)'s evidence policy
   ships as the default that each agency's owner adopts for its tenant.
5. **No real data exists** (OPEN-11, closed).
   - Databases may be dropped and reseeded until the first customer.
   - Legacy rows are synthetic seed data and may be replaced instead of migrated.
   - The read-only preflight (`0.4.1`) still reports violations of the integrity rules, but needs no
     owner-approved mapping.
6. **Portable by design.** Development runs on any machine with Docker (`just up`). The first hosting
   target is one small server running the same stack in production mode (`1.10.1`, `1.12.4`). No step may
   depend on a managed cloud service unless an alternative runs on that server.

## Alternatives rejected
- **Keep the order.** The first agency-visible feature would arrive only after all of Phase 0: 17–35
  weeks of foundation work, by the plan's model.
- **A clickable prototype on simulated data.** It's the fastest thing to show, but its screens would not
  be the product, and the owner asked for the demo to be the real app.
- **A lighter foundation for the demo.** Tenancy, row-level security, authorization, audit and the file
  pipeline cannot be added cheaply once features sit on top of them, so they stay first.

## Consequences
- Phase numbers no longer give the build order; the milestone does.
- The production gate and Phase 1's production work follow the demo. A hosted demo waits for the
  production gate, the deployment path, managed secrets, telemetry and security scanning (`1.12.4`); the
  launch waits for all of group 1.10.
- Product defaults are shown as defaults where a step says so, so a prospect sees what can be changed.
- The plan now has 251 microsteps:
  - the foundation gate `0.11.0`;
  - legal on the shared surfaces `1.5.6`;
  - scouting on the shared surfaces `1.11.8`;
  - the demo group `1.12.1`–`1.12.4`.

## Revisit when
- A first agency signs: production hardening becomes the priority, and its requirements are adopted.
- The pitch date moves.
- The measured pace makes the milestone unreachable; the [checkpoints and cut
  list](../implementation/demo-milestone.md#forecast-and-checkpoints) apply.
