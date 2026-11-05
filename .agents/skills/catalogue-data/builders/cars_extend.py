#!/usr/bin/env python3
"""Add the car models the shelves lack.

build_cars.py reads Wikidata's whole model list; this pass reads the finished
shelves, asks Wikipedia only for the models below, derives the year from the
lead with the builder's own rules, files each under its era shelf and A–Z band,
and recomputes the counts. A model already present is skipped, so a second run
changes nothing.

    python3 .agents/skills/catalogue-data/builders/cars_extend.py
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

import build_cars as bc

OUT = bc.OUT

EXTRA = """
Rimac Nevera
Lucid Air
Rivian R1T
Ford F-150 Lightning
Hyundai Ioniq 5
Kia EV6
BYD Atto 3
Nio ET7
XPeng P7
Polestar 2
Volkswagen ID.3
Peugeot e-208
Fiat 500e
Honda e
Mazda MX-30
Toyota bZ4X
Subaru Solterra
Nissan Ariya
GMC Hummer EV
Tesla Semi
Tesla Cybertruck
Tesla Roadster (second generation)
Mercedes-Benz EQS
BMW iX
Audi e-tron GT
Lotus Eletre
Rolls-Royce Spectre
Cadillac Lyriq
Ford Mustang Mach-E
Volkswagen ID. Buzz
Jeep Avenger
Dacia Spring
MG4 EV
VinFast VF 8
Fisker Ocean
Aptera (solar electric vehicle)
Koenigsegg Jesko
SSC Tuatara
Hennessey Venom F5
McLaren Speedtail
Aston Martin Valkyrie
Mercedes-AMG One
Gordon Murray T.50
Czinger 21C
Automobili Pininfarina Battista
DeLorean Alpha5
Tatra 603
Tatra 97
Škoda Popular
Wartburg 353
Trabant 601
Zastava 750
FSO Polonez
GAZ Chaika
GAZ Volga
Moskvitch 408
Hindustan Ambassador
Premier Padmini
Paykan
Saipa Pride
Proton Saga
Perodua Myvi
Daihatsu Copen
Suzuki Alto
Maruti 800
Tata Nano
Mahindra Thar
Renault Kwid
Dacia Logan
Lada Granta
UAZ Patriot
Chery QQ
Geely Emgrand
Great Wall Haval H6
Changan CS75
Tata Indica
Hyundai Santro
Auto Union Type C
Mercedes-Benz 300 SLR
Jaguar D-Type
Ford GT40
Porsche 917
Ferrari 250 GTO
Lotus Seven
"""

YEAR_HINT = {"Volkswagen ID. Buzz": 2022}


def summary(title):
    return bc_fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" +
                    urllib.parse.quote(title.replace(" ", "_")))


def bc_fetch(url, tries=4):
    import urllib.error
    import urllib.request
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=bc.UA), timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            return {"__error__": "HTTP %s" % exc.code}
        except Exception as exc:  # noqa: BLE001
            if attempt < tries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return {"__error__": str(exc)}
    return {"__error__": "gave up"}


def picture(page):
    thumb = (page.get("thumbnail") or {}).get("source", "")
    if not thumb:
        return ""
    thumb = thumb.split("?")[0]
    thumb = thumb.replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
    return re.sub(r"/\d+px-", "/250px-", thumb, count=1)


def first_sentence(text, name):
    held = text.replace(name, "\x00")
    first = re.split(r"(?<=[.!?])\s", held)[0].replace("\x00", name)
    first = re.sub(r"^The %s (?:is|was|are|were)\s+" % re.escape(name), "", first)
    first = re.sub(r"\s{2,}", " ", first).strip()
    if first:
        first = first[:1].upper() + first[1:]
    return first[:172].rsplit(" ", 1)[0] + "…" if len(first) > 175 else first


def main():
    manifest = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    shelves = {}
    for entry in manifest["categories"]:
        doc = json.load(open(os.path.join(OUT, entry["key"] + ".json"), encoding="utf-8"))
        shelves[entry["key"]] = {"entry": entry, "doc": doc,
                                 "groups": {group["name"]: group["items"] for group in doc["groups"]}}

    existing = {item["u"] for state in shelves.values()
                for items in state["groups"].values() for item in items}
    names = {item["n"].lower() for state in shelves.values()
             for items in state["groups"].values() for item in items}
    labels = {label: code for label, code in bc.BANDS}

    added = 0
    for title in [line.strip() for line in EXTRA.strip().splitlines() if line.strip()]:
        page = summary(title)
        if "__error__" in page or page.get("type") in ("disambiguation", "no-extract"):
            print("  !", title, "->", page.get("__error__", page.get("type", "missing")))
            continue
        url = page.get("content_urls", {}).get("desktop", {}).get("page") or \
            "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        name = page.get("title") or title
        if url in existing or name.lower() in names:
            print("  =", name, "already shelved")
            continue
        extract = page.get("extract") or ""
        year = YEAR_HINT.get(name) or bc.year_of(extract, name)
        shelf = bc.shelf_of(year)
        sentence = first_sentence(extract, name) if extract else ""
        lead = str(year) if year else ""
        description = (lead + " — " + sentence) if lead and sentence else (lead or sentence)
        entry = {"n": name, "u": url, "d": description[:210]}
        photo = picture(page)
        if photo:
            entry["i"] = photo
        code = bc.band(name)
        label = next(label for label, band_code in bc.BANDS if band_code == code)
        shelves[shelf]["groups"].setdefault(label, []).append(entry)
        existing.add(url)
        names.add(name.lower())
        added += 1
        print("  +", name, "->", shelves[shelf]["entry"]["title"], "/", label)

    total = photos = 0
    for key, state in shelves.items():
        doc = state["doc"]
        doc["groups"] = [
            {"name": label, "items": sorted(state["groups"][label],
                                            key=lambda car: re.sub(r"^(The|A|An) ", "", car["n"]).lower())}
            for label, _code in bc.BANDS if state["groups"].get(label)
        ]
        cars = sum(len(group["items"]) for group in doc["groups"])
        found = sum(1 for group in doc["groups"] for item in group["items"] if item.get("i"))
        doc["cars"] = cars
        state["entry"]["cars"] = cars
        total += cars
        photos += found
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as handle:
            json.dump(doc, handle, separators=(",", ":"), ensure_ascii=False)
    manifest["cars"] = total
    manifest["photos"] = photos
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, separators=(",", ":"), ensure_ascii=False)
    print("added:", added)
    print("index:", {"cars": total, "photos": photos, "shelves": len(manifest["categories"])})


if __name__ == "__main__":
    sys.exit(main())
