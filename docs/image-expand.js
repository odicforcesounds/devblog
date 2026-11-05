(function () {
  "use strict";

  var OVERLAY = "img-expand-overlay";
  var active = null;

  function installStyle() {
    if (document.getElementById("img-expand-style")) return;
    var sheet = document.createElement("style");
    sheet.id = "img-expand-style";
    sheet.textContent =
      "img[data-expand]{cursor:zoom-in}" +
      "#" + OVERLAY + "{position:fixed;inset:0;z-index:1000;display:flex;align-items:center;" +
      "justify-content:center;padding:3vmin;background:rgba(4,7,10,.92);cursor:zoom-out;" +
      "-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}" +
      "#" + OVERLAY + " img{max-width:96vw;max-height:94vh;width:auto;height:auto;" +
      "border:1px solid rgba(255,255,255,.22);border-radius:.6rem;" +
      "box-shadow:0 1.5rem 4rem rgba(0,0,0,.6);background:#101018;cursor:default}" +
      "#" + OVERLAY + ":focus-visible{outline:none}" +
      "@media print{#" + OVERLAY + "{display:none}}";
    document.head.appendChild(sheet);
  }

  function bigger(src) {
    return String(src || "").replace(/\/(\d+)px-/, "/500px-");
  }

  function close() {
    if (!active) return;
    var opener = active.opener;
    if (active.node.parentNode) active.node.parentNode.removeChild(active.node);
    active = null;
    if (opener && opener.setAttribute) opener.setAttribute("aria-expanded", "false");
    if (opener && opener.focus) {
      try { opener.focus(); } catch (error) { /* the opener can be gone */ }
    }
  }

  function open(image) {
    installStyle();
    close();
    var box = document.createElement("div");
    box.id = OVERLAY;
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", image.alt ? "Expanded photograph: " + image.alt : "Expanded photograph");
    box.tabIndex = -1;

    var big = document.createElement("img");
    big.src = bigger(image.currentSrc || image.src);
    big.alt = image.alt || "";
    big.decoding = "async";
    box.appendChild(big);

    box.addEventListener("click", close);
    document.body.appendChild(box);
    box.focus();
    image.setAttribute("aria-expanded", "true");
    active = { node: box, opener: image };
  }

  function isInside(node, selector) {
    return !!(node && node.closest && node.closest(selector));
  }

  function candidate(image) {
    if (!image || image.tagName !== "IMG") return false;
    if (isInside(image, ".living-panel")) return false;
    if (isInside(image, "#" + OVERLAY)) return false;
    return isInside(image, "main");
  }

  function usable(image) {
    return candidate(image) && (image.naturalWidth || image.width || 0) >= 48;
  }

  function arm(image) {
    if (!candidate(image) || image.getAttribute("data-expand")) return;
    image.setAttribute("data-expand", "1");
    image.setAttribute("role", "button");
    image.setAttribute("tabindex", "0");
    image.setAttribute("aria-expanded", "false");
    if (!image.getAttribute("aria-label")) {
      image.setAttribute("aria-label", image.alt ? "Expand the photograph: " + image.alt
                                                 : "Expand the photograph");
    }
  }

  function armAll(root) {
    if (!root || !root.querySelectorAll) return;
    var images = root.querySelectorAll("img");
    for (var index = 0; index < images.length; index += 1) arm(images[index]);
    if (root.tagName === "IMG") arm(root);
  }

  document.addEventListener("click", function (event) {
    var image = event.target;
    while (image && image !== document.body && image.tagName !== "IMG") {
      image = image.parentNode;
    }
    if (!usable(image)) return;
    event.preventDefault();
    event.stopPropagation();
    open(image);
  }, true);

  document.addEventListener("keydown", function (event) {
    if (active && (event.key === "Escape" || event.key === "Esc")) {
      event.preventDefault();
      close();
      return;
    }
    var image = event.target;
    if (!image || image.tagName !== "IMG") return;
    if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") {
      if (!usable(image)) return;
      event.preventDefault();
      open(image);
    }
  });

  armAll(document);
  installStyle();
  new MutationObserver(function (records) {
    records.forEach(function (record) {
      Array.prototype.forEach.call(record.addedNodes, function (node) {
        if (node.nodeType === 1) armAll(node);
      });
    });
  }).observe(document.body, { childList: true, subtree: true });
})();
