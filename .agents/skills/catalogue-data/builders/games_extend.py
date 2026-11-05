#!/usr/bin/env python3
"""Add the games the shelves lack.

No builder writes this catalogue; the shelves are curated JSON. This pass reads
them, asks Wikipedia for the articles below, files each under its shelf and the
group whose name matches, with the year, origin, licence and age this catalogue
curates, and recomputes the counts. A game already present is skipped.

    python3 .agents/skills/catalogue-data/builders/games_extend.py
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

OUT = "docs/games/data"
API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "devblog-games/1.0 (https://blog.odicforcesounds.com; contact via site)"}

# shelf key | group keyword | article | year | origin | licence | age
EXTRA = [
    ("arcade", "first screens", "Pong", "1972", "United States", "commercial", "family"),
    ("arcade", "coin-op", "Space Invaders", "1978", "Japan", "commercial", "family"),
    ("arcade", "coin-op", "Pac-Man", "1980", "Japan", "commercial", "family"),
    ("arcade", "coin-op", "Asteroids (video game)", "1979", "United States", "commercial", "family"),
    ("computer", "console", "Super Mario Bros.", "1985", "Japan", "commercial", "family"),
    ("computer", "console", "The Legend of Zelda", "1986", "Japan", "commercial", "family"),
    ("computer", "computer", "Tetris", "1984", "Soviet Union", "commercial", "family"),
    ("computer", "computer", "Doom (1993 video game)", "1993", "United States", "commercial", "teen"),
    ("computer", "computer", "Minecraft", "2011", "Sweden", "commercial", "family"),
    ("online", "networked", "World of Warcraft", "2004", "United States", "commercial", "teen"),
    ("online", "networked", "League of Legends", "2009", "United States", "commercial", "teen"),
    ("online", "networked", "Fortnite", "2017", "United States", "commercial", "teen"),
    ("online", "networked", "Roblox", "2006", "United States", "commercial", "family"),
    ("open", "Roguelikes", "NetHack", "1987", "United States", "free", "family"),
    ("open", "Roguelikes", "Dwarf Fortress", "2006", "United States", "free", "teen"),
    ("open", "Sandbox", "0 A.D. (video game)", "2001", "International", "free", "family"),
    ("party", "party", "Charades", "19th c.", "France", "public-domain", "family"),
    ("party", "party", "Pictionary", "1985", "United States", "commercial", "family"),
    ("party", "party", "Twister (game)", "1966", "United States", "commercial", "family"),
    ("board", "board", "Go (game)", "ancient", "China", "public-domain", "family"),
    ("board", "board", "Backgammon", "ancient", "Mesopotamia", "public-domain", "family"),
    ("board", "board", "Scrabble", "1938", "United States", "commercial", "family"),
    ("board", "board", "Monopoly (game)", "1935", "United States", "commercial", "family"),
    ("cards", "cards", "Poker", "19th c.", "United States", "public-domain", "adult"),
    ("cards", "cards", "Blackjack", "18th c.", "France", "public-domain", "adult"),
    ("cards", "cards", "Contract bridge", "1925", "United States", "public-domain", "family"),
    ("dice", "dice", "Yahtzee", "1956", "United States", "commercial", "family"),
    ("dice", "dice", "Dungeons & Dragons", "1974", "United States", "commercial", "teen"),
    ("dice", "dice", "Mahjong", "19th c.", "China", "public-domain", "family"),
    ("modern", "Eurogames", "Catan", "1995", "Germany", "commercial", "family"),
    ("modern", "Eurogames", "Ticket to Ride", "2004", "United States", "commercial", "family"),
    ("modern", "Eurogames", "Carcassonne (board game)", "2000", "Germany", "commercial", "family"),
    ("tabletop", "worlds", "Warhammer 40,000", "1987", "United Kingdom", "commercial", "teen"),
    ("tabletop", "worlds", "Magic: The Gathering", "1993", "United States", "commercial", "teen"),
    ("collect", "cards", "Pokémon Trading Card Game", "1996", "Japan", "commercial", "family"),
    ("collect", "cards", "Yu-Gi-Oh! Trading Card Game", "1999", "Japan", "commercial", "family"),
    ("children", "playground", "Hide-and-seek", "traditional", "worldwide", "public-domain", "family"),
    ("children", "playground", "Tag (game)", "traditional", "worldwide", "public-domain", "family"),
    ("children", "playground", "Hopscotch", "traditional", "worldwide", "public-domain", "family"),
    ("puzzles", "puzzles", "Sudoku", "1979", "Japan", "public-domain", "family"),
    ("puzzles", "puzzles", "Crossword", "1913", "United States", "public-domain", "family"),
    ("puzzles", "puzzles", "Rubik's Cube", "1974", "Hungary", "commercial", "family"),
]


def fetch(titles):
    found = {}
    for start in range(0, len(titles), 20):
        batch = titles[start:start + 20]
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "extracts|pageimages|info", "exintro": 1, "explaintext": 1,
            "exsentences": 1, "exlimit": "max", "redirects": 1,
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
            first = extract.split(". ")[0]
            if len(first) > 180:
                first = first[:177].rstrip() + "…"
            elif first and not first.endswith("."):
                first += "."
            thumb = (page.get("thumbnail") or {}).get("source", "")
            found[title] = {
                "n": page.get("title") or title,
                "u": page.get("fullurl") or ("https://en.wikipedia.org/wiki/" +
                                             urllib.parse.quote(title.replace(" ", "_"))),
                "d": first,
                "img": thumb.split("?")[0] if thumb else "",
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
    for _key, _group, article, _y, _o, _l, _a in EXTRA:
        if article not in titles:
            titles.append(article)
    fetched = fetch(titles)
    for title in titles:
        if not fetched.get(title):
            print("  !", title, "not found")

    added = 0
    for key, keyword, article, year, origin, licence, age in EXTRA:
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
        state["groups"][target].append({
            "n": page["n"], "o": origin, "d": page["d"], "t": key,
            "lic": licence, "age": age, "u": page["u"], "y": year, "img": page["img"],
        })
        added += 1
        print("  +", page["n"], "->", state["entry"]["title"], "/", target)

    total = 0
    for key, state in shelves.items():
        doc = state["doc"]
        seen = set()
        for group in doc["groups"]:
            kept = []
            for item in state["groups"][group["name"]]:
                folded = item["n"].lower()
                if folded in seen:
                    continue
                seen.add(folded)
                kept.append(item)
            state["groups"][group["name"]] = kept
            group["items"] = kept
        games = sum(len(items) for items in state["groups"].values())
        state["entry"]["games"] = games
        state["entry"]["groups"] = len(doc["groups"])
        total += games
        with open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=0)
    index["games"] = total
    index["shelves"] = len(index["categories"])
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    print("added:", added)
    print("index:", {"games": index["games"], "shelves": index["shelves"]})


if __name__ == "__main__":
    sys.exit(main())
