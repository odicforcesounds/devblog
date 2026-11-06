---
name: link-integrity
description: Verify that every link on the site resolves — an offline pass that fails on any relative href/src pointing at a file that is not in docs/, plus an optional, cached, sampled pass over the 64k absolute links to catch link rot. Use after renaming, moving or deleting a page or asset, before publishing, and whenever a page shows a broken stylesheet, image or jump link.
---

# Links — does every one of them go somewhere

**Run these checks and builds only when the author asks.** The audit scripts named here,
and `build_sitemap.py` / `build_api.py`, are not part of every task: finish the edit, say
which check would prove it, and run it when it is requested.

**One page is one project.** Each `docs/*.html` file is a project of its own: its markup,
script and styles are written there, and the only relation between two pages is the `<a>`
link from one to the other. Where a page fetches data, that data is its own API, in its
own files and folder (`docs/api/`, or the page's own `data/`). One page is one API. Test
only the page and the API you touched; every other page and API is out of scope.

`check_site.py` audits the head; `seo-indexation` audits reachability **between** pages.
Neither opens a `href`. This skill does: a link is a promise, and the promise is either
kept by a file in `docs/` or by somebody else's server.

## Two passes, because they cost different things

| Pass | Runs | Cost | Catches |
| --- | --- | --- | --- |
| **local** (default) | always | milliseconds, no network | a renamed page, a stylesheet never shipped, `bsdAlternatives.html.html`, an image moved out of `docs/images/` |
| **external** (`--external`) | on request | minutes, network | link rot on the 64,489 absolute links, one dead host at a time |

The local pass is the one to run on every change. The external pass is a scheduled chore:
it samples by default, caches every answer for 30 days, and rotates with `--offset`.

## Commands

```sh
python3 .agents/skills/link-integrity/check_links.py                     # the pages changed in git
python3 .agents/skills/link-integrity/check_links.py docs/Page.html      # that page only
python3 .agents/skills/link-integrity/check_links.py --all               # every root page
python3 .agents/skills/link-integrity/check_links.py --external          # add 120 sampled URLs
python3 .agents/skills/link-integrity/check_links.py --external --sample 0 --offset 12000
python3 .agents/skills/link-integrity/check_links.py --json              # machine-readable
python3 .agents/skills/link-integrity/check_links.py --drop-cache        # start the external pass fresh
```

The pages are independent files, so a run covers the pages this change touched and takes
the rest as already sound; `--all` is the whole-site pass. `<pre>` and `<code>` samples
are teaching material, not links: a lesson that shows `<script src="app.js">` is not
reported as a dead reference.

Exit code 0 when nothing is broken, 1 when a link is dead or an external anchor is
malformed. Warnings (unverifiable, server-side errors, a missing `#id`) never set the code.

## Every external link opens a new tab

An anchor that leaves the site carries both attributes, in this order:

```html
<a href="https://example.org/report" target="_blank" rel="noopener">report</a>
```

The local pass fails a page whose external `href` lacks `target="_blank"`, and fails one
that has `target="_blank"` without `noopener` in `rel` (the a11y audit checks the second
half too). No exceptions: an internal `./Page.html` stays in the same tab; anything with a
scheme, or a `//host/` path, is external and gets both attributes.

## What counts as a link

`href` and `src`, single or double quoted, on the 542 root pages: pages, sheets, scripts,
images, PDFs, `fetch()` targets that are written as attributes, and the `#fragment` of
each one. Skipped on purpose: `mailto:`, `tel:`, `data:`, `javascript:`, `about:`, `sms:`,
`blob:` — those are not files and not servers.

Resolution follows the browser, not the eye: `./x`, `x`, `/x` and `images/x` are all
resolved against the page's own directory, `%20` is decoded, `?query` is dropped, and a
path that names a directory becomes its `index.html`.

## Rules

- **A dead local link is always a failure, never a warning.** It cannot be fixed by a
  later deploy; it is a file the page asks for and does not get. Either the file ships or
  the link goes.
- **Never "fix" a dead link by deleting the anchor.** The prose that surrounds it is the
  page. Point it at the page that replaced the target, or at the archive copy, and say
  which in the commit message.
- **The external pass never decides a page's fate.** A 403 or a 429 means a site refuses
  robots, not that a human sees a broken link. Those are warnings by design.
- **Never commit the cache.** `tmp/link-cache.json` is scratch: gitignored, disposable,
  and meaningless after 30 days.
- **`--sample 0` is a decision, not a default.** It fetches every stale URL; run it
  deliberately, not on every change, and not from a shared IP you care about.
- **A same-tab external link is a failure, not a style choice.** `target="_blank"` plus
  `rel="noopener"` on every off-site anchor is part of the link contract, checked offline
  by the local pass.

## What it found the first time

**26 local references point at files that do not exist, on 15 pages.** `evilForums.html`
links a stylesheet `archive.css` that was never shipped, so it renders unstyled;
`theFreeDocs.html` links `bsdAlternatives.html.html`, a doubling typo; `secretFiles.html`
alone has eleven `./archive/files/…` targets from the old layout; `logicProvocation.html`
and `theories.html` still point into `./blog/awesome/files/…`; `Nentoo.html` reaches
outside the site to `../gentloo.html`; and `domain_statistics.html` and `hackclub.html`
link `.md` files that were never part of the site.

286 further warnings, almost all the same shape: a `#fragment` that names no `id`, often
doubled by a builder — `fishesIndex.html#order-oegopsida#order-oegopsida`.

The absolute links were never verified: **64,489 of them across 10,859 distinct hosts**.

## After a run

```sh
python3 .agents/skills/link-integrity/check_links.py      # no dead local reference
python3 .agents/skills/blog-ops/check_site.py             # head contract still intact
```

A local failure is fixed by one of three edits — ship the file, repoint the anchor, or
remove the link with the sentence that needed it. Anything else leaves the audit red.
