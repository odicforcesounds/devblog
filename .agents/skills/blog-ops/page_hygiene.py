#!/usr/bin/env python3
"""Check the three content rules of a page: unique links, unique information,
no authoring comments.

    python3 .agents/skills/blog-ops/page_hygiene.py docs/Name.html
    python3 .agents/skills/blog-ops/page_hygiene.py --all          # every root page
    python3 .agents/skills/blog-ops/page_hygiene.py --quiet docs/*.html

Rules for one page:

1. **No duplicated links.** The same target (`href`) may appear once per document
   scope. A page with two language blocks has two scopes — the translations may
   each carry their own copy of a link, because a reader only sees one block. A
   repeated target inside a single scope is a duplicate and is reported.
2. **No duplicated information.** A text block (`p`, `li`, `blockquote`, `dd`,
   `h2`, `h3`, `td`) of eight words or more may not repeat inside the same scope.
   Translation between the EN and PT blocks is not repetition: different scope.
   Neither is the head contract's four identical description copies (meta, og,
   twitter, JSON-LD) — that is required there and lives in `<head>`.
3. **No authoring comments.** No HTML comment that talks about the instruction,
   the request, the prompt or the authoring session. The page must read as if it
   were written for its readers; comments that describe *how it was made* are
   evidence of the request, not documentation of the page.

Exit 0 when the pages are clean, 1 when anything is reported. Standard library
only.
"""

import os
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser

DOCS = "docs"
ORIGIN = "https://blog.odicforcesounds.com"
TEXT_BLOCKS = {"p", "li", "blockquote", "dd", "h2", "h3", "td"}
SKIP_TEXT = {"script", "style", "pre", "code", "textarea", "svg"}
MIN_WORDS = 8

# A comment matching any of these is about the authoring session, not the page.
AUTHORING = re.compile(
    r"""(?ix)
    \b(as\s+(?:requested|asked|instructed|you\s+(?:wanted|asked|said)))
    | \b(per|following|according\s+to)\s+(?:the\s+)?(?:user|request|prompt|instructions?)
    | \b(user|writer|author)\s+(?:asked|wants|wanted|requested|instructed)
    | \bprompt\b
    | \b(assistant|chatgpt|claude|codebuff|copilot)\b
    | \b(todo|fixme)\b
    | \b(note\s+to\s+self|do\s+not\s+(?:remove|change|delete)\s+this\s+comment)
    | \b(add|insert|put|change|edit|update|remove)\s+(this|here|the\s+following)\b
    """
)


def normal_href(href):
    """Compare targets by what they point at, not by how they are spelled."""
    value = href.strip()
    if value.lower().startswith(ORIGIN):
        value = value[len(ORIGIN):] or "/"
    while value.startswith("./"):
        value = value[2:]
    if value in ("", "."):
        value = "/"
    return value


def normal_text(text):
    return " ".join(text.split()).lower()


class Hygiene(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []            # [(tag, opens_scope)]
        self.lang = []             # active data-lang-block values, innermost last
        self.links = defaultdict(list)
        self.blocks = []           # (scope, tag, text)
        self.captures = []         # [{depth, scope, tag, parts}]
        self.comments = []
        self.skip_tag = None       # tag whose content is code, not prose

    def _scope(self):
        return self.lang[-1] if self.lang else ""

    def _link(self, href):
        href = (href or "").strip()
        if href and href != "#" and not href.lower().startswith("javascript:"):
            self.links[self._scope()].append(normal_href(href))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        opens_scope = tag == "div" and bool(attrs.get("data-lang-block"))
        if opens_scope:
            self.lang.append(attrs["data-lang-block"])
        if tag == "a":
            self._link(attrs.get("href"))
        if tag in SKIP_TEXT and self.skip_tag is None:
            self.skip_tag = tag
        if tag in TEXT_BLOCKS and self.skip_tag is None:
            self.captures.append({"depth": len(self.stack), "scope": self._scope(),
                                  "tag": tag, "parts": []})
        self.stack.append((tag, opens_scope))

    def handle_startendtag(self, tag, attrs):
        if tag == "a":
            self._link(dict(attrs).get("href"))

    def handle_endtag(self, tag):
        index = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                index = i
                break
        if index is None:
            return                          # stray end tag: a browser ignores it
        closed = self.stack[index:]
        del self.stack[index:]

        for capture in [c for c in self.captures if c["depth"] >= index]:
            text = " ".join("".join(capture["parts"]).split())
            if len(text.split()) >= MIN_WORDS:
                self.blocks.append((capture["scope"], capture["tag"], text))
            self.captures.remove(capture)

        for closed_tag, opens_scope in closed:
            if opens_scope and self.lang:
                self.lang.pop()
        if self.skip_tag == tag:
            self.skip_tag = None

    def handle_data(self, data):
        if self.skip_tag is not None:
            return
        for capture in self.captures:
            capture["parts"].append(data)

    def handle_comment(self, data):
        text = " ".join(data.split())
        if text and AUTHORING.search(text):
            self.comments.append(text[:90])


def report(name):
    path = os.path.join(DOCS, name)
    with open(path, encoding="utf-8", errors="replace") as fh:
        parser = Hygiene()
        parser.feed(fh.read())
        parser.close()

    problems = []

    for scope, hrefs in parser.links.items():
        where = " (%s block)" % scope if scope else ""
        for href, count in Counter(hrefs).items():
            if count > 1:
                problems.append("%s appears %d times%s" % (href, count, where))

    seen = Counter((scope, normal_text(text)) for scope, _, text in parser.blocks)
    for (scope, text), count in seen.items():
        if count > 1:
            where = " (%s block)" % scope if scope else ""
            problems.append("repeated text%s: %r" % (
                where, text[:60] + ("…" if len(text) > 60 else "")))

    for comment in parser.comments:
        problems.append("authoring comment: %r" % comment)

    return problems


def main(argv):
    quiet = "--quiet" in argv
    args = [a for a in argv if a != "--quiet"]
    if "--all" in args:
        names = sorted(n for n in os.listdir(DOCS) if n.endswith(".html"))
    else:
        names = []
        for arg in args:
            name = os.path.basename(arg)
            if not name.endswith(".html"):
                print("%s is not an .html page" % arg)
                return 2
            if not os.path.exists(os.path.join(DOCS, name)):
                print("no such page: %s" % os.path.join(DOCS, name))
                return 2
            names.append(name)
        if not names:
            print(__doc__.strip())
            return 2

    failures = 0
    for name in names:
        for problem in report(name):
            failures += 1
            print("%s: %s" % (name, problem))

    if not quiet:
        print("pages %d, failures %d" % (len(names), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
