---
name: page-weight
description: Measure what a reader actually downloads per page — the HTML plus every local sheet, script, image and JSON it pulls in — against a budget per page class (article, catalogue, archive), and fail on the payloads that make the site slow. Use when adding a page, a catalogue data file, a PDF or a large image, or when a page feels heavy.
---

# Weight — what the browser pays

The size of `docs/` on disk is not the interesting number; a 58 MB folder of PDFs costs a
reader nothing until they open one. What costs is the **closure** of a page: its HTML plus
every local file it names, plus every JSON it fetches when it opens.

## The budgets

| Class | How it is recognised | HTML | Closure |
| --- | --- | --- | --- |
| article | everything not below | 512 KB | 1.5 MB |
| catalogue | `*Index.html`, `*_story.html` | 1.5 MB | 4 MB |
| archive | `docs/archive/**`, `docs/obsdRouter/**` | 4 MB | 8 MB |

A single asset over **2 MB** is a failure on its own, whichever page uses it — that rule
catches a catalogue JSON before its page does. Crossing 60% of a budget is a warning, so
the drift is visible before the failure.

## Commands

```sh
python3 .agents/skills/page-weight/check_weight.py            # summary + heaviest pages
python3 .agents/skills/page-weight/check_weight.py --top 25   # a longer list
python3 .agents/skills/page-weight/check_weight.py --json     # machine-readable
```

Exit code 0 when nothing is over budget, 1 when something is. Read-only: it writes no
file, and it is not a minifier.

## What it counts, precisely

`href` and `src` on the page, every candidate in a `srcset`, every `fetch("….json")`, and
any quoted `*.json` path the page names — local ones only, resolved against the page's own
directory. Remote files are somebody else's weight and are not counted, though a remote
sheet still delays the first paint.

## Rules

- **A breach is fixed by splitting, not by raising the budget.** `docs/awesome/data/*.json`
  is already partitioned by category for exactly this reason; keep new data in
  per-category files and fetch the one the reader asked for.
- **Never inline a large JSON into the page.** It moves the cost from a cacheable file to
  the HTML, which cannot be cached separately and is parsed on every visit.
- **A PDF is not a page.** It may be large, but it must not be linked from a page that
  also carries the whole catalogue; `target="_blank"` and a size hint in the anchor text
  are the honest treatment.
- **Budgets live at the top of `check_weight.py`.** Change them in one edit with a reason
  in the commit message, never per page.
- **Measure before and after.** A weight claim without a number on both sides is a guess.

## What it found the first time

**21 failures over 545 pages** (540 root pages plus the five archive ones), with 37.3 MB of
HTML in total:

- `docs/awesomeIndex.html` — **13.8 MB** of closure in 3 files, all of it the JSON it
  fetches at open: `index.json` 14 MB on disk, `languages.json` 2.8 MB,
  `plugins-for-the-deepseek-harness-dsh.json` 2.0 MB.
- `docs/awesome_story.html` — **10.2 MB of HTML**, seven times its catalogue budget.
- `docs/gameReference.html` — 2.7 MB of HTML plus 290 KB of assets.
- `docs/FBSD.html` — 2.5 MB of closure from five assets on a 25 KB page.
- Eight articles over 512 KB of HTML: `habitacao.html` 962 KB, `aViragem.html` 773 KB,
  `bashScripting.html` 734 KB, `pythonCert.html` 713 KB, `ccna_ccnp.html` 700 KB,
  `git.html` 654 KB, `autonomia.html` 613 KB, `mapQuest.html` 572 KB.
- `docs/pdfs/handbook_en.pdf` 23 MB and `debian-handbook.pdf` 22 MB, the two largest
  single files in the repository.

## After a run

```sh
python3 .agents/skills/page-weight/check_weight.py       # no page over budget
python3 .agents/skills/link-integrity/check_links.py     # and nothing it names is missing
```

A page can pass the budget and still be broken by a dead reference; the two audits answer
different questions and both belong before a publish.
