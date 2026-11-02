#!/usr/bin/env python3
"""Measure what a reader actually downloads, and fail when it is too much.

A page's weight is the HTML plus every local file it names — sheets, scripts, images —
plus every JSON it fetches at open time. That closure is what the browser pays for the
first visit; the repository size on disk is a different and less interesting number.

Budgets are per page class, because a catalogue that draws 3,800 tools legitimately costs
more than an article:

    article     512 KB html, 1.5 MB closure
    catalogue   1.5 MB html, 4 MB closure
    archive     4 MB html, 8 MB closure   (docs/archive/**, docs/obsdRouter/**)

    python3 .agents/skills/page-weight/check_weight.py
    python3 .agents/skills/page-weight/check_weight.py --top 25
    python3 .agents/skills/page-weight/check_weight.py --json

Read-only: it writes nothing and fixes nothing. Exit code 0 when no page is over budget,
1 when one is. A single asset over 2 MB is a failure on its own, whichever page uses it.
"""

import argparse
import glob
import json
import os
import re
import sys

DOCS = "docs"
KB = 1024
LINK_TAG = re.compile(r'<link\b[^>]*>', re.I)
SCRIPT_TAG = re.compile(r'<script\b[^>]*>', re.I)
MEDIA_TAG = re.compile(r'<(?:img|source|video|audio)\b[^>]*>', re.I)
SRCSET = re.compile(r'srcset\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', re.I)
FETCH = re.compile(r'''fetch\(\s*['"]([^'"]+\.json)['"]''', re.I)
LOCAL_JSON = re.compile(r'''['"]([A-Za-z0-9_./-]+\.json)['"]''')
CATALOGUE = re.compile(r'(Index\.html|_story\.html)$', re.I)
ARCHIVE_PREFIX = ("archive/", "obsdRouter/")

BUDGET = {
    "article":   {"html": 512 * KB,  "closure": 1536 * KB},
    "catalogue": {"html": 1536 * KB, "closure": 4096 * KB},
    "archive":   {"html": 4096 * KB, "closure": 8192 * KB},
}
ASSET_FAIL = 2 * 1024 * KB


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def page_class(name):
    if name.startswith(ARCHIVE_PREFIX):
        return "archive"
    if CATALOGUE.search(name) or "Index" in name:
        return "catalogue"
    return "article"


def resolve(page, ref):
    ref = ref.strip()
    if not ref or ref.startswith(("#", "data:", "mailto:", "javascript:")):
        return None
    if ref.startswith("//") or re.match(r'^[a-z][a-z0-9+.-]*:', ref, re.I):
        return None
    ref = ref.split("?")[0].split("#")[0]
    if not ref:
        return None
    base = os.path.dirname(os.path.join(DOCS, page))
    path = os.path.normpath(os.path.join(DOCS, ref.lstrip("/")) if ref.startswith("/")
                            else os.path.join(base, ref))
    return path if os.path.exists(path) else None


