#!/usr/bin/env python3
"""Prove that every link on the site goes somewhere.

Two passes, deliberately separate because they cost different things:

  local     (default)     offline, milliseconds. Every relative href/src must resolve
                          to a real file inside docs/. This is the pass that catches a
                          renamed page, a stylesheet that was never shipped, a typo
                          like bsdAlternatives.html.html.
  external  (--external)  network, minutes. HEADs a rotating sample of the absolute
                          links and caches the answer in tmp/link-cache.json, so a
                          second run inside the cache window costs nothing.

    python3 .agents/skills/link-integrity/check_links.py
    python3 .agents/skills/link-integrity/check_links.py --external --sample 150
    python3 .agents/skills/link-integrity/check_links.py --json
    python3 .agents/skills/link-integrity/check_links.py --drop-cache

Read-only with respect to the site: it never edits a page. The only file it writes is
the external cache, which lives in the gitignored tmp/.

Exit code 0 when the pass found nothing to fix, 1 when it found a dead link.
"""

import argparse
import glob
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

DOCS = "docs"
CACHE = os.path.join("tmp", "link-cache.json")
CACHE_DAYS = 30
TIMEOUT = 12
WORKERS = 8
USER_AGENT = "Mozilla/5.0 (compatible; devblog-link-integrity/1.0)"
URL_ATTRS = re.compile(r'(?:href|src)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', re.I)
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:', re.I)
SKIP_SCHEME = ("mailto:", "tel:", "data:", "javascript:", "about:", "sms:", "blob:")
ASSET_EXT = {".html", ".htm", ".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".webp",
             ".gif", ".svg", ".ico", ".pdf", ".txt", ".xml", ".avif", ".woff", ".woff2",
             ".mp3", ".mp4", ".webm", ".zip"}
DEAD_STATUS = {404, 410, 451}


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


PLACEHOLDER = ("${", "{{", "}}", "' +", '" +', " + '", "`", "<", "\n")


def refs(source):
    """Every href/src value on the page, unescaped, in document order.

    Values that are JavaScript being concatenated ("…" + x), template literals, or a
    clause of an inline template are not links: they are the string a script will build.
    Counting them reports a page as broken for writing code.
    """
    for match in URL_ATTRS.finditer(source):
        value = match.group(1) if match.group(1) is not None else match.group(2)
        value = html.unescape(value).strip()
        if not value or any(token in value for token in PLACEHOLDER):
            continue
        yield value


def is_external(ref):
    return ref.startswith("//") or bool(SCHEME.match(ref))


def local_path(page, ref):
    """(absolute path inside docs, fragment) for a local reference, or None.

    A bare word with no dot and no slash is not a relative path in practice: it is the
    residue of a template ("user", "page") that a build step fills. Those are counted
    separately as warnings instead of being reported as dead pages.
    """
    if not ref or ref.startswith("#") or is_external(ref):
        return None
    if "." not in ref and "/" not in ref:
        return None
    path, _, fragment = ref.partition("#")
    path = path.split("?")[0]
    if not path:
        return None
    path = urllib.parse.unquote(path)
    if path.startswith("/"):
        target = os.path.normpath(os.path.join(DOCS, path.lstrip("/")))
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(os.path.join(DOCS, page)), path))
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return target, fragment


def ids_in(path):
    try:
        return set(re.findall(r'\bid\s*=\s*"([^"]+)"', read(path)))
    except OSError:
        return set()


def check_local(pages):
    failures, warnings = [], []
    seen, warned = set(), set()
    for page in pages:
        source = read(os.path.join(DOCS, page))
        for ref in refs(source):
            parsed = local_path(page, ref)
            if not parsed:
                continue
            target, fragment = parsed
            if not os.path.exists(target):
                key = (page, ref)
                if key not in seen:
                    seen.add(key)
                    failures.append((page, ref))
                continue
            if fragment and target.endswith(".html") and fragment not in ids_in(target):
                note = "%s#%s — no such id in %s" % (ref, fragment, os.path.basename(target))
                if note not in warned:
                    warned.add(note)
                    warnings.append((page, note))
        for ref in refs(source):
            if not ref or ref.startswith("#") or is_external(ref):
                continue
            if "." not in ref and "/" not in ref:
                warnings.append((page, "%r is not a path — template leftover?" % ref))
    return failures, warnings, None


