# -*- coding: utf-8 -*-
"""
Constrói os cartões dos dois manuais INGLESES e o grafo de docs/theTurning.html.

Cada cartão novo tem exactamente 3 saídas:
  1. a unidade seguinte da mesma secção (em ciclo)
  2. travessia para a secção oposta do outro manual
  3. volta ao índice da secção
"""
import re, html, json, sys

MIST = "docs/chineseMysticismManual.html"
BUD = "docs/buddhismManual.html"
GAME = "docs/theTurning.html"

# ---------------------------------------------------------------- utils

def read(p):
    return open(p, encoding="utf-8").read()

def clean(s):
    s = s.replace("</span><span", "</span> <span").replace("</td><td", "</td> <td")
    s = re.sub(r'<span class="pinyin">\s*(.*?)\s*</span>', r' (\1)', s, flags=re.S)
    s = re.sub(r'<span class="py">\s*(.*?)\s*</span>', r' (\1)', s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:!?»”])", r"\1", s)
    return s.strip()

SENT = re.compile(r"(?<=[.!?…»”])\s+(?=[«\"“(\[]?[A-Z0-9])")

def excerpt(text, first=2, least=200, most=470):
    parts = SENT.split(text)
    out, n = [], 0
    for p in parts:
        if n >= first and len(" ".join(out)) >= least:
            break
        if n >= 6:
            break
        out.append(p)
        n += 1
        if len(" ".join(out)) >= most:
            break
    s = " ".join(out).strip()
    if len(s) > most:
        s = s[:most].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return s

GLUE = {"a", "an", "the", "of", "and", "in", "on", "to", "that", "is", "are", "was",
        "were", "with", "by", "for", "as", "at", "from", "but", "or", "not", "its",
        "their", "this", "these", "those", "it", "be", "has", "have", "had", "which",
        "when", "while", "than", "then", "so", "such", "into", "over", "under"}

def heading(text, limit=56):
    t = text.strip()
    cand = t[:limit]
    end = re.search(r"[.!?…](?=\s)", t[:limit + 12])
    if end and 18 <= end.start() <= limit:
        out = " ".join(t[:end.start()].split())
        return (out[:1].upper() + out[1:]).strip(" .,;:—–\"«»“”")
    best = -1
    for sep in (": ", " — ", " – ", "; ", ", "):
        i = cand.rfind(sep)
        if i >= 20 and i > best:
            best = i
    if best >= 20:
        out = cand[:best]
        words = out.split()
        while words and words[-1].lower().strip(".,;:—–") in GLUE:
            words.pop()
        out = " ".join(words).strip(" .,;:—–\"«»“”")
    elif len(t) > limit and " " in cand:
        out = cand.rsplit(" ", 1)[0].rstrip(" .,;:—–")
        trimmed = re.sub(r"\s*\([^)]*$", "", out).rstrip(" .,;:—–")
        if len(trimmed) >= 18:
            out = trimmed
        out += "…"
    else:
        out = cand.strip()
    return (out[:1].upper() + out[1:]) if out else ""

def snippet(text, limit=54):
    return heading(text, limit)

def wlabel(text, limit=25):
    t = text.strip()
    if len(t) <= limit:
        return t
    out = t[:limit].rsplit(" ", 1)[0]
    words = out.split()
    while words and words[-1].lower().strip(".,;:—–") in GLUE:
        words.pop()
    return " ".join(words) or t.split()[0]

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HEX = re.compile(r"[\u4dc0-\u4dff]")
TRI = re.compile(r"[\u2630-\u2637]")
PINYIN = re.compile(r"^[a-z\u00c0-\u024f\u0300-\u036f\s,·/'-]{1,24}$")

def has_pinyin_name(cell):
    return bool(CJK.search(cell)) and len(cell) <= 14

# ---------------------------------------------------------------- tabelas

