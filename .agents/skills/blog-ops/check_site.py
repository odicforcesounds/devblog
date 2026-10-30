#!/usr/bin/env python3
"""Audit the published site in docs/ without touching it.

Checks every root page for the head contract this blog relies on — doctype first,
one canonical, complete Open Graph and Twitter tags, one JSON-LD block, one <h1>,
a usable description — then checks that sitemap.xml, robots.txt and the JSON API
describe the same set of pages.

    python3 .agents/skills/blog-ops/check_site.py
    python3 .agents/skills/blog-ops/check_site.py --quiet   # failures only

Exit code 0 when the site is consistent, 1 when anything failed. Standard library
only, so it runs anywhere python3 does.
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

ORIGIN = "https://blog.odicforcesounds.com"
DOCS = "docs"

# Pages that are interface, not archive: excluded from the JSON API on purpose.
# Empty since the standalone API browser page was dropped; only the infra pages
# below are out of the API now.
NOT_ARTICLES = set()

# Infrastructure pages: served by the host, never listed in the sitemap or the API,
# and not intended to rank. Only doctype, one <h1> and noindex are required.
INFRA_PAGES = {"404.html", "home.html"}  # 404 + the old redirect stub

DESC_MIN, DESC_MAX = 110, 155
DESC_SOFT_MIN = 90              # below this: report as a stub, do not fail
ALLOWED_LD = {"BlogPosting", "CollectionPage", "WebPage"}
HEAD_TAGS = ("og:title", "og:description", "og:type", "og:url", "og:site_name",
             "og:image", "twitter:card", "twitter:title", "twitter:description",
             "twitter:image")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


def expected_url(name):
    """The canonical form of a page: the root is the site URL itself."""
    return ORIGIN + "/" if name == "index.html" else "%s/%s" % (ORIGIN, name)


def acceptable_urls(name):
    """Forms already live in the wild that point at the same document."""
    if name == "index.html":
        return {ORIGIN + "/", ORIGIN + "/index.html"}
    return {expected_url(name)}


class Audit(HTMLParser):
    """Collects the head contract and the h1 of one document.

    Deliberately forgiving: pages here contain end tags that do not match
    (<h1>…</h2>, <h1>…</h3>), articles that quote HTML inside <pre>, and files with
    a whole second document pasted after the first. A browser recovers from all of
    it, so this parser must too — otherwise it reports problems that do not exist
    on screen.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.doctype = None
        self.leading = None           # first thing seen when it is not the doctype
        self.title = []
        self.title_count = 0
        self.metas = []               # (key, content)
        self.canonical = []
        self.h1 = []
        self.h1_count = 0
        self.ld = []
        self.stack = []               # [(tag, attrs)]
        self.captures = []            # [{kind, tag, depth, parts}] currently open
        self.in_head = False

    # -- capture bookkeeping --------------------------------------------
    def _store(self, capture):
        text = " ".join("".join(capture["parts"]).split())
        if not text:
            return
        if capture["kind"] == "title":
            self.title.append(text)
        elif capture["kind"] == "h1":
            self.h1.append(text)
        elif capture["kind"] == "ld":
            self.ld.append(text)

    def _close_from(self, depth):
        keep = []
        for capture in self.captures:
            if capture["depth"] >= depth:
                self._store(capture)
            else:
                keep.append(capture)
        self.captures = keep

    def flush(self):
        """Close whatever malformed markup left open at end of file."""
        for capture in self.captures:
            self._store(capture)
        self.captures = []

    # -- parser events --------------------------------------------------
    def handle_decl(self, decl):
        # Only the first declaration counts. A later one is document content
        # (an article quoting HTML, or a second file pasted in), never a prefix.
        if self.doctype is None and self.leading is None:
            self.doctype = decl

    def handle_data(self, data):
        if self.captures:
            for capture in self.captures:
                capture["parts"].append(data)
            return
        if self.doctype is None and data.strip():
            self.leading = self.leading or repr(data.strip()[:40])

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.doctype is None and self.leading is None:
            self.leading = "<%s>" % tag
        if tag == "head":
            self.in_head = True
        if tag == "meta" and self.in_head:
            key = attrs.get("property") or attrs.get("name")
            if key:
                self.metas.append((key, attrs.get("content", "")))
        if tag == "link" and self.in_head and (attrs.get("rel") or "").lower() == "canonical":
            self.canonical.append(attrs.get("href", ""))
        if tag == "title" and self.in_head:
            self.title_count += 1
        if tag == "h1":
            self.h1_count += 1
        if tag in VOID:
            return
        kind = None
        if tag == "title" and self.in_head:
            kind = "title"
        elif tag == "h1":
            kind = "h1"
        elif tag == "script" and self.in_head and attrs.get("type") == "application/ld+json":
            kind = "ld"
        if kind:
            self.captures.append({"kind": kind, "tag": tag, "depth": len(self.stack), "parts": []})
        self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag == "script" or tag == "title":
            # no-op; normal path below handles them
            pass
        index = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                index = i
                break
        if index is None:
            return                      # stray end tag: a browser ignores it
        del self.stack[index:]
        self._close_from(index)


