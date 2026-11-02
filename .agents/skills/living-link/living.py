#!/usr/bin/env python3
"""Put one random living being and one random tool on every page of the blog.

On the front page it is a small fixed card that stays in view while you scroll:

    <aside class="living-box" id="living-box">
      <img src="…/500px-…jpg" alt="Common carp">
      <p>this <a href="animalsIndex.html#order-cypriniformes">Common carp</a> likes to code
      with <a href="awesomeIndex.html#cat-shell">Bash</a>, and this site has a
      <a href="bashScripting.html">Bash guide</a>.</p>
    </aside>

On every other page it is one quiet line at the end of the footer:

    <p class="small living-link">this <a href="…">European robin</a> likes to code with …</p>

Beings come from the five catalogue indexes under docs/<kingdom>/data/; tools come
from docs/awesome/data/, and the link points at the category the tool sits in.

Runs without JavaScript and without a network request: the sentence is written into
the page, so it survives a strict Content-Security-Policy. Each page gets its own
pick, stable across runs, so the site as a whole reads varied.

    python3 .agents/skills/living-link/living.py             # every page
    python3 .agents/skills/living-link/living.py --dry-run    # show, do not write
    python3 .agents/skills/living-link/living.py --seed 7     # reshuffle the lot
    python3 .agents/skills/living-link/living.py --page index.html
    python3 .agents/skills/living-link/living.py --remove     # take the lines out
"""

import argparse
import glob
import hashlib
import html
import json
import os
import random
import re
import sys

DOCS = "docs"
CATALOGUES = (
    ("birds", "birdsIndex.html"),
    ("plants", "plantsIndex.html"),
    ("animals", "animalsIndex.html"),
    ("fishes", "fishesIndex.html"),
    ("insects", "insectsIndex.html"),
)
# The one page that is deliberately left alone: its story boxes are read in parts
# and a stray paragraph would break the reader.
SKIP = {"awesome_story.html"}
FRONT = "index.html"          # the page that gets the fixed card instead of a footer line
SNIPPET = re.compile(r'\n?[ \t]*<p class="small living-link">.*?</p>', re.S)
BOX = re.compile(r'\n?[ \t]*<aside class="living-box" id="living-box".*?</aside>', re.S)
BOX_STYLE = re.compile(r'[ \t]*<style id="living-box-style">.*?</style>\n', re.S)
BOX_OPEN = '<style id="living-box-style">'

BOX_CSS = """    /* The living link on the front page: a strip at the foot of the window that
       stays there while the archive scrolls — the slot an advert would take,
       given to one animal and one tool instead. */
    body{padding-bottom:5rem}
    .living-box{position:fixed;left:0;right:0;bottom:0;z-index:40;
      display:flex;align-items:center;justify-content:center;gap:.85rem;
      margin:0;padding:.6rem clamp(.8rem,2vw,1.6rem);border-top:1px solid var(--line);
      background:rgba(8,12,17,.96);-webkit-backdrop-filter:blur(10px);
      backdrop-filter:blur(10px);box-shadow:0 -18px 44px -30px rgba(0,0,0,.95);text-align:left}
    .living-box img{width:58px;height:58px;flex:0 0 auto;object-fit:cover;border-radius:.5rem;
      border:1px solid var(--line);background:var(--panel)}
    .living-box p{margin:0;max-width:54rem;font-size:.82rem;line-height:1.5;color:var(--muted)}
    .living-box a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--line-strong)}
    .living-box a:hover,.living-box a:focus-visible{color:var(--accent-warm);border-color:currentColor}
    .to-top{bottom:calc(clamp(.9rem,3vw,1.8rem) + 4.6rem)}
    @media (max-width:640px){.living-box{gap:.6rem;padding:.5rem .7rem}
      .living-box img{width:46px;height:46px}.living-box p{font-size:.78rem}}
    @media print{.living-box{display:none}body{padding-bottom:0}.to-top{bottom:1.5rem}}
"""


def esc(text):
    return html.escape(text, quote=True)