TABLES = [
    ("phases",     "Correspondences of the five phases"),
    ("trigrams",   "The eight trigrams"),
    ("hexagrams",  "The sixty-four hexagrams"),
    ("trunks",     "天干"),
    ("branches",   "地支"),
    ("solarterms", "二十四節氣"),
    ("mansions",   "The twenty-eight lunar mansions"),
    ("gods",       "十神"),
    ("organs",     "五臟六腑"),
    ("principles", "八綱"),
    ("tones",      "五音"),
    ("pipes",      "十二律"),
    ("scripts",    "六書"),
    ("creatures",  "四象"),
    ("truths",     "四聖諦"),
    ("factors",    "八正道"),
    ("links",      "十二因緣"),
    ("precepts",   "五戒"),
    ("realms",     "三十一界"),
    ("baskets",    "three baskets"),
    ("schools",    "The main families"),
    ("jhanas",     "eight absorptions"),
    ("sutras1",    "A shelf of early sutras"),
    ("sutras2",    "Ten more, with the one thing"),
    ("chant",      "How the same texts sound"),
    ("mudras",     "Hand gestures"),
    ("paramitas",  "六度 / 十度"),
    ("festivals",  "The year, as most Buddhist countries"),
]

BARE = {
    "Meaning", "What is in it", "Signature", "Contents", "What it marks",
    "What it means in practice", "What it trains", "What it rules out",
    "Traditional function", "Task", "Inhabitants", "Relation to the day master",
    "Principle", "Style", "What drops away", "When", "Examples", "Reading", "Pinyin",
}

