#!/usr/bin/env python3
"""Add the two species whose common names were disambiguation pages."""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, "tmp")
import build_animals as ba  # noqa: E402

OUT = ba.OUT

ALT = [
    ("Agalychnis callidryas", "amphibian", "Anura", "Hylidae",
     ["forest"], ["americas"], ["arboreal", "nocturnal"]),
    ("Scolopendra gigantea", "invertebrate", "Scolopendromorpha", "Scolopendridae",
     ["forest"], ["americas"], ["venomous"]),
]


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["groups"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {"group": group,
                                "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    titles = {a["u"].rsplit("/wiki/", 1)[-1] for state in groups.values()
              for fam in state["families"].values() for a in fam}
    added = 0
    for page, cls, order, family, habitats, regions, traits in ALT:
        slug = ba.slug(order)
        if slug in groups and family in groups[slug]["families"]:
            if any(page.replace("_", " ") in a["u"] for a in groups[slug]["families"][family]):
                continue
        summary = ba.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                           urllib.parse.quote(page))
        if summary.get("__error__") or summary.get("type") in ("disambiguation", "no-extract"):
            print("  ! no article for", page)
            continue
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page))
        entry = {
            "n": summary.get("title") or page,
            "u": url,
            "d": ba.clean_extract(summary.get("extract") or ""),
            "h": habitats, "r": regions, "t": traits,
            "fam": family, "ord": order, "cls": cls,
        }
        thumb = ba.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = ba.file_page(thumb)
        media = ba.fetch("https://en.wikipedia.org/api/rest_v1/page/media-list/" + urllib.parse.quote(page))
        for item in media.get("items", []):
            name = item.get("title", "")
            if item.get("type") == "audio" and name.lower().endswith((".ogg", ".oga", ".wav", ".mp3", ".flac")):
                entry["a"] = "https://commons.wikimedia.org/wiki/Special:FilePath/" + name.split(":", 1)[1]
                break
        qid = summary.get("wikibase_item")
        if qid:
            status, taxon, length, mass = ba.wikidata([qid])
            if qid in taxon:
                entry["s"] = taxon[qid]
            if qid in status:
                entry["st"] = status[qid]
            if qid in length:
                entry["l"] = length[qid]
            if qid in mass:
                entry["m"] = mass[qid]
        if slug not in groups:
            fresh = {"key": slug, "num": "%02d" % (len(groups) + 1), "title": order,
                     "animals": 0, "families": 0, "photos": 0, "songs": 0}
            groups[slug] = {"group": fresh, "families": {}}
            index["groups"].append(fresh)
        groups[slug]["families"].setdefault(family, []).append(entry)
        print("  +", entry["n"])
        added += 1
        time.sleep(1.5)

    facets = {"class": {}, "habitat": {}, "region": {}, "trait": {}, "status": {}}
    total = photos = songs = statuses = 0
    for key, state in groups.items():
        animals = [a for fam in state["families"].values() for a in fam]
        for fam in state["families"]:
            state["families"][fam].sort(key=lambda a: a["n"])
        payload = {"key": key, "title": state["group"]["title"], "families": [
            {"n": fam, "c": len(state["families"][fam]), "s": state["families"][fam]}
            for fam in sorted(state["families"], key=lambda f: (-len(state["families"][f]), f))
        ]}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(animals)
        photos += sum(1 for a in animals if a.get("i"))
        songs += sum(1 for a in animals if a.get("a"))
        statuses += sum(1 for a in animals if a.get("st"))
        state["group"]["animals"] = len(animals)
        state["group"]["families"] = len(state["families"])
        state["group"]["photos"] = sum(1 for a in animals if a.get("i"))
        state["group"]["songs"] = sum(1 for a in animals if a.get("a"))
        for animal in animals:
            facets["class"][animal["cls"]] = facets["class"].get(animal["cls"], 0) + 1
            for value in animal["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in animal["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in animal["t"]:
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if animal.get("st"):
                facets["status"][animal["st"]] = facets["status"].get(animal["st"], 0) + 1

    index["animals"] = total
    index["families"] = len({a["fam"] for state in groups.values()
                             for fam in state["families"].values() for a in fam})
    index["orders"] = len(groups)
    index["classes"] = len({a["cls"] for state in groups.values()
                            for fam in state["families"].values() for a in fam})
    index["photos"] = photos
    index["songs"] = songs
    index["statuses"] = statuses
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("added:", added)
    print("index:", {k: index[k] for k in ("animals", "families", "orders", "classes",
                                           "photos", "songs", "statuses")})


if __name__ == "__main__":
    main()
