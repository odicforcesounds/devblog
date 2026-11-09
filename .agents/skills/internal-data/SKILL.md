---
name: internal-data
description: Decide where the JSON a page reads lives and who can read it — a page's own data folder or docs/api/ for what may be public, backups/ or the ignored stk/ folder for anything internal, because every file under docs/ is downloadable. Use when a page needs data, when adding or changing a data file, or when a fetch would expose something meant to stay inside.
---

# Internal data — public file, private file

The rule is "JSON files hold public data, requested when a reader opens the page; they
belong to an internal API, not available to the public". This host is static: there is no
internal API to authenticate against. The rule survives as a placement decision.

## The static fact

GitHub Pages serves every file under `docs/`, including `docs/api/` and every
`docs/<catalogue>/data/` shelf. `robots.txt` disallows `/api/` so crawlers leave it alone;
a person with the URL still downloads it. So:

- **May be public** — names, links, counts, article metadata and text, catalogue rows,
  generated dates. These go under `docs/`.
- **Must not be public** — credentials, service keys, drafts, customer rows, private
  notes, an inbox export, anything from `stk/`. These never go under `docs/`, whatever
  the page does with them. `backups/` is tracked and never served; `stk/` is ignored.

If a page genuinely needs a secret, it cannot have it: a static page has no server side
to keep one. Say that instead of hiding it in a JSON file.

## The shape

A data set is a manifest plus one file per shelf, not one large blob:

```text
docs/<catalogue>/data/index.json     the shelves, their titles and counts
docs/<catalogue>/data/<shelf>.json   one shelf, fetched when opened
docs/api/index.json                  the archive metadata + the chunk manifest
docs/api/dates.json                  name -> published instant, for the front page
docs/api/text/NNN.json               article bodies, one chunk at a time
```

The page fetches the index, paints the shelves, and fetches one shelf when it is opened.
That is why `awesomeIndex.html` opens fast with 46,353 tools behind it. Follow the same
pattern for a new set; do not load everything to filter it in the browser.

## Rules

- **Generated data is generated.** Anything under `docs/api/` comes from
  `.agents/skills/blog-ops/build_api.py`; catalogue shelves come from
  `.agents/skills/catalogue-data/builders/`. Hand-editing either is undone on the next run.
  Rebuilding is an author-only step, asked for by name.
- **The builder validates the shape.** A category key must name a real file, a shelf must
  declare its own key and title, an entry must carry a name and an `http(s)` URL — see the
  `catalogue-data` skill and its checker.
- **No key in JSON.** A token in `docs/` is a published token, whether or not a page links
  it.
- **No per-reader data and no write path.** A static file cannot personalise an answer,
  and a `POST` has nowhere to land. A feature that needs either is a server feature, not a
  data file.
- **One page, one API.** A page that fetches reads its own folder or the archive API, not
  another page's shelf.

## Check before you call it internal

```sh
python3 -m http.server 8080 --bind 0.0.0.0 --directory docs
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/api/dates.json
```

A `200` means the world can read it too. If the file is not meant for that, move it out of
`docs/` (to `backups/` or the ignored `stk/`) and report where it was.
