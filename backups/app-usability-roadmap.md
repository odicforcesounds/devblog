---
doc: app-usability-roadmap
type: roadmap
apps: [Civic Perks, Social Tool Kit]
platform: web
targets:
  civic-perks: mobile-first, 360 px baseline
  social-tool-kit: desktop-first normal website, phone readable
audience: ai-coding-agent
status: proposed
cost: free-only
updated: 2026-11-09
source_docs:
  - backups/civic-perks-usability.md
  - backups/social-tool-kit-usability.md
---

# App usability roadmap — Civic Perks + Social Tool Kit

Internal planning note for the author. Not published, not linked from `docs/`.
Written 2026-11-09. Merges `backups/civic-perks-usability.md` and
`backups/social-tool-kit-usability.md` into one order of work. Nothing here is implemented.

**Shared diagnosis.** Both apps fail at the same two moments: the first visit (too much is
asked before anything is shown) and the second week (nothing brings the person back). Civic
Perks can be tried without an account, so it is the faster activation win. Social Tool Kit
needs a public proof before it can recruit a group, so its first job is to make published
work visible.

## How an AI agent uses this roadmap

- The table is the dependency order. Do not start a row before the rows it needs are stable.
- One workstream per change. Open the app document and take the lowest unblocked task ID
  (`CP-xx` or `STK-xx`); the roadmap does not replace the task's acceptance criteria.
- Respect the surface split: Civic Perks is phone-first; Social Tool Kit is a normal
  desktop-first website whose phone layout must stay readable. No native build for either.
- Do not start a feature bet before the P0 rows are done and measured.
- Evidence for every change: task ID, files, behaviour, exact commands and results, measured
  numbers. If the code contradicts the spec, stop and report it instead of changing a product
  rule silently.

## Free-only rule

Every choice in this roadmap runs on a free service, a free tier or an open-source library.
No trial that expires into a paywall, no credit card, no paid dependency in the core loop.
Document the quota, cache the result, and name the fallback before adding a service. Prefer
on-device AI to a paid API, MapLibre and OpenStreetMap to a paid map, and a self-hosted
component to a vendor. Organisation subscriptions are allowed as revenue only if the core
loop still works without them. Apple sign-in is out while it requires a paid developer
account.

## Order of work

| Order | Workstream | App | Priority | Effort | Why now |
| --- | --- | --- | --- | --- | --- |
| 1 | Visitor map: read-only pins, inline sign-in, guest drafts | Civic Perks | P0 | M | Fastest path to a first confirmed pin |
| 2 | Location pre-prompt and denied fallback | Civic Perks | P0 | S | A denial currently ends the session |
| 3 | Three-tap pin + duplicate-to-confirm | Civic Perks | P0 | M | The core loop is the product |
| 4 | One-tap, distance-aware confirmation + status timeline | Civic Perks | P0 | M | Confirmation is what makes the map trustworthy |
| 5 | Seeded city pack + plain-language flag/cap/Vanguard | Civic Perks | P0 | M | An empty map reads as a broken app |
| 6 | Public catalogue of published proofs (logged out) | STK | P0 | M | A stranger must see the product before signing in |
| 7 | Group wizard with invite link + human-passable verification | STK | P0 | M | Group formation is the first hard wall |
| 8 | Challenge templates + take/release handshake | STK | P0 | M | Makes a first challenge plausible |
| 9 | Legible seven-verdict gate with deadline and reasons | STK | P0 | M | Trust mechanism currently invisible |
| 10 | Moderation: reports, block, audit log, appeals | Both | P0 | M | Required before any growth push |
| 11 | Consent at the recorder + takedown path | STK | P0 | M | Filming people without consent is the main legal risk |
| 12 | Harden the existing admin panel: 2FA, audit log, appeals | STK | P1 | M | Panel exists; make it accountable |
| 13 | Layouts per surface: Civic Perks phone-first, STK desktop-first | Both | P1 | M | Each app has one primary surface |
| 14 | Server-side counts, idempotency, rate limits, backups | Both | P0 | M | Coins and XP are money-like |
| 15 | Offline outbox + list view + filters | Civic Perks | P1 | M | Pins are made where coverage is worst |
| 16 | Email-link sign-in + guest merge | Civic Perks | P1 | L | Google-only excludes the unwilling |
| 17 | Shareable per-challenge page + discovery by cause/place | STK | P1 | M | A finished proof needs an address |
| 18 | Notifications: confirmations, verdicts, review requests | Both | P1 | M | The second visit has to be invited |
| 19 | Four-language parity + accessibility in the app | Both | P1 | M | The wiki promises what the app must deliver |
| 20 | Activation and time-to-proof dashboards | Both | P1 | S | Otherwise every later decision is opinion |

