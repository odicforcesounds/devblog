import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json, re, sys

path = "docs/pythonCert.html"
src = open(path, encoding="utf-8").read()

m = re.search(r"<main\b[^>]*>", src)
main_start = m.end()
main_end = src.index("</main>", main_start)
main = src[main_start:main_end]

BLOCK = {"h1", "h2", "h3", "h4", "p", "li", "td", "th", "dt", "dd", "caption", "summary", "figcaption"}
SKIP = {"pre", "code", "script", "style", "aside"}

tokens = re.finditer(r"<(/?)([a-zA-Z0-9]+)\b[^>]*?(/?)>", main)
units = []
stack = []          # [{tag, start, hasBlockChild, skip}]
skipping = 0

for t in tokens:
    closing, tag, selfclose = t.group(1), t.group(2).lower(), t.group(3)
    if tag in SKIP:
        skipping += 1 if not closing else -1
        skipping = max(0, skipping)
    if closing:
        if stack and stack[-1]["tag"] == tag:
            open_ = stack.pop()
            if open_["tag"] in BLOCK and not open_["hasBlockChild"] and not open_["skip"]:
                html = main[open_["start"]:t.start()]
                if re.sub(r"<[^>]+>", "", html).strip():
                    units.append({"tag": open_["tag"], "html": html.strip()})
        if stack and tag in {s["tag"] for s in stack}:
            for s in stack:
                if s["tag"] in BLOCK:
                    s["hasBlockChild"] = True
    elif not selfclose and tag in BLOCK:
        stack.append({"tag": tag, "start": t.end(), "hasBlockChild": False,
                      "skip": skipping > 0})
        for s in stack[:-1]:
            if s["tag"] in BLOCK:
                s["hasBlockChild"] = True

for i, u in enumerate(units, 1):
    u["id"] = f"u{i}"

with open("tmp/pythonCert.units.json", "w", encoding="utf-8") as fh:
    for u in units:
        fh.write(json.dumps(u, ensure_ascii=False) + "\n")

words = sum(len(re.sub(r"<[^>]+>", " ", u["html"]).split()) for u in units)
print(f"units={len(units)} words={words}")
for u in units[:3]:
    print(u["id"], u["tag"], re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", u["html"]))[:90])
