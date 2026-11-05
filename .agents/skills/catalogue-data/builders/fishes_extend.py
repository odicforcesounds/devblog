#!/usr/bin/env python3
"""Add the fishes, sharks and water beings the shelf lacks.

build_fishes.py writes the whole catalogue from scratch; this pass reads the
finished sections, fetches only the rows below, files each under its order and
family, and recomputes counts and facets. An article already present is skipped,
so a second run changes nothing.

    python3 .agents/skills/catalogue-data/builders/fishes_extend.py
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

import build_fishes as bf

OUT = bf.OUT

# title | group | order | family | salinity | zones | regions | traits
EXTRA = """
Great white shark|fish|Lamniformes|Lamnidae|marine|open-sea,coastal|worldwide|predator
Whale shark|fish|Orectolobiformes|Rhincodontidae|marine|open-sea,reef|worldwide|filter-feeder
Tiger shark|fish|Carcharhiniformes|Carcharhinidae|marine|coastal,reef|worldwide|predator
Hammerhead shark|fish|Carcharhiniformes|Sphyrnidae|marine|coastal,open-sea|worldwide|predator
Greenland shark|fish|Squaliformes|Somniosidae|marine|deep-sea,open-sea|europe,americas|predator,long-lived
Bull shark|fish|Carcharhiniformes|Carcharhinidae|both|coastal,river|worldwide|predator
Manta ray|fish|Myliobatiformes|Mobulidae|marine|open-sea,reef|worldwide|filter-feeder
Blue-spotted stingray|fish|Myliobatiformes|Dasyatidae|marine|reef,seabed|asia,africa,oceania|venomous
Sawfish|fish|Pristiformes|Pristidae|both|coastal,river|worldwide|predator
Emperor angelfish|fish|Perciformes|Pomacanthidae|marine|reef|asia,africa,oceania|
Butterflyfish|fish|Perciformes|Chaetodontidae|marine|reef|worldwide|
Parrotfish|fish|Labriformes|Scaridae|marine|reef|worldwide|herbivore
Lionfish|fish|Scorpaeniformes|Scorpaenidae|marine|reef|asia,oceania|venomous,predator
Moray eel|fish|Anguilliformes|Muraenidae|marine|reef,seabed|worldwide|predator
Triggerfish|fish|Tetraodontiformes|Balistidae|marine|reef|worldwide|territorial
Boxfish|fish|Tetraodontiformes|Ostraciidae|marine|reef|worldwide|venomous
Giant grouper|fish|Perciformes|Serranidae|marine|reef|asia,oceania|predator
Cleaner wrasse|fish|Labriformes|Labridae|marine|reef|asia,africa,oceania|symbiosis
Pipefish|fish|Syngnathiformes|Syngnathidae|marine|coastal,reef|worldwide|male-pregnancy,camouflage
Arapaima|fish|Osteoglossiformes|Arapaimidae|fresh|river,wetland|americas|air-breather
Wels catfish|fish|Siluriformes|Siluridae|fresh|river,lake|europe,asia|predator
Northern pike|fish|Esociformes|Esocidae|fresh|river,lake|europe,asia,americas|predator
European perch|fish|Perciformes|Percidae|fresh|river,lake|europe,asia|predator,shoaling
Largemouth bass|fish|Centrarchiformes|Centrarchidae|fresh|lake,river|americas|game-fish
Koi|fish|Cypriniformes|Cyprinidae|fresh|pond|asia|
Tench|fish|Cypriniformes|Cyprinidae|fresh|lake,river|europe,asia|
Bream|fish|Cypriniformes|Cyprinidae|fresh|lake,river|europe,asia|
Arctic char|fish|Salmoniformes|Salmonidae|both|river,lake,coastal|europe,americas|migratory
European eel|fish|Anguilliformes|Anguillidae|both|river,coastal,open-sea|europe,americas|migratory
Beluga sturgeon|fish|Acipenseriformes|Acipenseridae|both|river,coastal|europe,asia|caviar
Viperfish|fish|Stomiiformes|Stomiidae|marine|deep-sea|worldwide|predator,bioluminescent
Gulper eel|fish|Saccopharyngiformes|Eurypharyngidae|marine|deep-sea|worldwide|predator
Coelacanth|fish|Coelacanthiformes|Latimeriidae|marine|deep-sea,cave|africa|living-fossil
Lanternfish|fish|Myctophiformes|Myctophidae|marine|deep-sea,open-sea|worldwide|bioluminescent,migratory
Giant oarfish|fish|Lampriformes|Regalecidae|marine|deep-sea,open-sea|worldwide|
Common octopus|cephalopod|Octopoda|Octopodidae|marine|reef,seabed|worldwide|predator,camouflage
Giant Pacific octopus|cephalopod|Octopoda|Enteroctopodidae|marine|seabed,coastal|asia,americas|predator
Cuttlefish|cephalopod|Sepiida|Sepiidae|marine|coastal,reef|worldwide|camouflage
Nautilus|cephalopod|Nautilida|Nautilidae|marine|reef,deep-sea|oceania,asia|living-fossil
Moon jellyfish|jellyfish|Semaeostomeae|Ulmaridae|marine|coastal,open-sea|worldwide|venomous
Lion's mane jellyfish|jellyfish|Semaeostomeae|Cyaneidae|marine|open-sea,coastal|worldwide|venomous
Starfish|starfish|Forcipulatida|Asteriidae|marine|seabed,coastal|worldwide|predator,regeneration
Sea urchin|sea urchin|Camarodonta|Echinidae|marine|seabed,reef|worldwide|herbivore
European lobster|lobster|Decapoda|Nephropidae|marine|seabed,coastal|europe,americas|
American lobster|lobster|Decapoda|Nephropidae|marine|seabed,coastal|americas|
Blue crab|crab|Decapoda|Portunidae|both|estuary,coastal|americas|swimmer
Hermit crab|crab|Decapoda|Paguridae|marine|coastal,seabed|worldwide|builder
Krill|krill|Euphausiacea|Euphausiidae|marine|open-sea,deep-sea|worldwide|shoaling
Goose barnacle|barnacle|Pedunculata|Lepadidae|marine|coastal,open-sea|worldwide|filter-feeder
Blue mussel|mussel|Mytilida|Mytilidae|marine|coastal|europe,americas|filter-feeder
Giant clam|clam|Venerida|Tridacnidae|marine|reef|oceania,asia|symbiosis
Common periwinkle|snail|Littorinimorpha|Littorinidae|marine|coastal|europe,americas|grazer
"""


def rows():
    out = []
    for line in EXTRA.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        bits += [""] * (8 - len(bits))
        out.append({
            "title": bits[0], "grp": bits[1], "order": bits[2], "family": bits[3],
            "salinity": bits[4],
            "zones": [z for z in bits[5].split(",") if z],
            "regions": [r for r in bits[6].split(",") if r],
            "traits": [t for t in bits[7].split(",") if t],
        })
    return out


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for section in index["sections"]:
        payload = json.load(open(os.path.join(OUT, section["key"] + ".json"), encoding="utf-8"))
        groups[section["key"]] = {"group": section,
                                  "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    existing = {being["u"] for state in groups.values()
                for family in state["families"].values() for being in family}
    resolved = []
    for row in rows():
        summary = bf.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
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
    status, taxon, length, mass = bf.wikidata(qids) if qids else ({}, {}, {}, {})

    added = 0
    for row, summary, url in resolved:
        qid = summary.get("wikibase_item")
        entry = {
            "n": summary.get("title") or row["title"],
            "u": url,
            "d": bf.clean_extract(summary.get("extract") or ""),
            "z": row["zones"], "r": row["regions"], "t": row["traits"],
            "w": row["salinity"], "fam": row["family"], "ord": row["order"], "grp": row["grp"],
        }
        if qid:
            if qid in taxon:
                entry["s"] = taxon[qid]
            if qid in status:
                entry["st"] = status[qid]
            if qid in length:
                entry["l"] = length[qid]
            if qid in mass:
                entry["m"] = mass[qid]
        if not entry.get("s"):
            binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
            if binomial:
                entry["s"] = binomial.group(1)
        thumb = bf.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bf.file_page(thumb)
        key = bf.slug(row["order"])
        if key not in groups:
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": row["order"],
                     "beings": 0, "families": 0, "photos": 0, "songs": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["sections"].append(fresh)
        groups[key]["families"].setdefault(row["family"], []).append(entry)
        added += 1
        print("  +", entry["n"], "->", row["order"])
    print("added:", added)

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
    index["songs"] = songs
    index["statuses"] = statuses
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("index:", {k: index[k] for k in ("beings", "families", "orders", "groups",
                                           "photos", "songs", "statuses")})


if __name__ == "__main__":
    sys.exit(main())
