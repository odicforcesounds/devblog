// Teste de fumo do motor com um DOM mínimo: corre o script da página e caminha
// pelo grafo com as teclas 1–4, registando cada cartão que é desenhado.
const fs = require("fs");
const src = fs.readFileSync(process.argv[2] || "docs/aViragem.html", "utf8");
const script = src.match(/<script[^>]*>([\s\S]*?)<\/script>/)[1];

function el(id) {
  return {
    id, textContent: "", innerHTML: "", disabled: false, offsetWidth: 1,
    children: [], _cn: "",
    classList: { toggle() {}, remove() {}, add() {} },
    appendChild(c) { this.children.push(c); return c; },
    insertBefore(c) { this.children.push(c); return c; },
    addEventListener(t, f) { (this.listeners = this.listeners || {})[t] = f; },
    querySelectorAll() { return this.children.filter((c) => c.className === "choice"); },
    set className(v) { this._cn = v; },
    get className() { return this._cn; },
  };
}
const nodes = {};
global.document = {
  getElementById(id) { return nodes[id] || (nodes[id] = el(id)); },
  createElement(tag) { return el(tag); },
  createTextNode(t) { return { textContent: t }; },
  addEventListener(t, f) { if (t === "keydown") global.__key = f; },
};

eval(script);

const choicesEl = nodes["choices"];
const titleEl = nodes["title"];
const seen = new Set();
const key = (k) => global.__key({ key: k, preventDefault() {}, target: { tagName: "BODY" } });

let errors = 0;
for (let i = 0; i < 4000; i++) {
  const n = 1 + Math.floor(Math.random() * 4);
  try {
    key(String(n));
    if (i % 37 === 0) key("Backspace");
    if (i % 211 === 0) key("r");
  } catch (e) {
    errors++;
    if (errors < 3) console.error("ERRO:", e.message);
  }
  seen.add(titleEl.textContent);
}
// botões desenhados no último render
const buttons = choicesEl.children.filter((c) => c.className === "choice");
console.log("cartões distintos visitados:", seen.size);
console.log("erros:", errors);
console.log("saídas desenhadas no último cartão:", buttons.length);
console.log("exemplo:", [...seen].slice(0, 6).join(" / "));
