---
name: new-page
description: Create a new page for Monkey Blog (blog.odicforcesounds.com) from scratch — one self-contained HTML file in docs/, dark theme, pure CSS3 and vanilla JavaScript, no external requests, Portuguese and English in the same page behind a coloured language switch at the top, a Home link back to index.html, one-word link text, sourced external references and subject-matched internal links — then compile (sitemap, API, audit). Use whenever a new article, manual or tool page is requested for this blog.
---

# New Page

Monkey Blog is a static site. `docs/` **is** the site: GitHub Pages serves it at
`https://blog.odicforcesounds.com`. There is no framework, no bundler and no request-time
rendering, so every rule below is a file rule — if it is wrong in the source, it is wrong
on the site.

This skill covers **creating a page**. The audit contract, sitemap/API builders and the
runbooks live in the `blog-ops` skill; load it too when a page touches an existing one.

## Non-negotiable rules

1. **One new file, written from scratch:** `docs/Name.html` (PascalCase or camelCase, like
   the neighbours). Do not clone an existing page and rewrite it — start from the skeleton
   in this skill and copy only patterns, never stale prose.
2. **No external resources.** No CDN, no Google Fonts, no `@import`, no remote images or
   SVG, no analytics. Everything inline in the file: `<style>` for CSS3, `<script>` for
   vanilla JavaScript (no libraries, no modules from a registry). Only local assets from
   `docs/images/`. Fonts are system stacks (`system-ui`, `Georgia`, `ui-monospace`, …).
   The one legacy exception in the repo is the Bandcamp iframe in
   `templates/dataDossier.html`; do not copy it into a new page.
3. **Dark theme, always.** Dark background, light ink, one accent plus one warm accent,
   declared as custom properties in `:root`. Never a light page, never a `prefers-color-scheme`
   branch that turns the page white.
4. **A Home link to `./index.html`**, in the top bar of the page (the footer may repeat it).
5. **Portuguese and English on the same page**, switched from a coloured language link at
   the top. Both languages complete — no "translation later", no placeholder text, no
   machine stub. A half-translated page is a defect.
6. **Short linking style:** the link text is one word — `Debian`, `OpenBSD`, `privacy`,
   `RFC 7231`. Never "click here", never a bare URL as the text.
7. **External references link the word** they support: when a sentence relies on an outside
   fact, that word becomes the link (`<a href="https://example.org/report">report</a>`), and
   the sources are collected in a closing section.
8. **Internal links must be about the same subject.** Before linking, open the candidate
   page and read its `<h1>`/`<h2>` — link what is genuinely related, not what merely shares
   a category. Three to eight such links per article.
9. **Colour the option links.** Anything the reader chooses — language pills, tabs, filters,
   game doors, next/previous steps — is styled as a control: accent border, accent fill when
   current, warm accent on hover/focus, visible `:focus-visible` outline. Plain underlined
   text is not an option link.
10. **Be extensive and organized:** kicker, one `<h1>`, a lede, a contents list, `h2`
    sections with real substance, tables where a comparison is clearer than prose, a closing
    and a sources section. A stub is only acceptable when the subject truly is short — and
    then say so instead of padding it.

## Where things live

| Path | What it is |
| --- | --- |
| `docs/*.html` | The pages. `index.html` is the archive, `404.html` the error page. |
| `docs/images/` | Icons and pictures (`svg`, `png`, `webp`). Reference them as `./images/name.svg`. |
| `docs/article.css`, `index.css`, `style.css` | Shared styles. A new page carries its own `<style>`. |
| `docs/sitemap.xml`, `docs/robots.txt` | Generated — never hand-edit. |
| `docs/api/index.json`, `docs/api/dates.json`, `docs/api/text/*.json` | Generated index, date map + text chunks. |
| `docs/tools/` | Feed pipeline for `index.html` (`feeds.json`, `build.mjs`, `template.html`). |
| `tools/` | Local build/scan scripts (`bg_scan.py`). **Gitignored** — nothing durable goes here. |
| `tmp/` | Scratch space for one-off scripts. **Gitignored.** |
| `templates/` | Starting points (`dataDossier.html`). |
| `.agents/skills/blog-ops/` | The audit and build scripts this page must satisfy. |
| `backups/` | Runbooks (Firebase, Google, Cloudflare). |
| `pushit.sh` | Deploy. Only run it when the user asks to publish. |

