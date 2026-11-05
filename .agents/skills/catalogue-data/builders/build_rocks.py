#!/usr/bin/env python3
"""Write docs/rocks/data/ from Wikipedia's list of rock types.

The list page is already organised by class — Igneous rocks, Sedimentary rocks,
Metamorphic rocks and Specific varieties — and gives every entry a one-line
description, so the builder reads it once and writes one shelf per class.
Each rock also gets a 250px photograph from the same API, fetched fifty titles
at a time and cached in tmp/.

    python3 .agents/skills/catalogue-data/builders/build_rocks.py

The raw list is cached in tmp/rocks-list.json and the thumbnails in
tmp/rocks-images.json, so a second run does not touch the network.
"""

import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = ("https://en.wikipedia.org/w/api.php?action=parse&page=List_of_rock_types"
       "&prop=text&format=json&formatversion=2")
IMAGE_API = "https://en.wikipedia.org/w/api.php"
CACHE = os.path.join("tmp", "rocks-list.json")
IMAGE_CACHE = os.path.join("tmp", "rocks-images.json")
OUT = os.path.join("docs", "rocks", "data")
UA = {"User-Agent": "MonkeyBlogRocks/1.0 (https://blog.odicforcesounds.com)"}

SECTIONS = [
    ("igneous", "Igneous rocks", "Igneous rocks",
     "Rocks that cooled from melt: the volcanic ones that reached the surface and the "
     "plutonic ones that stayed below it, from adakite to the granite family."),
    ("sedimentary", "Sedimentary rocks", "Sedimentary rocks",
     "Rocks built from pieces, from chemistry or from living things: sandstone, "
     "limestone, chalk, coal and the evaporites left when a sea dries."),
    ("metamorphic", "Metamorphic rocks", "Metamorphic rocks",
     "Rocks changed in the solid state by heat and pressure: slates, schists, gneisses, "
     "marbles and the high-grade rocks that remember a mountain belt."),
    ("varieties", "Specific varieties", "Specific varieties",
     "Named kinds that cut across the three classes: textures, ores and trade names "
     "that a geologist says instead of the family name."),
]

BANDS = [("A – C", "ABC"), ("D – F", "DEF"), ("G – I", "GHI"), ("J – L", "JKL"),
         ("M – O", "MNO"), ("P – R", "PQR"), ("S – U", "STU"), ("V – Z", "VWXYZ")]

BAND_NAMES = {"ABC": "A – C", "DEF": "D – F", "GHI": "G – I", "JKL": "J – L",
              "MNO": "M – O", "PQR": "P – R", "STU": "S – U", "VWXYZ": "V – Z"}


def page_html():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as handle:
            return json.load(handle)["parse"]["text"]
    request = urllib.request.Request(API, headers=UA)
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    return data["parse"]["text"]


