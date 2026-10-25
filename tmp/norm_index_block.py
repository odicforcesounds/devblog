#!/usr/bin/env python3
import sys, re, urllib.parse

target = "docs/index.html"
raw = open(target, encoding="utf-8").read().splitlines(True)

# Only normalize lines inside the Monkey Blog links block so we do not touch unrelated markup.
start = None
for i, line in enumerate(raw):
    if "The Chosen Monkey | God(道) Choice to Save Reality" in line:
        start = i
        break

if start is None:
    sys.exit("no monkey block found")

i = start
while i < len(raw):
    line = raw[i]
    m = re.search(r'<li><a href="([^"]+)">([^<]*)</a><span>([^<]*)</span>\s*(?:<span[^>]*>([^<]*)</span>)?\s*</li>', line)
    if not m:
        i += 1
        continue
    href, title, desc, tag = m.group(1), m.group(2), m.group(3), (m.group(4) or "")
    if "theChosenMonkey.html" in href and "In English." in desc and len(desc.strip()) < 120:
        raw[i] = f'          <li><a href="{href}">{title}</a><span>In English. {desc}</span><span class="name-tag">{href.split("/")[-1]}</span></li>\n'
    i += 1

with open(target, "w", encoding="utf-8") as f:
    f.writelines(raw)

print("normalized index lines")