## The shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PAGE TITLE</title>
<meta name="description" content="110–155 characters, unique across the whole site.">
<link rel="canonical" href="https://blog.odicforcesounds.com/Name.html">
<meta property="og:title" content="PAGE TITLE">
<meta property="og:description" content="same text as the description">
<meta property="og:type" content="article">
<meta property="og:url" content="https://blog.odicforcesounds.com/Name.html">
<meta property="og:site_name" content="Monkey Blog">
<meta property="og:image" content="https://blog.odicforcesounds.com/images/peace.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="PAGE TITLE">
<meta name="twitter:description" content="same text as the description">
<meta name="twitter:image" content="https://blog.odicforcesounds.com/images/peace.jpg">
<link rel="icon" href="/favicon.ico" type="image/x-icon">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "https://blog.odicforcesounds.com/Name.html#article",
      "headline": "PAGE TITLE",
      "description": "same text as the description",
      "url": "https://blog.odicforcesounds.com/Name.html",
      "mainEntityOfPage": { "@type": "WebPage", "@id": "https://blog.odicforcesounds.com/Name.html" },
      "image": { "@type": "ImageObject", "url": "https://blog.odicforcesounds.com/images/peace.jpg", "width": 1496, "height": 960 },
      "inLanguage": "en",
      "author": { "@type": "Person", "name": "Oscar", "url": "https://blog.odicforcesounds.com/" },
      "publisher": {
        "@type": "Organization",
        "name": "Monkey Blog",
        "url": "https://blog.odicforcesounds.com/",
        "logo": { "@type": "ImageObject", "url": "https://blog.odicforcesounds.com/images/three.jpg", "width": 1024, "height": 1024 }
      },
      "isPartOf": { "@type": "Blog", "name": "Monkey Blog", "url": "https://blog.odicforcesounds.com/" },
      "articleSection": "CATEGORY AS WRITTEN ON index.html",
      "keywords": "the words that appear in the page's own h2/h3",
      "wordCount": 0,
      "datePublished": "YYYY-MM-DD",
      "dateModified": "YYYY-MM-DD"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://blog.odicforcesounds.com/" },
        { "@type": "ListItem", "position": 2, "name": "CATEGORY", "item": "https://blog.odicforcesounds.com/#category-category-slug" },
        { "@type": "ListItem", "position": 3, "name": "PAGE TITLE", "item": "https://blog.odicforcesounds.com/Name.html" }
      ]
    }
  ]
}
</script>
<style>
:root {
  --bg: #06090d;
  --panel: rgba(13, 20, 27, 0.88);
  --line: rgba(124, 227, 139, 0.16);
  --ink: #e6f1ec;
  --muted: #93a8a4;
  --accent: #7ce38b;
  --warm: #e9b26a;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.65 var(--sans); }
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--warm); }
/* … the page's own layout: header, main, sections, tables, footer … */
</style>
</head>
<body>

<nav class="lang-switch" aria-label="Language">
  <a href="?lang=pt" data-lang-switch="pt" lang="pt-PT">Português</a>
  <a href="?lang=en" data-lang-switch="en" aria-current="true" lang="en">English</a>
</nav>

<div id="lang-en" data-lang-block="en">
  <header>
    <a class="home" href="./index.html">Home</a>
    <h1>PAGE TITLE</h1>
  </header>
  <main><!-- English content --></main>
</div>

<div id="lang-pt" data-lang-block="pt" hidden>
  <header>
    <a class="home" href="./index.html">Início</a>
    <h2 class="seo-h2">TÍTULO</h2>
  </header>
  <main><!-- Portuguese content --></main>
</div>

