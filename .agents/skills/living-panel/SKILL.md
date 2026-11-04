---
name: living-panel
description: Keep the fixed living card on every page of Monkey Blog — one photograph of a being from the bird, animal, fish or insect catalogues and the sentence "this (being) likes to use (tool) and loves (component) while doing some diet with (plant) at (city)", pinned to the top right corner of the window with a fresh set on every load. Use when the card must be added, removed, restyled, reshuffled, or checked against links a page already carries.
---

# The living card — one being, one tool, one part, one plant, one city, every page

Every page under `docs/` except `index.html` carries one card:

```html
<aside class="living-panel" id="living-panel" aria-label="A living being, a tool, a component, a plant and a city">
  <img src="https://upload.wikimedia.org/…/250px-….jpg" alt="Golden hamster"
       width="152" height="90" loading="lazy" decoding="async">
  <p>this <a href="animalsIndex.html#order-rodentia" title="Cricetidae · Rodentia">Golden hamster</a>
  likes to use <a href="awesomeIndex.html#cat-dotnet" title="Stripe.Net · .NET libraries, tools and frameworks">Stripe.Net</a>
  and loves <a href="electronicsIndex.html#cat-assembly" title="Soldering and wiring · Boards, packaging and wiring">Desoldering</a>
  while doing some diet with <a href="plantsIndex.html#order-arecales" title="Arecaceae · Arecales">Coconut</a>
  at <a href="worldIndex.html#cat-tm" title="Turkmenistan · Asia">Ashgabat</a>.</p>
</aside>
```

The sentence is the picture and that line — nothing more, and the order is fixed:

> this **(being)** likes to use **(tool)** and loves **(component)** while doing some diet with **(plant)** at **(city)**.

Each name links to the shelf that holds it — the being to its order inside one of the four
kingdom catalogues, the tool to the Awesome Index drawer, the component to its category
drawer in the electronics catalogue, the plant to its order in the plant catalogue, and
the city to its country shelf in the world catalogue — and, in the card the script builds,
to the entry itself (see *A click lands on the entry*). The `title` on a component, a plant
or a city says what family, order or country it belongs to, so a bare `Desoldering`, a
Latin binomial or `Ashgabat` still reads as something placed. A city is always the most
populous place of its country whose name fits and needs no disambiguating suffix, so the
sentence never ends in `Lisbon · Maine`.

## Where it sits

`position: fixed; top: 60px; right: clamp(1.2rem, 7vw, 8rem)` — the right side of the
window, pulled a little way in from the edge, 60px down, floating above the top bar. The
sentence is left-aligned; only the photograph is centred. The card is the first child of
`<body>`; a fixed element needs a direct child of the body, because a transformed ancestor
would trap it. Nothing on the page is moved to make room: the card lives in the right
margin and shrinks at 1200px, 900px and 640px. It is hidden in print.

`index.html` carries no card: the social dock already holds a corner of the window.

## The set changes on every load

The markup holds one being, one tool, one component, one plant and one city so the card
still reads with scripts off. `docs/living-panel.js` (**185 KB**, one same-origin request,
holding 1,089 beings, 3,119 tools, 304 components, 265 plants and 246 cities) replaces
that set with a fresh random one each time the page is loaded, skipping any link the page
already carries and any target already used inside the card. The script tag is `defer` and sits in `<head>`;
the card markup stays as the no-script fallback.

The pool is the only real cost of the card: every browser downloads all of it to use four
entries, so an entry holds a name and the shortest thing that names its target, and the
script rebuilds the rest:

| Column | Stored | Rebuilt by the script |
| --- | --- | --- |
| being | name, catalogue code (`b`/`a`/`f`/`i`), order key, thumb path | `<catalogue>Index.html?q=<name>#order-<key>`, and `…/thumb/<path>/250px-<file>` from the path's own last segment |
| tool | name, drawer key | `awesomeIndex.html?q=<name>#cat-<key>` |
| component | name, category key | `electronicsIndex.html?q=<name>#cat-<key>` |
| plant | name, order key | `plantsIndex.html?q=<name>#order-<key>` |
| city | name, country key | `worldIndex.html?q=<name>#cat-<key>` |

That is what keeps five thousand entries at 185 KB instead of 403 KB. The no-script card
in the markup still carries the full `title` captions; the script does not, because it
would be the largest thing in the file and reads as tooltip noise.

## A click lands on the entry

Every link the script builds carries the name it shows:

```html
<a href="animalsIndex.html?q=Golden%20hamster#order-rodentia">Golden hamster</a>
```

The query is what the target page searches for, and the anchor is the shelf it opens, so a
click lands on the being, tool, component, plant or city named in the card rather than at
the top of a drawer. On load every catalogue page reads `q` and runs its own search:

| Page | What `?q=` does |
| --- | --- |
| `birdsIndex`, `animalsIndex`, `fishesIndex`, `insectsIndex`, `plantsIndex`, `electronicsIndex`, `awesomeIndex` | fills the page's search box and runs it, so the entry is the result |
| `worldIndex` | fills the place finder and runs it |

