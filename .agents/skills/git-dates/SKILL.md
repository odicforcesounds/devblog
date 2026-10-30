---
name: git-dates
description: Derive and fix article dates in this blog from git history — first commit as datePublished, last commit as dateModified, including the rename/copy case — and keep the JSON-LD, docs/api/index.json, sitemap lastmod and index.html consistent with that. Use whenever a page date, publication order, "Last 5 publications" entry or dateModified looks wrong.
---

# Dates come from git

This repository is the history. A page's publication date is the date its content first
entered git; its update date is the last commit that touched it. Nothing else is
authoritative: not the file mtime (a clone or checkout rewrites it), not a date typed into a page, not the machine clock.

## The commands

```sh
# published: the commit that added the file
git log --diff-filter=A --format=%ad --date=iso-strict -- docs/Page.html | tail -1

# modified: the last commit that touched it
git log -1 --format=%ad --date=iso-strict -- docs/Page.html

# the whole lineage, oldest last — needed when the file was renamed or copied
git log --follow --format='%h %ad %s' --date=iso-strict -- docs/Page.html
```

Use `%ad` (author date: when the work was done), not `%cd`. Use `iso-strict` so the offset
survives; the page JSON-LD takes `YYYY-MM-DD` and the index map takes the full timestamp.

## Renames and copies — the trap that already bit us

`--diff-filter=A` answers "when was *this path* added". A page copied or renamed from an
older one is therefore reported as added **today**, while its content is older. Worked
example: `docs/OneHumanSong.html` was created on 2026-10-30 as a copy of
`docs/CommonCultures.html`, which had the same `<title>` since 2026-10-16 22:49:01 +0100.
The true publication is 2026-10-16.

So when a page's date looks suspiciously recent:

```sh
# did this path come from somewhere?
git log --follow --name-status --format='--- %h %ad' --date=short -- docs/Page.html | head -30
# a line like  C061  docs/Old.html  docs/New.html  means: copied from docs/Old.html
```

Then date the page by the oldest commit in that lineage, and record the exception in
`.agents/skills/blog-ops/build_api.py` so the API agrees:

```python
PUBLISHED_OVERRIDES = {"OneHumanSong.html": "2026-10-16T22:49:01+01:00"}
```

`build_api.py` applies that map both to the cached dates and to freshly computed ones.

## Where the date is consumed

| Place | Field | Written by |
| --- | --- | --- |
| Page `<head>` JSON-LD | `datePublished`, `dateModified` | the page itself (`enrich_schema.py` can rewrite the graph) |
| `docs/api/index.json` | `published`, `modified`, `published_at`, `modified_at` | `.agents/skills/blog-ops/build_api.py` from git (`--diff-filter=A` / `-1`) |
| `docs/api/dates.json` | `published` map: name → instant | same script, same dates, compact form |
| `docs/sitemap.xml` | `lastmod` | `.agents/skills/blog-ops/build_sitemap.py` |
| `docs/index.html` | `published_at` read from `dates.json` | the page itself, at load time (no date object is stored in it) |

`index.html` keeps no dates of its own: it fetches `./api/dates.json` and uses the
`published` map for the "Last 5 publications" block and the date badges. A page missing
from that map simply has no badge — the honest fix is deriving the date from history, not
typing today's clock. Both JSON files come from the same `git_dates()` run, so they cannot
disagree; `check_site.py` fails if `dates.json` has no instant for a page listed in
`index.json`.

## Procedure for a wrong date

1. `git log --follow` the file and read the oldest commit — that is `datePublished`.
2. `git log -1` for `dateModified`.
3. Check whether the path was copied/renamed (the `C`/`R` status above). If so, use the
   source's oldest commit and add the `PUBLISHED_OVERRIDES` entry.
4. Update the page JSON-LD (`datePublished`, `dateModified`) — only those fields.
5. Nothing to edit in `docs/index.html`: it reads the date from the API at load time.
6. Rebuild: `python3 .agents/skills/blog-ops/build_api.py` and
   `python3 .agents/skills/blog-ops/build_sitemap.py`.
7. Prove agreement:

```sh
python3 - <<'PY'
import json, re
page = "docs/OneHumanSong.html"
src = open(page, encoding="utf-8").read()
ld = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)]
print("page:", ld[0]["@graph"][0]["datePublished"], ld[0]["@graph"][0]["dateModified"])
api = json.load(open("docs/api/index.json"))
slug = page.split("/")[-1][:-5]
print("api  :", [(a["published_at"], a["modified_at"]) for a in api["articles"] if a["slug"] == slug])
dates = json.load(open("docs/api/dates.json"))["published"]
print("dates:", dates.get(page.split("/")[-1]))
PY
```

8. Confirm the ordering effect before reporting: the "Last 5" list sorts every linked
   page by `published_at` descending, so a page moved back in time also moves down the
   list (or leaves it).

## Rules

- **Never** use `ls -l`, `stat`, `os.path.getmtime` or `new Date()` to date an article.
- **Never** hand-edit `docs/api/index.json` or `docs/sitemap.xml`; rebuild them.
- **Never** set a date that git cannot confirm; if history is missing (a shallow clone),
  say so instead of guessing.
- `dateModified` in JSON-LD is allowed to differ from the sitemap `lastmod` only when the
  page was edited without a commit yet; commit before calling it published.
- If the user wants a page to appear "a few days ago", that is a history question: find
  the commit that introduced the content (possibly under another name) and use it.
