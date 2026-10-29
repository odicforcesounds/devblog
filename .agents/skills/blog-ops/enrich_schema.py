#!/usr/bin/env python3
"""Upgrade the JSON-LD of every article to one @graph: BlogPosting + BreadcrumbList.

What it adds or normalises per page:

  image            ImageObject with the real width/height of the file it points at
  author           Person (not Organisation) with the site URL and the Mastodon profile
  publisher        Organisation with the brand image as logo
  articleSection   the category the page is listed under on index.html
  keywords         the page's own h2/h3 texts, cleaned and capped
  wordCount        words of visible text
  BreadcrumbList   Home › Category › Article, using the anchors on index.html

The rest of the head and the whole body are left byte for byte. Running it twice
changes nothing: the block is rebuilt from the fields it reads.

    python3 .agents/skills/blog-ops/enrich_schema.py --check   # report only
    python3 .agents/skills/blog-ops/enrich_schema.py           # write
"""

import html
import json
import os
import re
import sys

ORIGIN = "https://blog.odicforcesounds.com"
DOCS = "docs"
LOGO = ORIGIN + "/images/three.jpg"
LOGO_W, LOGO_H = 1024, 1024
DEFAULT_IMAGE = ORIGIN + "/images/peace.jpg"
AUTHOR_NAME = "Oscar"
AUTHOR_URL = ORIGIN + "/"
AUTHOR_SAME_AS = ["https://mastodon.social/@TaoExpression"]

# Pages that are interface, not articles: their JSON-LD is written by hand.
SKIP = {"404.html", "home.html"}

LD_RE = re.compile(r'<script type="application/ld\+json">[\s\S]*?</script>')


