#!/usr/bin/env python3
"""Add the insect orders and arachnid, myriapod and woodlouse species the shelf lacks.

build_insects.py writes the whole catalogue from scratch; this pass reads the
finished shelves, fetches only the rows below, files each under its order and
family, and recomputes counts and facets without touching a being that is
already there. Safe to run twice: an article already present is skipped.

    python3 .agents/skills/catalogue-data/builders/insects_extend.py
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import re
import sys
import time
import urllib.parse

import build_insects as bi

OUT = bi.OUT

# Articles for whole orders or families that earlier runs filed as if they were species.
DROP = {"Mecoptera", "Psocoptera", "Embioptera", "Chrysopidae"}

# title | group | order | family | metamorphosis | habitats | regions | roles
EXTRA = """
Mayfly|insect|Ephemeroptera|Ephemeridae|incomplete|river,lake|worldwide|indicator-species
Caddisfly|insect|Trichoptera|Limnephilidae|complete|river,lake|worldwide|builder,indicator-species
Chrysoperla carnea|insect|Neuroptera|Chrysopidae|complete|farmland,urban|worldwide|predator
Antlion|insect|Neuroptera|Myrmeleontidae|complete|desert,woodland|worldwide|predator,burrower
Dobsonfly|insect|Megaloptera|Corydalidae|complete|river,woodland|americas,asia|predator
Alderfly|insect|Megaloptera|Sialidae|complete|river,wetland|europe,asia,americas|
Snakefly|insect|Raphidioptera|Raphidiidae|complete|woodland|europe,asia,americas|predator
Panorpa communis|insect|Mecoptera|Panorpidae|complete|woodland,grassland|europe,asia|
Liposcelis bostrychophila|insect|Psocodea|Liposcelididae|incomplete|urban|worldwide|pest
Oligotoma saundersii|insect|Embioptera|Oligotomidae|incomplete|forest,urban|asia,africa,americas|builder
Stylops|insect|Strepsiptera|Stylopidae|complete|farmland,grassland|worldwide|parasite
Campodea|insect|Diplura|Campodeidae|none|woodland,farmland|worldwide|
Acerentomon|insect|Protura|Acerentomidae|none|woodland,farmland|worldwide|
Zorotypus|insect|Zoraptera|Zorotypidae|incomplete|forest|americas,asia,africa|social
Grylloblatta campodeiformis|insect|Notoptera|Grylloblattidae|incomplete|alpine|americas|cold-tolerant
Western flower thrips|insect|Thysanoptera|Thripidae|incomplete|farmland,urban|worldwide|pest
Mormon cricket|insect|Orthoptera|Tettigoniidae|incomplete|grassland|americas|pest
Corixa punctata|insect|Hemiptera|Corixidae|incomplete|wetland,lake|europe,asia|
Pond skater|insect|Hemiptera|Gerridae|incomplete|wetland|worldwide|surface-tension
Horse fly|insect|Diptera|Tabanidae|complete|wetland,grassland|worldwide|parasite
Bee fly|insect|Diptera|Bombyliidae|complete|grassland,urban|worldwide|pollinator
Tiger beetle|insect|Coleoptera|Cicindelidae|complete|grassland,woodland|worldwide|predator
Rove beetle|insect|Coleoptera|Staphylinidae|complete|woodland,farmland|worldwide|predator
Click beetle|insect|Coleoptera|Elateridae|complete|woodland,farmland|worldwide|
Soldier beetle|insect|Coleoptera|Cantharidae|complete|woodland,grassland|worldwide|predator
Cecropia moth|insect|Lepidoptera|Saturniidae|complete|forest|americas|
Comet moth|insect|Lepidoptera|Saturniidae|complete|forest|africa|
Pararge aegeria|insect|Lepidoptera|Nymphalidae|complete|woodland,urban|europe,asia,africa|
Sawfly|insect|Hymenoptera|Tenthredinidae|complete|woodland,farmland|worldwide|pest
Sphex ichneumoneus|insect|Hymenoptera|Sphecidae|complete|grassland,urban|americas|predator,burrower
Halictus ligatus|insect|Hymenoptera|Halictidae|complete|farmland,urban|americas|pollinator
Blue dasher|insect|Odonata|Libellulidae|incomplete|wetland|americas|predator
Willow emerald damselfly|insect|Odonata|Lestidae|incomplete|wetland|europe,asia|
Oriental cockroach|insect|Blattodea|Blattidae|incomplete|urban|worldwide|pest
Chinese mantis|insect|Mantodea|Mantidae|incomplete|grassland,urban|asia,americas|predator
Carausius morosus|insect|Phasmatodea|Lonchodidae|incomplete|forest,urban|asia|camouflage
Oniscus asellus|woodlouse|Isopoda|Oniscidae|na|woodland,urban|europe|decomposer
Porcellio scaber|woodlouse|Isopoda|Porcellionidae|na|urban,woodland|worldwide|decomposer
Sydney funnel-web spider|spider|Araneae|Atracidae|na|forest,urban|oceania|venomous
Brazilian wandering spider|spider|Araneae|Ctenidae|na|forest,urban|americas|venomous
Peacock spider|spider|Araneae|Salticidae|na|desert,woodland|oceania|
Spiny orb-weaver|spider|Araneae|Araneidae|na|forest,urban|americas,asia|silk
Androctonus australis|scorpion|Scorpiones|Buthidae|na|desert|africa,asia|venomous
Giant forest scorpion|scorpion|Scorpiones|Scorpionidae|na|forest|asia|predator,burrower
Scabies mite|mite|Sarcoptiformes|Sarcoptidae|na|urban|worldwide|parasite
Demodex|mite|Trombidiformes|Demodicidae|na|urban|worldwide|parasite
Chigger|mite|Trombidiformes|Trombiculidae|na|grassland,woodland|worldwide|parasite
Lone star tick|tick|Ixodida|Ixodidae|na|woodland,grassland|americas|parasite
Leiobunum rotundum|harvestman|Opiliones|Sclerosomatidae|na|woodland,urban|europe|scavenger
Lithobius forficatus|centipede|Lithobiomorpha|Lithobiidae|na|woodland,urban|europe,americas|predator
Geophilus|centipede|Geophilomorpha|Geophilidae|na|farmland,woodland|worldwide|predator
Tachypodoiulus niger|millipede|Julida|Julidae|na|woodland|europe|decomposer
Narceus americanus|millipede|Spirobolida|Spirobolidae|na|forest|americas|decomposer
Polyxenus lagurus|millipede|Polyxenida|Polyxenidae|na|woodland,urban|europe|decomposer
Sminthurus viridis|springtail|Symphypleona|Sminthuridae|none|farmland,grassland|worldwide|pest
"""


def rows():
    out = []
    for line in EXTRA.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        bits += [""] * (8 - len(bits))
        out.append({
            "title": bits[0], "grp": bits[1], "order": bits[2], "family": bits[3],
            "meta": bits[4],
            "habitats": [h for h in bits[5].split(",") if h],
            "regions": [r for r in bits[6].split(",") if r],
            "roles": [r for r in bits[7].split(",") if r],
        })
    return out


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for section in index["sections"]:
        payload = json.load(open(os.path.join(OUT, section["key"] + ".json"), encoding="utf-8"))
        families = {fam["n"]: [being for being in fam["s"] if being["n"] not in DROP]
                    for fam in payload["families"]}
        groups[section["key"]] = {"group": section,
                                  "families": {name: beings for name, beings in families.items() if beings}}

    existing = {being["u"] for state in groups.values()
                for family in state["families"].values() for being in family}
    resolved = []
    for row in rows():
        summary = bi.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                           urllib.parse.quote(row["title"].replace(" ", "_")))
        if "__error__" in summary or summary.get("type") in ("disambiguation", "no-extract"):
            print("  !", row["title"], "->", summary.get("__error__", summary.get("type", "missing")))
            continue
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(row["title"].replace(" ", "_")))
        if url in existing:
            print("  =", row["title"], "already shelved")
            continue
        existing.add(url)
        resolved.append((row, summary, url))
        time.sleep(0.4)

    qids = [summary.get("wikibase_item") for _, summary, _ in resolved if summary.get("wikibase_item")]
    status, taxon = bi.wikidata(qids) if qids else ({}, {})

    added = 0
    for row, summary, url in resolved:
        qid = summary.get("wikibase_item")
        entry = {
            "n": summary.get("title") or row["title"],
            "u": url,
            "d": bi.clean_extract(summary.get("extract") or ""),
            "h": row["habitats"], "r": row["regions"], "t": row["roles"],
            "m": row["meta"], "fam": row["family"], "ord": row["order"], "grp": row["grp"],
        }
        if qid:
            if qid in taxon:
                entry["s"] = taxon[qid]
            if qid in status:
                entry["st"] = status[qid]
        if not entry.get("s"):
            binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
            if binomial:
                entry["s"] = binomial.group(1)
        thumb = bi.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bi.file_page(thumb)
        key = bi.slug(row["order"])
        if key not in groups:
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": row["order"],
                     "beings": 0, "families": 0, "photos": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["sections"].append(fresh)
        groups[key]["families"].setdefault(row["family"], []).append(entry)
        added += 1
        print("  +", entry["n"], "->", row["order"])
    print("added:", added)

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
    for position, section in enumerate(index["sections"], 1):
        section["num"] = "%02d" % position
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
    print("index:", {k: index[k] for k in ("beings", "families", "orders", "groups",
                                           "photos", "statuses")})


if __name__ == "__main__":
    sys.exit(main())
