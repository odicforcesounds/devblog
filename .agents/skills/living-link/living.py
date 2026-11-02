#!/usr/bin/env python3
"""Put one random living being and one random tool on every page of the blog.

The line reads:

    this <a href="birdsIndex.html">European robin</a> likes to code with
    <a href="awesomeIndex.html#cat-shell" title="Bash · Shell, terminal and
    one-liners">shellcheck</a>.

Beings come from the five catalogue indexes under docs/<kingdom>/data/; tools come
from docs/awesome/data/, and the link points at the category the tool sits in, so
a click lands on the drawer of the Awesome Index that holds it.

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
SNIPPET = re.compile(r'\n?[ \t]*<p class="small living-link">.*?</p>', re.S)
CLASS = 'class="small living-link"'


def esc(text):
    return html.escape(text, quote=True)


def beings():
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
                    if not name or len(name) > 28:
                        continue
                    # Straight to the order the being sits in, inside its catalogue.
                    found.append({"name": name, "page": page,
                                  "href": "%s#order-%s" % (page, data.get("key", ""))})
    return found


def tools():
    """Tool names from the Awesome Index, with the category that holds them.

    A list is often named after the tool itself (Bash, Go, Docker), which reads best
    in the sentence, so the list name is used when it looks like one. Otherwise the
    first short, real tool name in that list stands in.
    """
    boring = re.compile(r"cheat|sheet|book|knowledge|awesome|lists?\b|resources?|\bapps\b|\btools\b|"
                        r"community|tutorial|guide|course|news|blog|misc|article|collection|top\b|"
                        r"\bbest\b|free|open source|\bpdf\b|\bhtml\b|\bcss\b|\bjson\b|\bxml\b|"
                        r"\byaml\b|\bcsv\b|\bsvg\b|\bhttp\b|\bapi\b|\bide\b|\bios\b|\bos\b|"
                        r"testing|framework|librar|language|style|design|icons?|fonts?|images?|"
                        r"videos?|audio|papers?|books?|games?|editors?|extensions?|music|"
                        r"investing|blockchain|crypto|forensic|scalab|microservice|serverless|"
                        r"sysadmin|pentest|\bctf\b|\bwaf\b|privacy|learning|education|career|"
                        r"health|financ|marketing|awesome", re.I)
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
    """The one line the page carries."""
    if link_being:
        who = '<a href="%s">%s</a>' % (esc(being["href"]), esc(being["name"]))
    else:
        who = esc(being["name"])
    line = ('  <p class="small living-link">this %s likes to code with '
            '<a href="awesomeIndex.html#cat-%s" title="%s · %s">%s</a>'
            % (who, esc(tool["key"]), esc(tool["list"]), esc(tool["title"]),
               esc(tool["name"])))
    if guide:
        line += (', and this site has a <a href="%s">%s guide</a>'
                 % (esc(guide[0]), esc(guide[1])))
    return line + ".</p>"


def links_in(source):
    return set(re.findall(r'href="([^"]+)"', source))


def place(source, block):
    """Put the line at the end of the page footer, or before </body> if there is none."""
    index = source.rfind("</footer>")
    if index != -1:
        return source[:index] + block + "\n" + source[index:]
    index = source.rfind("</body>")
    if index != -1:
        return source[:index] + block + "\n" + source[index:]
    return None


def pick(rng, items, taken):
    """Random pick that does not repeat a link the page already carries."""
    free = [item for item in items if (item.get("href") or "") not in taken]
    if not free:
        return rng.choice(items), False
    return rng.choice(free), True


def rewrite(source, rng, being_pool, tool_pool, guide_pool, page):
    clean = SNIPPET.sub("", source)
    taken = links_in(clean)
    being, link_being = pick(rng, being_pool, taken)
    # One category first, then one tool inside it: the drawers hold very different
    # numbers of lists, and picking flat would drown the page in the biggest one.
    by_category = {}
    for tool in tool_pool:
        if "awesomeIndex.html#cat-" + tool["key"] in taken:
            continue
        by_category.setdefault(tool["key"], []).append(tool)
    if by_category:
        category = rng.choice(sorted(by_category))
        tool = rng.choice(by_category[category])
    else:
        tool = rng.choice(tool_pool)
    # A page of this blog that expands on the tool, if one exists and is not
    # already linked here (and is not this page itself).
    guide = None
    for word in (tool["name"], tool["list"]):
        for candidate in guide_pool.get(word.lower(), []):
            if candidate != page and candidate not in taken:
                guide = (candidate, word)
                break
        if guide:
            break
    block = sentence(being, tool, link_being, guide)
    updated = place(clean, block)
    if updated is None:
        return None, being, tool
    return updated, being, tool


def main(argv=None):
    parser = argparse.ArgumentParser(description="A random living being and tool on every page.")
    parser.add_argument("--seed", default="", help="change it to reshuffle every page")
    parser.add_argument("--page", action="append", default=[], help="only this page (repeatable)")
    parser.add_argument("--remove", action="store_true", help="take the line out again")
    parser.add_argument("--dry-run", action="store_true", help="print, do not write")
    args = parser.parse_args(argv)

    being_pool = beings()
    tool_pool = tools()
    guide_pool = guides()
    if not being_pool or not tool_pool:
        print("no beings or no tools found — nothing to do", file=sys.stderr)
        return 1
    print("beings: %d | tools: %d" % (len(being_pool), len(tool_pool)))

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
            cleaned = SNIPPET.sub("", source)
            if cleaned != source:
                if not args.dry_run:
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(cleaned)
                removed += 1
            continue
        rng = random.Random(hashlib.sha256((name + "|" + args.seed).encode()).hexdigest())
        updated, being, tool = rewrite(source, rng, being_pool, tool_pool, guide_pool, name)
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
