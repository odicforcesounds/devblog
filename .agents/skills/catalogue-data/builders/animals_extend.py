#!/usr/bin/env python3
"""Add the mammals, reptiles and amphibians the animal shelf lacks.

build_animals.py writes the whole catalogue from scratch; this pass reads the
finished groups, fetches only the rows below, files each under its class, order
and family, and recomputes counts and facets. An article already present is
skipped, so a second run changes nothing.

    python3 .agents/skills/catalogue-data/builders/animals_extend.py
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

import build_animals as ba

OUT = ba.OUT

# title | class | order | family | habitats | regions | traits
EXTRA = """
Pangolin|mammal|Pholidota|Manidae|forest,grassland|asia,africa|insectivore
Aardvark|mammal|Tubulidentata|Orycteropodidae|grassland,desert|africa|insectivore,nocturnal
Aye-aye|mammal|Primates|Daubentoniidae|forest|africa|nocturnal,insectivore
Fossa|mammal|Carnivora|Eupleridae|forest|africa|predator
Kinkajou|mammal|Carnivora|Procyonidae|forest|americas|arboreal,frugivore
Okapi|mammal|Artiodactyla|Giraffidae|forest|africa|herbivore
Saiga antelope|mammal|Artiodactyla|Bovidae|grassland,desert|asia|herbivore,migratory
Gerenuk|mammal|Artiodactyla|Bovidae|desert,grassland|africa|herbivore
Dik-dik|mammal|Artiodactyla|Bovidae|grassland,woodland|africa|herbivore
Pika|mammal|Lagomorpha|Ochotonidae|alpine|asia,americas|herbivore
Solenodon|mammal|Eulipotyphla|Solenodontidae|forest|americas|venomous,insectivore
Tenrec|mammal|Afrosoricida|Tenrecidae|forest|africa|insectivore
Numbat|mammal|Dasyuromorphia|Myrmecobiidae|woodland|oceania|insectivore
Quokka|mammal|Diprotodontia|Macropodidae|woodland,urban|oceania|herbivore
Wombat|mammal|Diprotodontia|Vombatidae|woodland|oceania|herbivore,burrower
Tasmanian devil|mammal|Dasyuromorphia|Dasyuridae|forest|oceania|predator,scavenger
Short-beaked echidna|mammal|Monotremata|Tachyglossidae|woodland,desert|oceania|insectivore,egg-laying
Platypus|mammal|Monotremata|Ornithorhynchidae|river,wetland|oceania|egg-laying,venomous
Dugong|mammal|Sirenia|Dugongidae|marine,coastal|oceania,asia,africa|herbivore
Narwhal|mammal|Cetacea|Monodontidae|marine|arctic|predator
Beluga whale|mammal|Cetacea|Monodontidae|marine|arctic|predator,social
Sperm whale|mammal|Cetacea|Physeteridae|marine|open-sea,deep-sea|worldwide|predator,diver
Vaquita|mammal|Cetacea|Phocoenidae|marine|coastal|americas|critically-endangered
Ganges river dolphin|mammal|Cetacea|Platanistidae|fresh|river|asia|echolocation
Bactrian camel|mammal|Artiodactyla|Camelidae|desert|asia|herbivore
Przewalski's horse|mammal|Perissodactyla|Equidae|grassland|asia|herbivore
Alpine ibex|mammal|Artiodactyla|Bovidae|alpine|europe|herbivore,climber
Chamois|mammal|Artiodactyla|Bovidae|alpine,forest|europe,asia|herbivore,climber
Muskox|mammal|Artiodactyla|Bovidae|alpine|americas,europe|herbivore,social
Takin|mammal|Artiodactyla|Bovidae|alpine,forest|asia|herbivore
Komodo dragon|reptile|Squamata|Varanidae|grassland,forest|asia|predator,venomous
Saltwater crocodile|reptile|Crocodilia|Crocodylidae|wetland,coastal|asia,oceania|predator
Nile crocodile|reptile|Crocodilia|Crocodylidae|wetland,river|africa|predator
American alligator|reptile|Crocodilia|Alligatoridae|wetland|americas|predator
Galápagos tortoise|reptile|Testudines|Testudinidae|grassland,alpine|americas|herbivore,long-lived
Green sea turtle|reptile|Testudines|Cheloniidae|marine,coastal|worldwide|herbivore,migratory
King cobra|reptile|Squamata|Elapidae|forest,farmland|asia|venomous,predator
Reticulated python|reptile|Squamata|Pythonidae|forest|asia|predator
Veiled chameleon|reptile|Squamata|Chamaeleonidae|desert,woodland|asia|camouflage
Gila monster|reptile|Squamata|Helodermatidae|desert|americas|venomous
Tuatara|reptile|Rhynchocephalia|Sphenodontidae|woodland|oceania|living-fossil
Axolotl|amphibian|Urodela|Ambystomatidae|lake,wetland|americas|neoteny
Poison dart frog|amphibian|Anura|Dendrobatidae|forest|americas|venomous
Common toad|amphibian|Anura|Bufonidae|woodland,urban|europe,asia|nocturnal
Fire salamander|amphibian|Urodela|Salamandridae|forest|europe|venomous
Chinese giant salamander|amphibian|Urodela|Cryptobranchidae|river|asia|amphibian
Caecilian|amphibian|Gymnophiona|Caeciliidae|forest|americas,asia,africa|burrower
Great white shark|fish|Lamniformes|Lamnidae|marine,coastal|worldwide|predator
Whale shark|fish|Orectolobiformes|Rhincodontidae|marine,open-sea|worldwide|filter-feeder
Ocean sunfish|fish|Tetraodontiformes|Molidae|marine,open-sea|worldwide|
Moray eel|fish|Anguilliformes|Muraenidae|marine,reef|worldwide|predator
"""


def rows():
    out = []
    for line in EXTRA.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        bits += [""] * (7 - len(bits))
        out.append({
            "title": bits[0], "cls": bits[1], "order": bits[2], "family": bits[3],
            "habitats": [h for h in bits[4].split(",") if h],
            "regions": [r for r in bits[5].split(",") if r],
            "traits": [t for t in bits[6].split(",") if t],
        })
    return out


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["groups"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {"group": group,
                                "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    existing = {animal["u"] for state in groups.values()
                for family in state["families"].values() for animal in family}
    resolved = []
    for row in rows():
        summary = ba.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
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
    status, taxon, length, mass = ba.wikidata(qids) if qids else ({}, {}, {}, {})

    added = 0
    for row, summary, url in resolved:
        qid = summary.get("wikibase_item")
        entry = {
            "n": summary.get("title") or row["title"],
            "u": url,
            "d": ba.clean_extract(summary.get("extract") or ""),
            "h": row["habitats"], "r": row["regions"], "t": row["traits"],
            "fam": row["family"], "ord": row["order"], "cls": row["cls"],
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
        thumb = ba.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = ba.file_page(thumb)
        key = ba.slug(row["order"])
        if key not in groups:
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": row["order"],
                     "animals": 0, "families": 0, "photos": 0, "songs": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["groups"].append(fresh)
        groups[key]["families"].setdefault(row["family"], []).append(entry)
        added += 1
        print("  +", entry["n"], "->", row["order"])
    print("added:", added)

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

    index["groups"].sort(key=lambda g: (-g["animals"], g["title"]))
    for position, group in enumerate(index["groups"], 1):
        group["num"] = "%02d" % position
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
    print("index:", {k: index[k] for k in ("animals", "families", "orders", "classes",
                                           "photos", "songs", "statuses")})


if __name__ == "__main__":
    sys.exit(main())
