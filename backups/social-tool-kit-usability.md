---
doc: social-tool-kit-usability
app: Social Tool Kit
app_url: https://stk.odicforcesounds.com
type: ai-implementation-brief
platform: web
target: desktop-first normal website; phone readable
audience: ai-coding-agent
status: proposed
cost: free-only
updated: 2026-11-09
companions:
  - backups/app-usability-roadmap.md
hard_constraints:
  - no native app, APK or store build
  - free services, free tiers or open-source libraries only
  - desktop-first normal website; the phone must stay readable
  - no feed, follower graph, likes, comments or direct messages
  - no money to users and no public ranking of individuals
  - no exact locations of homes or shelters
non_goals:
  - native wrappers
  - auto-publish without seven verdicts
---

# Social Tool Kit — usability improvements

Internal working notes for the author. Not published, not linked from `docs/`.
Written 2026-11-09 from `stk.odicforcesounds.com`, the build log and simulator in
`docs/socialToolKit.html`, the official rules page
(`wiki.odicforcesounds.com/social-tool-kit.html`) and the growth guide. Everything below is
a proposal; nothing here is implemented.

Revised after author review: the admin panel exists, the wiki is available publicly and
in-app, and the product is a normal website used on desktop and readable on a phone. Item
14 is about desktop comfort, not a mobile rescue and not an install. Items 9 and 16 are
scoped to hardening and parity.

**What the app is today.** A workspace where a group takes on something that needs help,
films the proof, and seven outsiders decide whether it holds. Three paths organise the
actions: nature care (NCP), animal care (ACP) and human care (HCP). A Google account is the
identity; a group must be approved; a challenge costs two coins to publish, another group
takes it, the proof is published, and the seventh approval publishes the challenge while
seven denials remove it. Points are views, not verified impact. Coins are split between the
members who did the work and a treasury. Each user has a QR identity to be vouched for in
contexts. There is deliberately no feed, no followers and no money. An admin panel exists:
an allowlist that can block and unblock an account and remove a challenge or a member.
The wiki is available both publicly and inside the app. A site-first model is designed — a one-time twelve-character code, a domain file that proves
a group owns its site, a parsed video link from six sources, and view counting that ignores
brand-new accounts — and is modelled, not necessarily live.

**The one-sentence diagnosis.** The product asks for the three hardest things at once — an
account, a group and a camera — before it shows a single published proof, and it gives a
group no reason to come back after the seventh approval.

## How to read this

- **P0** — blocks a group from ever publishing a first proof.
- **P1** — decides whether a group publishes a second one.
- **P2** — trust, scale and the long tail.
- Each item has the problem, the change, and a test that says it is done.
- Effort: S (a day), M (a few days), L (a week or more).
- New features are collected in the section before "What not to build", with a fit label:
  Core, Adjacent, Product change or Reject.

## AI implementation brief

**Read order.** Front matter → this brief → one task section → the data model. This file is
the specification; implement it in the app repository, not here.

**Surface.** A normal website, used on desktop. Groups review proofs on a laptop and publish
from a phone. There is no APK, no store listing and no app shell; the phone must stay
readable but desktop is the primary workspace.

**Desktop contract (check after every change).**
- 1280–1920 px: sidebar navigation, two-pane review queue, reading measure near 70 characters.
- Keyboard: tab order, visible focus, shortcuts for next/previous proof and approve/deny.
- Hover may add information, never the only way to reach an action; resize never loses state.
- Video only on click; thumbnails lazy; first load under 250 KB of JavaScript compressed.

**Phone contract.** 360 px baseline, one column, 48 px targets, 16 px inputs, no horizontal
scroll, no hover-only action, video tap-to-play. Readable, not a second product.

**Non-negotiable rules.**
- No feed, follower graph, likes, comments or direct messages.
- No money to users; no public ranking of individuals or groups by points.
- Seven approvals publish, seven denials remove, seven reports go to a human.
- The publisher's group and the taker's group cannot review; one verdict per person.
- No exact home, shelter or minor's location; consent before an identifiable face is published.

**Task order.** `STK-02 → STK-03 → STK-04 → STK-05 → STK-06 → STK-07 → STK-08 → STK-10`;
`STK-01 → STK-11`; `STK-09` and `STK-15` can run in parallel; `STK-17` before any growth
push; `STK-12`, `STK-13` and `STK-16` after the first published proof.

