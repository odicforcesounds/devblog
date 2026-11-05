#!/usr/bin/env python3
"""Add the traditions the religion shelves lack.

No builder writes this catalogue; the shelves are curated JSON. This pass reads
them, asks Wikipedia for the articles below, files each under its shelf and the
group whose name matches, and recomputes the counts. An article already present
is skipped, so a second run changes nothing.

    python3 .agents/skills/catalogue-data/builders/religions_extend.py
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json
import os
import sys
import time
import urllib.parse
import urllib.request

OUT = "docs/religions/data"
API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "devblog-religions/1.0 (https://blog.odicforcesounds.com; contact via site)"}

# shelf key | group keyword | article
EXTRA = [
    ("abrahamic", "Judaism", "Kabbalah"),
    ("abrahamic", "Christianity", "Eastern Orthodox Church"),
    ("abrahamic", "Christianity", "Protestantism"),
    ("abrahamic", "Christianity", "Anglicanism"),
    ("abrahamic", "Christianity", "Pentecostalism"),
    ("abrahamic", "Islam", "Sunni Islam"),
    ("abrahamic", "Islam", "Shia Islam"),
    ("abrahamic", "Islam", "Sufism"),
    ("dharmic", "Hinduism", "Vaishnavism"),
    ("dharmic", "Hinduism", "Shaivism"),
    ("dharmic", "Hinduism", "Shaktism"),
    ("dharmic", "Buddhism", "Theravada"),
    ("dharmic", "Buddhism", "Mahayana"),
    ("dharmic", "Buddhism", "Zen"),
    ("dharmic", "Buddhism", "Vajrayana"),
    ("dharmic", "Jainism", "Digambara"),
    ("dharmic", "Sikhism", "Khalsa"),
    ("east-asian", "Taoism", "Quanzhen School"),
    ("east-asian", "Shinto", "State Shinto"),
    ("east-asian", "Confucianism", "Neo-Confucianism"),
    ("esoteric", "Hermetic", "Hermeticism"),
    ("esoteric", "Theosophy", "Theosophy"),
    ("esoteric", "Anthroposophy", "Anthroposophy"),
    ("modern", "Wicca", "Wicca"),
    ("modern", "Revivals of the old gods", "Heathenry (new religious movement)"),
    ("modern", "Revivals of the old gods", "Kemetism"),
    ("modern", "Revivals of the old gods", "Rodnovery"),
    ("modern", "The new churches", "Tenrikyo"),
    ("modern", "The new churches", "Caodaism"),
    ("modern", "Scientology", "Scientology"),
    ("abrahamic", "The smaller paths", "Baháʼí Faith"),
    ("abrahamic", "The smaller paths", "Druze"),
    ("abrahamic", "The smaller paths", "Mandaeism"),
    ("esoteric", "Gnosis and magic", "Rosicrucianism"),
    ("esoteric", "Spirit and the unseen", "Spiritualism (movement)"),
    ("east-asian", "Korea", "Cheondoism"),
    ("east-asian", "Vietnam", "Cao Đài"),
    ("diaspora", "West Africa and its diaspora", "Rastafari"),
    ("africa-americas", "Africa", "Yoruba religion"),
    ("near-east", "Mithraism", "Mithraism"),
    ("greece-rome", "Orphism", "Orphism (religion)"),
    ("diaspora", "Vodou", "Haitian Vodou"),
    ("diaspora", "Ifá", "Ifá"),
    ("africa-americas", "Candomblé", "Candomblé"),
    ("before-writing", "Animism", "Animism"),
    ("before-writing", "Totemism", "Totemism"),
]


def fetch(titles):
    found = {}
    for start in range(0, len(titles), 20):
        batch = titles[start:start + 20]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "extracts|pageimages|info", "exintro": 1, "explaintext": 1,
            "exsentences": 2, "exlimit": "max", "redirects": 1,
            "piprop": "thumbnail", "pithumbsize": "250", "inprop": "url",
            "titles": "|".join(batch),
        })
        request = urllib.request.Request(API + "?" + query, headers=UA)
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        payload = data.get("query", {})
        pages = {page.get("title"): page for page in payload.get("pages", [])}
        alias = {}
        for item in payload.get("normalized", []) + payload.get("redirects", []):
            alias[item.get("from", "")] = item.get("to", "")
        for title in batch:
            key = alias.get(alias.get(title, title), title)
            page = pages.get(key) or pages.get(title)
            if not page or page.get("missing"):
                found[title] = None
                continue
            extract = " ".join((page.get("extract") or "").split())
            thumb = (page.get("thumbnail") or {}).get("source", "")
            found[title] = {
                "n": page.get("title") or title,
                "u": page.get("fullurl") or ("https://en.wikipedia.org/wiki/" +
                                             urllib.parse.quote(title.replace(" ", "_"))),
                "s": extract,
                "i": thumb.split("?")[0] if thumb else "",
            }
        time.sleep(0.3)
    return found


def main():
    index = json.load(open(os.path.join(OUT, "index.json"), encoding="utf-8"))
    shelves = {}
    for entry in index["categories"]:
        doc = json.load(open(os.path.join(OUT, entry["key"] + ".json"), encoding="utf-8"))
        shelves[entry["key"]] = {"entry": entry, "doc": doc,
                                 "groups": {group["name"]: group["items"] for group in doc["groups"]}}
    existing = {item["u"] for state in shelves.values()
                for items in state["groups"].values() for item in items}
    names = {item["n"].lower() for state in shelves.values()
             for items in state["groups"].values() for item in items}
    titles = []
    for _key, _group, article in EXTRA:
        if article not in titles:
            titles.append(article)
    fetched = fetch(titles)
    for title in titles:
        if not fetched.get(title):
            print("  !", title, "not found")

    added = 0
    for key, keyword, article in EXTRA:
        page = fetched.get(article)
        if not page:
            continue
        if page["u"] in existing or page["n"].lower() in names:
            print("  =", article, "already shelved")
            continue
        state = shelves[key]
        target = next((name for name in state["groups"] if keyword.lower() in name.lower()), None)
        if target is None:
            print("  ! no group matching", keyword, "in", key)
            continue
        existing.add(page["u"])
        names.add(page["n"].lower())
        state["groups"][target].append(page)
        added += 1
        print("  +", page["n"], "->", state["entry"]["title"], "/", target)

    total = groups_total = photos = 0
    for key, state in shelves.items():
        doc = state["doc"]
        entries = sum(len(items) for items in state["groups"].values())
        found = sum(1 for items in state["groups"].values() for item in items if item.get("i"))
        state["entry"]["entries"] = entries
        state["entry"]["groups"] = len(doc["groups"])
        state["entry"]["photos"] = found
        total += entries
        groups_total += len(doc["groups"])
        photos += found
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=0)
    index["shelves"] = len(index["categories"])
    index["groups"] = groups_total
    index["entries"] = total
    index["photos"] = photos
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    print("added:", added)
    print("index:", {k: index[k] for k in ("shelves", "groups", "entries", "photos")})


if __name__ == "__main__":
    sys.exit(main())
