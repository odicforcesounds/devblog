#!/usr/bin/env python3
"""Build the English tool pages: every linked tool from the 113 awesome lists.

One page per subject, split when a subject exceeds ~2,500 tools. Output is
docs/awesome-tools-*.html, linked from docs/awesomeIndex.html.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import html
import json
import re
import sys
from urllib.parse import urlparse

DATA = "tmp/tools.json"
HUB = "docs/awesomeIndex.html"
ORIGIN = "https://blog.odicforcesounds.com"
IMG = ORIGIN + "/images/peace.jpg"
CAP = 2500

LABEL = {
    "shell": "Shell",
    "lang": "Languages",
    "systems": "Systems",
    "data": "Data",
    "security": "Security",
    "ai": "AI",
    "web": "Web",
    "learning": "Learning",
    "beyond": "Beyond",
}
BLURB = {
    "shell": "Editors, prompts, one-liners and terminal applications — every one of them linked here with the sentence its own list wrote about it.",
    "lang": "Libraries, frameworks and tooling for each language, straight from the lists that curate them. No summaries, no opinions: the name, the link, the line.",
    "systems": "Containers, servers, self-hosted software and the utilities that keep machines alive.",
    "data": "Bytes in motion and at rest: crawlers, storage, packets, ledgers and the analysis that follows them.",
    "security": "The long shelf: recon, exploitation, defence, malware, privacy. Everything the lists point at, by list.",
    "ai": "Models, agents, workflows — the plumbing of the last few years.",
    "web": "CSS, design systems, front-end tooling and the guidelines that keep a codebase readable.",
    "learning": "Courses, interviews, newsletters, streams and the resources students actually use.",
    "beyond": "Food, music, money, health and games: the lists that have nothing to do with work.",
}


def esc(t):
    return html.escape(t, quote=True) if t else ""


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


SEEN = {}


def dedupe(key):
    """One href per destination: a tool linked by two lists is listed once."""
    seen = set()
    for item in data[key]:
        kept = []
        for tool in item["tools"]:
            u = tool["url"].rstrip("/")
            if u in seen:
                continue
            seen.add(u)
            kept.append(tool)
        item["tools"] = kept
    SEEN[key] = seen


def chunks(groups, key):
    lists = [item for item in data[key] if item["tools"]]
    out, cur, size = [], [], 0
    for item in lists:
        n = len(item["tools"])
        if cur and size + n > CAP:
            out.append(cur)
            cur, size = [], 0
        cur.append(item)
        size += n
    if cur:
        out.append(cur)
    return out


def description(label, total, part, parts):
    base = ("Every tool in the %s awesome lists on this blog — %d links, each with the "
            "description its own list gave it. Page %d of %d." % (label.lower(), total, part, parts))
    if not 110 <= len(base) <= 155:
        base = ("All %d tools curated by the %s awesome lists collected on this blog, with their "
                "own one-line descriptions and links. Part %d of %d."
                % (total, label.lower(), part, parts))
    if not 110 <= len(base) <= 155:
        sys.exit("description %d chars for %s %d/%d: %r" % (len(base), label, part, parts, base))
    return base


def page_html(key, part, parts, items, filename, prev_name, next_name):
    label = LABEL[key]
    total = sum(len(i["tools"]) for i in items)
    title = "Awesome Tools — %s%s" % (label, "" if parts == 1 else " (%d/%d)" % (part, parts))
    desc = description(label, total, part, parts)

    body, words, toc = [], 0, []
    for item in items:
        anchor = "l-" + slug(item["list"])[:40]
        toc.append('<a href="#%s">%s<span>%d</span></a>' % (anchor, esc(item["list"]), len(item["tools"])))
        rows = []
        for tool in item["tools"]:
            host = urlparse(tool["url"]).netloc.replace("www.", "")
            d = ('<span class="d">%s</span>' % esc(tool["desc"])) if tool["desc"] else ""
            rows.append('<li><a href="%s" target="_blank" rel="noopener noreferrer">%s</a>'
                        '<span class="host">%s</span>%s</li>'
                        % (esc(tool["url"]), esc(tool["name"]), esc(host), d))
            words += len((tool["name"] + " " + tool["desc"]).split())
        # The list's own repository is usually one of its own entries; the card
        # already carries that link, so the "from" line is left out then.
        from_line = ""
        if item["url"].rstrip("/") not in SEEN[key]:
            from_line = ('<p class="from">from <a href="%s" target="_blank" '
                         'rel="noopener noreferrer">%s</a></p>'
                         % (esc(item["url"]), esc(item["repo"])))
        body.append("""
    <section class="src" id="%s">
      <h2>%s<span class="count">%d tools</span></h2>
      %s
      <ul class="tools">
