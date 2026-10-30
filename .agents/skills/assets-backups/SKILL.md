---
name: assets-backups
description: Manage the non-article material of this repository — page templates in templates/, the runbooks and old files in backups/, and every image or icon under docs/images/ (formats, naming, size, references, unused files). Use when adding an image, changing a template, writing a runbook, or pruning backups and assets.
---

# Assets, templates and backups

Three directories, three different promises:

- `templates/` — starting points, **never published**, not part of the site.
- `backups/` — memory, **tracked on purpose**, never published either (it sits outside `docs/`).
- `docs/images/` — **published**, served from the same origin as the pages, so weight and
  naming are part of the product.

## templates/

`templates/dataDossier.html` is the only template: 469 lines, a dark shell with the head
contract already in place. It is generic and date-free, and it carries one deliberate
legacy exception — a Bandcamp `<iframe>`; do not copy that into a new page (`new-page`
forbids every external request).

Rules:

- A template is a starting point, not a page: no canonical pointing at itself, no entry in
  `index.html`, the sitemap or the API, and no article prose left over from the article it
  was extracted from.
- Changing a template changes **nothing published** — pages were copied from it and are
  independent files. If an old template bug must be fixed across the archive, that is a bulk
  script in `tmp/`, not a template edit.
- Keep it complete: a template that needs three manual fixes before it passes
  `check_site.py` is not a template.

## backups/

Tracked, outside `docs/`, therefore never served. It holds:

| File | What it is |
| --- | --- |
| `CLOUDFLARE.md` | Hosting runbook: DNS, proxy, bot rules, redirects, cache, headers, HSTS. Read before touching the edge. |
| `GOOGLE.md` | Search Console and structured-data runbook: order of operations, known gaps. |
| `firebase-rules.txt` | Firestore rules for the comment form; changes must be pasted into the console. |
| `comments-login-failure.md` | Diagnosis of the sign-in failures, with the evidence. |
| `setup-facebook-github.md` | How to enable another auth provider. |
| `original/` | Pre-rewrite versions: `index.html`, `change.html`, `index.css`, `templates/`. |
| `art_map.json`, `blog_map.json`, `project_map.json` | Structural maps of the archive. |
| `blog_sitemap.xml`, `urls/` | Previous sitemap and URL inventories. |

Rules:

- **One fact per file, named for the fact.** A runbook is updated in place; a diagnosis is
  a dated snapshot — if it is superseded, delete it, git keeps the old text.
- **A backup is not a safety copy.** Git is the safety copy. `backups/` exists for things
  git cannot explain — why a setting is what it is, how the console must be configured.
- **Maps go stale.** `*_map.json` describes the archive at a moment; if it is regenerated
  by a script, say which one, and if it is not, treat it as a snapshot and do not cite it
  as current.
- **No credentials.** Public client config is fine; private keys, tokens and passwords are
  not — say where the value comes from instead.
- Nothing here is linked from `docs/`; a runbook that must be reachable by readers becomes a
  page in `docs/`, with a different job.

## docs/images/

28 files, about 8.9 MB. Formats in use: `.svg` (icons and emblems), `.webp`, `.jpg`,
`.jpeg`, `.png` (photos and screenshots). Served at
`https://blog.odicforcesounds.com/images/name.ext`.

Rules:

- **Format by purpose.** New icons and logos are `.svg` (small, sharp, themeable:
  `one-human-song.svg`, `adversario.svg`, `economia.svg`). Photos are `.webp`; `.jpg`/`.png`
  are legacy. Do not add a PNG icon.
- **Size matters.** Several files are over 1 MB (`freebsd.png` 2.3 MB, `brutalbsd.png`
  1.5 MB, `PowerFinger.webp` 1.3 MB). A new picture over ~300 KB should be resized or
  converted before it is referenced; the page must stay usable on a phone.
- **Name lower-case, hyphenated, at a glance readable**: `one-human-song.svg`. Existing
  mixed-case names (`Business.webp`) are legacy — do not rename a file pages already use
  unless you update every reference in the same change.
- **Every reference is local and relative**: `<img src="./images/name.ext" alt="" width="…"
  height="…">`. Remote images are forbidden (`new-page`), and so are `@import`/`url(http…)`
  in the page CSS.
- **Always set `width`/`height`** (no layout shift) and `alt` (empty only when decorative),
  `loading="lazy"` below the fold.
- **One icon per meaning.** `icons.svg` is a sprite; a page that needs a single glyph either
  references the sprite symbol or gets its own small `.svg` — do not inline a 4 KB path
  twice.
- **Remote media is legacy only.** A few articles still embed a Bandcamp `<iframe>` player
  (`4yfn.html`, `aboutPolitics.html`, …). That is not an image and must not be copied into
  a new page — `new-page` forbids every external request.

### Audit the folder

```sh
# weight, biggest first
ls -lhS docs/images | head -12

# unreferenced files (candidate deletions, but check dynamic references first)
python3 - <<'PY'
import pathlib
root = pathlib.Path("docs")
corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                   for p in root.rglob("*") if p.suffix in {".html", ".css", ".js", ".json"})
for img in sorted((root / "images").iterdir()):
    if img.name not in corpus:
        print("unreferenced:", img.relative_to(root))
PY

# names that collide when case is ignored (Windows/macOS checkouts)
ls docs/images | tr 'A-Z' 'a-z' | sort | uniq -d

# references that are not local — the only legitimate hits are the legacy Bandcamp players
grep -rnoE '(src|url\()\s*=?\s*"?https?://[^")]*' docs/*.html docs/*.css | head
```

Before adding an image, check whether one already carries that meaning (`icons.svg`,
`peace.jpg`, `three.jpg`), and after adding it verify the page still opens with no network:
the file lives in `docs/images/`, so the page works from `docs/` alone.
