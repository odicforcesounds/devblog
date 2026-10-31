---
name: tools-index
description: The path index for every tool this repository uses — the tracked build/audit scripts under .agents/skills/blog-ops/, the feed pipeline in docs/tools/, the page modules in docs/, the local scanner in tools/, the scratch scripts and harnesses in tmp/ (gitignored), and the external binaries (python3, node, git, ksh). Use when you need to know where a tool lives, which path to run, or where a new script should be put so it is reachable later.
---

# Tools — where every path is

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
| `.agents/skills/blog-ops/build_api.py` | Regenerates `docs/api/index.json`, `dates.json`, `text/NNN.json`. | `python3 .agents/skills/blog-ops/build_api.py` |
| `.agents/skills/blog-ops/build_sitemap.py` | Rebuilds `docs/sitemap.xml`; `--robots` rewrites `docs/robots.txt` only. | `python3 .agents/skills/blog-ops/build_sitemap.py [--robots]` |
| `.agents/skills/blog-ops/enrich_schema.py` | Rebuilds every page's JSON-LD `@graph`; idempotent. | `python3 .agents/skills/blog-ops/enrich_schema.py` |
| `docs/tools/build.mjs` | Inlines the feed data into `index.html`. | `node docs/tools/build.mjs` |
| `docs/tools/build_feeds.mjs` | Rebuilds `docs/tools/feeds.json` from the source list. | `node docs/tools/build_feeds.mjs` |
| `docs/tools/check_feeds.mjs` | Validates the feed data / generated blob. | `node docs/tools/check_feeds.mjs` |
| `docs/tools/parse_urls.mjs` | Parses the URL list into feed records. | `node docs/tools/parse_urls.mjs` |
| `docs/tools/shard_runner.sh` | Runs the feed pipeline in shards. | `sh docs/tools/shard_runner.sh` |
| `pushit.sh` | Deploy: pull, `git add .`, commit, push. **Only when asked to publish.** | `./pushit.sh` |
| `update.sh` | Pull only, through a fresh ssh-agent. | `./update.sh` |

Data and templates that travel with those scripts: `docs/tools/feeds.json`,
`docs/tools/template.html`, `docs/tools/shell.html`.

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

| Path | Tool |
| --- | --- |
| `tools/bg_scan.py` | Scans the archive for descriptions/titles/tags. Pins `os.chdir("/home/om/devblog/docs")`; fix it to resolve the root before reusing. |

## `tmp/` — scratch tools, gitignored

This is where most one-off work lives. `git check-ignore tmp/x.py` confirms it: nothing
here exists in a clone, nothing here is deployed, and nothing tracked may point at it.
Listed so a returning task can find its predecessor instead of rebuilding it.

**Bilingual editions (one file, `?lang=pt` block)** — each group is an extractor/builder
plus the Portuguese part files:

| Page | Paths |
| --- | --- |
| `OpenBSDTribute.html` | `tmp/build-openbsd-pt.py`, `tmp/openbsd-pt-block.html`, `tmp/openbsd-check.js` |
| `FreeBSDReference.html` | `tmp/splice-fbsd.py`, `tmp/fbsd-pt-1.js`, `tmp/fbsd-pt-2.js`, `tmp/fbsd-pt-3.js`, `tmp/fbsd-check.js`, `tmp/fbsd-render.js`, `tmp/FreeBSDReference.before.html` |
| `DebianSecurity.html` | `tmp/splice-debian.py`, `tmp/debian-pt.html`, `tmp/debian-script.js`, `tmp/debian-check.js`, `tmp/DebianSecurity.before.html` |
| `SELinuxTutorial.html` | `tmp/splice-selinux.py`, `tmp/selinux-pt.html`, `tmp/selinux-script.js`, `tmp/selinux-check.js` |
| `KaliLinux.html` | `tmp/kali/{extract.py,build.py,app.js,inline.js,pt-1.json,KaliLinux.en.html}` |
| `redhatCert.html` | `tmp/rhel/{extract-js.py,build.py,cp-en.json,cp-pt.json,pt-1.json,pt-2.json,pt-3.json,pt-fill.json,domtest/}` |
| `bashScripting.html` | `tmp/bash/{build.py,engine.js,pt-01.html…pt-10.html}` |
| Security manual | `tmp/splice-security.py`, `tmp/security-pt-1.html`, `tmp/security-pt-2.html`, `tmp/security-pt-3.html`, `tmp/Security.before.html` |
| Multiple languages | `tmp/i18n/{assemble.py,assemble2.py,clean.py,clean2.py,aut-*.html,hab-*.html}` |
| Single-language passes | `tmp/cli-pt.js`, `tmp/go-pt.js`, `tmp/rx-pt.js`, `tmp/tenda-pt.js`, `tmp/tenda-d.js`, `tmp/merge_lang.py`, `tmp/patch_langs.py` |

