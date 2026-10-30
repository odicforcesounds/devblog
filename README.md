# devblog

A static, self-contained blog published at <https://blog.odicforcesounds.com>.

There is no server and no build step between a file and the site: everything under
`docs/` **is** the website, served by GitHub Pages. Alongside the pages live three
things that are generated rather than written — the sitemap, the JSON API and its text
chunks — plus the scripts that regenerate them.

## What this repository contains

- **The archive** — 524 HTML files at the root of `docs/`: 521 articles, plus
  `index.html` (the landing page), `404.html` and `home.html` (a redirect stub kept for
  old links). The subject range is deliberately wide; see
  [Topics covered](#topics-covered).
- **Search on the landing page** — `docs/index.html` filters its own category list from
  a single input, with no dependency and no second page to visit.
- **A 404 page** — `docs/404.html`, which GitHub Pages serves for missing paths, with
  its own search over the JSON API.
- **A comment form** — on `index.html` only: Google, e-mail/password and phone number
  sign-in, a Firestore-backed thread, no anonymous posting. Rules in
  `backups/firebase-rules.txt`; what was broken and how it was fixed in
  `backups/comments-login-failure.md`; how to add back Facebook or GitHub in
  `backups/setup-facebook-github.md`.
- **A static JSON API** — `docs/api/index.json` (metadata and a chunk manifest),
  `docs/api/dates.json` (name → publication instant, 24 KB, what `index.html` loads)
  and `docs/api/text/*.json` (article text, 14 chunks). Built by
  `.agents/skills/blog-ops/build_api.py`, read by
  `docs/api.js`.
- **Shared styling** — `docs/article.css`, `docs/index.css`, `docs/style.css`.
- **A page template** — `templates/dataDossier.html`.
- **The feed pipeline for `index.html`** — `docs/tools/feeds.json` (feeds by category)
  injected into the page as `window.FEED_DATA` by `docs/tools/build.mjs`.
- **Runbooks, in `backups/`** — `CLOUDFLARE.md` (DNS, proxy, bots, redirects, cache,
  headers, HSTS), `GOOGLE.md` (structured data, Search Console order of operations),
  the two comment documents above. None of them is published: `backups/` sits outside
  `docs/`.
- **The skills, in `.agents/skills/`** — `blog-ops` (the audit and build scripts:
  `check_site.py`, `build_sitemap.py`, `enrich_schema.py`), `new-page` (how a page is
  written and compiled), `repo-layout` (what belongs in which directory), `git-dates`
  (publication and update dates from git history), `tmp-tools` (scripts and scratch in
  `tmp/` and `tools/`) and `assets-backups` (templates, runbooks, images).
- **Archive collections** — third-party snapshots under `docs/archive/` and
  `docs/obsdRouter/`, kept for readers and excluded in `robots.txt`.

## Repository structure

```text
devblog/
├── README.md
├── pushit.sh, update.sh       deploy helpers (ksh)
├── .agents/skills/blog-ops/   build_api.py, check_site.py, build_sitemap.py, enrich_schema.py
├── .agents/skills/*/          SKILL.md per skill (new-page, repo-layout, git-dates, tmp-tools, assets-backups)
├── backups/                   runbooks, originals, maps, firebase-rules.txt
├── docs/                      ← published site root
│   ├── index.html             landing page, categories, search, comment form
│   ├── 404.html               error page (noindex), search over the API
│   ├── home.html              redirect stub for the old page name
│   ├── *.html                 the 521 articles
│   ├── api/                   generated: index.json + text/NNN.json
│   ├── api.js                 vanilla ES module that reads the API
│   ├── archive/, obsdRouter/, pdfs/, images/
│   ├── article.css, index.css, style.css
│   ├── sitemap.xml, robots.txt, CNAME, .nojekyll
│   └── tools/                 feed pipeline for index.html
├── templates/dataDossier.html
├── tools/                     local scratch (gitignored)
└── tmp/                       local scratch (gitignored)
```

## How the site is served

GitHub Pages publishes the `docs/` folder of `main` for the custom domain in
`docs/CNAME`. A Cloudflare proxy sits in front of it; the edge can change how the site
is crawled or inject scripts without a byte changing here, so the settings that matter
are written down in `backups/CLOUDFLARE.md`.

`docs/.nojekyll` is present so GitHub serves the tree exactly as it is. `docs/404.html`
is served, with a 404 status, for any path that does not exist.

## Writing a page

1. Start from `templates/dataDossier.html`, or copy the markup and inline CSS of a
   similar page. Pages are self-contained: their `<style>` and `<script>` live in the
   file.
2. Keep the head contract. Every page has exactly one of each:
   `<title>`, `meta[name=description]`, `link[rel=canonical]`, the Open Graph tags
   (`og:title`, `og:description`, `og:type`, `og:url`, `og:site_name`, `og:image`), the
   Twitter tags (`twitter:card`, `twitter:title`, `twitter:description`,
   `twitter:image`), one JSON-LD block, and **one** `<h1>` with text. The JSON-LD block
   is a `@graph` with a `BlogPosting` (image object with dimensions, `Person` author,
   publisher with logo, category, keywords, word count) and a `BreadcrumbList`
   Home › category › article. `datePublished` and `dateModified` come from git.
   Descriptions run 110–155 characters and are unique across the site. Run
   `enrich_schema.py` rather than writing a graph by hand.
3. `<!DOCTYPE html>` is the first thing in the file. Anything before it puts the page in
   quirks mode.
4. Regenerate what is derived, and audit before committing:

   ```sh
   python3 .agents/skills/blog-ops/enrich_schema.py        # JSON-LD graph (idempotent)
   python3 .agents/skills/blog-ops/build_api.py            # docs/api/
   python3 .agents/skills/blog-ops/build_sitemap.py        # sitemap.xml + robots.txt
   python3 .agents/skills/blog-ops/check_site.py           # exit 0 = consistent
   ```

5. `./pushit.sh` pulls, commits and pushes. Nothing is live until it runs.

## Comments

One page has them: `docs/index.html`. The thread lives in Firestore
(`blog-comments-6b4f5`) and is readable by anyone; writing needs an account.

Three ways in, matching exactly what is enabled in the Firebase project:

| Method | SDK call |
| --- | --- |
| Google | `signInWithPopup`, falling back to `signInWithRedirect` |
| E-mail and password | `signInWithEmailAndPassword`, `createUserWithEmailAndPassword`, `sendPasswordResetEmail` |
| Phone | `RecaptchaVerifier` (invisible) + `signInWithPhoneNumber`, then the SMS code |

The buttons are built from the `AUTH_PROVIDERS` array in the module at the bottom of
`index.html`; a provider that is not enabled in the Firebase console must not be in that
array, because the only thing its button can do is fail. Phone sign-in additionally
needs the reader's country allowed under Authentication → Settings → SMS region policy.

The Firestore rules (`backups/firebase-rules.txt`) accept a create only from a
signed-in user, with the exact field set, length caps, `request.auth.uid` matching
`uid`, and `createdAt == request.time`; update and delete are denied from the client.

**Editing the widget:** the module is ES-module only and jsdom cannot fetch its imports,
so behaviour is tested by stubbing Firebase and running the module body inside jsdom
(`tmp/authtest/test_comments_auth.mjs` when that scratch file is present). It covers
sign-in, sign-out, wrong password, an existing account, the SMS flow, a bad code, the
Google popup and the reset mail.

## The JSON API

A static substitute for an endpoint: plain JSON files served like any other asset, read
in the browser. No server, no database, no third-party requests.

```sh
curl -s https://blog.odicforcesounds.com/api/index.json | jq '{count, languages, years}'
```

`index.json` carries `generated`, `origin`, `count`, `languages`, `years`, `chunks`
(the text manifest) and `articles` (522 entries, `index.html` among them). Each entry has
`slug`, `url`, `path`,
`title`, `description`, `lang`, `published`, `modified`, `published_at`, `modified_at`,
`h1`, `headings`, `words`, `chars`.

```js
import { BlogAPI } from "/api.js";

await BlogAPI.ready();
BlogAPI.search("freebsd");         // titles, headings, descriptions
await BlogAPI.searchFull("pf");    // adds article text, streamed chunk by chunk
BlogAPI.recent(5);                 // newest changes
```

`searchFull` calls `onResults` after each chunk, so a page can paint while the rest is
still travelling. `404.html` is built on it.

`404.html` calls `searchFull` before the manifest has arrived — the retry is inside
`docs/api.js`; do not remove it.

The API covers the pages as documents, `index.html` included. Only `404.html` and the
`home.html` stub are left out: one must never appear in results, the other is not a
page.

## Checks

`python3 .agents/skills/blog-ops/check_site.py` audits every root page for the head
contract above and then verifies that `sitemap.xml`, `robots.txt` and `docs/api/`
describe the same set of pages. It exits non-zero on any failure and prints short
descriptions as warnings rather than errors.

Current run: 524 pages, 0 short-description warnings, 0 failures. The two pages that used
to carry a second pasted document (`ArtOfCreation.html`, `JS4Children.html`) were split;
`check_site.py` reports any page that merges two documents again.

## Publication dates

Pages do not display a publication date. `datePublished` and `dateModified` in each
page's JSON-LD come from git — the first commit that touched the file and the last one:

```sh
git log -1 --format=%ad --date=short -- docs/Page.html
```

There is no date object inside `index.html`: the home page fetches `docs/api/dates.json`
(24 KB, `name → published_at`) and uses it for the date badges and the ordering of
"Last 5 publications". The full `docs/api/index.json` (362 KB) is for `docs/api.js` and
the JSON consumers, not for the home page. Either way the generated API is the only copy
of the dates the browser sees.

Because that is a `fetch`, the home page needs to be served over HTTP: opened from disk
(`file://`) the request fails and the archive shows no dates.

## CSS and layout

- `docs/article.css` — article page styles
- `docs/index.css` — home page styles
- `docs/style.css` — shared base

Most pages also carry a `<style>` block of their own, because they were written as
self-contained documents. Keep that local styling local: a fix for one article should
not move the rest of the archive.

## Topics covered

- **Operating systems and open source** — Linux, FreeBSD, OpenBSD
- **Security and hacking** — defensive and offensive notes, tools, field manuals
- **Programming, sysadmin and infrastructure** — practical write-ups
- **Social commentary, politics and law** — criticism and controversial takes
- **Philosophy, psychology, creativity and music** — fewer pages, same archive

Some of it is intentionally provocative.

## Notes on the archive

- `docs/archive/` and `docs/obsdRouter/` hold snapshots of third-party pages. They are
  readable but disallowed in `robots.txt` and absent from the sitemap.
- `docs/questions.html` is the loose thread: entries that were moved, retitled or
  grouped.
- `tmp/`, `tools/`, `free/` and `.agents/*` (except `.agents/skills/`) are
  gitignored. Scripts that must survive belong at the repository root or in
  `.agents/skills/` — `pushit.sh` runs `git add .`, so scratch files left outside those
  paths get committed.
- `backups/` is tracked on purpose: the runbooks and the original pages are part of the
  repository's memory, and GitHub Pages never serves them because they sit outside
  `docs/`.

## Current state

Branch `main`, deployed by GitHub Pages. 521 articles across four language tags
(`en`, `pt`, `pt-PT`, `es`), dated 2025–2026. Publishing has no fixed cadence; the
repository activity is the way to follow it.