**Protocol.**
1. Pick the lowest-numbered task whose dependencies are done.
2. Read its section and the data model; map names to the real code, do not invent files.
3. Change the smallest surface that satisfies "Done when"; no unrelated refactor, no new
   dependency without a stated reason.
4. Run the repository's formatter, linter, typecheck, tests and build; record exact commands.
5. Check the desktop and phone matrix: 1280 px, 1920 px, 360 px, keyboard, 200% zoom, screen
   reader, slow connection.
6. Report: task ID, files, behaviour, commands and results, measured numbers, follow-ups.
   One task per change.

**Data model (suggested; adapt names to the codebase).**
```text
users/{uid}                 name, email, locale, ageGate, role, createdAt
groups/{groupId}            name, cause, place, site, status(pending|approved),
                            verification{method,value,checkedAt}, leaderUid, treasury
memberships/{groupId_uid}   role(leader|member|reviewer), joinedAt
challenges/{challengeId}    title, path(NCP|ACP|HCP), goal, coins, templateId,
                            authorUid, groupId, phase, deadline, createdAt
proofs/{proofId}            challengeId, groupId, source, videoId, url, embed, thumb,
                            consent[], submittedAt
reviews/{proofId_uid}       verdict(approve|deny), reasonCode, createdAt
ledger/{entryId}            account, amount, reason, idempotencyKey, settledAt
views/{challengeId_uid}     windowStart, counted
reports/{reportId}          targetType, targetId, reporterUid, reason, status
```
**Invariants.** One verdict per `uid` per proof. Seven approvals publish; seven denials remove;
no auto-publish. The publisher cannot review. Views count once per account per window, and an
account younger than 48 h is stored but not counted. Every credit and coin write carries an
idempotency key and settles exactly once. No document stores a movement trail.

**Suggested callables.** `createGroup`, `verifyGroup`, `publishChallenge`, `takeChallenge`,
`releaseChallenge`, `submitProof`, `castVerdict`, `countView`, `settleLedger` — each validates
shape, auth, role and rate limit, and is safe to retry.

**Every screen needs five states.** loading (skeleton, not a full-page spinner), empty (with
the next action), error (plain sentence and retry), offline (what is saved), success (one
sentence and the next step).

**Verification.** The app repository owns the commands; run what exists and do not add
tooling to satisfy this document. Minimum evidence: lint, typecheck, unit tests, build, plus
the manual desktop and phone matrix. Report a check that could not run as a limitation,
never as a pass.

## Priority table

| # | Improvement | Priority | Effort |
| --- | --- | --- | --- |
| 1 | Show published proofs to strangers, without an account | P0 | M |
| 2 | Explain the Google dependency at the sign-in button | P0 | S |
| 3 | Turn group creation into a three-step wizard with an invite link | P0 | M |
| 4 | Replace the domain file with a check a non-developer can pass | P0 | M |
| 5 | Make the challenge form a template, not a blank page | P0 | M |
| 6 | Add a real "I'll take it" handshake, with release and reminder | P0 | M |
| 7 | Film in the app: 60 seconds, trim, retry, consent | P0 | L |
| 8 | Make the seven-review gate legible and time-boxed | P0 | M |
| 9 | Harden the existing admin panel: authentication, audit, appeals | P1 | M |
| 10 | Count views server-side, once, and say what points mean | P1 | M |
| 11 | Publish a challenge page that can be shared and indexed | P1 | M |
| 12 | Add discovery by cause and place, without a feed | P1 | M |
| 13 | Tell people what happened: review requests and verdicts | P1 | S |
| 14 | Desktop comfort and phone readability for the website | P1 | M |
| 15 | Consent, minors, filming and location rules in the flow | P0 | M |
| 16 | Accessibility and four-language parity in the app | P1 | M |
| 17 | Reliability: idempotency, rate limits, backups, monitoring | P0 | M |
| 18 | Measure time-to-first-proof, not sign-ups | P1 | S |

## STK-01 · Show published proofs to strangers, without an account (P0)

**Problem.** The first screen asks for a Google account before showing anything a stranger
can judge. There is no feed by design, which is defensible, but "no feed" has been implemented
as "no public product". A visitor cannot see what a published proof looks like.

**Change.**

- A public home that lists recently published challenges: photo or thumbnail, place, path
  (NCP/ACP/HCP), group name, date, and the number of reviewers. No infinite scroll; a short
  curated list and a "browse all" page.
- A 30-second explanation above it: what a challenge is, what the seven reviewers do, what a
  group gets. One example challenge, annotated ("this is the proof, this is the verdict").
