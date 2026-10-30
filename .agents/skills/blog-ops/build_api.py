#!/usr/bin/env python3
"""Build the static API for the blog.

Reads every docs/*.html, writes:

  docs/api/index.json      metadata for all articles + chunk manifest
  docs/api/text/NNN.json   article text, split into fetch-on-demand chunks

Everything is plain JSON served as files: no server, no database, no third
party. Run it after adding or editing an article, from the repository root:

    python3 .agents/skills/blog-ops/build_api.py
"""

import glob
import html
import json
import os
import re
import subprocess
import sys
import datetime

DOCS = "docs"
OUT = os.path.join(DOCS, "api")
ORIGIN = "https://blog.odicforcesounds.com"
TEXT_CAP = 20000          # characters kept per article
CHUNK_BYTES = 240000      # rough raw size of one text chunk
DATE_CACHE = "tmp/seo/dates-v2.json"

# A page copied or renamed after it was published appears in git as newly added
# on the copy day. These keep the instant the article itself first went up.
PUBLISHED_OVERRIDES = {"OneHumanSong.html": "2026-10-16T22:49:01+01:00"}

NOISE = re.compile(
    r"<(script|style|nav|footer|aside|iframe|figure|form|template)\b.*?</\1\s*>",
    re.I | re.S,
)


def clean_text(fragment):
    text = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return " ".join(text.split())


def body_text(source):
    start = re.search(r"<body[^>]*>", source, re.I)
    body = NOISE.sub(" ", source[start.end():] if start else source)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    return clean_text(body)


def title_of(source):
    m = re.search(r"<title[^>]*>(.*?)</title>", source, re.S | re.I)
    return clean_text(m.group(1)) if m else ""


def meta(source, key):
    m = re.search(r'<meta\s+(?:name|property)="%s"\s+content="([^"]*)"' % re.escape(key),
                  source, re.I)
    return html.unescape(m.group(1)) if m else ""


def headings(source, tag, limit):
    out = []
    for m in re.finditer(r"<%s\b[^>]*>(.*?)</%s\s*>" % (tag, tag), source, re.S | re.I):
        text = clean_text(m.group(1))
        if 2 <= len(text) <= 120:
            out.append(text)
        if len(out) >= limit:
            break
    return out


def lang_of(source):
    m = re.search(r"<html\b[^>]*>", source, re.I)
    if not m:
        return "en"
    a = re.search(r'lang="([^"]*)"', m.group(0), re.I)
    return (a.group(1) if a else "en") or "en"


def page_dates(path):
    """Dates for a page git does not know yet: its own JSON-LD, then mtime."""
    candidate = path if os.path.exists(path) else os.path.join(DOCS, os.path.basename(path))
    try:
        with open(candidate, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        return "", ""
    try:
        stamp = datetime.date.fromtimestamp(os.path.getmtime(candidate)).isoformat()
    except OSError:
        stamp = ""
    pub = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', source)
    mod = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})', source)
    published = pub.group(1) if pub else stamp
    modified = mod.group(1) if mod else published
    return published, modified


def apply_overrides(dates):
    for name, published in PUBLISHED_OVERRIDES.items():
        entry = dates.get(os.path.join(DOCS, name))
        if entry:
            entry["published"] = published[:10]
            entry["published_at"] = published
    return dates