def beings(with_image=False):
    """Every species and plant in the five catalogues, with the index that lists it."""
    found = []
    for folder, page in CATALOGUES:
        for path in sorted(glob.glob(os.path.join(DOCS, folder, "data", "*.json"))):
            if path.endswith("index.json"):
                continue
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            for family in data.get("families", []):
                for being in family.get("s", []):
                    name = (being.get("n") or "").strip()
                    image = being.get("i") or ""
                    if not name or len(name) > 28:
                        continue
                    if with_image and not image:
                        continue
                    found.append({"name": name, "page": page,
                                  "href": "%s#order-%s" % (page, data.get("key", "")),
                                  "image": image})
    return found


def tools():
    """Tool names from the Awesome Index, with the category that holds them.

    A list is often named after the tool itself (Bash, Go, Docker), which reads best
    in the sentence, so that name is used when it is the thing you code with.
    Otherwise one short, real tool from that list stands in.
    """
    boring = re.compile(r"cheat|sheet|book|knowledge|awesome|lists?\b|resources?|\bapps\b|\btools\b|"
                        r"community|tutorial|guide|course|news|blog|misc|article|collection|top\b|"
                        r"\bbest\b|free|open source|\bpdf\b|\bhtml\b|\bcss\b|\bjson\b|\bxml\b|"
                        r"\byaml\b|\bcsv\b|\bsvg\b|\bhttp\b|\bapi\b|\bide\b|\bios\b|\bos\b|"
                        r"testing|framework|librar|language|style|design|icons?|fonts?|images?|"
                        r"videos?|audio|papers?|books?|games?|editors?|extensions?|music|"
                        r"investing|blockchain|crypto|forensic|scalab|microservice|serverless|"
                        r"sysadmin|pentest|\bctf\b|\bwaf\b|privacy|learning|education|career|"
                        r"health|financ|marketing", re.I)
    tool_name = re.compile(r"^[A-Za-z][\w.+#-]{1,15}$")
    # Lists whose own name is the thing you code with. Everything else is a topic
    # (`Music`, `Investing`, `Scalability`) and lends the line a real tool instead.
    code_list = {"bash", "zsh", "fish", "powershell", "go", "rust", "python", "ruby",
                 "node.js", "typescript", "javascript", "php", "java", "kotlin", "swift",
                 "c", "c++", "c#", ".net", "angular", "react", "vue", "svelte", "django",
                 "flask", "rails", "laravel", "docker", "kubernetes", "emacs", "vim",
                 "neovim", "git", "postgresql", "mysql", "redis", "sqlite", "nix", "elixir",
                 "erlang", "haskell", "clojure", "scala", "dart", "flutter", "electron",
                 "wasm", "llvm", "linux", "macos", "android", "ios", "arduino", "lua",
                 "perl", "julia", "zig", "ocaml"}
    found = []
    for path in sorted(glob.glob(os.path.join(DOCS, "awesome", "data", "*.json"))):
        if path.endswith("index.json"):
            continue
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        key = data.get("key") or ""
        title = data.get("title") or ""
        for lst in data.get("lists", []):
            list_name = (lst.get("n") or "").strip()
            chosen = None
            if list_name.lower() in code_list:
                chosen = list_name
            else:
                options = []
                for drawer in lst.get("d", []):
                    for entry in drawer.get("c", []):
                        name = (entry.get("n") or "").strip()
                        if not tool_name.match(name) or boring.search(name):
                            continue
                        if "github.com" not in (entry.get("u") or ""):
                            continue
                        options.append(name)
                if options:
                    # One stable pick per list, so every drawer lends a different tool.
                    seed = hashlib.sha256((key + "/" + list_name).encode()).hexdigest()
                    chosen = options[int(seed[:8], 16) % len(options)]
                elif tool_name.match(list_name) and not boring.search(list_name):
                    chosen = list_name
            if not chosen:
                continue
            found.append({"name": chosen, "list": list_name, "key": key, "title": title})
    return found


