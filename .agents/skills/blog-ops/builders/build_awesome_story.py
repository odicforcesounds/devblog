#!/usr/bin/env python3
"""Rebuild docs/awesome_story.html as a story of Awesome people.

The page is one continuous line: it opens with someone who discovers a computer,
then follows the shelves he meets, the people who join him, and the directions they
take. Every tool and list behind docs/awesomeIndex.html is one sentence, and the
link in each sentence is the word "awesome".
"""

from __future__ import annotations

import os as _os

_os.chdir(_os.path.abspath(_os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)),
    "..", "..", "..", "..")))

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "docs" / "awesome" / "data"
STORY = ROOT / "docs" / "awesome_story.html"
OUT = ROOT / "tmp" / "story.html"

A = '<a class="external" target="_blank" href="{href}" rel="noopener noreferrer">awesome</a>'

FLAT_LABELS = {
    "quozd/awesome-dotnet": ".NET",
    "vsouza/awesome-ios": "iOS",
    "rockerBOO/awesome-neovim": "Neovim",
    "awesome-dsh-plugin/awesome-dsh-plugin": "the DeepSeek harness",
    "rothgar/awesome-tuis": "the terminal UI",
    "jondot/awesome-react-native": "React Native",
    "pluja/awesome-privacy": "privacy-respecting services",
    "wasabeef/awesome-android-ui": "Android UI",
}

# The arc: discovery, language, machines, people, divergence. Each connector is
# narration only; the sentences after it carry the links.
PHASES = [
    (
        "It starts with one person, a machine that only answers in errors, and a terminal that "
        "does not explain itself.",
        ["Shell, terminal and one-liners", "Collections of awesome Neovim plugins",
         "Projects that provide terminal user interfaces"],
    ),
    (
        "The terminal stops being a box and becomes a language, and the languages multiply faster "
        "than he can learn them.",
        ["Languages and frameworks", ".NET libraries, tools and frameworks"],
    ),
    (
        "Then the machine is no longer on the desk: it is the server, the container, the cable and "
        "the archive that outlive it.",
        ["Servers, containers and self-hosting", "Data, networks and archives"],
    ),
    (
        "By now the work is not his alone: people appear, first one, then a few, then strangers who "
        "correct his mistakes.",
        ["Security, privacy and forensics",
         "Services and alternatives that respect your privacy",
         "Learning, careers and collections"],
    ),
    (
        "And then everyone goes somewhere else: the browser, the phone, the model, the drawing, the "
        "life that starts when the lid closes.",
        ["Web, design and product", "Android UI/UX libraries and resources",
         "A curated list of iOS ecosystem libraries and resources",
         "React Native components, news and tooling", "AI and automation",
         "Plugins for the DeepSeek Harness (dsh)", "Beyond code"],
    ),
]

PATTERNS = [
    "The {n} people work with {a} skill: {d}, {c} entries, and the next reader starts there.",
    "Somebody did the {n} reading with {a} patience: {d}, {c} entries sorted against the clock.",
    "Around {n} there is an {a} habit — {d} — and {c} entries left open for whoever comes next.",
    "Whoever lives in {n} writes it down with {a} care: {d}, {c} places set for strangers.",
    "For {n} the {a} part is not the tool but the writing down: {d}, {c} entries long.",
    "The {n} shelf was stocked with {a} stubbornness: {d} — {c} entries, none of them an advertisement.",
    "It is {a} how much of {n} is only a list: {d}, {c} entries, one apology per shortcut.",
    "Even {n} has its own {a} version of the story: {d} — {c} entries and a door left open.",
    "Ask the {n} crowd and they hand you an {a} list instead of advice: {d}, {c} entries of it.",
    "There is an {a} honesty in the {n} list: {d}, and {c} entries that admit the job is not finished.",
    "The {n} chapter is written with {a} endurance: {d} — {c} entries, edited by everyone who was annoyed.",
    "Nobody finishes {n}, they only keep an {a} list of where they stopped: {d}, {c} entries in.",
]

ZERO_PATTERNS = [
    "The {n} people work with {a} skill: {d}.",
    "For {n} the {a} part is not the tool but the writing down: {d}.",
    "Around {n} there is an {a} habit: {d}, left open for whoever comes next.",
    "Whoever lives in {n} writes it down with {a} care: {d}, and never counts it.",
    "The {n} shelf was stocked with {a} stubbornness: {d} — none of them an advertisement.",
    "Even {n} has its own {a} version of the story: {d}, and a door left open.",
]

TOOL_PATTERNS = [
    "{n} sits inside {l} with an {a} note: {d}.",
    "{n} is one more line in {l}, {a} and specific: {d}.",
    "Then there is {n} — {a}, filed under {l} with the sentence {d}.",
    "{n} made the cut with {a} modesty: {d}.",
    "Somebody wrote {n} into {l} with {a} brevity: {d}.",
    "The {l} list also keeps {n}, {a} and unglamorous: {d}.",
    "{n} is there for the afternoon it saves — {a}, {d}.",
    "And {n}: {a}, {d}.",
]

TOOL_SHORT_PATTERNS = [
    "{n} is filed under {l} with an {a} one-liner and no explanation.",
    "And {n} — {a}, and that is the whole introduction.",
    "{n} also appears in {l}, {a}, small and enough.",
    "There is {n} too: {a}, and the name is the argument.",
    "{n} is listed in {l} with {a} brevity and nothing else.",
    "Somebody added {n} to {l} with {a} finality.",
    "{n} keeps its place in {l} with {a} indifference.",
    "Then {n}: {a}, no ceremony, some use.",
]

FLAT_PATTERNS = [
    "The whole {label} corner is one {a} repository — {c} entries, from {s1} and {s2} down to {s3}, and still growing.",
    "{Label} lives in a single {a} drawer here: {c} entries, with {s1}, {s2}, {s3} and the rest of the alphabet inside.",
]