**Bulk page passes** — each rewrote many pages once, then was superseded by the commit:
`tmp/batch2.py` … `tmp/batch11.py`, `tmp/convert.py`, `tmp/cleanup_index.py`,
`tmp/gen_mapquest.py`, `tmp/repair_hab.py`, `tmp/repair_kali.py`,
`tmp/reorder-levels.py`, `tmp/fix-operador-commas.py`, `tmp/merge.py`,
`tmp/merge_game.py`, `tmp/add-linux-level.py`, `tmp/add-rust-level.py`,
`tmp/add-gns3-ccna.py`, `tmp/add_walkthrough.py`.

**Harnesses and page logic** — jsdom, fake Firebase, inlined module bodies:

| Path | Harness |
| --- | --- |
| `tmp/domtest/*.js` | Per-page DOM checks (`check-cli.js`, `check-go.js`, `check-rust.js`, `check-tents.js`, `cases-audit.js`, `lang*.js`). |
| `tmp/authtest/{test_comments_auth.mjs,test_hydroponics.mjs,node_modules/}` | Comment sign-in and hydroponics switcher, with jsdom installed. |
| `tmp/home/{test_home.mjs,test_404.mjs,test_debug.mjs,dbg404.mjs,module_check.mjs,page.html}` | `index.html` and `404.html` behaviour. |
| `tmp/game/{assemble.py,extract.js,engine.js,body.js,rules-*.json,civ,est,pen,tra}` | Builds the lawyer game from the rules data. |
| `tmp/ga.mjs`, `tmp/ga-check.mjs` | `gameAccount.js` module checks. |
| `tmp/game.js`, `tmp/game0.js`, `tmp/game1.js`, `tmp/game.inline.js`, `tmp/oJogo.js`, `tmp/operador-tail.html`, `tmp/rebuild-levels.js` | Operator game body/engine splicing. |
| `tmp/inline.js`, `tmp/index.inline.js`, `tmp/index-mod.mjs`, `tmp/check_lonely.js`, `tmp/rx-logic.js`, `tmp/rx-data.js`, `tmp/test_mapquest.js` | Inlining and per-feature checks. |
| `tmp/auth/{build_test.py,test.js,page.html}`, `tmp/seo/{apply_desc.py,check_all.js,check_dom.js,describe.py,h1_fix.py,node_modules/}` | Auth page prototype; description/`h1` audit passes. |
| `tmp/spec/*.json` | Per-article specifications used by the bulk passes. |

**Snapshots and data** — `.before*.html` / `.broken.html` copies for diffing a rewrite
(`index.before.html`, `oJogoDoOperador.broken.html`, …), plus `tmp/data.json`,
`tmp/out.txt`, `tmp/__pycache__/`. A snapshot dies once its page is committed.

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

# the scratch groups above — missing entries just mean tmp/ was pruned
ls tmp tmp/bash tmp/rhel tmp/kali tmp/domtest tmp/authtest 2>/dev/null

# a path named in this skill that no longer resolves (commands and bare names skipped)
grep -o '`[^`]*\.\(py\|sh\|js\|mjs\)`' .agents/skills/tools-index/SKILL.md | tr -d '`' |
  while read -r p; do
    case "$p" in *'*'*|*'{'*|*' '*|*'...'*) continue;; esac
    case "$p" in */*) [ -e "$p" ] || echo "missing: $p";; esac
  done
```
