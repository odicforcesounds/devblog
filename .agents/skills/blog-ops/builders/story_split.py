#!/usr/bin/env python3
"""Split the one-line Awesome Story into numbered parts with a menu at the top.

The text stays in the same file — it is only hidden behind the menu in the
browser, so the page still carries every word and every link.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import re

PATH = "docs/awesome_story.html"
PARTS = 24

START = '<div id="story" class="textbox black">'
END = "</div>\n<footer>"


def cut_points(story, count):
    """Positions just after a sentence end, never inside a tag."""
    candidates = []
    for match in re.finditer(r"\.\s", story):
        index = match.start()
        if story.rfind("<", 0, index) > story.rfind(">", 0, index):
            continue                                   # inside an attribute
        following = story[match.end():match.end() + 40].lstrip()
        if not following or not (following[0].isupper() or following[0] == "<"):
            continue
        candidates.append(match.end())
    target = len(story) / count
    chosen, previous = [], 0
    for step in range(1, count):
        goal = target * step
        best = min(candidates,
                   key=lambda p: (abs(p - goal) if p > previous + target * 0.55 else float("inf")))
        if best <= previous:
            best = min((p for p in candidates if p > previous), default=len(story) - 1)
        chosen.append(best)
        previous = best
    return chosen


def main():
    html = open(PATH, encoding="utf-8").read()
    start = html.index(START) + len(START)
    end = html.index(END, start)
    story = html[start:end]
    print("story:", len(story), "chars,", story.count("<a "), "links")

    cuts = [0] + cut_points(story, PARTS) + [len(story)]
    pieces = [story[cuts[i]:cuts[i + 1]] for i in range(len(cuts) - 1)]
    sizes = [len(p) for p in pieces]
    print("parts:", len(pieces), "| chars min/max:", min(sizes), max(sizes))

    menu_items, sections, rows = [], [], []
    for number, piece in enumerate(pieces, 1):
        links = piece.count("<a ")
        menu_items.append(
            '        <li><button type="button" class="part-link" data-part="%d"'
            ' aria-current="%s">Part %d</button></li>'
            % (number, "true" if number == 1 else "false", number))
        hidden = "" if number == 1 else " hidden"
        sections.append(
            '    <section class="story-part" id="part-%d" data-part="%d" aria-label="Part %d of %d"%s>%s</section>'
            % (number, number, number, len(pieces), hidden, piece))
        rows.append(links)

    block = """  <nav class="story-menu" aria-label="Story parts">
    <div class="story-menu-head">
      <p>Read it in parts<span>%d steps, one at a time</span></p>
      <p class="story-count" id="story-status">Part 1 of %d · %s links</p>
    </div>
    <ol class="story-parts">
%s
    </ol>
  </nav>
  <div id="story" class="textbox black" tabindex="0" aria-label="The Awesome Story, current part">
