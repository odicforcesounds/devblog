#!/usr/bin/env python3
"""Verify docs/xtermHero.html (structure, self-containment, index entry)."""
import re

PATH = "docs/xtermHero.html"
src = open(PATH, encoding="utf-8").read()
problems = []

# 1. tag balance for the tags that matter
void_tags = {"meta", "link", "br", "hr", "img", "input"}
tags = ["html", "head", "body", "style", "script", "main", "nav", "footer",
        "header", "table", "thead", "tbody", "section", "label", "button",
        "ol", "ul", "pre", "details", "summary", "a", "tr", "th", "td", "p", "li"]
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
ids = set(re.findall(r'<section class="entry" id="([^"]+)"', src))
missing = [a for a in anchors if a not in ids]
if missing:
    problems.append("toc anchors without section: %s" % missing)
if len(anchors) != 13 or len(ids) != 13:
    problems.append("expected 13 toc anchors and 13 sections, got %d and %d"
                    % (len(anchors), len(ids)))

# 4. checklist keys + counter wording
keys = re.findall(r'data-key="([^"]+)"', src)
if len(keys) != 12:
    problems.append("expected 12 checklist items, got %d" % len(keys))
if '<span id="xtCount">0 / 12' not in src:
    problems.append("checklist counter not 0 / 12")

# 5. Home links + distinct storage key
if src.count("./index.html") < 2:
    problems.append("missing Home link(s)")
if "xtermHero.progress.v1" not in src:
    problems.append("xterm storage key missing")

# 6. title demo buttons exist outside <pre>
if "id=\"titleDemo\"" not in src or "id=\"titleRestore\"" not in src:
    problems.append("title demo buttons missing")
demo_zone = src.split("id=\"titleDemo\"")[0][-80:]
if demo_zone.endswith("<pre>"):
    problems.append("title demo buttons still inside <pre>")

# 7. index.html entry
idx = open("docs/index.html", encoding="utf-8").read()
needle = '<li><a href="./xtermHero.html">xterm \u2014 From Nothing to Hero</a>'
if needle not in idx:
    problems.append("index entry missing")
if idx.count("xtermHero.html") != 3:  # li href + name-tag + data inline
    problems.append("index references xtermHero.html %d times (want 3)"
                    % idx.count("xtermHero.html"))
cat = re.search(r'data-title="Programming &amp; Development">.*?</section>', idx, re.S).group(0)
if re.findall(r'aria-hidden="true">55<', cat):
    problems.append("Programming category still has a stale '55' count")
if cat.count('aria-hidden="true">56<') != 1 or cat.count('aria-hidden="true">54<') != 1:
    problems.append("Programming category counts not 56/54")
if '"xtermHero.html": "2026-10-26T12:30:00+01:00"' not in idx:
    problems.append("inline CREATION_DATES entry missing")

# 8. leftover draft garbage must be gone
for bad_token in ["かに", "拉的", "Shiff", "translastes", "Уt", "吓", "Uterm:", "blac</span>"]:
    if bad_token in src:
        problems.append("leftover draft token: %s" % bad_token)

# 9. dates.json intocado (regra do utilizador)
dj = open("docs/dates.json", encoding="utf-8").read()
for probe in ("openbsdCompilation", "openbsdDesktop", "xtermHero"):
    if probe in dj:
        problems.append("dates.json contains %s although it must not be edited" % probe)

print("PROBLEMS: %d" % len(problems))
for p in problems:
    print(" -", p)
print("toc anchors:", len(anchors), "| ids:", len(ids),
      "| checklist keys:", len(keys), "| home links:", src.count("./index.html"))
if not problems:
    print("ALL OK")
