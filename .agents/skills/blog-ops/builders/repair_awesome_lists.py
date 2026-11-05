#!/usr/bin/env python3
"""Repair an awesome shelf whose lists came out empty.

extract_tools.py only reads `- [name](url)` bullets, so a README that puts its
entries in Markdown tables (awesome-api-security does) yields no tools and the
list ships with a table of contents and nothing under it. This script refetches
the README of every empty list in one shelf, reads bullets and tables, files the
entries by the heading they sit under, and patches that shelf and its manifest.

    python3 .agents/skills/blog-ops/builders/build_awesome_json.py --help   # not this
    python3 .agents/skills/blog-ops/builders/repair_awesome_lists.py security-privacy-and-forensics

The shelf is docs/awesome/data/<slug>.json; the manifest is next to it.
"""

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

DATA = "docs/awesome/data"
UA = {"User-Agent": "MonkeyBlogAwesomeRepair/1.0 (https://blog.odicforcesounds.com)"}
SKIP_HEADING = re.compile(
    r"^(about|contribut|licen[cs]e|table of contents|contents|credits?|changelog|"
    r"footnotes?|see also|acknowledg|disclaimer|star history|backers?|sponsors?)\b", re.I)
BAD_URL = re.compile(r"shields\.io|badge|travis-ci|circleci|codecov|awesome\.re|"
                     r"opencollective|patreon|paypal|img\.shields", re.I)
BAD_NAME = {
    "awesome", "back to top", "top", "↑", "contents", "index", "here", "documentation",
    "docs", "discord", "github", "paper", "website", "blog", "twitter", "telegram",
    "slack", "matrix", "contributing", "license", "licence", "changelog", "releases",
    "sponsor", "donate", "issues", "discussions", "stars", "chat", "community", "npm",
    "pypi", "crates.io", "docker hub", "youtube", "reddit", "mastodon", "forum",
    "roadmap", "wiki", "readme", "homepage", "demo", "download",
}

BULLET = re.compile(r"^\s*[-*+]\s+\[([^\]]+)\]\((https?://[^)\s]+)\)(.*)$")
ORDERED = re.compile(r"^\s*\d+[.)]\s+\[([^\]]+)\]\((https?://[^)\s]+)\)(.*)$")
NAKED = re.compile(r"^\s*[-*+]\s+(https?://[^\s)]+)\s*(.*)$")
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
README_NAMES = ("README.md", "readme.md", "Readme.md", "README.markdown")
HEADING = re.compile(r"^(#{2,4})\s+(.*?)\s*#*$")


def clean(text):
    text = html.unescape(text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r":[a-z0-9_+-]{2,}:", "", text, flags=re.I)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2192\u2190\u203a\u00bb]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch(repo):
    for branch in ("main", "master"):
        for name in README_NAMES:
            url = "https://raw.githubusercontent.com/%s/%s/%s" % (repo, branch, name)
            try:
                request = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(request, timeout=30) as response:
                    return response.read().decode("utf-8", "replace")
            except urllib.error.HTTPError:
                continue
            except urllib.error.URLError:
                continue
    return ""


def name_from_url(url):
    path = urllib.parse.urlsplit(url).path.rstrip("/")
    tail = path.rsplit("/", 1)[-1] if path else ""
    tail = re.sub(r"\.git$", "", tail)
    return clean(tail.replace("-", " ").replace("_", " ")).title()


