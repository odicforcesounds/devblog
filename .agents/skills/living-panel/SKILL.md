---
name: living-panel
description: Keep the fixed living card on every page of Monkey Blog — one photograph of a being from the bird, animal, fish or insect catalogues and the sentence "this (being) likes to use (tool)", pinned to the left edge of the window at mid height with a fresh pair on every load. Use when the card must be added, removed, restyled, reshuffled, or checked against links a page already carries.
---

# The living card — one being, one tool, every page

Every page under `docs/` except `index.html` carries one card:

```html
<aside class="living-panel" id="living-panel" aria-label="A living being and a tool">
  <img src="https://upload.wikimedia.org/…/250px-….jpg" alt="European goldfinch"
       width="152" height="90" loading="lazy" decoding="async">
  <p>this <a href="birdsIndex.html#order-passeriformes">European goldfinch</a> likes to use
  <a href="awesomeIndex.html#cat-neovim">Scrollbar</a>.</p>
</aside>
```

The sentence is the picture and that line — nothing more. The being links to the order
it sits in inside one of the five catalogues, the tool to the drawer of the Awesome Index
that holds it.

## Where it sits

`position: fixed; top: 50%; left: clamp(.7rem, 1.6vw, 1.2rem); transform: translateY(-50%)`
— the left edge at mid height, the corner the social dock takes on the front page. The
card is the first child of `<body>`; a fixed element needs a direct child of the body,
because a transformed ancestor would trap it. Nothing on the page is moved to make room:
the card lives in the left margin and shrinks at 1200px, 900px and 640px. It is hidden in
print.

`index.html` carries no card: the social dock already holds that corner.

## The pair changes on every load

The markup holds one being and one tool so the card still reads with scripts off.
`docs/living-panel.js` (290 KB, one same-origin request, holds 1,089 beings and 3,808
tools) replaces that pair with a fresh random one each time the page is loaded, skipping
any link the page already carries. The script tag is `defer` and sits in `<head>`; the
card markup stays as the no-script fallback.

## The rules

- **One card per page, once.** The generator strips the older shapes as it writes: the
  `living-link` footer paragraph, the `living-top` aside and its style, the `living-box`
  strip, and any previous card and script of its own — so a second run changes nothing.
- **No repeated links.** `page_hygiene.py` fails a page that repeats a target, so the
  being links to `index.html#order-<key>` (the order, not the catalogue) and the tool to
  `awesomeIndex.html#cat-<key>` (the drawer). `check_panel_links.py` verifies it across
  the whole site; it must report zero.
- **The photograph is 250px.** The catalogue keeps a 500px file; Wikimedia serves only
  its listed widths and answers 400 for any other, so 250 is used (26 KB instead of
  96 KB). The host is `upload.wikimedia.org`, and the generator adds it to `img-src` on
  pages whose Content-Security-Policy would block it — that directive and no other.
- **The photograph has no anchor of its own.** The being's name carries the link; a second
  anchor to the same order would be a duplicate.
- **The pair in the markup is derived from the page name**, so two generator runs give the
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

# prove no page carries a card target twice
python3 .agents/skills/living-panel/check_panel_links.py
```

After either generator, rebuild the API and audit the site:
`python3 .agents/skills/blog-ops/build_api.py` then
`python3 .agents/skills/blog-ops/check_site.py` (expect `0 failures`).

## Reading the pools

Beings come from the bird, animal, fish and insect catalogues under
`docs/<kingdom>/data/` (every species with a name of 28 characters or less and a
photograph). The plant catalogue is left out: no card names a plant. Tools come from the shelves under
`docs/awesome/data/`, one per list: the list's own name when it is something you code
with (`Bash`, `Go`, `Docker`), otherwise one short real entry from inside it, chosen by a
hash of the list so the site reads varied. One category is drawn first, then a tool inside
it, because the shelves hold very different numbers of lists.

If a shelf file stops being JSON, `awesomeIndex.html` cannot paint and this card loses its
tools: restore it with `.agents/skills/blog-ops/restore_awesome_data.py --apply` rather
than writing a replacement by hand.
