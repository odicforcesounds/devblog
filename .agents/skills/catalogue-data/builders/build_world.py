#!/usr/bin/env python3
"""Build the world catalogue JSON from the GeoNames dump.

One shelf per country: the shelf holds the country's first-level regions as
groups, and every populated place of 500 people or more as an entry. Names,
populations and the place pages come from GeoNames; nothing here is invented.
The dump is cached in tmp/world/ and downloaded only when it is missing.
Writes docs/world/data/index.json and one file per country. Re-runnable.
"""

import json
import os
import sys
import unicodedata
import urllib.request
import zipfile

OUT = "docs/world/data"
CACHE = "tmp/world"
BASE = "https://download.geonames.org/export/dump/"

CONTINENTS = [
    ("AF", "Africa"),
    ("AS", "Asia"),
    ("EU", "Europe"),
    ("NA", "North America"),
    ("OC", "Oceania"),
    ("SA", "South America"),
    ("AN", "Antarctica"),
]
CONTINENT_NAME = dict(CONTINENTS)
CONTINENT_ORDER = {code: i for i, (code, _) in enumerate(CONTINENTS)}

SOURCE_SHAPE = (
    "GeoNames, a dump of every populated place the project records, "
    "published under CC BY 4.0"
)


def fetch(name):
    path = os.path.join(CACHE, name)
    if os.path.exists(path):
        return path
    os.makedirs(CACHE, exist_ok=True)
    url = BASE + name
    print("fetching " + url, file=sys.stderr)
    with urllib.request.urlopen(url, timeout=900) as response:
        with open(path, "wb") as handle:
            handle.write(response.read())
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as archive:
            archive.extractall(CACHE)
    return path


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read().splitlines()


def tsv_rows(path):
    for line in read_lines(path):
        if not line or line.startswith("#"):
            continue
        yield line.split("\t")


def load_countries():
    by_iso = {}
    for row in tsv_rows(fetch("countryInfo.txt")):
        if len(row) < 9:
            continue
        iso, name, continent = row[0], row[4], row[8]
        if not iso or continent not in CONTINENT_NAME:
            continue
        by_iso[iso] = (name, continent)
    return by_iso


def load_regions():
    names = {}
    for row in tsv_rows(fetch("admin1CodesASCII.txt")):
        if len(row) < 2:
            continue
        names[row[0]] = row[1]
    return names


def kind_of(code, population):
    if code == "PPLC":
        return "capital"
    if population >= 100000:
        return "city"
    if population >= 10000:
        return "town"
    return "village"


def load_places(countries, regions):
    path = fetch("cities500.zip")
    listing = os.path.join(CACHE, "cities500.txt")
    if not os.path.exists(listing):
        with zipfile.ZipFile(path) as archive:
            archive.extractall(CACHE)
    places = {}
    for line in read_lines(listing):
        row = line.split("\t")
        if len(row) < 15:
            continue
        name, code, iso, admin1, population = row[1], row[7], row[8], row[10], row[14]
        if iso not in countries or not name:
            continue
        try:
            population = int(population or 0)
        except ValueError:
            population = 0
        region = regions.get("%s.%s" % (iso, admin1)) or countries[iso][0]
        places.setdefault(iso, []).append({
            "id": row[0],
            "n": name,
            "r": region,
            "p": population,
            "t": kind_of(code, population),
        })
    return places


def dedupe(entries):
    seen = {}
    for entry in entries:
        seen[entry["n"]] = seen.get(entry["n"], 0) + 1
    used = set()
    for entry in entries:
        name = entry["n"]
        if seen[name] > 1:
            name = "%s · %s" % (name, entry["r"])
            if name in used:
                name = "%s · %s" % (name, entry["p"])
        base, suffix = name, 2
        while name in used:
            name = "%s (%d)" % (base, suffix)
            suffix += 1
        used.add(name)
        entry["n"] = name
    return entries


def fold(text):
    """The letters a search box can type: no accents, no case."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()


def main():
    countries = load_countries()
    regions = load_regions()
    places = load_places(countries, regions)
    search = {}

    os.makedirs(OUT, exist_ok=True)
    for stale in os.listdir(OUT):
        if stale.endswith(".json"):
            os.remove(os.path.join(OUT, stale))

    ordered = sorted(
        countries,
        key=lambda iso: (
            CONTINENT_ORDER[countries[iso][1]],
            countries[iso][0].lower(),
        ),
    )

    categories = []
    total_places = 0
    total_regions = 0
    number = 0

    for iso in ordered:
        entries = places.get(iso, [])
        if not entries:
            continue
        country_name, continent = countries[iso]
        entries = dedupe(sorted(entries, key=lambda e: -e["p"]))

        for entry in entries:
            initial = fold(entry["n"])[:1]
            bucket = initial if "a" <= initial <= "z" else "other"
            search.setdefault(bucket, []).append(
                [entry["n"], iso.lower(), entry["r"], entry["p"], int(entry["id"])]
            )

        groups = {}
        for entry in entries:
            groups.setdefault(entry["r"], []).append(entry)
        ordered_groups = sorted(groups.items(), key=lambda kv: -sum(e["p"] for e in kv[1]))

        key = iso.lower()
        number += 1
        categories.append({
            "key": key,
            "num": "%02d" % number,
            "title": country_name,
            "continent": CONTINENT_NAME[continent],
            "regions": len(ordered_groups),
            "places": len(entries),
            "slug": key,
            "blurb": (
                "%s: %s places of 500 people or more across %s regions, "
                "the largest town first."
                % (
                    CONTINENT_NAME[continent],
                    "{:,}".format(len(entries)),
                    len(ordered_groups),
                )
            ),
        })

        payload = {
            "key": key,
            "num": "%02d" % number,
            "title": country_name,
            "blurb": (
                "Every place GeoNames records above 500 people in %s: %s towns "
                "and villages, grouped by region and ordered by population."
                % (country_name, "{:,}".format(len(entries)))
            ),
            "groups": [
                {
                    "name": region,
                    "items": [
                        {
                            "n": entry["n"],
                            "u": "https://www.geonames.org/%s" % entry["id"],
                            "p": entry["p"],
                            "t": entry["t"],
                        }
                        for entry in items
                    ],
                }
                for region, items in ordered_groups
            ],
        }
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))

        total_places += len(entries)
        total_regions += len(ordered_groups)

    search_dir = os.path.join(OUT, "search")
    os.makedirs(search_dir, exist_ok=True)
    buckets = [chr(code) for code in range(ord("a"), ord("z") + 1)] + ["other"]
    for bucket in buckets:
        rows = sorted(search.get(bucket, []), key=lambda row: -row[3])
        with open(os.path.join(search_dir, bucket + ".json"), "w", encoding="utf-8") as handle:
            json.dump(rows, handle, ensure_ascii=False, separators=(",", ":"))

    index = {
        "source": "geonames.org",
        "licence": "CC BY 4.0",
        "countries": len(categories),
        "regions": total_regions,
        "places": total_places,
        "categories": categories,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, separators=(",", ":"))

    print(
        "countries %d | regions %d | places %d | files %d"
        % (len(categories), total_regions, total_places, len(categories) + 1)
    )


if __name__ == "__main__":
    main()
