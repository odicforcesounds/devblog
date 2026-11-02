#!/usr/bin/env python3
"""Repair the Awesome Story page: unclosed h1/header, cramped box, ragged text.

The page opened `<h1 class="title1"` and never closed the tag or the `<header>`,
so the menu, the story and the footer were all parsed as attributes or children
of the header — the whole reading column was squeezed into `--reading` (72ch).
This closes both tags, gives the story the wide column the menu already uses,
and justifies the text.
"""

import io

PATH = "docs/awesome_story.html"

EDITS = [
    (
        '  <h1 class="title1"  <nav class="story-menu" aria-label="Story parts">',
        '  <h1 class="title1">The Awesome Story</h1>\n'
        '  </header>\n'
        '  <nav class="story-menu" aria-label="Story parts">',
        '<h1 class="title1">The Awesome Story</h1>',
    ),
    (
        '    #story.textbox.black{display:block;overflow-y:auto;overflow-x:hidden;\n'
        '      height:calc(100vh - 12rem);height:calc(100dvh - 12rem);\n'
        '      margin:0 auto .8rem;padding-right:1.1rem;\n'
        '      font-size:.86rem;line-height:1.75}\n'
        '    @media (min-width:900px){#story.textbox.black{font-size:.9rem}}',
        '    #story.textbox.black{display:block;overflow-y:auto;overflow-x:hidden;\n'
        '      width:min(var(--wide),calc(100vw - 1.5rem));\n'
        '      max-width:min(var(--wide),calc(100vw - 1.5rem));\n'
        '      height:calc(100vh - 12rem);height:calc(100dvh - 12rem);\n'
        '      margin:0 auto .8rem;padding:.4rem clamp(1.1rem,3vw,2.4rem) 1rem;\n'
        '      font-size:.9rem;line-height:1.8}\n'
        '    #story .story-part{text-align:justify;hyphens:auto;-webkit-hyphens:auto;\n'
        '      orphans:2;widows:2}\n'
        '    @media (min-width:900px){#story.textbox.black{font-size:.95rem}}',
        '#story .story-part{text-align:justify',
    ),
    (
        '    if (window.visualViewport) window.visualViewport.addEventListener("resize", fit);',
        '    if (window.visualViewport) window.visualViewport.addEventListener("resize", fit);\n'
        '    window.addEventListener("load", fit);',
        'window.addEventListener("load", fit);',
    ),
]


def main():
    with io.open(PATH, encoding="utf-8") as handle:
        source = handle.read()
    original = source
    for old, new, marker in EDITS:
        if marker in source:
            print("  already applied:", marker[:48])
            continue
        if old not in source:
            raise SystemExit("  ! pattern not found: %r" % old[:60])
        source = source.replace(old, new, 1)
    reserved = ('      var panel = document.querySelector(".living-panel");\n'
                '      var used = (head ? head.offsetHeight : 0) + (menu ? menu.offsetHeight : 0) +\n'
                '        (turn ? turn.offsetHeight : 0) + (foot ? foot.offsetHeight : 0) +\n'
                '        (panel ? panel.offsetHeight + 10 : 0) + 26;')
    plain = ('      var used = (head ? head.offsetHeight : 0) + (menu ? menu.offsetHeight : 0) +\n'
             '        (turn ? turn.offsetHeight : 0) + (foot ? foot.offsetHeight : 0) + 26;')
    if reserved in source:
        source = source.replace(reserved, plain, 1)
        print("  removed the offset reserved for a card that is no longer at the foot")
    if source == original:
        print("nothing to change")
        return 0
    with io.open(PATH, "w", encoding="utf-8") as handle:
        handle.write(source)
    print("awesome_story.html repaired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
