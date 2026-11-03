# Visual design — direction, principles, skills and references

How Sadara's interface should look and feel, and the tools and references that get it there
([ADR-0026](../adr/0026-interface-design-with-skills-and-references.md)). It applies to every change
to the web app, the Keycloak sign-in theme (`1.1.7`) and the demo (`1.12`).

**Order of authority.**
1. [`ui-ux.md`](ui-ux.md) is the behavioural contract: states, Arabic and English, accessibility, data
   safety. It prevails over this file.
2. The [conventions](../implementation/01-conventions.md) (invariant 8: Arabic and English together,
   logical CSS, bidi isolation) prevail over both.
3. This file decides what the contract leaves open: how the interface looks.

## The product it serves

- **Who uses it.** A football agency's staff (agents and managers, legal, medical, scouts, coaches,
  administrators) and its owner. They spend their working hours on players' careers in Arabic or
  English.
- **What it is.** A football platform for the people who run players' careers: the agency's private
  system for its players' identity, contracts, documents, medical care and scouting. Confidential by
  default. Football here is association football, the game some countries call soccer.
- **What it must feel like: sporty, all through.** Football, seen from the professional side of the
  game:
  - **work screens** are sporty and exact, like a top club's analysis room: bold figures, crisp lines,
    quick and decisive feedback, and nothing that slows the work;
  - **the moments** when a person meets the product or a player are full match day: the floodlit pitch,
    a broadcast's line-up, a club's signing announcement.

  Arabic is a first language, as it is for the game across the region: a screen is designed in both
  directions from its first sketch.
- **What it is not.** A betting product, a video game, or a fan site's noise. It copies no club's,
  league's or game's identity.
- **The brand is the owner's.** That covers the logo, the brand colour, and any typeface beyond IBM Plex
  Sans Arabic and Geist (`0.9.2`). Until the owner chooses:
  - the tokens carry a neutral palette with one accent;
  - each agency's branding (`1.1.2`) replaces that accent within the contrast rules below.

## The football in it

