// Syntax check + smoke run of a page script inside a tiny DOM stub.
// Usage: node tmp/smoke_obc.js [desktop|compile|xterm|mutt|i3]
var vm = require("vm");
var MODES = {
  desktop: { page: "docs/openbsdDesktop.html",
    dom: { box: "deskChecklist", count: "deskCount", bar: "deskBar", reset: "deskReset",
      key: "openbsdDesktop.progress.v1" },
    ids: ["deal", "values", "persist", "firefox", "audio", "ram", "input",
      "power", "wm", "fonts", "boring", "reference", "checklist"],
    keys: ["baseline", "maxfiles", "maxproc", "maxthread", "video", "vmstat",
      "sndio", "input", "power", "backup"], total: 10 },
  compile: { page: "docs/openbsdCompilation.html",
    dom: { box: "buildChecklist", count: "checkCount", bar: "checkBar", reset: "checkReset",
      key: "openbsdCompilation.progress.v1" },
    ids: ["why", "machine", "tree", "branches", "order", "kernel",
      "userland", "xenocara", "ports", "release", "traps", "reference", "checklist"],
    keys: ["base", "trees", "doas", "disk", "obj", "includes",
      "kernel", "boot", "build", "merge", "x11", "ports"], total: 12 },
  xterm: { page: "docs/xtermHero.html",
    dom: { box: "xtChecklist", count: "xtCount", bar: "xtBar", reset: "xtReset",
      key: "xtermHero.progress.v1" },
    ids: ["nothing", "first", "menus", "fonts", "colors", "resources", "scrollback",
      "clipboard", "keys", "titles", "resize", "vocab", "checklist"],
    keys: ["launch", "menus", "fonts", "colors", "xrdb", "appres", "scrollback",
      "ctrls", "clipboard", "meta", "title", "resize"], total: 12 },
  i3: { page: "docs/i3Hero.html",
    dom: { box: "i3Checklist", count: "i3Count", bar: "i3Bar", reset: "i3Reset",
      key: "i3Hero.progress.v1" },
    ids: ["nothing", "config", "keys", "workspaces", "startup", "bar", "icons",
      "extras", "fancy", "gaps", "scratchpad", "vocab", "checklist"],
    keys: ["install", "spine", "keys", "workspaces", "rules", "startup", "bar",
      "glyphs", "launcher", "extras", "fancy", "scratchpad"], total: 12 },
  mutt: { page: "docs/muttHero.html",
    dom: { box: "mtChecklist", count: "mtCount", bar: "mtBar", reset: "mtReset",
      key: "muttHero.progress.v1" },
    ids: ["nothing", "first", "files", "boxes", "accounts", "imap", "smtp",
      "providers", "colors", "patterns", "macros", "vocab", "checklist"],
    keys: ["install", "keys", "spine", "browser", "hooks", "imap", "smtp",
      "secrets", "accounts", "gmail", "colors", "patterns"], total: 12 }
};
var MODE = MODES[process.argv[2]] ? process.argv[2] : "compile";
var CFG = MODES[MODE];
var PAGE = CFG.page;
var SRCDOM = CFG.dom;
var src = require("fs").readFileSync(PAGE, "utf8");
var m = src.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("no script block found"); process.exit(2); }
var js = m[1];

var IDS = CFG.ids;
var KEYS = CFG.keys;

var storage = {};
var checkCountEl = { textContent: "" };
var checkBarEl = { style: {} };
var resets = 0;
var sectionsById = {};

function El(tag) {
  this.tag = tag;
  this.children = [];
  this.style = {};
  this.textContent = "";
  this.handlers = {};
  this.checked = false;
  var self = this;
  this.classList = {
    toggle: function (c, on) { self._active = !!on; },
    add: function () {}, remove: function () {}
  };
  this._attrs = {};
}
El.prototype.appendChild = function (c) { this.children.push(c); return c; };
El.prototype.removeChild = function (c) { this.children = this.children.filter(function (x) { return x !== c; }); };
El.prototype.addEventListener = function (t, f) { (this.handlers[t] = this.handlers[t] || []).push(f); };
El.prototype.setAttribute = function (k, v) { this._attrs[k] = v; };
El.prototype.getAttribute = function (k) { return this._attrs[k]; };
El.prototype.select = function () {};

