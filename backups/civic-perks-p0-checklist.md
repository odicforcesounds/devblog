# Civic Perks — P0 implementation checklist

Internal working note for the author. Not published, not linked from `docs/`.
Companion to `backups/civic-perks-usability.md`; this file only covers the P0 items and the
shared work they depend on. The app's source is not in this repository, so tasks are named by
screen and behaviour rather than by file path; map them to the real components when you open
the app repo.

**Scope of this pass.** A stranger opens the site, understands it, and publishes or confirms
a pin without an account wall; the map looks alive; the rules are legible; moderation and
privacy basics exist.

## 0. Decisions to lock before coding

- [ ] Confirmation radius (suggested 150 m, or 250 m outside dense areas) and whether accuracy
      counts toward it.
- [ ] Daily pin cap stays 20; the counter resets at local midnight.
- [ ] Vanguard threshold stays 3 distinct scouts in the area; define "area" (city, or a
      1 km grid) and store it.
- [ ] Seed content is labelled and ages out after 90 days without re-confirmation.
- [ ] Guest pins are allowed and merge on sign-in; the account remains optional for reading.
- [ ] Address fuzzing distance (suggested 30 m, snapped to a 50 m grid).
- [ ] Minimum age 16, with a self-declared gate and a removal contact.

## 1. Visitor map

- [ ] **Auth gate removed from the map route.** Firestore reads for pins and public reports
      allowed to unauthenticated clients, or served through a read-only endpoint with a
      cache. Writes remain authenticated.
- [ ] **Visitor state in the UI.** No modal on load; an inline strip with "Sign in to pin,
      confirm and keep your XP" and a dismiss that persists for the session.
- [ ] **Read-only pin sheet.** Photo, category, status, age, distance if location is granted.
      Confirm and report buttons become "Sign in to confirm" and keep the pin open after
      sign-in.
- [ ] **Last activity line.** "Last confirmed 2 h ago in Bonfim", computed from public data,
      with a fallback when the city has none.
- [ ] **Guest scout.** Anonymous local identity (UUID in localStorage) holds drafts and a
      pending-pin count; on sign-in, offer "Attach 3 pins to your account" and merge.
- [ ] **Feature flag** (`visitor_map`) so this can be disabled without a redeploy.

**Acceptance:** logged out, on a 360 px phone, a visitor can pan, zoom, open a pin, read its
photo and see recent activity. No write request is made. Sign-in returns them to the same pin.

## 2. Location permission

- [ ] **Pre-permission sheet** on the first action that needs position: what is read, what is
      never shared, why. Buttons: "Use my location" / "Not now".
- [ ] **No geolocation call on page load.** The map opens at the last city or the geo-IP city.
- [ ] **Denied state.** Banner with the exact re-enable path for Android Chrome and iOS Safari,
      dismissible, and a "Place the pin myself" action.
- [ ] **Tap-to-place fallback.** Draggable pin, address search, and a badge:
      "unverified by distance" (reduced XP, still publishes).
- [ ] **Accuracy display.** A circle with radius in metres; if accuracy is worse than 100 m,
      warn before publishing rather than blocking.
- [ ] **Moving warning.** If speed suggests driving or cycling, pause the primary action and
      show the safety line.

**Acceptance:** with location denied, a pin can still be created by tapping the map. With it
granted, the prompt appears only after the explanation.

## 3. Pin creation

- [ ] **+ Pin button** fixed above the bottom edge, 56 px, thumb reach, one per screen.
- [ ] **Camera-first screen.** Capture, retake, use gallery. No form before the photo.
- [ ] **Compression** to ~1600 px long edge, JPEG quality ~0.8, before upload; show the final
      size.
- [ ] **Three category chips** (fix / protect / needs help), icons plus one line each.
- [ ] **Location confirmation.** Pre-filled position, draggable pin, "Use my position".
- [ ] **Optional note** behind a disclosure: 140 chars, dictation button, counter.
- [ ] **Publish** as the only primary button; cancel keeps a draft.
- [ ] **Upload state** as a thumbnail with a progress ring; the map stays usable.
- [ ] **Private-property/road warning** shown once at the pin step, not as a blocking modal.
- [ ] **Draft store** in IndexedDB: photo blob, coords, accuracy, category, note, createdAt,
      guest id.
- [ ] **First-pin celebration** that does not cover the map: XP tick plus one sentence.

**Acceptance:** with location granted, a photo pin is published in three taps and under 20
seconds on a mid-range Android; cancelling and reloading restores the draft.

## 4. Duplicate → confirmation

- [ ] **Query** pins within 25 m, same category, status not fixed, at the confirm step.
- [ ] **Inline offer:** "Someone already reported this — confirm it instead", with the
      existing photo and age.
- [ ] **Confirm path** uses the existing pin and pays confirmation XP, not creation XP.
- [ ] **Create anyway** links `duplicateOf` and flags for moderation; zone totals count it
      once.
