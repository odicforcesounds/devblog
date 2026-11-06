---
name: stk-development
description: The contract for moving Social Tool Kit — the private stk folder — from an Android application to a Facebook application: where each of its five code bases sits, what runs on this host, how identity and the video source change, the defects that block a public URL, and how every step is recorded on docs/socialToolKit.html. Use when building, planning, fixing or reviewing anything in the STK project.
---

# Social Tool Kit — from Android to a Facebook application

**Run these checks and builds only when the author asks.** The page audits named at the end
are not part of every task: finish the edit, say which check would prove it, and run it when
it is requested.

**The folder is private.** `stk/` is its own repository, ignored by this one, and
nothing in it is published from here. Read it freely; change a file inside it only when the
request names that file, and never copy its contents — keys, documents, source — into
`docs/`. What this repository holds about it is the log page, and nothing else.

## The record is the page

`docs/socialToolKit.html` is the only account of this work: a **Setup** fold (what to install
on this host), **Step 1** (what the project is), **Step 2** (the move to Facebook, 2.1–2.13),
**Step 7** (the backend that runs the challenge domain, 7.1–7.8).
Every step taken is a row in the log table of 1.10, numbered onwards from the last; every
decision carries its own numbered section; every outside fact it relies on is a link in a
sources section, checked to answer 200 before it is written down. A change to the folder, a
decision taken with the author or a check that fails becomes a row and, when it needs more
than a sentence, a section.

## Where the pieces are

| Path | What it is | Stack |
| --- | --- | --- |
| `stk/MobileCode/Challenge` | The Android client | React Native 0.80.1, React 19, 30 routes, 17 native modules |
| `stk/MobileCode/UI_Change_Testing` | A second copy of the same app, same package name | Same |
| `stk/BackendCode` | The API | Express 5, Mongoose 8, 92 routes, 17 models, JWT, multer |
| `stk/Frontend` | The public web site | Vite 7, React 18.3, Ant Design 5; three routes |
| `stk/AdminPanel` | The admin dashboard | Same stack; users, organizations, feeds |
| `stk/Database/dump.zip` | A `mongodump` archive | Database `challenge`, 12 collections |
| `stk/FacebookCode` | The Facebook surface and the challenge domain | Express 5, a static client, 14 video routes plus the challenge API, file or Mongo store |

`FacebookCode` is the only folder that speaks to the Graph API; it is where this skill's work
happens. `SETUP.md` in it is the console guide, and `README.md` its route table.

## The Facebook surface

```sh
cd stk/FacebookCode
npm install
cp .env.example .env        # FB_APP_ID, FB_APP_SECRET, SESSION_SECRET, TOKEN_KEY
npm start                   # http://localhost:3000, /healthz answers JSON
STORE=file npm start        # writes data/db.json, no database needed
```

Its rules, which a change must not break: the app secret never reaches the browser; Page and
user tokens are AES-256-GCM under `TOKEN_KEY`; a pasted link must be a Facebook video, reel
or watch id (`normalizeVideo`); the player is the embedded iframe, never a copied file; every
unsafe request carries an `Origin` that matches `PUBLIC_BASE_URL`; `POST /data-deletion`
verifies `signed_request` before deleting anything.

`Frontend` and `AdminPanel` are the same application under two names. The public one is the
only place a browser client can grow from; the admin one stays admin.

## The challenge domain (Step 7)

Step 7 is the narrative and `FacebookCode/README.md` the route table. The code is five
modules beside the video surface, and nothing from `BackendCode` was copied:

| Path | Holds |
| --- | --- |
| `src/domain/rules.js` | the constants and identity helpers: `PATHS`, `APPROVALS` 7, `MEMBER_VIEW_CAP` 20, daily caps, `normalizePath`, `normalizeEmail`, `memberKey`, `memberMatches`, `isMember`, `requiredMembers` |
| `src/domain/ledger.js` | `award` (unique key, optional daily cap, never negative) and `balance` by user id or email |
| `src/domain/service.js` | every rule: group registration, approval, claim, quorum, proof, independent review, publication, payout, view counting, leaderboard, wallet |
| `src/domain/router.js` | the HTTP layer, the session reader, the Page ownership check, the development login |
| `src/page.js` | the reporter: a Graph post when `FB_PAGE_ID` and `FB_PAGE_TOKEN` exist, a stored line otherwise |
| `src/store/file.js`, `src/store/mongo.js` | the same namespaces in both drivers: `groups`, `challenges`, `views`, `ledger`, `pagePosts`, plus `users.bumpReviews` |

