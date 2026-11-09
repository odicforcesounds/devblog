---
doc: civic-perks-usability
app: Civic Perks
app_url: https://civic-perks.org
type: ai-implementation-brief
platform: web
target: mobile-first, 360 px baseline
audience: ai-coding-agent
status: proposed
cost: free-only
updated: 2026-11-09
companions:
  - backups/civic-perks-p0-checklist.md
  - backups/civic-perks-microcopy.md
hard_constraints:
  - no native app, APK or store build
  - free services, free tiers or open-source libraries only
  - phone-first; desktop is a fallback that must not break
  - no public feed, follower graph or direct messages
  - no live location of scouts and no sale of location data
  - no ads beyond the opt-in rewarded video
non_goals:
  - native wrappers
  - street or individual public rankings
---

# Civic Perks — usability improvements

Internal working notes for the author. Not published, not linked from `docs/`.
Written 2026-11-09 from the live app (`civic-perks.org`), its privacy and terms pages, the
official rules page (`wiki.odicforcesounds.com/presentation-container.html`) and the growth
guide. Everything below is a proposal; nothing here is implemented.

**What the app is today.** A location-based civic game. A scout walks, drops a pin with a
photograph, another scout confirms it, a third scout unlocks validation and solving. Rewards
are XP and Impact Credits, with quests, boosts, leaderboards and verified weekly reports.
Sign-in is Google through Firebase; the map is OpenStreetMap; hosting is Cloudflare; an
optional rewarded video from AppLixir pays for a boost. New pins are auto-verified but
flagged for back-check, and the daily cap is 20. Under three scouts the area is in
**Vanguard** state, where credits stay flat and predictable. Minimum age is 16.

**The one-sentence diagnosis.** The map is the product, but a first-time visitor sees an
empty map and a sign-in wall, and a second-time visitor has no reason to come back. Almost
every improvement below attacks one of those two moments.

## How to read this

- **P0** — blocks a first-time visitor from reaching the first confirmed pin. Do these first.
- **P1** — decides whether the second week happens.
- **P2** — polish, scale, and the things that only matter once there are users.
- Each item has the problem, the change, and a test that says it is done.
- Effort is a rough size for one person: S (a day), M (a few days), L (a week or more).
- New features are collected in the section before "What not to build". The fit column says
  whether a feature strengthens today's loop or changes what the product is.

## AI implementation brief

**Read order.** Front matter → this brief → one task section → the data model. This file is
the specification; implement it in the app repository, not here.

**Surface.** A phone-first web app that already feels like an Android app. The phone is the
product; desktop is a fallback that must not break. No native build, no store listing, no
second mobile product.

**Phone contract (check after every change).**
- 320–430 px wide, 360 px baseline, one column, no horizontal scroll at 320 px.
- Targets 48 × 48 px; primary action in the bottom third; safe-area padding.
- Inputs 16 px or larger; labels visible; the keyboard never covers the submit action.
- No hover-only action; every map action has a list equivalent.
- Offline draft survives reload; 200% zoom and reduced motion respected.
- First load under 200 KB of JavaScript compressed; tiles and the ad lazy.

**Non-negotiable rules.**
- No feed, follower graph or direct messages.
- No live scout position, no movement history, no sale of location data.
- No ads beyond the opt-in rewarded video; no pay-to-win.
- One confirmation per account per pin; 20 pins per day; Vanguard at three scouts.
- Private addresses fuzzed; 16+ only; ad consent withdrawable.

**Task order.** `CP-01 → CP-03 → CP-04 → CP-05 → CP-07`; `CP-02 → CP-03`; `CP-06` and
`CP-14` can run in parallel; `CP-08`, `CP-09` and `CP-12` follow `CP-03`; `CP-11` follows
`CP-01`; `CP-17` is instrumented with `CP-01` and `CP-03`.

**Protocol.**
1. Pick the lowest-numbered task whose dependencies are done.
2. Read its section and the data model; map names to the real code, do not invent files.
3. Change the smallest surface that satisfies "Done when"; no unrelated refactor, no new
   dependency without a stated reason.