def attributes(text):
    return {k.lower(): v for k, v in re.findall(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', text)}


def assets_of(page):
    """What the page makes the browser fetch: sheets, scripts, media, fetched JSON.

    An `<a href>` is a destination, not weight — following it would count the whole site
    from the front page, which is why the earlier version reported 35 MB pages.
    """
    source = read(os.path.join(DOCS, page))
    found = set()
    for tag in LINK_TAG.findall(source):
        attrs = attributes(tag)
        if "stylesheet" in attrs.get("rel", "").lower() and attrs.get("href"):
            path = resolve(page, attrs["href"])
            if path:
                found.add(path)
    for tag in SCRIPT_TAG.findall(source):
        attrs = attributes(tag)
        if attrs.get("src"):
            path = resolve(page, attrs["src"])
            if path:
                found.add(path)
    for tag in MEDIA_TAG.findall(source):
        attrs = attributes(tag)
        for key in ("src", "poster"):
            if attrs.get(key):
                path = resolve(page, attrs[key])
                if path:
                    found.add(path)
    for match in SRCSET.finditer(source):
        value = match.group(1) if match.group(1) is not None else match.group(2)
        for candidate in value.split(","):
            path = resolve(page, candidate.strip().split(" ")[0])
            if path:
                found.add(path)
    for match in FETCH.finditer(source):
        path = resolve(page, match.group(1))
        if path:
            found.add(path)
    for match in LOCAL_JSON.finditer(source):
        path = resolve(page, match.group(1))
        if path and path not in found and path.endswith(".json"):
            found.add(path)
    found.discard(os.path.join(DOCS, page))
    return found


def human(bytes_):
    if bytes_ >= 1024 * KB:
        return "%.1f MB" % (bytes_ / float(1024 * KB))
    return "%.0f KB" % (bytes_ / float(KB))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure page weight against a budget.")
    parser.add_argument("--top", type=int, default=12, help="how many heaviest pages to list")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "*.html")))
    for sub in ARCHIVE_PREFIX:
        pages += sorted("%s%s" % (sub, os.path.basename(p))
                        for p in glob.glob(os.path.join(DOCS, sub, "*.html")))
    if not pages:
        print("no pages found", file=sys.stderr)
        return 1

    rows, failures, warnings, asset_users = [], [], [], {}
    total_site = 0
    for page in pages:
        cls = page_class(page)
        html_bytes = size(os.path.join(DOCS, page))
        closure = set()
        for path in assets_of(page):
            closure.add(path)
            asset_users.setdefault(path, []).append(page)
        assets_bytes = sum(size(p) for p in closure)
        total = html_bytes + assets_bytes
        total_site += html_bytes
        budget = BUDGET[cls]
        over = []
        if html_bytes > budget["html"]:
            failures.append((page, "html %s over the %s budget" % (human(html_bytes), human(budget["html"]))))
            over.append("html")
        elif html_bytes > budget["html"] * 0.6:
            warnings.append((page, "html %s — %d%% of the %s budget" % (human(html_bytes), 100 * html_bytes // budget["html"], cls)))
        if total > budget["closure"]:
            failures.append((page, "closure %s over the %s budget" % (human(total), human(budget["closure"]))))
        elif total > budget["closure"] * 0.6:
            warnings.append((page, "closure %s — %d%% of the %s budget" % (human(total), 100 * total // budget["closure"], cls)))
        rows.append((total, page, cls, html_bytes, assets_bytes, len(closure)))

    for path, users in asset_users.items():
        if size(path) > ASSET_FAIL:
            failures.append((path, "%s, used by %d page(s)" % (human(size(path)), len(users))))
    for path in glob.glob(os.path.join(DOCS, "**", "*.pdf"), recursive=True):
        if size(path) > ASSET_FAIL:
            failures.append((path, "%s — a PDF with no chunking" % human(size(path))))

    rows.sort(reverse=True)
    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "site_html": total_site,
            "heaviest": [{"page": p, "class": c, "html": h, "assets": a, "files": n, "total": t}
                         for t, p, c, h, a, n in rows[:args.top]],
            "failures": [{"what": w, "why": t} for w, t in failures],
            "warnings": [{"what": w, "why": t} for w, t in warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    print("pages %d | html %s | budgets article %s / catalogue %s / archive %s"
          % (len(pages), human(total_site), human(BUDGET["article"]["closure"]),
             human(BUDGET["catalogue"]["closure"]), human(BUDGET["archive"]["closure"])))
    print("heaviest pages:")
    for total, page, cls, html_bytes, assets_bytes, count in rows[:args.top]:
        print("  %-40s %-9s %8s = %7s html + %8s in %d file(s)"
              % (page, cls, human(total), human(html_bytes), human(assets_bytes), count))
    if failures:
        print("failures %d" % len(failures))
        for what, why in failures[:20]:
            print("  %s — %s" % (what, why))
        if len(failures) > 20:
            print("  … and %d more" % (len(failures) - 20))
    if warnings:
        print("warnings %d" % len(warnings))
        for what, why in warnings[:8]:
            print("  %s — %s" % (what, why))
        if len(warnings) > 8:
            print("  … and %d more" % (len(warnings) - 8))
    if not failures and not warnings:
        print("nothing to fix")
    elif not failures:
        print("no failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
