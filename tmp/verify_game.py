# -*- coding: utf-8 -*-
"""Verifica o grafo de docs/aViragem.html: sintaxe, destinos, alcance, 2–3 saídas."""
import json, re, subprocess, sys, collections

GAME = sys.argv[1] if len(sys.argv) > 1 else "docs/aViragem.html"
src = open(GAME, encoding="utf-8").read()

# 1) script inteiro -> node --check
script = re.search(r"<script[^>]*>(.*?)</script>", src, re.S).group(1)
open("/tmp/game_check.js", "w", encoding="utf-8").write(script)
r = subprocess.run(["node", "--check", "/tmp/game_check.js"], capture_output=True, text=True)
print("node --check:", "OK" if r.returncode == 0 else "FALHOU\n" + r.stderr)

# 2) extrair o objecto NODES (chavetas fora de strings)
start = src.index("var NODES = {")
i = src.index("{", start)
depth, instr, esc, end = 0, None, False, None
for j in range(i, len(src)):
    ch = src[j]
    if instr:
        if esc:
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == instr:
            instr = None
    else:
        if ch in "\"'":
            instr = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                break
obj = src[i:end]
open("/tmp/nodes.js", "w", encoding="utf-8").write("module.exports = " + obj + ";")
r = subprocess.run(["node", "-e", "console.log(JSON.stringify(require('/tmp/nodes.js')))"],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr)
    sys.exit(1)
# os hooks são aplicados em runtime
r2 = subprocess.run(["node", "-e", """
const N = require('/tmp/nodes.js');
const s = require('fs').readFileSync('/tmp/game_check.js','utf8');
const m = s.match(/var MANUAL_EXTRA = \\{([\\s\\S]*?)\\n        \\};/);
const obj = eval('({' + m[1] + '})');
for (const k in obj) { if (N[k]) N[k].c = N[k].c.concat(obj[k]); }
console.log(JSON.stringify(N));
"""], capture_output=True, text=True)
if r2.returncode != 0:
    print(r2.stderr)
    sys.exit(1)
N = json.loads(r2.stdout)

# 3) chaves duplicadas no literal (o eval esconderia)
keys = re.findall(r"^          ([A-Za-z_\"'][^:\n]*): \{", src, re.M)
dups = [k for k, n in collections.Counter(keys).items() if n > 1]
print("nós:", len(N), "| chaves duplicadas:", len(dups), dups[:5])

# 4) integridade das arestas
missing, bad, counts = [], [], []
for nid, n in N.items():
    for attr in ("w", "g", "t", "x", "s", "n"):
        if not n.get(attr):
            bad.append((nid, attr))
    if not n.get("c"):
        bad.append((nid, "c-vazio"))
    counts.append(len(n["c"]))
    for pair in n["c"]:
        if not (isinstance(pair, list) and len(pair) == 2):
            bad.append((nid, "par-malformado"))
        elif pair[1] not in N:
            missing.append((nid, pair[1]))

# 5) alcance a partir de start
seen, queue = {"start"}, ["start"]
while queue:
    cur = queue.pop()
    for _, tgt in N[cur]["c"]:
        if tgt in N and tgt not in seen:
            seen.add(tgt)
            queue.append(tgt)
unreach = sorted(set(N) - seen)

# 6) cartões novos: 2–3 saídas
new = [k for k in N if k.startswith(("u_", "S_", "M_"))]
over = [(k, len(N[k]["c"])) for k in new if not 2 <= len(N[k]["c"]) <= 3]
hooks = {k: len(N[k]["c"]) for k in ("b1", "b2", "b4", "b5", "b7", "x1", "x2", "x3", "x4", "x6")}

print("destinos em falta:", len(missing), missing[:5])
print("nós incompletos:", len(bad), bad[:5])
print("inalcançáveis:", len(unreach), unreach[:8])
print("novos fora de 2–3 saídas:", len(over), over[:5])
print("saídas: min %d max %d média %.2f" % (min(counts), max(counts), sum(counts) / len(counts)))
print("hooks existentes:", hooks)
print("cartões novos:", len(new), "| antigos:", len(N) - len(new))