The visual language comes from the game itself, not from generic software: the product should look
and move like sport. Everything below sits inside the [principles](#principles) and the
[two kinds of surface](#two-kinds-of-surface). Football gives the interface its character, and never at
the cost of legibility, accessibility or confidentiality.

**Sporty at every level, workspaces included.**
- **Type with a sporting stance.** Headings and key figures use the heavy weights of the two licensed
  families. Numbers lead, as on a scoreboard. Arabic is never letter-spaced.
- **Energy in the shapes.** A slanted edge, a kit stripe or a pitch line marks an accent or a section.
  Slants lean in the reading direction, and mirror in Arabic. Corners are tight: the curves are the
  pitch's (the centre circle, the arc), not a generic softness.
- **Colour with a team's confidence.** Neutral, high-contrast surfaces, with the agency's colour used
  decisively: one strong colour, as on a kit, never a pastel wash. The dark theme is first-class, like a
  night match.
- **Motion like a pass:** quick and decisive, easing out and never floating or bouncing, within the
  [motion rules](#principles).
- **Icons from the game where they carry meaning:** a ball, a boot, a whistle, a shirt, a card, a
  trophy. Drawn in lucide's stroke style, and made for the project when lucide has none.

**Motifs, from the pitch and the match.**
- **The pitch's geometry.** Touchlines, the halfway line, the centre circle, the penalty area and its arc
  serve as layout guides and as thin-line ornament in moments. A drawn pitch keeps the proportions of
  105 × 68 m. Mown stripes are a texture for moments only, kept faint.
- **Shirt numbers and the scoreboard.** In moments, a player's number and the key figure of a view are set
  large and heavy, as a kit or a score is. In tables, figures stay tabular and quiet.
- **Match-day light.** The floodlit pitch at night (deep green-black, light falling on the subject) is
  the atmosphere of the moments. In workspaces, colour belongs to the data.
- **The agency's colours, like a club's.** An agency's accent, and later its crest, come from its own
  branding (`1.1.2`) and play the part club colours play on match day.

**Rules that keep it professional.**
- **Positions are physical.** A pitch diagram never mirrors in right-to-left: a left-back stays on the
  left. The text around the diagram mirrors; the pitch does not.
- **Pitch green is not a status.** Success, warning and danger keep their own tokens, distinct from any
  grass or floodlight colour used in a moment, so decoration never reads as "valid".
- **Real football appears as data, never as decoration.**
  - A real club, league or competition is named where a record needs it.
  - Its crest, kit or colours never decorate the product.
  - Nothing is modelled on a video game's player card.
  - The demo's clubs and players are fictional (`1.12.1`).

**Football's ways of showing information.** These are information design, so they may appear in
workspaces:
- **the player card**, Player 360's header: the agency's photograph of the player, name in both scripts,
  number, positions, club, nationality, age, and contract end. Modelled on a match programme's or a
  broadcast's line-up card;
- **positions on a pitch**, in a small diagram in the directory and Player 360, and formations drawn the
  same way;
- **time measured in seasons and matches**: a career timeline with season markers; contract and season
  calendars;
- **attributes and performance** (Phase 2) as analysts show them: radar and percentile bars, each with
  its table alternative;
- **squad and recruitment views**: a depth chart by position, and scouting's shortlist as a transfer
  board.

**Moments, imagined from match day.** These are starting points for the design pass, not commitments:
- **sign-in and the demo's opening:** a floodlit pitch at night, in 3D or as a still, lit in the
  agency's colours;
- **a contract signed:** a signing-announcement card (the player in the agency's colours, "signed until"
  the contract's end) with a short burst of particles;
- **empty states:** a line drawing from the pitch; an empty penalty area for "no players yet";
- **a milestone:** a trophy or a ball, built with img2threejs, for the moments the product celebrates.

**Football to study**, for patterns and never for identity:
- **data-rich match apps:** [FotMob](https://www.fotmob.com/) and [Sofascore](https://www.sofascore.com/)
  for player profiles, ratings, dense live data and dark themes;
- **the professional side:** [Transfermarkt](https://www.transfermarkt.com/) for player profiles,
  contract ends and market data; [Hudl Wyscout](https://www.hudl.com/products/wyscout) for scouting
  workflows, shortlists and shadow teams;
- **leagues and competitions:** [Premier League](https://www.premierleague.com/),
  [UEFA](https://www.uefa.com/) and the [Saudi Pro League](https://www.spl.com.sa/), the last for Arabic
  football presentation;
- **Arabic sports media:** [beIN SPORTS](https://www.beinsports.com/) for how football reads right to
  left: line-ups, score graphics, statistics;
- **match broadcasts' graphics:** line-ups, score bugs, transitions, as reference for moments' motion.
  The Sports Video Group's
  [design of the modern score bug](https://www.sportsvideo.org/2026/06/09/designing-the-modern-scorebug-how-broadcast-graphics-teams-are-rethinking-the-most-important-element-on-screen/)
  explains the choices behind them;
- **sports design at its best:** the [Awwwards sports collection](https://www.awwwards.com/websites/sports/),
  [Speckyboy's sports websites](https://speckyboy.com/sport-web-design-inspiration), and
  [LJ Studio's motion design system for the French Football Federation](https://www.abduzeedo.com/lj-studios-sports-motion-design-system-france)
  for a federation-grade football identity across screens.

**Directing the skills.**
- A moment's brief to design-taste-frontend names this section, and a direction that does not read as
  football is dealt again.
- img2threejs builds football objects (a ball, a trophy, a goal frame, a stadium silhouette), never a
  person.
- impeccable's `shape` starts from the football ways of showing information above.

## Two kinds of surface

| | Workspaces | Moments |
|---|---|---|
| **Where** | the directory and Player 360's tabs, contracts, legal, medical, documents, notifications, audit, settings | sign-in and the Keycloak theme, first run and onboarding, empty states, Player 360's header, a contract signed, the demo's opening screen, a milestone |
| **The job** | work through records quickly and correctly, for hours | make the product memorable and the next step obvious |
| **Football** | its energy and its information design: bold figures, crisp lines, decisive motion, player cards, positions on a pitch, seasons, depth charts | its atmosphere: the floodlit pitch, the line-up card, the signing announcement |
| **Allowed** | density; aligned figures; colour spent on status and data; motion as feedback (about 100–200 ms); shadcn/ui components | art direction; imagery; expressive type and numbers; motion; one 3D scene or particle field, under the rules below |
| **Never** | 3D, particles, decorative animation, imagery that competes with data, art-directed layouts | anything that delays the task or hides an action; confidential data in decoration |

Medical and legal are always workspaces, and the quietest ones. A public dossier or certificate check is
a minimal surface of its own (`ui-ux.md`), never a moment.

## Principles

**Hierarchy.**
- One primary action per view.
- Headings in order, the page's purpose readable in the first screen.
- Secondary actions visibly secondary.
- Nothing competes with the record a person came for.

**Type.**
- IBM Plex Sans Arabic and Geist, self-hosted (`0.9.2`), on one scale shared by both scripts.
- Arabic gets more line height than Latin, for its marks, and **never letter-spacing**: spacing breaks
  the joins.
- Tables use tabular figures, so columns of numbers align. Digits follow the rules in `ui-ux.md`.

**Colour.**
- Tokens only, by role: surface, text, border, accent, and the four statuses (success, warning, danger,
  information). No raw colour values in components.
- Text meets WCAG 2.2 AA (4.5:1; 3:1 for large text and for controls). Status is never carried by colour
  alone.
- Light and dark themes come from the same tokens (`0.9.6`).
- An agency's accent is accepted only with a foreground that keeps these contrasts (`1.1.2`).

**Space and layout.**
- One spacing scale (Tailwind's 4-pixel steps), with one density per surface.
- Layouts are designed at 360, 768 and 1440 CSS pixels, and mirror through logical properties
  (`ms-`, `pe-`, `start-`): never transforms, never physical sides.
- Reading and focus order follow the visual order in both directions.

**Components.**
- shadcn/ui through its CLI with `rtl: true` (`0.9.6`): composed, not forked; variants through
  class-variance-authority.
- Every component has the states the contract lists: loading, empty, error, offline, stale, pending.

**Data.**
- Text aligns to the start, numbers to the end, and both mirror.
- Missing is not zero.
- Every chart has a table alternative and its source period (`ui-ux.md`). Colour in a chart is spent on
  the data, not on decoration.

**Motion.**
- Only for feedback, continuity or attention: about 100–200 ms for controls, up to about 400 ms for a
  view change.
- Never on figures someone is reading; no endless loops in a workspace.
- `prefers-reduced-motion` turns movement into a cross-fade or nothing.

**Imagery and icons.**
- Icons are lucide-react. Directional icons mirror in right-to-left (`rtl:rotate-180`); logos, media
  controls and numbers do not.
- **Never a real person's photograph or likeness** in the product's own assets, the demo or the
  evidence. Players in the demo are fictional (`1.12.1`); real photographs arrive only as an agency's own
  uploads, through the file pipeline.
- Illustrations and photographs are self-hosted, with their licence recorded beside them. Nothing is
  hotlinked.

**Copy.**
- Short, specific, in the voice of a careful colleague.
- Arabic is written, not translated word for word: the native review is `1.10.15`.

**The generic tells to refuse.** These are what impeccable's detector flags:
- purple-to-blue gradients;
- cards nested in cards;
- grey text on coloured backgrounds;
- a rounded icon tile above every heading;
- cramped padding;
- skipped heading levels.

Above all: the interface any agent would produce for any product, with Sadara's name pasted in.

## The design skills

Agent skills, installed on each machine at the versions below (setup further down). They give an agent a
vocabulary, a direction and a reviewer. They do not replace the contract, the tokens or the tests.

| Skill | What it gives | When | Version · licence |
|---|---|---|---|
| [**impeccable**](https://github.com/pbakaus/impeccable) | 24 commands: `shape` plans a screen before code; `typeset`, `layout`, `colorize`, `quieter`, `distill`, `animate`, `delight` and `overdrive` steer; `critique` scores usability and `audit` checks accessibility, performance, theming and responsiveness, ranked P0–P3; `harden`, `adapt`, `clarify`, `onboard` and `polish` finish. A detector of 62 deterministic rules runs in the agent (a design hook), or as `npx impeccable detect` on files or a running page | every UI step: shape first, critique and audit before the evidence | npm `impeccable` 4.8.0 · Apache-2.0 |
| [**design-taste-frontend**](https://github.com/Leonxlnx/taste-skill) (taste-skill) | art direction from a study of 247 curated sites; an app-screen route for dashboards and work screens (quiet panels, aligned figures, colour spent on data); checks its own work in a real browser at three widths | moments, the demo, the sign-in theme; its app route for a new workspace's first layout | commit `12af471` · MIT |
| [**shadcn**](https://ui.shadcn.com/docs/skills) (shadcn/ui's skill) | knows this project's shadcn setup (`shadcn info`), the CLI (`add`, `search`, `view`, `diff`), theming with CSS variables and dark mode, and composition rules | adding or changing a component (`0.9.6` onward) | commit `4233ed1` of shadcn-ui/ui · MIT |
| [**Playwright CLI**](https://github.com/microsoft/playwright-cli) | the agent looks at the running app: snapshots and screenshots, in isolated sessions (`PLAYWRIGHT_CLI_SESSION`) | after every build step: 360/768/1440 × `ar`/`en` × light/dark | npm `@playwright/cli` 0.1.22 · Apache-2.0 |
| [**img2threejs**](https://github.com/img2threejs/img2threejs) | rebuilds the object in a reference image as procedural three.js code, through staged, quality-gated passes, ready to animate | a moment that needs a 3D object (a ball, a pitch, a trophy, a stadium silhouette) | npm `img2threejs` 0.1.1 · Apache-2.0 |

**Their context in this repository.** In `0.9.6`, `impeccable init` and `impeccable document` write the
frontend's `PRODUCT.md` and `DESIGN.md` from this file and the tokens. Every later command reads them.
They summarise this reference and never contradict it: a change of direction is made here first.

**Geist and the detector.** impeccable's `overused-font` rule names Geist among the faces seen on too
many sites, but Geist is this project's licensed, self-hosted Latin face (`0.9.2`), and the brand's type is
the owner's decision. `0.9.6` records that choice in impeccable's own configuration, with
`npx impeccable ignores add-value overused-font Geist --reason "the licensed Latin face, 0.9.2"`. The
detector keeps every other rule. On 3 November 2026 it found nothing in the web app's source, so its
rendered-page rules start working with `0.9.6`'s first screens.

## The references

| Reference | Take from it | Never | Licence |
|---|---|---|---|
| [shadcn/ui](https://ui.shadcn.com/) | the components, blocks and charts this app is built on; theming; its [RTL guide](https://ui.shadcn.com/docs/rtl) | a component outside the CLI's flow, or a block's sample data | MIT |
| [uiverse.io](https://uiverse.io/) | micro-interactions: buttons, toggles, checkboxes, inputs, loaders, tooltips, notifications | an element as it is: they are written in physical CSS, fixed pixels and left-to-right only | MIT, community-made; credit the creator and Uiverse |
| [three.js](https://threejs.org/) | the manual and examples behind a 3D moment: scenes, lights, materials, performance | a scene in a workspace | MIT |
| [particles.js](https://vincentgarreau.com/particles.js/) | the look of a particle field, from its demos (default, NASA, bubble, snow) | the library: its last release, 2.0.0, is from May 2015. Build the effect with [tsParticles](https://github.com/tsparticles/tsparticles) or three.js | MIT |
| [Refero Styles](https://styles.refero.design/) | more than 2,000 design systems extracted from real product websites, as `DESIGN.md`: type scales, spacing, colour roles, component patterns of mature products | a brand's identity (its colours, type and signature shapes together) | no licence stated: study only |
| [awesome-design-skills](https://github.com/bergside/awesome-design-skills) | 67 design-system skill files (`SKILL.md` and `DESIGN.md`): how such a file is structured, and the vocabulary for ours | adopting one wholesale: they conflict with agency branding and right-to-left layout | MIT |
| [Apple HIG: Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left) and [Design for Arabic](https://developer.apple.com/videos/play/wwdc2022/10034/) | what mirrors and what does not; Arabic layout and type | — | Apple |
| [Material: Bidirectionality](https://m2.material.io/go/design-bidirectionality) (Material 2) and [Wikimedia Codex: Bidirectionality](https://doc.wikimedia.org/codex/latest/style-guide/bidirectionality.html) | icon mirroring rules; bidirectional text in components | — | Google; Wikimedia |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | the accessibility target (`ui-ux.md`) | — | W3C |

**Adapting code from a reference.** A snippet becomes project code only after it is:
1. rewritten to the tokens, with no raw colours or pixel sizes outside the scale;
2. converted to logical properties, and checked in both directions;
3. given visible focus, keyboard operation and a reduced-motion path;
4. checked for contrast in both themes and with an agency accent;
5. free of any CDN, font or image loaded from elsewhere;
6. annotated with its source and licence: an MIT or Apache-2.0 snippet keeps its copyright notice, in a
   comment that links its origin.

## 3D, particles and motion

- **Only in a moment**, only one per view, and decorative: `aria-hidden`, with the meaning carried by
  text beside it.
- **three.js is the only 3D runtime.** The first step that needs it adds it under the dependency policy
  (the seven-day cooldown, the lockfile, review). It is a client component, loaded with `next/dynamic`
  after the page is usable, never in the first paint's critical path.
- **It degrades.**
  - Under `prefers-reduced-motion`, without WebGL or on a low-power device, the scene is a still image of
    itself.
  - It pauses when off-screen or when the tab is hidden.
  - Its device pixel ratio is capped at 2.
- **It costs nothing to the work.** The page's interaction stays responsive while the scene loads, and
  the scene is measured on a mid-range phone before it ships.
- **Particles** follow the same rules, through tsParticles or three.js.

## Set up, once per machine

The versions below are at least seven days old and reviewed. Changing one is a PR to this file.

```bash
# impeccable: the skill and its design hook (accept the hook); Codex: --providers=codex
npx --yes impeccable@4.8.0 install --providers=claude --scope=global

# taste-skill and shadcn/ui's skill, pinned to reviewed commits; Codex: -a codex
npx --yes skills@1.7.4 add https://github.com/Leonxlnx/taste-skill/tree/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill -g -a claude-code -y
npx --yes skills@1.7.4 add https://github.com/shadcn-ui/ui/tree/4233ed1caded8c38f4bc14b14afe1f93ebcaf966/skills/shadcn -g -a claude-code -y

# Playwright CLI and its skill
npm install --global @playwright/cli@0.1.22 && playwright-cli install --skills

# img2threejs: links the skill into each agent found, then checks it
npx --yes img2threejs@0.1.1 install && npx --yes img2threejs@0.1.1 doctor
```

**Guardrails for the tools:**
- **impeccable's live mode** works on a local checkout only. Start it with
  `IMPECCABLE_LIVE_COPY_AGENT=chat`: otherwise its fallback runs an agent CLI with approvals and the
  sandbox switched off. No tool here runs with a bypassed sandbox.
- **Pictures.** taste-skill looks for pictures in open archives. Keep none of a real person, and record
  the licence of anything kept. img2threejs is never pointed at a real person's likeness.
- **Playwright CLI** drives the local stack only: synthetic data, the development identities, never a
  deployed environment or a real credential. Its screenshots are evidence under the
  [security never-list](../../.claude/rules/security.md).
- **Third-party services.** The Refero and typeui registries are read, never written to: no source code,
  product screenshot or tenant data goes to them.
- **Attribution.** What these tools write carries no assistant attribution, as everywhere else.

## The design pass, in every UI step

1. **Read** the step, its rows in [`ui-ux.md`](ui-ux.md), this file, and the frontend's `PRODUCT.md`
   and `DESIGN.md`.
2. **Shape:** `/impeccable shape <the screen>`, starting from [the football in it](#the-football-in-it).
   A moment also takes a direction from `design-taste-frontend`, briefed with that section.
3. **Build** with shadcn/ui and the tokens, through its skill: logical CSS, both catalogs, every state.
4. **Look** with Playwright CLI at 360, 768 and 1440 pixels, in `ar` and `en`, light and dark.
5. **Review:**
   - `/impeccable critique` and `/impeccable audit` on the changed surface;
   - `npx impeccable detect` on the changed files and on the running page.

   Fix every P0 and P1. A P2 or P3 left for later goes under "Not in this PR".
6. **Evidence:** screenshots from the capture tool (`npm run evidence`) in Arabic and English (and at
   mobile width when the layout changes), the journeys' axe results, and the review's summary in the
   report.