def image_size(url):
    """Width and height of a local image, read from its header."""
    path = os.path.join(DOCS, url.replace(ORIGIN + "/", "", 1))
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        head = fh.read(40)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            chunk = head[12:16]
            if chunk == b"VP8X":
                return (1 + int.from_bytes(head[24:27], "little"),
                        1 + int.from_bytes(head[27:30], "little"))
            if chunk == b"VP8L":
                bits = int.from_bytes(head[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            if chunk == b"VP8 " and head[23:26] == b"\x9d\x01\x2a":
                return (int.from_bytes(head[26:28], "little") & 0x3FFF,
                        int.from_bytes(head[28:30], "little") & 0x3FFF)
            return None
        if head[:2] == b"\xff\xd8":
            import struct
            fh.seek(2)
            while True:
                byte = fh.read(1)
                while byte and byte != b"\xff":
                    byte = fh.read(1)
                while byte == b"\xff":
                    byte = fh.read(1)
                if not byte:
                    return None
                marker = byte[0]
                length = struct.unpack(">H", fh.read(2))[0]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    data = fh.read(5)
                    height, width = struct.unpack(">HH", data[1:5])
                    return width, height
                fh.seek(length - 2, 1)
    return None


def slug(value):
    value = value.replace("&amp;", "and").replace("—", "-")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def categories():
    """page name -> (category title, anchor id) from the archive on index.html."""
    source = open(os.path.join(DOCS, "index.html"), encoding="utf-8").read()
    marks = list(re.finditer(r'<section class="category"[^>]*>', source))
    out = {}
    for i, mark in enumerate(marks):
        tag = mark.group(0)
        end = marks[i + 1].start() if i + 1 < len(marks) else len(source)
        title = html.unescape(re.search(r'data-title="([^"]*)"', tag).group(1))
        anchor = re.search(r'id="([^"]*)"', tag)
        for href in re.findall(r'href="\./([^"#?]+\.html)"', source[mark.start():end]):
            out.setdefault(href, (title, anchor.group(1) if anchor else None))
    return out


def visible_text(source):
    text = re.sub(r"<(script|style)\b[\s\S]*?</\1\s*>", " ", source, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html.unescape(text).split())


def keywords(source, limit=10):
    found = []
    for match in re.finditer(r"<h[23]\b[^>]*>([\s\S]*?)</h[23]\s*>", source, flags=re.I):
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", match.group(1))).split())
        text = re.sub(r"^\d+[.)]?\s*[—–-]?\s*", "", text)   # numbered section headings
        text = re.sub(r"\d+$", "", text).strip(" ·—-·")
        if not text or len(text) < 3 or len(text) > 40:
            continue
        if text.replace(" ", "").isdigit():
            continue
        if text.lower() in (f.lower() for f in found):
            continue
        found.append(text)
        if len(found) >= limit:
            break
    return ", ".join(found) if found else None


def image_node(url):
    size = image_size(url)
    node = {"@type": "ImageObject", "url": url}
    if size:
        node["width"], node["height"] = size
    return node


def build_article(page_url, source, section):
    name = os.path.basename(page_url)
    words = len(visible_text(source).split())
    node = {
        "@type": "BlogPosting",
        "@id": page_url + "#article",
        "headline": None,
        "name": None,
        "description": None,
        "url": page_url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "image": None,
        "inLanguage": None,
        "author": {
            "@type": "Person",
            "name": AUTHOR_NAME,
            "url": AUTHOR_URL,
            "sameAs": AUTHOR_SAME_AS,
        },
        "publisher": {
            "@type": "Organization",
            "name": "Monkey Blog",
            "url": ORIGIN + "/",
            "logo": {"@type": "ImageObject", "url": LOGO, "width": LOGO_W, "height": LOGO_H},
        },
        "isPartOf": {"@type": "Blog", "name": "Monkey Blog", "url": ORIGIN + "/"},
        "datePublished": None,
        "dateModified": None,
    }
    if section:
        node["articleSection"] = section[0]
    node["keywords"] = keywords(source)
    node["wordCount"] = words
    # present the descriptive fields before the dates
    for key in ("datePublished", "dateModified"):
        node[key] = node.pop(key)
    return node


def breadcrumb(page_url, section, title):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"}]
    if section and section[1]:
        items.append({
            "@type": "ListItem",
            "position": 2,
            "name": section[0],
            "item": "%s/#%s" % (ORIGIN, section[1]),
        })
    items.append({
        "@type": "ListItem",
        "position": len(items) + 1,
        "name": title or os.path.basename(page_url)[:-5],
        "item": page_url,
    })
    return {"@type": "BreadcrumbList", "itemListElement": items}


def rewrite(name, source, section):
    """Return the page with its JSON-LD block replaced, or the same text."""
    match = LD_RE.search(source)
    if not match:
        return source, False
    try:
        old = json.loads(match.group(0)[match.group(0).index(">") + 1:match.group(0).rindex("<")])
    except ValueError:
        return source, False

    if isinstance(old, dict) and isinstance(old.get("@graph"), list):
        nodes = old["@graph"]
        old = next((n for n in nodes if n.get("@type") == "BlogPosting"), nodes[0])
    if not isinstance(old, dict) or old.get("@type") != "BlogPosting":
        return source, False

    page_url = old.get("url") or (ORIGIN + "/" if name == "index.html" else "%s/%s" % (ORIGIN, name))
    node = build_article(page_url, source, section if name != "index.html" else None)
    if name == "index.html":
        node.pop("keywords", None)      # the archive page has category names, not keywords
    for key in ("headline", "name", "description", "inLanguage", "datePublished", "dateModified"):
        if old.get(key) is not None:
            node[key] = old[key]
    # The page's own og:image is the source of truth: it is assigned per page and
    # never rewritten here, so it survives repeated runs. Fall back to whatever the
    # JSON-LD already said, then to the site default.
    og = re.search(r'<meta property="og:image" content="([^"]+)"', source)
    raw_image = og.group(1) if og else None
    if not raw_image:
        raw_image = old.get("image")
        if isinstance(raw_image, dict):
            raw_image = raw_image.get("url")
    if not raw_image or not raw_image.startswith(ORIGIN + "/"):
        raw_image = DEFAULT_IMAGE
    node["image"] = image_node(raw_image)

    nodes = [node]
    if name != "index.html":
        # pages missing from the archive still get Home › Article
        title = node.get("headline") or node.get("name") or name[:-5]
        nodes.append(breadcrumb(page_url, section, title))

    graph = {"@context": "https://schema.org", "@graph": nodes}
    block = ('<script type="application/ld+json">\n'
             + json.dumps(graph, indent=2, ensure_ascii=False)
             + "\n  </script>")
    return source[:match.start()] + block + source[match.end():], True


def main(argv):
    check_only = "--check" in argv
    if not os.path.isdir(DOCS):
        print("run this from the repository root (no %s/ here)" % DOCS)
        return 2
    cats = categories()
    changed = skipped = touched = 0
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".html") or name in SKIP:
            continue
        path = os.path.join(DOCS, name)
        source = open(path, encoding="utf-8").read()
        new, ok = rewrite(name, source, cats.get(name))
        if not ok:
            skipped += 1
            continue
        if new == source:
            continue
        changed += 1
        if not check_only:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
        touched += 1
    print("%s: %d pages would change, %d without a BlogPosting block"
          % ("check" if check_only else "written", changed, skipped))
    return 1 if (check_only and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
