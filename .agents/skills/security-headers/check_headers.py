#!/usr/bin/env python3
"""Check that each page's own security policy permits what the page itself loads.

The failure this exists for is silent: a `Content-Security-Policy` meta that omits
`style-src 'self'` refuses every stylesheet file, so a page that links
`link-colors.css` renders with its fallback colours and looks merely different, not
broken. Thirty-one pages were in that state before anyone noticed.

So the policy is not compared against a template. It is compared against the page: every
stylesheet, script, iframe, image and fetch the page actually uses must be permitted by
the directive that governs it, with the CSP fallback chain applied (a missing `style-src`
is governed by `default-src`).

    python3 .agents/skills/security-headers/check_headers.py
    python3 .agents/skills/security-headers/check_headers.py --json
    python3 .agents/skills/security-headers/check_headers.py --page DragonFire.html

Read-only: it writes nothing. Exit code 0 when every page's policy allows its own
resources, 1 when one blocks something it loads.
"""

import argparse
import glob
import html
import json
import os
import re
import sys
import urllib.parse

DOCS = "docs"
POLICY = re.compile(r'<meta[^>]+http-equiv\s*=\s*"Content-Security-Policy"[^>]*>', re.I)
CONTENT = re.compile(r'content\s*=\s*"([^"]*)"', re.I)
LINK = re.compile(r'<link\b[^>]*>', re.I)
SCRIPT = re.compile(r'<script\b([^>]*)>', re.I)
IFRAME = re.compile(r'<iframe\b[^>]*\bsrc\s*=\s*"([^"]*)"', re.I)
IMG = re.compile(r'<img\b[^>]*\bsrc\s*=\s*"([^"]*)"', re.I)
FETCH = re.compile(r'''fetch\(\s*['"]([^'"]+)['"]''', re.I)
OTHER_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": None,
    "Referrer-Policy": None,
}


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def attributes(tag):
    return {k.lower(): html.unescape(v) for k, v in
            re.findall(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', tag)}


def parse_policy(source):
    found = POLICY.search(source)
    if not found:
        return None
    content = CONTENT.search(found.group(0))
    if not content:
        return None
    directives = {}
    for part in content.group(1).split(";"):
        tokens = part.split()
        if not tokens:
            continue
        directives[tokens[0].lower()] = [t for t in tokens[1:]]
    return directives


def governed(directives, name):
    """The sources that govern a fetch type, following the CSP fallback chain."""
    chain = [name, "default-src"] if name != "default-src" else ["default-src"]
    for key in chain:
        if key in directives:
            return directives[key]
    return []


def is_local(url):
    return not (url.startswith("//") or re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I))


def origin(url):
    if url.startswith("//"):
        return "https:" + url.split("/")[0]
    parsed = urllib.parse.urlsplit(url)
    return "%s://%s" % (parsed.scheme, parsed.netloc) if parsed.netloc else ""


def allows(sources, url):
    if not sources:
        return False
    if "'none'" in sources:
        return False
    local = is_local(url)
    for source in sources:
        lower = source.lower()
        if lower == "*":
            return True
        if lower == "'self'" and local:
            return True
        if lower.startswith("'") :
            continue
        if source.startswith("//"):
            source = "https:" + source
        if local:
            continue
        if re.match(r'^[a-z][a-z0-9+.-]*:$', lower):
            if url.lower().startswith(lower):
                return True
            continue
        candidate = source.rstrip("/")
        host = origin(url).rstrip("/")
        if not host:
            continue
        if candidate.startswith("*."):
            suffix = candidate[1:].lower()
            if host.lower().endswith(suffix):
                return True
        elif candidate.lower() == host.lower():
            return True
        elif url.lower().startswith(candidate.lower() + "/"):
            return True
    return False


def requirements(source):
    needs = []           # (directive, url, what)
    for tag in LINK.findall(source):
        attrs = attributes(tag)
        if "stylesheet" not in attrs.get("rel", "").lower():
            continue
        href = attrs.get("href", "")
        if href:
            needs.append(("style-src", href, "stylesheet"))
    for attrs_text in SCRIPT.findall(source):
        attrs = attributes(attrs_text)
        src = attrs.get("src")
        if src:
            needs.append(("script-src", src, "script"))
    for src in IFRAME.findall(source):
        needs.append(("frame-src", src, "iframe"))
    for src in IMG.findall(source):
        needs.append(("img-src", src, "image"))
    for src in FETCH.findall(source):
        needs.append(("connect-src", src, "fetch"))
    return needs


def has_inline_js(source):
    """Whether the page carries an executable inline script.

    `<script type="application/ld+json">` is data: the browser never executes it, so no
    policy blocks it and a checker that counts it invents a failure on 380 pages.
    """
    for attrs_text in SCRIPT.findall(source):
        attrs = attributes(attrs_text)
        if attrs.get("src"):
            continue
        kind = attrs.get("type", "").lower()
        if kind and "javascript" not in kind and "module" not in kind:
            continue
        return True
    return False


def audit(page):
    source = read(os.path.join(DOCS, page))
    failures, warnings = [], []
    policy = parse_policy(source)
    inline_scripts = has_inline_js(source)

    if policy is None:
        external = [u for u in IFRAME.findall(source) + IMG.findall(source) if not is_local(u)]
        if external:
            warnings.append("no Content-Security-Policy, and the page loads %d remote resource(s)" % len(external))
        else:
            warnings.append("no Content-Security-Policy")
        for header, value in OTHER_HEADERS.items():
            if header.lower() + "\"" not in source.lower():
                warnings.append("no %s meta" % header)
        return failures, warnings

    default_sources = governed(policy, "default-src")
    if not allows(default_sources, "page.html") and "'none'" not in default_sources:
        warnings.append("default-src is neither 'self' nor 'none' — every unlisted type is unconstrained")
    for directive, url, what in requirements(source):
        sources = governed(policy, directive)
        if not allows(sources, url):
            failures.append("%s %s is not allowed by %s" % (what, url, directive))
    if inline_scripts:
        script_sources = governed(policy, "script-src")
        nonce = any(s.startswith("'nonce-") or s.startswith("'sha") for s in script_sources)
        if "'unsafe-inline'" not in script_sources and not nonce:
            failures.append("inline <script> is blocked by script-src")
    if "'unsafe-eval'" in governed(policy, "script-src"):
        warnings.append("script-src allows 'unsafe-eval'")
    if "object-src" not in policy:
        warnings.append("no object-src 'none'")
    if "base-uri" not in policy:
        warnings.append("no base-uri 'self'")
    for header, value in OTHER_HEADERS.items():
        if header.lower() + "\"" not in source.lower():
            warnings.append("no %s meta" % header)
        elif value and value not in source:
            warnings.append("%s does not say %s" % (header, value))
    return failures, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check each page's policy against what it loads.")
    parser.add_argument("--page", help="audit one page by file name")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    pages = [args.page] if args.page else sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "*.html")))
    if not pages or not os.path.exists(os.path.join(DOCS, pages[0])):
        print("no pages found", file=sys.stderr)
        return 1

    policies = 0
    failures, warnings = [], []
    for page in pages:
        f, w = audit(page)
        if parse_policy(read(os.path.join(DOCS, page))) is not None:
            policies += 1
        failures += [(page, item) for item in f]
        warnings += [(page, item) for item in w]

    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "with_policy": policies,
            "failures": [{"page": p, "what": t} for p, t in failures],
            "warnings": [{"page": p, "what": t} for p, t in warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    print("pages %d | with a policy %d (%d without) | failures %d | warnings %d"
          % (len(pages), policies, len(pages) - policies, len(failures), len(warnings)))
    if failures:
        for page, what in failures[:25]:
            print("  %s — %s" % (page, what))
        if len(failures) > 25:
            print("  … and %d more" % (len(failures) - 25))
    if warnings and not failures:
        for page, what in warnings[:10]:
            print("  %s — %s" % (page, what))
        if len(warnings) > 10:
            print("  … and %d more" % (len(warnings) - 10))
    if not failures and not warnings:
        print("nothing to fix")
    elif not failures:
        print("no failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
