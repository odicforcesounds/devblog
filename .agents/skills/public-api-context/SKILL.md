---
name: public-api-context
description: Use keyless public APIs from publicapis.lol in JavaScript/API articles and in the search boxes of the catalogue indexes, with Art Institute of Chicago, Free Dictionary and Open Library as the three audited defaults. Use when an article already makes API calls, when a page needs a random text link, or when an index search needs an external escape hatch, and when a proposed remote fetch must be checked for HTTPS, CORS, CSP, caching, fallback and privacy.
---

# Public API context

The three default sources are listed on <https://publicapis.lol> and are used
here to add material that is not already on Wikipedia or Wikimedia:

| API | publicapis.lol category | Keyless endpoint | Result link | Image host |
| --- | --- | --- | --- | --- |
| Art Institute of Chicago | Art & Design | `https://api.artic.edu/api/v1/artworks/search?q={query}&limit=6&fields=id,title,artist_display,date_display,image_id` | `https://www.artic.edu/artworks/{id}` | `www.artic.edu` |
| Free Dictionary | Dictionaries | `https://api.dictionaryapi.dev/api/v2/entries/en/{word}` | `sourceUrls[0]`, else `https://en.wiktionary.org/wiki/{word}` | none |
| Open Library | Books | `https://openlibrary.org/search.json?q={query}&limit=6&fields=key,title,author_name,first_publish_year,cover_i` | `https://openlibrary.org{key}` | `covers.openlibrary.org` |

All three are HTTPS, keyless and client-side CORS-capable as of the last
audit. **The CORS badge on publicapis.lol is a lead, not a test.** The live
endpoints currently answer `access-control-allow-origin: *` when sent an
`Origin` header, including Open Library and Free Dictionary, whose directory
badges are stale. Re-run the check below before adding or keeping a call:

```bash
for url in \
  'https://api.artic.edu/api/v1/artworks/search?q=cat&limit=1&fields=id,title' \
  'https://api.dictionaryapi.dev/api/v2/entries/en/cat' \
  'https://openlibrary.org/search.json?q=tokyo&limit=1'; do
  curl -sS -D - -o /dev/null -H 'Origin: https://blog.odicforcesounds.com' "$url" \
    | grep -i '^access-control-allow-origin:'
done
```

Require `*` or the exact origin. If a header is missing, use the API at build
time or as an ordinary link only, or drop it; never route it through a CORS
proxy.

## Where each one belongs

Use context, not a rotation:

| Page subject | Default source | What it adds |
| --- | --- | --- |
| Art, architecture, visual culture, ritual objects | Art Institute of Chicago | object title, artist, date, IIIF image, collection record |
| Language, definitions, etymology, translation, naming | Free Dictionary | pronunciation, part of speech, definitions, examples, source URL |
| Books, literature, philosophy, religion, history of ideas | Open Library | edition, author, first publication year, cover, catalogue record |
| World, places, travel, environment | Open Library or Art Institute, chosen by the page's actual subject | a book about the place or an object from it, not a flag or a weather number |
| Games, music, tools, electronics, dance, animals and plants | Only when a result genuinely belongs to the page | a named work or a definition, never a decorative random result |

If none of the three belongs, another keyless, HTTPS, CORS-checked entry from
publicapis.lol is allowed. Name it in the page and add its host to this skill
and to `check_api_usage.py` after the audit. The three above stay the defaults
because they are broad, stable and image-friendly.

## Articles that already use JavaScript APIs

This skill applies when a page already has a `fetch`, an API example or a
JavaScript-driven result panel. Do not introduce an API call into an article
that has none merely to satisfy this rule, and do not replace the article's
existing source of truth.

- Put the API material in a clearly labelled **Elsewhere** or **From the
  catalogue** block after the prose it supports. Do not auto-link every noun,
  heading, quotation or navigation label.
- Show two to four results, not a feed. Label the source and link the result to
  the provider's record.
- Keep the article's local data first. The API is enrichment; it is never the
  only way to read the page.
- Do not copy a definition, book blurb or artwork description as if it were the
  blog's own prose. Quote briefly, attribute, and link.
- Do not put an API key in a page. All three defaults are keyless. A provider
  that needs a key is build-time only unless a server proxy exists.

