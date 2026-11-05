#!/usr/bin/env python3
"""Add the dance and martial styles the shelves lack.

build_dance.py writes the catalogue from its taxonomy; this pass reads the
finished shelves, asks Wikipedia only for the articles below, files each under
its shelf and group with the culture and era this catalogue curates, and
recomputes the counts. An article already present is skipped.

    python3 .agents/skills/catalogue-data/builders/dance_extend.py
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import sys

import build_dance as bd

OUT = bd.OUT

# shelf key | group | article | culture | era
EXTRA = [
    ("ritual", "Temple dance of India", "Bhagavata Mela", "Tamil Nadu, India", "16th c."),
    ("ritual", "Temple dance of India", "Vilasini Natyam", "Andhra Pradesh, India", "19th c. record"),
    ("ritual", "Southeast Asian courts", "Lakhon", "Thailand", "Ayutthaya court"),
    ("ritual", "East Asian ritual", "Bon Odori", "Japan", "medieval"),
    ("ritual", "East Asian ritual", "Eisa", "Okinawa, Japan", "19th c."),
    ("ritual", "Trance, possession and religion", "Vimbuza", "Malawi", "recorded 19th c."),
    ("court", "Ballet and its descendants", "Vaganova method", "Russia", "1930s"),
    ("court", "Ballet and its descendants", "Cecchetti method", "Italy and England", "1920s"),
    ("court", "The modern schools", "Judson Dance Theater", "United States", "1962"),
    ("court", "The modern schools", "Release technique", "United States", "1970s"),
    ("folk", "Europe", "Krakowiak", "Poland", "19th c."),
    ("folk", "Europe", "Oberek", "Poland", "17th c."),
    ("folk", "Europe", "Schuhplattler", "Bavaria", "19th c."),
    ("folk", "Europe", "Halling", "Norway", "medieval"),
    ("folk", "Europe", "Polska", "Sweden", "16th c."),
    ("folk", "The Americas", "Chacarera", "Argentina", "19th c."),
    ("folk", "The Americas", "Festejo", "Peru", "17th c."),
    ("folk", "The Americas", "Tamborito", "Panama", "17th c."),
    ("folk", "Asia and the Pacific", "Nongak", "Korea", "Joseon"),
    ("folk", "Asia and the Pacific", "Bihu dance", "Assam, India", "ancient"),
    ("folk", "Asia and the Pacific", "Dandiya Raas", "Gujarat, India", "medieval"),
    ("folk", "Asia and the Pacific", "Singkil", "Maranao, Philippines", "pre-colonial"),
    ("social", "Ballroom and Latin", "Quickstep", "England", "1920s"),
    ("social", "Ballroom and Latin", "Viennese waltz", "Austria", "18th c."),
    ("social", "Ballroom and Latin", "Paso doble", "Spain and France", "1920s"),
    ("social", "Africa and its diaspora", "Kuduro", "Angola", "1990s"),
    ("street", "African American street forms", "Jookin", "Memphis, Tennessee", "1990s"),
    ("street", "African American street forms", "Flexing", "Brooklyn, New York", "2000s"),
    ("street", "African American street forms", "Detroit Jit", "Detroit, Michigan", "1970s"),
    ("street", "African American street forms", "Chicago Footwork", "Chicago", "1990s"),
    ("street", "Caribbean and African club", "Dembow", "Dominican Republic", "1990s"),
    ("street", "Europe, Asia and the ballroom floor", "Jumpstyle", "Belgium and the Netherlands", "1990s"),
    ("street", "Europe, Asia and the ballroom floor", "Shuffle (dance)", "Australia", "2000s"),
    ("martial-east", "Japan", "Naginatajutsu", "Japan", "medieval"),
    ("martial-east", "Japan", "Sōjutsu", "Japan", "medieval"),
    ("martial-east", "China", "Liuhebafa", "China", "10th c."),
    ("martial-east", "China", "Emeiquan", "China", "17th c."),
    ("martial-east", "China", "Piguaquan", "China", "19th c."),
    ("martial-east", "Korea", "Subak", "Korea", "ancient"),
    ("martial-south", "India", "Kuttu Varisai", "Tamil Nadu, India", "ancient"),
    ("martial-south", "India", "Musti Yuddha", "India", "ancient"),
    ("martial-south", "Southeast Asia", "Kun Khmer", "Cambodia", "ancient"),
    ("martial-south", "Southeast Asia", "Tomoi", "Malaysia", "medieval"),
    ("martial-west", "Europe", "Canne de combat", "France", "19th c."),
    ("martial-west", "Europe", "Quarterstaff", "England", "16th c."),
    ("martial-west", "Africa and the Middle East", "Lutte traditionnelle", "West Africa", "pre-colonial"),
    ("martial-west", "Africa and the Middle East", "Engolo", "Angola", "pre-colonial"),
    ("martial-west", "The Americas", "Luta livre", "Brazil", "20th c."),
    ("martial-west", "The Americas", "Jeet Kune Do", "United States", "1967"),
]


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    shelves = {}
    for entry in index["categories"]:
        doc = json.load(open(os.path.join(OUT, entry["key"] + ".json"), encoding="utf-8"))
        shelves[entry["key"]] = {
            "entry": entry, "doc": doc,
            "groups": {group["name"]: group["items"] for group in doc["groups"]},
        }

    existing = {item["u"] for state in shelves.values()
                for items in state["groups"].values() for item in items}
    titles = []
    for _key, _group, article, _culture, _era in EXTRA:
        if article not in titles:
            titles.append(article)
    fetched = bd.fetch(titles)
    for title in titles:
        if not fetched.get(title):
            print("  !", title, "not found")

    added = 0
    cultures = {item["c"] for state in shelves.values()
                for items in state["groups"].values() for item in items if item.get("c")}
    for key, group_name, article, culture, era in EXTRA:
        page = fetched.get(article)
        if not page:
            continue
        if page["u"] in existing:
            print("  =", article, "already shelved")
            continue
        existing.add(page["u"])
        state = shelves[key]
        if group_name not in state["groups"]:
            print("  ! group missing:", key, group_name)
            continue
        state["groups"][group_name].append(
            {"n": page["n"], "u": page["u"], "s": page["s"], "c": culture, "e": era})
        cultures.add(culture)
        added += 1
        print("  +", page["n"], "->", state["entry"]["title"], "/", group_name)

    total = 0
    groups_total = 0
    for key, state in shelves.items():
        doc = state["doc"]
        styles = sum(len(items) for items in state["groups"].values())
        state["entry"]["styles"] = styles
        state["entry"]["groups"] = len(doc["groups"])
        total += styles
        groups_total += len(doc["groups"])
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=0)
    index["styles"] = total
    index["groups"] = groups_total
    index["cultures"] = len(cultures)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    print("added:", added)
    print("index:", {k: index[k] for k in ("styles", "groups", "cultures")})


if __name__ == "__main__":
    sys.exit(main())
