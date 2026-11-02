#!/usr/bin/env python3
"""Audit the things a screen reader, a keyboard and a search engine all depend on.

    python3 .agents/skills/a11y/check_a11y.py
    python3 .agents/skills/a11y/check_a11y.py --json
    python3 .agents/skills/a11y/check_a11y.py --page lifeIndex.html

Checks: an `<img>` with no `alt`, an `<html>` with no `lang`, Chinese text declared as
another language, a language block with no `lang` of its own, a link with no accessible
name, `target="_blank"` without `rel="noopener"`, a duplicate `id`, a form control with no
label, and a positive `tabindex`.

Read-only. Exit code 0 when nothing needs fixing, 1 when a failure is found. Warnings —
the language-heuristic findings — never set the code.
"""

import argparse
import glob
import html
import json
import os
import re
import sys

DOCS = "docs"
CJK = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
IMG = re.compile(r'<img\b[^>]*>', re.I)
ANCHOR = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.I | re.S)
TAG_ID = re.compile(r'\bid\s*=\s*"([^"]+)"')
LANG_BLOCK = re.compile(r'<(?:div|section|p|span|aside)\b[^>]*(?:data-lang-block|class\s*=\s*"[^"]*lang-block)[^>]*>', re.I)
CONTROL = re.compile(r'<(input|select|textarea)\b([^>]*)>', re.I)
LABEL_FOR = re.compile(r'<label\b[^>]*\bfor\s*=\s*"([^"]+)"', re.I)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def attributes(text):
    return {k.lower(): html.unescape(v) for k, v in re.findall(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', text)}


def text_of(fragment):
    stripped = re.sub(r'<[^>]+>', ' ', fragment)
    return " ".join(html.unescape(stripped).split())


def audit(page):
    source = read(os.path.join(DOCS, page))
    failures, warnings = [], []

    html_tag = re.search(r'<html\b([^>]*)>', source, re.I)
    lang = ""
    if not html_tag:
        failures.append("no <html> element")
    else:
        lang = attributes(html_tag.group(1)).get("lang", "")
        if not lang:
            failures.append("<html> has no lang")
    if lang and CJK.search(source):
        warnings.append("Chinese text under lang=\"%s\" — those runs are announced in the wrong language" % lang)

    for tag in IMG.findall(source):
        attrs = attributes(tag)
        if "alt" not in attrs:
            failures.append("img without alt: %s" % (attrs.get("src", "?")[:70]))

    labelled = set(LABEL_FOR.findall(source))
    for kind, body in CONTROL.findall(source):
        attrs = attributes(body)
        if attrs.get("type", "").lower() in ("hidden", "submit", "button", "reset", "image"):
            continue
        if attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"):
            continue
        if attrs.get("id") and attrs["id"] in labelled:
            continue
        if kind.lower() == "input" and attrs.get("type", "").lower() in ("checkbox", "radio"):
            continue
        warnings.append("<%s%s> has no label" % (kind, " name=%s" % attrs["name"] if attrs.get("name") else ""))

    for body, inner in ANCHOR.findall(source):
        attrs = attributes(body)
        name = text_of(inner)
        if not name:
            if "<img" in inner.lower():
                images = IMG.findall(inner)
                if images and any("alt" in attributes(t) and attributes(t)["alt"].strip() for t in images):
                    continue
            if attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"):
                warnings.append("link named only by a title or aria-label: %s" % attrs.get("href", "?")[:60])
                continue
            if attrs.get("href", "").startswith("#"):
                warnings.append("empty in-page anchor: %s" % attrs["href"][:40])
                continue
            failures.append("link with no accessible name: %s" % attrs.get("href", "?")[:70])
        if attrs.get("href") and attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", "").lower():
            failures.append("target=_blank without rel=noopener: %s" % attrs["href"][:60])

    for block in LANG_BLOCK.findall(source):
        if "lang" not in attributes(block):
            warnings.append("language block with no lang attribute")
            break

    seen = {}
    for identifier in TAG_ID.findall(source):
        seen[identifier] = seen.get(identifier, 0) + 1
    duplicates = [name for name, count in seen.items() if count > 1]
    if duplicates:
        failures.append("duplicate id: %s" % ", ".join(sorted(duplicates)[:5]))

    for value in re.findall(r'\btabindex\s*=\s*"(\d+)"', source):
        if int(value) > 0:
            warnings.append("positive tabindex=%s" % value)
            break

    return failures, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit accessibility basics on every page.")
    parser.add_argument("--page", help="audit one page by file name")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    pages = [args.page] if args.page else sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "*.html")))
    if not pages or not os.path.exists(os.path.join(DOCS, pages[0])):
        print("no pages found", file=sys.stderr)
        return 1

    failures, warnings = [], []
    for page in pages:
        f, w = audit(page)
        failures += [(page, item) for item in f]
        warnings += [(page, item) for item in w]

    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "failures": [{"page": p, "what": t} for p, t in failures],
            "warnings": [{"page": p, "what": t} for p, t in warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    print("pages %d | failures %d | warnings %d" % (len(pages), len(failures), len(warnings)))
    if failures:
        for page, what in failures[:25]:
            print("  %s — %s" % (page, what))
        if len(failures) > 25:
            print("  … and %d more" % (len(failures) - 25))
    if warnings:
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
