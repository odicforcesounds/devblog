#!/usr/bin/env python3
"""Add the parts the published electronics catalogue is missing, nothing else.

The taxonomy in build_electronics.py is the source of truth for what belongs in
docs/electronics/data/. A full run of that builder rewrites every category, which
is more than an addition needs and can drop a page that has since been renamed.
This pass compares the taxonomy with the files on disk and fetches only the
titles that are not there yet:

  * a category with no file is written in full (10 microelectronics, 11 industrial)
  * a group missing from a category file is appended
  * an item whose article is not already in that category is appended

index.json is recomputed from the files afterwards. Running it twice changes
nothing.

    python3 .agents/skills/catalogue-data/builders/add_electronics_parts.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_electronics as be  # noqa: E402

OUT = be.OUT


def read(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=0)


def urls(doc):
    return {item.get("u") for group in doc["groups"] for item in group["items"]}


def taken_everywhere():
    """Every article already in the catalogue, in any category.

    The builder dedupes globally: an article named in two groups appears once, in
    the category that reaches it first. An addition has to honour that, or power
    gains a second Transformer already sitting in passives.
    """
    taken = set()
    for path in sorted(os.listdir(OUT)):
        if path.endswith("index.json") or not path.endswith(".json"):
            continue
        taken |= urls(read(os.path.join(OUT, path)))
    return taken


def main():
    wanted = []
    for key, _, _, _, groups in be.TAXONOMY:
        path = os.path.join(OUT, key + ".json")
        have = urls(read(path)) if os.path.exists(path) else set()
        for _, titles in groups:
            for title in titles:
                if title not in wanted:
                    wanted.append(title)
    fetched = be.fetch(wanted)
    missing = [title for title, page in fetched.items() if not page]
    for title in missing:
        print("  no article:", title)

    added = 0
    taken = taken_everywhere()
    for key, num, title, blurb, groups in be.TAXONOMY:
        path = os.path.join(OUT, key + ".json")
        doc = read(path) if os.path.exists(path) else {
            "key": key, "num": num, "title": title, "blurb": blurb, "groups": []}
        have = urls(doc)
        names = {group["name"]: group for group in doc["groups"]}
        before = sum(len(group["items"]) for group in doc["groups"])

        for name, titles in groups:
            group = names.get(name)
            if group is None:
                group = {"name": name, "items": []}
                doc["groups"].append(group)
                names[name] = group
            for item_title in titles:
                page = fetched.get(item_title)
                if not page or page["u"] in taken:
                    continue
                taken.add(page["u"])
                have.add(page["u"])
                group["items"].append(page)

        now = sum(len(group["items"]) for group in doc["groups"])
        if now != before or not os.path.exists(path):
            doc["groups"] = [group for group in doc["groups"] if group["items"]]
            write(path, doc)
            print("%-18s %3d -> %3d parts" % (key, before, now))
            added += now - before

    index_path = os.path.join(OUT, "index.json")
    index = read(index_path)
    known = {c["key"]: c for c in index["categories"]}
    total = groups_total = 0
    for key, num, title, blurb, groups in be.TAXONOMY:
        path = os.path.join(OUT, key + ".json")
        if not os.path.exists(path):
            continue
        doc = read(path)
        parts = sum(len(group["items"]) for group in doc["groups"])
        with_images = sum(1 for group in doc["groups"] for item in group["items"]
                          if item.get("t"))
        entry = known.get(key) or {
            "key": key, "num": num, "title": title, "blurb": blurb, "slug": key}
        entry.update({"components": parts, "groups": len(doc["groups"]),
                      "images": with_images})
        known[key] = entry
        total += parts
        groups_total += len(doc["groups"])
    index["categories"] = sorted(known.values(), key=lambda c: c["num"])
    index["components"] = total
    index["groups"] = groups_total
    write(index_path, index)

    print("parts added: %d | catalogue now %d parts in %d groups across %d categories"
          % (added, total, groups_total, len(index["categories"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
