# -*- coding: utf-8 -*-
import re, sys, html

def load(p):
    return open(p, encoding="utf-8").read()

def strip(s):
    s = re.sub(r"<span class=\"pinyin\">(.*?)</span>", r"(\1)", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def sections(src):
    out = []
    for m in re.finditer(r'<section class="block" id="([^"]+)"', src):
        out.append((m.group(1), m.start()))
    return out

def sec_of(sections, pos):
    cur = "?"
    for sid, start in sections:
        if start <= pos:
            cur = sid
        else:
            break
    return cur

for path in ["docs/manualDaMisticaChinesa.html", "docs/manualDoBudismo.html"]:
    src = load(path)
    secs = sections(src)
    print("#" * 70)
    print(path)
    i = 0
    for m in re.finditer(r"<table[^>]*>(.*?)</table>", src, re.S):
        body = m.group(1)
        cap = re.search(r"<caption>(.*?)</caption>", body, re.S)
        cap = strip(cap.group(1)) if cap else "(sem caption)"
        rows = re.findall(r"<tr>(.*?)</tr>", body, re.S)
        i += 1
        print("\n[%d] sec=%s | %s | rows=%d" % (i, sec_of(secs, m.start()), cap, len(rows)))
        for r in rows[:2]:
            cells = [strip(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
            print("     ", " | ".join(cells)[:220])
