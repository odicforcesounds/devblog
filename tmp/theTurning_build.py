# -*- coding: utf-8 -*-
# Build script for theTurning.html (English twin of aViragem.html).
# All CJK chars written as explicit Unicode so nothing can be corrupted by encoding.

import io
import re

MID = "\u00b7"      # middle dot
EMD = "\u2014"      # em dash

def hz(*codes):
    return "".join(chr(int(c, 16)) for c in codes)

HE    = hz("5408")    # he: the crossing label
MING  = hz("51aa")    # ming: the dark
YUE   = hz("6a02")    # yue: music
QI    = hz("6c23")    # qi
SHEN  = hz("8eab")    # shen: body
ZHUAN = hz("8f49")    # zhuan: turning
HUN   = hz("9b42")    # hun
YIN2  = hz("5370")    # yin: seal
BA    = hz("516b")    # ba: eight
ZUO   = hz("5750")    # zuo: sit

DARK2     = hz("7384", "4e4b", "53c8", "7384", "ff0c", "773e", "5999", "4e4b", "9580")  # xuan zhi you xuan, zhong miao zhi men
TONES     = hz("5bae", "5546", "89d2", "5fb5", "7fbd")                                  # gong shang jue zhi yu
BIGSOUND  = hz("5927", "97f3", "5e0c", "8072")                                          # biggest sound is barely heard
JINGZUO   = hz("9759", "5750")                                                          # sitting in silence
XINGMING  = hz("6027", "547d")                                                          # xing ming: nature and life
NEIDAN    = hz("5167", "4e39")                                                          # inner alchemy
ZHUANS    = hz("8f49")                                                                  # zhuan
SEALSCR   = hz("7bc6", "66f8")                                                          # seal script
ZHANZ     = hz("7ad9", "6a81")                                                          # standing post
WUWEI     = hz("7121", "70ba")                                                          # wu wei

TT = "docs/theTurning.html"
AV = "docs/aViragem.html"

s = io.open(TT, encoding="utf-8").read()
orig = s

# ---------------------------------------------------------------- NODES -----
def node_def(nid, glyph, title, body, srcfile, srctitle, choices):
    lines = []
    lines.append('          %s: {' % nid)
    lines.append('            w: "%s %s The crossing", g: "%s", t: "%s",' % (HE, MID, glyph, title))
    lines.append('            x: "%s",' % body)
    lines.append('            s: "%s", n: "%s",' % (srcfile, srctitle))
    ch = ", ".join('["%s", "%s"]' % (lbl, tgt) for lbl, tgt in choices)
    lines.append('            c: [%s]' % ch)
    lines.append('          },')
    return "\n".join(lines)

