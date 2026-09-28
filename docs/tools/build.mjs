#!/usr/bin/env node
// Inject tools/feeds.json into index.html at the __FEED_DATA__ placeholder.
// Usage: node tools/build.mjs [feedsJsonPath]
import { readFileSync, writeFileSync, existsSync } from 'node:fs';

const feedsPath = process.argv[2] || 'tools/feeds.json';
const pagePath = 'index.html';
const MARK = '__FEED_DATA__';

const feedsRaw = readFileSync(feedsPath, 'utf8');
// Compact the JSON (single spaces) to keep the page lean; strings stay escaped properly.
const compact = JSON.stringify(JSON.parse(feedsRaw));
const page = readFileSync(pagePath, 'utf8');

const re = new RegExp('^(.*?)' + MARK + '(.*)$', 's');
const m = page.match(re);
if (!m) {
  if (page.includes(JSON.stringify(JSON.parse(feedsRaw)).slice(1, 60))) {
    console.log('index.html already contains injected data — nothing to do.');
    process.exit(0);
  }
  console.error('Placeholder ' + MARK + ' not found in index.html. Rebuild from template.');
  process.exit(1);
}

const out = m[1] + compact + m[2];
writeFileSync(pagePath, out);
const kb = (out.length / 1024).toFixed(0);
console.log(`Injected feeds into index.html (${kb} KB total).`);
if (existsSync('tools/check_results.json')) {
  console.log('Tip: to ship only feeds verified alive, run:');
  console.log('  node tools/filter_results.mjs && node tools/build.mjs');
}