def meta_map(metas):
    out = {}
    for key, content in metas:
        out.setdefault(key, []).append(content)
    return out


def primary_document(source):
    """Return (first document, number of documents found).

    A page must be exactly one document. Pasting a second file into an article
    leaves a doctype and a duplicate head/body mid-document: the browser ignores
    the second document's tags and merges its text into the page body.
    """
    lower = source.lower()
    starts = []
    at = lower.find("<!doctype")
    while at != -1:
        starts.append(at)
        at = lower.find("<!doctype", at + 1)
    if len(starts) <= 1:
        end = lower.find("</html>")
        return (source[: end + 7] if end != -1 else source), len(starts) or 1
    return source[: starts[1]], len(starts)


def audit_page(name):
    path = os.path.join(DOCS, name)
    with open(path, encoding="utf-8", errors="replace") as fh:
        source = fh.read()

    primary, documents = primary_document(source)
    parser = Audit()
    parser.feed(primary)
    parser.close()
    parser.flush()

    problems = []
    warnings = []

    if documents > 1:
        problems.append(
            "%d concatenated documents — everything after the first </html> lands in "
            "this page's body; split it into its own file" % documents
        )

    # 1. doctype first, or the browser renders in quirks mode
    if parser.leading is not None:
        problems.append("content before <!DOCTYPE>: %s" % parser.leading)
    if not parser.doctype:
        problems.append("no doctype")
    elif parser.doctype.strip().lower() != "doctype html":
        problems.append("doctype is <%s>" % parser.doctype)

    metas = meta_map(parser.metas)

    if name in INFRA_PAGES:
        if parser.h1_count != 1 or len(parser.h1) != 1:
            problems.append("infra page needs exactly one <h1> with text")
        if "noindex" not in (metas.get("robots", [""])[0]):
            problems.append("infra page is not marked noindex")
        return problems, warnings, ""

    # 2. one of each head tag
    if parser.title_count != 1 or len(parser.title) != 1:
        problems.append("%d <title> elements" % parser.title_count)

    descriptions = metas.get("description", [])
    if len(descriptions) != 1:
        problems.append("%d meta description" % len(descriptions))
    else:
        desc = descriptions[0]
        if len(desc) > DESC_MAX:
            problems.append("description is %d characters (max %d)" % (len(desc), DESC_MAX))
        elif len(desc) < DESC_MIN:
            note = "description is only %d characters" % len(desc)
            if len(desc) < DESC_SOFT_MIN:
                note += " — the page has almost no prose to summarise"
            warnings.append(note)
        if "Metadata-description-will-be-here" in desc:
            problems.append("description is still the template placeholder")

    for key in HEAD_TAGS:
        found = len(metas.get(key, []))
        if found != 1:
            problems.append("%s x%d" % (key, found))

    # 3. canonical is absolute, correct and unique
    want = expected_url(name)
    allowed = acceptable_urls(name)
    if len(parser.canonical) != 1:
        problems.append("%d canonical links" % len(parser.canonical))
    elif parser.canonical[0] not in allowed:
        problems.append("canonical is %r, expected %r" % (parser.canonical[0], want))
    if metas.get("og:url") and metas["og:url"][0] not in allowed:
        problems.append("og:url is %r" % metas["og:url"][0])
    for key in ("og:image", "twitter:image"):
        if metas.get(key) and not metas[key][0].startswith(ORIGIN + "/"):
            problems.append("%s is not absolute" % key)

    # 4. exactly one <h1>, with text
    if parser.h1_count != 1:
        problems.append("%d <h1> elements" % parser.h1_count)
    elif len(parser.h1) != 1 or not parser.h1[0].strip():
        problems.append("<h1> has no text")

    # 5. one valid JSON-LD block, agreeing with the metas
    if len(parser.ld) != 1:
        problems.append("%d JSON-LD blocks" % len(parser.ld))
    else:
        problems.extend(check_jsonld(name, parser.ld[0], allowed, descriptions))

    return problems, warnings, (descriptions[0] if descriptions else "")


