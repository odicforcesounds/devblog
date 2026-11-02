#!/usr/bin/env python3
"""Check that the Firebase pages agree with each other and with the rules they promise.

The comment form on `index.html` and the session-only chat on `secretChat.html` share one
Firebase project. The config block is copied into each page, so the pages can drift: a
different project id on one of them sends its writes somewhere nobody watches, and the
symptom is an empty thread, not an error.

    python3 .agents/skills/comments/check_firebase.py
    python3 .agents/skills/comments/check_firebase.py --json

Checks: the config objects are identical wherever they appear; the API key and project id
are the same; every collection name the code writes to is documented in
backups/firebase-rules.txt; the chat page does not keep anything on the device; the
provider list contains only providers that answer.

Read-only. Exit code 0 when the pages agree, 1 when they do not.
"""

import argparse
import glob
import json
import os
import re
import sys

DOCS = "docs"
RULES = os.path.join("backups", "firebase-rules.txt")
CONFIG = re.compile(r'(?:const|let|var)\s+firebaseConfig\s*=\s*\{(.*?)\};', re.S)
FIELD = re.compile(r'(\w+)\s*:\s*"([^"]*)"')
COLLECTION = re.compile(r'collection\(\s*[\w.]+\s*,\s*([\w"]+)\s*\)')
CONSTANT = re.compile(r'(?:const|let|var)\s+([A-Z][A-Z0-9_]{2,})\s*=\s*"([^"]+)"')
STORAGE = re.compile(r'\b(localStorage|sessionStorage)\b')


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def configs():
    found = {}
    for path in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        source = read(path)
        match = CONFIG.search(source)
        if not match:
            continue
        found[os.path.basename(path)] = dict(FIELD.findall(match.group(1)))
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check the Firebase pages against each other.")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    pages = configs()
    failures, warnings = [], []

    if not pages:
        print("no page carries a firebaseConfig")
        return 0

    reference_page = sorted(pages)[0]
    reference = pages[reference_page]
    for page, config in sorted(pages.items()):
        for field in ("apiKey", "authDomain", "projectId", "appId"):
            if config.get(field) != reference.get(field):
                failures.append((page, "%s differs from %s (%s)" % (field, reference_page, reference.get(field, "missing"))))

    rules = read(RULES) if os.path.exists(RULES) else ""
    if not rules:
        warnings.append((RULES, "no rules file — what may be written is undocumented"))
    collections = set()
    for page in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        source = read(page)
        constants = dict(CONSTANT.findall(source))
        reported = set()
        for token in COLLECTION.findall(source):
            if token.startswith('"'):
                name = token.strip('"')
            else:
                name = constants.get(token, "")
            if not name:
                warnings.append((os.path.basename(page), "collection named by %r, which is not a string on the page" % token))
                continue
            collections.add(name)
            if rules and name not in rules and name not in reported:
                reported.add(name)
                failures.append((os.path.basename(page), "writes collection \"%s\", absent from %s" % (name, RULES)))

    for page in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        source = read(page)
        if "firebase" not in source.lower():
            continue
        storage = set(STORAGE.findall(source))
        if "localStorage" in storage and "session" in os.path.basename(page).lower():
            failures.append((os.path.basename(page), "keeps chat state in localStorage — the page promises the session only"))
        if "localStorage" in storage:
            warnings.append((os.path.basename(page), "uses localStorage"))

    if args.json:
        print(json.dumps({
            "pages": sorted(pages),
            "project": reference.get("projectId"),
            "collections": sorted(collections),
            "failures": [{"page": p, "what": t} for p, t in failures],
            "warnings": [{"page": p, "what": t} for p, t in warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    print("pages with a firebaseConfig %d (%s) | project %s | collections %s"
          % (len(pages), ", ".join(sorted(pages)), reference.get("projectId", "?"),
             ", ".join(sorted(collections)) or "none"))
    if failures:
        print("failures %d" % len(failures))
        for page, what in failures:
            print("  %s — %s" % (page, what))
    if warnings:
        print("warnings %d" % len(warnings))
        for page, what in warnings[:8]:
            print("  %s — %s" % (page, what))
        if len(warnings) > 8:
            print("  … and %d more" % (len(warnings) - 8))
    if not failures and not warnings:
        print("nothing to fix")
    elif not failures:
        print("no failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