%s
  </div>
  <nav class="story-turn" aria-label="Turn to another part">
    <button type="button" id="part-prev">◀ Previous part</button>
    <button type="button" id="part-next">Next part ▶</button>
  </nav>""" % (len(pieces), len(pieces), "{:,}".format(rows[0]),
               "\n".join(menu_items), "\n".join(sections))

    html = html[:html.index(START) - len(START)] + block + html[end + len("</div>"):]

    style = """  <style>
    .story-menu{position:static;margin:0 auto .8rem;
      width:calc(100vw - 1.5rem);max-width:calc(100vw - 1.5rem);
      padding:.6rem clamp(.8rem,2vw,1.2rem);border:1px solid var(--line);
      border-radius:10px;background:rgba(9,10,16,.94)}
    .story-menu-head{display:flex;flex-wrap:wrap;align-items:baseline;
      justify-content:space-between;gap:.25rem 1.2rem;margin:0 0 .5rem}
    .story-menu-head p{margin:0;font-family:var(--mono);font-size:.72rem;
      letter-spacing:.16em;text-transform:uppercase;color:var(--faint)}
    .story-menu-head p span{font-family:var(--serif);font-style:italic;font-size:.92rem;
      letter-spacing:0;text-transform:none;color:var(--cyan);margin-left:.6rem}
    .story-menu-head .story-count{letter-spacing:.06em;text-transform:none;color:var(--muted)}
    .story-parts{display:flex;flex-wrap:wrap;gap:.3rem;margin:0;padding:0;list-style:none}
    .part-link{font:inherit;font-family:var(--mono);font-size:.76rem;line-height:1.5;
      cursor:pointer;padding:.18rem .58rem;border-radius:999px;color:var(--text);
      border:1px solid var(--line-2);background:rgba(255,255,255,.04);
      transition:color .12s,border-color .12s,background .12s}
    .part-link:hover{border-color:var(--cyan);color:#fff}
    .part-link[aria-current="true"]{background:rgba(92,225,255,.16);border-color:var(--cyan);color:#fff}
    .part-link:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
    .story-part[hidden]{display:none}
    .story-turn{display:flex;flex-wrap:wrap;justify-content:center;gap:.7rem;
      max-width:calc(100vw - 1.5rem);margin:.7rem auto .9rem}
    .story-turn button{font:inherit;font-family:var(--mono);font-size:.8rem;cursor:pointer;
      padding:.45rem 1rem;border-radius:999px;color:var(--text);
      border:1px solid var(--line-2);background:rgba(255,255,255,.04);
      transition:color .12s,border-color .12s,transform .12s}
    .story-turn button:hover:not(:disabled){color:#fff;border-color:var(--cyan);transform:translateY(-1px)}
    .story-turn button:disabled{opacity:.35;cursor:default}
    .story-turn button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
    /* The page body is 19px serif; this one continuous line reads too heavy at
       that size, so the story itself steps down and the lines breathe a little. */
    /* The story fills the window and scrolls inside itself. The height below is
       only a fallback: the script measures the page furniture and sets the exact
       height, so the writing never spills past the screen and the page itself
       stays scrollable if anything goes wrong. */
    #story.textbox.black{display:block;overflow-y:auto;overflow-x:hidden;
      height:calc(100vh - 12rem);height:calc(100dvh - 12rem);
      margin:0 auto .8rem;padding-right:1.1rem;
      font-size:.86rem;line-height:1.75}
    @media (min-width:900px){#story.textbox.black{font-size:.9rem}}
    #story.textbox.black:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
    @media (max-height:560px){.story-menu .story-menu-head p:first-child{display:none}}
    @media (prefers-reduced-motion:reduce){.part-link,.story-turn button{transition:none}
      .story-turn button:hover:not(:disabled){transform:none}}
  </style>
"""
    html = html.replace("</head>", style + "</head>", 1)
    html = html.replace(
        '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; img-src \'self\' data:;">',
        '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; img-src \'self\' data:; '
        'style-src \'unsafe-inline\'; script-src \'unsafe-inline\';">', 1)
    html = html.replace(
        "</head>",
        "  <noscript><style>.story-part[hidden]{display:block!important}"
        ".story-menu,.story-turn{display:none!important}</style></noscript>\n</head>", 1)

    script = """  <script>
  (function () {
    "use strict";
    var parts = [].slice.call(document.querySelectorAll(".story-part"));
    var buttons = [].slice.call(document.querySelectorAll(".part-link"));
    var status = document.getElementById("story-status");
    var prev = document.getElementById("part-prev");
    var next = document.getElementById("part-next");
    var story = document.getElementById("story");
    var menu = document.querySelector(".story-menu");
    var turn = document.querySelector(".story-turn");
    var head = document.querySelector("header");
    var foot = document.querySelector("footer");
    var current = 0;

    // Measure what the page furniture takes and give the rest to the story, so
    // the writing fills the window and scrolls inside it instead of growing down.
    function fit() {
      var used = (head ? head.offsetHeight : 0) + (menu ? menu.offsetHeight : 0) +
        (turn ? turn.offsetHeight : 0) + (foot ? foot.offsetHeight : 0) + 26;
      var room = window.innerHeight - used;
      story.style.height = Math.max(220, room) + "px";
    }
    window.addEventListener("resize", fit);
    window.addEventListener("orientationchange", fit);
    if (window.visualViewport) window.visualViewport.addEventListener("resize", fit);

    function show(index, move) {
      if (!parts.length) return;
      index = Math.max(0, Math.min(parts.length - 1, index));
      current = index;
      parts.forEach(function (part, place) { part.hidden = place !== index; });
      buttons.forEach(function (button, place) {
        button.setAttribute("aria-current", place === index ? "true" : "false");
      });
      var links = parts[index].querySelectorAll("a").length;
      status.textContent = "Part " + (index + 1) + " of " + parts.length + " · " +
        links.toLocaleString("en-GB") + " links";
      prev.disabled = index === 0;
      next.disabled = index === parts.length - 1;
      if (window.history && history.replaceState) {
        history.replaceState(null, "", index === 0 ? location.pathname : "#part-" + (index + 1));
      }
      if (story) story.scrollTop = 0;
    }

    buttons.forEach(function (button, place) {
      button.addEventListener("click", function () { show(place, true); });
    });
    prev.addEventListener("click", function () { show(current - 1, true); });
    next.addEventListener("click", function () { show(current + 1, true); });
    document.addEventListener("keydown", function (event) {
      if (event.target && /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) return;
      if (event.key === "ArrowRight") show(current + 1, true);
      if (event.key === "ArrowLeft") show(current - 1, true);
    });
    fit();
    var jump = /#part-(\\d+)/.exec(location.hash);
    show(jump ? parseInt(jump[1], 10) - 1 : 0, false);
    fit();
  })();
  </script>
"""
    html = html.replace("</body>", script + "</body>", 1)
    open(PATH, "w", encoding="utf-8").write(html)
    print("written:", len(html), "chars")


if __name__ == "__main__":
    main()