def clean(fragment):
    text = re.sub(r"<sup[^>]*>.*?</sup>", "", fragment, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def band(name):
    letter = name[0:1].upper()
    if letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return "VWXYZ"
    for code in ("ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWXYZ"):
        if letter in code:
            return code
    return "VWXYZ"


def items_of(section):
    found = []
    for chunk in re.findall(r"<li>(.*?)</li>", section, re.S):
        if "<ul" in chunk or "<ol" in chunk:
            continue
        anchor = re.search(r'<a href="/wiki/([^"#]+)"[^>]*>(.*?)</a>', chunk, re.S)
        if not anchor:
            continue
        name = clean(anchor.group(2))
        if not name or len(name) > 60:
            continue
        rest = clean(chunk[anchor.end():])
        description = re.sub(r"^[\s\u2013\u2014\-:·]+", "", rest)
        description = re.sub(r"\s+-\s+.*$", "", description)
        description = description[:180].strip()
        href = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(
            urllib.parse.unquote(anchor.group(1)), safe="/()_,'-.")
        found.append({"n": name, "u": href, "d": description})
    return found


def normal_thumb(url):
    """The commons file itself: no tracking query, no thumbnail proxy host."""
    url = url.split("?", 1)[0]
    return url.replace("https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")


def images(names):
    """A 250px thumbnail per article, fifty titles per request."""
    if os.path.exists(IMAGE_CACHE):
        with open(IMAGE_CACHE, encoding="utf-8") as handle:
            return json.load(handle)

    found = {}
    names = sorted(set(names))
    for start in range(0, len(names), 50):
        batch = names[start:start + 50]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "pageimages", "piprop": "thumbnail", "pithumbsize": "250",
            "redirects": "1", "titles": "|".join(batch),
        })
        request = urllib.request.Request(IMAGE_API + "?" + query, headers=UA)
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        payload = data.get("query", {})
        by_title = {}
        for page in payload.get("pages", []):
            thumb = normal_thumb((page.get("thumbnail") or {}).get("source", ""))
            if thumb:
                by_title[page.get("title", "")] = thumb
        alias = {}
        for item in payload.get("normalized", []) + payload.get("redirects", []):
            alias[item.get("from", "")] = item.get("to", "")
        for name in batch:
            title = alias.get(alias.get(name, name), name)
            if by_title.get(title):
                found[name] = by_title[title]
            elif by_title.get(name):
                found[name] = by_title[name]
        print("images: %d of %d titles resolved" % (len(found), min(start + 50, len(names))))

    os.makedirs(os.path.dirname(IMAGE_CACHE), exist_ok=True)
    with open(IMAGE_CACHE, "w", encoding="utf-8") as handle:
        json.dump(found, handle, ensure_ascii=False)
    return found


def main():
    source = page_html()
    sections = {}
    for match in re.finditer(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|$)", source, re.S):
        title = clean(match.group(1))
        sections[title] = items_of(match.group(2))

    per_shelf = []
    seen = set()
    for key, title, heading, blurb in SECTIONS:
        entries = []
        for item in sections.get(heading, []):
            if item["n"].lower() in seen:
                continue
            seen.add(item["n"].lower())
            entries.append(item)
        if not entries:
            print("  ! no entries for", title, file=sys.stderr)
            continue
        entries.sort(key=lambda item: item["n"].lower())
        per_shelf.append((key, title, blurb, entries))

    pictures = images([item["n"] for _key, _title, _blurb, entries in per_shelf
                       for item in entries])

    os.makedirs(OUT, exist_ok=True)
    catalogue = []
    total = 0
    for number, (key, title, blurb, entries) in enumerate(per_shelf, start=1):
        for item in entries:
            item["i"] = pictures.get(item["n"], "")
        groups = []
        for _label, code in BANDS:
            members = [item for item in entries if band(item["n"]) == code]
            if members:
                groups.append({"name": BAND_NAMES[code], "items": members})

        shelf = {
            "key": key,
            "num": "%02d" % number,
            "title": title,
            "blurb": blurb,
            "rocks": len(entries),
            "groups": groups,
        }
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as handle:
            json.dump(shelf, handle, separators=(",", ":"), ensure_ascii=False)
        catalogue.append({
            "key": key,
            "num": "%02d" % number,
            "title": title,
            "slug": key,
            "blurb": blurb,
            "rocks": len(entries),
        })
        total += len(entries)
        print("%-12s %3d rocks | %d groups | %d photos"
              % (key, len(entries), len(groups),
                 sum(1 for item in entries if item["i"])))

    manifest = {
        "source": "en.wikipedia.org + upload.wikimedia.org",
        "licence": "CC BY-SA 4.0",
        "generated": "2026-11-05",
        "rocks": total,
        "photos": sum(1 for _key, _t, _b, entries in per_shelf for item in entries if item["i"]),
        "categories": catalogue,
    }
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, separators=(",", ":"), ensure_ascii=False)
    print("index.json: %d rocks | %d shelves | %d photos"
          % (total, len(catalogue), manifest["photos"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
