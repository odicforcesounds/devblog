#!/usr/bin/env python3
"""Second pass over docs/plants/data/.

Two jobs:

1. The first build read edibility from the article's first two sentences, which
   hardly ever mention eating, so most plants came back "no food use". This
   refetches the full plain-text article in batches of ten and classifies
   against every sentence, storing the deciding sentence (eq) and, when the
   article also warns about a poisonous part, that warning (ew) beside it.
2. Five species had landed on disambiguation pages and are fetched here under
   their accepted titles.
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

sys.path.insert(0, "tmp")
import build_plants as bp  # noqa: E402  (shares the cues, cleaners and fetchers)

ALT = {
    "Hops": ("Humulus lupulus", "Rosales", "Cannabaceae", ["farmland", "woodland"], ["europe", "asia", "americas"], ["climber"]),
    "Theobroma cacao": ("Cacao", "Malvales", "Malvaceae", ["forest", "farmland"], ["americas", "africa"], ["tree"]),
    "Cooking banana": ("Plantain (fruit)", "Zingiberales", "Musaceae", ["farmland"], ["africa", "americas"], ["herb"]),
    "Canna (plant)": ("Canna", "Zingiberales", "Cannaceae", ["wetland", "urban"], ["americas"], ["herb"]),
    "Yam (vegetable)": ("Yam", "Dioscoreales", "Dioscoreaceae", ["farmland", "forest"], ["africa", "asia", "americas"], ["climber"]),
}

CACHE = "tmp/plant_texts.json"

# Human food language only: "eaten by thrushes" is not a culinary use.
HUMAN_FOOD = re.compile(
    r"(\bis (an? )?(edible|culinary)\b"
    r"|\bare (edible|eaten)\b"
    r"|\bedible (fruit|seed|seeds|leaves|roots?|tubers?|bulbs?|stalks?|shoots?|nuts?|berries|flowers)\b"
    r"|\b(fruit|seeds?|leaves|roots?|tubers?|bulbs?|stalks?|shoots?|berries|nuts?|flowers) (are|is) (edible|eaten|cooked)\b"
    r"|\bused as (a |an )?(food|vegetable|spice|herb|flavou?ring|staple)\b"
    r"|\b(is|are) (a |an )?(staple food|food crop|cash crop|root vegetable|leaf vegetable)\b"
    r"|\beaten (raw|cooked|fresh|ripe|boiled|roasted|fried)\b"
    r"|\bculinary (use|uses|herb|variety|rhubarb)\b"
    r"|\bfood (crop|source|plant|use)\b)", re.I)
HUMAN_TOXIC = re.compile(r"\b(poisonous|toxic|deadly|lethal|fatal|not edible|inedible|unpalatable|unsafe to eat)\b", re.I)
ANIMAL_ONLY = re.compile(r"\b(to|for) (cats|dogs|horses|cattle|livestock|birds|insects|pets|animals)\b", re.I)
ANIMAL_EATER = re.compile(r"\b(by|for|to)\b[^.]{0,34}\b(birds|animals|insects|mammals|caterpillars|larvae|fish|monkeys|rodents|thrushes|waxwings|pigs|cattle|livestock|beetles)\b", re.I)
WHOLE_PLANT = re.compile(r"\b(all parts|every part|entire plant|whole plant)\b", re.I)
PLAIN_TOXIC = re.compile(r"\b(is|are)\b[^.]{0,30}\b(poisonous|toxic|deadly)\b|\bcan be (fatal|lethal|deadly)\b", re.I)
INGEST = re.compile(r"\b(eaten|eating|ingest\w*|swallow\w*|consum\w*|food|poisoning)\b", re.I)


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


def verdict(text):
    """Return (class, evidence sentence, warning sentence) about eating the plant."""
    if not text:
        return "none", "", ""
    sentences = [s.strip() for s in bp.SENTENCES.split(text[:90000]) if 20 < len(s.strip()) < 400]
    shortest = lambda group: min(group, key=len) if group else ""  # noqa: E731

    food, cooked, toxic, med = [], [], [], []
    for sentence in sentences:
        if re.search(r"not\s+\w*\s*(toxic|poisonous|deadly)", sentence, re.I):
            continue
        if HUMAN_FOOD.search(sentence) and not ANIMAL_EATER.search(sentence) \
                and not HUMAN_TOXIC.search(sentence):
            food.append(sentence)
            if bp.COOKED_CUE.search(sentence):
                cooked.append(sentence)
        if HUMAN_TOXIC.search(sentence) and not ANIMAL_ONLY.search(sentence):
            if INGEST.search(sentence) or PLAIN_TOXIC.search(sentence):
                toxic.append(sentence)
        if bp.MED_CUE.search(sentence):
            med.append(sentence)

    if food and toxic:
        return "mixed", shortest(toxic), ""
    if food:
        return ("cooked" if cooked else "eaten"), (shortest(cooked) or food[0]), ""
    if toxic:
        deadly = any(bp.DEADLY_CUE.search(sentence) for sentence in toxic)
        return ("deadly" if deadly else "toxic"), shortest(toxic), ""
    if med:
        return "medicine", shortest(med), ""
    return "none", "", ""


def title_of(url):
    path = urllib.parse.unquote(url.split("#")[0].split("/wiki/", 1)[-1])
    return path.replace("_", " ")


def one_text(title):
    """Full plain text of one article; the batch endpoint truncates to one page."""
    query = urllib.parse.urlencode({
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "extracts", "explaintext": "1", "exlimit": "1",
        "redirects": "1", "titles": title,
    })
    data = fetch("https://en.wikipedia.org/w/api.php?" + query)
    for page in data.get("query", {}).get("pages", []):
        if page.get("extract"):
            return page["extract"]
    return ""


def full_texts(titles):
    unique = sorted(set(titles))
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as fh:
            cache = json.load(fh)
    missing = [title for title in unique if title not in cache]
    texts = {title: cache.get(title, "") for title in unique}
    if missing:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for done, (title, text) in enumerate(zip(missing, pool.map(one_text, missing)), 1):
                texts[title] = text
                cache[title] = text
                if done % 40 == 0:
                    print("  texts:", done, "/", len(missing))
        with open(CACHE, "w", encoding="utf-8") as fh:
            json.dump(cache, fh)
    print("  texts:", len(texts), "/", len(unique), "| fetched now:", len(missing))
    return texts


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    groups = {}
    for group in index["groups"]:
        payload = json.load(open(os.path.join(OUT, group["key"] + ".json"), encoding="utf-8"))
        groups[group["key"]] = {
            "group": group,
            "families": {fam["n"]: fam["s"] for fam in payload["families"]},
        }

    plants = [(key, fam, plant) for key, state in groups.items()
              for fam, list_ in state["families"].items() for plant in list_]
    titles = [title_of(plant["u"]) for _, _, plant in plants]

    # the five that need a better title
    for page_title, (name, _order, _family, _h, _r, _t) in ALT.items():
        titles.append(page_title)

    print("plants:", len(plants), "| titles to read:", len(set(titles)))
    texts = full_texts(titles)
    print("full texts:", sum(1 for t in texts.values() if t))

    # fetch summaries for the five replacements
    added = 0
    for page_title, (name, order, family, habitats, regions, forms) in ALT.items():
        known = {plant["n"] for _, _, plant in plants}
        if name in known:
            continue
        summary = bp.fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                           urllib.parse.quote(page_title.replace(" ", "_")))
        if summary.get("__error__") or summary.get("type") in ("disambiguation", "no-extract"):
            print("  ! still no article for", page_title)
            continue
        url = (summary.get("content_urls", {}).get("desktop", {}).get("page")
               or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page_title.replace(" ", "_")))
        entry = {
            "n": summary.get("title") or name,
            "u": url,
            "d": bp.clean_extract(summary.get("extract") or ""),
            "h": habitats, "r": regions, "t": forms,
            "fam": family, "ord": order,
        }
        thumb = bp.image_url((summary.get("thumbnail") or {}).get("source"))
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bp.file_page(thumb)
        key = bp.slug(order)
        if key not in groups:            # an order whose every plant was lost earlier
            fresh = {"key": key, "num": "%02d" % (len(groups) + 1), "title": order,
                     "plants": 0, "families": 0, "photos": 0, "food": 0, "poison": 0}
            groups[key] = {"group": fresh, "families": {}}
            index["groups"].append(fresh)
        groups[key]["families"].setdefault(family, []).append(entry)
        plants.append((key, family, entry))
        added += 1
        time.sleep(1.2)
    print("added:", added)

    changed = 0
    distribution = {}
    for _key, _fam, plant in plants:
        text = texts.get(title_of(plant["u"]), "")
        ed, evidence, warning = verdict(text)
        plant["ed"] = ed
        if evidence:
            plant["eq"] = evidence
        else:
            plant.pop("eq", None)
        if warning:
            plant["ew"] = warning
        else:
            plant.pop("ew", None)
        distribution[ed] = distribution.get(ed, 0) + 1
        changed += 1
    print("reclassified:", changed)
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
    index["families"] = len({p["fam"] for state in groups.values() for fam in state["families"].values() for p in fam})
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
