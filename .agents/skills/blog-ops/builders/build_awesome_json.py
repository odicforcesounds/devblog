#!/usr/bin/env python3
"""Write the awesome catalogue as data instead of pages.

docs/awesome/data/index.json   categories -> lists -> drawer names and counts
docs/awesome/data/<slug>.json  the same categories with every tool card

Category -> awesome list -> theme drawer -> card, exactly the structure the
generated pages used, minus the HTML. docs/awesomeIndex.html fetches the index
on load and a category file when it is first opened. The shell shelf has its own
theme vocabulary and examples, so that builder is imported too.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import importlib.util
import json
import os
import sys
from urllib.parse import urlparse


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HERE = os.path.dirname(os.path.abspath(__file__))

bd = load(os.path.join(HERE, "build_deep.py"), "bd")
sd = load(os.path.join(HERE, "build_shell_deep.py"), "sd")
ma = load(os.path.join(HERE, "mkawesome.py"), "ma")

SRC = "tmp/tools.json"
OUT = "docs/awesome/data"
GROUPS = [g[0] for g in ma.GROUPS]

SHELL = {
    "key": "shell",
    "num": "01",
    "slug": "shell",
    "title": "Shell, terminal and one-liners",
    "blurb": ("The command line as a workshop: prompts, one-liners, cheat sheets and text "
              "services, filed by what each tool is for."),
}


def category_meta(key):
    if key == "shell":
        return SHELL
    meta = bd.CATS[key]
    return {"key": key, "num": meta["num"], "slug": meta["slug"],
            "title": meta["h1"], "blurb": meta["lede"]}


def build(key, data, sections, seen, dupes):
    meta = category_meta(key)
    if key == "shell":
        bucket_of = lambda list_name, tool: sd.bucket_of(list_name, tool["name"])
        example_of = lambda tool: sd.EXAMPLES.get(tool["name"].strip().lower())
        noex = sd.noex
        everything_else = "Everything else"
    else:
        compiled = bd.compile_themes(key)
        bucket_of = lambda list_name, tool: bd.bucket_of(
            compiled, (tool["name"] + " " + tool["desc"]).strip())
        example_of = lambda tool: bd.EXAMPLES.get(tool["name"].strip().lower())
        noex = bd.noex
        everything_else = bd.EVERYTHING_ELSE

    # Lists come from the index catalogue, so a list whose README yielded no
    # linkable entry is still here with its link and its one-line description.
    by_url = {lst["url"].rstrip("/"): lst for lst in (data.get(key) or [])}
    entries = sorted(((u, n, en) for u, n, g, en, _pt in ma.E if g == key),
                     key=lambda r: r[1].lower())
    if not entries:
        return None, None

    # A list heading is itself a link to that list, so a tool that points at any
    # list in this category would print the same href a second time.
    # Seen and dupes are shared across categories: the page draws each href
    # exactly once, so a tool in two shelves keeps the first card and notes the
    # other list. seen starts seeded with every list url, because a list heading
    # is a link to that list and a card pointing there would repeat it.
    order, counts = [], {}
    for url, name, _desc in entries:
        src = by_url.get(url)
        counts[name] = 0
        if not src:
            continue
        kept = []
        for tool in src["tools"]:
            if bd.junk(tool):
                continue
            u = tool["url"].rstrip("/")
            if u in seen:
                dupes.setdefault(u, []).append(name)
                continue
            seen.add(u)
            kept.append(tool)
            order.append((name, tool))
        src["tools"] = kept

    buckets = {name: {} for _u, name, _d in entries}
    counters = {name: 0 for name in counts}
    for list_name, tool in order:
        counters[list_name] += 1
        title = bucket_of(list_name, tool)
        url = tool["url"].rstrip("/")
        example = example_of(tool)
        card = {"n": tool["name"].strip(), "i": counters[list_name], "u": tool["url"],
                "h": urlparse(tool["url"]).netloc.replace("www.", "")}
        if tool["desc"]:
            card["d"] = tool["desc"].strip()
        if example:
            card["x"] = example
        else:
            card["y"] = noex(tool["url"])
        if url in dupes:
            card["a"] = sorted(set(dupes[url]))
        buckets[list_name].setdefault(title, []).append(card)

    lists_full, lists_nav, total = [], [], 0
    for url, name, desc in entries:
        group = buckets[name]
        keys = sorted(group, key=lambda k: (k == everything_else, -len(group[k])))
        drawers = [{"t": k, "c": group[k]} for k in keys]
        count = sum(len(d["c"]) for d in drawers)
        total += count
        src = by_url.get(url)
        repo = src["repo"] if src else url.replace("https://github.com/", "")
        entry = {"n": name, "r": repo, "u": url, "w": desc, "c": count}
        sec = sections.get(repo) or {}
        if sec.get("sections"):
            entry["toc"] = {"n": len(sec["sections"]), "e": sec.get("entries", 0),
                            "names": sec["sections"]}
        lists_nav.append(dict(entry, d=[{"t": d["t"], "c": len(d["c"])} for d in drawers]))
        lists_full.append(dict(entry, d=drawers))

    full = {"key": key, "num": meta["num"], "title": meta["title"],
            "lists": lists_full, "tools": total}
    nav = {"key": key, "num": meta["num"], "slug": meta["slug"], "title": meta["title"],
           "blurb": meta["blurb"], "lists": lists_nav, "tools": total,
           "drawers": sum(len(x["d"]) for x in lists_nav)}
    return nav, full


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    try:
        sections = json.load(open("tmp/sections.json", encoding="utf-8"))
    except (OSError, ValueError):
        sections = {}

    os.makedirs(OUT, exist_ok=True)
    index = {"categories": [], "lists": 0, "tools": 0, "drawers": 0}
    seen = {u.rstrip("/") for u, _n, _g, _d, _p in ma.E}
    dupes = {}
    for key in GROUPS:
        nav, full = build(key, data, sections, seen, dupes)
        if nav is None:
            continue
        path = os.path.join(OUT, "%s.json" % nav["slug"])
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(full, fh, ensure_ascii=False, separators=(",", ":"))
        index["categories"].append(nav)
        index["lists"] += len(nav["lists"])
        index["tools"] += nav["tools"]
        index["drawers"] += nav["drawers"]
        print("%-28s %2d lists %6d tools %5d drawers %7.1f KB"
              % (path, len(nav["lists"]), nav["tools"], nav["drawers"],
                 os.path.getsize(path) / 1024))

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, separators=(",", ":"))
    print("index: %d categories, %d lists, %d tools, %.1f KB"
          % (len(index["categories"]), index["lists"], index["tools"],
             os.path.getsize(os.path.join(OUT, "index.json")) / 1024))


if __name__ == "__main__":
    main()
