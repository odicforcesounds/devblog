---
name: deploy-cloudflare
description: Publish to Cloudflare with Wrangler only for a project that declares wrangler.toml or wrangler.jsonc and only when the author asks — Pages, Workers and KV — and keep this blog's Cloudflare where it belongs, as the edge in front of GitHub Pages. Use when an application is hosted on Cloudflare or reads KV, or to confirm that no deploy applies here.
---

# Deploying to Cloudflare

## Does it apply?

```sh
ls wrangler.toml wrangler.jsonc wrangler.json
```

This repository has none. Its origin is GitHub Pages and Cloudflare sits in front as a
proxy: DNS, TLS, bots, redirects, cache, headers and HSTS are console settings recorded in
`backups/CLOUDFLARE.md`, and none of them is a Wrangler deploy. Do not add a Wrangler
configuration to make a deploy possible — that is a configuration change and needs its own
request (see `config-changes`).

When a project does declare the file, this skill applies to that project.

## The deploy

```sh
npx wrangler login
npx wrangler whoami                    # the account the deploy will use
npx wrangler deploy                    # Workers
npx wrangler pages deploy <dir>        # a Pages project that is not Git-connected
npx wrangler deploy --env staging      # a named environment
```

Deploy one environment at a time. `--env production` is the author's decision, not a
default.

## KV is not a database

KV is a distributed key-value store: reads are fast and cached at the edge, writes are
eventually consistent, there is no query language and no transaction across keys.

- **The key is the schema.** `article:<slug>`, `date:<name>`, `shelf:<catalogue>:<name>`
  — a list or a filter has to be another key, built at write time.
- **A write may not be visible immediately** in another region; do not read your own write
  and treat the stale answer as a bug.
- **Values have a size limit**; large JSON belongs in R2 or in a static file, not in a KV
  entry.
- **A key without an expiry is permanent.** Name the TTL when the data has one.

```sh
npx wrangler kv namespace list
npx wrangler kv key get --namespace-id=<id> "article:simplicity"
npx wrangler kv key put --namespace-id=<id> "article:simplicity" --path=./value.json
```

## Rules

- Secrets go through `npx wrangler secret put NAME`; never into `wrangler.toml`, a page or
  a commit.
- A delete is named key by key. No `--prefix` cleanup on production without the author
  saying which prefix.
- Verify with the deployed URL and one KV-backed route; report the URL, the environment and
  what the edge answered.
- Wrangler is not the tool for the blog's cache or headers. Those are Cloudflare dashboard
  or API settings, and `backups/CLOUDFLARE.md` says how each is confirmed with `curl`.
