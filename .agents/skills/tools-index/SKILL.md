---
name: tools-index
description: The path index for every tool this repository uses — the tracked build/audit scripts under .agents/skills/blog-ops/, the feed pipeline in docs/tools/, the page modules in docs/, the local scanner in tools/, the scratch scripts and harnesses in tmp/ (gitignored), and the external binaries (python3, node, git, ksh). Use when you need to know where a tool lives, which path to run, or where a new script should be put so it is reachable later.
---

# Tools — where every path is

**Run these checks and builds only when the author asks.** The audit scripts named here,
and `build_sitemap.py` / `build_api.py`, are not part of every task: finish the edit, say
which check would prove it, and run it when it is requested.

One job: given "the script that builds the API" or "the jsdom harness", answer with a
path you can run. `repo-layout` says which directory owns what; `tmp-tools` says how to
treat scratch. This file is the index itself.

Everything below is relative to the repository root. Never write an absolute path into a
script or a document: resolve the root from the file's own location.

```sh
ROOT="$(git rev-parse --show-toplevel)"
python3 .agents/skills/blog-ops/check_site.py
```

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]   # tmp/x.py or .agents/skills/<s>/x.py -> root
DOCS = ROOT / "docs"
```

## Tracked — these run on a fresh clone

| Path | Tool | Run it |
| --- | --- | --- |
| `.agents/skills/blog-ops/check_site.py` | Site audit: doctype, head tags, one `h1`, JSON-LD, description lengths, sitemap + API coverage. Exit 1 on failure. | `python3 .agents/skills/blog-ops/check_site.py` |
| `.agents/skills/blog-ops/page_hygiene.py` | Page content audit: duplicate `href` targets and repeated text blocks per language scope, HTML comments about the request/prompt. Exit 1 on findings. | `python3 .agents/skills/blog-ops/page_hygiene.py docs/Name.html` (`--all`, `--quiet`) |
| `.agents/skills/blog-ops/build_api.py` | Regenerates `docs/api/index.json`, `dates.json`, `text/NNN.json`. **Author-only — never run at the end of a task.** | `python3 .agents/skills/blog-ops/build_api.py` (on the author's request) |
| `.agents/skills/blog-ops/build_sitemap.py` | Rebuilds `docs/sitemap.xml`; `--robots` rewrites `docs/robots.txt` only. | `python3 .agents/skills/blog-ops/build_sitemap.py [--robots]` |
| `.agents/skills/blog-ops/enrich_schema.py` | Rebuilds every page's JSON-LD `@graph`; idempotent. | `python3 .agents/skills/blog-ops/enrich_schema.py` |
| `.agents/skills/blog-ops/restore_awesome_data.py` | Restores a shelf under `docs/awesome/data/` from git history when it stops being JSON; `--apply` writes. | `python3 .agents/skills/blog-ops/restore_awesome_data.py [--apply]` |
| `.agents/skills/blog-ops/fix_story.py` | Repairs the unclosed `h1`/`header` and the cramped column of `docs/awesome_story.html`; idempotent. | `python3 .agents/skills/blog-ops/fix_story.py` |
| `.agents/skills/living-panel/living_panel.py` | Writes the fixed living card, its style and its script tag into every page; `--remove` takes them out. | `python3 .agents/skills/living-panel/living_panel.py [--dry-run] [--page P]` |
| `.agents/skills/living-panel/build_living.py` | Rebuilds `docs/living-panel.js`, the pool the card rotates through on each load. | `python3 .agents/skills/living-panel/build_living.py` |
| `.agents/skills/living-panel/check_panel_links.py` | Reports pages where the card repeats a link the page already carries. | `python3 .agents/skills/living-panel/check_panel_links.py` |
| `.agents/skills/link-colors/link_colors.py` | Generates `docs/link-colors.css` and links it from every page except `index.html`; `--check` verifies, `--remove` takes the links out. | `python3 .agents/skills/link-colors/link_colors.py [--dry-run\|--check\|--remove]` |
| `.agents/skills/page-css/page_css.py` | Generates `docs/page.css` and swaps any `article.css` link for it; `--check` proves nothing still points at the old file. | `python3 .agents/skills/page-css/page_css.py [--dry-run\|--check]` |
| `.agents/skills/seo-indexation/check_seo.py` | Indexation audit: title length and uniqueness, description fit, canonical ↔ file name, noindex ↔ sitemap ↔ API, sitemap and robots consistency, JSON-LD date parity, internal-link count and reachability from `index.html`. Read-only. Exit 1 on findings. | `python3 .agents/skills/seo-indexation/check_seo.py` (`--quiet`, `--json`) |
| `.agents/skills/link-integrity/check_links.py` | Offline audit of every relative `href`/`src` on the root pages; `--external` HEADs a cached, sampled share of the 64k absolute links (`tmp/link-cache.json`). Read-only. Exit 1 on a dead link. | `python3 .agents/skills/link-integrity/check_links.py [--external --sample N]` |
| `.agents/skills/page-weight/check_weight.py` | Page weight against a budget per class (article 512 KB/1.5 MB, catalogue 1.5/4 MB, archive 4/8 MB), counting sheets, scripts, media and fetched JSON. Read-only. Exit 1 over budget. | `python3 .agents/skills/page-weight/check_weight.py` (`--top`, `--json`) |
| `.agents/skills/security-headers/check_headers.py` | Derives each page's required permissions from what it loads and checks its CSP against them, plus `nosniff`/`X-Frame-Options`/`Referrer-Policy`. Read-only. Exit 1 when a policy blocks its own page. | `python3 .agents/skills/security-headers/check_headers.py` (`--page`, `--json`) |
| `.agents/skills/a11y/check_a11y.py` | Alt text, document and block language, accessible link names, `rel=noopener`, duplicate ids, unlabelled controls, positive `tabindex`. Read-only. Exit 1 on failure. | `python3 .agents/skills/a11y/check_a11y.py` (`--page`, `--json`) |
| `.agents/skills/catalogue-data/check_catalogue.py` | Validates `docs/*/data/`: parse, category keys ↔ file names, declared key ↔ stem, http(s) URLs, duplicate names, orphan shelves. Read-only. Exit 1 on a broken file. | `python3 .agents/skills/catalogue-data/check_catalogue.py` (`--dir`, `--json`) |
| `.agents/skills/comments/check_firebase.py` | The two Firebase pages agree field by field, every written collection is named in `backups/firebase-rules.txt`, the chat keeps nothing in `localStorage`. Read-only. Exit 1 on divergence. | `python3 .agents/skills/comments/check_firebase.py` (`--json`) |
| `docs/tools/build.mjs` | Inlines the feed data into `index.html`. | `node docs/tools/build.mjs` |
| `docs/tools/build_feeds.mjs` | Rebuilds `docs/tools/feeds.json` from the source list. | `node docs/tools/build_feeds.mjs` |
| `docs/tools/check_feeds.mjs` | Validates the feed data / generated blob. | `node docs/tools/check_feeds.mjs` |
| `docs/tools/parse_urls.mjs` | Parses the URL list into feed records. | `node docs/tools/parse_urls.mjs` |
| `docs/tools/shard_runner.sh` | Runs the feed pipeline in shards. | `sh docs/tools/shard_runner.sh` |
| `.agents/skills/blog-ops/commitit.sh` | Interactive commit: asks about each changed file from `git status` and for that file's own message, then commits them one per commit — no push, no tool attribution. | `./.agents/skills/blog-ops/commitit.sh` (any cwd in the repo) |
| `pushit.sh` | Deploy: pull, `git add .`, commit, push. **Only when asked to publish.** | `./pushit.sh` |
| `update.sh` | Pull only, through a fresh ssh-agent. | `./update.sh` |

Data and templates that travel with those scripts: `docs/tools/feeds.json`,
`docs/tools/template.html`, `docs/tools/shell.html`.

## Builders — the one-shot scripts, now tracked

These came out of the gitignored `tmp/` so that a clone carries them. They are not audits:
each one produced data or pages once, and re-running it rebuilds that output. **Run from the
repository root**, because they open `docs/…` and `tmp/…` by relative path.

| Path | Wrote |
| --- | --- |
| `.agents/skills/catalogue-data/builders/build_animals.py` | `docs/animals/data/` |
| `.agents/skills/catalogue-data/builders/animals_repair.py` | two disambiguation names in the animal data |
| `.agents/skills/catalogue-data/builders/build_birds.py` | `docs/birds/data/` |
| `.agents/skills/catalogue-data/builders/repair_birds.py` | the bird species the first build lost to HTTP 429 |
| `.agents/skills/catalogue-data/builders/birds_index.py` | `docs/birds/data/index.json` counts and facets |
| `.agents/skills/catalogue-data/builders/build_fishes.py` | `docs/fishes/data/` |
| `.agents/skills/catalogue-data/builders/fishes_repair.py` | four disambiguation names in the fish data |
| `.agents/skills/catalogue-data/builders/build_insects.py` | `docs/insects/data/` |
| `.agents/skills/catalogue-data/builders/insects_repair.py` | twelve disambiguation names in the insect data |
| `.agents/skills/catalogue-data/builders/insects_groups.py` | five group articles swapped for species |
| `.agents/skills/catalogue-data/builders/build_plants.py` | `docs/plants/data/` |
| `.agents/skills/catalogue-data/builders/plants_edibility.py` | the edibility verdict on each plant |
| `.agents/skills/catalogue-data/builders/plants_fix.py` | second pass over those verdicts |
| `.agents/skills/catalogue-data/builders/build_electronics.py` | `docs/electronics/data/` |
| `.agents/skills/catalogue-data/builders/extract_tools.py` | `tmp/tools.json`, the input the awesome builders read |
| `.agents/skills/blog-ops/builders/build_awesome_json.py` | `docs/awesome/data/` |
| `.agents/skills/blog-ops/builders/build_deep.py` | the `docs/awesome-0N-*.html` category pages, since replaced by `docs/awesome/data/` |
| `.agents/skills/blog-ops/builders/build_shell_deep.py` | `docs/awesome-01-shell.html`, since replaced by `docs/awesome/data/shell.json` |
| `.agents/skills/blog-ops/builders/mkawesome.py` | `docs/awesomeIndex.html` (its `GROUPS` is the subject order) |
| `.agents/skills/blog-ops/builders/build_tools.py` | `docs/awesome-tools-*.html` |
| `.agents/skills/blog-ops/builders/build_awesome_story.py` | `docs/awesome_story.html` |
| `.agents/skills/blog-ops/builders/story_split.py` | the numbered story parts and their menu |
| `.agents/skills/blog-ops/builders/commit_drive.py` | `tmp/commit_answers.txt`, the answers `commitit.sh` reads |
| `.agents/skills/blog-ops/builders/extract-units.py`, `extract-sections.py`, `verify-pt.py` | `tmp/pythonCert.*.json` |
| `.agents/skills/blog-ops/builders/bilingual/extract.py` | `tmp/<slug>.units.json` for any bilingual article |
| `.agents/skills/blog-ops/builders/bilingual/verify.py` | checks the Portuguese block of that article against `tmp/<slug>.units.json` and `.pt.json` |

## Served, not run by you

Modules the pages `import`; edit them in place, they ship as-is:

| Path | Role |
| --- | --- |
| `docs/api.js` | `BlogAPI` — reads `docs/api/`, search over the text chunks. |
| `docs/article-lang.js` | The PT/EN switch shared by article pages. |
| `docs/gameAccount.js` | Firebase account + level comment panel for the games. |

## Read-only, third-party

`docs/archive/radios/download-radions.sh`, `docs/archive/security/cloneThemAll.sh` —
snapshot scripts kept for provenance. Do not run them, do not edit them, do not index
the pages around them.

## Local only — gitignored, may not exist on your machine

`tools/` is in `.gitignore` and **is not present**: it held a single script,
`bg_scan.py` — an archive scan for descriptions, titles and tags, pinned to
`os.chdir("/home/om/devblog/docs")` — and it was pruned. What it fed is now the read-only
audits in `.agents/skills/` (`seo-indexation`, `a11y`, `page-weight`). A local scanner that
is not a skill belongs here, never in `docs/`.

## `tmp/` — scratch, gitignored

`git check-ignore tmp/x.py` confirms it: nothing here exists in a clone, nothing here is
deployed, and nothing tracked may point at it. Since the builders moved to
`.agents/skills/*/builders/`, the directory holds what those scripts **read and write** —
inputs, caches, logs — plus the remains of earlier sessions.

| Path | What it is | Size |
| --- | --- | --- |
| `tmp/readmes/` | 114 awesome-list READMEs, the input `extract_tools.py` parses | 9.4 MB |
| `tmp/tools.json` | every tool those READMEs link, extracted; input of the awesome builders | 5.2 MB |
| `tmp/index_rescue/` | 26 `docs/awesome/data/` shelves copied out while that tree was rebuilt | 14 MB |
| `tmp/sections.json` | each list's own table of contents; read by `mkawesome.py` and `build_awesome_json.py` | |
| `tmp/plant_sections.json`, `tmp/plant_texts.json` | cached article sections and text, so `plants_edibility.py` re-runs offline | 4.2 MB |
| `tmp/pythonCert.{units,units2,pt,pt2…pt5}.json` | unit, section and Portuguese extracts for `docs/pythonCert.html` | |
| `tmp/git.{units,pt,pt2…pt11}.json` | the same for `docs/git.html` | |
| `tmp/{animals,birds,fishes,insects,plants}_build.log` | output of the catalogue builders | |
| `tmp/{animal,fish,plant,story}_script.js`, `tmp/story_test.js`, `tmp/check_awesome_render.js` | page logic extracted for inspection, and the story render check | |
| `tmp/inject-pt.mjs`, `tmp/reorder-levels.mjs`, `tmp/scaffold-bilingual.mjs`, `tmp/validate-game.mjs`, `tmp/bl/{extract,scaffold}.mjs` | language splice, level reorder, bilingual page scaffolder, game validator | |
| `tmp/awesome_story.before.html`, `tmp/oJogoDoOperador.{before,pristine}.html`, `tmp/pythonCert.orig.html` | pre-edit snapshots; each dies once its page is committed | |
| `tmp/commit_plan.txt`, `tmp/commit_answers.txt`, `tmp/commit_*.log` | the 550-file commit session: plan, script answers, run logs | |
| `tmp/seo/dates-v2.json` | a `name → date` map from an earlier audit | |

`tmp/__pycache__/` appears whenever a builder runs. Nothing is imported from here by
anything tracked; a missing file means a cache was pruned, and the builder that reads it
will fetch again.

## External binaries

Not in the repository; check before assuming a version:

```sh
command -v python3 node git ksh curl   # paths actually used
python3 --version                      # 3.13.5 on the machine this was written
node --version                         # v24.22.1
git --version                          # 2.55.0
```

`update.sh` and `pushit.sh` are `#!/bin/ksh`; use `./script` or `ksh script`, and
`ssh-add ~/.ssh/github` is assumed. jsdom for page tests comes from `node_modules/` inside
the matching `tmp/` harness — there is no project-wide install and no `package.json` at
the root.

## Adding a tool to the index

A new durable script belongs in `.agents/skills/blog-ops/` (a documented workflow) or the
repository root (a deploy helper) — never only in `tmp/` or `tools/`, which a clone does
not receive. Either way, add its row here in the same commit, so the next task finds it by
path instead of by memory. Scratch that runs once stays in `tmp/`; record it in the
matching group above only if it is worth reusing.

## Verify the index

```sh
# every tracked path this file names must exist
git ls-files | grep -E '(^|/)(pushit|update)\.sh$|\.agents/skills/blog-ops/|docs/tools/|docs/(api|article-lang|gameAccount)\.js$'

# the tmp inventory above — a missing entry means the cache was pruned
ls tmp tmp/bl tmp/readmes tmp/index_rescue tmp/seo 2>/dev/null

# a path named in this skill that no longer resolves (commands and bare names skipped)
grep -o '`[^`]*\.\(py\|sh\|js\|mjs\)`' .agents/skills/tools-index/SKILL.md | tr -d '`' |
  while read -r p; do
    case "$p" in *'*'*|*'{'*|*' '*|*'...'*) continue;; esac
    case "$p" in */*) [ -e "$p" ] || echo "missing: $p";; esac
  done
```