- [ ] **Merge action** in moderation preserves both photos and credits both reporters.

**Acceptance:** a second report within 25 m offers confirmation first; the merged pin shows
both photos and both credits.

## 5. Confirmation

- [ ] **Bottom sheet** with photo, category, status, age, distance and accuracy.
- [ ] **Primary: "I can see it"**, secondary "It's gone" / "Not sure".
- [ ] **Distance gate** with a plain sentence when too far; never a silent failure.
- [ ] **One verdict per account per pin**, idempotent write keyed by `pinId + uid`.
- [ ] **14-day "still there?"** prompt before the pin counts again.
- [ ] **Confirmation available** from the pin sheet, the list view and a notification link.
- [ ] **Feedback:** XP tick and "Confirmed. A neighbour's report now counts." No modal.

**Acceptance:** one tap confirms from the sheet; a second attempt from the same account is
rejected with a readable message; a too-far attempt explains the radius.

## 6. Seed pack and empty state

- [ ] **Import tool** for 30–50 pins per city: photo, category, coordinates, note, date,
      attribution "Civic Perks team".
- [ ] **Visual distinction** for team pins, and a 90-day ageing rule.
- [ ] **Zero-pin street:** "This street has no pins yet. Adopt it for a week" with a five-pin
      quest on the same street.
- [ ] **Vanguard progress line:** "3 scouts unlock validation here — 1 so far."
- [ ] **No invented activity.** No fake online counts, no fake confirmations.

**Acceptance:** a fresh city shows at least 30 team pins; a street with none offers the quest.

## 7. Plain-language rules in the UI

- [ ] **Pin timeline:** Reported → Confirmed → Fixed, with who and when.
- [ ] **Flag text** on the new pin: "We accept it now. A neighbour's confirmation removes the
      'new' mark."
- [ ] **Cap counter:** "18 of 20 pins left today", reset time in local time.
- [ ] **Vanguard copy:** what still works first, then what waits.
- [ ] **Four locales** wired to the same keys; no hard-coded English in toasts.
- [ ] **Link** from each explanation to the full rules page, opening in a new tab.

**Acceptance:** a first-time user can explain, without the wiki, what happens after Send and
why credits are flat in Vanguard.

## 8. Moderation and privacy basics

- [ ] **Report pin** and **report user**: reason codes (false, duplicate, unsafe, private
      property, offensive), optional note, confirmation that a human reviews.
- [ ] **Block user**: hides their pins locally immediately and records the block.
- [ ] **Address fuzzing** within 30 m of a residential address; snap to street/grid; tell the
      reporter.
- [ ] **No live position** exposed; presence heartbeat aggregated only.
- [ ] **Moderator queue**: merge, remove, restore, with an audit entry (who, when, why).
- [ ] **Appeal** path with a response target.
- [ ] **Safety interstitial** on the first pin and in the map's about sheet; emergency
      disclaimer visible.
- [ ] **Age gate** consistent with 16+; child-data removal contact.
- [ ] **Data rights**: export JSON, delete account and local data, withdraw ad consent.

**Acceptance:** a pin and a user can be reported and blocked in-app; a moderator action has an
audit entry; a home-address pin is fuzzed by default.

## 9. Shared foundations this pass needs

- [ ] **Auth:** Firebase Google stays; add email link if it can ship this week. Apple is out
      under the free-only rule.
- [ ] **Rules:** Firestore rules tested for unauthenticated reads of published pins only, and
      authenticated writes with shape validation.
- [ ] **Functions:** `createPin`, `confirmPin`, `mergeDuplicate`, `reportContent` — each
      idempotent with a client-supplied key.
- [ ] **Analytics:** map_view, pin_start, pin_published, confirm_attempt, confirm_success,
      sign_in, report, boost_open — no coordinates, no email.
- [ ] **PWA:** manifest, icons, service worker shell, install prompt after the first
      confirmation.
- [ ] **Budget:** first load under 200 KB JS compressed; AppLixir loaded only from the boost
      shop.

## 10. Phone test script (run before shipping)

- [ ] Android Chrome, 360 px, mid-range device, location granted: publish a pin in under 20 s.
- [ ] Same device, location denied: place a pin by tapping, see the unverified badge.
- [ ] Airplane mode: create a pin, reload, see it pending, go online, see it publish.
- [ ] Second account within 25 m: offered confirmation, not a new pin.
- [ ] Two accounts confirm the same pin: count is 2, no duplicate XP.
- [ ] Screen reader on: open a pin, confirm it, hear the result.
- [ ] 200% text zoom: primary buttons remain visible and tappable.
- [ ] iOS Safari: pre-permission sheet, denied banner, install prompt, safe-area padding.
- [ ] Logged out: map, pin sheet, last activity, sign-in strip; no write requests in the
      network panel.

## 11. Out of scope for this pass

List view, filters, offline tile cache, account switching, push notifications, leaderboard
privacy, and the economy audit are P1/P2 in the main guide. Do not let them delay items 1–7.
