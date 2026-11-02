---
name: page-css
description: Keep the article pages on one generated stylesheet, docs/page.css, and off the old docs/article.css — the same class contract as before with a fluid type scale, a shorter measure, sticky-bar-safe anchors, responsive tables and media, and print rules that stay readable. Use when the pages' shared styling has to be generated, improved, audited, or when an article.css link is still hanging around.
---

# Page CSS — one sheet for the article family

`docs/page.css` supersedes `docs/article.css`. Both are class-compatible; the pages
no longer load the old file, and the runner swaps any `article.css` link it finds.

| | `article.css` (old) | `page.css` (now) |
| --- | --- | --- |
| Body type | fixed `19px` | fluid `clamp(17.5px, .45vw + 16px, 19.5px)` |
| Measure | `72ch` | `68ch`, `100%` under 720px |
| Column | `1060px` | `1080px`, tighter vertical padding |
| Headings | fixed steps | clamped steps, `text-wrap: balance` |
| Anchors | jump under the sticky bar | `scroll-padding-top` follows `--head` |
| Paragraphs | left, or justified in `.textbox` | justified with hyphenation on wide screens, left on phones |
| Tables | overflow the page | scroll inside the column under 720px |
| Images | `max-width` only | also `max-height: 82vh`, `object-fit: contain` |
| Missing elements | — | `blockquote`, `hr`, `ul/ol`, `dl`, `figure/figcaption`, `::selection` |
| Print | text only | keeps code blocks, code and headings legible |
| Background classes | kept | kept: `.monkey`, `.Memories`, `.offensive`, `.dragon`, `.king`, `.dragonFire`, `.brutalBSD` |
| Legacy classes | kept | kept: `.textbox`, `.black`, `.title1…4`, `.h1-role`, `.md`, `.logicThought`, `.itemList`, `.answer`, `.sourceCode`, `.gr/.b/.r`, `.just`, `.center`, `.note`, `.small`, `.lede`, `.player` |

## Commands

```sh
python3 .agents/skills/page-css/page_css.py            # write the sheet, swap the links
python3 .agents/skills/page-css/page_css.py --dry-run   # report only
python3 .agents/skills/page-css/page_css.py --check      # exit 1 if anything still points at article.css
```

The runner leaves `index.html` alone (it has its own `index.css`) and does not touch
`docs/article.css` itself: the file stays on disk as the previous generation, it is
simply no longer linked. Pages that never loaded `article.css` are not changed, so a
page keeps the design it was built with unless the request names it.

## Order in the head

`page.css` takes the exact slot `article.css` had, so the sheet order stays:

```html
<link rel="stylesheet" href="page.css">
...
<link rel="stylesheet" href="link-colors.css">   <!-- last: colours by destination -->
```

`link-colors.css` must remain the last stylesheet: it paints local, art and external
links and wins the cascade by order. The `link-colors` skill's `--check` proves it is
still linked, and this skill's `--check` proves nothing still points at `article.css`.

## After a run

```sh
python3 .agents/skills/page-css/page_css.py --check
python3 .agents/skills/link-colors/link_colors.py --check
python3 .agents/skills/blog-ops/check_site.py     # expect "0 failures"
```

No browser is available in this environment, so a change here is verified by the
generated file, the link count per page and the audit — not by a screenshot. When a
page looks wrong after a swap, compare its own `<style>` block against the sheet
above: the page-level rules still come later and still win.
