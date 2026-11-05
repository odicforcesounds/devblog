#!/usr/bin/env python3
"""Write docs/cars/data/ from Wikidata's car models and their Wikipedia leads.

Wikidata lists the car models that have an English Wikipedia article and a
photograph; Wikipedia supplies the sentence and, in most leads, the year the
model was introduced. The two are joined by article, split into era shelves,
and written one file per shelf with the pictures as 250px Wikimedia thumbnails.

    python3 .agents/skills/catalogue-data/builders/build_cars.py

Caches live in tmp/: cars-all.json (the Wikidata rows), cars-makers.json (maker
labels), cars-text.json (one lead per article), cars-dates.json (the inception
dates Wikidata does have). A second run does not touch the network for what it
already fetched.
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "MonkeyBlogCars/1.0 (https://blog.odicforcesounds.com)"}
ALL = os.path.join("tmp", "cars-all.json")
MAKERS = os.path.join("tmp", "cars-makers.json")
TEXT = os.path.join("tmp", "cars-text.json")
DATES = os.path.join("tmp", "cars-dates.json")
OUT = os.path.join("docs", "cars", "data")
WIKI = "https://en.wikipedia.org/w/api.php"

BANDS = [("A – C", "ABC"), ("D – F", "DEF"), ("G – I", "GHI"), ("J – L", "JKL"),
         ("M – O", "MNO"), ("P – R", "PQR"), ("S – U", "STU"), ("V – Z", "VWXYZ")]

SHELVES = [
    ("pioneers", "Pioneers and veteran cars",
     "The first cars that ran: the Benz Patent-Motorwagen and the steam, electric and petrol "
     "machines that followed it, before mass production existed.", 1800, 1904),
    ("brass", "Brass era",
     "The brass era, when the steering wheel replaced the tiller and the electric starter "
     "began to retire the crank.", 1905, 1918),
    ("vintage", "Vintage years",
     "The vintage years, when closed bodies, four-wheel brakes and the assembly line turned "
     "the car from a rich man's toy into transport.", 1919, 1930),
    ("prewar", "Before the war",
     "Streamlined shapes and the first cheap V8s, up to the last civilian models built "
     "before 1945.", 1931, 1945),
    ("postwar", "After the war",
     "Post-war recovery and the great expansion: family saloons, cheap sports cars and the "
     "first compacts.", 1946, 1969),
    ("modern", "Modern classics",
     "The modern classics: fuel injection, hatchbacks, turbocharging and the safety "
     "revolution of the 1970s and 1980s.", 1970, 1989),
    ("contemporary", "The contemporary years",
     "The contemporary years: airbags, engine electronics, diesel and the first hybrids.", 1990, 2009),
    ("today", "The present",
     "What the manufacturers build now: electric drivetrains, crossovers and software on "
     "wheels.", 2010, 2026),
    ("undated", "Without a production year",
     "Models whose article and record give no year to file them by, kept here rather than "
     "dropped from the index.", None, None),
]

ANY_YEAR = re.compile(r"\b(18[0-9]\d|19\d\d|20[0-2]\d)\b")
LEAD_YEAR = [
    re.compile(r"\b(?:from|between)\s+(1[89]\d\d|20[0-2]\d)\b", re.I),
    re.compile(r"\b(?:introduced|launched|unveiled|revealed|presented|produced|manufactured|"
               r"built|sold|released|debuted|entered production)\b[^.]{0,80}?"
               r"\b(1[89]\d\d|20[0-2]\d)\b", re.I),
]


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False)


def fetch_leads(titles, cache):
    pending = [title for title in titles if title not in cache]
    print("leads: %d to fetch, %d cached" % (len(pending), len(titles) - len(pending)), flush=True)
    for start in range(0, len(pending), 20):
        batch = pending[start:start + 20]
        query = urllib.parse.urlencode({
            "action": "query", "prop": "extracts", "exintro": "1", "explaintext": "1",
            "exchars": "500", "redirects": "1", "format": "json", "formatversion": "2",
            "titles": "|".join(batch),
        })
        for attempt in range(3):
            try:
                with urllib.request.urlopen(
                        urllib.request.Request(WIKI + "?" + query, headers=UA), timeout=60) as response:
                    pages = json.load(response)["query"]["pages"]
                break
            except (urllib.error.HTTPError, urllib.error.URLError, KeyError):
                time.sleep(3)
        else:
            continue
        for page in pages:
            cache[page.get("title", "")] = (page.get("extract") or "").strip()
        for title in batch:
            cache.setdefault(title, "")
        if start % 200 == 0:
            save(TEXT, cache)
            print("  %d/%d" % (min(start + 20, len(pending)), len(pending)), flush=True)
    save(TEXT, cache)
    return cache


def year_of(text, title):
    """The production year the lead states, never a number the model is named after."""
    numbered = set(re.findall(r"\d{3,4}", title))
    for pattern in LEAD_YEAR:
        for match in pattern.finditer(text):
            if match.group(1) not in numbered:
                return int(match.group(1))
    for match in ANY_YEAR.finditer(text):
        if match.group(1) not in numbered:
            return int(match.group(1))
    return None


def sentence(text, title):
    text = re.sub(r"\s+", " ", text).strip()
    first = re.split(r"(?<=[.!?])\s", text)[0] if text else ""
    subject = re.match(r"^(?:The )?%s(?: \([^)]*\))*\s+(?:is|was|are|were)\s+(.*)$"
                       % re.escape(title), first)
    if subject:
        rest = subject.group(1).strip()
        first = rest[:1].upper() + rest[1:]
    first = re.sub(r"\[[^\]]*\]", "", first)
    first = re.sub(r"\(\s*[/;][^)]*\)", "", first)
    first = first.strip(" ,;")
    if len(first) > 175:
        first = first[:172].rsplit(" ", 1)[0] + "…"
    return first


def photo(file_name):
    name = file_name.replace(" ", "_")
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    quoted = urllib.parse.quote(name)
    return ("https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/250px-%s"
            % (digest[0], digest[:2], quoted, quoted))


def band(name):
    letter = re.sub(r"^(The|A|An) ", "", name)[:1].upper()
    if letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return "VWXYZ"
    for _label, code in BANDS:
        if letter in code:
            return code
    return "VWXYZ"


def shelf_of(year):
    if year is None:
        return "undated"
    for key, _title, _blurb, low, high in SHELVES:
        if low is not None and low <= year <= high:
            return key
    return "undated"


def main():
    rows = load(ALL, [])
    if not rows:
        print("missing %s: run the Wikidata query first" % ALL, file=sys.stderr)
        return 1
    makers = load(MAKERS, {})
    dated = load(DATES, {})
    cache = load(TEXT, {})
    cache = fetch_leads([row["t"] for row in rows], cache)

    seen = set()
    cars = []
    for row in rows:
        key = row["u"].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        name = row["t"]
        if len(name) < 3 or name.isdigit():
            continue
        text = cache.get(name, "")
        year = dated.get(row["q"])
        if not year and text:
            year = year_of(text, name)
        description = sentence(text, name) if text else ""
        maker = makers.get(row["m"], "")
        line = []
        if year:
            line.append(str(year))
        if maker:
            line.append(maker)
        lead = " · ".join(line)
        if description:
            description = (lead + " — " + description) if lead else description
        elif lead:
            description = lead
        cars.append({
            "n": name,
            "u": row["u"],
            "y": year,
            "d": description[:210],
            "i": photo(row["f"]) if row["f"] else "",
            "s": shelf_of(year),
        })

    print("cars: %d | with year %d | with photo %d"
          % (len(cars), sum(1 for car in cars if car["y"]),
             sum(1 for car in cars if car["i"])), flush=True)

    os.makedirs(OUT, exist_ok=True)
    catalogue = []
    written = 0
    for number, (key, title, blurb, _low, _high) in enumerate(SHELVES, start=1):
        members = [car for car in cars if car["s"] == key]
        members.sort(key=lambda car: re.sub(r"^(The|A|An) ", "", car["n"]).lower())
        groups = []
        for label, code in BANDS:
            items = [car for car in members if band(car["n"]) == code]
            if not items:
                continue
            groups.append({"name": label, "items": [{
                "n": car["n"], "u": car["u"], "d": car["d"],
                **({"i": car["i"]} if car["i"] else {}),
            } for car in items]})
        shelf = {
            "key": key, "num": "%02d" % number, "title": title, "blurb": blurb,
            "cars": len(members), "groups": groups,
        }
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as handle:
            json.dump(shelf, handle, separators=(",", ":"), ensure_ascii=False)
        catalogue.append({"key": key, "num": "%02d" % number, "title": title,
                          "slug": key, "blurb": blurb, "cars": len(members)})
        written += len(members)
        print("%-13s %4d cars | %d groups | %d photos"
              % (key, len(members), len(groups),
                 sum(1 for car in members if car["i"])), flush=True)

    manifest = {
        "source": "wikidata.org + en.wikipedia.org + upload.wikimedia.org",
        "licence": "CC BY-SA 4.0",
        "generated": time.strftime("%Y-%m-%d"),
        "cars": written,
        "photos": sum(1 for key, _t, _b, _l, _h in SHELVES
                      for car in cars if car["s"] == key and car["i"]),
        "categories": catalogue,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, separators=(",", ":"), ensure_ascii=False)
    print("index.json: %d cars | %d shelves | %d photos"
          % (written, len(catalogue), manifest["photos"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