def guides():
    """Pages of this blog that expand on a tool, keyed by the word they open with.

    A title that starts `Bash: …` or a file called bashScripting.html both answer
    to `bash`, so the sentence can point at the manual as well as the drawer.
    """
    skip = {"index.html", "404.html", "home.html", "awesome_story.html"}
    skip |= {page for _, page in CATALOGUES}
    found = {}
    for path in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        name = os.path.basename(path)
        if name in skip:
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(6000)
        title = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
        title = re.sub(r"\s+", " ", title.group(1) if title else "").strip()
        stem = os.path.splitext(name)[0]
        words = []
        head_word = re.match(r"([A-Za-z][A-Za-z0-9.+#-]{1,20})\s*[:—–-]", title)
        if head_word:
            words.append(head_word.group(1))
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", stem)
        if parts:
            words.append(parts[0])
        for word in words:
            token = word.lower().strip(".-+#")
            if len(token) < 3:
                continue
            found.setdefault(token, []).append(name)
    for token in found:
        found[token].sort(key=lambda page: (len(page), page))
    return found


def sentence(being, tool, link_being=True, guide=None):
    """The one line, as the paragraph it always is."""
    if link_being:
        who = '<a href="%s">%s</a>' % (esc(being["href"]), esc(being["name"]))
    else:
        who = esc(being["name"])
    line = ('this %s likes to code with '
            '<a href="awesomeIndex.html#cat-%s" title="%s · %s">%s</a>'
            % (who, esc(tool["key"]), esc(tool["list"]), esc(tool["title"]),
               esc(tool["name"])))
    if guide:
        line += (', and this site has a <a href="%s">%s guide</a>'
                 % (esc(guide[0]), esc(guide[1])))
    return line + "."


def links_in(source):
    return set(re.findall(r'href="([^"]+)"', source))


def place(source, block):
    """Put a line at the end of the page footer, or before </body> if there is none."""
    index = source.rfind("</footer>")
    if index != -1:
        return source[:index] + block + "\n" + source[index:]
    index = source.rfind("</body>")
    if index != -1:
        return source[:index] + block + "\n" + source[index:]
    return None


def card(being, tool, link_being=True, guide=None):
    """The front page version: same sentence, the creature's photograph, fixed in view."""
    inner = sentence(being, tool, link_being, guide)
    # The catalogue keeps a 500px photograph. Wikimedia serves thumbnails only at
    # the widths it lists, and 250 is on that list: 26 KB instead of 96 KB.
    thumb = re.sub(r"/500px-", "/250px-", being.get("image") or "", count=1)
    image = ('<img src="%s" alt="%s" width="58" height="58" loading="lazy" decoding="async">\n      '
             % (esc(thumb), esc(being["name"]))) if thumb else ""
    return ('  <aside class="living-box" id="living-box" aria-label="A living being and a tool">\n'
            '      %s<p>%s</p>\n  </aside>' % (image, inner))


def with_card(source, block):
    """Drop the card at the end of <body> so nothing transformed can trap it."""
    source = BOX.sub("", source)
    source = SNIPPET.sub("", source)          # the footer line, if this page ever had one
    source = BOX_STYLE.sub("", source)
    style = "  %s\n%s  </style>\n" % (BOX_OPEN, BOX_CSS)
    source = re.sub(r"</head>", style + "</head>", source, count=1, flags=re.I)
    index = source.rfind("</body>")
    if index == -1:
        return None
    return source[:index] + block + "\n" + source[index:]


def pick(rng, items, taken):
    """Random pick that does not repeat a link the page already carries."""
    free = [item for item in items if (item.get("href") or "") not in taken]
    if not free:
        return rng.choice(items), False
    return rng.choice(free), True


