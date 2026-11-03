import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import json, re, collections

s = open("docs/pythonCert.html", encoding="utf-8").read()
pt_start = s.index('<div id="lang-pt" data-lang-block="pt" hidden>')
pt_end = s.index("</div>\n\n<script>", pt_start)
pt = s[pt_start:pt_end]
en = s[s.index('<div id="lang-en" data-lang-block="en">'):pt_start]

print("h1 in document:", len(re.findall(r"<h1\b", s)))
print("h1 in EN block:", len(re.findall(r"<h1\b", en)), "| h1 in PT block:", len(re.findall(r"<h1\b", pt)))
print("PT title element:", re.findall(r'<h[12] class="title"', pt))
print("scoped title CSS:", "#lang-pt h2.title" in s)

ids = re.findall(r'\bid="([^"]+)"', s)
dups = {k: v for k, v in collections.Counter(ids).items() if v > 1}
print("duplicate ids:", dups or "none")

switches = re.findall(r'data-lang-switch="(\w+)"', s)
print("switch links:", collections.Counter(switches), "| blocks:", re.findall(r'data-lang-block="(\w+)"', s))
print("switch nav before both blocks:", s.index('class="lang-switch"') < s.index('<div id="lang-en"'))

units = {}
for line in open("tmp/pythonCert.units2.json", encoding="utf-8"):
    if line.strip():
        u = json.loads(line)
        units[u["id"]] = u
m = json.load(open("tmp/pythonCert.pt.json", encoding="utf-8"))
ident = [k for k, v in m.items() if k in units and units[k]["html"] == v]
print("translations supplied:", len(m), "| identity (same word in both languages):", len(ident))

left = []
for tag, body in re.findall(r"<(p|li|h2|h3|h4|td|th|dd|dt|caption)\b[^>]*>([\s\S]*?)</\1>", pt):
    if 'target="_blank"' in body or 'class="src"' in body:
        continue
    txt = re.sub(r"<[^>]+>", " ", body)
    words = txt.split()
    if len(words) >= 6 and re.search(r"\b(the|and|with|this|that|from|your)\b", txt) and not re.search(r"\b(de|para|que|com|uma|não|é|os|as|do|da)\b", txt):
        left.append((tag, " ".join(words)[:70]))
print("English-looking prose left in PT block:", len(left))
for t in left[:8]:
    print("   -", t[0], "|", t[1])

# required Portuguese markers, one per level
markers = ["Do zero ao herói", "O que o Python é de facto", "Configuração pós-instalação", "venv, PEP 668",
           "Essenciais da linguagem", "Comandos e opções", "biblioteca padrão, organizada",
           "Segurança: os padrões", "Testes e qualidade", "Bibliotecas por objectivo",
           "Empacotamento e dependências", "Más decisões", "Desempenho e depuração",
           "Operações: correr Python", "Manutenção a longo prazo", "Avaliação final"]
missing = [x for x in markers if x not in pt]
print("level markers present:", f"{len(markers) - len(missing)}/{len(markers)}", "missing:", missing)
print("gate notes in PT:", pt.count("Verificação de conhecimentos"), "| scripts in PT:", pt.count("<script"))
print("size: EN", len(en), "chars | PT", len(pt), "chars")