- Actions that need an identity are offered in place ("Sign in to take this challenge"), not
  as a gate on the whole site.
- Keep the no-feed principle: this is a catalogue of published work, not a stream of
  updates, likes or comments.

**Done when.** A logged-out visitor can open three published proofs and understand the
ritual without creating an account.

## STK-02 · Explain the Google dependency at the sign-in button (P0)

**Problem.** Google sign-in is the only door, and the reason is never stated. A note about a
download that does not work is the kind of sentence that loses a user at the door: there is
no app to install, only the website. People without Google, iPhone users and
privacy-conscious organisers all stop here.

**Change.**

- Put the reason next to the button: "We use Google only to identify you; your videos stay on
  YouTube, unlisted if you prefer."
- Add email-link sign-in (Firebase, no password); Apple sign-in needs a paid developer
  account, so it stays out while the rule is free-only. If a group is YouTube-based, ask for
  the channel link later, at the moment of publishing, not at sign-up.
- A "look around first" path that preserves the visitor's place when they return.
- Remove the old download note from the blog page and say what is available today: the
  website, readable on a phone and on a desktop, with nothing to download.

**Done when.** A person without a Google account can enter with an email address, and the
sign-in screen says why YouTube is involved before the click.

## STK-03 · Turn group creation into a three-step wizard with an invite link (P0)

**Problem.** A group is the unit of work, but forming one is a form with a name, a site and a
leader, followed by an approval of unknown duration. Members have to be added by email, one
at a time, by someone who already understands the model.

**Change.**

- Three steps: **name and cause** (with a one-line purpose), **invite** (link or QR, no email
  needed), **proof of existence** (item 4). Progress is saved between steps.
- An invite link that expires in 7 days, shows "3 of 5 joined", and lets the leader approve
  joins if the group wants a gate.
- Roles: leader, member, reviewer. A leader can transfer leadership and leave; a group with
  no leader is flagged, not silently broken.
- Show the approval state with an owner and an expectation: "Waiting for a human review,
  usually under 48 h", not a spinner.
- A group profile page: name, cause, place, members (first names only), published proofs,
  contact link.

**Done when.** A new organiser can create a group, invite two people and see the pending
state explained, all from a phone, without typing an email address.

## STK-04 · Replace the domain file with a check a non-developer can pass (P0)

**Problem.** The site-first model proves a group owns its domain by placing a file at a
path. That is reasonable for a tech collective and impossible for a tenants' association, a
school club or a church group — the very groups the product wants.

**Change.**

- Offer three proofs in order of difficulty: a **DNS TXT record** (copy-paste from the
  registrar), a **meta tag** on the group's home page, or a **manual review** with a phone
  call and a public page.
- If a group has no site, let it exist unverified, with a badge and a lower publishing limit,
  rather than blocking it.
- A verification screen that detects the method automatically and says which of the three
  was found, with the exact value to copy.
- Re-verify yearly, and notify 14 days before expiry.

**Done when.** A group without a developer can pass verification with a DNS record or a
manual review, and the failure message names the value it looked for.

## STK-05 · Make the challenge form a template, not a blank page (P0)

**Problem.** "Publish a challenge" asks for a title, a path, a coin amount and a video link.
That is a form for someone who already knows what a good challenge is. New groups freeze.

**Change.**

- Six starter templates, two per path, each pre-filled with a realistic title, a one-line
  goal, a duration, a proof shot list and a suggested coin amount: water a courtyard, clear
  a drain, walk a shelter dog, carry tools upstairs, cook for a neighbour, accompany someone
  to an appointment.
- Guided fields in this order: what, where (optional, coarse), when, who films, what the
  proof must show, how many coins.
- A "what a good proof looks like" example clip or three annotated stills, per path.
- Autosave the draft, allow editing before the first taker, and show a preview exactly as a
  reviewer will see it.
- Explain the two-coin fee and when it is refunded (cancelled before a taker, or removed by
  moderation) at the point of payment.
