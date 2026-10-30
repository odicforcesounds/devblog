/* ==========================================================================
   article-lang.js — shared PT/EN switch for the article family.
   Each page holds one <article class="doc" data-lang="pt|en" data-title
   data-desc> per language; exactly one is visible. Portuguese is the
   default; the choice is remembered across the site.
   ========================================================================== */
(function () {
  "use strict";

  var KEY = "monkeyblog:lang";
  var articles = Array.prototype.slice.call(document.querySelectorAll("article.doc[data-lang]"));
  if (articles.length < 2) return;

  var buttons = Array.prototype.slice.call(document.querySelectorAll(".lang-switch button[data-lang]"));
  var byLang = {};
  articles.forEach(function (article) { byLang[article.getAttribute("data-lang")] = article; });

  function stored() {
    try { return window.localStorage.getItem(KEY); } catch (error) { return null; }
  }

  function save(lang) {
    try { window.localStorage.setItem(KEY, lang); } catch (error) { /* private mode */ }
  }

  function fromQuery() {
    var match = /[?&]lang=(pt|en)\b/.exec(window.location.search);
    return match ? match[1] : null;
  }

  function meta(selector, value) {
    var node = document.querySelector(selector);
    if (node && value) node.setAttribute("content", value);
  }

  function apply(lang) {
    if (!byLang[lang]) lang = byLang.pt ? "pt" : articles[0].getAttribute("data-lang");
    var article = byLang[lang];
    var title = article.getAttribute("data-title") || document.title;
    var desc = article.getAttribute("data-desc") || "";
    var y = window.pageYOffset;

    articles.forEach(function (node) {
      node.hidden = node !== article;
    });

    document.documentElement.lang = article.getAttribute("lang") || (lang === "pt" ? "pt-PT" : "en");
    document.title = title;

    meta('meta[name="description"]', desc);
    meta('meta[property="og:title"]', title);
    meta('meta[property="og:description"]', desc);
    meta('meta[name="twitter:title"]', title);
    meta('meta[name="twitter:description"]', desc);
    meta('meta[property="og:locale"]', lang === "pt" ? "pt_PT" : "en_GB");

    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", button.getAttribute("data-lang") === lang ? "true" : "false");
    });

    try { window.scrollTo(0, Math.min(y, document.documentElement.scrollHeight)); } catch (error) { /* ignore */ }
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var lang = button.getAttribute("data-lang");
      save(lang);
      apply(lang);
    });
  });

  var initial = fromQuery() || stored();
  if (initial !== "pt" && initial !== "en") initial = byLang.pt ? "pt" : articles[0].getAttribute("data-lang");
  apply(initial);

  window.__setArticleLang = apply;
})();