<script>
/* language switch — see below */
</script>
</body>
</html>
```

## Bilingual layout

The repo has three historical shapes — know them so you recognise one, then pick the third:

- **English markup plus a Portuguese dictionary** applied to `data-i18n` nodes:
  `docs/hydroponics.html`, `docs/recycling.html`, `docs/python-cli.html`,
  `docs/rust-cli.html`, `docs/golang-cli.html`, `docs/tendas-manifestacao.html`.
- **`.langswitch` buttons** switching blocks with lang-prefixed anchors:
  `docs/povertyAndFaith.html`, `docs/ordersAndConscience.html`, `docs/memoryAtlas.html`,
  and the stripped-down `templates/dataDossier.html`.
- **Two language blocks** with one visible at a time: `docs/evilInNameOfGood.html`,
  `docs/buddhismManual.html`, and `docs/aViragem.html` for the Portuguese-first, JS-heavy case.

New pages use **two blocks**; do not invent a fourth shape.

Rules for the blocks:

- English is the document language (`<html lang="en">`) and the head language; the English
  block is first and visible, the Portuguese block follows with `hidden`.
- The switch lives **outside both blocks**, so it stays reachable in either language, and
  carries `data-lang-switch="pt|en"`; the current one has `aria-current="true"`.
- Every `id` inside the Portuguese block is prefixed `pt-`, and so is every reference to it
  (`href="#…"`, `for`, `aria-labelledby`, `aria-controls`) and every JavaScript lookup
  (`getElementById("pt-…")`, `querySelector("#pt-…")`). Otherwise the two copies collide.
- The Portuguese `<h1>` becomes `<h2 class="seo-h2">` — a document has exactly one `<h1>` —
  and the page's own `h1` declarations are copied onto `.seo-h2` so it looks unchanged.
- Any listener registered on `document` or `window` inside a block gates itself:
  `if (document.getElementById("lang-pt").hidden) { return; }`.
- A JS-heavy page boots the second language lazily (`window.__langBoot`) instead of running
  two engines at once; `docs/aViragem.html` is the worked example.
- `?lang=pt` and `#pt-…` deep links must open the Portuguese block.

### Switch, CSS

```css
.lang-switch {
  display: flex; justify-content: center; gap: 0.4rem;
  padding: 0.8rem 1rem 0.2rem;
  font-family: var(--mono); font-size: 0.72rem;
  letter-spacing: 0.18em; text-transform: uppercase;
}
.lang-switch a {
  padding: 0.32rem 0.95rem;
  color: var(--accent); font-weight: 600;
  background: transparent;
  border: 1px solid var(--accent); border-radius: 999px;
  opacity: 0.8;
  transition: opacity 150ms ease, background-color 150ms ease, color 150ms ease;
}
.lang-switch a[aria-current="true"] { color: var(--bg); background: var(--accent); opacity: 1; }
.lang-switch a:hover,
.lang-switch a:focus-visible { color: var(--bg); background: var(--warm); border-color: var(--warm); opacity: 1; }
[data-lang-block][hidden] { display: none !important; }
```

### Switch, JavaScript

```js
(function () {
  "use strict";
  var blocks = document.querySelectorAll("[data-lang-block]");
  var links = document.querySelectorAll("[data-lang-switch]");

  function apply(lang) {
    Array.prototype.forEach.call(blocks, function (block) {
      block.hidden = block.getAttribute("data-lang-block") !== lang;
    });
    Array.prototype.forEach.call(links, function (link) {
      if (link.getAttribute("data-lang-switch") === lang) { link.setAttribute("aria-current", "true"); }
      else { link.removeAttribute("aria-current"); }
    });
    document.documentElement.lang = lang === "pt" ? "pt-PT" : "en";
  }

  Array.prototype.forEach.call(links, function (link) {
    link.addEventListener("click", function (event) {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.button) { return; }
      event.preventDefault();
      apply(link.getAttribute("data-lang-switch"));
    });
  });

  var wanted = new URLSearchParams(location.search).get("lang");
  if (wanted === "en" || wanted === "pt") { apply(wanted); }
  else if (location.hash.indexOf("#pt-") === 0) { apply("pt"); }
})();
```

If the author wants Portuguese to be the page's primary language (as in `docs/aViragem.html`),
swap the positions: `<html lang="pt-PT">`, Portuguese head and block first, English second.
Nothing else in this skill changes.

## Content

- **Structure:** kicker → `<h1>` → lede → contents (`<nav>` with anchor links) → sections
  (`h2`, `h3` where needed) → closing → sources. Long pages get a sticky progress bar or a
  contents box; keep both CSS-only or a dozen lines of JS.
- **Substance per section:** a claim, the reasoning, and what it costs or changes. Tables for
  comparisons (distro vs package model, language vs use case), `<blockquote>` for a quote,
  a short list for steps. No filler paragraphs that repeat the heading.
- **Links:** one word of text. Internal → `./File.html`; external → the full `https://` URL in
  `href` and the word as text. Option links get the accent/warm styling and a focus outline.