- Safety notes per template ("do not enter private property", "do not film faces without
  consent") and a required checkbox for the risky ones.

**Done when.** A first-time group can publish a plausible challenge in under five minutes by
starting from a template.

## STK-06 · Add a real "I'll take it" handshake, with release and reminder (P0)

**Problem.** A group takes a challenge and disappears. Nobody knows whether it is coming, the
publisher cannot plan, and the two-availability lock is invisible until it is too late.

**Change.**

- **I'll take it** creates a commitment with a deadline (default 7 days) and a named contact
  in the taking group.
- A reminder to the taker 48 h before the deadline, and to the publisher when it lapses.
- **Release** with a reason ("no access", "weather", "group unavailable"), returning the
  challenge to open without penalty the first time.
- A small coordination panel: who films, when, meeting point (coarse), what to bring.
- Show availability as a sentence — "one group has taken this; a second would lock it" — not
  as a counter.
- Do not let the publisher review their own challenge, and say so on the page.

**Done when.** A taker can commit, be reminded, and release; a lapsed challenge returns to
the open list automatically.

## STK-07 · Film in the app: 60 seconds, trim, retry, consent (P0)

**Problem.** The camera is the hardest step and it lives outside the product. Users must
record, edit, upload to YouTube, set visibility, copy a link and paste it back. Every one of
those is a place to quit, and the link parser refuses channels, playlists and bare domains —
correctly, but without teaching.

**Change.**

- An in-app recorder: 60-second cap, front/back switch, pause, a shot list from the template,
  and a trim handle. Compress to 720p before upload.
- **Consent**: a face-release screen for anyone identifiable, with a stored checkbox and a
  "blur faces" option. For children, a guardian confirmation.
- Upload from the gallery as an alternative, with the same trim and consent steps.
- If YouTube is required, a single illustrated screen for "upload unlisted" with the exact
  taps, and a "paste the link" field that accepts the six sources and shows the thumbnail
  before submitting.
- Parser errors in plain language: "That is a channel, not a video. Open the video itself and
  copy its address." Never a bare "invalid".
- Save the draft locally, retry the upload, and never lose a recorded clip on a failed
  request.
- A reviewer-facing player that works without a YouTube account and without third-party
  cookies where possible.

**Done when.** A group can record, consent, upload and submit a proof without leaving the
app, and a rejected link says what to paste instead.

## STK-08 · Make the seven-review gate legible and time-boxed (P0)

**Problem.** Seven approvals is the trust mechanism, but the publisher sees no progress, the
reviewer sees no criteria, and a challenge can sit in limbo forever. Seven denials remove it
without an explanation the group can act on.

**Change.**

- Progress everywhere: "4 of 7 approvals", the deadline, and what happens at zero.
- A reviewer queue with a card per proof: the goal, the shot list, the video, and three
  yes/no criteria (safe, relevant, evidence matches the goal). Reason codes on denial, shown
  to the group.
- Time-box: 72 h to reach seven verdicts, then a fallback — extend once, or publish with a
  "partially reviewed" badge if approvals outnumber denials.
- Conflict rules enforced and explained: the publisher's group and the taker's group cannot
  review; one verdict per person per challenge.
- A published page that shows the verdict count, the date, and the names of reviewing groups
  (not individuals unless they opt in).
- An appeal after removal, with a human decision and a written reason.

**Done when.** A publisher can see the verdict count and deadline at any time, and a denied
challenge carries reason codes and an appeal link.

## STK-09 · Harden the existing admin panel (P1)

**Problem.** The admin panel exists and does its job — an allowlist can block and unblock an
account and remove a challenge or a member — but it is kept off the front page, and its
safety comes from being unlisted. Unlisted is not protected: anyone who learns the path
reaches a moderation tool, and the panel should not depend on obscurity for authentication,
on memory for its audit trail, or on goodwill for appeals.

**Change.**

- Keep the panel on its own path, but require an allowlisted Firebase account plus a second
  factor, with session expiry and a visible "you are acting as moderator" banner.
- Every action logged: who, when, what, why, and the previous state. Immutable, exportable.
- Reasons selectable from a list, shown to the affected group with an appeal button.
- Limits on blocking and removing per hour, so a compromised account is noisy rather than
  destructive.
- A moderator queue ordered by reports and age, with the evidence inline.
- A published transparency note: what is removed, how often, and how to appeal.
- Link the panel from the admin's own profile only, never from the public navigation.

**Done when.** An unauthenticated request to the panel is refused, and every removal has an
audit entry and an appeal path.

## STK-10 · Count views server-side, once, and say what points mean (P1)

**Problem.** A point is added on a page read and write, so a reload inflates it. Points are
views, not impact, and the UI does not say so. The view rule also ignores accounts younger
than two days and requires verified accounts to cross a threshold — good anti-farming, but
invisible to the group whose count stays at zero.

**Change.**

- Move the count to a Cloud Function (or an atomic transaction) with one key per account per
  challenge per window; deduplicate by account and by session.
- Show the rule in the UI: "Views count once per signed-in account; new accounts count after
  48 h." A group then understands a slow start.
- Separate the numbers: views, unique viewers, approvals, completions. Never collapse them
  into one "points" figure without a definition on screen.
- Points settle after a delay and are labelled pending → settled, with a ledger entry.
- Cap the points a single challenge can earn per day, and stop paying for views from accounts
  that never review or take anything.

**Done when.** Reloading a published proof does not change its count, and the group can read
what each number means.

## STK-11 · Publish a challenge page that can be shared and indexed (P1)

**Problem.** The only shareable object is the app root. A group that finishes a proof cannot
send a link to its funder, its neighbourhood or a search engine.

**Change.**

- A server-rendered page per published challenge: title, group, place, date, proof embed,
  verdict summary, and a call to take a similar challenge. Open Graph image generated from
  the proof thumbnail.
- A clean URL (`/c/<slug>`), a canonical, and inclusion in a sitemap.
- A "share" sheet that copies the link and a one-line caption, plus a QR for offline
  hand-outs.
- The same page works logged out, with the action buttons asking for sign-in in place.

**Done when.** Every published challenge has a public URL that renders without JavaScript,
shows its proof and verdict, and previews correctly in a chat app.

## STK-12 · Add discovery by cause and place, without a feed (P1)

**Problem.** With no feed, a new group has no way to find an open challenge or another group
like it. The catalogue exists for the visitor (item 1) but not for the participant.

**Change.**

- Browse open challenges by path, place and duration; saved filters; "near my group" using a
  coarse city, not GPS.
- A group directory by cause and place, with a contact link and published proofs; opt-in.
- "Groups like yours" suggestions based on path and language, not on a ranking of people.
- No infinite scroll, no algorithmic ranking, no engagement counters on groups. Sort by
  deadline and recency, and say so.
- A weekly email digest of three open challenges matching the group's paths (item 13).

**Done when.** A group can find three open challenges it could realistically take, without a
feed and without exposing anyone's location.

## STK-13 · Tell people what happened: review requests and verdicts (P1)

**Problem.** A reviewer is asked to act with no notification, and a group learns the verdict
only by returning to the site.

**Change.**

- Email (and optional web push) for: you are asked to review, your proof reached four of
  seven, your challenge was published, your challenge was removed with reasons, your
  challenge is about to lapse.
- A weekly digest for groups: open challenges matching your paths, one published proof worth
  reading, and the state of your own challenges.
- Quiet hours, a single unsubscribe that covers all non-transactional mail, and no
  re-engagement campaign aimed at dormant users.
- Transactional messages must still arrive if marketing is unsubscribed.

**Done when.** A reviewer can act from the email link, and a group is told the verdict
without opening the site.

## STK-14 · Keep the website fast and comfortable on desktop, readable on a phone (P1)

**Problem.** Social Tool Kit is a normal website, used on desktops: groups review proofs on a
laptop and publish from a phone. It is readable on small screens, so there is nothing to
rescue there. What is missing is the desktop layer — a review queue that uses the width, a
keyboard flow, a comfortable measure — and the old download note still suggests an app that
does not exist.

**Change.**

- A desktop layout at 1280 px and above: sidebar navigation, a two-pane review queue (list
  beside the proof), a reading column capped near 70 characters and keyboard shortcuts.
- Keep the phone layout as one readable column: 48 px targets on touch, 16 px inputs, no
  horizontal scrolling and no hover-only action.
- 48 px targets on touch, hover never the only way to reach an action, and a focus order that
  survives a window resize.
- No install prompt and no app shell: the site stays a normal browser destination. A service
  worker is optional and only for an offline draft.
- A service worker for the shell and the last viewed challenge, plus an offline draft of a
  proof submission.
- Budget: under 250 KB of JavaScript compressed for first load, thumbnails lazy, video only
  on tap, no autoplay.
- Test on a desktop browser at 1280 px and 1920 px, and on a 360 px phone with iOS Safari
  and Android Chrome; fix the keyboard covering the submit button and the back-button trap in
  the wizard.
- Deep links open the right challenge in the browser, and the share sheet is native where the
  browser has one.

**Done when.** A reviewer can work the queue at 1280 px and above without stretching a single
column, the site reads on a 360 px phone without zooming, and nothing requires an install.

## STK-15 · Consent, minors, filming and location rules in the flow (P0)

**Problem.** The product films people and places. The rules are well documented — on the
public wiki and in its in-app copy — but consent, age and location handling must be part of
the action, not a page the user is expected to have read.

**Change.**

- Face-release and guardian consent at the recorder (item 7), stored with the proof and
  revocable before publication.
- A clear minimum age, an age gate at sign-in, and a child-safety contact; no challenges that
  require filming children.
- Location at city or neighbourhood level by default; exact addresses optional and never
  public. A "private home" warning on any challenge at a residential address.
- Report and block for users and groups; a "this proof shows me and I did not consent"
  takedown path with a 24 h target.
- Data export and account deletion that also handles the group's published proofs (anonymise
  or remove, with the group told which).