def table_rows(body):
    head = re.search(r"<thead>(.*?)</thead>", body, re.S)
    headers = []
    if head:
        headers = [clean(c) for c in re.findall(r"<th[^>]*>(.*?)</th>", head.group(1), re.S)]
    rows = []
    for r in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        cells = [clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if cells:
            rows.append(cells)
    return headers, rows

def build_item(headers, cells, section_glyph):
    glyph, i, bits = None, 0, []

    if re.fullmatch(r"\d+[a-z]?", cells[0]):
        bits.append(cells[0])
        i = 1
        if i < len(cells) and (HEX.search(cells[i]) or TRI.search(cells[i])):
            glyph = cells[i]
            i += 1
        if i < len(cells) and (has_pinyin_name(cells[i]) or cells[i][:1].isalpha()):
            bits.append(cells[i])
            i += 1
    else:
        bits.append(cells[0])
        i = 1
        if i < len(cells) and (HEX.search(cells[0]) or TRI.search(cells[0])) and has_pinyin_name(cells[i]):
            glyph = cells[0]
            bits.append(cells[i])
            i += 1

    if i < len(cells) and cells[i] and headers[i:i + 1] == ["Pinyin"] and PINYIN.match(cells[i]):
        bits.append(cells[i])
        i += 1

    if not glyph:
        for b in bits:
            m = HEX.search(b) or TRI.search(b) or CJK.search(b)
            if m:
                glyph = m.group(0)
                break

    bits = [re.sub(r"\s*\(([^)]*)\)\s*$", r" \1", b).strip() for b in bits]
    bits = list(dict.fromkeys([b for b in bits if b]))
    if len(bits) > 1 and re.fullmatch(r"\d+[a-z]?", bits[0]):
        title = bits[0] + " · " + " ".join(bits[1:])
    else:
        title = " ".join(bits) if len(bits) > 1 and all(PINYIN.match(b) or CJK.search(b) for b in bits[1:]) else " · ".join(bits)

    chunks = []
    for h, v in list(zip(headers[i:], cells[i:])):
        if not v or v in bits:
            continue
        v = v.strip()
        if not v:
            continue
        sent = v if h in BARE else ("%s: %s" % (h, v) if h else v)
        if sent[:1].islower():
            sent = sent[:1].upper() + sent[1:]
        chunks.append(sent)
    text = " ".join(c if c.endswith((".", "!", "?", "…")) else c + "." for c in chunks)
    return title, (glyph or section_glyph), text

# ---------------------------------------------------------------- secções

def parse_section(sid, block, glyph):
    units = []
    pieces = re.split(r"(?=<h3>)", block)
    h3 = None
    used_h3 = set()

    for piece in pieces:
        m = re.match(r"<h3>(.*?)</h3>", piece, re.S)
        if m:
            h3 = clean(m.group(1))
            piece = piece[m.end():]
        ctx = h3

        for pm in re.finditer(r"<p([^>]*)>(.*?)</p>", piece, re.S):
            attrs, body = pm.group(1), pm.group(2)
            if re.search(r'class="[^"]*(source|iast|say|tags|orig|trans|py)[^"]*"', attrs):
                continue
            txt = clean(body)
            if len(txt) < 70 or txt.rstrip().endswith(":"):
                continue
            ex = excerpt(txt)
            if len(ex) < 70:
                continue
            before = piece[:pm.start()]
            h4 = re.findall(r"<h4[^>]*>(.*?)</h4>", before, re.S)
            if h4:
                t = clean(h4[-1])
            elif ctx and ctx not in used_h3:
                t = ctx
                used_h3.add(ctx)
            else:
                t = snippet(txt)
            units.append(("prose", t, ex, sid, "lead" in attrs))

        for key, cap in TABLES:
            for tm in re.finditer(r"<table[^>]*>(.*?)</table>", piece, re.S):
                body = tm.group(1)
                cm = re.search(r"<caption>(.*?)</caption>", body, re.S)
                caption = clean(cm.group(1)) if cm else ""
                if cap.lower() not in caption.lower():
                    continue
                headers, rows = table_rows(body)
                for cells in rows:
                    t, g, x = build_item(headers, cells, glyph)
                    if not t or len(x) < 12:
                        continue
                    units.append(("item", t, x, sid, g))
    return units

def parse_manual(path, manual_name):
    src = read(path)
    starts = [(m.start(), m.group(1)) for m in re.finditer(r'<section class="block" id="([^"]+)"', src)]
    bounds = [s for s, _ in starts[1:]] + [len(src)]
    secs = []
    for (pos, sid), end in zip(starts, bounds):
        block = src[pos:end]
        gm = re.search(r'<span class="block__glyph"[^>]*>(.*?)</span>', block, re.S)
        glyph = clean(gm.group(1)) if gm else "經"
        hm = re.search(r"<h2>(.*?)</h2>", block, re.S)
        h2 = hm.group(1) if hm else ""
        hnm = re.search(r'<span class="han">(.*?)</span>', h2, re.S)
        han = clean(hnm.group(1)) if hnm else ""
        rest = clean(h2.replace(hnm.group(0), "")) if hnm else clean(h2)
        secs.append(dict(id=sid, han=han, title=rest, glyph=glyph, file=path.split("/")[-1],
                         manual=manual_name, units=parse_section(sid, block, glyph)))
    return secs

myst = parse_manual(MIST, "The Dark and the Five")
bud = parse_manual(BUD, "The Sound of Emptiness")

# ---------------------------------------------------------------- travessias

CROSS = {
    ("x", "scope"): ("b", "scope"),
    ("x", "dao"): ("b", "emptiness"),
    ("x", "cosmos"): ("b", "marks"),
    ("x", "yinyang"): ("b", "marks"),
    ("x", "wuxing"): ("b", "meditation"),
    ("x", "bagua"): ("b", "truths"),
    ("x", "yijing"): ("b", "sutras"),
    ("x", "numbers"): ("b", "canon"),
    ("x", "qi"): ("b", "meditation"),
    ("x", "spirit"): ("b", "death"),
    ("x", "dark"): ("b", "emptiness"),
    ("x", "sound"): ("b", "sound"),
    ("x", "writing"): ("b", "canon"),
    ("x", "glyphs"): ("b", "symbols"),
    ("x", "creatures"): ("b", "world"),
    ("x", "fengshui"): ("b", "places"),
    ("x", "alchemy"): ("b", "meditation"),
    ("x", "history"): ("b", "history"),
    ("x", "practice"): ("b", "practice"),
    ("x", "glossary"): ("b", "practice"),
    ("b", "scope"): ("x", "scope"),
    ("b", "buddha"): ("x", "dao"),
    ("b", "truths"): ("x", "bagua"),
    ("b", "marks"): ("x", "yinyang"),
    ("b", "jewels"): ("x", "practice"),
    ("b", "world"): ("x", "cosmos"),
    ("b", "canon"): ("x", "writing"),
    ("b", "schools"): ("x", "history"),
    ("b", "emptiness"): ("x", "dark"),
    ("b", "meditation"): ("x", "qi"),
    ("b", "mantra"): ("x", "sound"),
    ("b", "mantras"): ("x", "sound"),
    ("b", "sutras"): ("x", "writing"),
    ("b", "sound"): ("x", "sound"),
    ("b", "symbols"): ("x", "creatures"),
    ("b", "ethics"): ("x", "practice"),
    ("b", "death"): ("x", "spirit"),
    ("b", "places"): ("x", "fengshui"),
    ("b", "history"): ("x", "history"),
    ("b", "practice"): ("x", "practice"),
}

HOOKS = {
    "b1": [("b", "buddha"), ("M", "b")],
    "b2": [("b", "truths")],
    "b4": [("b", "emptiness")],
    "b5": [("b", "sutras")],
    "b7": [("b", "mantras")],
    "x1": [("x", "wuxing"), ("M", "x")],
    "x2": [("x", "creatures")],
    "x3": [("x", "bagua")],
    "x4": [("x", "writing")],
    "x6": [("x", "yijing")],
}

# ---------------------------------------------------------------- montagem

cards = {}
order = []
sec_of_group = {"x": myst, "b": bud}
manual_idx = {"x": "M_x", "b": "M_b"}
MANUAL = {
    "x": ("The Dark and the Five", "chineseMysticismManual.html"),
    "b": ("The Sound of Emptiness", "buddhismManual.html"),
}

for g in ("x", "b"):
    for s in sec_of_group[g]:
        sid_card = "S_%s_%s" % (g, s["id"])
        units = list(s["units"])
        lead = None
        if units and units[0][0] == "prose":
            lead = units.pop(0)
        x0 = lead[2] if lead else (units[0][2] if units else "The manual opens a door here.")
        s["idx"] = sid_card
        cards[sid_card] = dict(
            w="%s · %s" % ("佛" if g == "b" else "玄", wlabel(s["title"])),
            g=s["glyph"], t=s["title"], x=x0,
            s="%s#%s" % (MANUAL[g][1], s["id"]),
            n="%s — %s" % (MANUAL[g][0], s["title"]), c=[])

        ids, seen_titles = [], {}
        for i, u in enumerate(units):
            uid = "u_%s_%s_%d" % (g, s["id"], i)
            title = u[1]
            if title in seen_titles:
                seen_titles[title] += 1
                title = "%s (%d)" % (title, seen_titles[title] + 1)
            else:
                seen_titles[title] = 0
            cards[uid] = dict(
                w=cards[sid_card]["w"], g=(u[4] if u[0] == "item" else s["glyph"]),
                t=title, x=u[2], s=cards[sid_card]["s"], n=cards[sid_card]["n"], c=[])
            ids.append(uid)
        order.append((g, s, sid_card, ids))

def short(t, limit=62):
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "…"

for g, s, sid_card, ids in order:
    other = CROSS.get((g, s["id"]))
    cross_card = "S_%s_%s" % (other[0], other[1])
    if cross_card not in cards:
        cross_card = manual_idx[other[0]]
    for i, uid in enumerate(ids):
        nxt = ids[(i + 1) % len(ids)]
        cards[uid]["c"] = [
            ["→ " + short(cards[nxt]["t"]), nxt],
            ["⇄ " + short(cards[cross_card]["t"], 48), cross_card],
            ["↩ " + short(s["title"], 44), sid_card],
        ]
    same = [(gg, ss, sc, ii) for (gg, ss, sc, ii) in order if gg == g]
    pos = [x[2] for x in same].index(sid_card)
    nxt_sec = same[(pos + 1) % len(same)]
    cards[sid_card]["c"] = [
        ["→ " + short(cards[ids[0]]["t"]) if ids else "→ Go on", ids[0] if ids else manual_idx[g]],
        ["→ Next section: " + short(nxt_sec[1]["title"], 32), nxt_sec[2]],
        ["← Manual index", manual_idx[g]],
    ]

cards["M_x"] = dict(
    w="玄 · The manual", g="玄", t="The Dark and the Five",
    x="Twenty sections: the way, the five phases, the eight trigrams, the sixty-four, "
      "number, qi, the dark, sound, characters, creatures, landscape, the elixir and "
      "history. Every page of the manual is a card; every card opens two or three ways on.",
    s="chineseMysticismManual.html", n="The Dark and the Five — the whole manual",
    c=[["→ " + short(cards["S_x_scope"]["t"]), "S_x_scope"],
       ["⇄ The Buddhist manual", "M_b"],
       ["← Back to the gate", "start"]])
cards["M_b"] = dict(
    w="佛 · The manual", g="佛", t="The Sound of Emptiness",
    x="Twenty sections: the Buddha, the four truths, the twelve links, the precepts, the "
      "canon, the schools, emptiness, meditation, the thirteen mantras, the twenty-two "
      "sutras, chanting, symbols, ethics, death and places. Every page is a card.",
    s="buddhismManual.html", n="The Sound of Emptiness — the whole manual",
    c=[["→ " + short(cards["S_b_scope"]["t"]), "S_b_scope"],
       ["⇄ The Chinese manual", "M_x"],
       ["← Back to the gate", "start"]])

print("secções: %d + %d" % (len(myst), len(bud)))
print("cartões totais gerados: %d" % len(cards))
per = {s["id"]: len(ids) for g, s, sid_card, ids in order}
print("por secção:", ", ".join("%s=%d" % (k, v) for k, v in per.items()))

if "--dump" in sys.argv:
    for uid, c in cards.items():
        print("%s\t%s\t%s" % (uid, c["t"], c["x"]))

if "--sample" in sys.argv:
    for g, s, sid_card, ids in order:
        print("\n## [%s] %s · %s (%d)" % (g, s["han"], s["title"], len(ids)))
        for uid in [sid_card] + ids[:3]:
            c = cards[uid]
            print("   %-24s %s | %s" % (uid, c["t"], c["x"][:110]))
            for pair in c["c"]:
                print("        %-58s -> %s" % (pair[0], pair[1]))

if "--write" in sys.argv:
    game = read(GAME)
    marker = "        };\n\n        var panel = document.getElementById"
    assert game.count(marker) == 1, "marcador do fim de NODES não é único"

    lines = []
    for uid, c in cards.items():
        lines.append("")
        lines.append("          %s: {" % json.dumps(uid, ensure_ascii=False))
        lines.append("            w: %s, g: %s, t: %s," % (
            json.dumps(c["w"], ensure_ascii=False), json.dumps(c["g"], ensure_ascii=False),
            json.dumps(c["t"], ensure_ascii=False)))
        lines.append("            x: %s," % json.dumps(c["x"], ensure_ascii=False))
        lines.append("            s: %s, n: %s," % (
            json.dumps(c["s"], ensure_ascii=False), json.dumps(c["n"], ensure_ascii=False)))
        lines.append("            c: [%s]" % ", ".join(
            "[%s, %s]" % (json.dumps(p[0], ensure_ascii=False), json.dumps(p[1], ensure_ascii=False))
            for p in c["c"]))
        lines.append("          },")
    block = "\n".join(lines)

    by_node = {}
    for node, targets in HOOKS.items():
        for kind, key in targets:
            if kind == "M":
                card = manual_idx[key]
                label = "↪ Open the manual (%s)" % MANUAL[key][0]
            else:
                card = "S_%s_%s" % (kind, key)
                label = "↪ " + short(cards[card]["t"], 44)
            by_node.setdefault(node, []).append((label, card))

    extra = "\n        var MANUAL_EXTRA = {\n"
    for node, pairs in by_node.items():
        extra += "          %s: [%s],\n" % (node, ", ".join(
            "[%s, %s]" % (json.dumps(l, ensure_ascii=False), json.dumps(c, ensure_ascii=False))
            for l, c in pairs))
    extra += "        };\n"
    extra += "        for (var _k in MANUAL_EXTRA) { if (NODES[_k]) { NODES[_k].c = NODES[_k].c.concat(MANUAL_EXTRA[_k]); } }\n"

    at = game.index(marker)
    prev = game[:at].rstrip()[-1:]
    lead_comma = "" if prev == "," else ","
    game = game[:at] + lead_comma + block + "\n        };\n" + extra + "\n        var panel = document.getElementById" + game[at + len(marker):]
    game = game.replace('var randomTargets = ["t1", "b1", "x1", "e1", "e2", "d1", "b7"];',
                        'var randomTargets = ["t1", "b1", "x1", "e1", "e2", "d1", "b7", "M_x", "M_b", "S_x_yijing", "S_b_mantras", "S_b_sutras"];')
    open(GAME, "w", encoding="utf-8").write(game)
    print("escrito em", GAME)
