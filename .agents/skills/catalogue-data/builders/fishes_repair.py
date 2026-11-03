#!/usr/bin/env python3
"""Add the four organisms whose common names were disambiguation pages."""

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
import build_fishes as bf  # noqa: E402

OUT = bf.OUT

ALT = [
    ("Taeniura lymma", "ray", "Myliobatiformes", "Dasyatidae", "marine",
     ["reef", "seabed"], ["asia", "oceania"], ["venomous"]),
    ("Pecten maximus", "mollusc", "Pectinida", "Pectinidae", "marine",
     ["seabed", "coastal"], ["europe"], ["swimmer"]),
    ("Xestospongia muta", "sponge", "Haplosclerida", "Petrosiidae", "marine",
     ["reef", "seabed"], ["americas"], ["filter-feeder", "sessile"]),
    ("Stentor coeruleus", "protist", "Heterotrichida", "Stentoridae", "fresh",
     ["lake", "wetland"], ["worldwide"], ["trumpet-shaped"]),
]


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["sections"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {"group": group,
                                "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    added = 0
    for page, grp, order, family, salinity, zones, regions, traits in ALT:
        summary = bf.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                           urllib.parse.quote(page))
        if summary.get("__error__") or summary.get("type") in ("disambiguation", "no-extract"):
            print("  ! no article for", page)
            continue
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page))
        entry = {
            "n": summary.get("title") or page,
            "u": url,
            "d": bf.clean_extract(summary.get("extract") or ""),
            "z": zones, "r": regions, "t": traits, "w": salinity,
            "fam": family, "ord": order, "grp": grp,
        }
        thumb = bf.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bf.file_page(thumb)
        media = bf.fetch("https://en.wikipedia.org/api/rest_v1/page/media-list/" + urllib.parse.quote(page))
        for item in media.get("items", []):
            name = item.get("title", "")
            if item.get("type") == "audio" and name.lower().endswith((".ogg", ".oga", ".wav", ".mp3", ".flac")):
                entry["a"] = "https://commons.wikimedia.org/wiki/Special:FilePath/" + name.split(":", 1)[1]
                break
        qid = summary.get("wikibase_item")
        if qid:
            status, taxon, length, mass = bf.wikidata([qid])
            if qid in taxon:
                entry["s"] = taxon[qid]
            if qid in status:
                entry["st"] = status[qid]
            if qid in length:
                entry["l"] = length[qid]
            if qid in mass:
                entry["m"] = mass[qid]
        key = bf.slug(order)
        if key not in groups:
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": order,
                     "beings": 0, "families": 0, "photos": 0, "songs": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["sections"].append(fresh)
        groups[key]["families"].setdefault(family, []).append(entry)
        print("  +", entry["n"])
        added += 1
        time.sleep(1.5)

    facets = {"group": {}, "salinity": {}, "zone": {}, "region": {}, "trait": {}, "status": {}}
    total = photos = songs = statuses = 0
    for key, state in groups.items():
        beings = [b for fam in state["families"].values() for b in fam]
        for fam in state["families"]:
            state["families"][fam].sort(key=lambda b: b["n"])
        payload = {"key": key, "title": state["group"]["title"], "families": [
            {"n": fam, "c": len(state["families"][fam]), "s": state["families"][fam]}
            for fam in sorted(state["families"], key=lambda f: (-len(state["families"][f]), f))
        ]}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(beings)
        photos += sum(1 for b in beings if b.get("i"))
        songs += sum(1 for b in beings if b.get("a"))
        statuses += sum(1 for b in beings if b.get("st"))
        state["group"]["beings"] = len(beings)
        state["group"]["families"] = len(state["families"])
        state["group"]["photos"] = sum(1 for b in beings if b.get("i"))
        state["group"]["songs"] = sum(1 for b in beings if b.get("a"))
        for being in beings:
            facets["group"][being["grp"]] = facets["group"].get(being["grp"], 0) + 1
            facets["salinity"][being["w"]] = facets["salinity"].get(being["w"], 0) + 1
            for value in being["z"]:
                facets["zone"][value] = facets["zone"].get(value, 0) + 1
            for value in being["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in being["t"]:
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if being.get("st"):
                facets["status"][being["st"]] = facets["status"].get(being["st"], 0) + 1

    index["beings"] = total
    index["families"] = len({b["fam"] for state in groups.values()
                             for fam in state["families"].values() for b in fam})
    index["orders"] = len(groups)
    index["groups"] = len({b["grp"] for state in groups.values()
                           for fam in state["families"].values() for b in fam})
    index["photos"] = photos
    index["songs"] = songs
    index["statuses"] = statuses
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("added:", added)
    print("index:", {k: index[k] for k in ("beings", "families", "orders", "groups",
                                           "photos", "songs", "statuses")})


if __name__ == "__main__":
    main()