4. Run the repository's formatter, linter, typecheck, tests and build; record exact commands.
5. Check the phone matrix: 360 px, 320 px, keyboard, offline, 200% zoom, screen reader.
6. Report: task ID, files, behaviour, commands and results, measured numbers, follow-ups.
   One task per change.

**Data model (suggested; adapt names to the codebase).**
```text
users/{uid}                displayName, email, locale, xp, credits, role, createdAt
pins/{pinId}               lat, lng, geohash, areaId, category, photo, note,
                           status(reported|confirmed|fixed), flag(new|none),
                           createdBy, createdAt, accuracyM, duplicateOf,
                           confirmationCount, afterPhoto
confirmations/{pinId_uid}  verdict(can_see|gone|unsure), distanceM, createdAt
reports/{reportId}         targetType, targetId, reporterUid, reason, status, createdAt
zones/{areaId}             scoutCount, unlocked
outbox (IndexedDB)         draftId, photoBlob, lat, lng, accuracyM, category, note, attempts
```
**Invariants.** One confirmation per `uid` per pin. The 20-pin cap is enforced server-side. A
same-category pin within 25 m offers confirmation first. Rewards are written once with an
idempotency key. No document stores a scout's live position or a history of it.

**Suggested callables.** `createPin`, `confirmPin`, `mergeDuplicate`, `reportContent`,
`awardCredits` — each validates shape, auth and rate limit, and is safe to retry.

**Every screen needs five states.** loading (skeleton, not a spinner over the map), empty
(with the next action), error (plain sentence and a retry), offline (what is saved), success
(one sentence and the next step).

**Verification.** The app repository owns the commands; run what exists and do not add
tooling to satisfy this document. Minimum evidence: lint, typecheck, unit tests, build, plus
the manual phone matrix. Report a check that could not run as a limitation, never as a pass.

## Priority table

| # | Improvement | Priority | Effort |
| --- | --- | --- | --- |
| 1 | Let a stranger see a living map before signing in | P0 | M |
| 2 | Explain location before the browser asks, and survive "no" | P0 | S |
| 3 | Make the first pin a three-tap action | P0 | M |
| 4 | Turn duplicates into confirmations | P0 | S |
| 5 | Make confirmation a one-tap, distance-aware action | P0 | M |
| 6 | Fill the empty map with a seeded city pack | P0 | M |
| 7 | Explain the flag, the cap and Vanguard in plain words | P0 | S |
| 8 | Keep drafts and pins when the phone is offline | P1 | M |
| 9 | Add a list view and filters beside the map | P1 | M |
| 10 | Give every pin a visible status timeline | P1 | S |
| 11 | Add email-link sign-in and merge guest progress | P1 | L |
| 12 | Install as a PWA, and load the ad only on demand | P1 | M |
| 13 | Notify on confirmation, not on marketing | P2 | M |
| 14 | Moderation, reporting and location privacy | P0 | M |
| 15 | Accessibility and four-language parity | P1 | M |
| 16 | Fair rewards and anti-farming | P2 | M |
| 17 | Measure activation, not downloads | P1 | S |

## CP-01 · Let a stranger see a living map before signing in (P0)

**Problem.** The app opens on a map that asks for an account before the product proves
itself. A visitor who does not want to hand a Google identity to an unknown civic game
leaves without ever seeing a pin.

**Change.**

- Open on the map in a read-only **visitor** state: tiles, pins, categories, pin details and
  the weekly public reports are visible; only writing needs an identity.
- Replace the blocking modal with one inline strip: "Sign in to pin, confirm and keep your
  XP" plus a "Look around first" dismissal that stays dismissed.
- Keep a **local guest scout**: pins drafted before sign-in are stored locally and offered
  for upload after sign-in, with a count ("3 pins waiting").