def git_dates(paths):
    cached = {}
    if os.path.exists(DATE_CACHE):
        with open(DATE_CACHE, encoding="utf-8") as fh:
            cached = json.load(fh)
    if all(cached.get(p, {}).get("published_at") for p in paths):
        return apply_overrides(cached)

    out = {}
    for path in paths:
        def one(args):
            try:
                r = subprocess.run(["git", "log"] + args + ["--", path],
                                   capture_output=True, text=True, check=True).stdout
            except subprocess.CalledProcessError:
                return ""
            lines = [l.strip() for l in r.splitlines() if l.strip()]
            return lines[-1] if lines else ""
        published_at = one(["--diff-filter=A", "--format=%aI"])
        modified_at = one(["-1", "--format=%aI"])
        if not published_at or not modified_at:
            fallback_pub, fallback_mod = page_dates(path)
            published_at = published_at or (fallback_pub + "T00:00:00Z" if fallback_pub else "")
            modified_at = modified_at or (fallback_mod + "T00:00:00Z" if fallback_mod else published_at)
        out[path] = {
            "published": published_at[:10],
            "modified": modified_at[:10],
            "published_at": published_at,
            "modified_at": modified_at,
        }
    os.makedirs(os.path.dirname(DATE_CACHE), exist_ok=True)
    with open(DATE_CACHE, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return apply_overrides(out)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(raw)
    return len(raw.encode("utf-8"))


# Pages that are part of the interface rather than the archive: browse.html is the
# browser built on top of this same JSON (listing it would point at itself), and
# 404.html is the error page the host serves for missing paths.
SKIP = {"browse.html", "404.html", "home.html"}


def main():
    paths = [
        p
        for p in sorted(glob.glob(os.path.join(DOCS, "*.html")))
        if os.path.basename(p) not in SKIP
    ]
    dates = git_dates(paths)

    articles = []
    texts = {}
    for path in paths:
        name = os.path.basename(path)
        slug = "" if name == "index.html" else name[:-5]
        with open(path, encoding="utf-8") as fh:
            source = fh.read()

        title = title_of(source) or slug
        if slug == "":
            # the home page lists the whole archive; its own prose is short
            text = meta(source, "description")
        else:
            text = body_text(source)

        truncated = len(text) > TEXT_CAP
        if truncated:
            text = text[:TEXT_CAP]

        d = dates.get(path, {})
        articles.append({
            "slug": slug,
            "url": (ORIGIN + "/" if slug == "" else "%s/%s.html" % (ORIGIN, slug)),
            "path": "index.html" if slug == "" else name,
            "title": title,
            "description": meta(source, "description"),
            "lang": lang_of(source),
            "published": d.get("published", ""),
            "modified": d.get("modified", ""),
            "published_at": d.get("published_at", ""),
            "modified_at": d.get("modified_at", ""),
            "h1": (headings(source, "h1", 1) or [""])[0],
            "headings": headings(source, "h2", 10) + headings(source, "h3", 6),
            "words": len(text.split()),
            "chars": len(text),
            "truncated": truncated,
        })
        if slug:
            texts[slug] = text

    for a in articles:  # cached dates may be full ISO timestamps
        a["published"] = a["published"][:10]
        a["modified"] = a["modified"][:10]

    articles.sort(key=lambda a: a["url"])

    # pack the texts into size-balanced chunks, in a stable order
    os.makedirs(os.path.join(OUT, "text"), exist_ok=True)
    chunks, current, size = [], {}, 0
    for slug in sorted(texts):
        piece = len(json.dumps({slug: texts[slug]}, ensure_ascii=False).encode("utf-8"))
        if current and size + piece > CHUNK_BYTES:
            chunks.append(current)
            current, size = {}, 0
        current[slug] = texts[slug]
        size += piece
    if current:
        chunks.append(current)

    manifest = []
    total = 0
    for i, data in enumerate(chunks):
        rel = "text/%03d.json" % i
        written = write_json(os.path.join(OUT, rel), data)
        total += written
        manifest.append({"file": rel, "count": len(data), "bytes": written})

    languages = sorted({a["lang"] for a in articles})
    years = sorted({a["published"][:4] for a in articles if a["published"]}, reverse=True)

    index_bytes = write_json(os.path.join(OUT, "index.json"), {
        "generated": max(a["modified"] for a in articles if a["modified"]),
        "origin": ORIGIN,
        "count": len(articles),
        "languages": languages,
        "years": years,
        "chunks": manifest,
        "articles": articles,
    })

    print("articles %d | languages %d | years %s..%s" %
          (len(articles), len(languages), years[-1], years[0]))
    print("index.json %.1f KB | %d text chunks %.1f KB" %
          (index_bytes / 1024, len(manifest), total / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
