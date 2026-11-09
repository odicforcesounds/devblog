---
name: local-server
description: Serve the site on this host's LAN address, 192.168.200.10:8080, with python3 -m http.server from the repository root so fetches, absolute paths and the API behave as they do in production. Use when checking a page in a browser, when a page's fetch fails from file://, or when testing on a phone on the same network.
---

# The local server on 192.168.200.10:8080

The site is static, so testing it is serving `docs/` over HTTP. From disk (`file://`) the
`fetch` calls fail with a null origin, and a phone cannot reach `127.0.0.1`.

## Start it

```sh
# from the repository root; docs/ is the site root
python3 -m http.server 8080 --bind 0.0.0.0 --directory docs
```

- Desktop: <http://192.168.200.10:8080/> or <http://127.0.0.1:8080/>
- A page: <http://192.168.200.10:8080/disobedience.html>
- The API the front page reads: <http://192.168.200.10:8080/api/dates.json>

`192.168.200.10` is this host's second address; `hostname -I` prints it beside
`192.168.1.225`. If the machine has moved network, name the address it actually has
instead of repeating the one above.

## Check it answers

```sh
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' \
  http://192.168.200.10:8080/index.html \
  http://192.168.200.10:8080/api/dates.json \
  http://192.168.200.10:8080/living-panel.js
```

Expect `200 text/html`, `200 application/json` and `200 text/javascript`. A `404` on a page
that exists means the server was started in the wrong directory — `--directory docs` from
the root, not from inside `docs/`.

## What it does not reproduce

- **No caching headers, no CORS headers.** GitHub Pages answers the JSON with
  `access-control-allow-origin: *` and `cache-control: max-age=600`; this server sends
  neither. A page from another origin that reads the data locally is not a valid test.
- **No `404.html`.** A missing path gets the server's plain text 404, not the site's page.
- **No Cloudflare.** The edge can inject, cache or block; `backups/CLOUDFLARE.md` is where
  that is tested with `curl`, not here.
- **No HTTPS.** A browser feature that requires a secure context (clipboard, camera,
  service worker) behaves differently on the LAN address.

## Rules

- One server per port. If `8080` is taken, say which process holds it rather than picking
  another port silently; the address in the rule is the one that gets tested.
- The STK apps use their own ports (`:3000`, `:3230`, `:5000`, `:5001`); do not run them
  on `8080`.
- Bind `0.0.0.0` only while testing on the LAN, and stop the server when the test is
  done — it publishes `docs/` to every device on the network.
- A server in the background is not a test result. Name the URL and the status codes you
  saw, then stop it.