nodes = "\n\n".join([
    node_def("c1", MING, "Emptiness and the dark",
        "Two traditions arrived at the same door by different roads. The Heart Sutra negates birth and destruction to break the imaginary solidity of things: emptiness does not say nothing exists, it says nothing exists from its own side. The Taoist folding of the dark " + DARK2 + " is not the absence of light, and not evil either: it is the undivided, the state before a figure is cut from the ground, the colour of a depth you cannot see the bottom of.",
        "chineseMysticismManual.html", "The Dark and the Five " + EMD + " " + hz("7384"),
        [["Back to the emptiness of the Heart Sutra", "b4"], ["Back into the dark", "d1"], ["On to the sound", "c2"]]),
    node_def("c2", YUE, "The wooden fish and the twelve pipes",
        "In both traditions the sound is the teaching itself. In the temple the wooden fish keeps the beat, the great bell is struck 108 times for the 108 afflictions, and the tantric bell rings emptiness. At the Chinese court the five tones " + TONES + " match the five phases, and the twelve pitch-pipes give the year its calendar: lose the tuning, lose the mandate. Both arrive at the same sobriety: " + BIGSOUND + ", the greatest sound is barely heard.",
        "chineseMysticismManual.html", "The Dark and the Five " + EMD + " " + hz("97f3"),
        [["Back to the chant", "b10"], ["Back to the five phases", "x1"], ["Follow the breath", "c3"]]),
    node_def("c3", QI, "Sixteen steps, four and six",
        "Breath is the smallest practice of both houses. The Anapanasati Sutta gives sixteen steps on the breath alone, from knowing a long breath to contemplating impermanence. The Chinese manual asks for less, in the same coin: " + JINGZUO + ", sitting in silence, inhale four, exhale six, without forcing; when the mind wanders, note it and come back. That return is the practice. And qi covers all scales of it: steam rising from rice, not a substance but a family of processes, time, air, vitality, the temper of an age.",
        "buddhismManual.html", "The Sound of Emptiness " + EMD + " meditation",
        [["Sit with him", "b3"], ["See the body as the cauldron", "c4"], ["Back to water that does not force", "t2"]]),
    node_def("c4", SHEN, "Boat and cauldron",
        "Both traditions give the body the same office. On the night of waking the body is not the enemy: it is the boat, and the memory of calm under a tree teaches it better than austerities. In inner alchemy it is more instrumental still: the body is the cauldron, the breath the bellows, and the three treasures, jing, qi and shen, the ingredients refined in the orbit that rises up the back and down the front. The pair of " + XINGMING + ", nature and life, ends the talk: to train only the nature is blind, to train only the life is empty.",
        "chineseMysticismManual.html", "The Dark and the Five " + EMD + " " + NEIDAN,
        [["Cook the elixir", "d3"], ["Back under the tree", "b3"], ["Feel the wheel turn", "c5"]]),
    node_def("c5", ZHUANS, "Everything turns, and the seed travels",
        "The three marks of Buddhism reduce to one: impermanence, all that is conditioned changes, and the wheel of the six realms is that turning drawn, with the three poisons biting each other at the centre. Yin and yang say the same in another grammar: at the extreme each becomes the other, noon turns to evening, and each fish of the diagram carries a point of its opposite, the seed of the other phase at its heart. The name of this game comes from there: " + ZHUANS + " describes no destination, only a turning.",
        "buddhismManual.html", "The Sound of Emptiness " + EMD + " dependent arising",
        [["Ask what crosses over", "c6"], ["Back to karma and the Monkeys", "b8"], ["Cast the sixty-four", "x6"]]),
    node_def("c6", HUN, "What crosses over death",
        "Neither tradition carries a soul with a passport. China splits the person in two: " + HUN + ", yang and light, leaves with the breath and must be called or guided by ritual, a lingering hun becomes a ghost; the po, yin, stays with the body and the grave. Buddhism compares rebirth to a flame passing to another flame: nothing material travels, and yet the next flame is not a stranger. The Tibetan bards give the intermediate state forty-nine days, read aloud to its occupant; what continues is a causal pattern, not a passenger.",
        "buddhismManual.html", "The Sound of Emptiness " + EMD + " death",
        [["Turn the light back inward", "d2"], ["Sit in the silence", "b11"], ["Return to emptiness", "b4"]]),
    node_def("c7", YIN2, "Symbols read without knowing how to read",
        "Art in both is a technology of memory. The Buddhist compressed the teaching into the eight auspicious symbols, lotus and wheel and endless knot, into the mudra of the hand, and into a stupa whose parts code the five elements. The Chinese cut patterns into oracle bones, ordered the characters into six scripts, and still signs today with the seal script, " + SEALSCR + ". Both give the same warning: distrust the pretty readings, only the oldest attested form counts.",
        "buddhismManual.html", "The Sound of Emptiness " + EMD + " the wheel",
        [["Back to the character", "x4"], ["Read the wheel in the parables", "b9"], ["Back to the gate", "start"]]),
    node_def("c8", BA, "Two wheels of eight",
        "The eightfold path is not a ladder: it is a spiral grouped in three trainings, ethics, stillness and wisdom, from right view to right concentration. The eight trigrams are not a list either: heaven and earth, thunder and wind, water and fire, mountain and lake pair up into the sixty-four situations of the Yijing. Eight factors keep life from turning blind; eight trigrams let it turn with a name. In both wheels, eight is the number that describes everything without exhausting anything.",
        "chineseMysticismManual.html", "The Dark and the Five " + EMD + " " + hz("516b") + hz("5366"),
        [["Rebuild the Buddha diagnosis", "b2"], ["Back to tiger and dragon", "x2"], ["Sit at the end of the lists", "c9"]]),
    node_def("c9", ZUO, "Both manuals end in the same ten minutes",
        "Both manuals close with twelve sober weeks. The Buddhist one: a chapter of the Dhammapada a day, metta for friend and for difficult person, a mantra recited 108 times. The Chinese one: a chapter of the Daodejing aloud, one character a day, sit ten minutes, stand five, " + ZHANZ + ", and once a week do nothing for twenty, " + WUWEI + ", which the modern world calls unbearable. It is the only scale that survives a working day, and the game keeps it: one page, one choice, another page.",
        "buddhismManual.html", "The Sound of Emptiness " + EMD + " practice",
        [["Back to the first gate", "start"], ["Back to the way", "t1"], ["Stay in the silence", "b11"]]),
])

old_close = '            c: [["Return to the road", "t1"], ["Sit in the silence", "b11"]]\n          }\n        };'
assert old_close in s, "e7 close anchor not found"
new_close = '            c: [["Return to the road", "t1"], ["Sit in the silence", "b11"]]\n          },\n\n' + nodes + '\n        };'
s = s.replace(old_close, new_close, 1)