## Two weeks, two tracks

The two apps can move in parallel because they touch different codebases; the only shared
work is the design system and the analytics schema. One person should not run both tracks at
full speed — pick the track that matches the launch you are actually doing, and keep the
other in review.

### Week 1

| Day | Civic Perks | Social Tool Kit |
| --- | --- | --- |
| 1 | Read-only visitor map behind a feature flag; sign-in strip instead of modal | Public catalogue route and layout, fed by published challenges only |
| 2 | Pre-permission sheet; ask on first action; denied banner with browser paths | Sign-in screen copy; "look around first"; remove the old download note |
| 3 | Tap-to-place fallback and unverified-by-distance badge | Group wizard step 1–2: name, cause, invite link |
| 4 | Camera-first +Pin; three category chips; 140-char note | Verification by DNS or meta tag, with manual review fallback |
| 5 | Client-side compression, upload progress, draft in IndexedDB | Group profile page; roles; transfer leadership; pending explanation |
| 6 | 25 m duplicate query and "confirm instead" merge | Challenge templates (two per path) with shot lists |
| 7 | Pin sheet with distance, age, accuracy; one-tap confirm | Take/release with deadline, reminder and reason codes |

### Week 2

| Day | Civic Perks | Social Tool Kit |
| --- | --- | --- |
| 8 | "Still there?" 14-day re-confirm; status timeline | Review progress 4/7, deadline, criteria, conflict rules |
| 9 | Seed one city pack (30–50 team pins); label seeded content | Review queue with reason codes; denial explanation |
| 10 | Explain flag, cap (18 of 20) and Vanguard in four languages | Publish page with verdict summary; appeal link |
| 11 | Report/block buttons; address fuzzing at ~30 m | Face-release screen; blur option; guardian consent |
| 12 | Moderator queue with merge, remove, audit entry | Admin hardening: 2FA, audit log, hourly limits, appeal path |
| 13 | Phone-first install and offline outbox | Desktop two-pane review queue; phone readability check |
| 14 | Analytics events; funnel dashboard v1 | View counting transaction; points definition on screen |
| 15 | Ship, measure first-pin rate, fix the biggest drop | Ship, measure sign-in → first published proof |

## Weeks 3–6

| Week | Focus | Exit test |
| --- | --- | --- |
| 3 | STK: in-app 60-second recorder, trim, gallery upload, parser coaching; CP: offline outbox | A proof can be recorded and submitted without leaving the app |
| 4 | Both: notifications for the three transactional events; email link sign-in | A confirmation and a verdict arrive without opening the site |
| 5 | STK: per-challenge public pages, sitemap, OG images; CP: list view and filters | A published proof renders logged out and previews in a chat app |
| 6 | Both: four-language pass, screen-reader pass, accessibility audit | Core loop completes with a screen reader at 200% zoom |

## Build once, use twice

These pieces are near-identical in both apps and should share a specification, even if the
code is duplicated:

- **Identity:** Firebase Google + email link, account linking, export, delete. Apple is out
  while it needs a paid developer account.
- **Camera/upload:** 60 s cap, trim, 720p compression, consent record, retry, local draft.
- **Outbox:** IndexedDB queue with visible pending state and backoff.
- **Notifications:** three transactional events, quiet hours, one unsubscribe.
- **Moderation:** reason codes, report/block, audit log, appeal, 24–48 h targets.
- **Analytics schema:** visit, identity, create, confirm/take, publish, install — no PII.
- **i18n:** PT/EN/ES/FR with a shared glossary (pin, scout, challenge, proof, verdict).
- **Design tokens:** 48 px targets, 16 px body, 4.5:1 contrast, reduced motion.