### The shapes

```js
group     { id, name, email, site, status: 'pending'|'approved'|'denied',
            account: { facebookId, verified },
            page: { id, name, verified, verification: 'graph'|'dev' } | null,
            members: [{ userId?, email, name, role: 'leader'|'member' }],
            treasury, createdBy }
challenge { id, kind: 'challenge'|'action', title, path: 'NCP'|'ACP'|'HCP',
            link, embed, goal, coins,
            phase: 'open'|'assigned'|'locked'|'proof'|'published' (an action: 'fun'),
            authorId, groupId, videoSelected, available: [memberKey],
            proofs: [{ id, userId, link, note, status, reviews: [{ userId, decision, at }] }],
            pointsAtPublish }
view      { challengeId, userId, member, counted }      one row per account and challenge
ledger    { key (unique), userId?, email?, groupId?, amount, reason, refId }
pagePost  { text, delivered, at }
```

### The phase machine

| Phase | Reached by | Server rule |
| --- | --- | --- |
| `open` | `POST /api/challenges` | path in NCP/ACP/HCP, a Facebook video link, a goal of five characters, coins 5–200 |
| `assigned` | `POST /api/challenges/:id/take` | approved group, caller is a member, challenge still open |
| `locked` | `POST /api/challenges/:id/availability` | `available.length >= requiredMembers(group)`, where required is `ceil(members / 2)` |
| `proof` | `POST /api/challenges/:id/proofs` | only from `locked`, only a member, the same link rule as a video |
| `published` | the seventh approval on a proof | points copied into `pointsAtPublish`, payout once, Page line |

A rejection returns the proof to the group (`phase: 'locked'`) and pays nothing. Views are
accepted from `open` to `proof`; after publication they answer `409`.

### The rules and the code that enforces them

| Rule | Where |
| --- | --- |
| A group needs a Facebook session | `createGroup` refuses without an actor; the router answers `401` |
| The named Page must be administered by that account | `verifyPage`: decrypt the stored user token, read `/me/accounts`, match the id; otherwise `403`; no app credentials means `503` |
| Registration waits for a person | `reviewGroup` requires an address in `ADMIN_EMAILS`; approving twice leaves one Page post |
| One view per account | a unique `(challengeId, userId)` index in Mongo, a lookup in the file store; a repeat returns `already: true` |
| The group's own audience stops at 20 | the view row carries `member`; past the cap it is stored `counted: false`, so the watch is kept and the point is not |
| Points freeze at publication | `pointsAtPublish` is written with the seventh approval |
| Seven independent approvals | the publisher and every group member are refused before a review is stored |
| One coin, one award | the ledger key `challenge:<id>`, `bonus:<id>`, `payout:<id>:<member>`, `review:<proof>:<user>:<n>`; a duplicate key returns the existing row |
| Three publishes and ten reviews a day | `store.ledger.countToday(userId, reason)` before the award |
| Seven tenths to the available members | `Math.floor(coins * 0.7 / available.length)` each, the remainder added to `group.treasury` |
| The Page reports each step | approval, claim, lock, proof, the 200-point milestone, publication; a Graph failure is logged and the line is stored with `delivered: false` |

### Code patterns to keep

- **Throw a status, answer a sentence.** `fail(status, message)` attaches `status`; the server's
error handler returns `{ error }`. `wrap` is required around every async handler in Express 5.
- **Derive, never increment.** Views, points, member counts and quorums are queries over events.
The only stored totals are `treasury` and `pointsAtPublish`, both written once.
- **Identity is the user id or the email.** `memberKey` is `userId || email`, and
`memberMatches` accepts either. An invited email can later sign in and act as that member,
and a payout row stored with `email` is counted by `ledger.balance({ userId, email })`.
- **The ledger is the only place a coin changes hands.** No route writes a balance. Awards carry
a reason, a reference and a key, so a retry cannot pay twice.
- **Money is integers.** Round shares down and give the remainder to the treasury; 25 coins with
two available members pays 8, 8 and 9, never 8.75.
- **A repeated action must be a no-op.** Approving an approved group, toggling availability and
re-submitting a proof each return the current state and write nothing new.
- **Devices of convenience stay behind a flag.** `ALLOW_DEV_LOGIN=1` opens `/auth/dev` and the
view seeder; both answer `404` otherwise. Never leave it on a public host.
- **The store contract is the namespace, not the driver.** Add a method to both `file.js` and
`mongo.js` in the same shape; business rules belong in `service.js`, not in a route or a model.
- **A Page post never fails the request.** `report()` catches its own errors; the challenge
state is already committed.

