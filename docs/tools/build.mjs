#!/usr/bin/env node
// Inject tools/feeds.json into index.html (or tools/template.html when given).
// Handles both the raw placeholder state and a previously built page.
// Usage: node tools/build.mjs [feedsJsonPath] [pagePath]
import { readFileSync, writeFileSync } from 'node:fs';

const feedsPath = process.argv[2] || 'tools/feeds.json';
const pagePath = process.argv[3] || 'index.html';
const MARK = '__FEED_DATA__';

const compact = JSON.stringify(JSON.parse(readFileSync(feedsPath, 'utf8')));
const page = readFileSync(pagePath, 'utf8');

let out;
if (page.includes(MARK)) {
  out = page.replace(MARK, compact);
} else {
  // Page was already built once: replace the existing embedded dataset.
  const re = /window\.FEED_DATA = \{.*?\};\n/s;
  if (!re.test(page)) {
    console.error('No placeholder and no embedded FEED_DATA found in ' + pagePath);
    process.exit(1);
  }
  out = page.replace(re, 'window.FEED_DATA = ' + compact + ';\n');
}

writeFileSync(pagePath, out);
console.log(`Injected feeds into ${pagePath} (${(out.length / 1024).toFixed(0)} KB total).`);
