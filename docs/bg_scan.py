import os, re, json, html
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

os.chdir("/home/om/devblog/docs")

def clean(s):
    if not s: return ""
    return html.unescape(re.sub(r"\s+", " ", s)).strip()

def first_nonempty(pattern):
    def grab(t):
        for m in re.finditer(pattern, t, re.I):
            val = clean(m.group(1))
            if val.strip(): return val
        return ""
    return grab

NAME_DESC = first_nonempty(r'<meta\s+name="description"\s+content="([^"]*)"')
OG_DESC = first_nonempty(r'<meta\s+property="og:description"\s+content="([^"]*)"')
TW_DESC = first_nonempty(r'<meta\s[^>]*(?:name|property)="twitter:description"\s+content="([^"]*)"')
OG_TITLE = first_nonempty(r'<meta\s+property="og:title"\s+content="([^"]*)"')
OG_URL = first_nonempty(r'<meta\s+property="og:url"\s+content="([^"]*)"')
OG_IMAGE = first_nonempty(r'<meta\s+property="og:image"\s+content="([^"]*)"')
TW_IMAGE = first_nonempty(r'<meta\s[^>]*(?:name|property)="twitter:image"\s+content="([^"]*)"')
CANON = first_nonempty(r'<link\s+rel="canonical"\s+href="([^"]*)"')
TW_CARD = first_nonempty(r'<meta\s+name="twitter:card"\s+content="([^"]*)"')
PUB = first_nonempty(r'<meta\s+property="article:published_time"\s+content="([^"]*)"')
LANG = first_nonempty(r'<html[^>]+lang="([^"]+)"')

INDEX_DATES = {}
try:
    idx = json.loads(Path("/home/om/devblog/docs/index.html").read_text(encoding="utf-8"))
    for k, v in idx.items():
        try:
            dtp = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            if dtp.tzinfo is None: dtp = dtp.replace(tzinfo=timezone.utc)
            INDEX_DATES[k] = dtp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception: pass
except Exception: pass

META_JSON_DATES = {}
try:
    meta = json.loads(Path("/home/om/devblog/blog_meta.json").read_text(encoding="utf-8"))
    entries = meta.get("entries") if isinstance(meta, dict) else (meta if isinstance(meta, list) else [])
    for e in entries:
        if not isinstance(e, dict): continue
        fn = e.get("file") or e.get("path") or e.get("src")
        dt = e.get("date") or e.get("dateModified") or e.get("published") or e.get("pubDate")
        if fn and dt:
            fn = str(fn).lstrip("/").replace("\\", "/")
            if fn.endswith(".html"):
                try:
                    dtp = datetime.fromisoformat(str(dt).replace("Z", "+00:00"))
                    if dtp.tzinfo is None: dtp = dtp.replace(tzinfo=timezone.utc)
                    META_JSON_DATES[fn] = dtp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                except Exception: pass
except Exception: pass

BG_MAP = {
    "brutalBSD": "images/brutalbsd.png",
    "Memories": "images/three.jpg",
    "dragonFire": "images/dragonFire.jpg",
    "king": "images/prince.webp",
    "monkey": "images/peace.jpg",
    "offensive": "images/PowerFinger.webp",
    "dragon": "images/offensive.jpeg",
}

def rel_to_url(v):
    if not v: return ""
    v = v.strip()
    if v.startswith("data:") or v.startswith("http") or v.startswith("https"):
        return v
    if not v.startswith("/"): v = "./" + v
    return "https://blog.odicforcesounds.com/" + v.lstrip("/")

def page_image_urls(t):
    out = []
    for m in re.finditer(r'(?:background-image|background)\s*:\s*(?:url\(\s*["\']?([^"\'()]+)["\']?|\s*["\']?(/[^"\'()]+)["\']?)', t, re.I):
        val = (m.group(1) or m.group(2)).strip()
        if not val: continue
        if val.startswith("data:") or val.startswith("http") or val.startswith("https"):
            out.append(val); continue
        normalized = "./" + val if not val.startswith("/") else val
        full = rel_to_url(normalized.lstrip("./"))
        if full and full not in out: out.append(full)
    classes = set(re.findall(r'class="([^"]+)"', t))
    for cls in sorted(classes):
        im = BG_MAP.get(cls)
        if im:
            v = "https://blog.odicforcesounds.com/" + im
            if v not in out: out.append(v)
    return out

def image_for_file(t):
    body_m = re.search(r'<body[^>]*\bclass="([^"]*)"', t, re.I)
    if body_m and "dragonFire" in body_m.group(1).split():
        return "https://blog.odicforcesounds.com/images/dragonFire.jpg"
    for img in page_image_urls(t):
        if img.lower().endswith((".jpg",".jpeg",".png",".webp")):
            return img
    return ""

final = {"site":"blog.odicforcesounds.com","image":"https://blog.odicforcesounds.com/images/dragonFire.jpg","updated_at":"2026-10-27T00:00:00Z","files":[]}
for p in sorted(Path(".").glob("*.html")):
    t = p.read_text(encoding="utf-8", errors="replace")
    fn = p.name
    title_m = re.search(r"<title[^>]*>(.*?)</title>", t, re.I | re.S)
    title = clean(title_m.group(1)) if title_m else ""
    desc_src = NAME_DESC(t) or OG_DESC(t) or TW_DESC(t) or title
    og_desc = OG_DESC(t) or desc_src
    tw_title_src = clean(re.search(r'<meta\s[^>]*(?:name|property)="twitter:title"[^>]*content="([^"]*)"', t, re.I).group(1)) if re.search(r'<meta\s[^>]*(?:name|property)="twitter:title"[^>]*content="([^"]*)"', t, re.I) else ""
    pub = PUB(t) or (INDEX_DATES.get(fn) or META_JSON_DATES.get(fn) or "1970-01-01T00:00:00Z")
    img = OG_IMAGE(t) or image_for_file(t) or ""
    desc_fallback = title if desc_src == title and not desc_src else desc_src
    final["files"].append({
        "file": fn,
        "url": f"https://blog.odicforcesounds.com/{fn}",
        "canonical": CANON(t) or f"https://blog.odicforcesounds.com/{fn}",
        "title": title,
        "description": desc_src,
        "og_url": OG_URL(t) or f"https://blog.odicforcesounds.com/{fn}",
        "og_title": OG_TITLE(t) or title,
        "og_description": og_desc,
        "og_type": "article",
        "og_site_name": "Monkey Blog",
        "og_image": img,
        "twitter_title": tw_title_src or title,
        "twitter_description": TW_DESC(t) or og_desc or desc_fallback or title,
        "twitter_card": TW_CARD(t) or "summary_large_image",
        "twitter_image": TW_IMAGE(t) or img,
        "lang": LANG(t) or "en",
        "published": pub,
    })

P = Path("/home/om/devblog/docs_index.json")
P.write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")

d = json.loads(P.read_text(encoding="utf-8"))
print("wrote", P, "entries:", len(final["files"]))
print("image distribution:")
for k,v in Counter(e["og_image"] for e in d["files"]).most_common():
    print(f"  {v:>4}  {k}")
print("\ncustom image entries (non-empty, non-dragonFire fallback):")
for e in d["files"]:
    if e["og_image"] and e["og_image"] != "https://blog.odicforcesounds.com/images/dragonFire.jpg":
        print(" ", e["file"], "||", e["og_image"])
print("\nempty image entries:")
print(" ", [e["file"] for e in d["files"] if not e["og_image"]])