# ---------------------------------------------------------------- WIRES -----
wires = [
    ('c: [["Ask what emptiness means", "b4"], ["Open the sutras", "b5"]]',
     'c: [["Ask what emptiness means", "b4"], ["Open the sutras", "b5"], ["Weigh the eight factors against the trigrams", "c8"]]'),
    ('c: [["Ask the koan of one hand", "b6"], ["Listen to the chant", "b10"]]',
     'c: [["Ask the koan of one hand", "b6"], ["Listen to the chant", "b10"], ["Follow the breath step by step", "c3"]]'),
    ('c: [["Take the mantra gate gate", "b7"], ["Ask about buddha-nature", "b8"]]',
     'c: [["Take the mantra gate gate", "b7"], ["Ask about buddha-nature", "b8"], ["Open the door of the dark", "c1"]]'),
    ('c: [["Meet the Monkeys l of Asia", "e2"], ["Return to emptiness", "b8"]]',
     None),
    ('c: [["Meet the Monkeys of Asia", "e2"], ["Return to emptiness", "b4"]]',
     'c: [["Meet the Monkeys of Asia", "e2"], ["Return to emptiness", "b4"], ["Watch the wheel turn", "c5"]]'),
    ('c: [["Look for the jewel in yourself", "b8"], ["Step into the silence", "b11"]]',
     'c: [["Look for the jewel in yourself", "b8"], ["Step into the silence", "b11"], ["Read the symbols without reading", "c7"]]'),
    ('c: [["Follow the five tones into the phases", "x1"], ["Let the sound end", "b11"], ["Ask what cultures share", "e6"]]',
     'c: [["Follow the five tones into the phases", "x1"], ["Let the sound end", "b11"], ["Ask what cultures share", "e6"], ["Rise to tone and pitch-pipe", "c2"]]'),
    ('c: [["Return to the gate", "start"], ["Go into the dark", "d1"], ["Ask what a religion is", "e7"]]',
     'c: [["Return to the gate", "start"], ["Go into the dark", "d1"], ["Ask what a religion is", "e7"], ["Ask what crosses over", "c6"]]'),
    ('c: [["Sit in the valley", "t4"], ["Turn the light around", "d2"]]',
     'c: [["Sit in the valley", "t4"], ["Turn the light around", "d2"], ["Let the dark become emptiness", "c1"]]'),
    ('c: [["Return to the way", "t1"], ["Return to the gate", "start"]]',
     'c: [["Return to the way", "t1"], ["Return to the gate", "start"], ["See the body as the boat", "c4"]]'),
    ('c: [["Sit in the valley", "t4"], ["Climb to the five phases", "x1"]]',
     'c: [["Sit in the valley", "t4"], ["Climb to the five phases", "x1"], ["Breathe without forcing", "c3"]]'),
    ('c: [["Cast the sixty-four", "x6"], ["Turn toward the dark", "d1"]]',
     'c: [["Cast the sixty-four", "x6"], ["Turn toward the dark", "d1"], ["Eight factors beside the trigrams", "c8"]]'),
    ('c: [["Return to the way", "t1"], ["Step into the dream", "e1"]]',
     'c: [["Return to the way", "t1"], ["Step into the dream", "e1"], ["Open the seals and the wheel", "c7"]]'),
    ('c: [["Read the characters", "x4"], ["Enter the dream", "e1"]]',
     'c: [["Read the characters", "x4"], ["Enter the dream", "e1"], ["Ten minutes at the end of the lists", "c9"]]'),
]

for old, new in wires:
    if new is None:
        continue
    assert old in s, "wire anchor missing: " + old[:60]
    s = s.replace(old, new, 1)

# ------------------------------------------------------- LEGEND + CARDS -----
# extract node fields for the compendium cards
cards = {}
for nid in ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9"]:
    mm = re.search(r'\n          ' + nid + r': \{\n(.+?)\n          \}', s, re.S)
    assert mm, "node missing: " + nid
    block = mm.group(1)
    gt = re.search(r't: "(.+)",\n', block)
    gx = re.search(r'x: "(.+)",\n', block)
    cards[nid] = (gt.group(1), gx.group(1))

