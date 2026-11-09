---
name: privacy-data
description: Keep personal data off every page, public or private — no e-mail address, surname, city, phone number, token or screenshot that carries one — and check what a form, a JSON file or a commit message would publish before it ships. Use when a page would show a person's details, when adding a form, a data file, an example or an image, and before publishing anything that came from a real inbox.
---

# Personal data — what never goes on a page

**Run a check only when the author asks.** Finish the edit, name the check that would
prove it, and run it on request.

## What counts

An e-mail address, a phone number, a surname attached to a private person, a home or
office city, a street, coordinates, a customer or order number, an account id, an IP
address tied to a person, a token, a key, a password, a screenshot of an inbox, a
dashboard, a log or a chat. A name alone is not personal data when it is the subject of
a public page (an author, a politician, a species); it is when it identifies a private
person who did not ask to be published.

## Why "private page" does not save it

Everything under `docs/` is served by GitHub Pages: a page that is not linked, not in the
sitemap, and disallowed in `robots.txt` still answers `200` to anyone who guesses the
name. `robots.txt` asks crawlers to stay away; it is not a lock. Only two places are
outside the published tree — `backups/` (tracked, never served) and the ignored `stk/`
folder — and neither is a place for a reader's data either.

## Where it leaks here

| Surface | The leak |
| --- | --- |
| Page prose | An address in a code sample, a real name in an anecdote, a city under "I live in". |
| `docs/*/data/`, `docs/api/` | A field a builder copied from a private list (`email`, `phone`, `address`, `token`). |
| `docs/images/` | A screenshot with a mailbox, a name in a tab title, a photo carrying GPS EXIF. |
| `<head>` | `author` in JSON-LD, an `og:image` URL with a query string. |
| `alt` text | The full name of a private person, or a file name that is one. |
| Commit messages | They publish with the repository; an address there is as public as a page. |
| Cited links | A URL with an e-mail or a session id in its query string. |

## The substitutions

- Addresses use `example.com` / `example.org`; a real domain only when the domain itself
  is the subject.
- Phone numbers use a documented fictional range (`+1 555 0100`, `+351 210 000 000`),
  never a number that rings.
- A role address (`postmaster@`, `abuse@`) is public by design; a person's is not.
- A city from `docs/world/data/` is catalogue data, not a location of a person. The
  living card says "at Lisbon" because Lisbon is a row, not because anyone is there.
- In a form, ask for nothing the feature does not use. The comment widget takes an
  account, not an address typed into the page, and the phone sign-in number is handled by
  Firebase and never stored by the page.

## Checks

```sh
# addresses and numbers a page would publish
grep -nE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' docs/Page.html
grep -nE '(\+[0-9]{1,3}[ .-]?)?\(?[0-9]{3}\)?[ .-]?[0-9]{3}[ .-]?[0-9]{4}' docs/Page.html

# fields that should never appear in JSON a page fetches
grep -nE '"(email|phone|address|token|key|secret|password)"' docs/*/data/*.json

# what the diff would add
git diff -U0 -- docs/Page.html | grep '^+'
```

Open any new image before committing it; a reader's name in a screenshot is the same
leak as a name in text.

## Rules

- **A test value is a value.** `john@company.com` becomes a real inbox eventually; use
  the reserved domains.
- **Do not "fix" a leak by deleting the file.** Remove the field or the image reference,
  and report what was there.
- **The form's promise is part of the feature.** A page that says a thread is public, or
  that a message disappears in fifteen minutes, must not collect more than that.
- **Keys are never data.** A Firebase web config is a public identifier and is allowed in
  a page; a service-account key, an API secret or a page token is not, in any file.
