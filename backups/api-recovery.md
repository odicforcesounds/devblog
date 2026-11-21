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
base = "docs/api/"
i = json.load(open(base + "index.json"))
for c in i["chunks"]:
    d = json.load(open(base + c["file"]))
    size = len(json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode())
    assert len(d) == c["count"], c["file"]
    assert size == c["bytes"], "%s: %d bytes, manifest says %d" % (c["file"], size, c["bytes"])
print(len(i["chunks"]), "chunks agree with the manifest")
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

`--restore` reads the map in `HEAD`, so it only undoes an edit that has not been committed.
A wrong value that is already in `HEAD` is not repaired that way — `HEAD` is then the wrong
source, and "good" is not a property of a commit you can see. A revision is usable when its
row for that page equals the instant of the first commit that added the page (or a value
someone decided by hand, for a copy or a rename). Test it before copying anything:

```sh
python3 - <<'PY'
import json, subprocess
rev, name = "HEAD", "Page.html"
row = json.loads(subprocess.run(["git", "show", rev + ":docs/api/dates.json"],
                                capture_output=True, text=True).stdout)["published"].get(name)
add = subprocess.run(["git", "log", "--diff-filter=A", "--format=%aI", "--", "docs/" + name],
                     capture_output=True, text=True).stdout.strip().splitlines()
print("%s %s: map %s | first add %s"
      % (rev, name, row, add[-1] if add else "(never added)"))
PY
```

The last line of that log is the first add, the same `tail -1` the script uses. Keep the
path exact: a log over all of `docs/` answers a different question than a log over one file,
and comparing the two produces mismatches that are not there. The page file must exist in
`docs/` before a row is restored: a deleted page comes back as a page
(`git show <rev>:docs/Page.html > docs/Page.html`), then as a row.

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

`--check` proves the shape of the map — it parses, it is in order, every page has a row — not
that an individual value is the right one. For a value, run the snippet in step 2 against the
revision it came from.

When a commit broke a table, say which one in the report — `git log -S` on the row, or the
commit the loop above skipped past. A file is never emptied or rewritten to make a build
pass.
