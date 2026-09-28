#!/usr/bin/env bash
# Split feeds.json into shards, check all in parallel, merge results.
set -u
cd "$(dirname "$0")/.."

SHARDS=4
CONC=100
mkdir -p tools/shards

node -e '
const fs = require("fs");
const d = JSON.parse(fs.readFileSync("tools/feeds.json", "utf8"));
const all = [];
for (const [cat, urls] of Object.entries(d)) for (const u of urls) all.push([cat, u]);
const N = parseInt(process.argv[1], 10);
const shards = Array.from({ length: N }, () => ({}));
all.forEach(([cat, u], i) => {
  const s = i % N;
  (shards[s][cat] = shards[s][cat] || []).push(u);
});
shards.forEach((sh, i) => fs.writeFileSync(`tools/shards/s_${i}.json`, JSON.stringify(sh)));
console.log(`shards written: ${all.length} urls into ${N} files`);
' "$SHARDS"

pids=()
for i in $(seq 0 $((SHARDS - 1))); do
  node tools/check_feeds.mjs --urls "tools/shards/s_${i}.json" --out "tools/shards/r_${i}.json" --conc "$CONC" &
  pids+=($!)
done

fail=0
for p in "${pids[@]}"; do
  wait "$p" || fail=1
done

if [ "$fail" -ne 0 ]; then
  echo "ERROR: one or more shards failed"
  exit 1
fi

node -e '
const fs = require("fs");
const merged = {};
let total = 0, ok = 0;
for (let i = 0; i < parseInt(process.argv[1], 10); i++) {
  const r = JSON.parse(fs.readFileSync(`tools/shards/r_${i}.json`, "utf8"));
  for (const [cat, m] of Object.entries(r)) {
    merged[cat] = merged[cat] || {};
    for (const [u, res] of Object.entries(m)) {
      merged[cat][u] = res;
      total++;
      if (res.ok) ok++;
    }
  }
}
fs.writeFileSync("tools/check_results.json", JSON.stringify(merged));
console.log(`merged: ${ok}/${total} feeds alive`);
' "$SHARDS"
echo "DONE"
