---
name: ask-first
description: Stop and ask when a decision is not the agent's to make — scope, a file outside docs/, a deletion, a generator run, a config change, two sources that disagree — and decide alone only when the request already answers the question. Use while scoping a request, before an irreversible step, and whenever two reasonable outcomes are possible.
---

# Decide, or ask

The rule is to ask when something must be decided. Asking is not a delay; a wrong guess
is, because it is discovered after the work is done.

## Ask when

- The request names no file, or names one outside `docs/` (the page contract in
  `START-HERE.md`).
- The change needs a deletion, a move or a rename.
- The change needs a generator run — `build_api.py`, `build_sitemap.py`,
  `enrich_schema.py`, a `living-panel` generator — because it rewrites many files at once.
- The change needs a configuration edit: CSP, `CNAME`, `robots.txt`, Firebase rules,
  `.gitignore`, a deploy helper (see `config-changes`).
- A check fails for a reason unrelated to the request, and the obvious repair touches a
  file the request did not name.
- The request contradicts `START-HERE.md`. Quote the line, say which two outcomes are
  possible, and ask which wins.

## How to ask

1. State what you already checked, in one sentence, so the question is not answerable by
   reading the tree.
2. Offer two or three concrete outcomes, not "what should I do?".
3. Name the default you would take and what it costs.
4. Stop. Do not start the work in the same turn and mention the question afterwards.

> The page names `docs/ordersAndConscience.html`, which fails `page_hygiene.py` on 50
> existing duplicate links. I can add the new section without touching them, or fix the
> duplicates first in the same file. Default: add the section only.

## Do not ask when

- The request names a file and the fix is a typo, a broken tag or a sentence inside it.
- A reversible edit is already inside the named scope.
- The request names the check and its command; running it is the instruction.
- The same question was answered earlier in the session; use the answer.

## After the answer

Carry the decision into the work and into the record: the commit message for a normal
repository, the numbered step table for `docs/socialToolKit.html`, the page's own prose
where the page exists to explain a choice. A decision that lives only
in the chat is lost on the next change.