STOPWORDS = {
    "the", "a", "an", "this", "these", "one", "every", "curated", "awesome",
    "scripts", "terminal", "tools", "resources", "collections", "projects",
    "documentation", "libraries", "cheat", "hand", "list", "protocols",
}

anchor_data = {"href": ""}


def clean(text: str) -> str:
    text = html.escape(" ".join(str(text or "").split()), quote=False)
    return re.sub(r"\.$", "", text)


def count(n: int) -> str:
    return f"{n:,}"


def anchor() -> str:
    return A.format(href=html.escape(anchor_data["href"], quote=True))


def soften(desc: str) -> str:
    head = re.match(r"([A-Z][a-z]+)\b", desc)
    if head and head.group(1).lower() in STOPWORDS:
        return desc[0].lower() + desc[1:]
    return desc


def list_sentence(name: str, desc: str, entries: int, toc: list[str], seed: int) -> str:
    detail = soften(desc or ", ".join(clean(x) for x in toc[:3]) or "everything else")
    if entries:
        return PATTERNS[seed % len(PATTERNS)].format(n=name, a=anchor(), d=detail, c=count(entries))
    return ZERO_PATTERNS[seed % len(ZERO_PATTERNS)].format(n=name, a=anchor(), d=detail)


def tool_sentence(name: str, desc: str, list_name: str, seed: int) -> str:
    if desc:
        return TOOL_PATTERNS[seed % len(TOOL_PATTERNS)].format(
            n=name, a=anchor(), l=list_name, d=soften(desc))
    return TOOL_SHORT_PATTERNS[seed % len(TOOL_SHORT_PATTERNS)].format(
        n=name, a=anchor(), l=list_name)


def build() -> tuple[dict[str, list[str]], int, dict[str, int]]:
    index = json.loads((DATA / "index.json").read_text(encoding="utf-8"))
    seen: set[str] = set()
    buckets: dict[str, list[str]] = {}
    total = 0

    for category in index["categories"]:
        data = json.loads((DATA / f"{category['slug']}.json").read_text(encoding="utf-8"))
        entries = data.get("lists", [])
        if not entries:
            continue
        repos = {entry.get("r", "") for entry in entries if entry.get("r")}
        flat = len(repos) == 1 and not any(entry.get("w") for entry in entries)
        bucket: list[str] = []

        if flat:
            repo = next(iter(repos))
            href = f"https://github.com/{repo}"
            if href in seen:
                continue
            anchor_data["href"] = href
            label = FLAT_LABELS.get(repo) or clean(category["title"])
            words = [clean(entry.get("n", "")) for entry in entries if entry.get("n")]
            picks = words[:1] + [words[len(words) // 3]] + words[-1:] if len(words) > 2 else (words + ["the first entry"])[:3]
            template = FLAT_PATTERNS[total % len(FLAT_PATTERNS)]
            bucket.append(template.format(label=label, Label=label[0].upper() + label[1:],
                                          a=anchor(), c=count(len(entries)),
                                          s1=picks[0], s2=picks[1], s3=picks[2]))
            seen.add(href)
            total += 1
            for entry in entries:
                url = (entry.get("u") or "").strip()
                if not url.startswith("http") or url in seen:
                    continue
                anchor_data["href"] = url
                bucket.append(tool_sentence(clean(entry.get("n") or "this"),
                                            clean(entry.get("w") or ""), label, total))
                seen.add(url)
                total += 1
        else:
            for entry in entries:
                href = (entry.get("u") or "").strip()
                if not href.startswith("http") or href in seen:
                    continue
                name = clean(entry.get("n") or entry.get("r") or "this")
                anchor_data["href"] = href
                toc = (entry.get("toc") or {}).get("names") or []
                desc = clean(entry.get("w") or "")
                entries_n = int(entry.get("c") or 0) or int((entry.get("toc") or {}).get("e") or 0)
                bucket.append(list_sentence(name, desc, entries_n, toc, total))
                seen.add(href)
                total += 1
                for part in entry.get("d") or []:
                    for tool in part.get("c") or []:
                        url = (tool.get("u") or "").strip()
                        if not url.startswith("http") or url in seen:
                            continue
                        anchor_data["href"] = url
                        bucket.append(tool_sentence(clean(tool.get("n") or "this"),
                                                    clean(tool.get("d") or ""), name, total))
                        seen.add(url)
                        total += 1

        buckets[category["title"]] = bucket

    return buckets, total, {"categories": len(buckets)}


def main() -> None:
    buckets, total, meta = build()

    parts: list[str] = []
    used: set[str] = set()
    for connector, titles in PHASES:
        parts.append(connector)
        for title in titles:
            if title in buckets and title not in used:
                parts.append(" ".join(buckets[title]))
                used.add(title)
    for title, sentences in buckets.items():
        if title not in used:
            parts.append(" ".join(sentences))

    closing = (
        "Nobody finishes this list, they only keep adding to it: the tools are the people, and the "
        "people are the story. All of them, sorted by subject with one line each: "
        "<a href=\"awesomeIndex.html\">the Awesome Index</a>."
    )

    original = STORY.read_text(encoding="utf-8")
    head = original[: original.index("</head>") + len("</head>")]
    footer = original[original.index("<footer>"):]
    page = (
        head
        + "\n<body>\n  <header>\n  <h1 class=\"title1\">The Awesome Story</h1>\n  </header>\n"
        + '  <div id="story" class="textbox black">' + " ".join(parts) + " " + closing + "</div>\n"
        + footer
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"links: {total}  categories: {meta['categories']}  phases: {len(PHASES)}  bytes: {len(page):,}")


if __name__ == "__main__":
    main()
