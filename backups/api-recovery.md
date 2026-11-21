# Restoring `docs/api/` from git

`docs/api/` is the site's database and nothing rebuilds it. `dates.json` holds one row per
page, `index.json` one row per page that reads the API plus the chunk manifest, and
`text/NNN.json` the text rows themselves. A bad write — an empty file, a parse error, a row
that came back with the wrong instant — is repaired by restoring the smallest piece from a
revision. `build_api.py` is never the repair: it rewrites every row and the history of the
tables with it.

## 1. Say what is broken

```sh
python3 -c "import json; json.load(open('docs/api/dates.json'))" && echo "dates.json parses"
python3 -c "import json; json.load(open('docs/api/index.json'))" && echo "index.json parses"
python3 .agents/skills/blog-ops/append_dates.py --check   # names undated pages, reports order
```

`--check` reads only, never writes, and exits 1 when a page has no row or the map is out of
order. The chunk manifest is checked by size:

```sh
python3 - <<'PY'
import json
i = json.load(open("docs/api/index.json"))
for c in i["chunks"]:
    d = json.load(open("docs/api/" + c["file"]))
    print(c["file"], "rows", len(d), "of", c["count"], "bytes", c["bytes"])
    assert len(d) == c["count"], c["file"]
PY
```

## 2. Find the last revision that parses

```sh
for rev in $(git log --format=%h -- docs/api/index.json); do
  if git show "$rev:docs/api/index.json" 2>/dev/null | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    echo "$rev is the newest revision that parses"; break
  fi
done
```

Run the same loop with `docs/api/dates.json` or a single chunk. `git log --oneline -- <path>`
gives the commits that touched it; `git show <rev>:<path>` shows the bytes.

## 3. Restore the smallest thing

| Symptom | Restore |
| --- | --- |
| One name missing or holding a wrong instant, `dates.json` parses | `python3 .agents/skills/blog-ops/append_dates.py --restore Page.html` — takes the value from the last committed map, not from the first commit |
| `dates.json` empty or not JSON | `git show <rev>:docs/api/dates.json > docs/api/dates.json`, then `--check` |
| One article row missing, `index.json` parses | `python3 .agents/skills/blog-ops/append_dates.py --index Page.html` — re-adds the row and the page's text to the newest chunk |
| `index.json` empty or not JSON | `git show <rev>:docs/api/index.json > docs/api/index.json` |
| One text chunk damaged, the rest fine | `git show <rev>:docs/api/text/015.json > docs/api/text/015.json`, then re-check the manifest row |
| A whole file restored to fewer rows than the manifest says | take the chunk's `count` and `bytes` from the same revision as the chunk |

Never re-chunk the set and never renumber an existing chunk to make a file fit: those
files are rows other pages already read. A restore that changes `chunks` changes it back to
what that revision had.

## 4. Prove the restore

```sh
python3 .agents/skills/blog-ops/append_dates.py --check
git diff --numstat -- docs/api          # only the file you restored
python3 .agents/skills/blog-ops/check_site.py   # only when the author asks for the audit
```

When a commit broke a table, say which one in the report — `git log -S` on the row, or the
commit the loop above skipped past. A file is never emptied or rewritten to make a build
pass.
