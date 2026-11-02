#!/usr/bin/env python3
"""Put one living being and one tool from the indexes on every page of the blog.

Every docs/*.html except index.html carries one card fixed to the left edge of
the window at mid height — the place the social dock takes on the front page:

    <aside class="living-panel" id="living-panel" ...>
      <img src="…/250px-…jpg" alt="European robin" width="56" height="56" loading="lazy">
      <p>this <a href="birdsIndex.html#order-passeriformes">European robin</a> likes to use
      <a href="awesomeIndex.html#cat-shell">Bash</a>.</p>
    </aside>

The being and its photograph come from the five catalogues under
docs/<kingdom>/data/, the tool from the shelves under docs/awesome/data/.
The pair written into the page is derived from the page name, so two runs give
the same site; the pool in docs/living-panel.js then replaces that pair with a
fresh one on every load (built by build_living.py, beside this file).

    python3 .agents/skills/living-panel/living_panel.py              # every page
    python3 .agents/skills/living-panel/living_panel.py --dry-run     # report only
    python3 .agents/skills/living-panel/living_panel.py --page docs/x.html
    python3 .agents/skills/living-panel/living_panel.py --remove      # take it out again
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
FRONT = "index.html"
CATALOGUES = (
    ("birds", "birdsIndex.html"),
    ("plants", "plantsIndex.html"),
    ("animals", "animalsIndex.html"),
    ("fishes", "fishesIndex.html"),
    ("insects", "insectsIndex.html"),
)
SEED = "2026-11-02"

STYLE_OPEN = '<style id="living-panel-style">'
CSS = """    .living-panel{position:fixed;top:50%;left:clamp(.7rem,1.6vw,1.2rem);z-index:95;
      transform:translateY(-50%);width:9.5rem;display:flex;flex-direction:column;
      align-items:center;gap:.45rem;margin:0;padding:.55rem .5rem;text-align:center;
      background:rgba(8,12,17,.9);border:1px solid var(--line, rgba(255,255,255,.14));
      border-radius:14px;-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
      font-family:var(--sans, system-ui, sans-serif)}
    .living-panel img{width:100%;height:5.6rem;object-fit:cover;border-radius:.5rem;
      border:1px solid var(--line, rgba(255,255,255,.14));background:var(--panel, #101018)}
    .living-panel p{margin:0;font-size:.7rem;line-height:1.45;color:var(--muted, #a9a9ba)}
    .living-panel a{color:var(--cyan, #5ce1ff);text-decoration:none;
      border-bottom:1px solid rgba(92,225,255,.4)}
    .living-panel a:hover,.living-panel a:focus-visible{color:var(--gold, #ffd23f);
      border-color:currentColor}
    @media (max-width:1200px){.living-panel{width:8.4rem;padding:.45rem}
      .living-panel img{height:4.8rem}.living-panel p{font-size:.66rem}}
    @media (max-width:900px){.living-panel{width:7rem;gap:.35rem}
      .living-panel img{height:4rem}.living-panel p{font-size:.62rem;line-height:1.4}}
    @media (max-width:640px){.living-panel{width:5.8rem;padding:.35rem .3rem}
      .living-panel img{height:3.2rem}.living-panel p{font-size:.56rem}}
    @media print{.living-panel{display:none}}
"""

STYLE = re.compile(r"\n?[ \t]*" + re.escape(STYLE_OPEN) + r".*?</style>", re.S)
PANEL = re.compile(r"\n?[ \t]*<aside class=\"living-panel\".*?</aside>", re.S)
OLD_FOOTER = re.compile(r"\n?[ \t]*<p class=\"small living-link\">.*?</p>", re.S)
OLD_TOP = re.compile(r"\n?[ \t]*<aside class=\"living-top\".*?</aside>", re.S)
OLD_STYLE = re.compile(r"\n?[ \t]*<style id=\"living-top-style\">.*?</style>", re.S)
OLD_BOX = re.compile(r"\n?[ \t]*<aside class=\"living-box\" id=\"living-box\".*?</aside>", re.S)
OLD_BOX_STYLE = re.compile(r"\n?[ \t]*<style id=\"living-box-style\">.*?</style>", re.S)
SCRIPT = re.compile(r"\n?[ \t]*<script src=\"/?living-panel\.js\"[^>]*></script>", re.I)
OLD = (STYLE, PANEL, OLD_FOOTER, OLD_TOP, OLD_STYLE, OLD_BOX_STYLE, OLD_BOX, SCRIPT)

IMAGE_HOST = "https://upload.wikimedia.org"
CSP = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(")', re.I)
IMG_SRC = re.compile(r"img-src[^;]*", re.I)


def esc(text):
    return html.escape(text, quote=True)


def beings():
    found = []
    for folder, page in CATALOGUES:
        for path in sorted(glob.glob(os.path.join(DOCS, folder, "data", "*.json"))):
            if path.endswith("index.json"):
                continue
            try:
                with open(path, encoding="utf-8") as handle:
                    data = json.load(handle)
            except Exception:
                continue
            key = data.get("key") or os.path.splitext(os.path.basename(path))[0]
            for family in data.get("families", []):
                for being in family.get("s", []):
                    name = (being.get("n") or "").strip()
                    image = being.get("i") or ""
                    if not name or not image or len(name) > 28:
                        continue
                    found.append({"name": name, "page": page,
                                  "href": "%s#order-%s" % (page, key),
                                  "image": image})
    return found


def tools():
    boring = re.compile(r"cheat|sheet|book|knowledge|awesome|lists?\b|resources?|\bapps\b|"
                        r"\btools\b|community|tutorial|guide|course|news|blog|misc|article|"
                        r"collection|top\b|\bbest\b|free|open source|\bpdf\b|\bhtml\b|\bcss\b|"
                        r"\bjson\b|\bxml\b|\byaml\b|\bcsv\b|\bsvg\b|\bhttp\b|\bapi\b|\bide\b|"
                        r"\bios\b|\bos\b|testing|framework|librar|language|style|design|"
                        r"icons?|fonts?|images?|videos?|audio|papers?|books?|games?|"
                        r"editors?|extensions?|music|investing|blockchain|crypto|forensic|"
                        r"scalab|microservice|serverless|sysadmin|pentest|\bctf\b|\bwaf\b|"
                        r"privacy|learning|education|career|health|financ|marketing", re.I)
    tool_name = re.compile(r"^[A-Za-z][\w.+#-]{1,15}$")
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
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue
        key = data.get("key") or os.path.splitext(os.path.basename(path))[0]
        title = data.get("title") or key
        for listing in data.get("lists", []):
            list_name = (listing.get("n") or "").strip()
            chosen = None
            if list_name.lower() in code_list:
                chosen = list_name
            else:
                options = []
                for drawer in listing.get("d", []):
                    for entry in drawer.get("c", []):
                        name = (entry.get("n") or "").strip()
                        if not tool_name.match(name) or boring.search(name):
                            continue
                        if "github.com" not in (entry.get("u") or ""):
                            continue
                        options.append(name)
                if options:
                    digest = hashlib.sha256((key + "/" + list_name).encode()).hexdigest()
                    chosen = options[int(digest[:8], 16) % len(options)]
                elif tool_name.match(list_name) and not boring.search(list_name):
                    chosen = list_name
            if chosen:
                found.append({"name": chosen, "list": list_name, "key": key, "title": title})
    return found


def links_in(source):
    return set(re.findall(r'href="([^"]+)"', source))


def pick_being(rng, pool, taken):
    free = [item for item in pool if item["href"] not in taken]
    if not free:
        return rng.choice(pool), False
    return rng.choice(free), True


def pick_tool(rng, pool, taken):
    by_category = {}
    for item in pool:
        if "awesomeIndex.html#cat-" + item["key"] not in taken:
            by_category.setdefault(item["key"], []).append(item)
    if not by_category:
        return rng.choice(pool)
    category = rng.choice(sorted(by_category))
    return rng.choice(by_category[category])


def thumb(url):
    return re.sub(r"/500px-", "/250px-", url, count=1)


def clean(source):
    for pattern in OLD:
        source = pattern.sub("", source)
    return source


def allow_images(source):
    """Let the panel's photograph load under the page's own policy.

    The being's picture is served by Wikimedia, the same host the five catalogues
    already use. A page whose `img-src` does not name it would show a broken
    image, so the host is added to that directive and to nothing else.
    """

    def fix(match):
        policy = match.group(2)
        if IMAGE_HOST in policy or not policy.strip() or policy.strip() == "...":
            return match.group(0)
        if IMG_SRC.search(policy):
            policy = IMG_SRC.sub(lambda m: m.group(0) + " " + IMAGE_HOST, policy, count=1)
        elif policy.rstrip().endswith(";"):
            policy = policy.rstrip() + " img-src 'self' data: %s;" % IMAGE_HOST
        else:
            policy = policy.rstrip() + "; img-src 'self' data: %s" % IMAGE_HOST
        return match.group(1) + policy + match.group(3)

    return CSP.sub(fix, source)


def panel(being, tool, link_being):
    who = ('<a href="%s">%s</a>' % (esc(being["href"]), esc(being["name"]))
           if link_being else esc(being["name"]))
    line = ('this %s likes to use <a href="awesomeIndex.html#cat-%s" title="%s · %s">%s</a>.'
            % (who, esc(tool["key"]), esc(tool["list"]), esc(tool["title"]),
               esc(tool["name"])))
    return ('<aside class="living-panel" id="living-panel" aria-label="A living being and a tool">\n'
            '    <img src="%s" alt="%s" width="152" height="90" loading="lazy" decoding="async">\n'
            '    <p>%s</p>\n  </aside>'
            % (esc(thumb(being["image"])), esc(being["name"]), line))


def main(argv=None):
    parser = argparse.ArgumentParser(description="A living being and a tool on every page.")
    parser.add_argument("--page", action="append", default=[], help="only this page (repeatable)")
    parser.add_argument("--remove", action="store_true", help="take the block out again")
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    pages = args.page or sorted(glob.glob(os.path.join(DOCS, "*.html")))
    being_pool = beings()
    tool_pool = tools()
    if not being_pool or not tool_pool:
        print("no beings or no tools found — nothing to do", file=sys.stderr)
        return 1
    print("beings: %d | tools: %d" % (len(being_pool), len(tool_pool)))

    written = removed = skipped = 0
    samples = []
    for path in pages:
        name = os.path.basename(path)
        if name == FRONT or not os.path.exists(path):
            skipped += 1
            continue
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        if args.remove:
            updated = clean(source)
            if updated != source:
                if not args.dry_run:
                    with open(path, "w", encoding="utf-8") as handle:
                        handle.write(updated)
                removed += 1
            else:
                skipped += 1
            continue

        body = clean(source)
        taken = links_in(body)
        rng = random.Random(hashlib.sha256((name + "|" + SEED).encode()).hexdigest())
        being, link_being = pick_being(rng, being_pool, taken)
        tool = pick_tool(rng, tool_pool, taken)
        block = panel(being, tool, link_being)

        styled = allow_images(body)
        if "</head>" in styled:
            style = "  %s\n%s  </style>\n" % (STYLE_OPEN, CSS)
            src = "/living-panel.js" if name == "404.html" else "living-panel.js"
            script = '  <script src="%s" defer></script>\n' % src
            styled = styled.replace("</head>", style + script + "</head>", 1)
        match = re.search(r"<body[^>]*>", styled, re.I)
        if match is None:
            print("  ! no body tag:", name)
            skipped += 1
            continue
        index = match.end()
        updated = styled[:index] + "\n" + block + styled[index:]
        if len(samples) < 5:
            samples.append("%-26s %s + %s" % (name, being["name"], tool["name"]))
        if updated != source:
            if not args.dry_run:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(updated)
            written += 1

    if args.remove:
        print("blocks removed: %d | skipped: %d" % (removed, skipped))
        return 0
    print("pages written: %d | skipped: %d | unchanged: %d"
          % (written, skipped, len(pages) - written - skipped))
    for line in samples:
        print("  ", line)
    if args.dry_run:
        print("dry run — nothing was written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
