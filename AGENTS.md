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
| Publish dates, `dateModified` | `git-dates` |
| Add/move/delete any file | `repo-layout` |
| Where a script goes | `tools-index`, `tmp-tools` |
| Images, templates, `backups/` | `assets-backups` |
| The fixed living card on every page | `living-panel` |
| Link colours by destination | `link-colors` |
| The article pages' shared stylesheet | `page-css` |
| Titles, canonicals, sitemap, what a crawler indexes | `seo-indexation` |
| A dead link, local or external | `link-integrity` |
| What a page downloads, payload budgets | `page-weight` |
| CSP and the other meta headers | `security-headers` |
| Alt text, language, labels, focus | `a11y` |
| The JSON behind the catalogue pages | `catalogue-data` |
| The comment form and the secret chat | `comments` |

## Scope

- **Change only what the request names.** A defect you notice on the way is
  reported at the end of the run, not repaired on your own initiative.
- **Never edit a skill, a script, `AGENTS.md`, or an unrelated page or data file
  without an explicit instruction to do so.** The files under `.agents/skills/`
  are the contract that governs every other change: a request about a page does
  not authorise changes to the rules that govern pages. When a rule itself looks
  wrong, say which line and why, and wait to be asked.
- **No comments unless asked.** No HTML comment, CSS comment or code comment that
  explains the edit, the request, the session or the intent.
- **Nothing is committed unless the author asks**; when they do, follow `## Commits`.
- **Never empty or rewrite a data file to make a build pass.** Restore it from
  history (`git show <rev>:<path>`) and name the commit that broke it.

## The fixed message on every page

Every page under `docs/` except `index.html` carries one card fixed to the left
edge of the window at mid height — the place the social dock takes on the front
page — holding the photograph of one living being from the four living catalogues
and saying which tool it likes, which electronic part it loves, which plant it is
on a diet with and which city it stands in.

```html
<aside class="living-panel" id="living-panel" aria-label="A living being, a tool, a component, a plant and a city">
  <img src="…/250px-…jpg" alt="Golden hamster" width="152" height="90" loading="lazy" decoding="async">
  <p>this <a href="animalsIndex.html#order-rodentia" title="Cricetidae · Rodentia">Golden hamster</a>
  likes to use <a href="awesomeIndex.html#cat-dotnet" title="Stripe.Net · .NET libraries, tools and frameworks">Stripe.Net</a>
  and loves <a href="electronicsIndex.html#cat-assembly" title="Soldering and wiring · Boards, packaging and wiring">Desoldering</a>
  while doing some diet with <a href="plantsIndex.html#order-arecales" title="Arecaceae · Arecales">Coconut</a>
  at <a href="worldIndex.html#cat-tm" title="Turkmenistan · Asia">Ashgabat</a>.</p>
</aside>
```

- Exactly one block per page, plus one `<style id="living-panel-style">` in `<head>`.
  The block is the first thing after `<body …>`: a fixed element needs a direct child
  of the body, because a transformed ancestor would trap it.
- Nothing is pushed around to make room. The card lives in the left margin, outside
  the reading column, and shrinks in steps as the window narrows.
- The sentence is the picture and
  `this <being> likes to use <tool> and loves <component> while doing some diet with <plant> at <city>.`
  — nothing else, in that order. The being links to its order in its catalogue, the tool
  to its drawer in `awesomeIndex.html`, the component to its category drawer in
  `electronicsIndex.html`, the plant to its order in `plantsIndex.html`, and the city to
  its country shelf in `worldIndex.html`. All five targets must be ones the page does not
  already carry, and must differ from each other. The city is the most populous place of
  its country whose name fits the card, so the sentence never ends in `Lisbon · Maine`.
- The photograph is the catalogue's 500px file rewritten to 250px; Wikimedia serves
  only its listed widths and answers 400 for any other.
- `index.html` carries no card: the social dock already takes that corner of the
  window. The generator leaves the front page alone.
- The set written into the page is the no-script fallback. `docs/living-panel.js`
  (`.agents/skills/living-panel/build_living.py`) holds every being, tool, component,
  plant and city and replaces the set with a fresh one on each load, skipping any link
  the page already carries.
- Generators live with the skill: `.agents/skills/living-panel/living_panel.py`
  (`--dry-run`, `--page`, `--remove`), `build_living.py` and `check_panel_links.py`.

