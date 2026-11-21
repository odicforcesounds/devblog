#!/usr/bin/env python3
"""Insert the records of named pages into the files that hold the site's data.

The API is a database kept in JSON files, so adding a page inserts rows: this
script never regenerates a table. The date map is put in the builder's order
(`index.html` first, the rest by name) and the new names are placed in it; with
`--index` the same happens to the article table, the page's text joining the
newest chunk. No existing value changes, and only `count`, `generated` and that
chunk's `count`/`bytes` move.

    python3 .agents/skills/blog-ops/append_dates.py                     # missing dates
    python3 .agents/skills/blog-ops/append_dates.py Page.html           # the names given
    python3 .agents/skills/blog-ops/append_dates.py --index Page.html   # + article row, text
    python3 .agents/skills/blog-ops/append_dates.py --restore Page.html # instant from history
    python3 .agents/skills/blog-ops/append_dates.py --check             # report only, exit 1 on a gap
    python3 .agents/skills/blog-ops/append_dates.py --dry-run           # report, write nothing

The instant is the first commit that added that path
(`git log --diff-filter=A --format=%aI -- docs/Page.html`), the same rule as the
page and the sitemap. A page renamed inside docs/ keeps the date it already has
(OneHumanSong.html came from CommonCultures.html); a page copied from another
starts at the copy, which is why `--follow` is not used here. A value no commit
records — a seed from a build — is not a date: it moves to what git says. `--restore` prefers the value in the last committed
`docs/api/dates.json`, so a row whose instant was decided by hand (a copy or a
rename) comes back as it was, and a row whose value differs from that map is put
back. `--check` writes nothing: it names every page with
no row and says whether the map is in order, exiting 1 when either is wrong.
A page git does not know yet is skipped and named — commit it, then run this
again. `404.html` and `home.html` are in no table.

`build_api.py` is not part of this: it rewrites the index of every page ever
written, and that index is never rebuilt to add one row.

Standard library only.
"""

import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DOCS = os.path.join(ROOT, "docs")
DATES = os.path.join(DOCS, "api", "dates.json")
INDEX = os.path.join(DOCS, "api", "index.json")
SKIP = {"404.html", "home.html"}

sys.path.insert(0, HERE)
import build_api as builder  # the record shape must not drift from the page audit