The name arrives URL-encoded (`encodeURIComponent` in the script, `quote(name, safe="")`
in the generator) because a binomial, a `.NET` library or a place name carries dots, spaces
and parentheses.

The target page reads that `q` as a **linked query**: it fills the search box, runs the
match, hides the full catalogue and shows only the result, then returns the viewport to
the top. The whole name must match, the shelf or order in the hash selects between namesakes,
and exactly one card is painted — the Bratislava in the Slovakia shelf, not every
Bratislava. Editing or
clearing the search box leaves linked mode and brings the full index back below the
matches.

The card written into the markup keeps the plain anchor (`animalsIndex.html#order-rodentia`).
With scripts off nothing reads a query string, and the anchor is what still opens the
shelf, so `plain()` strips the query before it is written — a generator run stays
idempotent and the 545 pages are not rewritten for a link the fallback cannot use.

`fishesIndex`, `insectsIndex`, `plantsIndex` and `electronicsIndex` gained their search
line for this card: before it, a click could only open a drawer.

## The photograph expands, the card can go away

A single click on the photograph opens the 500px copy over a dark overlay; a click
anywhere on the overlay or `Escape` closes it. The image is keyboard-focusable and
`Enter` or `Space` toggles the same view. A double-click hides the whole card for the
rest of that page load; reloading brings it back. Both gestures are wired in
`docs/living-panel.js`, so with scripts off the card remains the read-only fallback.

## The rules

- **One card per page, once.** The generator strips the older shapes as it writes: the
  `living-link` footer paragraph, the `living-top` aside and its style, the `living-box`
  strip, and any previous card and script of its own — so a second run changes nothing.
- **No repeated links.** `page_hygiene.py` fails a page that repeats a target, so each of
  the five links goes to a shelf anchor rather than a page: `#order-<key>` for being and
  plant, `#cat-<key>` for tool, component and city. In the script the shell string carries
  the query as well, which keeps the five apart even where two entries share a shelf. The five must also differ from each
  other — a being and a plant from the same order would otherwise collide, and two cities
  of one country share their `#cat-<key>`. `check_panel_links.py` verifies both, across the
  whole site; it must report zero.
- **The photograph is 250px.** The catalogue keeps a 500px file; Wikimedia serves only
  its listed widths and answers 400 for any other, so 250 is used (26 KB instead of
  96 KB). The host is `upload.wikimedia.org`, and the generator adds it to `img-src` on
  pages whose Content-Security-Policy would block it — that directive and no other.
- **The photograph has no anchor of its own.** The being's name carries the link; the
  photograph is a button-like image that expands on a click and hides the card on a
  double-click.
- **The set in the markup is derived from the page name**, so two generator runs give the
  same site; the rotation happens in the browser, not at build time.

## Commands

```sh
# write the card and its style + script tag into every page
python3 .agents/skills/living-panel/living_panel.py
python3 .agents/skills/living-panel/living_panel.py --dry-run
python3 .agents/skills/living-panel/living_panel.py --page docs/lichess.html
python3 .agents/skills/living-panel/living_panel.py --remove

# rebuild the pool the card rotates through (after the catalogues or shelves change)
python3 .agents/skills/living-panel/build_living.py

# prove no page carries a card target twice, and no card repeats itself
python3 .agents/skills/living-panel/check_panel_links.py
```

After either generator, rebuild the API and audit the site:
`python3 .agents/skills/blog-ops/build_api.py` then
`python3 .agents/skills/blog-ops/check_site.py` (expect `0 failures`).

## Reading the five pools

| Column | Source | Rule |
| --- | --- | --- |
| being | `docs/{birds,animals,fishes,insects}/data/` | A species with a photograph and a name of 28 characters or less; its 500px file is rewritten to 250px. |
| tool | `docs/awesome/data/`, one per list | The list's own name when it is something you code with (`Bash`, `Go`, `Docker`), otherwise one short real entry from inside it, chosen by a hash of the list. One category is drawn first, then a tool inside it. |
| component | `docs/electronics/data/`, every item | Name between 3 and 24 characters, linked to its category drawer. |
| plant | `docs/plants/data/`, every species | Name of 28 characters or less, linked to its order. The name is the catalogue's `n`, so it is a binomial for most species and a common name for those the data has one for. |
| city | `docs/world/data/`, one per country | The most populous place of the country whose name is 22 characters or less and carries no `·` suffix, linked to that country's shelf. 246 countries, so 246 cities. |

The being keeps the photograph; the other four are words, which is what keeps the pool
under a quarter of a megabyte for five thousand entries.

If a shelf file stops being JSON, `awesomeIndex.html` cannot paint and this card loses its
tools: restore it with `.agents/skills/blog-ops/restore_awesome_data.py --apply` rather
than writing a replacement by hand.
