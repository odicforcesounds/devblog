#!/usr/bin/env python3
"""Guard the fifteen docs/*Index.html catalogue pages.

Read-only. Checks local search and data, head contract, living panel, CSP,
remote scripts, proxy use, secret-like queries and API fallback.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

EXPECTED = {
    "animalsIndex.html",
    "awesomeIndex.html",
    "birdsIndex.html",
    "carsIndex.html",
    "catsIndex.html",
    "danceIndex.html",
    "dogsIndex.html",
    "electronicsIndex.html",
    "fishesIndex.html",
    "gamesIndex.html",
    "insectsIndex.html",
    "lifeIndex.html",
    "marketsIndex.html",
    "pianosIndex.html",
    "plantsIndex.html",
    "religionsIndex.html",
    "reptilesIndex.html",
    "rocksIndex.html",
    "worldIndex.html",
}
NO_DATA = {"lifeIndex.html", "reptilesIndex.html"}
DATA_DIR = {
    "animalsIndex.html": "animals",
    "awesomeIndex.html": "awesome",
    "birdsIndex.html": "birds",
    "carsIndex.html": "cars",
    "catsIndex.html": "cats",
    "danceIndex.html": "dance",
    "dogsIndex.html": "dogs",
    "electronicsIndex.html": "electronics",
    "fishesIndex.html": "fishes",
    "gamesIndex.html": "games",
    "insectsIndex.html": "insects",
    "marketsIndex.html": "markets",
    "pianosIndex.html": "pianos",
    "plantsIndex.html": "plants",
    "religionsIndex.html": "religions",
    "rocksIndex.html": "rocks",
    "worldIndex.html": "world",
}
TITLE = re.compile(r"(?is)<title\b[^>]*>(.*?)</title>")
H1 = re.compile(r"(?is)<h1\b[^>]*>(.*?)</h1>")
CANONICAL = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
CSP_META = re.compile(
    r'<meta[^>]+http-equiv=["\']Content-Security-Policy["\'][^>]+content=(["\'])(.*?)\1',
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_BLOCK = re.compile(
    r"(?is)<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>"
)
EXTERNAL_SCRIPT = re.compile(
    r'<script\b[^>]*\bsrc=["\']https?://[^"\']+["\']',
    re.IGNORECASE,
)
FETCH_CALL = re.compile(r"""\bfetch\(\s*["'`](https?://[^"'`]+)["'`]""")
SEARCH_INPUT = re.compile(r'<input\b[^>]*\btype=["\']search["\']', re.IGNORECASE)
PANEL_CLASS = re.compile(r'class=["\']living-panel["\']', re.IGNORECASE)
PANEL_STYLE = re.compile(r'id=["\']living-panel-style["\']', re.IGNORECASE)
PANEL_SCRIPT = re.compile(r'src=["\']living-panel\.js["\']', re.IGNORECASE)
PANEL_TOP = re.compile(r"\.living-panel\{[^}]*\btop\s*:\s*(\d+)px", re.IGNORECASE)
SECRET_KEY = re.compile(
    r"(api[_-]?key|apikey|access[_-]?key|secret|token|password|client[_-]?secret)",
    re.IGNORECASE,
)
PROXY_HOST = re.compile(r"(corsproxy|cors-anywhere|allorigins|thingproxy|proxy\.cors)", re.IGNORECASE)


def meta_content(source: str, key: str) -> str:
    for match in re.finditer(r"<meta\b[^>]*>", source, re.IGNORECASE):
        tag = match.group(0)
        if re.search(
            rf'\b(?:name|property)=["\']{re.escape(key)}["\']',
            tag,
            re.IGNORECASE,
        ):
            content = re.search(r'\bcontent=(["\'])(.*?)\1', tag, re.IGNORECASE | re.DOTALL)
            if content:
                return content.group(2)
    return ""


def directive(policy: str, name: str) -> list[str]:
    for part in policy.split(";"):
        bits = part.strip().split()
        if bits and bits[0].lower() == name:
            return bits[1:]
    return []


def allows(policy: str, name: str, host: str) -> bool:
    values = directive(policy, name) or directive(policy, "default-src")
    return "*" in values or host in values or f"https://{host}" in values


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def audit(path: Path) -> tuple[list[str], list[str]]:
    name = path.name
    source = path.read_text(encoding="utf-8", errors="replace")
    failures: list[str] = []
    warnings: list[str] = []

    titles = TITLE.findall(source)
    if len(titles) != 1:
        failures.append(f"{name}: expected one title, found {len(titles)}")
    headings = H1.findall(source)
    if len(headings) != 1 or not strip_tags(headings[0]):
        failures.append(f"{name}: expected one non-empty h1, found {len(headings)}")

    description = meta_content(source, "description")
    if not 110 <= len(description) <= 155:
        failures.append(
            f"{name}: description is {len(description)} characters, expected 110-155"
        )

    canonical = CANONICAL.search(source)
    expected_canonical = f"https://blog.odicforcesounds.com/{name}"
    if not canonical:
        failures.append(f"{name}: canonical is missing")
    elif canonical.group(1) != expected_canonical:
        failures.append(f"{name}: canonical is {canonical.group(1)!r}, expected {expected_canonical!r}")

    csp_match = CSP_META.search(source)
    csp = csp_match.group(2) if csp_match else ""
    if not csp:
        failures.append(f"{name}: Content-Security-Policy is missing")
    else:
        if "'self'" not in directive(csp, "default-src"):
            failures.append(f"{name}: default-src does not contain 'self'")
        for policy_name in ("default-src", "connect-src", "img-src", "script-src"):
            if "*" in directive(csp, policy_name):
                failures.append(f"{name}: wildcard in {policy_name}")

    if len(PANEL_CLASS.findall(source)) != 1:
        failures.append(f"{name}: expected one living-panel block")
    if len(PANEL_STYLE.findall(source)) != 1:
        failures.append(f"{name}: expected one living-panel-style block")
    if len(PANEL_SCRIPT.findall(source)) != 1:
        failures.append(f"{name}: expected one living-panel.js script")
    top = PANEL_TOP.search(source)
    if not top:
        failures.append(f"{name}: living-panel top is missing")
    elif top.group(1) != "60":
        failures.append(f"{name}: living-panel top is {top.group(1)}px, expected 60px")

    if SEARCH_INPUT.search(source):
        pass
    else:
        warnings.append(f"{name}: no type=search input")

    if "noindex" in meta_content(source, "robots").lower():
        failures.append(f"{name}: catalogue is marked noindex")

    if EXTERNAL_SCRIPT.search(source):
        failures.append(f"{name}: remote script tag is not allowed")

    scripts = "\n".join(SCRIPT_BLOCK.findall(source))
    calls = FETCH_CALL.findall(scripts)
    for url in calls:
        host = (urlsplit(url).hostname or "").lower()
        if not host:
            continue
        if urlsplit(url).scheme.lower() != "https":
            failures.append(f"{name}: non-HTTPS fetch to {url}")
            continue
        if PROXY_HOST.search(host):
            failures.append(f"{name}: CORS proxy fetch to {host}")
            continue
        if csp and not allows(csp, "connect-src", host):
            failures.append(f"{name}: fetch host {host} is absent from connect-src")
        for key, _ in parse_qsl(urlsplit(url).query, keep_blank_values=True):
            if SECRET_KEY.search(key):
                failures.append(f"{name}: fetch query carries a secret-like key {key!r}")

    directory = DATA_DIR.get(name)
    if directory and not (Path("docs") / directory / "data" / "index.json").is_file():
        warnings.append(f"{name}: local data manifest docs/{directory}/data/index.json is missing")
    elif name in NO_DATA:
        warnings.append(f"{name}: no local data manifest by design")

    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", help="limit to one index file")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args()

    if args.page:
        path = Path(args.page)
        if not path.is_file():
            path = Path("docs") / Path(args.page).name
        paths = [path]
    else:
        paths = [Path(item) for item in sorted(glob.glob("docs/*Index.html"))]

    failures: list[str] = []
    warnings: list[str] = []
    seen = {path.name for path in paths}
    if args.page:
        for extra in sorted(seen - EXPECTED):
            warnings.append(f"{extra}: index page outside the guarded seventeen")
    else:
        for missing in sorted(EXPECTED - seen):
            failures.append(f"{missing}: expected index page is missing")
        for extra in sorted(seen - EXPECTED):
            warnings.append(f"{extra}: index page outside the guarded seventeen")

    for path in paths:
        page_failures, page_warnings = audit(path)
        failures.extend(page_failures)
        warnings.extend(page_warnings)

    report = {
        "indexes": len(paths),
        "failures": failures,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"indexes: {len(paths)} | failures: {len(failures)} | warnings: {len(warnings)}")
        for item in failures:
            print(f"FAIL {item}")
        for item in warnings:
            print(f"WARN {item}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
