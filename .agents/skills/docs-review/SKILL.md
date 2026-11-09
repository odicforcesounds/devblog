---
name: docs-review
description: When a feature or a decision lands, find every document it invalidates — the page that records it, README.md, the AGENTS.md task table, the skills and the backups runbooks — and review those statements before calling the work done. Use after adding a feature, changing a command or a path, renaming a section, or when documentation contradicts the tree.
---

# Review the documents a change touches

A feature is not finished when the code works; it is finished when the documents that
describe the old behaviour no longer lie. The rule is to review documentation whenever a
feature is added, and the review is a search, not a memory exercise.

## The set to review

| Document | What it owns |
| --- | --- |
| The page that records the work | `docs/socialToolKit.html` for STK (steps, log table, sources), the article itself for a blog feature. |
| `README.md` | What the project is, how to run and check it, counts, structure. |
| `AGENTS.md` | The task → skill table and the commit contract. |
| `.agents/skills/*/SKILL.md` | Commands, paths, sizes, counts and rules for one area. |
| `backups/*.md` | Runbooks: `CLOUDFLARE.md`, `GOOGLE.md`, the Firebase and provider notes. |
| `docs/GlobalSkills.md` | The numbered rules this project's skills are expected to cover. |

## The procedure

1. List what changed: `git status --short` and `git diff --stat`.
2. For each changed path, name, command or number, search the tree for it.
3. Read the paragraph around each hit and test the claim: does the path exist, does the
   command run, does the count match, does the anchor still resolve?
4. Classify each hit: **true**, **false** (report with file and line), or **cannot be
   verified here** (say which fact would be needed).

```sh
grep -rn 'build_api.py' README.md AGENTS.md START-HERE.md backups/*.md | cut -c1-160
grep -rn 'socialToolKit' README.md AGENTS.md .agents/skills/*/SKILL.md | cut -c1-160
```

## The edit gate

- A `docs/` page named by the request may be corrected inside that page.
- `README.md`, `AGENTS.md`, `START-HERE.md` and every `SKILL.md` are read-only without a
  request that names them (`START-HERE.md`, limits 2 and 3). A stale line there is
  reported — file, line, current text, what it should say — and left in place.
- A contradiction between two documents is reported as a contradiction, with both lines;
  the agent does not pick a winner.

## Known gaps at the time of writing

- `AGENTS.md`'s table lists 14 skills; `.agents/skills/` holds more, including the skills
  added for `docs/GlobalSkills.md`.
- `README.md`'s skill paragraph lists a subset, and its page counts predate the current
  API (see `readme-updates`).
- `docs/GlobalSkills.md` cites `https://publicapis.dev/` while
  `public-api-context` documents `publicapis.lol`; both are checkable, neither is the
  same site.

None of these is repaired by this skill; they are what a review is for.
