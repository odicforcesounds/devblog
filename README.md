# devblog

A static, self-contained blog repository used to publish articles at
<https://blog.odicforcesounds.com>.

The site is built from plain HTML and CSS. Articles are organized in
`docs/` and there is a small helper toolset under `tools/`. This
repository also tracks publication dates for the articles.

## What this repository contains

- **Article archive** — HTML pages under `docs/`, covering many subjects
  instead of a single narrow topic.
- **Shared styling** — CSS used across the article pages:
  - `docs/article.css`
  - `docs/index.css`
  - `templates/article.css`
- **Page templates** — starting points for article pages:
  - `templates/default.html`
  - `templates/techArticle.html`
  - `templates/brutalArticle.html`
  - `templates/offensiveArticle.html`
- **Images** — shared images under `docs/images/`.
- **Archive collections** — older or grouped material under
  `docs/archive/`.
- **Publication dates** — stored in `docs/dates.json`.
- **Helper tools** — small utilities under `tools/`, such as
  `tools/clean_rss.py` and `tools/prompts.txt`.
- **Router notes** — OpenBSD router material under `docs/obsdRouter/`.
- **Backups and PDFs** — stored in `backups/` and `docs/pdfs/`.

## Topics covered

The blog is deliberately broad. Common themes include:

- **Operating systems and open source** — especially Linux, FreeBSD, and
  OpenBSD
- **Security and hacking** — defensive and offensive perspectives,
  tools, and practical notes
- **Programming, sysadmin, and infrastructure** — technical write-ups and
  field-manual style articles
- **Social commentary, politics, and law** — criticism, reactions, and
  controversial takes
- **Creative, philosophical, and psychological pieces** — fewer in
  number, but part of the same archive

The blog also includes some intentionally provocative content.

## Repository structure

```text
devblog/
├── README.md
├── backups/
├── docs/
│   ├── archive/
│   ├── images/
│   ├── obsdRouter/
│   ├── pdfs/
│   ├── article.css
│   ├── index.css
│   ├── dates.json
│   └── *.html
├── templates/
│   ├── default.html
│   ├── techArticle.html
│   ├── brutalArticle.html
│   └── offensiveArticle.html
├── tools/
│   ├── clean_rss.py
│   └── prompts.txt
├── tmp/
├── todos/
└── .git/
```

## Publication dates

Articles do not display publication time on the rendered pages.

Publication and change metadata are tracked separately in
`docs/dates.json` instead of on the blog itself. If you want to
understand when articles were published or updated, that file is the
place to watch.

## Editing and adding content

The blog is edited as static files.

A practical workflow is:

1. Add or edit an HTML file under `docs/`.
2. Update `docs/dates.json` if the publication date is changing.
3. Commit the change.
4. Push when ready.

If you create a new article, use one of the templates in `templates/`
as a starting point and keep the shared styling consistent with the
existing pages.

## CSS and layout

The article pages use shared CSS rules. The most important ones for
layout are:

- `docs/article.css` — article page styles
- `docs/index.css` — home page styles
- `templates/article.css` — template-level article styles

Some pages also include inline styles when they need local layout
control.

## Site sections

The home page groups links into categories. Those categories are
collapsed by default and expand on demand.

One prominent entry point on the home page is the top centered link,
currently **Dream Path**.

Other parts of the site live on separate subdomains:

1. Wiki
2. Book
3. Art
4. Blog

The blog is one part of the larger `odicforcesounds.com` space.

## Hosting and updates

The repository is hosted on GitHub:

- `https://github.com/odicforcesounds/devblog`

The published site is available at:

- `https://blog.odicforcesounds.com`

Updates are not scheduled on a fixed publishing calendar. The articles
are written as timeless pieces first, and the repository activity is
the main way to follow changes.

## Notes on the archive

- Some files under `docs/archive/` are older or grouped for reference.
- `docs/questions.html` is used as a loose thread page for entries that
  were moved, retitled, or gathered together.
- Temporary material may appear under `tmp/` during work in progress.

## Current state

Main branch: `main`
Latest commit: `d3f1dbe`

Repository state is kept clean on the main line. Temporary artifacts
may exist locally under `tmp/` or as editor swap files, but the
published structure is meant to stay static and readable.
