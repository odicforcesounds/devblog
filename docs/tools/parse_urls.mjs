#!/usr/bin/env node
// Parse the `urls` file into { category: [feedUrl, ...] } with dedupe + cleanup.
// Run from the project root:  node tools/parse_urls.mjs
import { readFileSync, writeFileSync } from 'node:fs';

const raw = readFileSync('urls', 'utf8');

const categories = new Map();
let current = 'Uncategorized';
categories.set(current, []);
const order = [current];

for (const line of raw.split(/\r?\n/)) {
  const t = line.trim();
  if (!t) continue;

  // Category header: dashes followed by a name (e.g. "----BSD")
  const m = t.match(/^-{2,}\s*(.+?)\s*$/);
  if (m) {
    current = m[1];
    if (!categories.has(current)) {
      categories.set(current, []);
      order.push(current);
    }
    continue;
  }

  // Strip trailing comments (# ... or quoted text) and keep only the URL itself
  let url = t.split('#')[0].trim();
  if (!url) continue;
  url = url.split(/\s+/)[0];
  if (!/^https?:\/\//.test(url)) continue;

  if (!categories.has(current)) {
    categories.set(current, []);
    order.push(current);
  }
  const list = categories.get(current);
  if (!list.includes(url)) list.push(url);
}

// Drop the empty "Uncategorized" placeholder if unused
if (categories.get('Uncategorized')?.length === 0) {
  categories.delete('Uncategorized');
  order.splice(order.indexOf('Uncategorized'), 1);
}

// The "Imobiliário" section is followed by a giant dump of unrelated personal-blog
// feeds. Keep the first couple of feeds under their original category and move the
// rest into a generic "Blogs" category so the page can sample from it.
const SPLIT_THRESHOLD = 1000; // categories larger than this get split
const extraOrder = [];
for (const c of order.slice()) {
  const list = categories.get(c);
  if (list && list.length > SPLIT_THRESHOLD) {
    const keep = list.slice(0, 2);
    const rest = list.slice(2);
    categories.set(c, keep);
    if (!categories.has('Blogs')) {
      categories.set('Blogs', []);
      extraOrder.push('Blogs');
    }
    const blogs = categories.get('Blogs');
    for (const u of rest) if (!blogs.includes(u)) blogs.push(u);
    console.log(`split category "${c}": kept ${keep.length}, moved ${rest.length} to "Blogs"`);
  }
}
for (const c of extraOrder) order.push(c);

const out = {};
for (const c of order) out[c] = categories.get(c);

let total = 0;
for (const [c, list] of Object.entries(out)) {
  console.log(c.padEnd(28), list.length);
  total += list.length;
}
console.log('TOTAL'.padEnd(28), total);

writeFileSync('tools/feeds.json', JSON.stringify(out, null, 1));
