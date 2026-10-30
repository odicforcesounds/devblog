---
name: tmp-tools
description: Manage the scripts and scratch files of this repository — what belongs in tmp/ (one-off scripts, .orig.html snapshots, harnesses), what belongs in tools/ (local scanners), why both are gitignored, when a script must be promoted into .agents/skills/blog-ops/, and how to audit and clean the pile without losing the work it represents. Use when adding, reusing, moving or pruning scripts in this repository.
---

# tmp/ and tools/ — scripts and scratch

Neither directory is in git. `.gitignore` lists `tmp/` and `tools/`, so a file there is
invisible to `git status`, absent from a fresh clone, and never deployed. That is the point
(scratch must not ship) and the trap (work can vanish). Decide which one you are doing
before writing the first line.

## What is there today

| Path | Holds | Count |
| --- | --- | --- |
| `tools/bg_scan.py` | Local scan of the archive (descriptions, titles, tags). | 1 |
| `tmp/*.orig.html` | Pre-edit snapshots (`2FA.orig.html`, `4yfn.orig.html`, …). | 4 |
| `tmp/*.py` | Bulk passes: `batch2.py`…`batch11.py`, `merge*.py`, `patch_*.py`, `repair_hab.py`, `cleanup_index.py`, `convert.py`, `gen_mapquest.py`. | 19 |
| `tmp/*.js` | Page harnesses and language data (`cli-pt.js`, `rx-logic.js`, `test_mapquest.js`). | 10 |
| `tmp/*.html` | Language variants and merged drafts (`cli-a.html`, `merged.html`, `tenda-*.html`). | 22 |
| `tmp/{auth,authtest,domtest,game,home,i18n,seo,spec}/` | Harness and data sets used by earlier tasks. | 9 dirs |

The scripts are history, not a library: each one encoded one edit. They are not imported by
anything, and nothing tracked may depend on them.

## Rules

1. **One-off work goes to `tmp/`.** A script that rewrites 40 pages runs once; keeping it in
   `tmp/` is correct, and deleting it afterwards is also correct — git already has the
   result. Give it a name that says what it did (`patch_langs.py`, not `script2.py`).
2. **Anything referenced by a tracked document lives in a tracked path.** `README.md` and
   the skills tell a reader to run `python3 .agents/skills/blog-ops/build_api.py`: any script
   a document depends on must live outside `tools/`, which is gitignored:
   on a fresh clone that file does not exist. A durable script belongs in
   `.agents/skills/blog-ops/` (or the repository root), where it is committed.
3. **A script another skill needs must be committed**, next to the `SKILL.md` that names it —
   that is why `check_site.py`, `build_sitemap.py` and `enrich_schema.py` sit in
   `.agents/skills/blog-ops/`.
4. **Idempotence is the price of a bulk script.** Running it twice must produce the same
   files; otherwise a retry after an error corrupts the archive. Prove it before reporting
   (`git diff --numstat` empty on the second run).
5. **Snapshots are temporary.** A `*.orig.html` copy exists to diff and to recover a body
   that a rewrite destroyed. Once the result is verified and committed, the snapshot is
   dead weight — delete it, or move a genuinely valuable one to `backups/`.
6. **No absolute paths in scripts.** `tools/bg_scan.py` currently does
   `os.chdir("/home/om/devblog/docs")`, which pins it to one machine. New scripts resolve
   the repository root from `__file__`:

   ```python
   from pathlib import Path
   ROOT = Path(__file__).resolve().parents[2]   # tmp/x.py -> repo root
   DOCS = ROOT / "docs"
   ```

7. **Never point a tracked file at `tmp/`.** A link, an import or a documented command that
   starts with `tmp/` breaks on every other machine. The exception is a note that says the
   harness must be recreated (the comment sign-in tests in `blog-ops` do exactly that).
8. **No secrets in either directory.** `tmp/` is still on disk and gets copied around;
   tokens, keys and private URLs belong in the environment, not in a scratch script.

## Audit and clean

```sh
# inventory, newest first — the top of the list is what a past task left behind
ls -lt tmp | head -20
ls -lt tools

# how big the scratch pile is
du -sh tmp tools

# scripts nothing refers to (safe to delete once the task is committed)
grep -rn "tmp/" --include='*.md' --include='*.html' --include='*.py' \
  --exclude-dir=tmp --exclude-dir=free . | head

# snapshots whose page has already been committed
for f in tmp/*.orig.html; do
  page="docs/$(basename "$f" .orig.html).html"
  [ -f "$page" ] || echo "orphan snapshot: $f"
done

# does the build script the docs name actually exist?
ls -l .agents/skills/blog-ops/*.py
```

## When something in tmp/ becomes permanent

Promote it, do not copy the habit:

1. Move the file to `.agents/skills/<skill>/` (or root for a deploy helper).
2. Change hardcoded paths to repository-relative ones.
3. Make it idempotent and give it `--check`/dry-run behaviour if it edits pages.
4. Name it in the owning `SKILL.md`, with the command and the expected output.
5. Run it once more from a clean shell, then `git status` — the promoted file and only it
   should be new.

Deleting scratch is safe **after** the change it produced is committed: `git log` and
`git show` are the backup. Before that, keep it.
