---
name: device-scale
description: Size every page for a phone first and a desktop second — viewport meta, body text that never drops under 16px, tap targets of 44px, no horizontal scroll, and a head-level detection script only where CSS genuinely cannot decide. Use when adding a layout, a navigation bar, a form, a table, an image or any interactive element, and when a page is hard to use on a phone.
---

# Big on a phone, normal on a desktop

The rule is that elements are large for phone screens and normal for desktop screens,
with a detection script loaded at the first level. The way to honour it here is CSS
first: the sheet already scales with the window, and a blocking script costs more than a
media query.

## What exists

- `docs/page.css` carries the fluid scale: `body` from `17.5px` to `19.5px` through
  `clamp(17.5px, 0.45vw + 16px, 19.5px)`, an `h1` from `1.9rem` to `3.05rem`, a measure of
  `68ch`, and one breakpoint at `max-width: 720px`.
- Pages declare `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
  and nothing else. No page ships a user-agent test or a device class today.
- The living card shrinks in steps instead of pushing the reading column.
- Catalogue pages paint one shelf at a time; their weight is the payload budget in
  `page-weight`, not the layout.

## The numbers

| Thing | Phone | Desktop |
| --- | --- | --- |
| Body text | 17.5px minimum, never below 16px | up to 19.5px |
| Tap target (link, button, tab) | 44 × 44px with 8px between | 32px accepted with a pointer |
| Input text | 16px minimum (below that iOS zooms on focus) | same |
| Line length | fills the column | 68ch |
| Fixed card | shrinks, never covers text | full size in the margin |
| Table | scrolls inside a wrapper | full width |

## Rules

- **CSS decides size.** `clamp()`, `min()`, `max()` and media queries. Fewer breakpoints
  beat more; the content should say where one is needed.
- **`viewport` is exactly `width=device-width, initial-scale=1.0`.** No `user-scalable=no`,
  no fixed width, no `maximum-scale`.
- **Font-size is never set to zero to hide text**, and never under 16px on an input.
- **Images carry `width` and `height`** (or `aspect-ratio`) so the layout does not jump,
  and `max-width: 100%` inside a card.
- **No horizontal scroll** at 360px. A wide table, a long code block or a fixed element is
  the usual cause; give it `overflow-x: auto` or shrink it.
- **The detection script is a last resort.** Only when CSS cannot express the decision
  (for example a coarse-pointer layout that needs a different DOM order): inline it in
  `<head>`, keep it under about 1KB, have it set one attribute on `<html>` before first
  paint, and leave the page usable when it does not run. No user-agent string matching —
  `matchMedia('(pointer: coarse)')` answers the question the user agent only guesses at.

```html
<script>document.documentElement.dataset.pointer =
  matchMedia('(pointer: coarse)').matches ? 'coarse' : 'fine';</script>
```

That is the whole script the rule asks for: a first-level detection that CSS can read
(`html[data-pointer="coarse"] .control { min-height: 44px }`), not a redirect or a second
document.

## Test

Check the page at 360 × 640, 390 × 844, 768 × 1024 and 1280 × 800: no horizontal scroll,
nothing under a 44px target that a thumb must hit, the fixed card clear of the text, and
one readable column. Name the viewport and the element when reporting a defect.