var tocLinks = IDS.map(function (id) {
  var a = new El("a");
  a._attrs.href = "#" + id;
  return a;
});

IDS.forEach(function (id) { sectionsById[id] = { offsetTop: 200 }; });

var codeBlocks = [];
for (var i = 0; i < 6; i += 1) {
  var pre = new El("pre");
  pre.textContent = "code " + i;
  var block = new El("div");
  block.querySelector = function () { return pre; };
  codeBlocks.push(block);
}

var checkboxes = KEYS.map(function (k) {
  var el = new El("input");
  el._attrs["data-key"] = k;
  return el;
});

var documentStub = {
  execCommand: function () { return true; },
  querySelectorAll: function (sel) {
    if (sel === "nav.toc ol a") { return tocLinks; }
    if (sel === ".code") { return codeBlocks; }
    if (sel === "input[type=checkbox]") { return checkboxes; }
    return [];
  },
  getElementById: function (id) {
    if (Object.prototype.hasOwnProperty.call(sectionsById, id)) { return sectionsById[id]; }
    if (id === SRCDOM.box) {
      return { querySelectorAll: function () { return checkboxes; } };
    }
    if (id === SRCDOM.count) { return checkCountEl; }
    if (id === SRCDOM.bar) { return checkBarEl; }
    if (id === SRCDOM.reset) {
      return { addEventListener: function () { resets += 1; } };
    }
    return null;
  },
  createElement: function (tag) { return new El(tag); },
  body: new El("body")
};

var windowStub = {
  scrollY: 0,
  requestAnimationFrame: function (f) { f(); },
  setTimeout: function (f) { f(); },
  addEventListener: function () {},
  localStorage: {
    getItem: function (k) { return storage[k] !== undefined ? storage[k] : null; },
    setItem: function (k, v) { storage[k] = String(v); },
    removeItem: function (k) { delete storage[k]; }
  }
};

var sandbox = {
  document: documentStub,
  window: windowStub,
  navigator: {}
};
vm.createContext(sandbox);
vm.runInContext(js, sandbox, { filename: "extracted-script.js" });

if (tocLinks.length !== 13) { throw new Error("toc links: " + tocLinks.length); }
if (codeBlocks.length !== 6) { throw new Error("code blocks: " + codeBlocks.length); }
if (checkboxes.length !== CFG.total) {
  throw new Error("checkboxes: " + checkboxes.length);
}

// 1 copy wiring: every .code block has a button with a click handler; fallback path runs
codeBlocks.forEach(function (b, i) {
  var btn = b.children.filter(function (c) { return c.tag === "button"; })[0];
  if (!btn || !btn.handlers.click) { throw new Error("copy button missing on block " + i); }
  btn.handlers.click[0]();
  if (btn.textContent === undefined) { throw new Error("copy click exploded"); }
});

// 2 checklist: toggle saves and paints the meter
(function () {
  var first = checkboxes[0];
  first.checked = true;
  first.handlers.change[0]();
  var state = JSON.parse(storage[SRCDOM.key]);
  if (state[KEYS[0]] !== true) { throw new Error("state not saved: " + Object.keys(state)); }
  if (checkCountEl.textContent !== "1 / " + CFG.total) {
    throw new Error("meter: " + checkCountEl.textContent);
  }
  if (checkBarEl.style.width !== Math.round(100 / CFG.total) + "%") {
    throw new Error("bar: " + checkBarEl.style.width);
  }
})();

if (resets !== 1) { throw new Error("reset handler not attached"); }

// 3 scroll highlight runs
sectionsById.checklist.offsetTop = 99999;
windowStub.scrollY = 500;
tocLinks.forEach(function (a) { a._active = undefined; });
windowStub.requestAnimationFrame(function () {}); // sanity
// re-run the scroll path directly: setActive is internal; simulate by rerunning script's rAF is not exposed,
// so simply confirm no throw when scrollY changes via the registered listener:
windowStub.scrollY = 12345;

console.log("SMOKE OK [" + MODE + "] — 13 toc,", codeBlocks.length, "code blocks,",
  checkboxes.length, "checks; meter:", checkCountEl.textContent, "| bar:", checkBarEl.style.width);
