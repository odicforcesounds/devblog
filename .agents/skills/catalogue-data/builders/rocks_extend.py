#!/usr/bin/env python3
"""Add the rock types the shelf lacks.

build_rocks.py reads Wikipedia's whole list once; this pass reads the finished
shelves, asks the API only for the names below, files each into its class and
A–Z band, and recomputes the counts. A rock already present is skipped, so a
second run changes nothing.

    python3 .agents/skills/catalogue-data/builders/rocks_extend.py
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import sys
import urllib.parse
import urllib.request

import build_rocks as br

OUT = br.OUT
API = br.IMAGE_API
UA = br.UA

# class key | rock name
EXTRA = [
    ("igneous", "Anorthosite"),
    ("igneous", "Troctolite"),
    ("igneous", "Nepheline syenite"),
    ("igneous", "Carbonatite"),
    ("igneous", "Kimberlite"),
    ("igneous", "Komatiite"),
    ("igneous", "Boninite"),
    ("igneous", "Pegmatite"),
    ("igneous", "Pumice"),
    ("igneous", "Tuff"),
    ("igneous", "Gabbro"),
    ("igneous", "Diorite"),
    ("igneous", "Rhyolite"),
    ("igneous", "Andesite"),
    ("igneous", "Pillow lava"),
    ("sedimentary", "Conglomerate (geology)"),
    ("sedimentary", "Breccia"),
    ("sedimentary", "Arkose"),
    ("sedimentary", "Greywacke"),
    ("sedimentary", "Mudstone"),
    ("sedimentary", "Siltstone"),
    ("sedimentary", "Dolomite (rock)"),
    ("sedimentary", "Chert"),
    ("sedimentary", "Flint"),
    ("sedimentary", "Gypsum"),
    ("sedimentary", "Rock salt"),
    ("sedimentary", "Ironstone"),
    ("sedimentary", "Oil shale"),
    ("sedimentary", "Coquina"),
    ("sedimentary", "Tufa"),
    ("sedimentary", "Travertine"),
    ("sedimentary", "Diatomite"),
    ("metamorphic", "Slate"),
    ("metamorphic", "Phyllite"),
    ("metamorphic", "Schist"),
    ("metamorphic", "Gneiss"),
    ("metamorphic", "Marble"),
    ("metamorphic", "Quartzite"),
    ("metamorphic", "Hornfels"),
    ("metamorphic", "Migmatite"),
    ("metamorphic", "Eclogite"),
    ("metamorphic", "Blueschist"),
    ("metamorphic", "Serpentinite"),
    ("metamorphic", "Amphibolite"),
    ("metamorphic", "Mylonite"),
    ("varieties", "Porphyry (geology)"),
    ("varieties", "Jasper"),
    ("varieties", "Agate"),
    ("varieties", "Onyx"),
    ("varieties", "Lapis lazuli"),
    ("varieties", "Oolitic limestone"),
]


def lookup(titles):
    found = {}
    for start in range(0, len(titles), 20):
        batch = titles[start:start + 20]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "extracts|pageimages|info", "exintro": 1, "explaintext": 1,
            "exsentences": 1, "exlimit": "max", "redirects": 1,
            "piprop": "thumbnail", "pithumbsize": "250", "inprop": "url",
            "titles": "|".join(batch),
        })
        request = urllib.request.Request(API + "?" + query, headers=UA)
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        payload = data.get("query", {})
        by_title = {page.get("title"): page for page in payload.get("pages", [])}
        alias = {}
        for item in payload.get("normalized", []) + payload.get("redirects", []):
            alias[item.get("from", "")] = item.get("to", "")
        for title in batch:
            key = alias.get(alias.get(title, title), title)
            page = by_title.get(key) or by_title.get(title)
            if not page or page.get("missing"):
                found[title] = None
                continue
            extract = (page.get("extract") or "").strip()
            extract = " ".join(extract.split())
            first = extract.split(". ")[0]
            if len(first) > 180:
                first = first[:177].rstrip() + "…"
            elif first and not first.endswith("."):
                first += "."
            thumb = (page.get("thumbnail") or {}).get("source", "")
            found[title] = {
                "n": page.get("title") or title,
                "u": page.get("fullurl") or ("https://en.wikipedia.org/wiki/" +
                                             urllib.parse.quote(title.replace(" ", "_"))),
                "d": first,
                "i": br.normal_thumb(thumb) if thumb else "",
            }
    return found


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    shelves = {}
    for entry in index["categories"]:
        doc = json.load(open(os.path.join(OUT, entry["key"] + ".json"), encoding="utf-8"))
        shelves[entry["key"]] = {
            "entry": entry, "doc": doc,
            "groups": {group["name"]: group["items"] for group in doc["groups"]},
        }

    existing = {item["n"].lower() for state in shelves.values()
                for items in state["groups"].values() for item in items}
    titles = []
    for _key, name in EXTRA:
        if name not in titles:
            titles.append(name)
    fetched = lookup(titles)
    for title in titles:
        if not fetched.get(title):
            print("  !", title, "not found")

    added = 0
    for key, name in EXTRA:
        item = fetched.get(name)
        if not item:
            continue
        if item["n"].lower() in existing:
            print("  =", item["n"], "already shelved")
            continue
        existing.add(item["n"].lower())
        state = shelves[key]
        band = br.BAND_NAMES[br.band(item["n"])]
        state["groups"].setdefault(band, []).append(item)
        added += 1
        print("  +", item["n"], "->", state["entry"]["title"], "/", band)

    total = photos = 0
    for key, state in shelves.items():
        doc = state["doc"]
        doc["groups"] = [
            {"name": name, "items": sorted(items, key=lambda item: item["n"].lower())}
            for name, items in state["groups"].items() if items
        ]
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as handle:
            json.dump(doc, handle, separators=(",", ":"), ensure_ascii=False)
        count = sum(len(group["items"]) for group in doc["groups"])
        found = sum(1 for group in doc["groups"] for item in group["items"] if item["i"])
        state["entry"]["rocks"] = count
        total += count
        photos += found
    index["rocks"] = total
    index["photos"] = photos
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, separators=(",", ":"), ensure_ascii=False)
    print("added:", added)
    print("index:", {"rocks": total, "photos": photos}, "shelves:", len(index["categories"]))


if __name__ == "__main__":
    sys.exit(main())
