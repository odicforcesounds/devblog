---
name: repo-layout
description: Know and enforce the layout of the devblog repository — which directory owns which kind of file (docs/ pages, docs/images/ assets, templates/, backups/, tmp/, tools/, .agents/skills/), what may never be added next to the pages, and how to verify that nothing landed in the wrong place before committing. Use for any request that adds, moves, renames or deletes files in this repository.
---

# Repository layout

`docs/` is the published site (GitHub Pages, custom domain in `docs/CNAME`). Everything
else is either source, scratch, memory or tooling — never a place for a page. So a file
in the wrong directory is either published by accident, lost by accident, or both.

## The map

| Path | Owner of | Tracked? |
| --- | --- | --- |
| `docs/*.html` | The site: 524 pages (`index.html`, `404.html`, the `home.html` stub, the articles). | Yes |
| `docs/*` (non-HTML) | A fixed infrastructure set, listed below. No new file type without a reason. | Yes |
| `docs/images/` | Every image the pages reference: icons (`.svg`), pictures (`.webp`, `.jpg`, `.jpeg`, `.png`). | Yes |
| `docs/api/` | **Generated** by `.agents/skills/blog-ops/build_api.py`: `index.json` + `text/NNN.json`. | Yes |
| `docs/tools/` | The feed pipeline for `index.html` (`feeds.json`, `build.mjs`, `template.html`). | Yes |
| `docs/archive/`, `docs/obsdRouter/` | Third-party snapshots. Read-only, excluded in `robots.txt`, absent from sitemap and API. | Yes |
| `docs/pdfs/` | Downloadable PDFs linked from articles. | Yes |
| `docs/sitemap.xml`, `docs/robots.txt` | **Generated** by `.agents/skills/blog-ops/build_sitemap.py`. | Yes |
| `templates/` | Starting points for new pages (`dataDossier.html`). Never published. | Yes |
| `backups/` | Memory: runbooks (`CLOUDFLARE.md`, `GOOGLE.md`, Firebase), old versions (`original/`), maps (`*_map.json`), `blog_sitemap.xml`, `urls/`. | Yes |
| `tools/` | Local scan scripts (`bg_scan.py`). | **No — gitignored** |
| `tmp/` | One-off scripts, `.orig.html` snapshots, harnesses, experiments. | **No — gitignored** |
| `free/` | Exported chat logs. | **No — gitignored** |
| `.agents/skills/` | The skills themselves, each `<name>/SKILL.md` plus its scripts. | Yes |
| `.github/` | Repository automation. | Yes |
| root | `README.md`, `.gitignore`, `pushit.sh`, `update.sh`. Nothing else. | Yes |

The whole non-HTML set at `docs/` root is: `api.js`, `article-lang.js`, `article.css`,
`index.css`, `style.css`, `musicDatabase.json`, `CNAME`, `favicon.ico`, `robots.txt`,
`sitemap.xml`, `.nojekyll`. Two of those are generated (regenerate, never hand-edit),
the rest are hand-written infrastructure. That list is the budget: a new `.md`, `.py`,
`.sh` or scratch `.json` at `docs/` root is a mistake.

## Where a new file goes

1. **An article, manual or game page?** `docs/Name.html` — see the `new-page` skill.
2. **An image or icon for a page?** `docs/images/name.ext`, referenced as
   `./images/name.ext`; asset rules are in the `assets-backups` skill.
3. **Data consumed by a page?** A `.json` under `docs/` only if the page `fetch`es it
   (`musicDatabase.json` is the precedent). Otherwise inline the data in the page.
4. **A script that must be run again** by a person or a skill? `.agents/skills/blog-ops/`
   when a documented workflow needs it, `tools/` when it is a local build/scan step.
   Both `tools/` and `tmp/` are gitignored, so nothing durable can live only there.
5. **A script run once** (a bulk rewrite, a migration)? `tmp/`, and it must be idempotent.
6. **A starting point for pages?** `templates/`. A template is generic and date-free.
7. **A previous version of something, or a runbook?** `backups/`, with a name that says
   what it is. Git already keeps history, so a backup is for facts, not for safety copies.

## Rules

- **`docs/` contains pages and their assets, nothing else.** No `.md` notes, no scripts,
  no editor leftovers, no `*.orig.html`, no `*.bak`.
- **Generated files are generated.** `docs/sitemap.xml`, `docs/robots.txt` and
  `docs/api/**` are rebuilt by scripts; editing them by hand is undone on the next build
  and hides a real inconsistency.
- **Tracked and gitignored are different promises.** `tools/`, `tmp/` and `free/` are
  ignored: a file there is invisible to `git`, to a fresh clone and to the deploy.
  `pushit.sh` runs `git add .`, so a stray tracked file gets published in the next commit.
- **Dates come from git**, never from a field typed by hand — see the `git-dates` skill.
- **Keep the root flat.** `README.md`, `.gitignore`, the two deploy scripts. A new
  top-level name needs a reason; scratch belongs in `tmp/`.
- **Descriptive lowercase names** for assets (`one-human-song.svg`); article names keep
  the existing PascalCase/camelCase (`oJogoDoAdvogado.html`).

## Verify before committing

```sh
# what is dirty, and what is new (untracked files are the usual mistake)
git status --porcelain

# the non-HTML files at docs root — must match the budget list above
find docs -maxdepth 1 -type f ! -name '*.html' | sort

# scratch that leaked into the published tree
find docs -maxdepth 1 -type f \( -name '*.md' -o -name '*.py' -o -name '*.sh' \
  -o -name '*.orig.*' -o -name '*.bak' -o -name '*~' \)

# anything tracked that should be ignored, and vice versa
git ls-files docs | wc -l
git check-ignore -v tools/bg_scan.py tmp/2FA.orig.html

# directories that must never appear in the sitemap or the API
grep -c 'archive/\|obsdRouter/\|api/' docs/robots.txt
```

A layout change is done when `git status` shows only the files the task was about, and
`python3 .agents/skills/blog-ops/check_site.py` still ends with `0 failures`.