%s
      </ul>
    </section>""" % (anchor, esc(item["list"]), len(item["tools"]), from_line,
                       "\n".join(rows)))

    keywords = ", ".join(i["list"] for i in items)
    pager = []
    if prev_name:
        pager.insert(0, '<a href="%s">← Previous</a>' % prev_name)
    if next_name:
        pager.append('<a href="%s">Next →</a>' % next_name)

    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; style-src 'unsafe-inline'">
<meta name="X-Content-Type-Options" content="nosniff">
<meta name="X-Frame-Options" content="DENY">
<meta name="Referrer-Policy" content="no-referrer">
<title>%(title)s | Monkey Blog</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(origin)s/%(file)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="article">
<meta property="og:url" content="%(origin)s/%(file)s">
<meta property="og:site_name" content="Monkey Blog">
<meta property="og:image" content="%(img)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(img)s">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "%(origin)s/%(file)s#article",
      "headline": "%(title)s",
      "name": "%(title)s",
      "description": "%(desc)s",
      "url": "%(origin)s/%(file)s",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "%(origin)s/%(file)s"
      },
      "image": {
        "@type": "ImageObject",
        "url": "%(img)s",
        "width": 1496,
        "height": 960
      },
      "inLanguage": "en",
      "author": {
        "@type": "Person",
        "name": "Oscar",
        "url": "https://blog.odicforcesounds.com/",
        "sameAs": ["https://mastodon.social/@TaoExpression"]
      },
      "publisher": {
        "@type": "Organization",
        "name": "Monkey Blog",
        "url": "https://blog.odicforcesounds.com/",
        "logo": {
          "@type": "ImageObject",
          "url": "https://blog.odicforcesounds.com/images/three.jpg",
          "width": 1024,
          "height": 1024
        }
      },
      "isPartOf": {
        "@type": "Blog",
        "name": "Monkey Blog",
        "url": "https://blog.odicforcesounds.com/"
      },
      "articleSection": "Programming & Development",
      "keywords": "%(keywords)s",
      "wordCount": %(words)d,
      "datePublished": "2026-11-02",
      "dateModified": "2026-11-02"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://blog.odicforcesounds.com/"},
        {"@type": "ListItem", "position": 2, "name": "Programming & Development", "item": "https://blog.odicforcesounds.com/#category-programming-and-development"},
        {"@type": "ListItem", "position": 3, "name": "%(title)s", "item": "%(origin)s/%(file)s"}
      ]
    }
  ]
}
</script>
<style>
:root{--bg:#070b10;--ink:#e9f0f7;--dim:#a9b7c6;--muted:#7d8d9f;--line:rgba(126,163,196,.15);
--line-2:rgba(126,163,196,.32);--accent:#54e3c4;--sans:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px;-webkit-text-size-adjust:100%}
body{margin:0;color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.6;
background:radial-gradient(60rem 38rem at 50% -14%,rgba(84,227,196,.07),transparent 62%),var(--bg)}
.topbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;
max-width:1080px;margin:0 auto;padding:18px 20px 14px;border-bottom:1px solid var(--line)}
.brand{font-family:var(--mono);font-size:13px;color:var(--accent);text-decoration:none}
.note{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
main{max-width:1080px;margin:0 auto;padding:30px 20px 90px}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}
h1{margin:0 0 12px;font-size:clamp(1.9rem,5vw,2.9rem);line-height:1.07;letter-spacing:-.02em}
.lede{margin:0 0 16px;max-width:74ch;color:var(--dim)}
.pager{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 4px}
.pager a{font-family:var(--mono);font-size:11.5px;padding:6px 11px;border:1px solid var(--line-2);
border-radius:999px;color:var(--dim);text-decoration:none}
.pager a:hover{color:var(--accent);border-color:rgba(84,227,196,.5)}
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 8px}
.toc a{font-size:12px;padding:4px 9px;border:1px solid var(--line);border-radius:6px;color:var(--dim);text-decoration:none}
.toc a span{font-family:var(--mono);font-size:10px;color:var(--muted);margin-left:5px}
.toc a:hover{color:var(--accent);border-color:rgba(84,227,196,.4)}
.src{margin:44px 0 0;padding-top:18px;border-top:1px solid var(--line)}
.src h2{display:flex;align-items:baseline;gap:10px;margin:0 0 4px;font-size:1.25rem;letter-spacing:-.01em}
.src h2 .count{margin-left:auto;font-family:var(--mono);font-size:.62em;color:var(--muted)}
.from{margin:0 0 14px;font-family:var(--mono);font-size:11px;color:var(--muted)}
.from a{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--line-2)}
.from a:hover{color:var(--accent)}
ul.tools{list-style:none;margin:0;padding:0;display:grid;gap:0}
ul.tools li{padding:9px 2px;border-bottom:1px solid var(--line);font-size:14.5px}
ul.tools li a{color:var(--ink);text-decoration:none;font-weight:600;border-bottom:1px solid rgba(84,227,196,.3)}
ul.tools li a:hover{color:var(--accent)}
.host{font-family:var(--mono);font-size:10.5px;color:var(--muted);margin-left:8px;white-space:nowrap}
.d{display:block;color:var(--dim);font-size:13.5px;margin-top:2px}
.page-foot{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
.page-foot a{color:var(--accent)}
@media print{.topbar,.pager,.toc{display:none}body{background:#fff;color:#111}ul.tools li a{color:#111}}
</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="awesomeIndex.html">◀ Awesome Index</a>
  <span class="note">%(label)s · %(total)d tools%(partnote)s</span>
</header>
<main>
  <p class="kicker">Awesome tools · %(label_lower)s</p>
  <h1>%(label)s</h1>
  <p class="lede">%(blurb)s</p>
  <nav class="pager" aria-label="Pages">%(pager)s</nav>
  <nav class="toc" aria-label="Lists on this page">%(toc)s</nav>
%(body)s
  <footer class="page-foot">
    <p>%(total)d tools from %(nlists)d lists, taken from the public README of each list. Links open in a new tab; nothing is fetched when this page loads.</p>
    <p><a href="awesome_story.html">the story behind these lists</a></p>
  </footer>
</main>
</body>
</html>
"""
    # CSS keeps real percent signs, so fill the template by token rather than %-formatting
    mapping = {
        "title": esc(title), "desc": esc(desc), "origin": ORIGIN, "file": filename, "img": IMG,
        "keywords": esc(keywords), "words": max(words, 1), "label": esc(label),
        "label_lower": esc(label.lower()), "blurb": esc(BLURB[key]), "pager": " ".join(pager),
        "toc": "\n    ".join(toc), "body": "".join(body), "total": total, "nlists": len(items),
        "partnote": "" if parts == 1 else " · page %d of %d" % (part, parts),
    }
    for k, v in mapping.items():
        doc = doc.replace("%(" + k + ")s", str(v)).replace("%(" + k + ")d", str(v))
    open("docs/" + filename, "w", encoding="utf-8").write(doc)
    return filename, title, total


def main():
    global data
    data = json.load(open(DATA, encoding="utf-8"))
    made = {}
    for key in LABEL:
        dedupe(key)
        parts = chunks(None, key)
        files = []
        for i, items in enumerate(parts, 1):
            name = "awesome-tools-%s%s.html" % (key, "" if len(parts) == 1 else "-%d" % i)
            files.append(name)
        prev = None
        for i, items in enumerate(parts, 1):
            name = files[i - 1]
            nxt = files[i] if i < len(files) else None
            filename, title, total = page_html(key, i, len(parts), items, name, prev, nxt)
            made[key] = made.get(key, [])
            made[key].append((filename, title, total))
            prev = name
        print("%-9s %d page(s) %s" % (key, len(parts), [f for f, _, _ in made[key]]))

    # The hub already links each shelf once, through its deep page; these flat
    # pages are reached from there, so nothing is injected here. A second nav
    # on the hub would list the same nine subjects twice.
    print("%d flat tool pages, reachable from their deep page" % sum(len(v) for v in made.values()))


if __name__ == "__main__":
    main()
