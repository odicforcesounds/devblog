#!/usr/bin/env python3
"""Update docs/sitemap.xml and docs/robots.txt from the pages that exist.

The sitemap is edited in place and only ever gains entries: the block for a page that is
missing is inserted where alphabetical order puts it, and every existing `<url>` block is
left byte for byte — no lastmod is rewritten, no entry is dropped. The file is generated
from scratch only when it does not exist yet.

    python3 .agents/skills/blog-ops/build_sitemap.py           # write
    python3 .agents/skills/blog-ops/build_sitemap.py --check    # diff only, no write

Every root docs/*.html becomes one URL; `index.html` is published as the site root.
`lastmod` is the date of the last commit that touched the file, falling back to its
mtime for pages that were never committed. Run this after adding or renaming a page,
before `.agents/skills/blog-ops/build_api.py`.

Standard library only.
"""

import os
import re
import subprocess
import sys
from xml.sax.saxutils import escape

ORIGIN = "https://blog.odicforcesounds.com"
DOCS = "docs"

# Served by the host for missing paths; it must never appear in a sitemap.
SKIP = {"404.html", "home.html"}  # error page and the redirect stub

ROBOTS = """# Policy: the archive is open to search engines, link previews and archives.
# Two directories are kept out of the index, and the API JSON is a data source.

# Every crawler not named below follows this group.
User-agent: *
Allow: /
Disallow: /archive/
Disallow: /obsdRouter/
Disallow: /api/

# Search engines. Same rules as above, repeated so that a crawler left out of this
# list is an omission somebody can see, not an ambiguity.
User-agent: Googlebot
User-agent: Googlebot-Image
User-agent: Googlebot-News
User-agent: Google-InspectionTool
User-agent: Bingbot
User-agent: BingPreview
User-agent: DuckDuckBot
User-agent: Applebot
User-agent: Baiduspider
User-agent: YandexBot
User-agent: SeznamBot
User-agent: Yeti
User-agent: Sogou web spider
User-agent: PetalBot
User-agent: Slurp
User-agent: MojeekBot
User-agent: Coccocbot
Allow: /
Disallow: /archive/
Disallow: /obsdRouter/
Disallow: /api/

# Link previews and archives: these read a page to build a card or a snapshot, never
# to rank it. Allowed so shared links render, keeping the same two exclusions.
User-agent: facebookexternalhit
User-agent: Twitterbot
User-agent: LinkedInBot
User-agent: Slackbot
User-agent: TelegramBot
User-agent: WhatsApp
User-agent: Discordbot
User-agent: ia_archiver
User-agent: archive.org_bot
User-agent: CCBot
User-agent: W3C_Validator
Allow: /
Disallow: /archive/
Disallow: /obsdRouter/
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
    if not os.path.exists(path):
        return ""
    import datetime
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def page_names():
    # The root first, then alphabetical: the landing page is the entry point.
    return sorted((n for n in os.listdir(DOCS) if n.endswith(".html") and n not in SKIP),
                  key=lambda n: (n != "index.html", n))


def loc_for(name):
    return ORIGIN + "/" if name == "index.html" else "%s/%s" % (ORIGIN, name)


def entries():
    return [(loc_for(n), lastmod(os.path.join(DOCS, n))) for n in page_names()]


def block(loc, when):
    lines = ["  <url>", "    <loc>%s</loc>" % escape(loc)]
    if when:
        lines.append("    <lastmod>%s</lastmod>" % when)
    lines.append("  </url>")
    return "\n".join(lines) + "\n"


def build():
    data = entries()
    head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    return head + "".join(block(loc, when) for loc, when in data) + "</urlset>\n", len(data)


BLOCK = re.compile(r'  <url>\n    <loc>([^<]*)</loc>\n(?:    <lastmod>([^<]*)</lastmod>\n)?  </url>\n')


def update(existing, names):
    """Insert the `<url>` blocks for pages the sitemap is missing; touch nothing else."""
    found = [(m.start(), m.end(), m.group(1)) for m in BLOCK.finditer(existing)]
    if not found:
        return None

    order = {loc_for(n): index for index, n in enumerate(names)}
    present = {loc for _, _, loc in found}
    pending = [n for n in names if loc_for(n) not in present]
    if not pending:
        return existing

    last = len(names)
    chunks = []
    for start, end, loc in found:
        while pending and order[loc_for(pending[0])] < order.get(loc, last):
            name = pending.pop(0)
            chunks.append(block(loc_for(name), lastmod(os.path.join(DOCS, name))))
        chunks.append(existing[start:end])
    for name in pending:
        chunks.append(block(loc_for(name), lastmod(os.path.join(DOCS, name))))

    return existing[:found[0][0]] + "".join(chunks) + existing[found[-1][1]:]


def current(name):
    path = os.path.join(DOCS, name)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main(argv):
    check_only = "--check" in argv
    robots_only = "--robots" in argv          # rewrite robots.txt, leave the sitemap alone
    if not os.path.isdir(DOCS):
        print("run this from the repository root (no %s/ here)" % DOCS)
        return 2

    if robots_only:
        sitemap, count = None, 0
        targets = (("robots.txt", ROBOTS),)
    else:
        names = page_names()
        existing = current("sitemap.xml")
        sitemap = update(existing, names) if existing.strip() else None
        if sitemap is None:
            sitemap, count = build()
        else:
            count = len(names)
        targets = (("sitemap.xml", sitemap), ("robots.txt", ROBOTS))
    changed = []

    for name, text in targets:
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

    if not robots_only:
        print("pages: %d" % count)
    if check_only:
        return 1 if changed else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