- A short, human-readable privacy summary at sign-up, with the full policy one tap away.

**Done when.** A proof cannot be published without the consent record for every identifiable
person, and a takedown request has a visible path and a deadline.

## STK-16 · Accessibility and four-language parity across the app and its wiki (P1)

**Problem.** The wiki carries English, Portuguese, Spanish and French, publicly and inside the
app. That promise is only as good as the chrome around it: if the workspace, the recorder and
the review flow fall back to English — or if the RGB channels are described as colours with
no text equivalent — the four-language wiki sits behind a one-language product.

**Change.**

- All four locales in the app chrome, with the in-app wiki keeping its own switch, one
  persisted choice shared by both, and no raw key left on screen.
- Never encode meaning in colour alone: label the three channels (nature, animal, human) next
  to the colour, and give the profile a text summary.
- Captions or a transcript field for proofs; alt text for thumbnails.
- 4.5:1 contrast, visible focus, 48 px targets, reduced motion, and a form that works at 200%
  text zoom.
- Screen-reader labels on the verdict buttons ("Approve this proof", not "Yes"), and a
  progress element that announces "4 of 7".
- Plain language in errors and empty states, at roughly a B1 reading level.

**Done when.** The review flow can be completed with a screen reader, in all four languages,
without relying on colour.

