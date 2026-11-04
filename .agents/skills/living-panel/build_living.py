#!/usr/bin/env python3
"""Write docs/living-panel.js — the pool the fixed card draws from on each load.

The markup in every page carries one being, one tool, one component, one plant and
one city so the card still reads with scripts off. This file gives the browser the whole
pool, and the page script replaces that set with a fresh one every time the page
is loaded. A click on the photograph opens a 500px copy; a double-click hides the
card for that page load. Both gestures are wired into the script below.

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
  var PAGES = { b: "birdsIndex.html", a: "animalsIndex.html",
                f: "fishesIndex.html", i: "insectsIndex.html" };
  var IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/";

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

  function asked(name) { return "?q=" + encodeURIComponent(name); }
  function beingHref(item) { return PAGES[item[1]] + asked(item[0]) + "#order-" + item[2]; }
  function toolHref(item) { return "awesomeIndex.html" + asked(item[0]) + "#cat-" + item[1]; }
  function partHref(item) { return "electronicsIndex.html" + asked(item[0]) + "#cat-" + item[1]; }
  function plantHref(item) { return "plantsIndex.html" + asked(item[0]) + "#order-" + item[1]; }
  function cityHref(item) { return "worldIndex.html" + asked(item[0]) + "#cat-" + item[1]; }

  function photo(item) {
    var rel = item[3];
    if (rel.indexOf("http") === 0) return rel;
    return IMG + rel + "/250px-" + rel.slice(rel.lastIndexOf("/") + 1);
  }

  function fullPhoto(item) {
    var rel = item[3];
    if (rel.indexOf("http") === 0) return rel;
    return IMG + rel + "/500px-" + rel.slice(rel.lastIndexOf("/") + 1);
  }

  function pick(pool, href, tries) {
    for (var n = 0; n < tries; n++) {
      var item = pool[Math.floor(Math.random() * pool.length)];
      if (!used[href(item)]) return item;
    }
    return pool[Math.floor(Math.random() * pool.length)];
  }

  function anchor(item, href) {
    var a = document.createElement("a");
    a.href = href(item);
    a.textContent = item[0];
    used[href(item)] = true;
    return a;
  }

  var being = pick(POOL.b, beingHref, 12);
  used[beingHref(being)] = true;
  var tool = pick(POOL.t, toolHref, 12);
  used[toolHref(tool)] = true;
  var part = pick(POOL.e, partHref, 12);
  used[partHref(part)] = true;
  var plant = pick(POOL.p, plantHref, 12);
  used[plantHref(plant)] = true;
  var city = pick(POOL.c, cityHref, 12);

  line.textContent = "";
  line.appendChild(document.createTextNode("this "));
  line.appendChild(anchor(being, beingHref));
  line.appendChild(document.createTextNode(" likes to use "));
  line.appendChild(anchor(tool, toolHref));
  line.appendChild(document.createTextNode(" and loves "));
  line.appendChild(anchor(part, partHref));
  line.appendChild(document.createTextNode(" while doing some diet with "));
  line.appendChild(anchor(plant, plantHref));
  line.appendChild(document.createTextNode(" at "));
  line.appendChild(anchor(city, cityHref));
  line.appendChild(document.createTextNode("."));

  if (image) {
    var fullSrc = fullPhoto(being);
    var zoom = null;
    var clickTimer = 0;

    image.src = photo(being);
    image.alt = being[0];
    image.title = "Click to expand · double-click to hide";
    image.style.cursor = "zoom-in";
    image.setAttribute("role", "button");
    image.setAttribute("tabindex", "0");
    image.setAttribute("aria-expanded", "false");
    image.setAttribute("aria-label", "Expand the photograph of " + being[0]);

    function closeZoom() {
      if (!zoom) return;
      if (zoom.parentNode) zoom.parentNode.removeChild(zoom);
      zoom = null;
      image.setAttribute("aria-expanded", "false");
      if (card.style.display !== "none") image.focus();
    }

    function openZoom() {
      if (zoom) return;
      zoom = document.createElement("div");
      zoom.setAttribute("role", "dialog");
      zoom.setAttribute("aria-modal", "true");
      zoom.setAttribute("aria-label", "Expanded photograph of " + being[0]);
      zoom.setAttribute("tabindex", "-1");
      zoom.style.cssText = "position:fixed;top:0;right:0;bottom:0;left:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;padding:1.25rem;background:rgba(4,7,10,.86);cursor:zoom-out";
      var big = document.createElement("img");
      big.src = fullSrc;
      big.alt = image.alt;
      big.style.cssText = "display:block;max-width:min(92vw,56rem);max-height:88vh;width:auto;height:auto;border:1px solid rgba(255,255,255,.2);border-radius:.8rem;box-shadow:0 1.5rem 4rem rgba(0,0,0,.6);background:#101018";
      zoom.appendChild(big);
      zoom.addEventListener("click", closeZoom);
      document.body.appendChild(zoom);
      image.setAttribute("aria-expanded", "true");
      zoom.focus();
    }

    function toggleZoom() {
      if (zoom) closeZoom();
      else openZoom();
    }

    image.addEventListener("click", function (event) {
      if (event.detail > 1) return;
      window.clearTimeout(clickTimer);
      clickTimer = window.setTimeout(toggleZoom, 220);
    });

    image.addEventListener("dblclick", function (event) {
      event.preventDefault();
      window.clearTimeout(clickTimer);
      card.style.display = "none";
      closeZoom();
    });

    image.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") {
        event.preventDefault();
        toggleZoom();
      } else if (event.key === "Escape") {
        closeZoom();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeZoom();
    });
  }
})();
"""