def choose(rng, taken, being_pool, tool_pool):
    being, link_being = pick(rng, being_pool, taken)
    # One category first, then one tool inside it: the drawers hold very different
    # numbers of lists, and picking flat would drown the page in the biggest one.
    by_category = {}
    for tool in tool_pool:
        if "awesomeIndex.html#cat-" + tool["key"] in taken:
            continue
        by_category.setdefault(tool["key"], []).append(tool)
    if by_category:
        tool = rng.choice(by_category[rng.choice(sorted(by_category))])
    else:
        tool = rng.choice(tool_pool)
    return being, link_being, tool


def find_guide(tool, guide_pool, taken, page):
    """A page of this blog that expands on the tool, if one exists and is not linked here."""
    for word in (tool["name"], tool["list"]):
        for candidate in guide_pool.get(word.lower(), []):
            if candidate != page and candidate not in taken:
                return (candidate, word)
    return None


def rewrite(source, rng, being_pool, tool_pool, guide_pool, page):
    clean = SNIPPET.sub("", source)
    taken = links_in(clean)
    being, link_being, tool = choose(rng, taken, being_pool, tool_pool)
    guide = find_guide(tool, guide_pool, taken, page)
    block = "  <p class=\"small living-link\">%s</p>" % sentence(being, tool, link_being, guide)
    updated = place(clean, block)
    return (updated, being, tool) if updated is not None else (None, being, tool)


def rewrite_front(source, rng, being_pool, tool_pool, guide_pool, page):
    taken = links_in(BOX.sub("", SNIPPET.sub("", source)))
    being, link_being, tool = choose(rng, taken, being_pool, tool_pool)
    guide = find_guide(tool, guide_pool, taken, page)
    updated = with_card(source, card(being, tool, link_being, guide))
    return (updated, being, tool) if updated is not None else (None, being, tool)


def main(argv=None):
    parser = argparse.ArgumentParser(description="A random living being and tool on every page.")
    parser.add_argument("--seed", default="", help="change it to reshuffle every page")
    parser.add_argument("--page", action="append", default=[], help="only this page (repeatable)")
    parser.add_argument("--remove", action="store_true", help="take it out again")
    parser.add_argument("--dry-run", action="store_true", help="print, do not write")
    args = parser.parse_args(argv)

    plain_pool = beings()
    image_pool = beings(with_image=True)
    tool_pool = tools()
    guide_pool = guides()
    if not plain_pool or not tool_pool:
        print("no beings or no tools found — nothing to do", file=sys.stderr)
        return 1
    print("beings: %d (%d with a photo) | tools: %d | guides: %d"
          % (len(plain_pool), len(image_pool), len(tool_pool), len(guide_pool)))

    pages = args.page or sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "*.html")))
    written = removed = skipped = 0
    samples = []
    for name in pages:
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            print("  ! missing:", name)
            skipped += 1
            continue
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        if name in SKIP:
            skipped += 1
            continue
        if 'http-equiv="refresh"' in source[:2000]:
            skipped += 1                       # a redirect, nobody reads it
            continue
        if args.remove:
            cleaned = BOX_STYLE.sub("", BOX.sub("", SNIPPET.sub("", source)))
            if cleaned != source:
                if not args.dry_run:
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(cleaned)
                removed += 1
            continue
        rng = random.Random(hashlib.sha256((name + "|" + args.seed).encode()).hexdigest())
        if name == FRONT:
            updated, being, tool = rewrite_front(source, rng, image_pool, tool_pool,
                                                 guide_pool, name)
        else:
            updated, being, tool = rewrite(source, rng, plain_pool, tool_pool, guide_pool, name)
        if updated is None:
            print("  ! no footer and no body end:", name)
            skipped += 1
            continue
        if len(samples) < 5:
            samples.append("%-22s %s + %s" % (name, being["name"], tool["name"]))
        if updated != source:
            if not args.dry_run:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(updated)
            written += 1

    if args.remove:
        print("lines removed on %d page(s), %d skipped" % (removed, skipped))
        return 0
    print("pages written: %d | skipped: %d | unchanged: %d"
          % (written, skipped, len(pages) - written - skipped))
    for line in samples:
        print("  ", line)
    if args.dry_run:
        print("dry run — nothing was written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
