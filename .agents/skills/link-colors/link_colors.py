#!/usr/bin/env python3
"""Colour every link on the blog by where it points.

Three destinations, three colours, so a reader can tell at a glance what leaves the blog:

    blog      a page of this blog        docs/*.html, ./x, images/x, /x,
                                         https://blog.odicforcesounds.com/x.html,
                                         https://odicforcesounds.com/x.html
    sibling   another subdomain of the same domain:
                                         art., book., music., www.odicforcesounds.com/…
    external  any other host, with a scheme of its own

In-page anchors (`#order-…`), `?lang=…`, `mailto:`, `tel:` and `javascript:` keep the
page's own colour: they do not go anywhere new.

The rules live in one generated sheet, `docs/link-colors.css`, and every page links it
as its last stylesheet, so it wins the cascade and also works on pages that never load
`article.css`. It is a same-origin file, so a policy that allows `'self'` styles keeps
working without `'unsafe-inline'`.

    python3 .agents/skills/link-colors/link_colors.py            # write the sheet + links
    python3 .agents/skills/link-colors/link_colors.py --dry-run   # report only
    python3 .agents/skills/link-colors/link_colors.py --check     # verify, exit 1 on drift
    python3 .agents/skills/link-colors/link_colors.py --remove    # take the links out
"""

import argparse
import collections
import glob
import os
import re
import sys

DOCS = "docs"
FRONT = "index.html"
SHEET = os.path.join(DOCS, "link-colors.css")

DOMAIN = "odicforcesounds.com"
BLOG_HOST = "blog." + DOMAIN
APEX_HOST = DOMAIN

BLOG = "#6fb3ff"
SIBLING = "#ffd23f"
EXTERNAL = "#ff9ecb"
HOVER = "#ffffff"

LINK_TAG = re.compile(r'\n?[ \t]*<link rel="stylesheet" href="/?link-colors\.css"[^>]*>', re.I)
STYLE_SRC = re.compile(r'(<meta http-equiv="Content-Security-Policy" content="[^"]*?style-src)([^";]*)', re.I)


def allow_self_styles(source):
    """Add 'self' to style-src so the page's own policy lets a same-origin sheet load.

    A page with `style-src 'unsafe-inline'` and no 'self' allows inline blocks and
    blocks every stylesheet file, this one included: the links would then keep the
    page's own colour and nothing would report it. Only that directive is touched.
    """
    def fix(match):
        if "'self'" in match.group(2):
            return match.group(0)
        return match.group(1) + " 'self'" + match.group(2)
    return STYLE_SRC.sub(fix, source, count=1)


def blocks_sheet(source):
    """True when the page links the sheet but its style-src would refuse it."""
    match = STYLE_SRC.search(source)
    return bool(match) and "'self'" not in match.group(2)

# Order matters, and the last matching rule wins: blog first, then sibling, then
# external. The blog rule matches every href ending in `.html`, which is how a page
# of this blog is written as a relative link; without the external rule coming last,
# https://www.rand.org/report.html would be painted as a page of this blog. The
# external rule names the schemes (`http:`, `https:`) instead of the bare `http`
# prefix, or a page called httpProtocol.html would look like a foreign host.
SHEET_CSS = """
:root {
  --link-blog: %(blog)s;
  --link-sibling: %(sibling)s;
  --link-external: %(external)s;
  --link-hover: %(hover)s;
}

a[href*="//%(blog_host)s"],
a[href*="//%(apex_host)s"],
a[href^="./"],
a[href^="/"]:not([href^="//"]),
a[href^="images/"],
a[href$=".html"],
a[href*=".html#"] {
  color: var(--link-blog) !important;
}

a[href*="%(domain)s"]:not([href*="//%(blog_host)s"]):not([href*="//%(apex_host)s"]):not([href^="mailto:"]):not([href^="tel:"]) {
  color: var(--link-sibling) !important;
}

a[href^="http:"]:not([href*="odicforcesounds.com"]),
a[href^="https:"]:not([href*="odicforcesounds.com"]),
a[href^="//"]:not([href*="odicforcesounds.com"]) {
  color: var(--link-external) !important;
}

a[href]:hover,
a[href]:focus-visible {
  color: var(--link-hover) !important;
}
"""

SHEET_CSS = re.sub(r"/\*.*?\*/", "", SHEET_CSS, flags=re.S)
SHEET_CSS = re.sub(r"\n{3,}", "\n\n", SHEET_CSS).strip() + "\n"

NEUTRAL_PREFIXES = ("#", "?", "mailto:", "tel:", "javascript:", "data:")


