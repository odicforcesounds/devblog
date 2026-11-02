#!/usr/bin/env python3
"""Report pages where the living card repeats a link the page already carries."""

import glob
import re
import sys

PANEL = re.compile(r'<aside class="living-panel".*?</aside>', re.S)


def main():
    pages = sorted(glob.glob("docs/*.html"))
    offenders = []
    for path in pages:
        source = open(path, encoding="utf-8", errors="replace").read()
        match = PANEL.search(source)
        if not match:
            continue
        panel = match.group(0)
        rest = source[:match.start()] + source[match.end():]
        rest_links = set(re.findall(r'href="([^"]+)"', rest))
        for href in re.findall(r'href="([^"]+)"', panel):
            if href in rest_links:
                offenders.append((path, href))
    print("pages checked: %d | repeated panel links: %d" % (len(pages), len(offenders)))
    for path, href in offenders:
        print("  %-40s %s" % (path, href))
    return 1 if offenders else 0


if __name__ == "__main__":
    sys.exit(main())
