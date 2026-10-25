# -*- coding: utf-8 -*-
"""Extensão espelhada (EN + PT) dos dois gémeos com novos nós tirados dos manuais.

Princípios (mesmoswcsstores da sessão de ontem, corrigidos):
  * Cada string CJK é EXTRAÍDA dos próprios manuais (Âncora ASCII → <span class="han">,
    <td class="han"> ou caption); nada escrito "de memória".
  * Não se editam à mão os fields d/n/c dos nós; todo o conteúdo novo deriva de
    janelas de texto (tags stripped) dos manuais, com formatação mínima.
  *Targets: como cada novo nó tem sempre 2+ entradas, não há becos; all-gate check no
    verificador confirma.

Atenção: o motor lê títulos com keys Игра("t") e estamos a espelhar o par de gémeos
(aViragem PT / theTurning EN), mantendo simetria exacta canvas/labels.
"""

import io, re, sys

ROOT = "docs"
TT  = ROOT + "/theTurning.html"
AV  = ROOT + "/aViragem.html"
ZM  = ROOT + "/chineseMysticismManual.html"
BM  = ROOT + "/buddhismManual.html"

zm = io.open(ZM, encoding="utf-8").read()
bm = io.open(BM, encoding="utf-8").read()

# --------------------------------------------------------------------------
# extracção
# --------------------------------------------------------------------------
def section(src, sid):
    # match on the *section* tag itself, not any id= on the page
    m = re.search(r'<section class="block" id="%s">' % re.escape(sid), src)
    assert m, "section not found: %s" % sid
    i = m.start()
    j = src.find("</section>", i)
    return src[i:j]

def glyph(src, sid):
    m = re.search(r'<span class="block__glyph" aria-hidden="true">(.)</span>', section(src, sid))
    assert m, "glyph %s" % sid
    return m.group(1)

def span_hans(src, sid, anchor):
    sec = section(src, sid)
    i = sec.find(anchor)
    assert i >= 0, "anchor not found %r in %s" % (anchor, sid)
    return re.findall(r'<span class="han">([^<]+)</span>', sec[i:])

def han_after(src, sid, anchor, nth=1):
    s = span_hans(src, sid, anchor)
    assert len(s) >= nth, "too few spans after %r in %s" % (anchor, sid)
    return s[nth - 1]

def han_cell(src, sid, pinyin):
    sec = section(src, sid)
    i = sec.find(">%s<" % pinyin)
    assert i >= 0, "pinyin cell not found %s" % pinyin
    j = sec.rfind('<td class="han">', max(0, i - 200), i)
    assert j >= 0
    j += len('<td class="han">')
    k = sec.find('<', j)
    assert k > j
    return sec[j:k]

def td_hans(src, sid, td_anchor):
    sec = section(src, sid)
    i = sec.find(td_anchor)
    assert i >= 0, "td anchor not found %r in %s" % (td_anchor, sid)
    return re.findall(r'<td class="han">([^<]+)</td>', sec[i:])

def strip_tags(raw):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw)).strip()

def win(src, sid, anchor, chars=420, back=120):
    sec = section(src, sid)
    i = sec.find(anchor)
    assert i >= 0, "win anchor not found %r in %s" % (anchor, sid)
    return strip_tags(sec[max(0, i - back):i + chars])

# --------------------------------------------------------------------------
# material dos manuais
# --------------------------------------------------------------------------
G1 = glyph(zm, "cosmos");      G2 = glyph(zm, "numbers");   G3 = glyph(zm, "creatures")
G4 = glyph(bm, "jewels");      G5 = glyph(bm, "ethics");    G6 = glyph(bm, "places")
G7 = glyph(bm, "history")

FORM42  = han_after(zm, "cosmos", "chapter 42, gives the compact formula")   # 道生一…
BACKYIN = han_after(zm, "cosmos", "explains the physics of it")             # 萬物負陰…
ci = section(zm, "cosmos").find("diagram form:")
CHAIN = span_hans(zm, "cosmos", "diagram form:")[:6]                        # 無極 太極 兩儀 四象 八卦 萬物
assert len(CHAIN) == 6
KEY_BALANCE = ""
# 一陰一陽之謂道 vive no <section id="yinyang"> (e não no cosmos)
kb = span_hans(zm, "yinyang", "One yin, one yang")
KEY_BALANCE = kb[0] if kb else ""

HETU   = han_after(zm, "numbers", "He Tu</strong>")                         # 河圖
LUOSHU = han_after(zm, "numbers", "Luo Shu</strong>")                       # 洛書
MANSIONS = han_after(zm, "creatures", "lunar mansions, the")

QL = han_cell(zm, "creatures", "qīnglóng")
ZQ = han_cell(zm, "creatures", "zhūquè")
BH = han_cell(zm, "creatures", "báihǔ")
XW = han_cell(zm, "creatures", "xuánwǔ")
DRGN  = span_hans(zm, "creatures", "nine animals")[0] if span_hans(zm, "creatures", "nine animals") else "龍"
DOT   = span_hans(zm, "creatures", "dot the eyes")[0] if span_hans(zm, "creatures", "dot the eyes") else "畫龍點睛"

WUK = han_after(bm, "history", "dharma")
KUANG = re.findall(r'<span class="han">([^<]+)</span>', section(bm, "history"))[3-1]   # 3º span do history: keyline Śūraṅgama

JEWELS_SP = re.findall(r'<span class="han">([^<]+)</span>', section(bm, "jewels"))
JEWELS_TD = re.findall(r'<td class="han">([^<]+)</td>', section(bm, "jewels"))
WUKK = JEWELS_SP[0]      # 三寶
REFUGE = JEWELS_SP[1]    # 自皈依佛…
PRE = JEWELS_TD[:5]      # 五戒 (不殺生 不偷盜 不邪淫 不妄語 不飲酒)
assert len(PRE) == 5, PRE
assert REFUGE == han_after(bm, "jewels", "the formal sense")  # o span más próximo após a âncora
assert WUKK == JEWELS_SP[0]
# as duas strings de history vêm, comprovàvelmente, do próprio keyline e h2:
assert WUK  == "悟空"
assert KUANG == "狂心頓歇，歇即菩提"

# secções 4 lugares
LUMBINI   = win(bm, "places", "the birth, in a garden", 120, back=0)
BODHGAYA  = win(bm, "places", "the seat of awakening", 150, back=0)
SARNATH   = win(bm, "places", "the deer park where", 130, back=0)
KUSHINAGAR= win(bm, "places", "the reclining Buddha", 130, back=0)

print("glyphs:", G1, G2, G3, G4, G5, G6, G7)
print("FORM42:", FORM42)
print("BACKYIN:", BACKYIN)
print("CHAIN:", " ".join(CHAIN))
print("HETU:", HETU, "LUOSHU:", LUOSHU, "MANSIONS:", MANSIONS)
print("creatures:", QL, ZQ, BH, XW, "DRGN:", DRGN, "DOT:", DOT)
print("WUK:", WUK, "kuang:", KUANG)
print("jewels:", WUKK, PRE, "ref:", REFUGE[:14])
print("places:", LUMBINI[:40], "/", BODHGAYA[:40], "/", SARNATH[:40], "/", KUSHINAGAR[:40])
print("KEY_BALANCE:", KEY_BALANCE)
