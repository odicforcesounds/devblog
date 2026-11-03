#!/usr/bin/env python3
"""Verdict pass for docs/plants/data/ — reads the article's own section headings.

A sentence is a bad place to learn whether a plant is food: "eaten by thrushes"
and "low in micronutrients" both look like culinary writing to a regex. An
article's structure is harder to fool: a species that people eat has a section
called "As food", "Culinary use" or "Nutrition", and a species that poisons
them has one called "Toxicity" or "Poisoning".

So the verdict is the presence of those headings, the evidence is the heading
quoted back, and only when an article has no such section does a strict
sentence check ("is a root vegetable", "edible fruit") decide. Everything is
cached in tmp/, so this can be re-run without touching the network.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

OUT = "docs/plants/data"
UA = {"User-Agent": "devblog-plants/1.0 (https://blog.odicforcesounds.com; contact via site)"}
SECTIONS = "tmp/plant_sections.json"
TEXTS = "tmp/plant_texts.json"

sys.path.insert(0, "tmp")
import build_plants as bp  # noqa: E402

# a heading that says the plant is food, not one that merely mentions food
FOOD_HEAD = re.compile(r"^(as food|food|foods|food use|food uses|food and drink|"
                       r"culinary( uses?| use)?|edible( uses?| parts?)?|nutrition|"
                       r"nutritional value|cooking|cooking and preparation|preparation|"
                       r"consumption|uses as food|eating)$", re.I)
TOXIC_HEAD = re.compile(r"\b(toxic|toxicity|poison|poisoning|poisonous|harmful|danger)\b", re.I)
DEADLY_HEAD = re.compile(r"\b(poisoning|deadly|fatal|lethal|deaths?)\b", re.I)
MED_HEAD = re.compile(r"\b(medicinal|medicine|ethnobotany|traditional use|pharmacology)\b", re.I)
COOK_HEAD = re.compile(r"\b(cooking|cookery|culinary|preparation)\b", re.I)
COOK_STATEMENT = re.compile(r"\b(must be cooked|needs? cooking|requires? cooking|leached|detoxified|"
                            r"after cooking|after boiling|cooked before|soaked and cooked|"
                            r"cannot be eaten raw|not eaten raw|inedible raw)\b", re.I)
EATEN_BY = re.compile(r"\b(food plant|food source)\b[^.]{0,40}\b(larvae|caterpillars|birds|insects|moths|"
                      r"beetles|mammals|animals|butterfl)\b|\b(eaten|fed on|consumed) by\b", re.I)
WHOLE_POISON = re.compile(r"\ball parts\b[^.]{0,90}\b(poisonous|toxic)\b|\b(entire|whole) plant\b[^.]{0,60}\b(poisonous|toxic)\b", re.I)
DEADLY_WORD = re.compile(r"\b(deadly|lethal|fatal|fatalities|deaths?)\b", re.I)

# only when an article has no food section at all
STRICT_FOOD = re.compile(
    r"\b(is|are) (an? )?(edible|staple food|food crop|root vegetable|leaf vegetable|"
    r"culinary (herb|vegetable))\b"
    r"|\bedible (fruit|seed|seeds|roots?|tubers?|leaves|stalks?|bulbs?|berries|nuts?)\b"
    r"|\bused as (a |an )?(food|vegetable|spice|herb)\b"
    r"|\beaten (raw|cooked|fresh|ripe)\b", re.I)


def fetch(url, tries=5):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(6 * (attempt + 1))
                continue
            return {"__error__": "HTTP %s" % exc.code}
        except Exception as exc:  # noqa: BLE001
            if attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            return {"__error__": str(exc)}
    return {"__error__": "gave up"}


def title_of(url):
    return urllib.parse.unquote(url.split("#")[0].split("/wiki/", 1)[-1]).replace("_", " ")


def headings(title):
    query = urllib.parse.urlencode({
        "action": "parse", "format": "json", "formatversion": "2",
        "prop": "sections", "redirects": "1", "page": title,
    })
    data = fetch("https://en.wikipedia.org/w/api.php?" + query)
    sections = data.get("parse", {}).get("sections", [])
    return [section.get("line", "") for section in sections if section.get("line")]


def load_cache(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def verdict(titles, text):
    food = [h for h in titles if FOOD_HEAD.search(h) and not TOXIC_HEAD.search(h)]
    toxic = [h for h in titles if TOXIC_HEAD.search(h)]
    deadly = [h for h in titles if DEADLY_HEAD.search(h)]
    med = [h for h in titles if MED_HEAD.search(h)]

    sentence = ""
    cooking = ""
    for candidate in bp.SENTENCES.split(text[:70000]):
        candidate = candidate.strip()
        if not 20 < len(candidate) < 300:
            continue
        if not sentence and STRICT_FOOD.search(candidate) and not EATEN_BY.search(candidate):
            sentence = candidate
        if not cooking and COOK_STATEMENT.search(candidate):
            cooking = candidate
        if sentence and cooking:
            break

    whole = WHOLE_POISON.search(text[:70000])
    if whole and not sentence:
        # a plant that is poisonous in every part is not a food, whatever else the page lists
        return ("deadly" if DEADLY_WORD.search(text[:70000]) else "toxic"), "“%s”" % whole.group(0).strip()[:160]

    if food or sentence:
        quoted = "section “%s”" % food[0] if food else "“%s”" % sentence
        if toxic:
            return "mixed", quoted + " beside “%s”" % toxic[0]
        if cooking:
            return "cooked", quoted + " — “%s”" % cooking
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
        groups[group["key"]] = {"group": group,
                                "families": {fam["n"]: fam["s"] for fam in payload["families"]}}

    plants = [(key, fam, plant) for key, state in groups.items()
              for fam, list_ in state["families"].items() for plant in list_]
    titles = sorted({title_of(plant["u"]) for _, _, plant in plants})

    section_cache = load_cache(SECTIONS)
    text_cache = load_cache(TEXTS)
    missing = [title for title in titles if title not in section_cache]
    print("plants:", len(plants), "| articles:", len(titles), "| headings to fetch:", len(missing))
    if missing:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for done, (title, lines) in enumerate(zip(missing, pool.map(headings, missing)), 1):
                section_cache[title] = lines
                if done % 50 == 0:
                    print("  headings:", done, "/", len(missing))
        with open(SECTIONS, "w", encoding="utf-8") as fh:
            json.dump(section_cache, fh)

    distribution = {}
    for _key, _fam, plant in plants:
        title = title_of(plant["u"])
        ed, evidence = verdict(section_cache.get(title, []), text_cache.get(title, ""))
        plant["ed"] = ed
        if evidence:
            plant["eq"] = evidence
        else:
            plant.pop("eq", None)
        plant.pop("ew", None)
        distribution[ed] = distribution.get(ed, 0) + 1
    print("verdicts:", sorted(distribution.items(), key=lambda kv: -kv[1]))

    facets = {"edibility": {}, "habitat": {}, "region": {}, "form": {}, "status": {}}
    total = photos = statuses = 0
    for key, state in groups.items():
        birds = [plant for fam in state["families"].values() for plant in fam]
        for fam in state["families"]:
            state["families"][fam].sort(key=lambda p: p["n"])
        payload = {"key": key, "title": state["group"]["title"], "families": [
            {"n": fam, "c": len(state["families"][fam]), "s": state["families"][fam]}
            for fam in sorted(state["families"], key=lambda f: (-len(state["families"][f]), f))
        ]}
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        total += len(birds)
        photos += sum(1 for p in birds if p.get("i"))
        statuses += sum(1 for p in birds if p.get("st"))
        state["group"]["plants"] = len(birds)
        state["group"]["families"] = len(state["families"])
        state["group"]["photos"] = sum(1 for p in birds if p.get("i"))
        state["group"]["food"] = sum(1 for p in birds if p["ed"] in ("eaten", "cooked"))
        state["group"]["poison"] = sum(1 for p in birds if p["ed"] in ("toxic", "deadly", "mixed"))
        for plant in birds:
            facets["edibility"][plant["ed"]] = facets["edibility"].get(plant["ed"], 0) + 1
            for value in plant["h"]:
                facets["habitat"][value] = facets["habitat"].get(value, 0) + 1
            for value in plant["r"]:
                facets["region"][value] = facets["region"].get(value, 0) + 1
            for value in plant["t"]:
                facets["form"][value] = facets["form"].get(value, 0) + 1
            if plant.get("st"):
                facets["status"][plant["st"]] = facets["status"].get(plant["st"], 0) + 1

    index["plants"] = total
    index["families"] = len({p["fam"] for state in groups.values()
                             for fam in state["families"].values() for p in fam})
    index["orders"] = len(groups)
    index["photos"] = photos
    index["statuses"] = statuses
    index["edible"] = sum(1 for state in groups.values() for fam in state["families"].values()
                          for p in fam if p["ed"] in ("eaten", "cooked"))
    index["poisonous"] = sum(1 for state in groups.values() for fam in state["families"].values()
                             for p in fam if p["ed"] in ("toxic", "deadly", "mixed"))
    index["facets"] = facets
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("index:", {k: index[k] for k in ("plants", "families", "orders", "photos", "edible", "poisonous")})
    print("edibility facet:", index["facets"]["edibility"])


if __name__ == "__main__":
    main()
