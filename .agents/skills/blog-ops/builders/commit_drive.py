#!/usr/bin/env python3
"""Build the answers file for .agents/skills/blog-ops/commitit.sh.

One answer per changed file: accept it, then give it a message that names what
changed in that file. Nothing is committed here; commitit.sh does the commits.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))

SPECIAL = {
    "AGENTS.md": "Point agents at the link-colours and page-css skills in the task table",
    ".agents/skills/tools-index/SKILL.md": "Index the two new skills' scripts so every tool still has a known path",
    ".agents/skills/living-panel/living_panel.py": "Leave plants out of the card pool and give the card a bigger frame",
    ".agents/skills/living-panel/SKILL.md": "Record that the plant catalogue is left out and the card frame grew",
    "docs/living-panel.js": "Rebuild the card pool without the plant catalogue",
    "docs/page.css": "Add page.css, the sheet that replaces article.css with a wider, calmer reading column",
    "docs/link-colors.css": "Add the stylesheet that colours a link by where it leads",
    ".agents/skills/link-colors/": "Add the link-colours skill: blue inside the blog, gold to the art site, pink outside",
    ".agents/skills/page-css/": "Add the page-css skill so every page can share one improved sheet",
    "docs/api/index.json": "Record the corrected title of simplicity.html in the API",
    "docs/api/text/008.json": "Re-export the article text chunk that holds simplicity.html",
    "docs/sitemap.xml": "Refresh lastmod after the simplicity.html title fix",
    ".gitignore": "Ignore the build_check scratch copy so it never lands in a commit",
    "docs/lifeIndex.html": "Drop the lucky-button form and the notes section, leaving the five catalogue doors",
    "docs/simplicity.html": "Replace the template title \"Warning\" with the article's real title in all five places",
}


def changed_paths():
    raw = subprocess.run(
        ["git", "-C", ROOT, "status", "--porcelain=v1", "-z"],
        capture_output=True,
    ).stdout.decode("utf-8", "replace").split("\0")
    out, skip = [], False
    for entry in raw:
        if not entry:
            continue
        if skip:
            skip = False
            continue
        if entry[0] in "RC":
            out.append(entry[3:])
            skip = True
        else:
            out.append(entry[3:])
    return [p for p in out if p]


def types_of(path):
    diff = subprocess.run(
        ["git", "-C", ROOT, "diff", "--unified=0", "--", path],
        capture_output=True,
    ).stdout.decode("utf-8", "replace")
    return {
        "swap": '-<link rel="stylesheet" href="article.css">' in diff,
        "colours": "+<link rel=\"stylesheet\" href=\"link-colors.css\">" in diff,
        "frame": "width:12.5rem" in diff,
        "pair": "likes to use" in diff,
        "published": "article:published_time" in diff,
    }


def message_for(path):
    if path in SPECIAL:
        return SPECIAL[path]
    if not (path.startswith("docs/") and path.endswith(".html")):
        return "Update %s with the current change" % path
    name = path.split("/")[-1]
    t = types_of(path)
    parts = []
    if t["swap"]:
        parts.append("serve it from page.css instead of article.css")
    if t["colours"]:
        parts.append("colour its links by destination")
    if t["frame"]:
        parts.append("widen the living card")
    if t["pair"]:
        parts.append("re-pick its card pair now that plants left the pool")
    if t["published"]:
        parts.append("take article:published_time from its own JSON-LD date")
    if not parts:
        parts.append("carry the current markup fix")
    return "%s: %s" % (name, ", ".join(parts))


def main():
    paths = changed_paths()
    lines = []
    for p in paths:
        lines.append("y")
        lines.append(message_for(p))
    lines.append("y")
    answers = "\n".join(lines) + "\n"
    with open(os.path.join(ROOT, "tmp", "commit_answers.txt"), "w", encoding="utf-8") as fh:
        fh.write(answers)
    print("answers for", len(paths), "files")
    for p in paths:
        print(" ", p, "->", message_for(p)[:100])


if __name__ == "__main__":
    main()
