#!/usr/bin/env python3
"""Add the bird orders and families the shelf holds at one or two species.

build_birds.py writes the whole catalogue from scratch; this pass reads the
finished groups, fetches only the rows below, files each under its order and
family, and recomputes counts and facets. An article already present is skipped,
so a second run changes nothing.

    python3 .agents/skills/catalogue-data/builders/birds_extend.py
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

import build_birds as bb

OUT = bb.OUT

# title | order | family | habitats | regions | traits
EXTRA = """
Cuckoo roller|Leptosomiformes|Leptosomidae|forest|africa|
Hoatzin|Opisthocomiformes|Opisthocomidae|wetland,forest|americas|
Tawny frogmouth|Podargiformes|Podargidae|woodland|oceania|nocturnal
Little spotted kiwi|Apterygiformes|Apterygidae|forest,grassland|oceania|nocturnal,flightless
Red-legged seriema|Cariamiformes|Cariamidae|grassland|americas|
Southern cassowary|Casuariiformes|Casuariidae|forest|oceania|flightless
Speckled mousebird|Coliiformes|Coliidae|woodland,urban|africa|
Pallas's sandgrouse|Pterocliformes|Pteroclidae|desert,grassland|asia|migratory
Sunbittern|Eurypygiformes|Eurypygidae|forest,wetland|americas|
Red-billed tropicbird|Phaethontiformes|Phaethontidae|marine,coastal|worldwide|seabird
Common loon|Gaviiformes|Gaviidae|lake,coastal|europe,americas|migratory
Northern gannet|Suliformes|Sulidae|marine,coastal|europe,americas|seabird,colonial
Great white pelican|Pelecaniformes|Pelecanidae|wetland,coastal|europe,asia,africa|fish-eater
White stork|Ciconiiformes|Ciconiidae|farmland,wetland|europe,asia,africa|migratory
Greater flamingo|Phoenicopteriformes|Phoenicopteridae|wetland,lake|europe,asia,africa,americas|filter-feeder
Great crested grebe|Podicipediformes|Podicipedidae|lake,wetland|europe,asia,oceania|
Great bustard|Otidiformes|Otididae|grassland,farmland|europe,asia|ground-nester
Rock dove|Columbiformes|Columbidae|urban,coastal|worldwide|
Common cuckoo|Cuculiformes|Cuculidae|woodland,farmland|europe,asia,africa|brood-parasite,migratory
European nightjar|Caprimulgiformes|Caprimulgidae|woodland|europe,asia|nocturnal
Common swift|Apodiformes|Apodidae|urban,farmland|europe,asia,africa|migratory
Resplendent quetzal|Trogoniformes|Trogonidae|forest|americas|
Common kingfisher|Coraciiformes|Alcedinidae|river,coastal|europe,asia,africa|fish-eater
Great spotted woodpecker|Piciformes|Picidae|woodland,urban|europe,asia|tool-user
Kea|Psittaciformes|Nestoridae|alpine,forest|oceania|tool-user,intelligent
Grey crowned crane|Gruiformes|Gruidae|wetland,grassland|africa|
Atlantic puffin|Charadriiformes|Alcidae|marine,coastal|europe,americas|seabird
Snowy albatross|Procellariiformes|Diomedeidae|marine,open-sea|worldwide|seabird
"""


def rows():
    out = []
    for line in EXTRA.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        bits += [""] * (6 - len(bits))
        out.append({
            "title": bits[0], "order": bits[1], "family": bits[2],
            "habitats": [h for h in bits[3].split(",") if h],
            "regions": [r for r in bits[4].split(",") if r],
            "traits": [t for t in bits[5].split(",") if t],
        })
    return out


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["groups"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {"group": group,
                                "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    existing = {bird["u"] for state in groups.values()
                for family in state["families"].values() for bird in family}
    resolved = []
    for row in rows():
        summary = bb.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
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

    added = 0
    for row, summary, url in resolved:
        entry = {
            "n": summary.get("title") or row["title"],
            "u": url,
            "d": bb.clean_extract(summary.get("extract") or ""),
            "h": row["habitats"], "r": row["regions"], "t": row["traits"],
            "fam": row["family"], "ord": row["order"],
        }
        binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
        if binomial:
            entry["s"] = binomial.group(1)
        thumb = bb.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bb.file_page(thumb)
        key = bb.slug(row["order"])
        if key not in groups:
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": row["order"],
                     "species": 0, "families": 0, "photos": 0, "songs": 0, "statuses": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["groups"].append(fresh)
        groups[key]["families"].setdefault(row["family"], []).append(entry)
        added += 1
        print("  +", entry["n"], "->", row["order"])
    print("added:", added)

    facets = {"habitat": {}, "region": {}, "trait": {}, "status": {}}
    total = photos = songs = statuses = 0
    for key, state in groups.items():
        birds = [b for fam in state["families"].values() for b in fam]
        for fam in state["families"]:
            state["families"][fam].sort(key=lambda b: b["n"])
        payload = {"key": key, "title": state["group"]["title"], "families": [
            {"n": fam, "c": len(state["families"][fam]), "s": state["families"][fam]}
            for fam in sorted(state["families"], key=lambda f: (-len(state["families"][f]), f))
        ]}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(birds)
        photos += sum(1 for b in birds if b.get("i"))
        songs += sum(1 for b in birds if b.get("a"))
        statuses += sum(1 for b in birds if b.get("st"))
        state["group"]["species"] = len(birds)
        state["group"]["families"] = len(state["families"])
        state["group"]["photos"] = sum(1 for b in birds if b.get("i"))
        state["group"]["songs"] = sum(1 for b in birds if b.get("a"))
        state["group"]["statuses"] = sum(1 for b in birds if b.get("st"))
        for bird in birds:
            for value in bird["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in bird["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in bird["t"]:
                facets["trait"][value] = facets["trait"].get(value, 0) + 1
            if bird.get("st"):
                facets["status"][bird["st"]] = facets["status"].get(bird["st"], 0) + 1

    index["groups"].sort(key=lambda g: (-g["species"], g["title"]))
    for position, group in enumerate(index["groups"], 1):
        group["num"] = "%02d" % position
    index["species"] = total
    index["families"] = len({b["fam"] for state in groups.values()
                             for fam in state["families"].values() for b in fam})
    index["orders"] = len(groups)
    index["photos"] = photos
    index["songs"] = songs
    index["statuses"] = statuses
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("index:", {k: index[k] for k in ("species", "families", "orders",
                                           "photos", "songs", "statuses")})


if __name__ == "__main__":
    sys.exit(main())
