#!/usr/bin/env python3
"""Audit what a search engine sees, and nothing else.

`check_site.py` proves the head contract. This proves the *indexation* story around it:
a title that fits in a result, a canonical that names its own file, pages that agree
about being indexed, a sitemap and a robots.txt that describe the same site, dates a
crawler can trust, and pages a crawler can reach from the front page.

Read-only: it never writes a page, a sitemap or a JSON file, and it fixes nothing. Each
finding is a line with the page and what is wrong, so the fix is a decision, not a
default.

    python3 .agents/skills/seo-indexation/check_seo.py            # full report
    python3 .agents/skills/seo-indexation/check_seo.py --quiet     # findings only
    python3 .agents/skills/seo-indexation/check_seo.py --json      # machine-readable

Exit code 0 when there is no failure, 1 otherwise. Warnings do not set the exit code.
"""

import argparse
import glob
import json
import os
import re
import sys
import urllib.parse
from collections import deque

DOCS = "docs"
ORIGIN = "https://blog.odicforcesounds.com"
INFRA = {"404.html", "home.html"}          # never in the sitemap or the API
TITLE_MAX = 60                             # characters a result shows, give or take
DESC_MIN, DESC_SOFT_MIN, DESC_MAX = 90, 110, 155
DATE_MIN_YEAR = 2024
DATE_MAX_YEAR = 2026
MIN_INTERNAL_LINKS = 3
MAX_DEPTH = 3
ALLOWED_LD = {"BlogPosting", "CollectionPage", "WebPage"}


class Report:
    def __init__(self):
        self.failures = []
        self.warnings = []

    def fail(self, where, what):
        self.failures.append((where, what))

    def warn(self, where, what):
        self.warnings.append((where, what))


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def one(pattern, src, flags=re.S | re.I):
    match = re.search(pattern, src, flags)
    return " ".join(match.group(1).split()) if match else ""


def page_facts(path):
    src = read(path)
    name = os.path.basename(path)
    facts = {
        "name": name,
        "title": one(r"<title>(.*?)</title>", src),
        "description": one(r'<meta name="description" content="(.*?)"', src),
        "canonical": one(r'<link rel="canonical" href="(.*?)"', src),
        "robots": one(r'<meta name="robots" content="(.*?)"', src).lower(),
        "h1": len(re.findall(r"<h1\b", src, re.I)),
        "published": one(r'name="article:published_time" content="(.*?)"', src),
        "ld": re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S),
        "bilingual": "data-lang-block" in src,
        "hreflang": "hreflang" in src,
    }
    links = []
    for href in re.findall(r'<a\b[^>]*href="([^"]*)"', src, re.I):
        value = href.strip()
        if not value or value.startswith(("#", "?", "mailto:", "tel:", "javascript:", "data:")):
            continue
        if value.startswith(("http://", "https://", "//")):
            if ORIGIN in value:
                value = value.split(ORIGIN, 1)[1]
            else:
                continue
        target = urllib.parse.unquote(value.split("#")[0].split("?")[0]).lstrip("./")
        if target.endswith(".html") and target in facts_targets:
            links.append(target)
    return facts, sorted(set(links))


# filled once, before the scan, so a relative link can be recognised as a page
facts_targets = set()


def check_titles(pages, report):
    seen = {}
    for name, facts in pages.items():
        title = facts["title"]
        if not title:
            report.fail(name, "no <title>")
            continue
        if len(title) > TITLE_MAX:
            report.warn(name, "title is %d characters, a result shows about %d"
                        % (len(title), TITLE_MAX))
        seen.setdefault(title.lower(), []).append(name)
    for title, owners in seen.items():
        if len(owners) > 1:
            report.fail(", ".join(owners), "the same <title> on %d pages" % len(owners))


def check_descriptions(pages, report):
    seen = {}
    for name, facts in pages.items():
        text = facts["description"]
        if not text:
            report.fail(name, "no meta description")
            continue
        if len(text) > DESC_MAX:
            report.fail(name, "description is %d characters (max %d)" % (len(text), DESC_MAX))
        elif len(text) < DESC_MIN:
            report.fail(name, "description is %d characters (min %d)" % (len(text), DESC_MIN))
        elif len(text) < DESC_SOFT_MIN:
            report.warn(name, "description is %d characters, under the %d soft floor"
                        % (len(text), DESC_SOFT_MIN))
        seen.setdefault(text.lower(), []).append(name)
    for text, owners in seen.items():
        if len(owners) > 1:
            report.fail(", ".join(owners), "the same description on %d pages" % len(owners))