def check_jsonld(name, raw, allowed, descriptions):
    """Validate the single block: one BlogPosting plus, for articles, a breadcrumb."""
    problems = []
    try:
        data = json.loads(raw)
    except ValueError as exc:
        return ["JSON-LD does not parse: %s" % exc]
    if not isinstance(data, dict):
        return ["JSON-LD is not an object"]

    nodes = data.get("@graph") if isinstance(data.get("@graph"), list) else [data]
    types = [n.get("@type") for n in nodes if isinstance(n, dict)]
    if len(types) != len(set(types)):
        problems.append("JSON-LD repeats a @type: %s" % types)
    posting = next((n for n in nodes if isinstance(n, dict) and n.get("@type") == "BlogPosting"), None)
    if posting is None:
        # A listing page is a CollectionPage, not an article: same url/language rules,
        # none of the article-only ones (author, breadcrumb, image, wordCount).
        if types and set(types) <= (ALLOWED_LD - {"BlogPosting"}):
            node = nodes[0]
            if node.get("url") is not None and node["url"] not in allowed:
                problems.append("JSON-LD url is %r" % node.get("url"))
            if node.get("inLanguage") is None:
                problems.append("JSON-LD has no inLanguage")
            if descriptions and node.get("description") != descriptions[0]:
                problems.append("JSON-LD description differs from meta description")
            return problems
        problems.append("JSON-LD has no BlogPosting (%s)" % types)
        return problems
    if posting.get("url") is not None and posting.get("url") not in allowed:
        problems.append("JSON-LD url is %r" % posting.get("url"))
    if not re.match(r"^\d{4}-\d{2}-\d{2}([T ].*)?$", str(posting.get("datePublished") or "")):
        problems.append("JSON-LD datePublished is %r" % posting.get("datePublished"))
    if posting.get("inLanguage") is None:
        problems.append("JSON-LD has no inLanguage")
    if descriptions and posting.get("description") != descriptions[0]:
        problems.append("JSON-LD description differs from meta description")

    image = posting.get("image")
    if isinstance(image, dict):
        if image.get("@type") != "ImageObject" or not image.get("url"):
            problems.append("JSON-LD image is not an ImageObject with a url")
        elif not image.get("width") or not image.get("height"):
            problems.append("JSON-LD image has no width/height")
    elif image is not None:
        problems.append("JSON-LD image is a plain string, not an ImageObject")

    author = posting.get("author")
    if not isinstance(author, dict) or author.get("@type") != "Person" or not author.get("name"):
        problems.append("JSON-LD author is not a Person with a name")
    publisher = posting.get("publisher")
    if not isinstance(publisher, dict) or publisher.get("@type") != "Organization":
        problems.append("JSON-LD has no publisher Organization")
    elif not isinstance(publisher.get("logo"), dict) or not publisher["logo"].get("url"):
        problems.append("JSON-LD publisher has no logo")
    if not isinstance(posting.get("wordCount"), int) or posting["wordCount"] <= 0:
        problems.append("JSON-LD wordCount is %r" % posting.get("wordCount"))

    crumbs = [n for n in nodes if isinstance(n, dict) and n.get("@type") == "BreadcrumbList"]
    wants_crumbs = name not in INFRA_PAGES and name != "index.html"
    if not wants_crumbs:
        if crumbs:
            problems.append("breadcrumb on a page that is not an article")
        return problems
    if not crumbs:
        problems.append("no BreadcrumbList")
        return problems
    items = crumbs[0].get("itemListElement") or []
    if len(items) < 2:
        problems.append("breadcrumb has %d items" % len(items))
        return problems
    if [i.get("position") for i in items] != list(range(1, len(items) + 1)):
        problems.append("breadcrumb positions are %s" % [i.get("position") for i in items])
    for item in items[:-1]:
        if not item.get("item"):
            problems.append("breadcrumb item %r has no url" % item.get("name"))
    if not any(i.get("name") for i in items):
        problems.append("breadcrumb has no names")
    last = items[-1]
    if last.get("item") and last["item"] not in allowed:
        problems.append("breadcrumb ends at %r" % last.get("item"))
    return problems


