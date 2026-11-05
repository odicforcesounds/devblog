#!/usr/bin/env python3
"""Add the missing trees, flowers, conifers, succulents and ferns to docs/plants/data/.

build_plants.py writes the shelf from scratch and does not know the fungi
shelf, so re-running it would drop those ten mushrooms. This pass reads the
finished shelves, fetches only the species below, files each under its order
and family, and recomputes the counts and facets without touching a plant that
is already there.

    python3 .agents/skills/catalogue-data/builders/plants_extend.py

The edibility verdict is read the same way plants_edibility.py reads it: from
the article's own section headings, with a strict sentence as the fallback.
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

import build_plants as bp

OUT = "docs/plants/data"
UA = bp.UA

# title | order | family | habitats | regions | form
EXTRA = """
Cedrus|Pinales|Pinaceae|forest,alpine|asia,africa|conifer
Abies|Pinales|Pinaceae|forest,alpine|europe,asia,americas|conifer
Larix decidua|Pinales|Pinaceae|forest,alpine|europe|conifer
Sequoia sempervirens|Pinales|Cupressaceae|forest,coastal|americas|conifer
Araucaria araucana|Pinales|Araucariaceae|forest,alpine|americas|conifer
Ulmus minor|Rosales|Ulmaceae|woodland,urban|europe,asia|tree
Populus alba|Malpighiales|Salicaceae|wetland,farmland|europe,asia,africa|tree
Carpinus betulus|Fagales|Betulaceae|forest,urban|europe,asia|tree
Ficus benghalensis|Rosales|Moraceae|forest,urban|asia|tree
Tectona grandis|Lamiales|Lamiaceae|forest,farmland|asia|tree
Swietenia mahagoni|Sapindales|Meliaceae|forest|americas|tree
Phalaenopsis|Asparagales|Orchidaceae|forest,urban|asia,oceania|herb
Bellis perennis|Asterales|Asteraceae|grassland,urban|europe,asia|herb
Paeonia lactiflora|Saxifragales|Paeoniaceae|woodland,urban|asia|herb
Dahlia pinnata|Asterales|Asteraceae|farmland,urban|americas|herb
Hydrangea macrophylla|Cornales|Hydrangeaceae|woodland,urban|asia,americas|shrub
Narcissus (plant)|Asparagales|Amaryllidaceae|grassland,woodland|europe,africa|bulb
Camellia japonica|Ericales|Theaceae|woodland,urban|asia|shrub
Iris (plant)|Asparagales|Iridaceae|wetland,grassland|europe,asia,africa|herb
Viola (plant)|Malpighiales|Violaceae|woodland,grassland|worldwide|herb
Tagetes|Asterales|Asteraceae|farmland,urban|americas|herb
Lilium|Liliales|Liliaceae|woodland,grassland|europe,asia|bulb
Dianthus caryophyllus|Caryophyllales|Caryophyllaceae|grassland,urban|europe|herb
Delphinium|Ranunculales|Ranunculaceae|alpine,grassland|europe,asia,americas|herb
Carnegiea gigantea|Caryophyllales|Cactaceae|desert|americas|succulent
Adiantum|Polypodiales|Pteridaceae|forest,urban|worldwide|fern
"""

FOOD_HEAD = re.compile(
    r"^(as food|food|foods|food use|food uses|food and drink|"
    r"culinary( uses?| use)?|edible( uses?| parts?)?|nutrition|"
    r"nutritional value|cooking|cooking and preparation|preparation|"
    r"consumption|uses as food|eating)$", re.I)
TOXIC_HEAD = re.compile(r"\b(toxic|toxicity|poison|poisoning|poisonous|harmful|danger)\b", re.I)
DEADLY_HEAD = re.compile(r"\b(poisoning|deadly|fatal|lethal|deaths?)\b", re.I)
MED_HEAD = re.compile(r"\b(medicinal|medicine|ethnobotany|traditional use|pharmacology)\b", re.I)
STRICT_FOOD = re.compile(
    r"\b(is|are) (an? )?(edible|staple food|food crop|root vegetable|leaf vegetable|"
    r"culinary (herb|vegetable))\b"
    r"|\bedible (fruit|seed|seeds|roots?|tubers?|leaves|stalks?|bulbs?|berries|nuts?)\b"
    r"|\bused as (a |an )?(food|vegetable|spice|herb)\b"
    r"|\beaten (raw|cooked|fresh|ripe)\b", re.I)
EATEN_BY = re.compile(r"\b(eaten|fed on|consumed) by\b", re.I)


def rows():
    out = []
    for line in EXTRA.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        if len(bits) != 6:
            continue
        out.append({
            "title": bits[0], "order": bits[1], "family": bits[2],
            "habitats": [h for h in bits[3].split(",") if h],
            "regions": [r for r in bits[4].split(",") if r],
            "forms": [f for f in bits[5].split(",") if f],
        })
    return out


def headings(title):
    query = urllib.parse.urlencode({
        "action": "parse", "format": "json", "formatversion": "2",
        "prop": "sections", "redirects": "1", "page": title,
    })
    data = bp.fetch("https://en.wikipedia.org/w/api.php?" + query)
    return [section.get("line", "") for section in data.get("parse", {}).get("sections", [])
            if section.get("line")]


def full_text(title):
    query = urllib.parse.urlencode({
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "extracts", "explaintext": "1", "exlimit": "1",
        "redirects": "1", "titles": title,
    })
    data = bp.fetch("https://en.wikipedia.org/w/api.php?" + query)
    for page in data.get("query", {}).get("pages", []):
        if page.get("extract"):
            return page["extract"]
    return ""


def verdict(lines, text):
    food = [h for h in lines if FOOD_HEAD.search(h) and not TOXIC_HEAD.search(h)]
    toxic = [h for h in lines if TOXIC_HEAD.search(h)]
    deadly = [h for h in lines if DEADLY_HEAD.search(h)]
    med = [h for h in lines if MED_HEAD.search(h)]
    sentence = ""
    for candidate in bp.SENTENCES.split(text[:70000]):
        candidate = candidate.strip()
        if 20 < len(candidate) < 300 and STRICT_FOOD.search(candidate) and not EATEN_BY.search(candidate):
            sentence = candidate
            break
    if food or sentence:
        quoted = "section “%s”" % food[0] if food else "“%s”" % sentence
        if toxic:
            return "mixed", quoted + " beside “%s”" % toxic[0]
        return "eaten", quoted
    if toxic:
        return ("deadly" if deadly else "toxic"), "section “%s”" % toxic[0]
    if med:
        return "medicine", "section “%s”" % med[0]
    return "none", ""


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["groups"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {
            "group": group,
            "families": {fam["n"]: fam["s"] for fam in payload["families"]},
        }

    existing_urls = {plant["u"] for state in groups.values()
                     for family in state["families"].values() for plant in family}
    added = 0
    ours = set()
    for row in rows():
        page = row["title"].replace(" ", "_")
        summary = bp.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(page))
        if summary.get("__error__") or summary.get("type") in ("disambiguation", "no-extract"):
            print("  !", row["title"], "->", summary.get("__error__", summary.get("type", "missing")))
            continue
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page))
        ours.add(url)
        if url in existing_urls:
            print("  =", row["title"], "already shelved")
            continue
        title = summary.get("title") or row["title"]
        entry = {
            "n": title,
            "u": url,
            "d": bp.clean_extract(summary.get("extract") or ""),
            "h": row["habitats"],
            "r": row["regions"],
            "t": row["forms"],
            "fam": row["family"],
            "ord": row["order"],
        }
        thumb = bp.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bp.file_page(thumb)
        text = full_text(page)
        lines = headings(page)
        ed, evidence = verdict(lines, text)
        entry["ed"] = ed
        if evidence:
            entry["eq"] = evidence
        if re.match(r"^[A-Z][a-z]+ [a-z-]+$", title):
            entry["s"] = title

        key = bp.slug(row["order"])
        if key not in groups:
            number = len(groups) + 1
            fresh = {"key": key, "num": "%02d" % number, "title": row["order"],
                     "plants": 0, "families": 0, "photos": 0, "food": 0, "poison": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["groups"].append(fresh)
        groups[key]["families"].setdefault(row["family"], []).append(entry)
        existing_urls.add(url)
        added += 1
        print("  +", title, "->", row["order"] + "/" + row["family"], "|", ed)
        time.sleep(0.6)

    print("added:", added)

    all_names = [plant["n"] for state in groups.values()
                 for family in state["families"].values() for plant in family]
    for state in groups.values():
        for family in state["families"].values():
            for plant in family:
                if plant["u"] not in ours:
                    continue
                clean = re.sub(r"\s*\(plant\)$", "", plant["n"])
                if clean != plant["n"] and all_names.count(clean) == 0 and all_names.count(plant["n"]) == 1:
                    all_names[all_names.index(plant["n"])] = clean
                    plant["n"] = clean

    renumbered = sorted(index["groups"], key=lambda group: (group["key"] == "fungi", int(group["num"])))
    for position, group in enumerate(renumbered, start=1):
        group["num"] = "%02d" % position
    index["groups"] = renumbered

    facets = {"edibility": {}, "habitat": {}, "region": {}, "form": {}, "status": {}}
    total = photos = statuses = 0
    for key, state in groups.items():
        plants = [plant for family in state["families"].values() for plant in family]
        for family in state["families"]:
            state["families"][family].sort(key=lambda p: p["n"])
        payload = {"key": key, "title": state["group"]["title"], "families": [
            {"n": family, "c": len(state["families"][family]), "s": state["families"][family]}
            for family in sorted(state["families"], key=lambda f: (-len(state["families"][f]), f))
        ]}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(plants)
        photos += sum(1 for p in plants if p.get("i"))
        statuses += sum(1 for p in plants if p.get("st"))
        group = state["group"]
        group["plants"] = len(plants)
        group["families"] = len(state["families"])
        group["photos"] = sum(1 for p in plants if p.get("i"))
        group["food"] = sum(1 for p in plants if p.get("ed") in ("eaten", "cooked"))
        group["poison"] = sum(1 for p in plants if p.get("ed") in ("toxic", "deadly", "mixed"))
        for plant in plants:
            state = plant.get("ed") or "none"
            facets["edibility"][state] = facets["edibility"].get(state, 0) + 1
            for value in plant.get("h") or []:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in plant.get("r") or []:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in plant.get("t") or []:
                facets["form"][value] = facets["form"].get(value, 0) + 1
            if plant.get("st"):
                facets["status"][plant["st"]] = facets["status"].get(plant["st"], 0) + 1

    index["plants"] = total
    index["families"] = len({p["fam"] for state in groups.values()
                             for family in state["families"].values() for p in family})
    index["orders"] = len(groups)
    index["photos"] = photos
    index["statuses"] = statuses
    index["edible"] = sum(1 for state in groups.values() for family in state["families"].values()
                          for p in family if p.get("ed") in ("eaten", "cooked"))
    index["poisonous"] = sum(1 for state in groups.values() for family in state["families"].values()
                             for p in family if p.get("ed") in ("toxic", "deadly", "mixed"))
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("index:", {k: index[k] for k in ("plants", "families", "orders", "photos", "edible", "poisonous")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
