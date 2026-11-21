#!/usr/bin/env python3
"""Write docs/rss.xml and docs/atom.xml from docs/api/index.json.

    python3 .agents/skills/blog-ops/build_rss.py           # write
    python3 .agents/skills/blog-ops/build_rss.py --check   # exit 0 if fresh, 1 if stale

The feed lists every page in docs/ (newest `published_at` first) with its meta
description as the summary; it is not full-text. Like the sitemap, it is
generated at build time — a feed reader fetches the file from the server, so it
must exist as a real file in docs/.

Standard library only.
"""

import email.utils
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from html import unescape as html_unescape
from xml.sax.saxutils import escape

ORIGIN = "https://blog.odicforcesounds.com"
DOCS = "docs"
ITEMS = 100
ATOM = "http://www.w3.org/2005/Atom"

# Never a feed entry: the front page (the channel itself) and the secret chat.
SKIP = {"index.html", "secretChat.html", "home.html", "404.html"}
# Cap on feed length, for when the catalogue grows too big; None = no cap.
ITEMS = None


def rfc822(iso):
    return email.utils.format_datetime(datetime.fromisoformat(iso))


def newest(entries):
    return sorted((a for a in entries if a.get("published_at") and a.get("path") not in SKIP),
                  key=lambda a: datetime.fromisoformat(a["published_at"]),
                  reverse=True)

def page_meta(root, name):
    """Title, description and JSON-LD dates read from the page itself."""
    path = os.path.join(root, DOCS, name)
    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        return None
    title = re.search(r"<title[^>]*>(.*?)</title>", source, re.S | re.I)
    if not title:
        return None
    desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', source, re.I)
    pub = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', source)
    mod = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})', source)
    return {
        "title": html_unescape(" ".join(title.group(1).split())),
        "description": html_unescape(desc.group(1)) if desc else "",
        "published": pub.group(1) if pub else "",
        "modified": mod.group(1) if mod else "",
    }


def first_commit_dates(root):
    """name -> ISO instant of the commit that first added the file."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "--diff-filter=A", "--format=%x00%aI", "--name-only"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}
    dates, stamp = {}, ""
    for line in out.splitlines():
        if line.startswith("\x00"):
            stamp = line[1:].strip()
        elif line.strip() and stamp:
            dates.setdefault(os.path.basename(line.strip()), stamp)
    return dates


def merge_missing(root, articles):
    """Add the pages the API does not carry: self-contained articles keep their text in HTML."""
    known = {a.get("path") for a in articles}
    folder = os.path.join(root, DOCS)
    try:
        names = sorted(n for n in os.listdir(folder) if n.endswith(".html"))
    except OSError:
        return articles
    stamps = first_commit_dates(root)
    extra = []
    for name in names:
        if name in known or name in SKIP:
            continue
        meta = page_meta(root, name)
        if not meta or not meta["description"]:
            continue
        stamp = stamps.get(name, "")
        if meta["published"]:
            published_at = meta["published"] + "T00:00:00Z"
        elif stamp:
            published_at = stamp
        else:
            try:
                published_at = date.fromtimestamp(os.path.getmtime(os.path.join(folder, name))).isoformat() + "T00:00:00Z"
            except OSError:
                continue
        if meta["modified"]:
            modified_at = meta["modified"] + "T00:00:00Z"
        else:
            modified_at = stamp or published_at
        extra.append({
            "path": name,
            "title": meta["title"],
            "description": meta["description"],
            "url": ORIGIN + "/" if name == "index.html" else "%s/%s" % (ORIGIN, name),
            "published_at": published_at,
            "modified_at": modified_at,
        })
    return articles + extra


def tail(tree, path):
    ET.indent(tree)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n")


def write_rss(path, site, items, now_iso):
    ET.register_namespace("atom", ATOM)
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = site["title"]
    ET.SubElement(channel, "link").text = ORIGIN + "/"
    ET.SubElement(channel, "description").text = site["description"]
    ET.SubElement(channel, "lastBuildDate").text = rfc822(now_iso)
    ET.SubElement(channel, "generator").text = "build_rss.py"
    ET.SubElement(channel, f"{{{ATOM}}}link",
                  {"rel": "self", "type": "application/rss+xml", "href": f"{ORIGIN}/rss.xml"})
    for a in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = a["title"]
        ET.SubElement(item, "link").text = a["url"]
        ET.SubElement(item, "guid", attrib={"isPermaLink": "true"}).text = a["url"]
        ET.SubElement(item, "description").text = a["description"]
        ET.SubElement(item, "pubDate").text = rfc822(a["published_at"])
    tail(ET.ElementTree(rss), path)


def write_atom(path, site, items, now_iso):
    ET.register_namespace("", ATOM)
    feed = ET.Element(f"{{{ATOM}}}feed")
    ET.SubElement(feed, f"{{{ATOM}}}title").text = site["title"]
    ET.SubElement(feed, f"{{{ATOM}}}subtitle").text = site["description"]
    ET.SubElement(feed, f"{{{ATOM}}}id").text = ORIGIN + "/"
    ET.SubElement(feed, f"{{{ATOM}}}updated").text = now_iso
    ET.SubElement(feed, f"{{{ATOM}}}generator").text = "build_rss.py"
    ET.SubElement(feed, f"{{{ATOM}}}link", {"href": ORIGIN + "/"})
    ET.SubElement(feed, f"{{{ATOM}}}link",
                  {"rel": "self", "type": "application/atom+xml", "href": f"{ORIGIN}/atom.xml"})
    for a in items:
        entry = ET.SubElement(feed, f"{{{ATOM}}}entry")
        ET.SubElement(entry, f"{{{ATOM}}}id").text = a["url"]
        ET.SubElement(entry, f"{{{ATOM}}}title").text = a["title"]
        ET.SubElement(entry, f"{{{ATOM}}}link",
                      {"rel": "alternate", "type": "text/html", "href": a["url"]})
        ET.SubElement(entry, f"{{{ATOM}}}published").text = a["published_at"]
        ET.SubElement(entry, f"{{{ATOM}}}updated").text = a.get("modified_at", a["published_at"])
        ET.SubElement(entry, f"{{{ATOM}}}summary", {"type": "html"}).text = escape(a["description"])
    tail(ET.ElementTree(feed), path)


def generate(root):
    with open(f"{root}/{DOCS}/api/index.json", encoding="utf-8") as fh:
        index = json.load(fh)
    site = next(a for a in index["articles"] if a["path"] == "index.html")
    items = newest(merge_missing(root, index["articles"]))
    if ITEMS is not None:
        items = items[:ITEMS]
    now_iso = max((a.get("modified_at") or a["published_at"] for a in items),
                  default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    write_rss(f"{root}/{DOCS}/rss.xml", site, items, now_iso)
    write_atom(f"{root}/{DOCS}/atom.xml", site, items, now_iso)
    return items


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    root = args[0] if args else "."
    items = generate(root)
    print(f"{DOCS}/rss.xml and {DOCS}/atom.xml written with {len(items)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