## Random text links

Free Dictionary is the random-link source.

- One or two random links per page load, maximum. No timer, no refresh loop, no
  link on every paragraph.
- Cache the chosen word for the session. A reader who returns to the page should
  see the same link, not a slot machine.
- Link the word to `sourceUrls[0]` from the API response, or to
  `https://en.wiktionary.org/wiki/{word}` when that field is absent.
- Use the API's word and part of speech as the link text; do not invent a
  sentence around it.
- Skip random links in medical, legal, safety and emergency passages. A playful
  link there is a credibility problem.

```js
const res = await fetch(
  `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`,
  { signal, headers: { Accept: "application/json" }, credentials: "omit" }
);
if (!res.ok) throw new Error(`Dictionary ${res.status}`);
const [entry] = await res.json();
const href = entry.sourceUrls?.[0] ||
  `https://en.wiktionary.org/wiki/${encodeURIComponent(entry.word)}`;
```

## Search boxes in the indexes

The local catalogue search is authoritative. An external search is an escape
hatch, not the search itself.

- Keep the existing local input, labels, result count and empty state.
- Show the external offer only after the local query has returned no results,
  or as a separate **Search elsewhere** link beside the box. Never send every
  keystroke to a remote API by default.
- Make the external offer a normal link with an encoded query. A click is the
  reader's consent to leave the local catalogue:

```text
https://openlibrary.org/search?q=<encoded>
https://www.artic.edu/collection?q=<encoded>
https://www.thefreedictionary.com/<encoded-word>
```

- Match the index: books and ideas to Open Library, art and objects to the Art
  Institute, words to Free Dictionary. Do not put a book search on the fish
  index just because it is available.
- If an index has two language search boxes, keep both local boxes and add at
  most one shared external offer. Do not duplicate ids.
- An external API failure must leave the local search and its results intact.
  Hide the external block and keep the local empty state.

## Runtime rules

Use one request per deliberate action, six results at most.

```js
const controller = new AbortController();
const timer = setTimeout(() => controller.abort(), 4000);
try {
  const res = await fetch(url, {
    signal: controller.signal,
    headers: { Accept: "application/json" },
    credentials: "omit",
    referrerPolicy: "no-referrer"
  });
  if (!res.ok) throw new Error(`${res.status}`);
  render(await res.json());
} catch {
  hideExternalBlock();
} finally {
  clearTimeout(timer);
}
```

- `credentials: "omit"`; no cookies, no auth, no API key.
- Debounce a typed query by at least 350 ms, require three characters, cancel
  the previous request and cache by API plus query.
- Show a loading state only inside the external block. Never disable the local
  search while a remote request runs.
- Cap images at 400 px wide, with `loading="lazy"`, `decoding="async"`, real
  `width`/`height` and alt text from the title or artist. Free Dictionary has
  no image.
- Send no reader text until the reader submits a query or clicks the external
  link. Article-side random links send only a fixed word chosen by the page.
- Do not claim the API is complete, current or official. Link the record.

## CSP and page weight

Add only the hosts the page actually uses. The complete set for all three is:

```text
connect-src 'self' https://api.artic.edu https://api.dictionaryapi.dev https://openlibrary.org;
img-src 'self' data: https://www.artic.edu https://covers.openlibrary.org;
```

Never widen to `connect-src *` or `img-src *`. Keep the existing
`default-src 'self'`; keep `script-src` free of remote scripts. Run
`.agents/skills/security-headers/check_headers.py` after the edit.

Budget: one JSON response per action, six records, at most six lazy images at
400 px. Do not preload covers. Do not fetch an API on page load merely to fill a
panel; a random text link may fetch one definition, and it must be hidden on
failure.

## Review

```bash
python3 .agents/skills/public-api-context/check_api_usage.py
python3 .agents/skills/index-guard/check_indexes.py
python3 .agents/skills/security-headers/check_headers.py
python3 .agents/skills/page-weight/check_weight.py
```

`check_api_usage.py` is offline: it checks HTTPS, the three audited hosts,
`connect-src`/`img-src`, query-string secrets, cancellation and fallback. CORS
itself is a live network property; the `Origin` check above is still required.