def dump(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def ordered(rows):
    """The builder's order: the root page first, then every other page by name."""
    return collections.OrderedDict(
        ([("index.html", rows["index.html"])] if "index.html" in rows else [])
        + sorted((k, v) for k, v in rows.items() if k != "index.html"))


def git(*args):
    try:
        run = subprocess.run(["git", "-C", ROOT] + list(args),
                             capture_output=True, text=True)
    except OSError:
        return ""
    return run.stdout if run.returncode == 0 else ""


def commit_instant(args, name):
    out = git("log", *(list(args) + ["--format=%aI", "--", os.path.join("docs", name)]))
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def first_commit(name):
    return commit_instant(["--diff-filter=A"], name)


def last_commit(name):
    return commit_instant(["-1"], name)


def committed_dates():
    """The date map as the last commit has it, for `--restore`."""
    try:
        return json.loads(git("show", "HEAD:docs/api/dates.json"))["published"]
    except (ValueError, KeyError, TypeError):
        return {}


def all_pages():
    return sorted(n for n in os.listdir(DOCS) if n.endswith(".html") and n not in SKIP)


def article_records(names, instants):
    """The article row and the text of each page, in the builder's own shape."""
    records = []
    for name in names:
        with open(os.path.join(DOCS, name), encoding="utf-8") as fh:
            source = fh.read()
        slug = name[:-5]
        text = builder.body_text(source)
        fetched = builder.split_text(name)
        if fetched:
            text = (text + " " + fetched).strip()
        truncated = len(text) > builder.TEXT_CAP
        if truncated:
            text = text[:builder.TEXT_CAP]
        modified = last_commit(name) or instants[name]
        records.append(({
            "slug": slug,
            "url": "%s/%s.html" % (builder.ORIGIN, slug),
            "path": name,
            "title": builder.title_of(source) or slug,
            "description": builder.meta(source, "description"),
            "lang": builder.lang_of(source),
            "published": instants[name][:10],
            "modified": modified[:10],
            "published_at": instants[name],
            "modified_at": modified,
            "h1": (builder.headings(source, "h1", 1) or [""])[0],
            "headings": builder.headings(source, "h2", 10) + builder.headings(source, "h3", 6),
            "words": len(text.split()),
            "chars": len(text),
            "truncated": truncated,
        }, text, slug))
    return records


def stage_index(records):
    """The article table with those rows in place, and the newest chunk grown."""
    with open(INDEX, encoding="utf-8") as fh:
        index = json.load(fh)
    manifest = index.get("chunks") or []
    rel = manifest[-1]["file"] if manifest else "text/000.json"
    chunk_path = os.path.join(DOCS, "api", rel)
    chunk = {}
    if os.path.exists(chunk_path):
        with open(chunk_path, encoding="utf-8") as fh:
            chunk = json.load(fh)
    for _, text, slug in records:
        chunk[slug] = text

    fresh = {record["path"] for record, _, _ in records}
    articles = [a for a in index.get("articles") or [] if a.get("path") not in fresh]
    articles += [record for record, _, _ in records]
    articles.sort(key=lambda a: a.get("url", ""))
    index["articles"] = articles
    index["count"] = len(articles)
    if articles:
        index["generated"] = max(a.get("modified") or "" for a in articles)
    entry = {"file": rel, "count": len(chunk), "bytes": len(dump(chunk).encode("utf-8"))}
    index["chunks"] = (manifest[:-1] + [entry]) if manifest else [entry]
    return index, chunk_path, chunk


def main(argv):
    dry = "--dry-run" in argv
    check = "--check" in argv
    with_index = "--index" in argv
    restore = "--restore" in argv
    wanted = [a for a in argv if not a.startswith("--")]

    try:
        with open(DATES, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        print("docs/api/dates.json is missing — "
              "git show HEAD:docs/api/dates.json > docs/api/dates.json")
        return 1
    try:
        data = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    except ValueError as exc:
        print("docs/api/dates.json does not parse (%s) — "
              "git show HEAD:docs/api/dates.json > docs/api/dates.json" % exc)
        return 1
    if dump(data) != raw:
        print("%s is not in the compact form this script writes — refusing to rewrite it"
              % os.path.relpath(DATES, ROOT))
        return 1

    published = ordered(data["published"])
    reordered = list(published) != list(data["published"])
    if check:
        missing = [n for n in all_pages() if n not in published]
        if reordered:
            print("dates.json is not in the builder's order: index.html first, then by name")
        if missing:
            print("%d page%s with no date row: %s"
                  % (len(missing), "" if len(missing) == 1 else "s", ", ".join(missing)))
        if not reordered and not missing:
            print("dates.json: %d entries, in the builder's order, every page dated"
                  % len(published))
            return 0
        return 1
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
        names = [n for n in all_pages() if n not in published]

    history = committed_dates() if restore else {}
    added, restored, present, unknown = [], [], [], []
    for name in names:
        if name in published:
            if name in history and published[name] != history[name]:
                published[name] = history[name]
                restored.append((name, history[name]))
            else:
                present.append(name)
            continue
        instant = history.get(name) or first_commit(name)
        if not instant:
            unknown.append(name)
            continue
        published[name] = instant
        added.append((name, instant))

    with open(INDEX, encoding="utf-8") as fh:
        listed = {a.get("path") for a in json.load(fh).get("articles") or []}
    index_missing = [n for n in names if n not in listed] if with_index else []

    if present:
        print("already in dates.json: %s" % ", ".join(sorted(present)))
    if unknown:
        print("not committed yet, nothing to date: %s" % ", ".join(sorted(unknown)))
    if reordered:
        print("date map put in the builder's order: %d entries" % len(published))
    if not added and not restored and not reordered and not index_missing:
        print("nothing to add: dates.json has %d entries" % len(published))
        return 0

    data["published"] = ordered(published)
    data["count"] = len(data["published"])
    data["generated"] = max([data.get("generated", "")] + [v[:10] for v in published.values()])

    staged = None
    if index_missing:
        instants = {n: published[n] for n in index_missing}
        staged = stage_index(article_records(index_missing, instants))

    for name, instant in added:
        print("%s %s" % (instant, name))
    for name, instant in restored:
        print("restored from history: %s %s" % (instant, name))
    if staged:
        rel = os.path.relpath(staged[1], ROOT)
        print("article row%s added for %s, text into %s"
              % ("s" if len(index_missing) > 1 else "", ", ".join(sorted(index_missing)), rel))

    if dry:
        if added or restored or reordered:
            print("would write dates.json: %d added, %d restored, count %d, generated %s"
                  % (len(added), len(restored), data["count"], data["generated"]))
        if staged:
            print("would write index.json: count %d, text in %s"
                  % (staged[0]["count"], os.path.basename(staged[1])))
        return 0

    with open(DATES, "w", encoding="utf-8") as fh:
        fh.write(dump(data))
    if staged:
        index, chunk_path, chunk = staged
        with open(chunk_path, "w", encoding="utf-8") as fh:
            fh.write(dump(chunk))
        with open(INDEX, "w", encoding="utf-8") as fh:
            fh.write(dump(index))
    print("dates.json count %d, generated %s%s"
          % (data["count"], data["generated"],
             ", index.json count %d" % staged[0]["count"] if staged else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