## STK-17 · Reliability: idempotency, rate limits, backups, monitoring (P0)

**Problem.** Coins, points and verdicts are money-like. A double submit, a retry or a
compromised client can pay twice, and there is no described backup or alerting.

**Change.**

- One idempotency key per publish, take, approval and payout; the server rejects a replay.
- Rate limits per account and per IP on publish, review, view and invite.
- Database indexes for the queues (open challenges by deadline, reviews by challenge, views
  by account), and a nightly backup with a tested restore.
- Error tracking and uptime checks with an alert to the operator; a status line in the app
  when a dependency (YouTube, email) is down.
- A staging environment with seeded data for the seven-review path, and a migration plan for
  the twelve collections.
- A documented incident runbook: disable publishing, freeze payouts, restore, communicate.

**Done when.** A repeated publish request creates one challenge, and a restore from backup
has been performed once, on purpose.

## STK-18 · Measure time-to-first-proof, not sign-ups (P1)

**Problem.** Sign-ups flatter a product that only works when a proof is published. The
funnel has four hard steps and no instrumentation described.

**Change.**

- Events: visit, sign_in, group_start, group_verified, challenge_draft, challenge_publish,
  challenge_take, proof_submit, review_open, verdict, published.
- The funnel to watch: sign-in → group verified → first challenge → first proof → first
  published proof, with median time per step and drop-off by step.
- Quality and trust: approval rate, median review time, denial reasons, appeals, takedowns.
- Retention: second challenge within 30 days, groups active after 60 days, reviewer response
  rate.
- Authenticity: share of views from accounts older than 48 h, duplicate-view rate, payout
  corrections.

**Done when.** A weekly report answers "where does a new group stop?" and "how long does a
proof wait for seven verdicts?".

## Free-only stack and attractive additions

**Rule.** Every feature below must run on a free service, a free tier or an open-source
library. No trial that expires into a paywall, no credit card, no paid dependency in the
core loop. Organisation subscriptions may exist as revenue, but a group must never pay to
publish, review or read a proof. Quotas are documented, results cached, and every free
dependency has a fallback (self-host or degrade) if its terms change.

### Free stack