## Feature bets beyond the first release

These are the new-feature possibilities from both guides, ordered by what they unlock. They
start only after the P0 pass is stable; each one gets a two-week prototype and a kill test.

| Bet | App | What it unlocks | Fit | Effort |
| --- | --- | --- | --- | --- |
| Street quest chains | Civic Perks | A reason to return without a notification | Core | S |
| Before/after share cards | Civic Perks | The only unprompted share the product has | Core | M |
| OSM note bridge | Civic Perks | Reports that outlive the app | Adjacent | M |
| Embeddable ward map | Civic Perks | Council and NGO distribution | Adjacent | M |
| QR/NFC spot tags | Civic Perks | A physical entry point, presence without tracking | Product change | M |
| Blind review | STK | Tests whether verdicts are about the proof | Core | S |
| AI pre-screen and captions | STK | Less reviewer work, human still decides | Adjacent | L |
| Funder-ready PDF | STK | A reason for a group to publish again | Core | M |
| Group task thread | STK | Coordination stops happening off-platform | Core | M |
| Public proof pages and API | STK | Shareable, indexable evidence | Adjacent | M |
| Passkeys everywhere | Both | Fewer identity dead ends | Core | S |
| Home-screen widget (Civic Perks) | Civic Perks | A surface outside the browser tab | Adjacent | M |

**How to choose.** Score each bet on four things: does it shorten the path to a first
confirmed pin or a first published proof; does it add a moderation or privacy burden; can it
be measured in two weeks; and does it still fit the product's stand (no feed, no surveillance,
no money to users). A bet that scores well on reach but badly on the last two is a product
decision, not a sprint.

**Sequence.** After the P0 pass: street quests and blind review (cheapest, core), then the
share cards and the funder PDF (retention and legitimacy), then the OSM bridge and public
proof pages (distribution), then the council widget and the QR tags (partnerships), and only
then the AI assist and the low-data mode.

## Definition of done for the first release

- **Civic Perks:** a logged-out visitor sees at least 30 pins in the launch city, and 35% of
  visitors who open the map publish or confirm a pin within 24 hours; median time from
  report to first confirmation under 48 hours.
- **Social Tool Kit:** a logged-out visitor can open three published proofs; 50% of
  sign-ins verify a group within 48 hours; 25% of published challenges receive a proof; the
  median wait for seven verdicts is under 48 hours.
- **Civic Perks:** the core loop reads and works at 360 px, installs from the browser and
  survives offline; every reward write is idempotent.
- **Social Tool Kit:** the review flow works at 1280 px with a keyboard, still reads at
  360 px, and every coin and view write is idempotent.

## Risks and what would change this order

- **Empty launch city.** If 30 seeded pins cannot be produced, do not launch there; a
  neighbourhood pilot with three scouts is better than a city with none.
- **Google-only identity.** If Firebase email-link cannot be enabled quickly, keep Google and
  the visitor mode as the escape hatch; Apple is out under the free-only rule.
- **Moderation capacity.** Do not run a growth campaign before report/block exist and the
  admin panel logs what it removes; one harassment incident costs more than the campaign
  gains.
- **Filming consent.** If the consent record cannot ship with the recorder, restrict proofs
  to no identifiable people until it does.
- **API cost.** Loading map tiles and video for logged-out visitors has a cost; cap the
  catalogue at recent proofs and lazy-load thumbnails.

## Source notes

- `backups/civic-perks-usability.md` — 17 items, evidence and acceptance tests.
- `backups/social-tool-kit-usability.md` — 18 items, evidence and acceptance tests.
- `backups/civic-perks-p0-checklist.md` — the Civic Perks P0 work broken into tasks.
- `backups/civic-perks-microcopy.md` — the plain-language strings for flag, cap, Vanguard.
