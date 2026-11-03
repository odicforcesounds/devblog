import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json, re

path = "docs/pythonCert.html"
src = open(path, encoding="utf-8").read()
m = re.search(r"<main\b[^>]*>", src)
main_start = m.end()
main_end = src.index("</main>", main_start)
main = src[main_start:main_end]

BLOCK = {"h1", "h2", "h3", "h4", "p", "li", "td", "th", "dt", "dd", "caption", "summary", "figcaption"}
SKIP = {"pre", "code", "script", "style", "aside"}

units, stack, sections = [], [], []
skipping = 0

for t in re.finditer(r"<(/?)([a-zA-Z0-9]+)\b[^>]*?(/?)>", main):
    closing, tag, selfclose = t.group(1), t.group(2).lower(), t.group(3)
    if tag in SKIP:
        skipping = max(0, skipping + (-1 if closing else 1))
    if closing:
        if stack and stack[-1]["tag"] == tag:
            open_ = stack.pop()
            if open_["tag"] in BLOCK and not open_["hasBlockChild"] and not open_["skip"]:
                html = main[open_["start"]:t.start()]
                if re.sub(r"<[^>]+>", "", html).strip():
                    units.append({"tag": open_["tag"], "section": sections[-1] if sections else "page",
                                  "html": html.strip()})
        if tag == "section" and sections:
            sections.pop()
        continue
    if tag in BLOCK or tag == "section":
        m_id = re.search(r'\bid="([^"]+)"', t.group(0))
        if tag == "section" and not selfclose:
            sections.append(m_id.group(1) if m_id else (sections[-1] if sections else "page"))
        if not selfclose and tag in BLOCK:
            stack.append({"tag": tag, "start": t.end(), "hasBlockChild": False, "skip": skipping > 0})
            for s in stack[:-1]:
                s["hasBlockChild"] = True

for i, u in enumerate(units, 1):
    u["id"] = f"u{i}"

with open("tmp/pythonCert.units2.json", "w", encoding="utf-8") as fh:
    for u in units:
        fh.write(json.dumps(u, ensure_ascii=False) + "\n")

per = {}
for u in units:
    per.setdefault(u["section"], [0, 0])
    per[u["section"]][0] += 1
    per[u["section"]][1] += len(re.sub(r"<[^>]+>", " ", u["html"]).split())
for sec, (n, w) in per.items():
    print(f"{sec:<24} units={n:<5} words={w}")
print("total", len(units), sum(v[1] for v in per.values()))