def entries(text):
    """Drawers by heading; each entry is a bullet or a table row with a link."""
    drawers = []
    current = ("Everything else", [])
    seen = set()

    def add(name, url, desc):
        name = clean(name)
        url = url.rstrip("/")
        if not name or len(name) > 90 or name.lower() in BAD_NAME:
            return
        if BAD_URL.search(url) or url in seen:
            return
        if any(url == item["u"].rstrip("/") for item in current[1]):
            return
        seen.add(url)
        desc = clean(desc).strip(" -–—:|·")
        if len(desc) > 180:
            desc = desc[:177].rstrip() + "…"
        current[1].append({"n": name, "u": url, "d": desc})

    for line in text.splitlines():
        heading = HEADING.match(line)
        if heading:
            linked = LINK.search(heading.group(2))
            if linked and len(heading.group(1)) >= 3:
                name = re.sub(r"[\u2192\u2190\u203a\u00bb\u2022\s]+", " ",
                              clean(heading.group(2))).strip(" -–—:|·")
                add(name, linked.group(2), "")
                continue
            title = clean(heading.group(2))
            if current[1]:
                drawers.append(current)
            current = (title if title and not SKIP_HEADING.match(title) else "Everything else", [])
            continue

        if "~~" in line and line.find("~~") < line.find("["):
            continue

        bullet = BULLET.match(line) or ORDERED.match(line)
        if bullet:
            add(bullet.group(1), bullet.group(2), bullet.group(3))
            continue

        naked = NAKED.match(line)
        if naked:
            add(name_from_url(naked.group(1)), naked.group(1), naked.group(2))
            continue

        if "|" in line and not line.lstrip().startswith("#"):
            row = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if any(re.fullmatch(r"[-: ]+", cell) for cell in row if cell):
                continue
            link = None
            for cell in row:
                found = LINK.search(cell)
                if found:
                    link = found
                    break
            if not link:
                continue
            name = clean(row[0]) if row else clean(link.group(1))
            if not name:
                name = clean(link.group(1))
            desc = row[-1] if len(row) > 1 else ""
            add(name, link.group(2), desc)

    if current[1]:
        drawers.append(current)

    return [{"t": title, "c": cards} for title, cards in drawers if cards]


def main(argv):
    slug = argv[1] if len(argv) > 1 else "security-privacy-and-forensics"
    shelf_path = os.path.join(DATA, slug + ".json")
    index_path = os.path.join(DATA, "index.json")
    shelf = json.load(open(shelf_path, encoding="utf-8"))
    index = json.load(open(index_path, encoding="utf-8"))
    before_tools = shelf.get("tools", 0)
    before_drawers = sum(len(lst.get("d", [])) for lst in shelf["lists"])

    entries_in_shelf = {item["u"].rstrip("/") for lst in shelf["lists"]
                        for drawer in lst.get("d", []) for item in drawer.get("c", [])}

    empty = [lst for lst in shelf["lists"] if not lst.get("d")]
    print("empty lists in %s: %d" % (slug, len(empty)))

    filled = 0
    for lst in empty:
        repo = lst.get("r") or ""
        text = fetch(repo) if repo else ""
        if not text:
            print("  ! %-32s README not reachable" % lst["n"][:32])
            continue
        drawers = []
        number = 0
        for drawer in entries(text):
            cards = []
            for entry in drawer["c"]:
                if entry["u"].rstrip("/") in entries_in_shelf:
                    continue
                entries_in_shelf.add(entry["u"].rstrip("/"))
                number += 1
                card = {"n": entry["n"], "i": number, "u": entry["u"],
                        "h": re.sub(r"^www\.", "", urllib.parse.urlsplit(entry["u"]).netloc)}
                if entry["d"]:
                    card["d"] = entry["d"]
                else:
                    card["y"] = "The list gives no description — the link is the description."
                cards.append(card)
            if cards:
                drawers.append({"t": drawer["t"], "c": cards})

        if not drawers:
            print("  ! %-32s README has no readable entries" % lst["n"][:32])
            continue

        total = sum(len(d["c"]) for d in drawers)
        lst["d"] = drawers
        lst["c"] = total
        if "toc" in lst:
            lst["toc"]["e"] = total
        filled += 1
        print("  + %-32s %3d tools in %d drawers" % (lst["n"][:32], total, len(drawers)))

    shelf["tools"] = sum(lst.get("c", 0) for lst in shelf["lists"])

    added_tools = shelf["tools"] - before_tools
    added_drawers = sum(len(lst.get("d", [])) for lst in shelf["lists"]) - before_drawers
    category = next((c for c in index["categories"] if c.get("slug") == slug), None)
    if category:
        category["tools"] = category.get("tools", 0) + added_tools
    index["tools"] = index.get("tools", 0) + added_tools
    index["drawers"] = index.get("drawers", 0) + added_drawers

    with open(shelf_path, "w", encoding="utf-8") as handle:
        json.dump(shelf, handle, ensure_ascii=False, separators=(",", ":"))
    with open(index_path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, separators=(",", ":"))

    print("filled %d lists | shelf tools %d | manifest tools %d"
          % (filled, shelf["tools"], index["tools"]))
    return 0 if filled else 1


if __name__ == "__main__":
    import urllib.parse
    sys.exit(main(sys.argv))
