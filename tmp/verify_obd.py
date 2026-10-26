#!/usr/bin/env python3
"""Verify docs/openbsdDesktop.html (structure, self-containment, index entry)."""
import re

PATH = "docs/openbsdDesktop.html"
src = open(PATH, encoding="utf-8").read()
problems = []

# 1. tag balance for the tags that matter
void_tags = {"meta", "link", "br", "hr", "img", "input"}
tags = ["html", "head", "body", "style", "script", "main", "nav", "footer",
        "header", "table", "thead", "tbody", "section", "label", "button",
        "ol", "ul", "pre", "details", "summary", "a", "tr", "th", "td"]
for tag in tags:
    opens = len(re.findall(r"<%s(\s|>)" % tag, src))
    closes = len(re.findall(r"</%s>" % tag, src))
    if tag in void_tags:
        continue
    if opens != closes:
        problems.append("tag %s: %d open vs %d close" % (tag, opens, closes))

# 2. no external resources
for m in re.finditer(r"(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", src):
    url = m.group(1)
    if re.match(r"https?:", url) or url.startswith("//"):
        problems.append("external URL: %s" % url)
if re.search(r"@import|url\(", src):
    problems.append("CSS import/url() found")

# 3. selectors in the JS must exist in the HTML
anchors = re.findall(r'<li><a href="#([^"]+)"', src)
ids = set(re.findall(r"<section class=\"entry\" id=\"([^\"]+)\"", src))
missing = [a for a in anchors if a not in ids]
if missing:
    problems.append("toc anchors without section: %s" % missing)
if len(ids) != 13:
    problems.append("expected 13 sections, got %d" % len(ids))

# 4. checklist keys + counter wording
keys = re.findall(r'data-key="([^"]+)"', src)
if len(keys) != 10:
    problems.append("expected 10 checklist items, got %d" % len(keys))
if "<span id=\"deskCount\">0 / 10" not in src:
    problems.append("checklist counter not 0 / 10")

# 5. Home links + storage key distinct from the sibling page
if src.count('./index.html') < 2:
    problems.append("missing Home link(s)")
if 'openbsdDesktop.progress.v1' not in src:
    problems.append('desktop storage key missing')

# 6. index.html entry
idx = open("docs/index.html", encoding="utf-8").read()
needle = '<li><a href="./openbsdDesktop.html">OpenBSD for Desktops</a>'
if needle not in idx:
    problems.append("index entry missing")
if idx.count('openbsdDesktop.html') != 3:  # li href + name-tag + data inline
    problems.append("index references openbsdDesktop.html %d times (want 3)"
                    % idx.count('openbsdDesktop.html'))
cat = re.search(r'data-title="BSD[^"]*">.*?</section>', idx, re.S).group(0)
if re.findall(r'aria-hidden="true">36<', cat):
    problems.append("BSD category still has a stale '36' count")
if cat.count('aria-hidden="true">37<') != 2:
    problems.append("BSD category '37' count wrong")
if '"openbsdDesktop.html": "2026-10-26T11:05:00+01:00"' not in idx:
    problems.append("inline CREATION_DATES entry missing")

# 7. dates.json intocado (regra do utilizador); confirma estado
dj = open("docs/dates.json", encoding="utf-8").read()
if "openbsdDesktop" in dj or "openbsdCompilation" in dj:
    problems.append("dates.json contains new files although it must not be edited")

print("PROBLEMS: %d" % len(problems))
for p in problems:
    print(" -", p)
print("toc anchors:", len(anchors), "| ids:", len(ids),
      "| checklist keys:", len(keys), "| home links:", src.count('./index.html'))
if not problems:
    print("ALL OK")