| Need | Free option | Note |
| --- | --- | --- |
| Hosting | Firebase Hosting or Cloudflare Pages free tier | static site plus functions quota |
| Auth | Firebase Authentication free tier | Google and email link only; Apple needs a paid account |
| Database | self-hosted MongoDB, or Firestore free quota | the site-first stack already runs MongoDB |
| Video | YouTube unlisted, or Vimeo free tier | embed, never re-host |
| Maps | MapLibre GL JS with OpenStreetMap tiles | neighbourhood level only; cache tiles |
| Captions | Web Speech API, or Whisper.cpp self-hosted | editable transcript, stored with the proof |
| Translation | LibreTranslate self-hosted | cache translations; no per-word API |
| Email | Brevo or Resend free tier | transactional first; check the daily limit |
| PDF | browser print stylesheet, or jsPDF (MIT) | generated in the browser |
| QR | qrcode (MIT) | rotating identity codes, generated locally |
| Analytics | Umami or Plausible CE, self-hosted | no third-party cookies |
| On-device AI | Transformers.js, MediaPipe or TensorFlow.js | relevance and safety hints, no paid API |
| Errors | GlitchTip self-hosted, or Sentry free tier | scrub personal data |

### Attractive additions that stay free

| Feature | What it adds | Free stack | Effort |
| --- | --- | --- | --- |
| Challenge of the week | One human-curated challenge on the home page, not a feed | editorial + static JSON | S |
| Proof story card | A shareable image with the proof thumbnail, place and verdict | Canvas | S |
| Auto-captions | A transcript under every proof, editable before publishing | Web Speech API or Whisper.cpp | M |
| On-device relevance hint | Flags a clip that does not match the goal; a human decides | Transformers.js | L |
| Proof map | Published proofs at neighbourhood level | MapLibre + OSM | M |
| Group badges | Recognition for a first proof, a series, a long project | SVG/CSS, no ranking | S |
| Template gallery | Six worked examples per cause, with shot lists | static JSON | S |
| Calendar and digest | An ICS feed plus a weekly email of three open challenges | ICS + free email tier | S |
| Embeddable proof | A widget a group puts on its own site | iframe | M |
| QR witness tag | A tag at the place of work, scanned when filming | qrcode + rotating token | M |

## New feature possibilities

These are additions beyond the P0 work. **Fit**: **Core** makes the existing ritual work
better; **Adjacent** adds a surface with the same promise; **Product change** needs a
decision because it alters what the product is; **Reject** is recorded so it stays closed.
Effort is S/M/L for one person.

### Challenge formats

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Recurring series | A weekly watering or walking slot a group can own | Core | M |
| Multi-week projects | Milestones, a mid-point proof and a final proof | Adjacent | L |
| Challenge packs | Six ready challenges per cause and season | Core | S |
| Micro-challenges | Something finishable in five minutes | Adjacent | S |
| Adopt a cause | A group commits to one place for three months | Adjacent | M |
| Joint proofs | Two groups take one challenge and split the work | Core | M |
| Urgent requests | A same-day need, fast-tracked | Reject | — |

### Proof and review

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Proof checklist | The template's shot list becomes tickable at upload | Core | M |
| Before/after frames | Two required frames for fixes and clean-ups | Core | S |
| Blind review | Reviewer sees the proof, not the group's name | Core | S |
| Reviewer pools | Match proofs to reviewers by cause and language | Core | M |
| Reviewer reputation | Jury duty and weight, never a public ranking | Adjacent | M |
| AI pre-screen | Flags unsafe or irrelevant clips; a human still decides | Adjacent | L |
| Captions and translation | Auto-captions, translated summary, editable | Adjacent | M |
| Verdict summary | "Why this passed" in three lines, written by reviewers | Core | S |
| Witness co-sign | Someone present confirms the filming took place | Adjacent | M |
| Place and time attestation | Stronger proof without storing a movement trail | Product change | L |

### Groups and institutions

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Group profile | Cause, place, members (first names), published proofs | Core | S |
| Chapters | One group, several local branches, shared identity | Adjacent | M |
| Group analytics | Views, approvals, completion time, retention | Core | M |
| Funder report | A PDF with proofs, verdicts, dates and reach | Core | M |
| Organisation accounts | SSO, roles, several groups under one roof | Product change | L |
| Mentorship pairing | A new group paired with an experienced one | Adjacent | M |
| Group partnerships | Two groups co-sign a long project | Core | M |
| Task thread | A group-only thread for coordination, not a DM inbox | Core | M |
| Group directory | Opt-in list by cause and place | Adjacent | M |

