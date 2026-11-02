#!/usr/bin/env python3
"""Write docs/living-panel.js — the pool the fixed card draws from on each load.

The markup in every page carries one being and one tool so the card still reads
with scripts off. This file gives the browser the whole pool, and the page script
replaces that pair with a fresh one every time the page is loaded.

    python3 .agents/skills/living-panel/build_living.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import living_panel as lp  # noqa: E402

OUT = "docs/living-panel.js"

JS = """(function () {
  "use strict";

  var POOL = %s;

  var card = document.getElementById("living-panel");
  if (!card) return;
  var image = card.querySelector("img");
  var line = card.querySelector("p");
  if (!line) return;

  var used = Object.create(null);
  var links = document.querySelectorAll("a[href]");
  for (var i = 0; i < links.length; i++) {
    used[links[i].getAttribute("href")] = true;
  }

  function pick(pool, key, tries) {
    for (var n = 0; n < tries; n++) {
      var item = pool[Math.floor(Math.random() * pool.length)];
      if (!used[key(item)]) return item;
    }
    return pool[Math.floor(Math.random() * pool.length)];
  }

  var being = pick(POOL.b, function (item) { return item[1]; }, 12);
  var tool = pick(POOL.t, function (item) { return "awesomeIndex.html#cat-" + item[1]; }, 12);

  line.textContent = "";
  line.appendChild(document.createTextNode("this "));

  var who = document.createElement("a");
  who.href = being[1];
  who.textContent = being[0];
  line.appendChild(who);

  line.appendChild(document.createTextNode(" likes to use "));

  var what = document.createElement("a");
  what.href = "awesomeIndex.html#cat-" + tool[1];
  what.textContent = tool[0];
  line.appendChild(what);

  line.appendChild(document.createTextNode("."));

  if (image && being[2]) {
    image.src = being[2];
    image.alt = being[0];
  }
})();
"""


def main():
    beings, tools = [], []
    seen = set()
    for being in lp.beings():
        key = (being["name"], being["href"])
        if key in seen:
            continue
        seen.add(key)
        beings.append([being["name"], being["href"], lp.thumb(being["image"])])
    seen = set()
    for tool in lp.tools():
        key = (tool["name"], tool["key"])
        if key in seen:
            continue
        seen.add(key)
        tools.append([tool["name"], tool["key"]])
    if not beings or not tools:
        print("no beings or no tools collected", file=sys.stderr)
        return 1
    payload = json.dumps({"b": beings, "t": tools}, separators=(",", ":"),
                         ensure_ascii=False)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(JS % payload)
    print("%s: %d beings, %d tools, %d KB"
          % (OUT, len(beings), len(tools), os.path.getsize(OUT) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
