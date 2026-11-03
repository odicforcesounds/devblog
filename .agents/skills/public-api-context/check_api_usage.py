#!/usr/bin/env python3
"""Audit browser calls to the public APIs allowed by this skill.

Checks HTTPS, the three audited hosts, connect-src/img-src, query-string
secrets, cancellation and a catch path. CORS is a live network property and is
not checked here.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from urllib.parse import parse_qsl, urlsplit

API_HOSTS = {
    "api.artic.edu": {"label": "Art Institute of Chicago", "images": ["www.artic.edu"]},
    "api.dictionaryapi.dev": {"label": "Free Dictionary", "images": []},
    "openlibrary.org": {"label": "Open Library", "images": ["covers.openlibrary.org"]},
}
IMAGE_HOSTS = {
    host: meta["label"]
    for meta in API_HOSTS.values()
    for host in meta["images"]
}
KNOWN_REMOTE = {"en.wikipedia.org", "upload.wikimedia.org", "thumb.wikimedia.org"}
SECRET_KEY = re.compile(
    r"(api[_-]?key|apikey|access[_-]?key|secret|token|password|client[_-]?secret)",
    re.IGNORECASE,
)
CSP_META = re.compile(
    r'<meta[^>]+http-equiv=["\']Content-Security-Policy["\'][^>]+content=(["\'])(.*?)\1',
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_BLOCK = re.compile(
    r"(?is)<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>"
)
FETCH_CALL = re.compile(r"""\bfetch\(\s*["'`](https?://[^"'`]+)["'`]""")
IMG_SRC = re.compile(r"""<img\b[^>]*\bsrc=["'](https?://[^"']+)["']""", re.IGNORECASE)
PROXY_HOST = re.compile(r"(corsproxy|cors-anywhere|allorigins|thingproxy|proxy\.cors)", re.IGNORECASE)


def directive(policy: str, name: str) -> list[str]:
    for part in policy.split(";"):
        bits = part.strip().split()
        if bits and bits[0].lower() == name:
            return bits[1:]
    return []


def allows(policy: str, name: str, host: str) -> bool:
    values = directive(policy, name) or directive(policy, "default-src")
    return "*" in values or host in values or f"https://{host}" in values


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def query_keys(url: str) -> list[str]:
    return [key for key, _ in parse_qsl(urlsplit(url).query, keep_blank_values=True)]


def audit_page(path: str) -> tuple[list[str], list[str], int]:
    source = open(path, encoding="utf-8", errors="replace").read()
    name = path.rsplit("/", 1)[-1]
    failures: list[str] = []
    warnings: list[str] = []
    csp_match = CSP_META.search(source)
    csp = csp_match.group(2) if csp_match else ""
    scripts = "\n".join(SCRIPT_BLOCK.findall(source))
    calls = FETCH_CALL.findall(scripts)
    public_calls = 0

    for url in calls:
        host = host_of(url)
        if not host:
            continue
        if urlsplit(url).scheme.lower() != "https":
            failures.append(f"{name}: non-HTTPS fetch to {url}")
            continue
        if PROXY_HOST.search(host):
            failures.append(f"{name}: CORS proxy fetch to {host}")
            continue
        if host in API_HOSTS:
            public_calls += 1
            label = API_HOSTS[host]["label"]
            if not csp:
                failures.append(f"{name}: {label} fetch without a CSP")
            elif "*" in directive(csp, "connect-src"):
                failures.append(f"{name}: {label} fetch under a wildcard connect-src")
            elif not allows(csp, "connect-src", host):
                failures.append(f"{name}: {label} host {host} is absent from connect-src")
            for key in query_keys(url):
                if SECRET_KEY.search(key):
                    failures.append(f"{name}: {label} query carries a secret-like key {key!r}")
            if "AbortController" not in scripts and "setTimeout" not in scripts:
                warnings.append(f"{name}: {label} fetch has no cancellation or timeout")
            if "catch" not in scripts:
                warnings.append(f"{name}: {label} fetch has no visible catch path")
        elif host in KNOWN_REMOTE:
            continue
        else:
            warnings.append(f"{name}: remote fetch outside the audited trio: {host}")

    for url in IMG_SRC.findall(source):
        host = host_of(url)
        if host in IMAGE_HOSTS and not allows(csp, "img-src", host):
            failures.append(f"{name}: {IMAGE_HOSTS[host]} image host {host} is absent from img-src")

    for host, label in IMAGE_HOSTS.items():
        if host in scripts and not allows(csp, "img-src", host):
            failures.append(f"{name}: {label} image host {host} is absent from img-src")

    return failures, warnings, public_calls


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", action="append", help="limit to a page path or file name")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args()

    paths = sorted(glob.glob("docs/*.html"))
    if args.page:
        wanted = {item.rsplit("/", 1)[-1] for item in args.page}
        paths = [path for path in paths if path.rsplit("/", 1)[-1] in wanted]

    failures: list[str] = []
    warnings: list[str] = []
    public_calls = 0
    for path in paths:
        page_failures, page_warnings, page_calls = audit_page(path)
        failures.extend(page_failures)
        warnings.extend(page_warnings)
        public_calls += page_calls

    report = {
        "pages": len(paths),
        "public_api_calls": public_calls,
        "audited_hosts": sorted(API_HOSTS),
        "failures": failures,
        "warnings": warnings,
        "cors": "not checked offline; verify access-control-allow-origin with an Origin header",
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"pages: {len(paths)} | public-api calls: {public_calls} | "
            f"audited hosts: {len(API_HOSTS)} | failures: {len(failures)} | warnings: {len(warnings)}"
        )
        for item in failures:
            print(f"FAIL {item}")
        for item in warnings:
            print(f"WARN {item}")
        if public_calls:
            print("Note: CORS is a live check; send Origin and require an ACAO header.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