labels = {
    "c1": ("Buddhism " + EMD + " emptiness", "Mysticism " + EMD + " the dark"),
    "c2": ("Buddhism " + EMD + " the chant", "Mysticism " + EMD + " the five tones"),
    "c3": ("Buddhism " + EMD + " the breath", "Mysticism " + EMD + " qi"),
    "c4": ("Buddhism " + EMD + " the night", "Mysticism " + EMD + " inner alchemy"),
    "c5": ("Buddhism " + EMD + " the marks", "Mysticism " + EMD + " yin and yang"),
    "c6": ("Buddhism " + EMD + " death", "Mysticism " + EMD + " hun and po"),
    "c7": ("Buddhism " + EMD + " the symbols", "Mysticism " + EMD + " the characters"),
    "c8": ("Buddhism " + EMD + " the path", "Mysticism " + EMD + " the trigrams"),
    "c9": ("Buddhism " + EMD + " practice", "Mysticism " + EMD + " practice"),
}
anchors = {
    "c1": ("#emptiness", "#dark"),
    "c2": ("#sound", "#sound"),
    "c3": ("#meditation", "#qi"),
    "c4": ("#emptiness", "#alchemy"),
    "c5": ("#marks", "#yinyang"),
    "c6": ("#death", "#spirit"),
    "c7": ("#relics", "#writing"),
    "c8": ("#truths", "#bagua"),
    "c9": ("#practice", "#practice"),
}
gl = {nid: n for nid, n in [
    ("c1", MING), ("c2", YUE), ("c3", QI), ("c4", SHEN), ("c5", ZHUANS),
    ("c6", HUN), ("c7", YIN2), ("c8", BA), ("c9", ZUO),
]}

cards_html = "\n\n".join(
    '        <article class="cross-card">\n'
    '          <span class="cross-han" aria-hidden="true">%s</span>\n'
    '          <h3>%s</h3>\n'
    '          <p>%s</p>\n'
    '          <p class="cross-src">Mysticism — <a href="./chineseMysticismManual.html%s">The Dark and the Five</a> · Buddhism — <a href="./buddhismManual.html%s">The Sound of Emptiness</a></p>\n'
    '        </article>'
    % (gl[nid], cards[nid][0], cards[nid][1], anchors[nid][1], anchors[nid][0])
    for nid in ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9"]
)

section = (
    '    <section class="cruzamentos">\n'
    '      <div class="cross-head">\n'
    '        <span class="cross-han" aria-hidden="true">' + HE + '</span>\n'
    '        <h2>The crossing of the manuals</h2>\n'
    '      </div>\n'
    '      <p class="cross-sub">Nine points where the Buddhist and the Taoist paths touch the same ground. In the game, they are the pages that tell where the turning story lets both manuals meet.</p>\n'
    + cards_html + '\n'
    '    </section>\n'
)

old_legend_tail = '        <div><a href="./asianMonkey.html">Monkeys in Asia</a> · <a href="./ArtOfCreation.html">Mind Resolution</a> · <a href="./religions.html">What Religions Are</a> · <a href="./CommonCultures.html">One Human Song</a> · <a href="./DragonFire.html">Dragon Fire</a></div>'
assert old_legend_tail in s, "legend anchor not found"
s = s.replace(
    old_legend_tail,
    '        <div><a href="./buddhismManual.html">Buddhism</a> · <a href="./chineseMysticismManual.html">Chinese Mysticism</a></div>\n' + old_legend_tail,
    1
)
old_legend_close = '      </div>\n    </main>\n'
assert old_legend_close in s, "legend close anchor not found"
s = s.replace(old_legend_close, '      </div>\n' + section + '    </main>\n', 1)

# ----------------------------------------------------------------- CSS ------
css_add = (
    '\n    /* --- .cruzamentos: shared-panel style for the new static section --- */\n'
    '    .cruzamentos { max-width: 760px; margin: 3rem auto 0; padding: 0 1rem; }\n'
    '    .cross-head { display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.25rem; }\n'
    '    .cross-head .cross-han { font-size: 2rem; }\n'
    '    .cross-head h2 { font-size: 1.5rem; margin: 0; }\n'
    '    .cross-sub { text-align: center; margin: 0.25rem 0 1.5rem; }\n'
    '    .cross-card { border: 1px solid #444; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1rem; }\n'
    '    .cross-card .cross-han { float: left; font-size: 1.6rem; margin-right: 0.6rem; line-height: 1; }\n'
    '    .cross-card h3 { font-size: 1.15rem; margin: 0.25rem 0 0.5rem; }\n'
    '    .cross-card .cross-src { font-size: 0.85rem; margin: 0.5rem 0 0; }\n'
)
assert '  </style>' in s
s = s.replace('  </style>', css_add + '\n  </style>', 1)

io.open(TT, "w", encoding="utf-8").write(s)

# ------------------------------------------ FIX corrupted glyph in aViragem --
av = io.open(AV, encoding="utf-8").read()
n_before = av.count("\u51ab")
assert n_before == 2, "expected exactly 2 corrupted ice-radical glyphs, found %d" % n_before
av = av.replace("\u51ab", MING)
io.open(AV, "w", encoding="utf-8").write(av)

print("theTurning nodes: OK; cards: OK; wires: OK; aViragem fix: %d glyphs" % n_before)
