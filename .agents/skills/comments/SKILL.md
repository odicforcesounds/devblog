---
name: comments
description: The one Firebase project behind the comment form and the session-only chat — which pages carry the config, which collection is written, what the security rules allow, what a reader is promised about privacy, and the checks that keep the copies from drifting. Use when touching a comment form, the chat page, the provider buttons or backups/firebase-rules.txt.
---

# Comments and the secret chat

Two pages talk to one Firebase project, `blog-comments-6b4f5`:

| Page | What it does | Where the state lives |
| --- | --- | --- |
| `index.html` | comment form and thread, Google and email sign-in | Firestore collection `comments` |
| `secretChat.html` | sign-in with Google, then a chat, `noindex` | the session of the people signed in; nothing kept on the device |

The config block (`apiKey`, `authDomain`, `projectId`, `storageBucket`,
`messagingSenderId`, `appId`) is **copied into each page**, because the pages are static
and there is no build step for them. Copies drift, and a drifted copy fails silently: the
form still renders, the write goes to a project nobody reads.

## What the checker holds together

| Check | Level |
| --- | --- |
| every page's `firebaseConfig` matches the others, field by field | failure |
| every collection the code writes is named in `backups/firebase-rules.txt` | failure |
| the chat page keeps nothing in `localStorage` | failure |
| a page using `localStorage` at all | warning |
| `backups/firebase-rules.txt` exists | warning |

```sh
python3 .agents/skills/comments/check_firebase.py          # the pages agree
python3 .agents/skills/comments/check_firebase.py --json
```

Exit code 0 when the pages agree, 1 when they do not. Read-only.

## What the reader is promised

- **Reads are public, writes are signed.** Anyone may read a thread; only a signed-in
  person may post, and a post carries the name and avatar of that account.
- **The chat is temporary.** Nobody's history is stored: what a signed-in person sees is
  what the others still signed in are holding. Sign out and it is gone; sign in again and
  there is nothing to return to.
- **Avatars come from the provider only.** `AVATAR_HOSTS` in `index.html` lists five
  provider hosts; any other URL is refused, because a comment field is written by its
  author and an open `<img src>` would let anyone plant a tracking pixel in a thread
  everyone reads.
- **`secretChat.html` is `noindex`.** It is also, today, listed in `sitemap.xml` and in
  `docs/api/index.json` — a contradiction the `seo-indexation` skill reports. One of the
  two promises has to go.

## What it found the first time

- Two pages carry the config — `index.html` and `secretChat.html` — and both name the same
  project, `blog-comments-6b4f5`. They agree field by field, so no write is going
  somewhere unwatched.
- **One failure: the chat writes a collection `chat` that `backups/firebase-rules.txt`
  never names.** Either the rules do not cover the chat at all — in which case every send
  is refused by default — or they cover it under another name and the file is out of date.
  Neither is safe to leave: the chat is the one feature whose promise is that nothing
  persists.
- Six pages use `localStorage` for their own state (`index.html`, `mapQuest.html`,
  `gameReference.html`, `awesome_story.html`, `reactNative.html`, `androidStudio.html`).
  None of them is the chat, so the session-only promise holds.

## Rules

- **Never loosen a Firestore rule to make a write succeed.** If a write is refused, the
  rule is describing something the page should not be doing.
- **Never put a service-account key or an admin token in a page.** The `apiKey` here is a
  public project identifier, not a secret; anything else is a secret and belongs nowhere in
  `docs/`.
- **A provider that is not enabled in the project is a button that can only fail.** The
  provider list is deliberately short (`google.com`, `password`); adding one means enabling
  it in the Firebase console first, and `auth/operation-not-allowed` is the error that
  proves it was not.
- **Validate before writing.** Length caps (`MAX_NAME`, `MAX_MESSAGE`) are enforced in the
  page and must be enforced again in the rules; a cap that exists only in JavaScript is a
  suggestion.
- **Say what is temporary, in the page.** A chat that keeps nothing must tell the reader so
  before they type, not after they sign out.

## After a change

```sh
python3 .agents/skills/comments/check_firebase.py     # config and rules still agree
python3 .agents/skills/blog-ops/check_site.py         # the pages still pass the head contract
```

A change to the rules is a change to `backups/firebase-rules.txt` yourself — the `docs/`
pages are static and cannot read a rules file, so this document is the only place the two
are held together.
