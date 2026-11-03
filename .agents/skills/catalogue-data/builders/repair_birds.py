#!/usr/bin/env python3
"""Fetch only the species that are missing from docs/birds/data/, then merge.

The first build lost the tail of the list to HTTP 429 (Wikimedia asks for
patience rather than concurrency). This walks the SPEC in build_birds.py beside
this file,
skips everything already written, and adds the rest one request at a time with
a long backoff, so a rebuild never has to start from zero.
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
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, "tmp")
import build_birds as bb  # noqa: E402  (shares SPEC, cleaners and URL builders)

OUT = bb.OUT
UA = bb.UA


def slow_fetch(url, tries=6):
    """One polite request: 429 and 5xx sleep for longer instead of giving up."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                wait = 8 * (attempt + 1)
                print("      %s, waiting %ss" % (exc.code, wait))
                time.sleep(wait)
                continue
            return {"__error__": "HTTP %s" % exc.code}
        except Exception as exc:  # noqa: BLE001
            if attempt < tries - 1:
                time.sleep(4 * (attempt + 1))
                continue
            return {"__error__": str(exc)}
    return {"__error__": "gave up"}


def spec_rows():
    rows = []
    for line in bb.SPEC.strip().splitlines():
        bits = [b.strip() for b in line.split("|")]
        if len(bits) < 3:
            continue
        bits += [""] * (6 - len(bits))
        rows.append({
            "title": bits[0], "order": bits[1], "family": bits[2],
            "habitats": [h for h in bits[3].split(",") if h],
            "regions": [r for r in bits[4].split(",") if r],
            "traits": [t for t in bits[5].split(",") if t],
        })
    return rows


def load_groups(index):
    groups = {}
    for group in index["groups"]:
        path = os.path.join(OUT, group["key"] + ".json")
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        families = {}
        for fam in payload["families"]:
            families[fam["n"]] = fam["s"]
        groups[group["key"]] = {"group": group, "families": families}
    return groups


def wikidata(qids):
    status, taxon, length_seen, mass_seen = {}, {}, {}, {}
    for start in range(0, len(qids), 30):
        batch = qids[start:start + 30]
        query = """
SELECT ?item ?taxon ?statusLabel ?len ?lenUnitLabel ?mass ?massUnitLabel WHERE {
  VALUES ?item { %s }
  OPTIONAL { ?item wdt:P141 ?status }
  OPTIONAL { ?item wdt:P225 ?taxon }
  OPTIONAL { ?item p:P2043/psv:P2043 ?lv .
             ?lv wikibase:quantityAmount ?len ; wikibase:quantityUnit ?lenUnit }
  OPTIONAL { ?item p:P2067/psv:P2067 ?mv .
             ?mv wikibase:quantityAmount ?mass ; wikibase:quantityUnit ?massUnit }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}""" % " ".join("wd:" + q for q in batch)
        data = slow_fetch("https://query.wikidata.org/sparql?" +
                          urllib.parse.urlencode({"format": "json", "query": query}))
        for binding in data.get("results", {}).get("bindings", []):
            qid = binding["item"]["value"].rsplit("/", 1)[-1]
            if "statusLabel" in binding:
                status.setdefault(qid, binding["statusLabel"]["value"])
            if "taxon" in binding and " " in binding["taxon"]["value"]:
                taxon.setdefault(qid, binding["taxon"]["value"])
            if "len" in binding:
                unit = binding.get("lenUnitLabel", {}).get("value", "")
                try:
                    value = float(binding["len"]["value"])
                except ValueError:
                    value = 0
                cm = value * 100 if unit == "metre" else value / 10 if unit == "millimetre" else value
                if 3 <= cm <= 300:
                    length_seen.setdefault(qid, []).append(round(cm, 1))
            if "mass" in binding:
                unit = binding.get("massUnitLabel", {}).get("value", "")
                try:
                    value = float(binding["mass"]["value"])
                except ValueError:
                    value = 0
                grams = value
                if unit == "kilogram":
                    grams = value * 1000
                elif unit == "milligram":
                    grams = value / 1000
                if 2 <= grams <= 200000:
                    mass_seen.setdefault(qid, []).append(round(grams, 1))
    return (status, taxon,
            {q: max(v) for q, v in length_seen.items()},
            {q: max(v) for q, v in mass_seen.items()})


