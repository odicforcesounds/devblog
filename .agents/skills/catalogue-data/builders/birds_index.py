#!/usr/bin/env python3
"""Recompute docs/birds/data/index.json from the per-order files.

Keeps the order/numbering already published and refreshes every count, so the
page stat line and the facet chips always describe the files beside them.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import sys

OUT = "docs/birds/data"
FACETS = ("habitat", "region", "trait", "status")


def main():
    index_path = os.path.join(OUT, "index.json")
    with open(index_path, encoding="utf-8") as fh:
        index = json.load(fh)

    facets = {name: {} for name in FACETS}
    species_total = photos = songs = statuses = 0
    families_seen = set()

    for group in index["groups"]:
        with open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8") as fh:
            payload = json.load(fh)
        birds = [bird for fam in payload["families"] for bird in fam["s"]]
        group["species"] = len(birds)
        group["families"] = len(payload["families"])
        group["photos"] = sum(1 for b in birds if b.get("i"))
        group["songs"] = sum(1 for b in birds if b.get("a"))
        group["statuses"] = sum(1 for b in birds if b.get("st"))
        species_total += len(birds)
        photos += group["photos"]
        songs += group["songs"]
        statuses += group["statuses"]
        for bird in birds:
            families_seen.add(bird.get("fam"))
            for value in bird.get("h", []):
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in bird.get("r", []):
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in bird.get("t", []):
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if bird.get("st"):
                facets["status"][bird["st"]] = facets["status"].get(bird["st"], 0) + 1

    index["species"] = species_total
    index["families"] = len(families_seen)
    index["orders"] = len(index["groups"])
    index["photos"] = photos
    index["songs"] = songs
    index["statuses"] = statuses
    index["facets"] = facets

    with open(index_path, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)

    print(json.dumps({k: v for k, v in index.items() if k != "groups"}, ensure_ascii=False)[:400])
    print("groups:", len(index["groups"]), "species:", species_total)
    print("trait kinds:", len(facets["trait"]), "| habitat kinds:", len(facets["habitat"]),
          "| region kinds:", len(facets["region"]), "| status kinds:", len(facets["status"]))


if __name__ == "__main__":
    sys.exit(main())
