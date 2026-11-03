#!/usr/bin/env python3
"""Check that the comment sign-in chain on docs/index.html is still complete.

The Google button is created at runtime, so this reads the page and follows the
chain instead of looking for a Google button in the HTML:

  comment-providers -> Firebase imports -> firebaseConfig -> renderProviders()
  -> GoogleAuthProvider -> signInWithPopup -> CSP permissions.

    python3 .agents/skills/comments-auth/check_comments_auth.py
    python3 .agents/skills/comments-auth/check_comments_auth.py --live
    python3 .agents/skills/comments-auth/check_comments_auth.py --json

Read-only. Exit code 0 when no failure remains, 1 otherwise.
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

PAGE = "docs/index.html"
POLICY = re.compile(r'<meta[^>]+http-equiv\s*=\s*"Content-Security-Policy"[^>]*>', re.I)
TAG_ATTRIBUTE = re.compile(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"')
CONFIG = re.compile(r'(?:const|let|var)\s+firebaseConfig\s*=\s*\{(.*?)\};', re.S)
CONFIG_FIELD = re.compile(r'(\w+)\s*:\s*"([^"]*)"')
PROVIDERS = re.compile(r'AUTH_PROVIDERS\s*=\s*\[(.*?)\];', re.S)
PROVIDER_ID = re.compile(r'\bid\s*:\s*"([^"]+)"')
AVATARS = re.compile(r'AVATAR_HOSTS\s*=\s*\[(.*?)\];', re.S)
AVATAR_VALUE = re.compile(r'"([^"]+)"')
IMPORT = re.compile(r'https://www\.gstatic\.com/firebasejs/([^/]+)/firebase-(app|auth|firestore)\.js')

REQUIRED_IMPORTS = {
    "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js",
    "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js",
    "https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js",
}

REQUIRED_AUTH_SYMBOLS = [
    "GoogleAuthProvider",
    "signInWithPopup",
    "signInWithRedirect",
    "onAuthStateChanged",
    "renderProviders();",
]


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_policy(source):
    tag = POLICY.search(source)
    if not tag:
        return None
    attributes = {key.lower(): html.unescape(value) for key, value in TAG_ATTRIBUTE.findall(tag.group(0))}
    content = attributes.get("content", "")
    directives = {}
    for part in content.split(";"):
        tokens = part.split()
        if tokens:
            directives[tokens[0].lower()] = tokens[1:]
    return directives


def source_allows(sources, url):
    if not sources or "'none'" in sources:
        return False
    parsed = urllib.parse.urlsplit(url)
    local = not parsed.scheme and not url.startswith("//")
    origin = "%s://%s" % (parsed.scheme, parsed.netloc) if parsed.netloc else ""
    for source in sources:
        lower = source.lower()
        if lower == "*":
            return True
        if lower == "'self'":
            if local:
                return True
            continue
        if lower.startswith("'"):
            continue
        if source.startswith("//"):
            source = "https:" + source
        if local:
            continue
        candidate = source.rstrip("/")
        if candidate.startswith("*."):
            suffix = candidate[1:].lower()
            if parsed.hostname and origin.lower().endswith(suffix):
                return True
            continue
        if candidate.startswith("wss://*.") or candidate.startswith("https://*."):
            suffix = candidate.split("*.", 1)[1].lower()
            if parsed.hostname and (parsed.hostname.lower() == suffix or parsed.hostname.lower().endswith("." + suffix)):
                return True
            continue
        if candidate.lower() == origin.lower():
            return True
        if re.match(r'^[a-z][a-z0-9+.-]*:$', lower) and url.lower().startswith(lower):
            return True
    return False


def check_csp(source, failures, warnings):
    policy = parse_policy(source)
    if policy is None:
        failures.append("no Content-Security-Policy meta")
        return
    script_sources = policy.get("script-src", policy.get("default-src", []))
    connect_sources = policy.get("connect-src", policy.get("default-src", []))
    frame_sources = policy.get("frame-src", policy.get("default-src", []))
    image_sources = policy.get("img-src", policy.get("default-src", []))

    if "'unsafe-eval'" in script_sources:
        failures.append("script-src contains 'unsafe-eval'")
    if not source_allows(script_sources, "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"):
        failures.append("script-src does not allow https://www.gstatic.com")
    if "'unsafe-inline'" not in script_sources:
        failures.append("script-src does not allow the page's inline module script")

    for url in [
        "https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri",
        "https://securetoken.googleapis.com/v1/token",
        "https://firestore.googleapis.com/v1/projects/blog-comments-6b4f5/databases/(default)/documents",
        "https://blog-comments-6b4f5.firebaseapp.com/__/auth/handler",
        "wss://blog-comments-6b4f5.firebaseio.com/",
    ]:
        if not source_allows(connect_sources, url):
            failures.append("connect-src does not allow %s" % urllib.parse.urlsplit(url).netloc)

    for url in [
        "https://blog-comments-6b4f5.firebaseapp.com/__/auth/handler",
        "https://accounts.google.com/",
    ]:
        if not source_allows(frame_sources, url):
            failures.append("frame-src does not allow %s" % urllib.parse.urlsplit(url).netloc)

    default_sources = policy.get("default-src", [])
    if "'self'" not in default_sources and "*" not in default_sources:
        warnings.append("default-src is neither 'self' nor *")
    if "object-src" not in policy:
        warnings.append("no object-src")
    if "base-uri" not in policy:
        warnings.append("no base-uri")


def check_avatars(source, image_sources, failures, warnings):
    avatars_match = AVATARS.search(source)
    if not avatars_match:
        warnings.append("AVATAR_HOSTS is absent; avatar host parity is not checked")
        return
    hosts = AVATAR_VALUE.findall(avatars_match.group(1))
    for host in hosts:
        url = "https://" + host.strip("/")
        if not source_allows(image_sources, url):
            failures.append("img-src does not allow avatar host %s" % host)


def check_page(source, failures, warnings):
    for token in ['id="comment-providers"', 'id="comment-form"', 'id="comment-submit"', 'id="comment-signin"']:
        if token not in source:
            failures.append("missing %s" % token)

    if re.search(r'<button[^>]*id="comment-submit"[^>]*\bdisabled\b', source) is None:
        failures.append("comment-submit does not start disabled")
    if 'data-locked="true"' not in source:
        failures.append("comment form does not start locked")

    providers_match = PROVIDERS.search(source)
    if not providers_match:
        failures.append("AUTH_PROVIDERS is absent")
        providers = []
    else:
        providers = PROVIDER_ID.findall(providers_match.group(1))
        if "google.com" not in providers:
            failures.append("AUTH_PROVIDERS does not contain google.com")
        extra = sorted(set(providers) - {"google.com", "password"})
        if extra:
            warnings.append("providers beyond google.com and password: %s" % ", ".join(extra))

    for symbol in REQUIRED_AUTH_SYMBOLS:
        if symbol not in source:
            failures.append("missing %s" % symbol)

    imports = set(IMPORT.findall(source))
    for url in sorted(REQUIRED_IMPORTS):
        if url not in source:
            failures.append("missing Firebase import %s" % url)
    versions = sorted({version for version, module in imports})
    if len(versions) > 1:
        failures.append("Firebase imports use different versions: %s" % ", ".join(versions))

    config_match = CONFIG.search(source)
    if not config_match:
        failures.append("firebaseConfig is absent")
        return {}, providers
    fields = dict(CONFIG_FIELD.findall(config_match.group(1)))
    for field in ("apiKey", "authDomain", "projectId", "appId"):
        if not fields.get(field):
            failures.append("firebaseConfig is missing %s" % field)
    project = fields.get("projectId", "")
    auth_domain = fields.get("authDomain", "")
    if project and auth_domain and auth_domain != project + ".firebaseapp.com":
        failures.append("authDomain %s does not match projectId %s" % (auth_domain, project))

    lowered = source.lower()
    for secret in ("private_key", "client_secret", "service_account", "begin private key"):
        if secret in lowered:
            failures.append("page contains a secret marker: %s" % secret)

    return fields, providers


def live_checks(fields, failures):
    key = fields.get("apiKey")
    if not key:
        failures.append("live check skipped: no apiKey")
        return
    payload = json.dumps({
        "identifier": "probe@example.com",
        "continueUri": "https://blog.odicforcesounds.com/",
        "providerId": "google.com",
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key=" + urllib.parse.quote(key),
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
        data = json.loads(body)
        uri = data.get("authUri", "")
        if "accounts.google.com" not in uri:
            failures.append("Firebase google.com createAuthUri did not return a Google authUri")
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        failures.append("Firebase google.com createAuthUri failed: %s" % error)

    for url in sorted(REQUIRED_IMPORTS):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                if response.status != 200:
                    failures.append("%s answered %s" % (url, response.status))
        except (urllib.error.URLError, TimeoutError) as error:
            failures.append("%s could not be fetched: %s" % (url, error))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check the index.html comment sign-in chain.")
    parser.add_argument("--live", action="store_true", help="also query Firebase and fetch the SDK modules")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        source = read(PAGE)
    except OSError as error:
        print("could not read %s: %s" % (PAGE, error), file=sys.stderr)
        return 1

    failures, warnings = [], []
    policy = parse_policy(source)
    fields, providers = check_page(source, failures, warnings)
    check_csp(source, failures, warnings)
    image_sources = policy.get("img-src", policy.get("default-src", [])) if policy else []
    check_avatars(source, image_sources, failures, warnings)

    if args.live:
        live_checks(fields, failures)

    result = {
        "page": PAGE,
        "project": fields.get("projectId", ""),
        "providers": providers,
        "live": bool(args.live),
        "failures": failures,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("%s | project %s | providers %s | live %s"
              % (PAGE, result["project"] or "?", ", ".join(providers) or "none",
                 "yes" if args.live else "no"))
        print("failures %d | warnings %d" % (len(failures), len(warnings)))
        for item in failures:
            print("  FAIL %s" % item)
        for item in warnings:
            print("  WARN %s" % item)
        if not failures:
            print("no failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