THUMB = "https://upload.wikimedia.org/wikipedia/commons/thumb/"
PAGE_CODES = {"birdsIndex.html": "b", "animalsIndex.html": "a",
              "fishesIndex.html": "f", "insectsIndex.html": "i"}


def column(items, shape):
    seen = set()
    out = []
    for item in items:
        key = (item["name"], item["href"])
        if key in seen:
            continue
        seen.add(key)
        out.append(shape(item))
    return out


def key_of(href, prefix):
    return href.split(prefix, 1)[1]


def short_photo(url):
    """The thumb path once, since the width part repeats its file name.

    `/thumb/d/db/Name.jpg/250px-Name.jpg` becomes `d/db/Name.jpg` and the script
    rebuilds the rest; nine files are served straight from commons and stay whole.
    """
    url = lp.thumb(url)
    if url.startswith(THUMB):
        rel = url[len(THUMB):]
        head, sep, tail = rel.rpartition("/250px-")
        if sep and head.split("/")[-1] == tail:
            return head
    return url


def main():
    beings = column(lp.beings(), lambda b: [b["name"],
                                            PAGE_CODES[b["page"]],
                                            key_of(b["href"], "#order-"),
                                            short_photo(b["image"])])
    tools = column(lp.tools(), lambda t: [t["name"], key_of(t["href"], "#cat-")])
    parts = column(lp.components(), lambda c: [c["name"], key_of(c["href"], "#cat-")])
    plants = column(lp.plants(), lambda p: [p["name"], key_of(p["href"], "#order-")])
    cities = column(lp.cities(), lambda c: [c["name"], key_of(c["href"], "#cat-")])
    if not beings or not tools or not parts or not plants or not cities:
        print("a pool came back empty", file=sys.stderr)
        return 1
    payload = json.dumps({"b": beings, "t": tools, "e": parts, "p": plants, "c": cities},
                         separators=(",", ":"), ensure_ascii=False)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(JS % payload)
    print("%s: %d beings, %d tools, %d components, %d plants, %d cities, %d KB"
          % (OUT, len(beings), len(tools), len(parts), len(plants), len(cities),
             os.path.getsize(OUT) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
