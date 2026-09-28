#!/usr/bin/env node
// Build tools/feeds.json for index.html.
// Named categories: Activism, BSD, Coding, Hacking, Security, Linux (from the
// categorized file) + Noticias (its original 5 links). EVERYTHING else — the
// entire blog dump, unsampled — goes into "Blogs".
// Usage: node tools/build_feeds.mjs   (run from project root)
import { readFileSync, writeFileSync } from 'node:fs';

const NAMED = ['Activism', 'BSD', 'Coding', 'Hacking', 'Security', 'Linux'];
// Original Noticias section (categorized file had it between "Global News in
// Portuguese" and the blog dump):
const NOTICIAS = [
  'https://www.noticiasaominuto.com/rss/pais',
  'https://www.noticiasaominuto.com/rss/mundo',
  'https://www.rtp.pt/noticias/rss/pais',
  'https://www.rtp.pt/noticias/rss/mundo',
  'http://www.paredesdecoura.pt/rss',
];

// --- categorized file -> named sections -----------------------------------
const raw = readFileSync('urls.bak', 'utf8');
const sections = new Map();
let current = null;
for (const line of raw.split(/\r?\n/)) {
  const t = line.trim();
  if (!t) continue;
  const m = t.match(/^-{2,}\s*(.+?)\s*$/);
  if (m) { current = m[1]; continue; }
  let u = t.split('#')[0].trim();
  if (!u) continue;
  u = u.split(/\s+/)[0];
  if (!/^https?:\/\//.test(u)) continue;
  if (!sections.has(current)) sections.set(current, []);
  const list = sections.get(current);
  if (!list.includes(u)) list.push(u);
}

// --- flat one-line list = the universe of all links ------------------------
const all = [];
{
  const flat = readFileSync('urls', 'utf8');
  const re = /"(https?:\/\/[^"]+)"/g;
  let m;
  while ((m = re.exec(flat)) !== null) all.push(m[1]);
}

// --- assemble ---------------------------------------------------------------
const out = {};
const seen = new Set();

for (const cat of NAMED) {
  out[cat] = [];
  for (const u of sections.get(cat) || []) {
    if (!seen.has(u)) { seen.add(u); out[cat].push(u); }
  }
}
out.Noticias = [];
for (const u of NOTICIAS) {
  if (!seen.has(u)) { seen.add(u); out.Noticias.push(u); }
}
out.Blogs = []; // added after Noticias so it renders last

// Blogs: every link from the flat list not already in a named category.
for (const u of all) {
  if (!seen.has(u)) { seen.add(u); out.Blogs.push(u); }
}

writeFileSync('tools/feeds.json', JSON.stringify(out));

let total = 0;
for (const [c, list] of Object.entries(out)) {
  console.log(c.padEnd(28), String(list.length).padStart(6));
  total += list.length;
}
console.log('TOTAL'.padEnd(28), String(total).padStart(6));
