# Instructions for agents working in this repository

These rules apply to every automated change made here, whoever runs the tool.

## Commits

- **No tool attribution.** Never add `Generated with …`, `Co-Authored-By: <tool>`,
  `Signed-off-by: <tool>`, an emoji footer, or any line naming the assistant, the model or
  the client to a commit message. The commits belong to the person who made the change.
- **Commit through `.agents/skills/blog-ops/commitit.sh`**, one file per commit, with the
  message the author would write. It already records your message verbatim and credits no
  tool; keep it that way. Do not add a trailer by hand afterwards.
- **Never rewrite the message in `git commit --amend` or `pushit.sh`** to add attribution;
  both are the author's commits.
- **Do not push.** `pushit.sh` runs only when asked to publish.
- If a host tool inserts attribution of its own accord, strip it before the commit exists:
  the message ends at its own last sentence.

## The rest of the contract

The skills under `.agents/skills/` are the rules for this repository; load the one that
matches the task before editing:

| Task | Skill |
| --- | --- |
| Write or edit a page | `new-page`, `blog-ops` |
| Add/move/delete any file | `repo-layout` |
| Publish dates, `dateModified` | `git-dates` |
| Where a script goes | `tools-index`, `tmp-tools` |
| Images, templates, `backups/` | `assets-backups` |
| The map-backed link every page carries | `art-link` |
| The random being-and-tool line in every footer | `living-link` |