### Group validation: inside the application, not a second platform

Registration is validated in three steps, all in this app: the signed Facebook session names
the account, the named Page must appear in that account's `/me/accounts` answer, and an address
in `ADMIN_EMAILS` approves the group. A separate website is only needed if the leaderboard must
be readable without a Facebook login, and even then it can be one public route on this server.

### Running and testing the domain

```sh
cd stk/FacebookCode
PORT=3230 DATA_DIR=/tmp/stk-run PUBLIC_BASE_URL=http://127.0.0.1:3230 \
SESSION_SECRET=test TOKEN_KEY=test ALLOW_DEV_LOGIN=1 ADMIN_EMAILS=admin@test.local \
STORE=file node server.js
```

A cookie-keeping client in Node (`fetch`, copy the `set-cookie` header) drives `/auth/dev`
for thirteen accounts, then the whole lifecycle: two group members, one challenge, a claim, two
availabilities, seeded views, a proof, six approvals, the seventh, the wallet, the treasury,
the leaderboard and the member cap. The reference run has 75 checks and all pass; the scratch
files live in `/tmp`, never in the folder. Stop the server when done and check its log for
uncaught errors.

What the local run cannot prove: real `/me/accounts`, a real Page post, App Review for
`pages_manage_posts`, and `STORE=mongo` on a live database (the Mongo driver is import-checked
only). Say so instead of claiming a pass.

## What runs on this host

```sh
cd stk/BackendCode && node server.js      # :5001, needs MONGO_URI and JWT_SECRET
cd stk/Frontend  && npm run dev          # Vite
cd stk/AdminPanel && npm run dev -- --port 5000
cd stk/MobileCode/Challenge && yarn start   # Metro; needs the watcher limit
```

The database, the JDK, the SDK and the watcher limit are installed by the page's Setup fold;
do not repeat those commands in a new document, link the section instead.

## The target: a Facebook application

- **No Android application is required.** The Facebook application is an app record — id,
  secret, permissions, redirect URI, privacy policy — pointing at a web product. Meta
  reviews the product at its URL and a screencast of the login and the permission use; an
  APK never enters the review.
- **What it does require:** an HTTPS origin with no path rewrite in front of the API, a
  privacy policy at a stable URL, a data deletion callback that answers Meta's signed
  request with a confirmation code and a status URL, an app icon, a category, App Review
  for every permission beyond the default profile read, and Business Verification for
  advanced access.
- **The product is the browser client**, not the phone. The phone may keep running against
  the same API or stop; neither changes the app record.

## The order of work

1. **Identity.** Facebook Login on the web; a server route that exchanges the code for a
   token, asks the Graph API who the person is, stores `facebookId` on the user and signs
   the JWT the API already understands. The client never states who it is.
2. **A client.** Grow the public Vite app into feed, challenge, upload, rate, profile,
   notifications. Do not move the admin screens into it.
3. **The video source.** A Page replaces the channel; keep the old YouTube fields readable
   so existing challenges still render.
4. **Media in a browser.** File input, `video`, the camera for the QR scan; the multer route
   stays but needs a public base URL, a static handler and a size limit.
5. **Notifications, later.** The notification collections already carry what an in-app badge
   needs; Web Push waits.
6. **The review kit.** Privacy policy, terms, deletion callback, icon, category, screencast.
7. **The repairs a public URL makes urgent** — the gate below.
8. **A named first cut.** Login, feed read-only, one challenge page, one upload. No push, no
   scan, no native rebuild.

## Identity contract

- The permission asked at login is `public_profile` plus `email`; anything about the
  person's Page or content is asked at the moment they connect it, because a permission
  unused for ninety days must be granted again.
