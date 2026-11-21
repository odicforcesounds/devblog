#!/usr/bin/env python3
"""Append the dates of named pages to docs/api/dates.json.

The API is a database kept in JSON files, so adding a page inserts one record:
this script never regenerates the map. Every existing key is left as it is, the
new names are placed where the builder sorts them (`index.html` first, the rest
by name), and only `count` and `generated` move.

    python3 .agents/skills/blog-ops/append_dates.py                # every missing page
    python3 .agents/skills/blog-ops/append_dates.py Page.html      # the names given
    python3 .agents/skills/blog-ops/append_dates.py --dry-run      # report, write nothing

The instant is the first commit that added the file:
`git log --diff-filter=A --format=%aI -- docs/Page.html`, the same rule as the
page and the sitemap. A page git does not know yet is skipped and named — commit
it, then run this again. `404.html` and `home.html` are in no table.

`build_api.py` is not part of this: it rewrites the index of every page ever
written, and that index is never rebuilt to add one row.

Standard library only.
"""

import collections
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
DOCS = os.path.join(ROOT, "docs")
DATES = os.path.join(DOCS, "api", "dates.json")
SKIP = {"404.html", "home.html"}


def dump(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def first_commit(name):
    try:
        run = subprocess.run(
            ["git", "-C", ROOT, "log", "--diff-filter=A", "--format=%aI", "--",
             os.path.join("docs", name)],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    lines = [line.strip() for line in run.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def main(argv):
    dry = "--dry-run" in argv
    wanted = [a for a in argv if a != "--dry-run"]

    with open(DATES, encoding="utf-8") as fh:
        raw = fh.read()
    data = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    if dump(data) != raw:
        print("%s is not in the compact form this script writes — refusing to rewrite it"
              % os.path.relpath(DATES, ROOT))
        return 1

    published = data["published"]
    if wanted:
        names = []
        for arg in wanted:
            name = os.path.basename(arg.strip().replace("\\", "/"))
            if not name.endswith(".html"):
                name += ".html"
            if not os.path.exists(os.path.join(DOCS, name)):
                print("no such page in docs/: %s" % name)
                return 2
            if name in SKIP:
                print("%s is in no table — skipped" % name)
                continue
            names.append(name)
    else:
        names = sorted(n for n in os.listdir(DOCS)
                       if n.endswith(".html") and n not in SKIP and n not in published)

    added, present, unknown = [], [], []
    for name in names:
        if name in published:
            present.append(name)
            continue
        instant = first_commit(name)
        if not instant:
            unknown.append(name)
            continue
        published[name] = instant
        added.append((name, instant))

    if present:
        print("already in dates.json: %s" % ", ".join(sorted(present)))
    if unknown:
        print("not committed yet, nothing to date: %s" % ", ".join(sorted(unknown)))
    if not added:
        print("nothing to add: dates.json has %d entries" % len(published))
        return 0

    data["published"] = collections.OrderedDict(
        ([("index.html", published["index.html"])] if "index.html" in published else [])
        + sorted((k, v) for k, v in published.items() if k != "index.html"))
    data["count"] = len(data["published"])
    data["generated"] = max([data.get("generated", "")] + [v[:10] for v in published.values()])

    for name, instant in added:
        print("%s %s" % (instant, name))
    print("%s %d, count %d, generated %s"
          % ("would add" if dry else "added", len(added), data["count"], data["generated"]))
    if dry:
        return 0

    with open(DATES, "w", encoding="utf-8") as fh:
        fh.write(dump(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