def check_canonical(pages, report):
    for name, facts in pages.items():
        if name in INFRA:
            continue
        want = ORIGIN + "/" if name == "index.html" else ORIGIN + "/" + name
        got = facts["canonical"]
        if not got:
            report.fail(name, "no canonical")
        elif got != want:
            report.fail(name, "canonical is %s, expected %s" % (got, want))


def check_indexability(pages, sitemap, api, report):
    noindex = {name for name, facts in pages.items() if "noindex" in facts["robots"]}
    listed = set(sitemap)
    indexed = set(api)
    for name in sorted(noindex):
        if name in listed:
            report.fail(name, "noindex, yet listed in sitemap.xml")
        if name in indexed:
            report.fail(name, "noindex, yet present in docs/api/index.json")
    for name in sorted(set(pages) - INFRA - noindex - listed):
        report.fail(name, "indexable page missing from sitemap.xml")
    for url in sorted(listed - set(pages)):
        report.fail(url, "sitemap URL without a page")
    for name in sorted(set(pages) - INFRA - noindex - indexed):
        report.warn(name, "missing from docs/api/index.json")
    for name in sorted(noindex):
        report.warn(name, "kept out of the index on purpose — say so in the page or the docs")


def check_sitemap(xml, report):
    if not xml:
        report.fail("docs/sitemap.xml", "missing — run build_sitemap.py")
        return []
    urls = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml)
    lastmods = re.findall(r"<lastmod>\s*([^<]*?)\s*</lastmod>", xml)
    names = []
    for url in urls:
        if not url.startswith(ORIGIN + "/"):
            report.fail("docs/sitemap.xml", "URL on another origin: %s" % url)
            continue
        tail = url[len(ORIGIN) + 1:]
        names.append("index.html" if tail in ("", "index.html") else tail)
    if len(set(names)) != len(names):
        report.fail("docs/sitemap.xml", "%d duplicate <loc>" % (len(names) - len(set(names))))
    if len(lastmods) != len(urls):
        report.warn("docs/sitemap.xml", "%d URLs without <lastmod>" % (len(urls) - len(lastmods)))
    for lastmod in lastmods:
        year = lastmod[:4]
        if year and not (str(DATE_MIN_YEAR) <= year <= str(DATE_MAX_YEAR)):
            report.fail("docs/sitemap.xml", "lastmod outside %d-%d: %s"
                        % (DATE_MIN_YEAR, DATE_MAX_YEAR, lastmod))
    return names


def check_robots(text, report):
    if not text:
        report.fail("docs/robots.txt", "missing — run build_sitemap.py")
        return
    if "Sitemap: %s/sitemap.xml" % ORIGIN not in text:
        report.fail("docs/robots.txt", "no Sitemap line for %s" % ORIGIN)
    groups, current = [], None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.lower().startswith("user-agent:"):
            current = {"agent": stripped.split(":", 1)[1].strip(), "rules": []}
            groups.append(current)
        elif stripped.lower().startswith(("allow:", "disallow:")) and current is not None:
            current["rules"].append(stripped)
        elif stripped.lower().startswith("sitemap:"):
            pass
        else:
            report.fail("docs/robots.txt", "unrecognised line: %s" % stripped)
    if not groups:
        report.fail("docs/robots.txt", "no User-agent group")
        return
    first = set(groups[0]["rules"])
    for group in groups[1:]:
        if set(group["rules"]) != first:
            report.warn("docs/robots.txt", "group %r has different rules from the first group"
                        % group["agent"])
    disallow = " ".join(first)
    for path in ("/api/", "/archive/", "/obsdRouter/"):
        if "Disallow: %s" % path not in disallow:
            report.fail("docs/robots.txt", "%s is not disallowed" % path)


def check_dates(pages, report):
    for name, facts in pages.items():
        if facts["h1"] != 1:
            report.fail(name, "%d <h1> elements" % facts["h1"])
        if not facts["ld"]:
            report.warn(name, "no JSON-LD block")
            continue
        if len(facts["ld"]) > 1:
            report.fail(name, "%d JSON-LD blocks" % len(facts["ld"]))
            continue
        try:
            data = json.loads(facts["ld"][0])
        except Exception as exc:
            report.fail(name, "JSON-LD does not parse: %s" % exc)
            continue
        node = None
        for item in data.get("@graph", [data]):
            if item.get("@type") in ALLOWED_LD:
                node = item
                break
        if node is None:
            report.fail(name, "no BlogPosting/CollectionPage/WebPage node")
            continue
        published = str(node.get("datePublished", ""))
        if not published:
            report.warn(name, "JSON-LD without datePublished")
        else:
            year = published[:4]
            if year and not (str(DATE_MIN_YEAR) <= year <= str(DATE_MAX_YEAR)):
                report.fail(name, "datePublished %s outside %d-%d"
                            % (published, DATE_MIN_YEAR, DATE_MAX_YEAR))
            meta = facts["published"]
            if meta and meta[:4] != year:
                report.fail(name, "article:published_time %s disagrees with datePublished %s"
                            % (meta, published))
        if facts["published"] and meta_year_bad(facts["published"]):
            report.fail(name, "article:published_time %s outside %d-%d"
                        % (facts["published"], DATE_MIN_YEAR, DATE_MAX_YEAR))