def audio_urls(titles):
    urls = {}
    for start in range(0, len(titles), 40):
        batch = titles[start:start + 40]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "imageinfo", "iiprop": "url", "titles": "|".join(batch),
        })
        data = slow_fetch("https://en.wikipedia.org/w/api.php?" + query)
        found = data.get("query", {})
        for page in found.get("pages", []):
            info = page.get("imageinfo") or []
            if info and info[0].get("url"):
                url = info[0]["url"].split("?utm_source")[0]
                urls[page["title"]] = url
                urls[page["title"].replace(" ", "_")] = url
        for norm in found.get("normalized", []):
            if norm.get("to") in urls:
                urls[norm["from"]] = urls[norm["to"]]
    return urls


def main():
    with open(os.path.join(OUT, "index.json"), encoding="utf-8") as fh:
        index = json.load(fh)
    groups = load_groups(index)
    present = set()
    for state in groups.values():
        for birds in state["families"].values():
            for bird in birds:
                present.add(bird["n"])

    missing = [row for row in spec_rows() if row["title"] not in present]
    print("already written:", len(present), "| missing:", len(missing))
    if not missing:
        return 0

    fetched, failed = [], []
    for row in missing:
        page = row["title"].replace(" ", "_")
        summary = slow_fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                             urllib.parse.quote(page))
        if "__error__" in summary or summary.get("type") in ("disambiguation", "no-extract"):
            failed.append((row["title"], summary.get("__error__", summary.get("type"))))
            print("  !", row["title"], "->", failed[-1][1])
            time.sleep(1.5)
            continue
        media = slow_fetch("https://en.wikipedia.org/api/rest_v1/page/media-list/" +
                           urllib.parse.quote(page))
        audio = None
        for item in media.get("items", []):
            name = item.get("title", "")
            if item.get("type") == "audio" and name.lower().endswith((".ogg", ".oga", ".wav", ".mp3", ".flac")):
                audio = name
                break
        fetched.append((row, summary, audio))
        print("  +", row["title"])
        time.sleep(1.2)

    titles = sorted({audio for _, _, audio in fetched if audio})
    urls = audio_urls(titles) if titles else {}
    qids = [summary.get("wikibase_item") for _, summary, _ in fetched if summary.get("wikibase_item")]
    status, taxon, length, mass = wikidata(qids) if qids else ({}, {}, {}, {})

    for row, summary, audio in fetched:
        qid = summary.get("wikibase_item")
        thumb = bb.image_url((summary.get("thumbnail") or {}).get("source"))
        entry = {
            "n": summary.get("title") or row["title"],
            "s": taxon.get(qid, "") if qid else "",
            "u": (summary.get("content_urls", {}).get("desktop", {}).get("page")
                  or "https://en.wikipedia.org/wiki/" + urllib.parse.quote(row["title"].replace(" ", "_"))),
            "d": bb.clean_extract(summary.get("extract") or ""),
            "h": row["habitats"],
            "r": row["regions"],
            "t": row["traits"],
            "fam": row["family"],
            "ord": row["order"],
        }
        if thumb:
            entry["i"] = thumb
            entry["ic"] = bb.file_page(thumb)
        if audio and audio in urls:
            entry["a"] = urls[audio]
            entry["an"] = "song or call"
        if not entry["s"]:
            binomial = re.search(r"\(([A-Z][a-z]+ [a-z-]+)\)", summary.get("extract") or "")
            if binomial:
                entry["s"] = binomial.group(1)
        if qid and qid in status:
            entry["st"] = status[qid]
        if qid and qid in length:
            entry["l"] = length[qid]
        if qid and qid in mass:
            entry["m"] = mass[qid]
        key = bb.slug(row["order"])
        if key not in groups:      # an order whose every species was lost to the rate limit
            groups[key] = {"group": {"key": key, "num": "%02d" % (len(groups) + 1),
                                      "title": row["order"]}, "families": {}}
            index["groups"].append(groups[key]["group"])
        groups[key]["families"].setdefault(row["family"], []).append(entry)

    for state in groups.values():
        state["group"]["families"] = len(state["families"])
        for fam in state["families"]:
            state["families"][fam].sort(key=lambda b: b["n"])

    for key, state in groups.items():
        payload = {
            "key": key,
            "title": state["group"]["title"],
            "families": [
                {"n": fam, "c": len(state["families"][fam]), "s": state["families"][fam]}
                for fam in sorted(state["families"], key=lambda f: (-len(state["families"][f]), f))
            ],
        }
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)

    print("merged:", len(fetched), "| still failing:", failed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