def check_sitemap(names):
    path = os.path.join(DOCS, "sitemap.xml")
    if not os.path.exists(path):
        return ["sitemap.xml is missing — run build_sitemap.py"]
    with open(path, encoding="utf-8") as fh:
        xml = fh.read()
    locs = [chunk.split("</loc>")[0].strip() for chunk in xml.split("<loc>")[1:]]
    problems = []
    duplicates = len(locs) - len(set(locs))
    if duplicates:
        problems.append("sitemap has %d duplicate <loc>" % duplicates)
    want = {expected_url(n) for n in names if n not in INFRA_PAGES}
    missing = sorted(want - set(locs))
    extra = sorted(set(locs) - want)
    if missing:
        problems.append("sitemap missing %d pages (e.g. %s)"
                        % (len(missing), ", ".join(os.path.basename(m) for m in missing[:4])))
    if extra:
        problems.append("sitemap lists %d unknown urls (e.g. %s)"
                        % (len(extra), ", ".join(extra[:3])))
    return problems


def check_api(names):
    path = os.path.join(DOCS, "api", "index.json")
    if not os.path.exists(path):
        return ["docs/api/index.json is missing — run python3 .agents/skills/blog-ops/build_api.py"]
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except ValueError as exc:
        return ["docs/api/index.json does not parse: %s" % exc]

    problems = []
    articles = data.get("articles") or []
    want = {n for n in names if n not in NOT_ARTICLES and n not in INFRA_PAGES}
    got = {a.get("path") for a in articles}
    if data.get("count") != len(articles):
        problems.append("count says %r but there are %d articles" % (data.get("count"), len(articles)))
    missing = sorted(want - got)
    extra = sorted(got - want)
    if missing:
        problems.append("API missing %d pages (e.g. %s) — rerun .agents/skills/blog-ops/build_api.py"
                        % (len(missing), ", ".join(missing[:4])))
    if extra:
        problems.append("API lists %d unknown pages (e.g. %s)" % (len(extra), ", ".join(extra[:3])))
    for chunk in data.get("chunks") or []:
        target = os.path.join(DOCS, "api", chunk.get("file", ""))
        if not os.path.exists(target):
            problems.append("missing text chunk %s" % chunk.get("file"))
    for article in articles:
        if not article.get("description"):
            problems.append("%s has no description in the API" % article.get("path"))
            break
    return problems


def check_robots():
    path = os.path.join(DOCS, "robots.txt")
    if not os.path.exists(path):
        return ["robots.txt is missing"]
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    problems = []
    if "Sitemap: %s/sitemap.xml" % ORIGIN not in text:
        problems.append("robots.txt has no absolute Sitemap line")
    if "Disallow: /archive/" not in text:
        problems.append("robots.txt does not disallow /archive/")
    return problems


def main(argv):
    quiet = "--quiet" in argv
    if not os.path.isdir(DOCS):
        print("run this from the repository root (no %s/ here)" % DOCS)
        return 2
    names = sorted(n for n in os.listdir(DOCS) if n.endswith(".html"))

    failures = 0
    warnings = []
    descriptions = {}
    for name in names:
        problems, warns, description = audit_page(name)
        if problems:
            failures += len(problems)
            print("%s: %s" % (name, "; ".join(problems)))
        for warn in warns:
            warnings.append("%s: %s" % (name, warn))
        if description:
            descriptions.setdefault(description, []).append(name)

    for text, pages in sorted(descriptions.items()):
        if len(pages) > 1:
            failures += 1
            print("duplicate description in %s: %r" % (" and ".join(pages), text[:60] + "…"))

    for label, problems in (
        ("sitemap", check_sitemap(names)),
        ("api", check_api(names)),
        ("robots", check_robots()),
    ):
        for problem in problems:
            failures += 1
            print("%s: %s" % (label, problem))

    if not quiet:
        for warn in warnings:
            print("warning — %s" % warn)
        lengths = sorted(len(t) for t in descriptions)
        if lengths:
            print("descriptions: %d pages, min %d, median %d, max %d, %d under %d"
                  % (len(lengths), lengths[0], lengths[len(lengths) // 2], lengths[-1],
                     sum(1 for n in lengths if n < DESC_MIN), DESC_MIN))

    print("pages %d, warnings %d, failures %d" % (len(names), len(warnings), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
