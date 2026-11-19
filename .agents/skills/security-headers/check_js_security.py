#!/usr/bin/env python3
"""Audit the JavaScript the site ships against two client-side security guides.

The pages here carry their code in the browser, so the browser is the exposure
boundary: whatever a script contains is public to anyone who loads the page. This
script applies the recommendations of Jscrambler's "Enhancing JavaScript Security"
and NHI Mgmt Group's analysis of "JavaScript obfuscation and minification" to the
files the site actually publishes:

  integrity      a remote <script> or stylesheet must name the bytes it runs
                 (Subresource Integrity, plus crossorigin on the host that serves it)
  https          no subresource may be fetched over http:// — plain http is the
                 man-in-the-middle gap HTTPS closes
  unsafe-eval    'unsafe-eval' in the page's own script-src is a failure, not a
                 setting; nothing on this site needs it
  secrets        no key, token or private key inside an inline script or a local
                 .js file: minification and obfuscation change the reading cost,
                 not the exposure, so a secret in a shipped script is public
  obfuscation    a packed or renamed script is reported as a deterrent layer only,
                 never as a control — the secret scan runs on it all the same
  third-party    every remote script host is counted, because each one is a
                 supply-chain dependency the page cannot audit

    python3 .agents/skills/security-headers/check_js_security.py
    python3 .agents/skills/security-headers/check_js_security.py --page wordGame.html
    python3 .agents/skills/security-headers/check_js_security.py --json
    python3 .agents/skills/security-headers/check_js_security.py --strict

Read-only: it writes nothing and prints no secret in full. Exit code 0 when no page
has a defect, 1 when one does; --strict also fails on the hardening warnings.
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
SCRIPT_BLOCK = re.compile(r'<script\b([^>]*)>(.*?)</script\s*>', re.I | re.S)
LINK = re.compile(r'<link\b[^>]*>', re.I)
IFRAME = re.compile(r'<iframe\b[^>]*>', re.I)
IMG = re.compile(r'<img\b[^>]*>', re.I)
FORM = re.compile(r'<form\b[^>]*>', re.I)
# A link to an http:// page is navigation, judged by link-integrity; a subresource
# fetched over http is the man-in-the-middle gap this file exists for.
EVALUATES = re.compile(r'\beval\s*\(|\bnew\s+Function\s*\(|\(set(?:Timeout|Interval)\s*\(\s*["\']', re.I)

# A pattern that only a real credential matches: these are failures.
HARD_SECRETS = (
    ("Google API key", re.compile(r'\bAIza[0-9A-Za-z_-]{35}\b')),
    ("AWS access key", re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ("private key block", re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----')),
    ("Stripe live key", re.compile(r'\bsk_live_[0-9A-Za-z]{24,}\b')),
    ("GitHub token", re.compile(r'\bgh[pousr]_[0-9A-Za-z]{36,}\b')),
    ("Slack token", re.compile(r'\bxox[abprs]-[0-9A-Za-z-]{10,}\b')),
    ("JSON Web Token", re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b')),
)

# A guess: worth reading, not proof. Reported as a warning.
GENERIC_SECRET = re.compile(
    r'''(?i)\b(api[_-]?key|apikey|client[_-]?secret|secret|password|passwd|'''
    r'''auth[_-]?token|access[_-]?token|private[_-]?key)\b\s*[:=]\s*['"]([^'"\s]{16,})['"]'''
)

# Markers of a script transformed to be harder to read, not of a page that errors.
OBFUSCATED = (
    (re.compile(r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e'), "eval-packed"),
    (re.compile(r'\b_0x[0-9a-f]{4,}\b'), "renamed to hex identifiers"),
)

PLACEHOLDERS = ("your", "example", "placeholder", "changeme", "redacted", "todo",
                "insert", "dummy", "sample", "<", "...", "…", "xxxx")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def attributes(tag):
    return {k.lower(): html.unescape(v) for k, v in
            re.findall(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', tag)}


def is_local(url):
    return not (url.startswith("//") or re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I))


def origin(url):
    if url.startswith("//"):
        return "https:" + url.split("/")[0]
    parsed = urllib.parse.urlsplit(url)
    return "%s://%s" % (parsed.scheme, parsed.netloc) if parsed.netloc else ""


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
        if tokens:
            directives[tokens[0].lower()] = [t for t in tokens[1:]]
    return directives


def executable(box):
    """Whether a script body the browser would run, rather than data it would not."""
    attrs = attributes(box)
    if attrs.get("src"):
        return False
    kind = attrs.get("type", "").lower()
    return not kind or "javascript" in kind or "module" in kind


def mask(text):
    """Name a credential without printing it: a report is read, sometimes kept."""
    text = text.strip()
    if len(text) <= 8:
        return "%s… (%d chars)" % (text[:2], len(text))
    return "%s…%s (%d chars)" % (text[:4], text[-2:], len(text))


def scan_js(text, where, failures, warnings, firebase=False):
    """A credential in shipped code is public. What makes one safe is decided elsewhere.

    A Firebase web API key is meant to be in the page: it names the project, and access
    is decided by the database rules and by the key's restrictions in Google Cloud. The
    same shape anywhere else is a credential that has escaped, so it fails.
    """
    for label, pattern in HARD_SECRETS:
        for found in pattern.finditer(text):
            if firebase and label == "Google API key":
                warnings.append("%s carries the Google key that names a Firebase project: "
                                "it is public by design, so the page is only as safe as "
                                "the database rules and the key's restrictions — %s"
                                % (where, mask(found.group(0))))
                continue
            failures.append("%s carries a %s: %s" % (where, label, mask(found.group(0))))
    for found in GENERIC_SECRET.finditer(text):
        value = found.group(2)
        if any(token in value.lower() for token in PLACEHOLDERS):
            continue
        warnings.append("%s assigns a %d-character string to %s: %s"
                        % (where, len(value), found.group(1), mask(value)))
    for pattern, label in OBFUSCATED:
        if pattern.search(text):
            warnings.append("%s is %s — obfuscation raises the reading cost, it does "
                            "not hide anything from the browser" % (where, label))
            break


def audit_page(path, failures, warnings, hosts):
    source = read(path)
    name = os.path.basename(path)

    evaluates = any(EVALUATES.search(html.unescape(body))
                    for attrs_text, body in SCRIPT_BLOCK.findall(source)
                    if executable(" " + attrs_text))
    firebase = re.search(r'firestore\.googleapis\.com|firebase', source, re.I) is not None

    policy = parse_policy(source)
    if policy is not None:
        script_sources = policy.get("script-src") or policy.get("default-src") or []
        if "'unsafe-eval'" in script_sources and not evaluates:
            failures.append("%s: the page's own script-src allows 'unsafe-eval' while "
                            "nothing on the page evaluates a string — the directive can "
                            "simply be removed" % name)
        elif "'unsafe-eval'" in script_sources:
            warnings.append("%s: script-src allows 'unsafe-eval' because the page "
                            "evaluates strings; the protection is the sandbox around "
                            "eval, not the directive" % name)

    for tag in LINK.findall(source):
        attrs = attributes(tag)
        if "stylesheet" not in attrs.get("rel", "").lower():
            continue
        href = attrs.get("href", "")
        if not href or is_local(href):
            continue
        host = origin(href)
        hosts[host] = hosts.get(host, 0) + 1
        if not attrs.get("integrity"):
            if "fonts.googleapis.com" in host:
                warnings.append("%s: %s serves CSS that differs per browser, so integrity "
                                "cannot be pinned — self-host the font to remove the "
                                "dependency" % (name, host))
            else:
                warnings.append("%s: remote stylesheet %s has no integrity, so the host can "
                                "change what the page applies" % (name, href))
        elif not attrs.get("crossorigin"):
            warnings.append("%s: %s has integrity but no crossorigin, so the browser "
                            "will not check it" % (name, href))

    for attrs_text, body in SCRIPT_BLOCK.findall(source):
        attrs = attributes(attrs_text)
        src = attrs.get("src")
        if src and not is_local(src):
            host = origin(src)
            hosts[host] = hosts.get(host, 0) + 1
            if not attrs.get("integrity"):
                warnings.append("%s: third-party script %s has no integrity, so the host "
                                "chooses what runs on the page" % (name, src))
            elif not attrs.get("crossorigin"):
                warnings.append("%s: %s has integrity but no crossorigin, so the browser "
                                "will not check it" % (name, src))
        if not src and executable(" " + attrs_text):
            scan_js(html.unescape(body), "%s inline script" % name, failures, warnings,
                    firebase=firebase)

    for tag in IFRAME.findall(source):
        src = attributes(tag).get("src", "")
        if src and not is_local(src):
            hosts[origin(src)] = hosts.get(origin(src), 0) + 1

    for pattern, attribute, what, wanted in (
            (SCRIPT_BLOCK, "src", "script", None),
            (LINK, "href", "stylesheet", "stylesheet"),
            (IMG, "src", "image", None),
            (IFRAME, "src", "frame", None),
            (FORM, "action", "form target", None)):
        for tag in pattern.findall(source):
            tag = tag if isinstance(tag, str) else tag[0]
            attrs = attributes(tag)
            if wanted and wanted not in attrs.get("rel", "").lower():
                continue
            url = html.unescape(attrs.get(attribute, "")).strip()
            if re.match(r'^http://', url, re.I):
                failures.append("%s: %s %s is fetched over plain http, where the response "
                                "can be altered in transit" % (name, what, url))


def audit_scripts(failures, warnings):
    """Local scripts are audited once, not once per page that loads them."""
    for path in sorted(glob.glob(os.path.join(DOCS, "*.js"))):
        scan_js(read(path), os.path.basename(path), failures, warnings)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit the JavaScript the site ships.")
    parser.add_argument("--page", help="audit one page by file name")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--strict", action="store_true",
                        help="treat hardening warnings as failures")
    args = parser.parse_args(argv)

    pages = ([args.page] if args.page
             else sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "*.html"))))
    if not pages or not os.path.exists(os.path.join(DOCS, pages[0])):
        print("no pages found", file=sys.stderr)
        return 1

    failures, warnings, hosts = [], [], {}
    for page in pages:
        if page.endswith(".js"):
            scan_js(read(os.path.join(DOCS, page)), page, failures, warnings)
        else:
            audit_page(os.path.join(DOCS, page), failures, warnings, hosts)
    audit_scripts(failures, warnings)

    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "failures": failures,
            "warnings": warnings,
            "third_party_hosts": {h: c for h, c in sorted(hosts.items(), key=lambda kv: -kv[1])},
        }, ensure_ascii=False, indent=2))
        return 1 if failures or (args.strict and warnings) else 0

    print("pages %d | failures %d | warnings %d | third-party hosts %d"
          % (len(pages), len(failures), len(warnings), len(hosts)))
    for line in failures:
        print("  FAIL %s" % line)
    for line in warnings:
        print("  warn %s" % line)
    if hosts:
        print("third-party origins:")
        for host, count in sorted(hosts.items(), key=lambda kv: (-kv[1], kv[0])):
            print("  %-40s %d reference(s)" % (host, count))
    if not failures and not warnings:
        print("nothing to fix")
    return 1 if failures or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