- **Icons:** `./images/name.svg|png|webp`, with `alt=""` when decorative, `loading="lazy"`
  below the fold, `width`/`height` set to avoid layout shift.
- **Both languages say the same thing.** Translate the section headings and the table headers
  too, not only the body paragraphs.

## Put the page in the archive

Add exactly **one** row to `docs/index.html`, in the category it belongs to, inside the list
whose `data-lang` matches the page's primary language:

```html
<li><a href="./Name.html">Page Title</a><span>One line that says what the page is.</span><span class="name-tag">Name.html</span></li>
```

A bilingual page is listed once — never in both the English and the Portuguese list, because
the switch already carries the other language. Then:

- bump the `<h3 class="lang-head">` count for that list and the category's `<h2 … class="count">`;
- the page's date comes from git, not from the clock: commit the page, then rebuild the
  API so its `published_at` is that commit's instant — never edit a date by hand (see the
  `git-dates` skill);
- use the category's anchor (`#category-…`) in the JSON-LD breadcrumb;
- `articleSection` must be the category title exactly as written on `index.html`.

## Compile

Run all three, in this order, from the repository root:

```sh
python3 .agents/skills/blog-ops/build_sitemap.py    # sitemap.xml + robots.txt
python3 .agents/skills/blog-ops/build_api.py        # docs/api/index.json + dates.json + text chunks
python3 .agents/skills/blog-ops/check_site.py       # head contract, sitemap and API coverage
```

`check_site.py` must not report anything about the new page. The repository currently has
**two known-broken pages** — `ArtOfCreation.html` and `JS4Children.html`, each holding a
second pasted document — so a clean run still prints those two. Leave them alone here; any
other line is yours to fix before reporting the page as done.

Then prove the page itself:

```sh
# inline scripts must parse
python3 - <<'PY'
import re, subprocess, tempfile
src = open('docs/Name.html', encoding='utf-8').read()
for i, js in enumerate(m.group(2) for m in re.finditer(r'(?is)<script([^>]*)>(.*?)</script>', src)
                      if 'ld+json' not in m.group(1)):
    open('/tmp/s%d.js' % i, 'w', encoding='utf-8').write(js)
    print(i, 'ok' if subprocess.run(['node', '--check', '/tmp/s%d.js' % i]).returncode == 0 else 'SYNTAX ERROR')
PY

# only intended files moved
git diff --numstat

# no remote asset crept in (every https:// must be an <a href>, not src/@import/url())
grep -nE '(src=|url\(|@import)[^>]*https?://' docs/Name.html   # must print nothing

# serve and fetch
(cd docs && python3 -m http.server 8000) & sleep 1
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/Name.html   # expect 200
```

## Before saying it is done

- [ ] Doctype is the first byte of the file; no stray text before it.
- [ ] Exactly one `<title>`, one meta description (110–155 chars, unique on the site), one
      canonical, the full Open Graph and Twitter sets, one JSON-LD `@graph`, one `<h1>`.
- [ ] Dark theme, system fonts only, no external request anywhere in the file.
- [ ] Home link to `./index.html` present in the top bar.
- [ ] Language switch at the top, coloured, outside both blocks; switching works; `?lang=pt`
      opens Portuguese; every `id` in the Portuguese block is `pt-` prefixed and the script
      lookups match; no duplicate `id` in the document.
- [ ] Both languages complete and consistent; option links coloured; internal links verified
      by reading the target's headings; external sources linked on the word.
- [ ] Archive row added once, counts updated, breadcrumb matches, and the API
      `published_at` is the instant git reports for the file.
- [ ] `build_sitemap.py`, `build_api.py` and `check_site.py` run; no new failure.
- [ ] `git diff --numstat` shows only the new page, `index.html`, and the regenerated
      `sitemap.xml` / `api/*`.

## Gotchas that already cost time here

- Content before `<!DOCTYPE html>` throws the page into quirks mode — the layout breaks, not
  the audit only.
- Two `<h1>`s, or the same `id` twice (once per language block), break the audit and the
  page's own scripts.
- A Google Fonts link, a CDN script or a remote image silently violates the no-external-
  resources rule; the page must work offline from `docs/`.
- Copying an existing page's `<meta name="description">` fails the uniqueness check.
- `tools/` and `tmp/` are gitignored, so a script left there is not part of the project.
- `pushit.sh` runs `git add .` and deploys — never run it unasked, and never leave scratch
  files outside `tmp/`.
