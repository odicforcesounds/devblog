import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..", "..")))

import collections, json, re, sys

slug = sys.argv[1]
s = open(f"docs/{slug}.html", encoding="utf-8").read()
pt_start = s.index('<div id="lang-pt" data-lang-block="pt" hidden>')
pt_end = s.index("</div>\n\n<script>", pt_start)
pt = s[pt_start:pt_end]
en = s[s.index('<div id="lang-en" data-lang-block="en">'):pt_start]

print("h1 in document:", len(re.findall(r"<h1\b", s)),
      "| EN:", len(re.findall(r"<h1\b", en)), "| PT:", len(re.findall(r"<h1\b", pt)))
ids = re.findall(r'\bid="([^"]+)"', s)
print("duplicate ids:", {k: v for k, v in collections.Counter(ids).items() if v > 1} or "none")
print("blocks:", re.findall(r'data-lang-block="(\w+)"', s),
      "| switch above blocks:", s.index('class="lang-switch"') < s.index('<div id="lang-en"'))
print("PT sections:", pt.count('class="plevel'), "| .level left in PT:", len(re.findall(r'class="level[\" ]', pt)))
print("PT data-level/data-gate/data-status:", pt.count("data-level="), pt.count("data-gate="), pt.count("data-status"),
      "| lock overlays:", pt.count("lock-screen"), "| scripts:", pt.count("<script"))
print("PT grid shell removed:", 'class="shell"' not in pt, "| pt-shell:", 'class="pt-shell"' in pt)
anchors = set(re.findall(r'href="#([^"]+)"', pt))
print("PT internal anchors:", len(anchors), "| broken:", sorted(a for a in anchors if a not in set(ids)) or "none")

left = []
for tag, body in re.findall(r"<(p|li|h2|h3|h4|td|th|dd|dt|caption)\b[^>]*>([\s\S]*?)</\1>", pt):
    if 'target="_blank"' in body or 'class="src"' in body:
        continue
    txt = re.sub(r"<[^>]+>", " ", body)
    words = txt.split()
    if len(words) >= 6 and re.search(r"\b(the|and|with|this|that|from|your)\b", txt) and not re.search(r"\b(de|para|que|com|uma|não|é|os|as|do|da)\b", txt):
        left.append((tag, " ".join(words)[:70]))
print("English-looking prose left in PT:", len(left))
for t in left[:8]:
    print("   -", t[0], "|", t[1])

units = {}
for line in open(f"tmp/{slug}.units.json", encoding="utf-8"):
    if line.strip():
        u = json.loads(line)
        units[u["id"]] = u["html"]
try:
    m = json.load(open(f"tmp/{slug}.pt.json", encoding="utf-8"))
    ident = [k for k, v in m.items() if units.get(k) == v]
    print("translations:", len(m), "| identity:", len(ident),
          "| units untranslated:", len([k for k in units if k not in m]))
except FileNotFoundError:
    print("non-citation units untranslated:", "n/a (no translation file yet)")
print("size: EN", len(en), "| PT", len(pt))
