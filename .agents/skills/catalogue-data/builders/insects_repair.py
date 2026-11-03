#!/usr/bin/env python3
"""Add the twelve insects whose common names were disambiguation pages."""

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
import build_insects as bi  # noqa: E402

OUT = bi.OUT

ALT = [
    ("Lampyris noctiluca", "insect", "Coleoptera", "Lampyridae", "complete",
     ["grassland", "woodland"], ["europe", "asia"], ["bioluminescent"]),
    ("Vanessa atalanta", "insect", "Lepidoptera", "Nymphalidae", "complete",
     ["woodland", "urban"], ["europe", "asia", "americas"], ["migratory"]),
    ("Aglais io", "insect", "Lepidoptera", "Nymphalidae", "complete",
     ["woodland", "urban"], ["europe", "asia"], ["camouflage"]),
    ("Anthocharis cardamines", "insect", "Lepidoptera", "Pieridae", "complete",
     ["wetland", "woodland"], ["europe", "asia"], []),
    ("Morpho peleides", "insect", "Lepidoptera", "Nymphalidae", "complete",
     ["forest"], ["americas"], []),
    ("Calliphora vicina", "insect", "Diptera", "Calliphoridae", "complete",
     ["urban", "farmland"], ["worldwide"], ["decomposer", "indicator-species"]),
    ("Pantala flavescens", "insect", "Odonata", "Libellulidae", "incomplete",
     ["wetland", "grassland"], ["worldwide"], ["migratory", "aerial"]),
    ("Extatosoma tiaratum", "insect", "Phasmatodea", "Phasmatidae", "incomplete",
     ["forest"], ["oceania"], ["camouflage"]),
    ("Petrobius maritimus", "insect", "Archaeognatha", "Machilidae", "none",
     ["coastal"], ["europe"], ["cold-tolerant"]),
    ("Ixodes scapularis", "tick", "Ixodida", "Ixodidae", "none",
     ["forest", "woodland"], ["americas"], ["parasite"]),
    ("Scolopendra gigantea", "centipede", "Scolopendromorpha", "Scolopendridae", "none",
     ["forest"], ["americas"], ["predator", "venomous"]),
    ("Scutigera coleoptrata", "centipede", "Scutigeromorpha", "Scutigeridae", "none",
     ["urban"], ["europe", "asia", "americas"], ["predator"]),
]


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["sections"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {"group": group,
                                "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    added = 0
    for page, grp, order, family, meta, habitats, regions, roles in ALT:
        summary = bi.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                           urllib.parse.quote(page))
        if "__error__" in summary or summary.get("type") in ("disambiguation", "no-extract"):
            print("  ! no article for", page)
            continue
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page))
        entry = {
            "n": summary.get("title") or page,
            "u": url,
            "d": bi.clean_extract(summary.get("extract") or ""),
            "h": habitats, "r": regions, "t": roles,
            "m": meta, "fam": family, "ord": order, "grp": grp,
        }
        qid = summary.get("wikibase_item")
        if qid:
            status, taxon = bi.wikidata([qid])
            if qid in taxon:
                entry["s"] = taxon[qid]
            if qid in status:
                entry["st"] = status[qid]
        thumb = bi.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bi.file_page(thumb)
        key = bi.slug(order)
        if key not in groups:
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": order,
                     "beings": 0, "families": 0, "photos": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["sections"].append(fresh)
        groups[key]["families"].setdefault(family, []).append(entry)
        print("  +", entry["n"], "->", order)
        added += 1
        time.sleep(1.5)

    facets = {"group": {}, "metamorphosis": {}, "habitat": {}, "region": {},
              "role": {}, "status": {}}
    total = photos = statuses = 0
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
        statuses += sum(1 for b in beings if b.get("st"))
        state["group"]["beings"] = len(beings)
        state["group"]["families"] = len(state["families"])
        state["group"]["photos"] = sum(1 for b in beings if b.get("i"))
        for being in beings:
            facets["group"][being["grp"]] = facets["group"].get(being["grp"], 0) + 1
            facets["metamorphosis"][being["m"]] = facets["metamorphosis"].get(being["m"], 0) + 1
            for value in being["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in being["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in being["t"]:
                facets["role"][value] = facets["role"].get(value, 0) + 1
            if being.get("st"):
                facets["status"][being["st"]] = facets["status"].get(being["st"], 0) + 1

    index["sections"].sort(key=lambda s: (-s["beings"], s["title"]))
    for n, section in enumerate(index["sections"], 1):
        section["num"] = "%02d" % n
    index["beings"] = total
    index["families"] = len({b["fam"] for state in groups.values()
                             for fam in state["families"].values() for b in fam})
    index["orders"] = len(groups)
    index["groups"] = len({b["grp"] for state in groups.values()
                           for fam in state["families"].values() for b in fam})
    index["photos"] = photos
    index["statuses"] = statuses
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("added:", added)
    print("index:", {k: index[k] for k in ("beings", "families", "orders", "groups",
                                           "photos", "statuses")})


if __name__ == "__main__":
    main()
