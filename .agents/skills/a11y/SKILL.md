---
name: a11y
description: Audit the accessibility basics on every page — alt text, the document language, Chinese and Portuguese runs declared as the wrong language, links with no accessible name, target=_blank without rel=noopener, duplicate ids, controls with no label and positive tabindex. Use when adding an image, a link, a form or a second language to a page.
---

# Accessibility — who the page is for

The site is dark, dense and full of images, Chinese lines under English ones, and links
whose text is a single word on purpose. None of that is a problem. The problem is when the
markup does not say what the page visibly says: an image with no `alt` is a blank space, a
Chinese line under `lang="en"` is read aloud in English, a link whose only content is an
icon is announced as "link".

## What it checks

| Check | Level |
| --- | --- |
| `<img>` without `alt` | failure |
| `<html>` with no `lang`, or no `<html>` at all | failure |
| link with no accessible name (no text, no `alt` child, no `aria-label`) | failure |
| `target="_blank"` without `rel="noopener"` | failure |
| the same `id` twice on a page | failure |
| Chinese text under a `lang` that is not `zh`/`ja` | warning |
| a language block with no `lang` of its own | warning |
| `<input>`/`<select>`/`<textarea>` with no label | warning |
| link named only by `title` or `aria-label` | warning |
| positive `tabindex` | warning |

Failures are things a reader cannot work around; warnings are things a reader can, at a
cost. Contrast is not measured here — it needs a rendered page, and this runs offline.

## Commands

```sh
python3 .agents/skills/a11y/check_a11y.py                  # every root page
python3 .agents/skills/a11y/check_a11y.py --page x.html    # one page
python3 .agents/skills/a11y/check_a11y.py --json           # machine-readable
```

Exit code 0 when no failure, 1 when one is found. Read-only.

## Rules

- **`alt` describes the image, not the file.** `alt="Aedes aegypti"` on the panel image is
  right; `alt="image"` is not, and an empty `alt=""` is only right when the image is
  decoration beside text that already says the same thing.
- **A language switch sets `lang` on both blocks.** The page carries Portuguese and English
  in one URL; without `lang` on each block, a screen reader pronounces both in the
  document's language. That is the warning this skill raises on 31 pages.
- **`rel="noopener"` is not optional with `target="_blank"`.** Every external link here
  already carries it; a new one that does not is a failure, not a nit.
- **Never add `aria-label` to silence a finding on a link that has visible text** — the
  label replaces the text for a screen reader, and then the link no longer says what it
  shows.
- **Roles are not a fix for semantics.** Prefer the element (`<button>`, `<nav>`,
  `<aside>`) over `role="..."` on a `<div>`.

## What it found the first time

**34 failures and 335 warnings over 542 pages**, and the warnings outnumber the failures
for a reason: the language defects are systematic, not local.

- **10 `<img>` tags carry no `alt`** — `WebDesign.html` is the clearest, an image with no
  text beside it and no description at all.
- **11 external links open a new tab without `rel="noopener"`**, all of them on
  `EthicalLawsOnIT.html`, which means the old `window.opener` handle is handed to every
  one of the eleven repositories it links.
- **2 pages repeat an `id`**: `FreeBSDReference.html` uses `quiz` twice, and `Voltage.html`
  repeats `screen-`, `screen-intro` and `screen-victory`, so `#screen-intro` jumps to
  whichever came first.
- **`ArtOfCreation.html` has no `lang` on `<html>`** at all.
- **21 pages contain Chinese text while the document declares `lang="en"`** —
  `DragonFire.html` and `aViragem.html` among them, where the Chinese is not decoration
  but half the poem.
- 335 warnings, mostly two families: a `<select>` or `<input>` with no label
  (`Chemistry.html`), and the bilingual pages whose language blocks carry no `lang`, so
  both languages are pronounced in the document's voice.

## After a run

```sh
python3 .agents/skills/a11y/check_a11y.py            # no failure
python3 .agents/skills/blog-ops/check_site.py        # one h1, one title, one canonical
```
