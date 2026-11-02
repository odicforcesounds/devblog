---
name: security-headers
description: Audit each page's Content-Security-Policy against what that page actually loads — stylesheets, scripts, iframes, images and fetches — so a policy can never silently block its own page's sheet or script again, plus the other meta headers every page should carry. Use when adding a script, a stylesheet, an iframe or a remote image, when a page renders unstyled or its script does not run, and before publishing.
---

# Headers — the policy must permit the page

A CSP failure is invisible. The page still renders, the console is only seen by whoever
opens it, and the damage looks like a styling choice: **31 pages** linked
`link-colors.css` while their own `style-src` refused every stylesheet file, so every link
on them was one colour. Nothing looked broken, which is exactly why it lasted.

This skill derives the requirements from the page instead of comparing against a template:
whatever the page loads, its own policy has to allow.

## What it checks

| Requirement | Rule | Level |
| --- | --- | --- |
| Policy present | a `Content-Security-Policy` meta | warning |
| `default-src` | allows `'self'` (or `*`) | failure |
| Stylesheet | every local `<link rel=stylesheet>` allowed by `style-src` | failure |
| Script file | every `<script src>` allowed by `script-src` | failure |
| Inline script | `'unsafe-inline'`, a nonce or a hash when the page has one | failure |
| Iframe | every `<iframe src>` host allowed by `frame-src` | failure |
| Image | every `<img src>` host allowed by `img-src` | failure |
| Fetch | every `fetch(url)` allowed by `connect-src` | failure |
| `'unsafe-eval'` | absent | warning |
| `object-src`, `base-uri` | present and closed | warning |
| `nosniff`, `X-Frame-Options`, `Referrer-Policy` | present, `nosniff` spelled right | warning |

The directive falls back the way a browser does: a page with no `style-src` is governed by
`default-src`. A policy that closes a directive but loads that resource is a failure, not
a preference.

## Commands

```sh
python3 .agents/skills/security-headers/check_headers.py                  # every root page
python3 .agents/skills/security-headers/check_headers.py --page x.html    # one page
python3 .agents/skills/security-headers/check_headers.py --json           # machine-readable
```

Exit code 0 when no page blocks its own resources, 1 when one does. Read-only.

## Rules

- **Widen exactly one directive, in one place.** `link_colors.py` adds `'self'` to
  `style-src` and nothing else; `living_panel.py` adds the Wikimedia image host to
  `img-src` and nothing else. A wholesale policy replacement is how a page loses a
  permission nobody remembers it needed.
- **Never add `'unsafe-inline'` to `script-src` to silence a finding.** The pages here
  carry their JavaScript inline on purpose, so `'unsafe-inline'` is the accepted state for
  them — but it is a decision recorded for a page class, not a reflex for a red line.
- **`'unsafe-eval'` is never acceptable.** Nothing on this site needs it.
- **A missing policy is not a pass.** 162 of 542 pages carry no policy at all; the ones
  that load a remote frame or image are named as warnings so the gap is at least counted.
- **The browser is the judge, not this script.** When they disagree, the browser wins and
  the script is corrected.

## What it found the first time

**70 failures and 1,373 warnings over 542 pages.** 380 pages carry a policy, **162 carry
none**, and the 380 are not one policy: `vontadeDivina.html` allows inline scripts,
`aFairJusticeSystem.html` allows bandcamp frames, `digestUnix.html` allows only Wikimedia
images, `KaliLinux.html` closes everything and reopens only what it needs.

The failures are all the same shape — a page loading something its own policy refuses:

- **19 pages** embed a Bandcamp player under `default-src 'self'` with no `frame-src`, so
  the player cannot load at all: `EthicalLawsOnIT.html`, `aboutPolitics.html`,
  `beingSafe.html`, `changeWithin.html`, `confession.html` among them.
- **3 stylesheets** refused: `beingSafe.html` and `github_challenge.html` carry a
  `style-src` without `'self'`, so `page.css` and `link-colors.css` never load — the same
  defect that hit 31 pages before.
- **2 images** refused by `img-src`: a `raw.githubusercontent.com` screenshot on
  `darkInsideLight.html`, and the catalogues' Wikimedia photograph on `beingSafe.html`.
- **1 script** refused: `living-panel.js` on `beingSafe.html`.

## After a run

```sh
python3 .agents/skills/security-headers/check_headers.py   # no page blocks its own resources
python3 .agents/skills/link-colors/link_colors.py --check   # the sheet is still linked and permitted
python3 .agents/skills/blog-ops/check_site.py               # head contract intact
```
