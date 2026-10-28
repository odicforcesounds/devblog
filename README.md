# devblog

A static, self-contained blog published at <https://blog.odicforcesounds.com>.

There is no server and no build step between a file and the site: everything under
`docs/` **is** the website, served by GitHub Pages. Alongside the pages live three
things that are generated rather than written — the sitemap, the JSON API and its text
chunks — plus the scripts that regenerate them.

## What this repository contains

- **The archive** — 517 article pages under `docs/`, including `index.html`. The
  subject range is deliberately wide; see [Topics covered](#topics-covered).
- **A home page for the API** — `docs/home.html`, a vanilla JavaScript browser over the
  JSON index: full-text search, filters by language and year, no dependencies.
- **A static JSON API** — `docs/api/index.json` (metadata and a chunk manifest) and
  `docs/api/text/*.json` (article text, 13 chunks). Built by `build_api.py`, read by
  `docs/api.js`.
- **A 404 page** — `docs/404.html`, which GitHub Pages serves for missing paths, with
  its own search over the same API.
- **Shared styling** — `docs/article.css`, `docs/index.css`, `docs/style.css`.
- **A page template** — `templates/dataDossier.html`.
- **The feed pipeline for `index.html`** — `docs/tools/feeds.json` (feeds by category)
  injected into the page as `window.FEED_DATA` by `docs/tools/build.mjs`.
- **The comment form's rules** — `backups/firebase-rules.txt`: Firestore rules that
  accept a comment only from a signed-in account (Google, GitHub, Microsoft, Apple, X,
  Facebook, Yahoo — no anonymous sign-in), plus the console checklist.
- **Hosting runbook** — `CLOUDFLARE.md`: DNS/proxy state, WebMCP, bot rules, redirects,
  cache, headers, HSTS. Not published.
- **The `blog-ops` skill** — `.agents/skills/blog-ops/`, with `check_site.py` (audit)
  and `build_sitemap.py` (sitemap + robots).
- **Backups and snapshots** — `backups/`: original pages, URL maps, the previous
  sitemap, the Firebase rules.
- **Archive collections** — third-party snapshots under `docs/archive/` and
  `docs/obsdRouter/`, kept for readers and excluded in `robots.txt`.

## Repository structure

```text
devblog/
├── README.md
├── CLOUDFLARE.md              edge configuration runbook (not published)
├── build_api.py               rebuilds docs/api/ from docs/*.html
├── pushit.sh, update.sh       deploy helpers (ksh)
├── .agents/skills/blog-ops/   check_site.py, build_sitemap.py, SKILL.md
├── backups/                   originals, maps, firebase-rules.txt
├── docs/                      ← published site root
│   ├── index.html             archive landing page
│   ├── home.html              browser over the JSON API
│   ├── 404.html               error page (noindex)
│   ├── *.html                 the articles
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
are written down in `CLOUDFLARE.md`.

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
   `twitter:image`), one JSON-LD block (`BlogPosting`), and **one** `<h1>` with text.
   `datePublished` and `dateModified` come from git. Descriptions run 110–155
   characters and are unique across the site.
3. `<!DOCTYPE html>` is the first thing in the file. Anything before it puts the page in
   quirks mode.
4. Regenerate what is derived, and audit before committing:

   ```sh
   python3 build_api.py                                    # docs/api/
   python3 .agents/skills/blog-ops/build_sitemap.py        # sitemap.xml + robots.txt
   python3 .agents/skills/blog-ops/check_site.py           # exit 0 = consistent
   ```

5. `./pushit.sh` pulls, commits and pushes. Nothing is live until it runs.

## The JSON API

A static substitute for an endpoint: plain JSON files served like any other asset, read
in the browser. No server, no database, no third-party requests.

```sh
curl -s https://blog.odicforcesounds.com/api/index.json | jq '{count, languages, years}'
```

`index.json` carries `generated`, `origin`, `count`, `languages`, `years`, `chunks`
(the text manifest) and `articles`. Each article has `slug`, `url`, `path`, `title`,
`description`, `lang`, `published`, `modified`, `h1`, `headings`, `words`, `chars`.

```js
import { BlogAPI } from "/api.js";

await BlogAPI.ready();
BlogAPI.search("freebsd");         // titles, headings, descriptions
await BlogAPI.searchFull("pf");    // adds article text, streamed chunk by chunk
BlogAPI.recent(5);                 // newest changes
```

`searchFull` calls `onResults` after each chunk, so a page can paint while the rest is
still travelling. `home.html` and `404.html` are built on it.

`home.html` on a cold start calls `searchFull` before the manifest has arrived — the
retry is inside `docs/api.js`; do not remove it.

The API covers the articles only. `home.html` and `404.html` are excluded on purpose:
one is this browser, the other is a page that must never appear in results.

## Checks

`python3 .agents/skills/blog-ops/check_site.py` audits every root page for the head
contract above and then verifies that `sitemap.xml`, `robots.txt` and `docs/api/`
describe the same set of pages. It exits non-zero on any failure and prints short
descriptions as warnings rather than errors.

Two pages currently fail it, for a content reason, not a markup one:

- `docs/ArtOfCreation.html` contains three HTML documents concatenated — everything
  after the first `</html>` is merged into the page body by the browser.
- `docs/JS4Children.html` contains two.

Each needs to be split into separate files. `check_site.py` reports them and leaves them
alone.

## Publication dates

Pages do not display a publication date. `datePublished` and `dateModified` in each
page's JSON-LD come from git — the first commit that touched the file and the last one:

```sh
git log -1 --format=%ad --date=short -- docs/Page.html
```

There is no `dates.json`; that file is gone and nothing reads it.

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
- `tmp/`, `tools/` and `free/` are gitignored. Scripts that must survive belong at the
  repository root or in `.agents/skills/` — `pushit.sh` runs `git add .`, so scratch
  files left outside those paths get committed.

## Current state

Branch `main`, deployed by GitHub Pages. 517 articles across four language tags
(`en`, `pt`, `pt-PT`, `es`), dated 2025–2026. Publishing has no fixed cadence; the
repository activity is the way to follow it.
