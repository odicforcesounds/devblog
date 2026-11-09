---
name: deploy-firebase
description: Deploy to Firebase only for an application that declares firebase.json and only when the author asks — firebase deploy for Hosting and Firestore or Realtime Database rules, NoSQL data, no key in the client. Use when a project points at Firebase, when a rules change must go live, or when deciding whether a deploy applies to this repository at all.
---

# Deploying to Firebase

## Does it apply?

```sh
ls firebase.json .firebaserc
```

This repository has neither. Its hosting is GitHub Pages and its one Firebase project
(`blog-comments-6b4f5`) is reached by the browser SDK for sign-in and comments only. So
**no `firebase deploy` runs here** unless a request first adds an application that declares
the configuration. A rules file under `backups/` is a copy to paste into the console, not
a deploy target.

When a project does declare it, this skill applies to that project, not to `docs/`.

## The deploy

```sh
firebase login                        # once per machine; the author's session
firebase projects:list                # confirm the project id in .firebaserc
firebase deploy --only hosting        # the site
firebase deploy --only firestore:rules   # the security boundary
firebase deploy --only hosting,firestore:rules
```

Deploy named targets. A bare `firebase deploy` also ships functions, indexes and storage
rules that the request may not have mentioned.

## NoSQL, and what that changes

Firestore is collections of documents; the Realtime Database is one JSON tree. There is no
schema migration and no `ALTER`: a new field appears on the next write, and old rows simply
lack it. That makes the read path responsible for a missing field, and it makes a rules
change the only real migration.

- Rules are the security boundary, and they are deployed separately from the code.
- An index is a query requirement, not a performance hint: a missing one fails the query
  in production.
- A test account with a create permission writes production data; use an emulator or a
  local file store instead.

## Never

- Put a service-account key or an app secret in the repository, a page or a client bundle.
- Deploy from a request that only edited a page.
- Deploy to production unasked. Name the project and the targets, and ask.
- Say a rules change is live because the file changed. It is live when the deploy or the
  console paste finished.

## Verify and report

```sh
curl -s -o /dev/null -w '%{http_code}\n' https://<project>.web.app/
```

Report the project id, the targets deployed, the URL that answered, and anything the deploy
skipped. If a rule was meant to deny an unauthenticated write, prove it with a request that
is refused — a `200` is a finding, not a pass.
