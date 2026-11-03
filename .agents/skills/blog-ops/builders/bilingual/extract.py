import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..", "..")))

import json, re, sys

slug = sys.argv[1]
print_secs = []
if "--print" in sys.argv:
    print_secs = sys.argv[sys.argv.index("--print") + 1].split(",")

src = open(f"docs/{slug}.html", encoding="utf-8").read()
m = re.search(r"<main\b[^>]*>", src)
if m:
    start = m.end()
    end = src.index("</main>", start)
else:  # no <main>: use the body up to the first script
    start = src.index("<body") + src[src.index("<body"):].index(">") + 1
    end = src.index("<script", start)
main = src[start:end]

BLOCK = {"h1", "h2", "h3", "h4", "h5", "p", "li", "td", "th", "dt", "dd", "caption", "summary", "figcaption"}
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
        mid = re.search(r'\bid="([^"]+)"', t.group(0))
        if tag == "section" and not selfclose:
            sections.append(mid.group(1) if mid else (sections[-1] if sections else "page"))
        if not selfclose and tag in BLOCK:
            stack.append({"tag": tag, "start": t.end(), "hasBlockChild": False, "skip": skipping > 0})
            for s in stack[:-1]:
                s["hasBlockChild"] = True

for i, u in enumerate(units, 1):
    u["id"] = f"u{i}"
with open(f"tmp/{slug}.units.json", "w", encoding="utf-8") as fh:
    for u in units:
        fh.write(json.dumps(u, ensure_ascii=False) + "\n")

per = {}
for u in units:
    per.setdefault(u["section"], [0, 0, 0])   # units, prose words, code-ish units
    per[u["section"]][0] += 1
    txt = re.sub(r"<[^>]+>", " ", u["html"])
    stripped = re.sub(r"<code>[\s\S]*?</code>", "", u["html"])
    if u["html"].strip().startswith("<code>") and u["html"].strip().endswith("</code>"):
        per[u["section"]][2] += 1
    else:
        per[u["section"]][1] += len(re.sub(r"<[^>]+>", " ", stripped).split())

for sec, (n, w, c) in per.items():
    print(f"{sec:<22} units={n:<4} words={w:<5} code-cells={c}")
print("total", len(units), sum(v[1] for v in per.values()))

for u in units:
    if u["section"] in print_secs:
        print(u["id"], "|", u["section"], "|", u["tag"], "|", u["html"])