- Show the nearest five pins and one line of real activity ("last confirmed 2 h ago in
  Bonfim") so the visitor knows the map is alive.

**Done when.** A logged-out visitor can pan, zoom, open a pin, read its photo and see the
city's last confirmed pin without any network write and without an account.

## CP-02 · Explain location before the browser asks, and survive "no" (P0)

**Problem.** The permission prompt arrives cold, often on first paint. A denial is
effectively a dead end, and a denial is permanent for the origin until the user digs through
site settings.

**Change.**

- A pre-permission screen in plain language: what is read (precise position while playing),
  what is never shown (your live position to others), and why (placing and confirming pins).
  Only then call `getCurrentPosition`.
- **Denied fallback**: search an address or tap the map to place a pin, with a "this pin is
  unverified by distance" badge. The game still works, it just earns less.
- A persistent, dismissible banner explaining how to re-enable location, with the exact
  browser path for Android Chrome and iOS Safari.
- Never ask for location on page load; ask at the first action that needs it.

**Done when.** A user who denies location can still create a pin by tapping the map, and a
user who grants it never sees the prompt before an explanation.

## CP-03 · Make the first pin a three-tap action (P0)

**Problem.** Reporting is the core loop, but it competes with forms. Every extra field
before the camera is a lost pin.

**Change.**

- A single large **+ Pin** button in thumb reach, above the bottom edge, that opens the
  camera immediately. Photo first, everything else after.
- The photo screen carries three big category chips (fix / protect / needs help) with icons
  and one line each. Choosing one is the second tap; **Send** is the third.
- Location is pre-filled with an accuracy circle and a draggable pin. "Use my position" is
  the default; "move pin" is one tap away.
- Everything optional goes behind "Add a note" (one text field, 140 characters, with
  dictation). No tags, no severity slider, no title field on the first pass.
- Compress the photo client-side to about 1600 px on the long edge before upload, and show
  the upload as a thumbnail with a progress ring, not a spinner over the whole map.
- Warn once, at the moment of pinning, about private property and roads, and never require
  the user to stand in traffic to satisfy an accuracy threshold.

**Done when.** A new user with location granted can publish a photographic pin in under 20
seconds, measured on a mid-range Android phone.

## CP-04 · Turn duplicates into confirmations (P0)

**Problem.** Two neighbours report the same broken lamp and the map fills with overlapping
pins. The visitor reads it as noise, and the second reporter earns less than they expect.

**Change.**

- On the confirm screen, query pins within 25 m in the same category. If one exists, offer
  "Someone already reported this — confirm it instead" with the existing photo.
- If the user still creates a new pin, keep it but link it to the original as a duplicate
  candidate for moderation, and do not count it twice in zone totals.
- Merge duplicates when a moderator accepts, preserving both photos and both reporters'
  credit.

**Done when.** Reporting within 25 m of an existing same-category pin offers confirmation
first, and the merged pin shows both photos.

## CP-05 · Make confirmation a one-tap, distance-aware action (P0)

**Problem.** Confirmation is the second half of the loop, and it is where the map's trust
comes from. Today it asks for more attention than a walker has.

**Change.**

- Open a pin as a bottom sheet with the photo, category, age, distance and one primary
  button: **I can see it**. Optional secondary: "It's gone" and "Not sure".
- Show the distance and the accuracy circle on the sheet; refuse a confirmation from more
  than the allowed radius with a plain sentence, not a silent failure.
- Add a **"still there?"** state: if a pin is older than 14 days, ask the next visitor to
  re-confirm before it counts again.
- Let the confirm action work from the list view and from a notification, not only from the
  map.
- Reward the confirmer visibly at the moment of confirmation (XP tick and one sentence),
  and never with a modal that hides the map.

**Done when.** A confirmation is one tap from a pin sheet, works from a list, and a
too-far attempt explains itself.

## CP-06 · Fill the empty map with a seeded city pack (P0)

**Problem.** An empty map is indistinguishable from a broken app. Cold-start rules protect
the first scout but cannot invent neighbours.

**Change.**

- Ship a **city pack** per launch area: 30–50 real, pre-verified pins collected by the
  operator during the pilot, each with a photo and a date, attributed to "Civic Perks team".
- Keep a clear visual difference between team-seeded and scout-created pins, and age them
  out after 90 days unless re-confirmed.
- Zero-state call to action: "This street has no pins yet. Adopt it for a week" with a
  one-tap quest for five pins on the same street.
- Show a small "3 scouts unlock validation here" progress line, so the Vanguard state reads
  as a goal rather than a punishment.
- Never fake activity ("12 people online") — seeded content is labelled.

**Done when.** A new city opens with at least 30 team pins, and a zero-pin street offers the
adopt-a-street quest.

## CP-07 · Explain the flag, the cap and Vanguard in plain words (P0)

**Problem.** The rules are honest but written for the operator: "auto-verified but flagged
for back-check", "credits stay flat and predictable", "validate/solve wait until a third
scout". A new scout cannot tell whether they did something wrong.

**Change.**

- Put a one-line status on every pin: **Reported → Confirmed → Fixed**, with the next step
  and who does it.
- Explain the flag positively: "We accept your pin now. A neighbour's confirmation removes
  the 'new' mark."
- Show the cap as a resource, not a punishment: "18 of 20 pins left today", with the reset
  time in local time.
- In Vanguard, say what still works (walking, reporting, quests) before what does not.
- Put the same sentences in the four supported languages; keep them under 20 words each.

**Done when.** A first-time user can say, without opening the wiki, what happens after they
press Send and why nothing is payable yet.

## CP-08 · Keep drafts and pins when the phone is offline (P1)

**Problem.** Pins are made outdoors, where coverage is worst. A failed upload currently
loses the photo and the walk.

**Change.**

- Store the pending pin (photo blob + coordinates + category) in IndexedDB, show it on the
  map as a dashed outline, and retry with backoff.
- A visible **Outbox** in the profile with counts, last error and a manual retry.
- Cache the last viewed tiles and the pin list for the current city so the map still draws
  offline.
- Never block the camera on a network check.

**Done when.** A pin created in airplane mode is visible as pending, survives a reload, and
publishes automatically when the connection returns.

## CP-09 · Add a list view and filters beside the map (P1)

**Problem.** A map is poor at answering "what is near me and still open?", and impossible
for some users and some screens.

**Change.**

- A segmented control: **Map / List**. The list sorts by distance, shows category icons,
  status and age, and supports the same confirm action.
- Filters as chips: category, status (new / confirmed / fixed), age, "walking distance".
- Cluster pins at low zoom, and show counts instead of individual pins until the user zooms
  in.
- A "near me" button that also works from the list, and a visible scale bar.
- One-handed sheet for pin details with a drag handle; never rely on hover or right-click.

**Done when.** Every map action is available in the list, and the list is usable with the
keyboard and a screen reader.

## CP-10 · Give every pin a visible status timeline (P1)

**Problem.** The game's value is the record of what happened, but the UI shows a snapshot.

**Change.**

- On the pin sheet, a timeline: reported (who, when, photo), confirmed (who, when), fixed
  (who, when, optional after photo), with the current state highlighted.
- Allow one **after photo** when a scout marks a pin fixed; it is the proof the street
  changed and the most shareable object the app has.
- Link the weekly report to the pins it counts, so the report is auditable.

**Done when.** Any pin shows its full history, and a fixed pin carries an after photo.

## CP-11 · Add email-link sign-in and merge guest progress (P1)

**Problem.** Google-only is a hard wall for iPhone users, people without a Google account,
and anyone unwilling to link a real identity to a civic map. The terms already promise a
single account per person; identity choice should match.

**Change.**

- Firebase email-link sign-in (no password), with the same account-linking rules. Apple
  sign-in needs a paid developer account, so it stays out while the rule is free-only.
- On first sign-in, offer to attach the local guest scout's pins and XP to the account.
- Account screen: change display name, export data (JSON), delete account and local data,
  sign out of all devices.
- Explain the Google scopes on the sign-in button itself, not in a policy page.
- Keep the test account strictly out of production paths and label it in the UI if it is
  ever visible.

**Done when.** A new user can create an account with an email address only, and a guest's
draft pins survive sign-in.

## CP-12 · Install as a PWA, and load the ad only on demand (P1)

**Problem.** A browser tab is easy to lose, and the rewarded video is a third-party SDK that
should never sit on the critical path.

**Change.**

- Web app manifest, maskable icons, standalone display, theme colour, iOS meta tags, and an
  install prompt shown only after the first confirmed pin.
- A service worker that caches the shell, the last map view and the pin list; never cache
  the sign-in callback.
- Load AppLixir only when the user opens the Boost shop and chooses the video option, and
  show a plain "watch a video" label with the reward stated before the click.
- Budget: first load under 200 KB of JavaScript compressed, map tiles lazy, no web font on
  the critical path.
- A visible "low data" switch that disables photos in the list and reduces tile detail.

**Done when.** The app installs to the home screen, opens offline to the last map, and makes
no AppLixir request until the boost shop is opened.

## CP-13 · Notify on confirmation, not on marketing (P2)

**Problem.** There is no reason to return except a walk, and the weekly report arrives too
late to close the loop.

**Change.**

- Web push (or email if push is refused) for exactly three events: your pin was confirmed,
  a pin near you needs a second scout, your weekly report is ready.
- Ask for notification permission only after the first confirmation, and default to a weekly
  digest rather than per-event noise.
- Quiet hours in local time, a one-tap unsubscribe in every message, and no re-engagement
  nudges aimed at dormant users.

**Done when.** A user can receive a confirmation notice, silence it, and never be asked
again.

## CP-14 · Moderation, reporting and location privacy (P0)

**Problem.** A civic map collects precise movement and photographs of streets, and it will
attract false reports, harassment and privacy complaints. The current text promises process;
the app needs the buttons.

**Change.**

- Report a pin (false, duplicate, unsafe, private property, offensive) and report a user,
  each with reason codes and a confirmation that a human will review.
- Block a user; hide their pins locally immediately.
- Fuzz private addresses: when a pin is within ~30 m of a residential address, snap the
  public marker to the street or a 50 m grid, and say so.
- Never expose a live position, a home location from a profile, or a scout's movement
  history. The 15-minute presence heartbeat should be aggregate-only.
- A moderator queue with merge, remove, restore, and an audit log; an appeal path with a
  response target.
- Safety interstitial on first pin and on the weekly report; keep the emergency disclaimer
  visible on the map's "about" sheet.
- Age gate consistent with the 16+ terms, plus a clear child-data removal contact.
- Honour GDPR/LGPD rights in-app: export, delete, withdraw ad consent, and a record of the
  consent version.

**Done when.** A pin and a user can be reported and blocked from the app, a moderator can act
with an audit trail, and a private-address pin is fuzzed by default.

## CP-15 · Accessibility and four-language parity (P1)

**Problem.** The app is used outdoors, one-handed, in sunlight, by people with wet hands,
old phones and different languages. The wiki carries four languages; the app should not be
the weakest link.

**Change.**

- Minimum 48 × 48 px targets, 16 px body text, 4.5:1 contrast for text on map overlays, and
  a high-contrast map style option.
- A text alternative to the map: the list view is the accessible path, with pin buttons that
  read "Broken light, confirmed 2 days ago, 40 metres away".
- Keyboard pan/zoom, visible focus, no keyboard trap in the pin sheet, `aria-live` for
  confirmations and errors.
- Respect reduced motion for XP animations and map fly-to.
- Complete PT/EN/ES/FR strings, no hard-coded English in toasts, dates and numbers in the
  user's locale, and a language switch in Profile that survives a reload.
- Test at 200% text zoom without clipping the primary action.

**Done when.** The core loop (find, confirm, report) is completable with a screen reader and
at 200% zoom, in all four languages.

## CP-16 · Fair rewards and anti-farming (P2)

**Problem.** XP, credits, boosts and leaderboards create incentives before the app has
anti-abuse. The terms reserve the right to correct balances, which is an admission that the
economy can be gamed.

**Change.**

- Server-side validation of every award: one award key per action, idempotent writes, rate
  limits per account and per device.
- Detect impossible travel and duplicate photos (perceptual hash) before paying.
- Publish the reward table in the app so the economy is predictable, and never sell XP.
- Leaderboards opt-in, scoped to a city or a street, with an option to appear as
  "a scout in Bonfim".
- Make the ad-free path obvious: credits buy the same boosts, and watching a video is never
  the only route.
- Communicate cap resets and seasonal resets in advance.

**Done when.** Replaying a reward request cannot pay twice, and every leaderboard is
opt-in and place-scoped.

## CP-17 · Measure activation, not downloads (P1)

**Problem.** Without product events, every decision above is an opinion.

**Change.**

- Events with no personal data: map_view, pin_start, pin_published, confirm_attempt,
  confirm_success, sign_in, install, report, boost_open.
- The funnel that matters: first map view → first pin published → first confirmation
  received → second pin in 7 days. Report it weekly by city.
- Operational numbers: time from report to first confirmation, share of pins older than 14
  days without a second scout, empty-street ratio, crash-free sessions, tile and ad cost per
  active scout.
- A staging project with the same rules, so economy changes are tested before production.
- Feature flags for city packs and cold-start rules.

**Done when.** A weekly dashboard answers "where do new scouts stop?" for each launch city.

## Free-only stack and attractive additions

**Rule.** Every feature below must run on a free service, a free tier or an open-source
library. No trial that expires into a paywall, no credit card, no paid dependency in the
core loop. Revenue features may charge organisations, but a scout must never pay to pin,
confirm or read. Quotas are documented, results cached, and every free dependency has a
fallback (self-host or degrade) if its terms change.

### Free stack

| Need | Free option | Note |
| --- | --- | --- |
| Hosting | Cloudflare Pages or Firebase Hosting free tier | static site plus functions quota |
| Auth | Firebase Authentication free tier | Google and email link only; Apple needs a paid account |
| Database | Firestore free quota, or self-hosted MongoDB | cache reads; watch the daily quota |
| Maps and tiles | MapLibre GL JS with OpenStreetMap tiles | attribution required; cache; self-host tiles if traffic grows |
| Geocoding | Nominatim, self-hosted or public with a policy-compliant rate | cache results |
| Weather | Open-Meteo | no key, free for non-commercial use |
| Local knowledge | Wikipedia and Wikidata REST APIs | attribute, cache, no bulk scraping |
| Email | Brevo or Resend free tier | check the current daily limit; plain text fallback |
| Push | web-push with VAPID keys | open standard, no service fee |
| QR | qrcode (MIT) | generated on the device |
| Analytics | Umami or Plausible CE, self-hosted | no third-party cookies |
| On-device AI | Transformers.js, MediaPipe or TensorFlow.js | no per-request cost; download once |
| Errors | GlitchTip self-hosted, or Sentry free tier | scrub personal data |
| CI | GitHub Actions free minutes for public repositories | cache dependencies |

### Attractive additions that stay free

| Feature | What it adds | Free stack | Effort |
| --- | --- | --- | --- |
| Local history card | A short "this street was…" card from Wikipedia/Wikidata on a pin or street page | Wikipedia/Wikidata APIs | S |
| Weather-aware quests | Rain forecast turns on a drain-clearing quest for the week | Open-Meteo | S |
| Purposeful walk routes | A loop that passes five open pins, generated from the map | OSM + BRouter | M |
| Street time-lapse | The same corner across months, played from stored photos | Canvas, local storage | M |
| Adopt a drain or bench | A named fixed spot with a watering or clearing reminder | OSM tags + local reminders | M |
| Neighbourhood quiz | "What is this?" from local photos, with a short explanation | static JSON + Wikidata | S |
| Fix of the week | One human-curated repair, no algorithm | editorial | S |
| Printable street poster | A4 poster with a QR code for a shop window | print CSS + qrcode | S |
| Share card | Before/after image with the street name, made on the phone | Canvas | S |

## New feature possibilities

These are additional to the P0 work, not replacements for it. **Fit** is the column that
matters: **Core** strengthens the loop the app already has; **Adjacent** adds a surface that
keeps the same promise; **Product change** needs an explicit decision because it alters what
Civic Perks is; **Reject** is recorded at the end so the idea is closed rather than
rediscovered. Effort is S/M/L for one person.

### Participation and retention

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Street quest chains | Five linked pins on one street, progress bar, bonus at completion | Core | S |
| Crews of two to five | Shared streak and street, no public ranking of people | Core | M |
| Neighbourhood leagues | Opt-in area board by street, not by individual | Adjacent | M |
| Seasonal campaigns | "Drain week" before the rains, with a pack, a quest and a report | Core | M |
| Before/after gallery | Per street, with a slider and a share card; needs an after photo | Core | M |
| Monthly impact report | Pins, confirmations, streets covered; shareable image or PDF | Adjacent | M |
| Event mode | One-hour "fix-it Friday" quest with live progress | Adjacent | S |
| Streak grace days | A week off does not erase progress | Core | S |
| Mentor mode | First three pins with a buddy, who also gets credit | Adjacent | M |
| Category badges | Accessibility, water, safety; recognition without point inflation | Adjacent | S |

### Map, data and civic leverage

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| One-tap OSM note | Push a pin to OpenStreetMap as a note, with photo and description | Adjacent | M |
| Public open data | Monthly GeoJSON/CSV per city, ODbL-compatible attribution | Adjacent | M |
| Read-only public API | Keys, rate limits, docs, for researchers and civic hackers | Product change | M |
| Embeddable ward map | Cookie-free iframe for a council or NGO site | Adjacent | M |
| Aggregated heatmap | Time-lapse of pin density, never individual trails | Adjacent | M |
| Offline city pack | Download tiles and pins for an area, usable for a week | Core | L |
| Accessibility layer | Ramps, tactile paving, benches, accessible toilets as categories | Adjacent | M |
| Photo compare slider | Before and after on every fixed pin | Core | S |
| Street pages | Public URL per street with its pin history | Adjacent | M |
| Street-level imagery link | Mapillary or KartaView on a pin where available | Adjacent | S |

### Capture and verification

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Voice note | On-device transcription, with the text editable | Core | M |
| Ten-second video | For a hazard or a drain that a still cannot explain | Adjacent | L |
| Multi-photo pin | Up to three photos, first one is the cover | Core | S |
| Category suggestion | On-device model proposes a category from the photo | Adjacent | L |
| Perceptual-hash duplicates | Finds the same pothole beyond the 25 m radius | Core | M |
| QR/NFC spot tags | Weatherproof tag on a fixed spot; scanning opens its confirmation | Product change | M |
| Witness co-sign | A second scout at the scene confirms instantly | Adjacent | M |
| Time and place attestation | Stronger proof of presence, if it can be done without storing a trail | Product change | L |

### Identity, trust and institutions

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Passkeys | A second, phishing-resistant way in | Core | S |
| Organisation accounts | Council, NGO or school workspace with roles and a dashboard | Product change | L |
| Scout reputation | Privileges such as jury duty or zone edits, never a public score | Adjacent | M |
| Dispute jury | Three random scouts plus a moderator for contested pins | Adjacent | M |
| Partner-verified resident | A library or council vouches for a local address | Product change | L |
| Transparency report | Reports, removals, appeals and response times, published | Core | S |
| Moderation log | Removed pins with reason codes, no personal data | Adjacent | S |

### Platform, access and sustainability

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Home-screen widget | "Three pins near you" or the streak, without opening the app | Adjacent | M |
| Share target | Send a photo from the camera roll straight into a draft pin | Core | S |
| Calendar feed | ICS subscription for clean-ups and quest weeks | Adjacent | S |
| Audio guidance | Distance and direction to the next pin for low vision | Adjacent | M |
| Simplified mode | One action per screen and larger type | Core | S |
| More locales | Beyond PT/EN/ES/FR, added where a city pilot asks for it | Adjacent | M |
| Browser install | Add to home screen and a service worker, no store listing | Core | S |
| Sustainable funding | Council/NGO dashboard subscriptions, grants, donations | Product change | M |
| Researcher programme | Ethical review, aggregate data, published findings | Product change | M |

### Five bets worth prototyping

1. **Street quest chains.** The cheapest retention feature and the one that fits the existing
   loop. Test: three scouts complete five linked pins in seven days; measure completion and
   the share who return in week two.
2. **The OSM note bridge.** One tap turns a pin into an OpenStreetMap note, which gives the
   report a life beyond the app and a reason for mapping communities to care. Test: 20 pins
   pushed, five resolved, one partner interested.
3. **The embeddable ward map.** A council page that shows its own street pins is the most
   credible distribution channel available to a civic app. Test: one council embeds it;
   measure referred sessions and pins created from the referral.
4. **Before/after cards.** A fixed pothole with two photos is the only object in the product
   that people will share unprompted. Test: 30 fixed pins with after photos; measure shares
   and confirmations on those pins.
5. **QR/NFC spot tags.** A tag on a drain or a lamp proves presence without tracking a
   person, and gives a physical entry point. Test: ten tags, confirmations per tag, and one
   abuse attempt handled.

### Reject, with the reason

- **Public individual leaderboards by name** — turns neighbours into competitors and invites
  gaming; area-scoped, opt-in boards only.
- **A "street score" that ranks streets** — shames the people who live there and punishes
  the reporter for an honest map.
- **Live access for authorities** — a civic map is not a surveillance feed; aggregate reports
  only, with a warrant process if ever required.
- **Selling location or report data** — contradicts the privacy page and the promise.
- **Ads on the map or before the first pin** — the opt-in rewarded video is the ceiling.
- **AR pin overlays** — expensive, battery-hungry, and no evidence it helps a pin get
  confirmed; a demo, not a feature.
- **Downloadable installs** — the product is the website; installability comes from the
  browser, and a packaged build adds release and update overhead for no loop benefit.

## What not to build

- No public feed, no follower graph, no direct messages. They add moderation load and do not
  help a pin get confirmed.
- No live location sharing, no "scouts near you" map of people.
- No cash value, withdrawal or trading of credits, boosts or accounts.
- No gamified streak that punishes a week off; a missed day should not erase progress.
- No forced ad before the first value, and no ad on the map itself.
- No fake pins or invented activity to make a city look alive.

## First two weeks, in order

1. Visitor map + pre-permission screen + denied fallback (items 1–2).
2. Three-tap pin and duplicate-to-confirm (items 3–4).
3. One-tap confirmation and the status timeline (items 5, 10).
4. Seed one city pack and write the plain-language rules (items 6–7).
5. Moderation buttons, report and block, address fuzzing (item 14).
6. Instrument the funnel, then fix whatever it says is leaking (item 17).
7. Offline outbox, list view, PWA install (items 8, 9, 12).
8. Identity choices and guest merge (item 11).

## Assumptions to verify in the app

- Whether the visitor map is already readable before auth, or the map itself is gated.
- Whether a pin can be placed by tapping the map when location is denied.
- Whether drafts survive a reload or an offline upload today.
- Whether duplicate detection already exists server-side.
- Whether the four languages are complete in the app or only on the wiki.
- Whether XP and credit awards are written server-side with idempotency.
- The exact confirmation radius enforced, and whether it is explained in the UI.
