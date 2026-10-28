/* Blog API client — vanilla JavaScript, no dependencies, no external requests.
 *
 *   import { BlogAPI } from "./api.js";
 *   await BlogAPI.ready();
 *   BlogAPI.search("freebsd");
 *
 * The data lives next to this file, in docs/api/, and is produced by
 * tools/build_api.py. Nothing here talks to a server that runs code: the
 * "API" is a set of static JSON files plus this reader.
 */

const BASE = new URL("./api/", import.meta.url);
const INDEX_URL = new URL("index.json", BASE);

const state = {
  index: null,
  docs: [],
  bySlug: new Map(),
  texts: new Map(),      // slug -> text
  chunks: new Map(),     // chunk file -> Promise<object>
  loading: null,
  fullLoaded: 0,
};

/* ---------------------------------------------------------------- helpers */

export function normalize(value) {
  return String(value == null ? "" : value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function tokensOf(query) {
  return normalize(query)
    .split(/[^a-z0-9]+/i)
    .filter(function (t) { return t.length > 1; });
}

function dateOf(doc) {
  return doc.modified || doc.published || "";
}

function yearOf(doc) {
  return (doc.published || "").slice(0, 4);
}

function snippetOf(text, tokens, width) {
  if (!text) return "";
  const flat = text.replace(/\s+/g, " ");
  const lower = normalize(flat);
  let at = -1;
  for (let i = 0; i < tokens.length && at === -1; i++) {
    at = lower.indexOf(tokens[i]);
  }
  if (at === -1) {
    return flat.slice(0, width) + (flat.length > width ? "…" : "");
  }
  const from = Math.max(0, at - Math.floor(width / 3));
  let piece = flat.slice(from, from + width);
  if (from > 0) piece = "…" + piece.replace(/^\S*\s/, "");
  if (from + width < flat.length) piece = piece.replace(/\s\S*$/, "") + "…";
  return piece;
}

function prepare(doc) {
  if (doc._ready) return doc;
  doc._title = normalize(doc.title);
  doc._desc = normalize(doc.description);
  doc._heads = normalize([doc.h1].concat(doc.headings || []).join(" · "));
  doc._ready = true;
  return doc;
}

function scoreDoc(doc, tokens, phrase, text) {
  const title = doc._title;
  const heads = doc._heads;
  const desc = doc._desc;
  let score = 0;
  let everyToken = true;

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    let hit = 0;
    if (title.indexOf(token) !== -1) hit = 12;
    else if (heads.indexOf(token) !== -1) hit = 6;
    else if (desc.indexOf(token) !== -1) hit = 4;
    else if (text && normalize(text).indexOf(token) !== -1) hit = 2;
    if (!hit) everyToken = false;
    score += hit;
  }
  if (phrase && phrase.length > 3) {
    const haystack = title + " " + heads + " " + desc + (text ? " " + normalize(text) : "");
    if (haystack.indexOf(phrase) !== -1) score += 8;
  }
  if (everyToken && score > 0) score += 4;
  return score;
}

function publicResult(doc, score, text, tokens) {
  return {
    slug: doc.slug,
    title: doc.title,
    url: doc.url,
    path: doc.path,
    description: doc.description,
    lang: doc.lang,
    published: doc.published,
    modified: doc.modified,
    year: yearOf(doc),
    snippet: text ? snippetOf(text, tokens, 120) : "",
    score: score,
    full: Boolean(text),
  };
}

/* -------------------------------------------------------------- loading */

export function ready() {
  if (state.index) return Promise.resolve(state.index);
  if (state.loading) return state.loading;
  state.loading = fetch(INDEX_URL.href, { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error("api/index.json: " + response.status);
      return response.json();
    })
    .then(function (data) {
      state.index = data;
      state.docs = (data.articles || []).map(prepare);
      state.bySlug = new Map();
      state.docs.forEach(function (doc) { state.bySlug.set(doc.slug, doc); });
      return data;
    })
    .catch(function (error) {
      state.loading = null;
      throw error;
    });
  return state.loading;
}

function loadChunk(file) {
  if (state.chunks.has(file)) return state.chunks.get(file);
  const promise = fetch(new URL(file, BASE).href, { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error(file + ": " + response.status);
      return response.json();
    })
    .then(function (data) {
      Object.keys(data).forEach(function (slug) {
        state.texts.set(slug, data[slug]);
        state.fullLoaded += 1;
      });
      return data;
    });
  state.chunks.set(file, promise);
  return promise;
}

/* ------------------------------------------------------------ read side */

export function all() {
  return state.docs.slice();
}

export function count() {
  return state.docs.length;
}

export function get(slugOrPath) {
  const key = String(slugOrPath || "").replace(/^.*\//, "").replace(/\.html$/, "");
  return state.bySlug.get(key) || null;
}

export function languages() {
  return (state.index && state.index.languages) || [];
}

export function years() {
  return (state.index && state.index.years) || [];
}

export function stats() {
  if (!state.index) return null;
  const words = state.docs.reduce(function (sum, d) { return sum + (d.words || 0); }, 0);
  return {
    count: state.index.count,
    languages: state.index.languages.length,
    years: state.index.years.slice().sort(),
    words: words,
    chunks: state.index.chunks.length,
    generated: state.index.generated,
  };
}

export function recent(n) {
  return state.docs
    .filter(function (d) { return d.slug !== ""; })
    .slice()
    .sort(function (a, b) { return (dateOf(b) || "").localeCompare(dateOf(a) || ""); })
    .slice(0, n || 5);
}

export function byLang(lang) {
  const want = normalize(lang);
  return state.docs.filter(function (d) { return normalize(d.lang).indexOf(want) === 0; });
}

export function byYear(year) {
  return state.docs.filter(function (d) { return d.published.slice(0, 4) === String(year); });
}

export function random() {
  const pool = state.docs.filter(function (d) { return d.slug !== ""; });
  return pool[Math.floor(Math.random() * pool.length)] || null;
}

/* --------------------------------------------------------------- search */

export function search(query, options) {
  const opts = options || {};
  const limit = opts.limit || 12;
  const raw = String(query || "").trim();
  if (!raw) return [];
  const tokens = tokensOf(raw);
  if (!tokens.length) return [];
  const phrase = normalize(raw);

  const results = [];
  for (let i = 0; i < state.docs.length; i++) {
    const doc = state.docs[i];
    const score = scoreDoc(doc, tokens, phrase, "");
    if (score > 0) {
      results.push(publicResult(doc, score, "", tokens));
    }
  }
  results.sort(function (a, b) {
    return b.score - a.score || (b.published || "").localeCompare(a.published || "");
  });
  return results.slice(0, limit);
}

/* Full-text search walks the text chunks on demand and reports progress.
 * Resolves with everything it found; `onResults` is called after each chunk so
 * the page can paint while the rest still travels. */
export function searchFull(query, options) {
  const opts = options || {};
  const limit = opts.limit || 12;
  const onResults = typeof opts.onResults === "function" ? opts.onResults : function () {};
  const onProgress = typeof opts.onProgress === "function" ? opts.onProgress : function () {};
  const raw = String(query || "").trim();
  if (!raw) return Promise.resolve([]);
  const tokens = tokensOf(raw);
  if (!tokens.length) return Promise.resolve([]);
  const phrase = normalize(raw);

  const seen = new Map();
  let index = 0;
  let retried = false;

  function report() {
    const list = Array.from(seen.values()).sort(function (a, b) {
      return b.score - a.score || (b.published || "").localeCompare(a.published || "");
    });
    onResults(list.slice(0, limit), list.length);
    return list;
  }

  function step() {
    // Read the manifest here, not before ready(): a caller may search on first paint,
    // and state.index is only filled once index.json has arrived.
    const files = (state.index && state.index.chunks) || [];
    if (!files.length) {
      if (retried) return Promise.resolve(report());
      retried = true;
      return Promise.resolve(ready()).then(step);
    }
    if (index >= files.length) return Promise.resolve(report());
    if (seen.size >= limit * 2 && index >= 4) return Promise.resolve(report());
    const chunk = files[index++];
    return loadChunk(chunk.file).then(function () {
      state.docs.forEach(function (doc) {
        if (!doc.slug) return;
        const text = state.texts.get(doc.slug);
        if (!text) return;
        const score = scoreDoc(doc, tokens, phrase, text);
        if (score > 0) {
          const previous = seen.get(doc.slug);
          if (!previous || previous.score < score) {
            seen.set(doc.slug, publicResult(doc, score, text, tokens));
          }
        }
      });
      onProgress({ loaded: index, total: files.length });
      report();
      return step();
    });
  }

  return Promise.resolve(ready()).then(step);
}

/* Load every chunk once, for callers that want full-text results in one go. */
export function loadAllText() {
  const files = (state.index && state.index.chunks) || [];
  return Promise.all(files.map(function (c) { return loadChunk(c.file); }));
}

export const BlogAPI = {
  ready: ready,
  all: all,
  count: count,
  get: get,
  languages: languages,
  years: years,
  stats: stats,
  recent: recent,
  byLang: byLang,
  byYear: byYear,
  random: random,
  search: search,
  searchFull: searchFull,
  loadAllText: loadAllText,
  normalize: normalize,
};

if (typeof window !== "undefined") {
  window.BlogAPI = BlogAPI;
}

export default BlogAPI;
