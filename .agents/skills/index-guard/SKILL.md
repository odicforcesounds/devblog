---
name: index-guard
description: Protect every catalogue page docs/*Index.html — the sixteen local indexes on search, data, CSP, living panel, head contract, canonical, noindex, remote scripts and external-API fallback. Use before and after editing an index page, adding an index, changing an index search box, or wiring a public API into a catalogue, so a catalogue cannot lose its local search or data while gaining a remote one.
---

# Index guard

The `docs/*Index.html` pages are the site's catalogues. A decorative edit there
can erase the local search, the data source or the only route to an entry. This
skill states what must survive, then points to the read-only checker.

## The nineteen pages

| Page | Local data manifest | Local search |
| --- | --- | --- |
| `animalsIndex.html` | `docs/animals/data/index.json` | `type="search"` |
| `awesomeIndex.html` | `docs/awesome/data/index.json` | `type="search"` |
| `birdsIndex.html` | `docs/birds/data/index.json` | `type="search"` |
| `carsIndex.html` | `docs/cars/data/index.json` | `type="search"` |
| `catsIndex.html` | `docs/cats/data/index.json` | `type="search"` |
| `danceIndex.html` | `docs/dance/data/index.json` | none |
| `dogsIndex.html` | `docs/dogs/data/index.json` | `type="search"` |
| `electronicsIndex.html` | `docs/electronics/data/index.json` | `type="search"` |
| `fishesIndex.html` | `docs/fishes/data/index.json` | `type="search"` |
| `gamesIndex.html` | `docs/games/data/index.json` | `type="search"` |
| `insectsIndex.html` | `docs/insects/data/index.json` | `type="search"` |
| `lifeIndex.html` | none | none |
| `marketsIndex.html` | `docs/markets/data/index.json` | two: EN and PT |
| `pianosIndex.html` | `docs/pianos/data/index.json` | `type="search"` |
| `plantsIndex.html` | `docs/plants/data/index.json` | `type="search"` |
| `religionsIndex.html` | `docs/religions/data/index.json` | `type="search"` |
| `reptilesIndex.html` | none | none |
| `rocksIndex.html` | `docs/rocks/data/index.json` | `type="search"` |
| `worldIndex.html` | `docs/world/data/index.json` | `type="search"` |

`lifeIndex` and `reptilesIndex` carry their material in the page; they are still
indexes and still protected. `marketsIndex` has two local search inputs by
design; do not merge them.

## Invariants

1. **One local catalogue first.** The page's own search and data render before
   any remote result. A public API may add an escape hatch; it may not become
   the only way to find an entry. If the API fails, the local search still works.
2. **One `h1`, one title, one description.** Keep the description between 110
   and 155 characters, the canonical exactly
   `https://blog.odicforcesounds.com/<file>`, and the page indexable. Do not add
   `noindex` to a catalogue.
3. **One living panel, fixed at 60px.** Exactly one `aside.living-panel`, one
   `style#living-panel-style`, one `living-panel.js` script, and
   `top: 60px` in the panel style. The panel is the first child of `<body>`.
4. **One CSP, no remote scripts.** Keep `default-src 'self'`. Every remote
   `fetch` host must appear in `connect-src`; every remote image host in
   `img-src`. No proxy, no `*`, no external `<script src="https://…">`.
5. **No secret in a query.** An index is public; no `api_key`, token, password
   or client secret may appear in a URL, a constant or a comment.
6. **Search boxes stay local and labelled.** Keep the `<label>`, the input, the
   result count and the empty state. A new external offer is a separate link or
   a block shown after an empty local result; it never replaces the input.
7. **Data stays in the data directory.** Do not paste a catalogue into the page
   or empty a JSON manifest to make a build pass. Use the catalogue-data
   builders; restore a broken file from history and name the commit.
8. **Unique targets.** Panel links, search results and jump links must not repeat
   a target the page already carries. Run `check_panel_links.py`.
9. **No API-only content.** External results need a visible source label, a
   provider record link and a failure path that leaves the local page intact.
10. **Do not add a page without adding it here.** A new `docs/*Index.html` is
    outside the guard until it is listed in the table and in `EXPECTED` in
    `check_indexes.py`.

## Adding a public API to an index

Use `.agents/skills/public-api-context/SKILL.md`. On an index page the order is:

1. local input and local results;
2. local empty state;
3. optional **Search Open Library / Art Institute / Dictionary** link, matched
   to the catalogue's subject;
4. optional result block with a source label, at most six records and a catch
   path.

An index search must not call a public API on every keystroke. If it does fetch,
debounce at least 350 ms, require three characters, abort the previous request,
cache by query and keep the local results visible throughout. The full CSP
additions for all three audited APIs are in the public-api-context skill.

## Run the guard

```bash
python3 .agents/skills/index-guard/check_indexes.py
python3 .agents/skills/index-guard/check_indexes.py --json
python3 .agents/skills/index-guard/check_indexes.py --page docs/plantsIndex.html
```

The checker is read-only. It fails on a missing page, missing or duplicate
`h1`/title/description, wrong canonical, wrong description length, missing CSP,
missing `default-src 'self'`, missing or duplicate panel/style/script, a panel
not at 60px, a `noindex`, an external script, an HTTP fetch, a CORS proxy, a
secret-like query key or a remote fetch whose host is absent from
`connect-src`. It warns on a page without a local search input, a page without a
local data manifest, and an index page outside the expected sixteen.

Five current warnings are accepted: `danceIndex`, `lifeIndex` and
`reptilesIndex` have no `type="search"` input, and `lifeIndex` and
`reptilesIndex` have no data manifest by design. Do not add a search input
unless the request is about that page's search; the two data warnings are
informational.

## Related checks

Run these after an index edit; each owns a different failure:

```bash
python3 .agents/skills/catalogue-data/check_catalogue.py
python3 .agents/skills/link-integrity/check_links.py
python3 .agents/skills/living-panel/check_panel_links.py
python3 .agents/skills/security-headers/check_headers.py
python3 .agents/skills/seo-indexation/check_seo.py
python3 .agents/skills/blog-ops/check_site.py
```

Keep this skill's scope to the index pages. A defect noticed elsewhere is
reported, not repaired in the same edit.