### Discovery and data

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Cause and city pages | Indexable pages: "animal care in Porto" | Core | M |
| Search and tags | Find a proof or a challenge by what it is | Adjacent | S |
| Embeddable proof | A widget a group can put on its own site | Adjacent | M |
| Read-only public API | Aggregate published proofs for research | Adjacent | M |
| City proof map | Published proofs at neighbourhood level, never exact homes | Adjacent | M |
| Weekly digest | Three curated proofs and open challenges, not a feed | Adjacent | S |

### Identity, safety and access

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Email link and passkeys | Beyond Google, without a paid developer account | Core | M |
| Youth accounts | Guardian consent and a restricted path | Product change | L |
| Rotating QR | A new code per context, revocable, with consent per share | Core | S |
| Face blur | On-device blur before upload | Core | M |
| Takedown portal | "This proof shows me and I did not consent" | Core | S |
| Transparency report | Removals, appeals, response times | Core | S |
| Offline drafts | Record and submit when the connection returns | Core | M |
| Low-data mode | Audio-first proof and thumbnails only | Adjacent | M |
| Deep links | Open the exact challenge from a shared link | Adjacent | S |

### Sustainability

| Feature | What it adds | Fit | Effort |
| --- | --- | --- | --- |
| Grants and donations | Money to run the service, not to pay users | Adjacent | S |
| Organisation subscriptions | Paid dashboards for NGOs and councils | Product change | M |
| Sponsored challenge pool | A funder pays for ten challenges, clearly labelled | Product change | M |
| No advertising | Proofs stay ad-free; sponsorship is editorial and labelled | Core | — |

### Five bets worth prototyping

1. **Blind review.** Hiding the group's name from reviewers is cheap and tests whether the
   verdict is about the proof or about the group. Test: 20 proofs reviewed both ways; compare
   approval rates and reviewer comments.
2. **AI pre-screen plus captions.** The two features that remove the most reviewer work
   without taking the decision away from people. Test: measure review time and false flags on
   50 proofs, with a human deciding every case.
3. **The funder PDF.** A group that can hand its funder a dated, reviewed proof will keep
   publishing. Test: five groups export it; ask whether it was used in a report.
4. **The group task thread.** Coordination currently happens off-platform, and that is where
   challenges die. Test: three groups coordinate one challenge entirely in the thread.
5. **QR/NFC witness tags.** A tag at the place of work, scanned at filming, proves presence
   without tracking anyone. Test: five tags, ten proofs, one attempted replay.

### Reject, with the reason

- **Urgent or emergency requests** — the product cannot verify a crisis, and a late verdict
  on a real emergency is worse than no feature.
- **Public ranking of people or groups by points** — turns care into a competition and invites
  farming; recognition by proof, not by score.
- **Auto-publish when the deadline passes** — destroys the seven-outsider promise.
- **A public map of exact proof locations** — exposes homes and shelters; neighbourhood level
  at most.
- **Advertising inside proofs** — the no-money stand is the reason groups trust the space.
- **AI deciding a verdict** — screening is assistance; the seven humans remain the gate.

## What not to build

- No feed, follower graph, likes, comments or direct messages. That is the product's stand,
  and it would swamp moderation.
- No money, cash-out, trading or paid promotion of a challenge.
- No public ranking of individuals; groups may be listed, people may not.
- No exact home addresses, no live location, no map of users.
- No auto-publish on timeout without a visible badge; trust is the whole product.
- No growth loop that asks a group to invite contacts before it has published anything.

## First two weeks, in order

1. Public catalogue of published proofs, logged out (item 1).
2. Group wizard with invite link and a verification a non-developer can pass (items 3–4).
3. Challenge templates, the take/release handshake, and the review progress view (items 5–6,
   8).
4. Authenticated moderation with an audit log and appeals (item 9).
5. Consent at the recorder and the takedown path (items 7, 15).
6. Server-side view counting and the points definition (item 10).
7. Desktop review layout; phone readability check (item 14).
8. Idempotency, rate limits, a backup restore, and the funnel dashboard (items 17–18).

## Assumptions to verify in the app

- Whether a logged-out visitor can see any published proof today.
- Whether the site-first code and domain file are live or still a model.
- Whether the seven-verdict count is enforced by the app and whether progress is shown.
- Whether coins and points are written atomically, and what a reload does to a view count.
- Whether the site reads at 360 px today, how it behaves on iOS Safari, and whether the
  review queue uses a desktop width.
- Whether the existing admin panel enforces authentication beyond its allowlist, and whether
  it logs every action with a reason.
- Whether the in-app wiki exposes all four languages, and whether the workspace around it is
  translated too.