def meta_year_bad(value):
    year = value[:4]
    return bool(year) and not (str(DATE_MIN_YEAR) <= year <= str(DATE_MAX_YEAR))


def check_links(graph, report):
    for name, targets in graph.items():
        if name in INFRA:
            continue
        if len(targets) < MIN_INTERNAL_LINKS:
            report.warn(name, "%d internal links out (median is higher, so this page is a leaf)"
                        % len(targets))
    if "index.html" not in graph:
        report.fail("index.html", "the front page is missing")
        return
    depth = {"index.html": 0}
    queue = deque(["index.html"])
    while queue:
        node = queue.popleft()
        for target in graph.get(node, []):
            if target not in depth:
                depth[target] = depth[node] + 1
                queue.append(target)
    orphans = [name for name in graph if name not in INFRA and name not in depth]
    for name in orphans:
        report.warn(name, "not reachable from index.html")
    for name, level in sorted(depth.items()):
        if level > MAX_DEPTH and name not in INFRA:
            report.warn(name, "%d clicks from the front page" % level)


def check_languages(pages, report):
    silent = [name for name, facts in pages.items()
              if facts["bilingual"] and not facts["hreflang"]]
    if silent:
        report.warn("%d pages" % len(silent),
                    "two languages in one URL without hreflang (both are indexed as one document)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit indexation, read-only.")
    parser.add_argument("--quiet", action="store_true", help="findings only")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    paths = sorted(glob.glob(os.path.join(DOCS, "*.html")))
    if not paths:
        print("no pages found", file=sys.stderr)
        return 1
    global facts_targets
    facts_targets = {os.path.basename(p) for p in paths}

    pages, graph = {}, {}
    for path in paths:
        facts, links = page_facts(path)
        pages[facts["name"]] = facts
        graph[facts["name"]] = links

    sitemap_xml = read(os.path.join(DOCS, "sitemap.xml")) if os.path.exists(os.path.join(DOCS, "sitemap.xml")) else ""
    robots = read(os.path.join(DOCS, "robots.txt")) if os.path.exists(os.path.join(DOCS, "robots.txt")) else ""
    api_path = os.path.join(DOCS, "api", "index.json")
    api = set()
    if os.path.exists(api_path):
        try:
            api = {item["path"] for item in json.load(open(api_path, encoding="utf-8"))["articles"]}
        except Exception as exc:
            print("docs/api/index.json does not parse: %s" % exc, file=sys.stderr)
            return 1

    report = Report()
    sitemap = check_sitemap(sitemap_xml, report)
    check_titles(pages, report)
    check_descriptions(pages, report)
    check_canonical(pages, report)
    check_indexability(pages, sitemap, api, report)
    check_dates(pages, report)
    check_robots(robots, report)
    check_links(graph, report)
    check_languages(pages, report)

    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "sitemap": len(sitemap),
            "api": len(api),
            "failures": [{"where": w, "what": t} for w, t in report.failures],
            "warnings": [{"where": w, "what": t} for w, t in report.warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if report.failures else 0

    if not args.quiet:
        print("pages %d | sitemap %d | api %d | canonical host %s"
              % (len(pages), len(sitemap), len(api), ORIGIN))

    if report.failures:
        print("failures %d" % len(report.failures))
        for where, what in report.failures[:40]:
            print("  %s — %s" % (where, what))
        if len(report.failures) > 40:
            print("  … and %d more" % (len(report.failures) - 40))
    if report.warnings:
        print("warnings %d" % len(report.warnings))
        for where, what in report.warnings[:15]:
            print("  %s — %s" % (where, what))
        if len(report.warnings) > 15:
            print("  … and %d more" % (len(report.warnings) - 15))
    if not report.failures and not report.warnings:
        print("nothing to fix")
    elif not report.failures:
        print("no failures")
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
