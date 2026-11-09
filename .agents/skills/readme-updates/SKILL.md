---
name: readme-updates
description: Keep README.md true to the repository it describes — what the project is, how it is served and checked, where things live and how many there are — proposing the edit and applying it only when asked. Use when a feature, a script, a directory or a page count changes, or when a README statement can be tested against the tree and fails.
---

# The README is a claim about the tree

`README.md` is the front door of a GitHub project, and every sentence in it is checkable:
a path, a command, a count, a file name. When one of those changes, the README is wrong
until it is edited — but it is also read-only here without a request (`START-HERE.md`,
limits 2 and 3), so the agent's job is to **find the stale line, prove it, and propose the
diff**. Applying it needs the author to ask.

## What has to stay true

| Section | Claim |
| --- | --- |
| Introduction | Static site, `docs/` is the site, no build step between a file and the URL. |
| What this repository contains | Every named path exists and still does what the sentence says. |
| Repository structure | The tree matches the directories on disk. |
| How the site is served | GitHub Pages from `docs/`, custom domain in `docs/CNAME`, Cloudflare in front. |
| Writing a page | The five steps still run in that order. |
| The JSON API | File names, sizes and consumers. |
| CSS and layout | Which stylesheet is current, which is the previous generation. |
| Checks | The command printed exits `0` today. |
| Current state | Branch, article count, language tags, date range. |

## How to check a count

```sh
find docs -maxdepth 1 -name '*.html' | wc -l
python3 -c "import json; print(json.load(open('docs/api/index.json'))['count'])"
ls -d .agents/skills/*/ | wc -l
```

At the time of writing the API counts `563` documents while the introduction still says
`546` HTML files and `543` articles, and the skills paragraph lists a subset of
`.agents/skills/`. Those are reported as drift, not silently corrected.

## Rules

- **One claim, one source.** A count comes from the API or from `find`, not from the last
  README edit; a path comes from the tree, not from memory.
- **Do not rewrite around a false statement.** If a command no longer works, the README
  says so only after the behaviour is fixed or the author chooses the wording.
- **Nothing personal, nothing secret.** No e-mail address, token or private host detail
  (see `privacy-data`).
- **No changelog.** Git has the history; the README describes the state.
- **When asked to update it**, change the statements the request implies and leave the
  rest byte for byte. Verify each printed command still runs before committing.
- **A skill list is a promise.** If the README names the skills, a skill added or removed
  is a README edit waiting to be requested.
