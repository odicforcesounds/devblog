---
name: living-link
description: Put one random living being and one random tool on every page of this blog — a single quiet line near the footer, "this European robin likes to code with Bash", where the being links to the order it sits in inside one of the five catalogues and the tool links to the drawer of the Awesome Index that holds it, plus the guide on this site that expands on it when there is one. Use when the pages should carry that trail, when it needs reshuffling, or when it has to be taken out again.
---

# The living link — one being, one tool, every page

Every page ends with one sentence, set in the existing `.small` style:

```html
<p class="small living-link">this <a href="birdsIndex.html#order-pelecaniformes">Western cattle egret</a>
likes to code with <a href="awesomeIndex.html#cat-systems" title="API DevTools · Servers, containers
and self-hosting">Colossus</a>.</p>
```

and, when this blog already explains the tool somewhere:

```html
<p class="small living-link">this <a href="animalsIndex.html#order-cypriniformes">Common carp</a>
likes to code with <a href="awesomeIndex.html#cat-shell" title="Bash · Shell, terminal and
one-liners">Bash</a>, and this site has a <a href="bashScripting.html">Bash guide</a>.</p>
```

The point is the trail: a reader who lands on any article meets one creature and one tool, and
can follow either — into the catalogue that lists the creature, into the Awesome Index drawer
that holds the tool, and into the manual on this site that teaches the tool.

## The rules

- **One line per page, never more.** It is a footer note, not a section.
- **`awesome_story.html` is left alone.** Its text is read in parts by a menu, and a stray
  paragraph before its footer would break the reader. Redirect stubs (`http-equiv="refresh"`)
  are skipped too: nobody reads them.
- **The links must be ones the page does not already carry.** `page_hygiene.py` fails a page
  that repeats a target, so the being links to `index.html#order-<key>` (the order inside the
  catalogue, not the catalogue) and the tool to `awesomeIndex.html#cat-<key>` (the drawer, not
  the front page of the index). A page that already links the guide does not get a second one.
- **The being can go without a link, never with a duplicate.** If every catalogue is already
  linked on that page, the name is printed plain and the tool still carries the sentence.
- **Tools read as tools.** A list is used as the name only when it is the thing you code with
  (`Bash`, `Go`, `Rust`, `Docker`, …). Topic lists (`Music`, `Investing`, `Scalability`,
  `Cheat Sheets`) lend a real entry from inside them instead — a short `github.com` project
  name, one per list, chosen by a hash of the list so the site gets variety rather than the
  same first entry everywhere. One category is drawn first, then one tool inside it, because
  the drawers hold very different numbers of lists.
- **The guide is optional and real.** It is found by matching the tool name against a page's
  opening title word (`Bash: From Zero to Hero…`) or its camel-cased filename
  (`bashScripting.html`). No match, no third link — never invent one.
- **No JavaScript, no request, no CSS file.** The sentence is written into the HTML with the
  `.small` class that `article.css` already defines, so it survives a strict
  `Content-Security-Policy` and costs nothing at load time.
- **Reproducible.** Every page's pair is derived from the page name plus the seed, so two runs
  give the same site and `--seed` gives a different one.

## Running it

```sh
python3 .agents/skills/living-link/living.py            # every page
python3 .agents/skills/living-link/living.py --dry-run  # print counts, write nothing
python3 .agents/skills/living-link/living.py --seed 7   # reshuffle the whole site
python3 .agents/skills/living-link/living.py --page index.html
python3 .agents/skills/living-link/living.py --remove   # strip the line everywhere
```

It is idempotent: the old `<p class="small living-link">` is removed before the new one is
written, and a page whose pick does not change is left untouched. Placement is the end of the
page's `<footer>`; a page without a footer gets it just before `</body>`.

## Where the data comes from

| Part | Source |
| --- | --- |
| being | `docs/{birds,plants,animals,fishes,insects}/data/*.json` → `families[].s[].n`, linked to that catalogue plus `#order-<file key>` |
| tool | `docs/awesome/data/*.json` → list names and `lists[].d[].c[].n`, linked to `awesomeIndex.html#cat-<category key>` |
| guide | the page's `<title>` opening word or camel-cased filename, among `docs/*.html` |

Anchors were checked against the pages that build them: the catalogues name their sections
`order-<key>`, and `awesomeIndex.html` names its categories `cat-<key>`.

## Verifying

```sh
python3 .agents/skills/living-link/living.py --dry-run
grep -l 'class="small living-link"' docs/*.html | wc -l      # every page but the story
grep -c 'living-link' docs/awesome_story.html                # must be 0
python3 .agents/skills/blog-ops/check_site.py
python3 .agents/skills/blog-ops/page_hygiene.py docs/index.html docs/2FA.html
```

`page_hygiene.py` already reports duplicates that were there before this line existed
(`index.html` in toolbars, bandcamp links in a few articles); what matters is that no failure
mentions `#order-` or `#cat-`. To confirm the targets resolve, walk the pages and check that
each `#order-<key>` has its `docs/<catalogue>/data/<key>.json` and each `#cat-<key>` is a key in
`docs/awesome/data/index.json`.

The line is written into the pages, so it is part of the commit that touches them — no build
step has to run for it to appear. Rebuilding the API and the sitemap is not needed: the text
changes, the pages do not.
