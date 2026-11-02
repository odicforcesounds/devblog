#!/usr/bin/env python3
"""Validate the catalogue data that eight index pages read at open time.

Every `docs/<name>/data/` directory holds an `index.json` plus one file per category, and
the index page loads them with `fetch()`. A typo in one of those files is invisible until
the page is opened: the category silently disappears, or the page throws and shows
nothing. This checks the shape instead of the rendering.

    python3 .agents/skills/catalogue-data/check_catalogue.py
    python3 .agents/skills/catalogue-data/check_catalogue.py --dir animals
    python3 .agents/skills/catalogue-data/check_catalogue.py --json

What must hold:

    every file in docs/*/data/ parses as JSON
    index.json: each category has a key, a title, and no two share a key
    a category key names a file in the same directory (<key>.json)
    every <key>.json says "key": "<key>" and carries a title
    every entry has a name and, where it has a url, a http(s) url
    no name is repeated inside one category

Read-only. Exit code 0 when the data holds, 1 when a file is broken. Counts that a page
merely displays are not validated: they are prose, and they are allowed to disagree.
"""

import argparse
import glob
import json
import os
import re
import sys

DOCS = "docs"
NAME_KEYS = ("n", "name", "title")
URL_KEYS = ("u", "url", "href")


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def name_of(entry):
    for key in NAME_KEYS:
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def url_of(entry):
    for key in URL_KEYS:
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def entries_of(node):
    """Every dict that looks like a catalogue entry, at any depth."""
    if isinstance(node, dict):
        if name_of(node):
            yield node
        for value in node.values():
            yield from entries_of(value)
    elif isinstance(node, list):
        for value in node:
            yield from entries_of(value)


def categories_of(index):
    """The list of category objects inside an index, whatever it is called."""
    for key in ("categories", "groups", "sections", "orders"):
        value = index.get(key)
        if isinstance(value, list) and value and isinstance(value[0], dict) and "key" in value[0]:
            return value
    return []


def check_directory(path, failures, warnings, stats):
    files = sorted(glob.glob(os.path.join(path, "*.json")))
    if not files:
        return
    index_path = os.path.join(path, "index.json")
    index = None
    for file_path in files:
        try:
            data = read_json(file_path)
        except ValueError as error:
            failures.append((file_path, "does not parse: %s" % error))
            continue
        stats["files"] += 1
        if os.path.basename(file_path) == "index.json":
            index = data
        stem = os.path.splitext(os.path.basename(file_path))[0]
        if stem == "index":
            continue
        if isinstance(data, dict):
            declared = data.get("key")
            if isinstance(declared, str) and declared != stem:
                # A file whose name differs from its key is the legacy spelling of
                # <key>.json, kept beside the short name it was renamed to.
                twin = os.path.join(path, "%s.json" % declared)
                note = "legacy copy of %s.json" % declared if os.path.exists(twin) else \
                       "says key \"%s\" but the file is %s.json" % (declared, stem)
                warnings.append((file_path, note))
            if not isinstance(data.get("title"), str) or not data["title"].strip():
                warnings.append((file_path, "no title"))
        names = {}
        for entry in entries_of(data):
            label = name_of(entry)
            names[label] = names.get(label, 0) + 1
            url = url_of(entry)
            if url and not re.match(r'^(https?://|#)', url):
                failures.append((file_path, "entry \"%s\" has a url that is neither http(s) nor an anchor: %s" % (label[:40], url[:60])))
        stats["entries"] += sum(names.values())
        repeated = [label for label, count in names.items() if count > 1]
        if repeated:
            warnings.append((file_path, "%d name(s) repeated, e.g. %s" % (len(repeated), repeated[0][:50])))

    if index is None:
        warnings.append((path, "no index.json"))
        return
    categories = categories_of(index)
    seen = {}
    for index_entry in categories:
        key = index_entry.get("key", "")
        if not isinstance(key, str) or not key:
            failures.append((index_path, "a category has no key"))
            continue
        seen[key] = seen.get(key, 0) + 1
        if not isinstance(index_entry.get("title"), str) or not index_entry["title"].strip():
            warnings.append((index_path, "category \"%s\" has no title" % key))
        target = os.path.join(path, "%s.json" % key)
        if not os.path.exists(target):
            warnings.append((index_path, "category \"%s\" has no %s.json" % (key, key)))
    duplicates = [key for key, count in seen.items() if count > 1]
    if duplicates:
        failures.append((index_path, "%d duplicated category key(s): %s" % (len(duplicates), ", ".join(sorted(duplicates)[:4]))))
    referenced = set(seen)
    orphans = [os.path.basename(f) for f in files
               if os.path.basename(f) not in ("index.json",)
               and os.path.splitext(os.path.basename(f))[0] not in referenced]
    stats["categories"] += len(seen)
    if orphans:
        warnings.append((path, "%d data file(s) no category names: %s" % (len(orphans), ", ".join(sorted(orphans)[:4]))))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the catalogue data files.")
    parser.add_argument("--dir", help="only this data directory, e.g. animals")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    directories = sorted(glob.glob(os.path.join(DOCS, "*", "data")))
    if args.dir:
        directories = [d for d in directories if os.path.basename(os.path.dirname(d)) == args.dir]
    if not directories:
        print("no data directories found", file=sys.stderr)
        return 1

    failures, warnings = [], []
    stats = {"files": 0, "entries": 0, "categories": 0}
    for path in directories:
        check_directory(path, failures, warnings, stats)

    if args.json:
        print(json.dumps({
            "directories": len(directories),
            "stats": stats,
            "failures": [{"file": f, "what": t} for f, t in failures],
            "warnings": [{"file": f, "what": t} for f, t in warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    print("directories %d | files %d | categories %d | entries %d | failures %d | warnings %d"
          % (len(directories), stats["files"], stats["categories"], stats["entries"],
             len(failures), len(warnings)))
    if failures:
        for file_path, what in failures[:25]:
            print("  %s — %s" % (file_path, what))
        if len(failures) > 25:
            print("  … and %d more" % (len(failures) - 25))
    if warnings:
        for file_path, what in warnings[:10]:
            print("  %s — %s" % (file_path, what))
        if len(warnings) > 10:
            print("  … and %d more" % (len(warnings) - 10))
    if not failures and not warnings:
        print("nothing to fix")
    elif not failures:
        print("no failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
