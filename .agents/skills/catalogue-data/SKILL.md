---
name: catalogue-data
description: Keep the JSON behind the eight catalogue pages intact — every file parses, each category in index.json names a real file, every category file declares its own key and title, entries carry a name and an http(s) URL, no name repeats inside a category, and no data file is orphaned. Use when adding or editing anything under docs/*/data/, before publishing a catalogue, or when a category disappears from a page.
---

# Catalogue data — the JSON eight pages read

`docs/animals/`, `birds/`, `fishes/`, `insects/`, `plants/`, `electronics/`, `awesome/`
and `living/` are not pages, they are data sources: each `*Index.html` fetches
`data/index.json`, then the per-category file the reader asked for. A broken file does not
produce a broken page — it produces a **missing category**, with no error a reader can see.

## The shape

| Collection | `index.json` | One category file |
| --- | --- | --- |
| `animals`, `birds`, `fishes`, `insects`, `plants` | counts plus `groups`/`orders`/`sections` of `{key, num, title, …}` | `{key, title, families: [{n, c, s: [{n, s, u, d, h, r}]}]}` |
| `electronics` | counts plus `categories` of `{key, num, title, blurb, slug, …}` | `{key, num, title, blurb, groups: [{name, items: [{n, u, s, t}]}]}` |
| `awesome` | counts plus `categories` of `{key, num, title, lists, tools, slug}` | `{key, … items …}` |

The file name **is** the key: `carnivora.json` must say `"key": "carnivora"`, and the
category that lists it must use the same string. That is the only link between the page
and its data, and it is a string match.

## What it checks

| Check | Level |
| --- | --- |
| every file in `docs/*/data/` parses | failure |
| a category file's `key` equals its file name | failure |
| no two categories share a key | failure |
| an entry's URL, where present, is `http(s)` | failure |
| a category key with no `<key>.json` | warning |
| a category file no category names (orphan) | warning |
| a name repeated inside one file | warning |
| a category or file with no title | warning |

Counts such as `animals: 269` or `tools: 46353` are **not** validated: the pages display
them as prose, and a stale count is a sentence, not a failure.

## Commands

```sh
python3 .agents/skills/catalogue-data/check_catalogue.py            # every data directory
python3 .agents/skills/catalogue-data/check_catalogue.py --dir animals
python3 .agents/skills/catalogue-data/check_catalogue.py --json
```

Exit code 0 when the data holds, 1 when a file is broken. Read-only.

## Rules

- **Split by category, never by "everything".** `awesome/data/index.json` is 14 MB because
  it is one drawer of all 46,353 tools; the per-category files beside it are the fix and
  the model for anything new (see the `page-weight` skill).
- **The key is an identifier, not a label.** Renaming `key` renames the file and the
  category in `index.json` in the same change, or the reader loses the category.
- **Never hand-edit a generated file.** `tmp/build_electronics.py` and the animal/plant
  builders produce these; a manual edit is the next build's input, not its output.
- **A duplicate name inside one file is usually a merge accident**, and the second copy is
  the one to drop — it has the shorter description.
- **URLs are Wikipedia and Wikimedia.** They are read-only references; when one 404s the
  fix belongs in the builder, and `link-integrity --external` will find it there.

## What it found the first time

**384 files, 366 categories, 82,262 entries, 7 data directories — 3 failures and 66
warnings.** The data is in far better shape than its size suggests, and the three failures
are two typos and one legacy shelf:

- `docs/awesome/data/dotnet.json` and `net-libraries-tools-and-frameworks.json` — the
  FreeSql entry has `https:/github.com/…`, one slash short of a scheme, so the anchor is
  dead on the page.
- `a-curated-list-of-ios-ecosystem-libraries-and-resources.json` — the Doloffer Guide has
  `github.com/Doloffer-g/guide`, no scheme at all.
- The same file declares `"key": "ios"` while `index.json` counts the category as
  `android-ui` and `ios`: its name is neither, which is why it reads as a legacy shelf.
- `docs/awesome/data/` carries **aliases** — `ai.json` beside `ai-and-automation.json`,
  `beyond.json` beside `beyond-code.json`, `security.json` beside
  `security-privacy-and-forensics.json` — same bytes twice, which is why
  `restore_awesome_data.py` exists in `blog-ops`.
- `animals/data/tetraodontiformes.json` lists `Tetraodontidae` twice, and the awesome
  shelves repeat generic names (`Chrome extension`, `Unreal Engine`) across groups.

## After a run

```sh
python3 .agents/skills/catalogue-data/check_catalogue.py     # data holds together
python3 .agents/skills/page-weight/check_weight.py           # and is not too heavy to fetch
```