def collect_external(pages):
    urls = {}
    for page in pages:
        for ref in refs(read(os.path.join(DOCS, page))):
            if not is_external(ref):
                continue
            url = "https:" + ref if ref.startswith("//") else ref
            if url.split(":")[0].lower() + ":" in SKIP_SCHEME:
                continue
            urls.setdefault(url, []).append(page)
    return urls


def load_cache():
    try:
        with open(CACHE, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    temporary = CACHE + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(cache, handle, indent=0, sort_keys=True)
    os.replace(temporary, CACHE)


def fetch_status(url):
    """(status, note). status 0 means the answer could not be verified."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status, ""
        except urllib.error.HTTPError as error:
            if error.code in (403, 405, 429) and method == "HEAD":
                continue
            if error.code in (403, 401, 429):
                return 0, "HTTP %d — refuses automated requests" % error.code
            return error.code, ""
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if method == "HEAD":
                continue
            return 0, "no answer (%s)" % type(error).__name__
    return 0, "no answer"


def check_external(pages, sample, offset, refresh):
    urls = collect_external(pages)
    ordered = sorted(urls, key=lambda u: hashlib.sha1(u.encode("utf-8")).hexdigest())
    cache = {} if refresh else load_cache()
    now = time.time()
    stale = []
    for url in ordered:
        entry = cache.get(url)
        if entry and now - entry.get("at", 0) < CACHE_DAYS * 86400:
            continue
        stale.append(url)
    if sample and sample < len(stale):
        start = (offset % len(stale)) if stale else 0
        stale = (stale + stale)[start:start + sample]

    def work(url):
        status, note = fetch_status(url)
        cache[url] = {"status": status, "note": note, "at": now}
        return url, status, note

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for _ in pool.map(work, stale):
            pass
    if stale:
        save_cache(cache)

    failures, warnings = [], []
    checked = 0
    for url, entry in cache.items():
        if url not in urls:
            continue
        checked += 1
        status, note = entry.get("status", 0), entry.get("note", "")
        if status in DEAD_STATUS:
            failures.append((urls[url][0], "%s — HTTP %d" % (url, status)))
        elif status == 0:
            warnings.append((urls[url][0], "%s — %s" % (url, note or "unverified")))
        elif status >= 500:
            warnings.append((urls[url][0], "%s — HTTP %d (server side)" % (url, status)))
    return failures, warnings, {"urls": len(urls), "checked": checked, "fetched": len(stale)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify that every link resolves.")
    parser.add_argument("--external", action="store_true", help="also sample the absolute links over the network")
    parser.add_argument("--sample", type=int, default=120, help="how many stale external URLs to fetch (0 = all)")
    parser.add_argument("--offset", type=int, default=0, help="start further into the hash-ordered list")
    parser.add_argument("--refresh", action="store_true", help="ignore cached answers")
    parser.add_argument("--drop-cache", action="store_true", help="delete the cache and exit")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if args.drop_cache:
        if os.path.exists(CACHE):
            os.remove(CACHE)
            print("removed %s" % CACHE)
        else:
            print("no cache at %s" % CACHE)
        return 0

    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "*.html")))
    if not pages:
        print("no pages found", file=sys.stderr)
        return 1

    failures, warnings, extra = check_local(pages)
    local = {"pages": len(pages), "dead": len(failures)}
    if args.external:
        e_fail, e_warn, extra = check_external(pages, args.sample, args.offset, args.refresh)
        failures += e_fail
        warnings += e_warn

    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "local_dead": local["dead"],
            "external": extra,
            "failures": [{"page": p, "ref": r} for p, r in failures],
            "warnings": [{"page": p, "note": r} for p, r in warnings],
        }, ensure_ascii=False, indent=2))
        return 1 if failures else 0

    print("pages %d | local references %s | %s"
          % (len(pages), "ok" if not local["dead"] else "%d dead" % local["dead"],
             ("external sampled %(checked)d of %(urls)d, fetched %(fetched)d" % extra) if args.external
             else "external not checked (--external)"))
    if failures:
        print("failures %d" % len(failures))
        for page, ref in failures[:40]:
            print("  %s — %s" % (page, ref))
        if len(failures) > 40:
            print("  … and %d more" % (len(failures) - 40))
    if warnings:
        print("warnings %d" % len(warnings))
        for page, note in warnings[:10]:
            print("  %s — %s" % (page, note))
        if len(warnings) > 10:
            print("  … and %d more" % (len(warnings) - 10))
    if not failures and not warnings:
        print("nothing to fix")
    elif not failures:
        print("no failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
