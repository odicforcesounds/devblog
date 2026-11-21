---
name: incremental-api
description: Keep docs/api/ append-only — insert the record for one page and leave every other row of the JSON untouched, because each page is a project of its own and these files are the database this static site emulates. Use whenever docs/api/index.json, dates.json or text/NNN.json is about to change, when a new page needs a date badge or a search entry, or when an audit asks for an "API build".
---

# The API is a database, not a build

**Never a full API build.** `build_api.py` walks every `docs/*.html` and rewrites
`index.json`, `dates.json` and every text chunk. Run to add one page, it rewrites the record
of every page ever published, and the diff stops being the page you changed. No agent ever
runs it, at the end of a task, to make an audit green, or because the author said "update
the API": that request means *add the missing record*.

**Each page is independent.** `docs/*.html` is not one application. Every page carries its
own markup, script and styles, and the only relation between two pages is the `<a href>`
from one to the other. Where a page fetches data, that data is its own; a page that carries
its own text has no row in the shared API and does not need one.

**The JSON files are the database.** Nothing is rendered at request time, so the site keeps
its tables in files and the pages query them with `fetch`:

| File | Table | Row |
| --- | --- | --- |
| `docs/api/dates.json` | dates | `name → published_at`, one per page |
| `docs/api/index.json` | articles | one object per page that reads the API |
| `docs/api/text/NNN.json` | text | page text, packed in chunks; the manifest in `index.json` lists them |

A database update inserts or replaces the row you touched. Rewriting the table to add a row
is the defect this skill exists to prevent: it loses the diff, it can silently change rows
nobody asked about, and it makes the history unreadable.

## Adding one page

1. **Date — always.** Every root page gets one row in `dates.json`, because `index.html`
   reads it for the badges and the "Last 5 publications" order:

   ```sh
   python3 .agents/skills/blog-ops/append_dates.py docs/NewTitle.html   # --dry-run first
   ```

   The instant is the first commit that added the file
   (`git log --diff-filter=A --format=%aI -- docs/NewTitle.html | tail -1`), the same rule
   as the page and the sitemap — never the clock, never the mtime. `--restore` takes the
   value from the last committed `dates.json` instead, so an instant decided by hand for a
   copy or a rename comes back as it was, and a row whose value differs from that map is
   put back. `404.html` and `home.html` are in no table.

2. **Index — only if the page reads it.** A page that loads `api.js`, calls `BlogAPI`, or
   fetches under `api/` needs its article object appended to `articles`: the fields
   `build_api.py` writes, the page's text added to the **newest** text chunk, and that
   chunk's `count` and `bytes` in `chunks` updated. The script carries that row:

   ```sh
   python3 .agents/skills/blog-ops/append_dates.py --index Page.html
   ```

   Never re-chunk the set and never renumber an existing chunk: those files are the rows
   other pages already read. A page that carries its own text is left out, and
   `check_site.py` no longer asks for it.

3. **Put the file in order first.** The rows go in the builder's order — `index.html`
   first, the rest by name — before the new name is placed among them, so the record lands
   where it belongs instead of at the end of the file. Ordering moves keys, never values.

4. **Nothing else moves.** Existing rows, the compact separators and the `generated` field
   of untouched records stay as they are; `count` follows the number of rows.

## Prove it

```sh
python3 .agents/skills/blog-ops/append_dates.py --check   # writes nothing, exits 1 on a gap
python3 -c "import json; d=json.load(open('docs/api/dates.json')); print(d['count'], len(d['published']))"
git diff --numstat -- docs/api   # one file, one changed line for a one-page insert
```

`--check` names every root page with no date row and says whether the map is in the
builder's order; it is the read-only proof, and it never writes. A damaged table is
restored from a revision, not regenerated — `backups/api-recovery.md` has the steps.

The file is a single compact line, so `git diff` shows the whole line: read the added keys
in the diff rather than trusting the count alone. `generated` is the newest instant in the
map, not the day this skill was read.

`build_api.py` stays on disk as the script that first wrote the API and as the record of
how its rows look. Running it is a rewrite of that history; if a row is ever needed back,
restore the file from git (`git show <rev>:docs/api/dates.json`) instead of regenerating it,
as described in `backups/api-recovery.md`.
