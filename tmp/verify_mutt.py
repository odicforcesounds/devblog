#!/usr/bin/env python3
"""Verify docs/muttHero.html (structure, self-containment) + the index entry."""
import re

PATH = "docs/muttHero.html"
src = open(PATH, encoding="utf-8").read()
idx = open("docs/index.html", encoding="utf-8").read()
problems = []

# 1. tag balance for the tags that matter
void_tags = {"meta", "link", "br", "hr", "img", "input"}
for tag in ["html", "head", "body", "style", "script", "main", "nav", "footer",
            "header", "table", "thead", "tbody", "section", "label", "button",
            "ol", "ul", "pre", "details", "summary", "a", "tr", "h1", "h2", "h3",
            "div", "span", "p", "li", "textarea", "kbd", "code", "b", "i"]:
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

# 6. dark theme sanity: our own palette only, no light background hardcodes
if "background:#fff" in src or "background: #fff" in src or "#ffffff" in src:
    problems.append("light background colour found")

# 7. index entry present in Programming & Development, counts 56/54
if idx.count("muttHero.html") != 3:  # li href + name-tag + data inline
    problems.append("index references muttHero.html %d times (want 3)"
                    % idx.count("muttHero.html"))
cat = re.search(r'data-title="Programming &amp; Development">.*?</section>', idx, re.S)
if not cat:
    problems.append("Programming category not found in index")
else:
    block = cat.group(0)
    if "muttHero.html" not in block:
        problems.append("mutt entry not inside Programming & Development")
    if re.findall(r'aria-hidden="true">55<', block):
        problems.append("Programming category still has a stale '55' count")
    if block.count('aria-hidden="true">56<') != 1:
        problems.append("Programming cat-head count not 56")
    if block.count('aria-hidden="true">54<') != 1:
        problems.append("Programming EN count not 54")
    if re.findall(r'aria-hidden="true">53<', block):
        problems.append("Programming category still has a stale '53' EN count")

# 8. inline creation date added, dates.json untouched is the user's rule
if '"muttHero.html": "2026-10-26T14:10:00+01:00"' not in idx:
    problems.append("inline CREATION_DATES entry missing")

# 9. leftover draft tokens
for token in ["TODO", "TBD", "XXX", "placeholder"]:
    if token in src:
        problems.append("draft token left: %s" % token)

if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
    raise SystemExit(1)
print("ALL OK — muttHero.html: 13 sections, 12 checks, no external resources,",
      "index entry in Programming & Development (56/54) + inline date.")
