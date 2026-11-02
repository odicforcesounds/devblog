---
name: seo-indexation
description: Audit what a search engine can actually index on this blog — title length and uniqueness, description fit, canonical ↔ file name, noindex ↔ sitemap ↔ API agreement, sitemap and robots.txt consistency, JSON-LD date parity with article:published_time, internal-link count and reachability from index.html, and the language blocks that carry two languages in one URL. Read-only; it reports and fixes nothing. Use before publishing, after adding pages, or when a page is not being picked up.
---

# Indexation — what a crawler sees

`check_site.py` proves the head contract (one title, one canonical, one JSON-LD, one
`h1`). This skill audits the layer above it: whether those tags add up to a page a
search engine will index, and whether the sitemap, the API and the pages tell the same
story. Nothing here writes a file.

## The checks

| Check | Rule | Level |
| --- | --- | --- |
| Title | present, unique across the site, ≤ 60 characters | unique/present = failure, length = warning |
| Description | 90–155 characters, unique | out of range = failure, 90–110 = warning |
| Canonical | present and equal to `https://blog.odicforcesounds.com/<file>` ( `…/` for `index.html` ); `404.html` and `home.html` exempt | failure |
| Indexability | `noindex` page must not be in `sitemap.xml` **and** not in `docs/api/index.json` | failure |
| Coverage | every indexable page in the sitemap; every sitemap URL a real page | failure |
| Sitemap dates | `lastmod` on every URL, year between 2024 and 2026, one origin only | failure (missing lastmod = warning) |
| robots.txt | a `Sitemap:` line, three groups with the same rules, `/api/`, `/archive/`, `/obsdRouter/` disallowed | failure |
| `h1` | exactly one | failure |
| JSON-LD | parses, one block, a `BlogPosting`/`CollectionPage`/`WebPage` node, `datePublished` in 2024–2026 | failure |
| Date parity | `article:published_time` and `datePublished` name the same year | failure |
| Internal links | at least 3 outgoing links to other pages | warning |
| Reachability | every page within 3 clicks of `index.html` | warning |
| Languages | pages with `data-lang-block` and no `hreflang` | one warning for the set |

The thresholds are the ones a result page enforces in practice: about 60 characters of
title, about 155 of description. They live at the top of `check_seo.py` so a change is
one edit, not a search.

## Commands

```sh
python3 .agents/skills/seo-indexation/check_seo.py            # full report
python3 .agents/skills/seo-indexation/check_seo.py --quiet     # findings only
python3 .agents/skills/seo-indexation/check_seo.py --json      # machine-readable
```

Exit code 0 when there is no failure, 1 otherwise; warnings never set the code.

## What it found the first time

- 70 titles over 60 characters (`AndroidDevelopment.html` is 61).
- `secretChat.html` is `noindex` and was listed in the sitemap **and** in the API — the
  two signals contradict each other. That is a decision, not a typo: either the page is
  public and the `noindex` goes, or it stays secret and the builders must skip it.
- Four pages carried 2 internal links each (`militaryDumbs.html`, `learnChess.html`,
  `warVoid.html`, `loveStories.html`) against a median of 6.
- 31 pages hold English and Portuguese behind a switch in one URL, and 3 of them carry
  `hreflang`; a crawler indexes both languages as one document.

## Rules

- **Report, do not repair.** The findings are decisions about the blog's shape — a
  shorter title, a page dropped from the sitemap, an extra link from the archive. The
  script changes none of them.
- **Never hand-edit `sitemap.xml`, `robots.txt` or `docs/api/**`.** Rebuild with
  `build_sitemap.py` / `build_api.py`; a manual edit is undone by the next build.
- **A `noindex` page is a promise.** If it must stay out of the index, keep it out of the
  sitemap and the API in the same change, and say why in the page or the runbook.
- **Titles are written for the result, not for the archive.** `index.html` shows an
  entry's title with its own styling; a search result truncates it, so the first 60
  characters have to carry the subject.
- **Reachability beats a sitemap.** A page nobody links to is crawled late or not at
  all, even when listed; the fix is a link from a page that belongs to the same subject
  (the `new-page` skill's rule about subject-matched internal links).

## After a run

```sh
python3 .agents/skills/blog-ops/check_site.py       # the head contract
python3 .agents/skills/seo-indexation/check_seo.py  # the indexation layer
```

Both are read-only; neither needs a browser, a network request or a Search Console
account. Search Console itself is a console task, described in `backups/GOOGLE.md`
(which is older than the site it describes — see its state line before trusting its
numbers).
