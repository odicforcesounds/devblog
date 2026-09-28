#!/usr/bin/env node
// Probe feed URLs and record which ones work.
// Usage:
//   node tools/check_feeds.mjs --urls tools/shards/s_0.json --out tools/shards/r_0.json --conc 120
// Input/output format: { "Category": ["url", ...] } / { "Category": { "url": {ok,code,err} } }
// Add --sample K to only probe the first K urls of each category (for smoke tests).
import { readFileSync, writeFileSync } from 'node:fs';
import http from 'node:http';
import https from 'node:https';

const args = process.argv.slice(2);
function argOf(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
}
const IN = argOf('--urls', 'tools/feeds.json');
const OUT = argOf('--out', 'tools/check_results.json');
const CONC = Math.max(1, parseInt(argOf('--conc', '120'), 10));
const SAMPLE = parseInt(argOf('--sample', '0'), 10);

const data = JSON.parse(readFileSync(IN, 'utf8'));
const all = [];
for (const [cat, urls] of Object.entries(data)) {
  const list = SAMPLE > 0 ? urls.slice(0, SAMPLE) : urls;
  for (const u of list) all.push({ cat, url: u });
}

const results = {};
for (const cat of Object.keys(data)) results[cat] = {};
let cursor = 0;

function probeOnce(url, timeout, cb) {
  let u;
  try { u = new URL(url); } catch { return cb(false, 0, 'bad-url'); }
  const isHttps = u.protocol === 'https:';
  const mod = isHttps ? https : http;
  const opts = {
    hostname: u.hostname,
    port: u.port || (isHttps ? 443 : 80),
    path: u.pathname + u.search,
    method: 'GET',
    headers: {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36',
      'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*',
      'Accept-Encoding': 'identity',
    },
    timeout,
  };
  let settled = false;
  const finish = (ok, code, err) => {
    if (settled) return;
    settled = true;
    req.destroy();
    cb(ok, code, err);
  };
  const req = mod.request(opts, (res) => {
    const code = res.statusCode;
    if (code < 200 || code >= 400) {
      res.resume();
      return finish(false, code, `http-${code}`);
    }
    // Sniff first bytes: an empty body is not a usable feed/page.
    let bytes = 0;
    let sample = '';
    res.on('data', (chunk) => {
      bytes += chunk.length;
      if (sample.length < 500) sample += chunk.toString('latin1');
      if (bytes >= 200) finish(true, code, null);
    });
    res.on('end', () => {
      const emptyish = bytes < 120 || /^\s*$/.test(sample.slice(0, 64));
      finish(!emptyish, code, emptyish ? 'empty-body' : null);
    });
    res.on('error', () => finish(bytes > 0, code, bytes > 0 ? null : 'body-error'));
  });
  req.on('timeout', () => finish(false, 0, 'timeout'));
  req.on('error', (e) => finish(false, 0, e.code || e.message));
  req.end();
}

function probe(url, cb) {
  // attempt 1: short timeout (fast-fail on dead DNS/TLS)
  probeOnce(url, 6000, (ok1, c1, e1) => {
    if (ok1) return cb(true, c1, null);
    // attempt 2: full timeout
    probeOnce(url, 11000, (ok2, c2, e2) => {
      if (ok2) return cb(true, c2, null);
      cb(false, c2 || c1, e2 || e1 || 'unreachable');
    });
  });
}

function dump() {
  writeFileSync(OUT, JSON.stringify(results));
}

process.on('exit', dump);
process.on('SIGINT', () => process.exit(130));
process.on('SIGTERM', () => process.exit(143));

function worker() {
  if (cursor >= all.length) return;
  const item = all[cursor++];
  probe(item.url, (ok, code, err) => {
    results[item.cat][item.url] = { ok, code, err };
    setImmediate(worker);
  });
}
for (let i = 0; i < Math.min(CONC, all.length); i++) worker();