- The server verifies the token; it never trusts a client-sent id, email or Firebase token.
  The login that exists today finds a user by email and signs a JWT, and the
  `verifyIdToken` version is commented out — that is the defect this item repairs, not a
  pattern to copy.
- One user model serves both clients: `facebookId` is added beside `firebaseUid`, and the
  JWT stays the session token so every existing route keeps working unchanged.

## The video source

A Page is the public surface, not a person.

| Today | On Facebook |
| --- | --- |
| `youtubeChannelId`, `youtubeApiKey` | `facebookPageId` and a page token, server side only |
| `channels.list` | `GET /{page-id}?fields=name,picture,link` |
| `playlistItems` | `GET /{page-id}/videos?fields=title,description,created_time,permalink_url,length` |
| View counts copied once | Video insights, refreshed |
| YouTube iframe | A `video` element or the embedded player |
| `/api/connect-youtube` | `/api/connect-facebook` |

Permissions: `pages_show_list`, `pages_read_engagement` to read; `pages_manage_posts` and
`publish_video` only if the product publishes. Nothing is readable from a personal timeline.

## The gate before a public URL

Each line names the proof; a launch that skips one is a launch of something else.

| Check | Proof |
| --- | --- |
| The API can install from its own manifest | `cd stk/BackendCode && npm ls jsonwebtoken` — it is required and undeclared |
| The API reads the database the dump creates | one `MONGO_URI` line; `mongosh --eval 'db.getCollectionNames()'` |
| Uploaded images resolve | a static handler exists and the URL is not built from `MONGO_URI` |
| Points are earned, not declared | the donation route ignores a client `amount` and `transactionId` |
| Admin routes are guarded | `isAdmin` on every `/users` route that mutates |
| CORS is one origin | not `cors()` with no options |
| No key ships in a client | no `MAP_KEY`, no `YOUTUBE_API_KEY` compiled into a bundle |
| Login proves the caller | a token verified server side, not an email lookup |

## Recording a step on the page

- One `<details class="step">` per numbered step, inside the outer fold, closed by default;
  a `<nav class="toc">` at the top of the fold lists every step and every anchor it points at
  must exist.
- Continue the numbering (`2.1`, `2.2`, …); never renumber a step someone may have linked.
- Append to the log table of 1.10 rather than rewriting it, and keep one row per action with
  a result, not an intention.
- Verify every external link answers 200 before writing it; a documentation page that moved
  is replaced, not left as a dead anchor.
- No HTML comment about the task, no sentence addressed to the author, no duplicated
  paragraph: the page is read by someone who was not in the room.

## Verify

```sh
python3 .agents/skills/blog-ops/page_hygiene.py docs/socialToolKit.html
python3 .agents/skills/a11y/check_a11y.py --page socialToolKit.html
python3 .agents/skills/security-headers/check_headers.py --page socialToolKit.html
python3 .agents/skills/link-integrity/check_links.py docs/socialToolKit.html
python3 .agents/skills/page-weight/check_weight.py
```

`node --check stk/BackendCode/server.js` proves the entry point still parses; it
does not prove the API runs, because the database and the environment decide that. The
domain's own lifecycle is proved by the 75-check run above, not by opening the page.

The API's write routes reject a mismatched `Origin`; a request without one (curl, a server
job) passes, so a browser test must send the same origin as `PUBLIC_BASE_URL`.

## Rules

- **The API stays authoritative.** Do not follow the meeting notes into a second database;
  Firebase is identity and push, if it stays at all.
- **Never grant points from a request body.** Every balance change has a server-side reason,
a unique ledger key and, where the page promises one, a daily cap.
- **The challenge API is not the old API.** Do not copy a route or a masked prefix from
`BackendCode`; the domain's paths are plain `/api/…` and its identity is the Facebook session.
- **A phase change is a server decision.** The client asks; the server checks the phase, the
membership and the quorum, and answers with the new state or the reason it refused.
- **No new dependency without saying so**, in the log row, with the reason it was needed.
- **Report a defect on the way, do not repair it on the way.** The page's findings section is
  where it goes, with the file it lives in.
- **No tool attribution in a commit**, one file per commit, through
  `.agents/skills/blog-ops/commitit.sh`, and no push without being asked.
- **Nothing is committed until the author asks.**