def host_of(href):
    """The host of an absolute or protocol-relative link, lowercased, without a port."""
    value = re.sub(r"^[a-z][a-z0-9+.-]*:", "", href.strip(), flags=re.I)
    value = value.lstrip("/")
    host = re.split(r"[/?#]", value, 1)[0]
    host = host.split("@")[-1]
    host = host.split(":")[0]
    return host.lower()


def classify(href):
    """Which of the three colours a link gets; None when it keeps the page's own.

    Written to run in the same order as the selectors in the sheet, so the count this
    prints is the count a browser paints: blog first, sibling, external last.
    """
    value = (href or "").strip()
    if not value:
        return None
    lowered = value.lower()
    if lowered.startswith(NEUTRAL_PREFIXES):
        return None
    blog_host = "//" + BLOG_HOST in value or "//" + APEX_HOST in value
    kind = None
    if blog_host or value.startswith("./") or value.startswith("images/") \
            or (value.startswith("/") and not value.startswith("//")) \
            or value.endswith(".html") or ".html#" in value:
        kind = "blog"
    if DOMAIN in value and not blog_host:
        kind = "sibling"
    if lowered.startswith(("http:", "https:", "//")) and DOMAIN not in value:
        kind = "external"
    return kind


def subdomain_of(href):
    """The subdomain label of a same-domain link, for the report."""
    host = host_of(href)
    if host == APEX_HOST or not host.endswith("." + DOMAIN):
        return ""
    return host[: -len("." + DOMAIN)]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Colour links by destination.")
    parser.add_argument("--dry-run", action="store_true", help="report only")
    parser.add_argument("--check", action="store_true", help="verify, write nothing")
    parser.add_argument("--remove", action="store_true", help="take the links out")
    args = parser.parse_args(argv)

    pages = sorted(p for p in glob.glob(os.path.join(DOCS, "*.html"))
                   if os.path.basename(p) != FRONT)
    if not pages:
        print("no pages found", file=sys.stderr)
        return 1

    sheet = SHEET_CSS % {"blog": BLOG, "sibling": SIBLING, "external": EXTERNAL,
                         "hover": HOVER, "domain": DOMAIN,
                         "blog_host": BLOG_HOST, "apex_host": APEX_HOST}
    counts = {"blog": 0, "sibling": 0, "external": 0, "neutral": 0}
    subdomains = collections.Counter()
    missing = []
    unlinked = []
    blocked = []
    written = removed = 0

    for path in pages:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        for href in re.findall(r'<a[^>]*href="([^"]*)"', source, re.I):
            kind = classify(href)
            counts[kind or "neutral"] += 1
            if kind == "sibling":
                subdomains[subdomain_of(href) or "(apex)"] += 1

        body = LINK_TAG.sub("", source)
        if args.remove:
            if body != source:
                if not args.check and not args.dry_run:
                    with open(path, "w", encoding="utf-8") as handle:
                        handle.write(body)
                removed += 1
            continue

        if args.check:
            if "link-colors.css" not in source:
                missing.append(name)
            elif blocks_sheet(source):
                blocked.append(name)
            continue

        body = allow_self_styles(body)
        rel = "/link-colors.css" if name == "404.html" else "link-colors.css"
        tag = '  <link rel="stylesheet" href="%s">\n' % rel
        updated = body.replace("</head>", tag + "</head>", 1)
        if updated == body:
            unlinked.append(name)
            continue
        if updated != source:
            if not args.dry_run:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(updated)
            written += 1

    print("domain: %s | blog host: %s" % (DOMAIN, BLOG_HOST))
    print("links: blog %d | sibling %d | external %d | kept as written %d"
          % (counts["blog"], counts["sibling"], counts["external"], counts["neutral"]))
    if subdomains:
        print("sibling subdomains: " +
              ", ".join("%s %d" % (label, n) for label, n in subdomains.most_common()))

    if args.check:
        stale = []
        if os.path.exists(SHEET):
            with open(SHEET, encoding="utf-8") as handle:
                if handle.read() != sheet:
                    stale.append(SHEET)
        else:
            stale.append(SHEET)
        print("pages: %d | without the link: %d | sheet out of date: %d | policy blocks it: %d"
              % (len(pages), len(missing), len(stale), len(blocked)))
        for name in missing[:10]:
            print("  missing link:", name)
        for name in blocked[:10]:
            print("  style-src without 'self':", name)
        for name in stale:
            print("  stale sheet:", name)
        return 1 if (missing or stale or blocked) else 0

    if args.remove:
        print("links removed: %d | pages: %d" % (removed, len(pages)))
        return 0

    if not args.dry_run:
        with open(SHEET, "w", encoding="utf-8") as handle:
            handle.write(sheet)
    print("stylesheet: %s (%d bytes)" % (SHEET, len(sheet)))
    print("pages written: %d | without a head: %d" % (written, len(unlinked)))
    if args.dry_run:
        print("dry run — nothing was written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
