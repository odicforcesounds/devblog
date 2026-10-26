#!/usr/bin/env python3
"""Verify docs/i3Hero.html (structure, self-containment) + the index entry."""
import re

PATH = "docs/i3Hero.html"
src = open(PATH, encoding="utf-8").read()
idx = open("docs/index.html", encoding="utf-8").read()
problems = []

# 1. tag balance for the tags that matter
void_tags = {"meta", "link", "br", "hr", "img", "input"}
for tag in ["html", "head", "body", "style", "script", "main", "nav", "footer",
            "header", "table", "thead", "tbody", "section", "label", "button",
            "ol", "ul", "pre", "details", "summary", "a", "tr", "h1", "h2", "h3",
            "div", "span", "p", "li", "kbd", "code", "b", "i", "figure", "figcaption"]:
    opens = len(re.findall(r"<%s(\s|>)" % tag, src))
    closes = len(re.findall(r"</%s>" % tag, src))
    if tag in void_tags:
        continue
    if opens != closes:
        problems.append("tag %s: %d open vs %d close" % (tag, opens, closes))

# dangling fragments of the sort that hurt the mutt draft
if re.search(r"<i3-msg", src):
    problems.append("broken <i3-msg tag left")
for token in ["TODO", "TBD", "XXX", "placeholder-glyph", "j4-dmenu"]:
    if token in src:
        problems.append("draft token left: %s" % token)

# 2. no external resources
for m in re.finditer(r"(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", src):
    url = m.group(1)
    if re.match(r"https?:", url) or url.startswith("//"):
        problems.append("external URL: %s" % url)
if re.search(r"@import|url\(", src):
    problems.append("CSS import/url() found")

# 3. selectors in the JS must exist in the HTML
anchors = re.findall(r'<li><a href="#([^"]+)"', src)
ids = re.findall(r'<section class="entry" id="([^"]+)"', src)
missing = [a for a in anchors if a not in ids]
if missing:
    problems.append("toc anchors without section: %s" % missing)
if len(ids) != 13:
    problems.append("expected 13 sections, got %d" % len(ids))

# 4. checklist keys must be unique and 12
keys = re.findall(r'input type="checkbox" data-key="([^"]+)"', src)
if len(keys) != 12 or len(set(keys)) != 12:
    problems.append("checklist keys wrong: %s" % keys)

# 5. 3 Home links (sticky bar + footer x2)
if src.count('href="./index.html"') < 3:
    problems.append("fewer than 3 Home links to ./index.html")

# 6. dark theme sanity
if "#ffffff" in src or "background:#fff" in src:
    problems.append("light background colour found")

# 7. index.html: entry in Linux & Open Source, counts 36/36, no stale 35
if idx.count("i3Hero.html") != 3:  # li href + name-tag + data inline
    problems.append("index references i3Hero.html %d times (want 3)" % idx.count("i3Hero.html"))
cat = re.search(r'data-title="Linux &amp; Open Source">.*?</section>', idx, re.S)
if not cat:
    problems.append("Linux category not found in index")
else:
    block = cat.group(0)
    if "i3Hero.html" not in block:
        problems.append("i3 entry not inside Linux & Open Source")
    if re.findall(r'aria-hidden="true">35<', block):
        problems.append("Linux category still has a stale '35' count")
    if block.count('aria-hidden="true">36<') != 2:
        problems.append("Linux category counts not 36/36")

# 8. inline creation date added
if '"i3Hero.html": "2026-10-26T16:20:00+01:00"' not in idx:
    problems.append("inline CREATION_DATES entry missing")

# 9. dates.json untouched is the user's rule
dj = open("docs/dates.json", encoding="utf-8").read()
if "i3Hero" in dj:
    problems.append("dates.json contains the new file although it must not be edited")

if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
    raise SystemExit(1)
print("ALL OK — i3Hero.html: 13 sections, 12 checks, no external resources,",
      "index entry in Linux & Open Source (36/36) + inline date.")
