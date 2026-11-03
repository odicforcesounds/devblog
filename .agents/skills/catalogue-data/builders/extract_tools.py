#!/usr/bin/env python3
"""Extract every linked tool from the 113 awesome-list READMEs (tmp/readmes/).

Writes tmp/tools.json as {group: [{repo, list, url, tools: [{name, url, desc}]}]}
and prints the size of each subject so the pages can be chunked sensibly.
"""

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import html
import json
import os
import re

INDEX = "docs/awesomeIndex.html"
REPOS = "tmp/repos.txt"
OUT = "tmp/tools.json"

BAD_URL = re.compile(r"shields\.io|badge|travis-ci|circleci|appveyor|codecov|"
                     r"awesome\.re|opencollective|patreon|paypal", re.I)
BAD_NAME = {
    "awesome", "back to top", "top", "↑", "contents", "index", "here",
    # generic project-header links that are not tools
    "documentation", "docs", "discord", "github", "paper", "website", "blog",
    "twitter", "telegram", "slack", "matrix", "mailing list", "mail", "e-mail",
    "contributing", "license", "licence", "changelog", "releases", "sponsor",
    "donate", "issues", "discussions", "stars", "star", "chat", "community",
    "npm", "pypi", "crates.io", "docker hub", "youtube", "reddit", "mastodon",
    "forum", "roadmap", "wiki", "readme", "homepage", "demo", "download",
}


def clean(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def group_lists():
    """Group key -> [(display name, repo url)] in the order the index shows them."""
    src = open(INDEX, encoding="utf-8").read()
    en = src.split('id="lang-pt"')[0]
    groups = {}
    for m in re.finditer(r'<section class="grp" id="section-([a-z]+)">(.*?)</section>', en, re.S):
        key, block = m.group(1), m.group(2)
        items = []
        for row in re.finditer(r'<td><a href="(https://github\.com/[^"]+)"[^>]*>([^<]+)</a>', block):
            items.append((html.unescape(row.group(2)), row.group(1)))
        groups[key] = items
    return groups


def main():
    slug = {}
    for line in open(REPOS, encoding="utf-8"):
        r = line.strip()
        if r:
            slug[r.replace("/", "_")] = r

    groups = group_lists()
    data = {}
    for key, items in groups.items():
        out = []
        for name, url in items:
            repo = url.replace("https://github.com/", "")
            path = "tmp/readmes/%s.md" % repo.replace("/", "_")
            text = open(path, encoding="utf-8", errors="replace").read() if os.path.exists(path) else ""
            tools, seen = [], set()
            for line in text.splitlines():
                m = re.match(r"^\s*[-*+]\s+\[([^\]]+)\]\((https?://[^)\s]+)\)(.*)$", line)
                if not m:
                    continue
                label, link, rest = m.group(1), m.group(2), m.group(3)
                label = clean(label)
                if not label or len(label) > 90 or label.lower() in BAD_NAME:
                    continue
                if link in seen or BAD_URL.search(link):
                    continue
                desc = clean(rest.strip(" -–—:|·"))
                if len(desc) > 180:
                    desc = desc[:177].rstrip() + "…"
                seen.add(link)
                tools.append({"name": label, "url": link, "desc": desc})
            out.append({"repo": repo, "list": name, "url": url, "tools": tools})
        data[key] = out

    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)

    total = 0
    for key, lists in data.items():
        n = sum(len(l["tools"]) for l in lists)
        total += n
        biggest = sorted(((len(l["tools"]), l["list"]) for l in lists), reverse=True)[:3]
        print("%-9s lists=%2d tools=%5d  biggest=%s" % (key, len(lists), n, biggest))
    print("total tools:", total)


if __name__ == "__main__":
    main()
