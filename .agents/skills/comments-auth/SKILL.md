---
name: comments-auth
description: Guard the Google and email sign-in path of the comment form on index.html — the provider list, Firebase imports, CSP permissions, Firebase config, avatar hosts, form lock and the live Google provider response. Use after changing index.html, its CSP, the auth imports or the comment widget, and before publishing.
---

# Comment sign-in guard

The comment widget on `docs/index.html` has no static Google button. The HTML leaves
`#comment-providers` empty; a module imports Firebase from `www.gstatic.com`, initializes
the project and calls `renderProviders()` to create the Google and Email buttons. If any
link in that chain breaks, the page still renders and simply shows no provider button —
the failure looks like a design choice, not an error.

This skill protects that chain. It is read-only.

## What it holds

| Check | Level |
| --- | --- |
| `index.html` still carries `#comment-providers` and the comment form | failure |
| `AUTH_PROVIDERS` still contains `google.com` | failure |
| `GoogleAuthProvider`, `signInWithPopup`, `signInWithRedirect`, `renderProviders()` and the Firebase imports are present | failure |
| the form starts locked and its submit button starts disabled | failure |
| `firebaseConfig` has `apiKey`, `authDomain`, `projectId` and `appId` | failure |
| the project id and auth domain agree | failure |
| no service-account key, client secret or private key is in the page | failure |
| the CSP allows the Firebase SDK scripts from `https://www.gstatic.com` | failure |
| the CSP allows the Firebase APIs and auth domain in `connect-src` | failure |
| the CSP permits the auth domain and `accounts.google.com` in `frame-src` | failure |
| `img-src` permits every host in `AVATAR_HOSTS` | failure |
| the CSP keeps `default-src 'self'`, `object-src 'none'` and `base-uri 'self'` | warning |
| the CSP does not contain `'unsafe-eval'` | failure |
| with `--live`, `createAuthUri` returns a Google `authUri` | failure |
| with `--live`, the three Firebase SDK modules answer `200` | failure |

The page currently needs these CSP sources:

- `script-src`: `'self' 'unsafe-inline' https://www.gstatic.com`
- `connect-src`: `'self' https://*.googleapis.com https://*.firebaseio.com wss://*.firebaseio.com https://blog-comments-6b4f5.firebaseapp.com`
- `frame-src`: `https://blog-comments-6b4f5.firebaseapp.com https://accounts.google.com`
- `img-src`: `'self' data: https://upload.wikimedia.org` plus every host named in
  `AVATAR_HOSTS` (`lh3.googleusercontent.com`, `avatars.githubusercontent.com`,
  `pbs.twimg.com`, `platform-lookaside.fbsbx.com`, `s.yimg.com`).

## Run it

```sh
python3 .agents/skills/comments-auth/check_comments_auth.py
python3 .agents/skills/comments-auth/check_comments_auth.py --live
python3 .agents/skills/comments-auth/check_comments_auth.py --json
```

`--live` performs two network checks: it asks the Firebase project whether `google.com`
answers `createAuthUri`, and it fetches the three Firebase SDK modules. Without `--live`
the check is entirely offline and only reads the page.

Exit code 0 when no failures remain, 1 otherwise. Warnings do not fail the run.

## Rules

- **The provider and the console must agree.** A provider in `AUTH_PROVIDERS` that is not
  enabled in Firebase is a button that can only fail. Add a provider to the console first,
  then to the array.
- **Widen one directive for one real request.** A sign-in change that needs a new origin
  adds that origin to the directive that governs it; it does not replace the policy with a
  wildcard and it does not add `'unsafe-eval'`.
- **Keep `'unsafe-inline'` in `script-src`.** The page carries its JavaScript inline on
  purpose. Removing it breaks the page, not an attack path this checker can repair.
- **The API key is public.** `apiKey` is a Firebase project identifier. A service-account
  key, a client secret or a private key is not, and must never appear in `docs/`.
- **A static search for “Google” proves nothing.** The button is created after the imports
  and `renderProviders()` run; the checker tests those links, not the word.
- **Do not edit the live Firebase rules from this skill.** The rules live in
  `backups/firebase-rules.txt` and are checked by the `comments` skill.

## After a change

```sh
python3 .agents/skills/comments-auth/check_comments_auth.py --live
python3 .agents/skills/comments/check_firebase.py
python3 .agents/skills/security-headers/check_headers.py --page index.html
python3 .agents/skills/blog-ops/check_site.py
```

The first command is the sign-in gate. The other three keep the project config, the
page's other resources and the site's head contract intact.
