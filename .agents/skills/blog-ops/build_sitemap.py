#!/usr/bin/env python3
"""Write docs/sitemap.xml and docs/robots.txt from the pages that exist.

    python3 .agents/skills/blog-ops/build_sitemap.py           # write
    python3 .agents/skills/blog-ops/build_sitemap.py --check    # diff only, no write

Every root docs/*.html becomes one URL; `index.html` is published as the site root.
`lastmod` is the date of the last commit that touched the file, falling back to its
mtime for pages that were never committed. Run this after adding or renaming a page,
before build_api.py.

Standard library only.
"""

import os
import subprocess
import sys
from xml.sax.saxutils import escape

ORIGIN = "https://blog.odicforcesounds.com"
DOCS = "docs"

ROBOTS = """User-agent: *
Allow: /

# Archived snapshots of third-party pages: kept for readers, not for indexing.
Disallow: /archive/
Disallow: /obsdRouter/

# JSON behind the on-page search. It is a data source, not a page.
Disallow: /api/

Sitemap: %s/sitemap.xml
""" % ORIGIN


def lastmod(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", path],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        out = ""
    if out:
        return out.splitlines()[0]
    import datetime
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def build():
    names = sorted(n for n in os.listdir(DOCS) if n.endswith(".html"))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name in names:
        path = os.path.join(DOCS, name)
        loc = ORIGIN + "/" if name == "index.html" else "%s/%s" % (ORIGIN, name)
        when = lastmod(path)
        lines.append("  <url>")
        lines.append("    <loc>%s</loc>" % escape(loc))
        if when:
            lines.append("    <lastmod>%s</lastmod>" % when)
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n", len(names)


def current(name):
    path = os.path.join(DOCS, name)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main(argv):
    check_only = "--check" in argv
    if not os.path.isdir(DOCS):
        print("run this from the repository root (no %s/ here)" % DOCS)
        return 2

    sitemap, count = build()
    changed = []

    for name, text in (("sitemap.xml", sitemap), ("robots.txt", ROBOTS)):
        if current(name) == text:
            print("%s: unchanged" % name)
            continue
        changed.append(name)
        if check_only:
            old_lines = set(current(name).splitlines())
            new_lines = set(text.splitlines())
            added = [l.strip() for l in new_lines - old_lines if l.strip()][:4]
            removed = [l.strip() for l in old_lines - new_lines if l.strip()][:4]
            print("%s: would change (%d lines added, %d removed)"
                  % (name, len(new_lines - old_lines), len(old_lines - new_lines)))
            for line in added:
                print("  + %s" % line)
            for line in removed:
                print("  - %s" % line)
        else:
            with open(os.path.join(DOCS, name), "w", encoding="utf-8") as fh:
                fh.write(text)
            print("%s: written" % name)

    print("pages: %d" % count)
    if check_only:
        return 1 if changed else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
