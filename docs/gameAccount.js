/* Monkey Blog — game accounts.
 *
 * One shared, local module for the level games (oJogoDoAdvogado.html and
 * oJogoDoOperador.html). It gives them three things without touching their
 * design:
 *   1. E-mail sign-in, through the Firebase project already used by the
 *      comments widget on index.html. E-mail is the only method offered here.
 *      It works through Google (Firebase) as the identity backend, but the
 *      player types an address and a password; no provider button is shown.
 *      An address only counts once Firebase confirms it: registration sends
 *      the verification link, and while user.emailVerified is false the note
 *      form stays closed. So a typed address has to exist and belong to who
 *      typed it before the form can be used.
 *   2. Score and certificate storage per player, in Firestore.
 *   3. One message per level, written and read only on the closing screen of
 *      that level.
 *
 * Loaded as <script type="module" src="./gameAccount.js"></script>. The games
 * call window.GameAccount from their own scripts and fall back to nothing when
 * this file has not run yet, or when the project is unreachable.
 *
 * Public API
 *   hud(lang)            account strip for the HUD
 *   level(opts)          note form + notes, for a level closing screen
 *   save(info)           points/certificate sync (debounced)
 *   afterRender()        fill the notes list after the game repaints
 *   click(event)         delegated clicks; returns true when handled
 */
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";
import {
  browserLocalPersistence,
  createUserWithEmailAndPassword,
  getAuth,
  onAuthStateChanged,
  sendPasswordResetEmail,
  setPersistence,
  sendEmailVerification,
  signInWithEmailAndPassword,
  signOut
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";
import {
  addDoc,
  collection,
  doc,
  getDocs,
  getFirestore,
  limit,
  orderBy,
  query,
  serverTimestamp,
  setDoc
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyAJm-VbCE6c-0shUsvFxKgFu9jnqdMU4So",
  authDomain: "blog-comments-6b4f5.firebaseapp.com",
  projectId: "blog-comments-6b4f5",
  storageBucket: "blog-comments-6b4f5.firebasestorage.app",
  messagingSenderId: "245435627450",
  appId: "1:245435627450:web:30fa931f6d447196604f83"
};

const PLAYERS = "gamePlayers";
const NOTES = "gameNotes";
const MAX_NAME = 60;
const MAX_NOTE = 280;
const AVATAR_HOSTS = ["lh3.googleusercontent.com"];
const LANG = {
  pt: {
    signout: "Sair",
    email: "E-mail",
    mailIn: "Entrar",
    mailUp: "Criar conta",
    mailReset: "Recuperar",
    mailFail: "E-mail ou palavra-passe errados.",
    mailBad: "Esse e-mail não parece válido.",
    mailShort: "A palavra-passe precisa de 6 caracteres.",
    mailNew: "Conta criada e sessão iniciada.",
    mailSent: "Ligação de recuperação enviada.",
    mailVerify: "Confirma o e-mail na caixa de entrada. Sem isso o formulário fica fechado.",
    verify: "Reenviar confirmação",
    verifySent: "Ligação de confirmação reenviada.",
    signedAs: "Sessão",
    noteTitle: "Mensagem deste nível",
    noteHint: "Só aparece no fim de cada nível. Máximo de 280 caracteres.",
    placeholder: "O que fica deste nível…",
    post: "Publicar",
    empty: "Ainda sem mensagens neste nível.",
    needSign: "Entra com o teu e-mail para publicar.",
    tooLong: "A mensagem passa dos 280 caracteres.",
    posted: "Publicada. Está aqui e na lista de jogadores.",
    failed: "Não foi possível guardar. Tenta outra vez.",
    saving: "A guardar…"
  },
  en: {
    signout: "Sign out",
    email: "Email",
    mailIn: "Sign in",
    mailUp: "Create account",
    mailReset: "Reset",
    mailFail: "Wrong email or password.",
    mailBad: "That e-mail does not look valid.",
    mailShort: "The password needs 6 characters.",
    mailNew: "Account created and signed in.",
    mailSent: "Reset link sent.",
    mailVerify: "Confirm the e-mail in your inbox. Until then the form stays closed.",
    verify: "Resend confirmation",
    verifySent: "Confirmation link sent again.",
    signedAs: "Session",
    noteTitle: "Message for this level",
    noteHint: "Only shown at the end of each level. 280 characters at most.",
    placeholder: "What this level leaves you…",
    post: "Post",
    empty: "No messages on this level yet.",
    needSign: "Sign in with your e-mail to post.",
    tooLong: "The message is over 280 characters.",
    posted: "Posted. It is here and on the players list.",
    failed: "Could not save. Try again.",
    saving: "Saving…"
  }
};

let app = null;
let auth = null;
let db = null;
let user = null;
let context = null;
let lastInfo = null;
let saveTimer = 0;
let notesSeq = 0;

try {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  db = getFirestore(app);
  setPersistence(auth, browserLocalPersistence).catch(function () {});
  onAuthStateChanged(auth, function (next) {
    user = next || null;
    if (user && window.localStorage) {
      try {
        const reminder = window.localStorage.getItem("gameAccount.signin");
        if (reminder) { window.localStorage.removeItem("gameAccount.signin"); }
      } catch (error) { /* private mode */ }
      flush();
    }
    syncLevel();
    afterRender();
    document.dispatchEvent(new CustomEvent("ga:change"));
  });
} catch (error) {
  app = null;
}

function esc(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function clean(value, max) {
  return String(value == null ? "" : value).trim().slice(0, max);
}

function nameOf() {
  if (!user) { return ""; }
  const fallback = user.email ? String(user.email).split("@")[0] : "";
  return clean(user.displayName || fallback || "Player", MAX_NAME);
}

function avatarOf() {
  const url = clean(user && user.photoURL, 300);
  if (!/^https:\/\//.test(url)) { return ""; }
  try {
    const host = new URL(url).hostname.toLowerCase();
    return AVATAR_HOSTS.indexOf(host) !== -1 ? url : "";
  } catch (error) {
    return "";
  }
}

function t(lang) {
  return LANG[lang === "en" ? "en" : "pt"];
}

function faceHTML(size) {
  const face = avatarOf();
  return face
    ? '<img src="' + esc(face) + '" alt="" width="' + size + '" height="' + size + '">'
    : "";
}

/* ---------------------------------------------------------------- account */

function hud(lang) {
  const text = t(lang);
  if (user) {
    const ready = verified();
    return '<div class="ga">' + faceHTML(20) +
      '<span class="ga-name">' + esc(nameOf()) + '</span>' +
      (ready ? "" :
        '<span class="ga-status" data-ga-mail>' + esc(text.mailVerify) + '</span>' +
        '<button type="button" class="ga-btn" data-ga="verify">' + esc(text.verify) + '</button>') +
      '<button type="button" class="ga-btn" data-ga="out">' + esc(text.signout) + '</button>' +
    '</div>';
  }
  return '<div class="ga">' +
    '<button type="button" class="ga-btn primary" data-ga="email" aria-expanded="false">' + esc(text.email) + '</button>' +
    '<form class="ga-form" data-ga-form="mail" hidden>' +
      '<input class="ga-input" type="email" name="mail" autocomplete="email" maxlength="254" placeholder="you@example.com" aria-label="' + esc(text.email) + '">' +
      '<input class="ga-input" type="password" name="pass" autocomplete="current-password" minlength="6" maxlength="128" placeholder="••••••" aria-label="' + esc(text.mailIn) + '">' +
      '<button type="button" class="ga-btn primary" data-ga="mailin">' + esc(text.mailIn) + '</button>' +
      '<button type="button" class="ga-btn" data-ga="mailup">' + esc(text.mailUp) + '</button>' +
      '<button type="button" class="ga-btn" data-ga="mailreset">' + esc(text.mailReset) + '</button>' +
      '<span class="ga-status" data-ga-mail></span>' +
    '</form>' +
  '</div>';
}

/* ------------------------------------------------------------ level notes */

/* The form is only usable for an address Firebase has confirmed. The player
 * registers, gets the link, confirms it, and only then does emailVerified
 * turn the textarea and the Post button on. */
function verified() {
  return Boolean(user && user.emailVerified);
}

function level(opts) {
  const lang = opts && opts.lang === "en" ? "en" : "pt";
  const text = t(lang);
  const open = verified();
  const game = clean(opts && opts.game, 40);
  const lvl = Number(opts && opts.level) || 0;
  const points = Number(opts && opts.points) || 0;
  const max = Number(opts && opts.max) || 0;
  context = { game: game, level: lvl, lang: lang, points: points, max: max };

  return '<div class="ga-note" data-ga-game="' + esc(game) + '" data-ga-level="' + lvl +
      '" data-ga-lang="' + lang + '" data-ga-points="' + points + '" data-ga-max="' + max + '">' +
    '<h3>' + esc(text.noteTitle) + '</h3>' +
    '<p>' + esc(text.noteHint) + '</p>' +
    '<div class="ga-slot">' + hud(lang) + '</div>' +
    '<textarea class="ga-input" maxlength="' + MAX_NOTE + '" rows="4" aria-label="' +
      esc(text.noteTitle) + '" placeholder="' + esc(text.placeholder) + '"' +
      (open ? "" : " disabled") + '></textarea>' +
    '<div class="ga-row">' +
      '<button type="button" class="ga-btn primary" data-ga="post"' + (open ? "" : " disabled") + '>' +
        esc(text.post) + '</button>' +
      '<span class="ga-status" data-ga-status>' +
        esc(user && !open ? text.mailVerify : "") + '</span>' +
    '</div>' +
    '<ul class="ga-notes" data-ga-notes><li class="ga-empty">' + esc(text.empty) + '</li></ul>' +
  '</div>';
}

function statusIn(host, message) {
  const status = host && host.querySelector("[data-ga-status]");
  if (status) { status.textContent = message || ""; }
}

function afterRender() {
  const host = document.querySelector("[data-ga-notes]");
  if (!host || !context || !db) { return; }
  loadNotes(host, context);
}

/* The note panel exists only on the level closing screen. Signing in from
 * there has to unlock it without waiting for the game to repaint. */
function syncLevel() {
  const panel = document.querySelector("[data-ga-game]");
  if (!panel) { return false; }
  const lang = panel.getAttribute("data-ga-lang") === "en" ? "en" : "pt";
  const slot = panel.querySelector(".ga-slot");
  if (slot) { slot.innerHTML = hud(lang); }
  const area = panel.querySelector(".ga-input");
  const button = panel.querySelector("[data-ga='post']");
  const open = verified();
  if (area) { area.disabled = !open; }
  if (button) { button.disabled = !open; }
  const status = panel.querySelector("[data-ga-status]");
  if (status && !open) { status.textContent = t(lang).mailVerify; }
  if (status && open && status.textContent === t(lang).mailVerify) { status.textContent = ""; }
  return open;
}

function loadNotes(host, ctx) {
  const seq = ++notesSeq;
  getDocs(query(collection(db, NOTES), orderBy("createdAt", "desc"), limit(300)))
    .then(function (snapshot) {
      if (seq !== notesSeq) { return; }
      const rows = [];
      snapshot.forEach(function (item) {
        const data = item.data() || {};
        if (data.game !== ctx.game || Number(data.level) !== Number(ctx.level)) { return; }
        rows.push(data);
      });
      if (!rows.length) {
        host.innerHTML = '<li class="ga-empty">' + esc(t(ctx.lang).empty) + "</li>";
        return;
      }
      host.innerHTML = rows.slice(0, 12).map(function (row) {
        const who = clean(row.name, MAX_NAME) || "Player";
        const stamp = when(row.createdAt, ctx.lang);
        return "<li><span class=\"who\">" + esc(who) + (stamp ? " · " + esc(stamp) : "") +
          "</span>" + esc(clean(row.text, MAX_NOTE)) + "</li>";
      }).join("");
    })
    .catch(function () {
      if (seq !== notesSeq) { return; }
      host.innerHTML = '<li class="ga-empty">' + esc(t(ctx.lang).empty) + "</li>";
    });
}

function when(value, lang) {
  if (!value) { return ""; }
  const date = typeof value.toDate === "function" ? value.toDate() : new Date(value);
  if (Number.isNaN(date.getTime())) { return ""; }
  try {
    return new Intl.DateTimeFormat(lang === "en" ? "en-GB" : "pt-PT", {
      day: "2-digit", month: "short"
    }).format(date);
  } catch (error) {
    return date.toISOString().slice(0, 10);
  }
}

function post(button) {
  const panel = button.closest("[data-ga-game]");
  if (!panel) { return; }
  const lang = panel.getAttribute("data-ga-lang") === "en" ? "en" : "pt";
  const text = t(lang);
  const area = panel.querySelector(".ga-input");
  const value = clean(area && area.value, MAX_NOTE);

  if (!user) { statusIn(panel, text.needSign); return; }
  if (!verified()) { statusIn(panel, text.mailVerify); return; }
  if (!value) { area && area.focus(); return; }
  if (area && area.value.trim().length > MAX_NOTE) { statusIn(panel, text.tooLong); return; }

  button.disabled = true;
  statusIn(panel, text.saving);

  addDoc(collection(db, NOTES), {
    uid: user.uid,
    name: nameOf(),
    photo: avatarOf(),
    game: clean(panel.getAttribute("data-ga-game"), 40),
    level: Number(panel.getAttribute("data-ga-level")) || 0,
    points: Number(panel.getAttribute("data-ga-points")) || 0,
    max: Number(panel.getAttribute("data-ga-max")) || 0,
    text: value,
    createdAt: serverTimestamp()
  }).then(function () {
    if (area) { area.value = ""; }
    statusIn(panel, text.posted);
    afterRender();
  }).catch(function () {
    statusIn(panel, text.failed);
  }).finally(function () {
    button.disabled = false;
  });
}

/* ----------------------------------------------------------------- scores */

function save(info) {
  if (!info) { return; }
  lastInfo = info;
  window.clearTimeout(saveTimer);
  saveTimer = window.setTimeout(flush, 900);
}

function flush() {
  if (!user || !db || !lastInfo) { return; }
  const info = lastInfo;
  const stamp = serverTimestamp();
  const payload = {
    uid: user.uid,
    name: nameOf(),
    photo: avatarOf(),
    provider: (user.providerData && user.providerData[0] && user.providerData[0].providerId) || "password",
    updatedAt: stamp,
    games: {}
  };
  payload.games[clean(info.game, 40)] = {
    points: Math.max(0, Number(info.points) || 0),
    max: Math.max(0, Number(info.max) || 0),
    levels: Math.max(0, Number(info.levels) || 0),
    level: Math.max(0, Number(info.level) || 0),
    answered: Math.max(0, Number(info.answered) || 0),
    total: Math.max(0, Number(info.total) || 0),
    certificate: Boolean(info.certificate),
    updatedAt: stamp
  };
  setDoc(doc(db, PLAYERS, user.uid), payload, { merge: true }).catch(function () {
    const panel = document.querySelector("[data-ga-status]");
    if (panel) { panel.textContent = t(context && context.lang).failed; }
  });
}

/* ------------------------------------------------------------------- auth */

function mailStatus(form, message) {
  const line = form && form.querySelector("[data-ga-mail]");
  if (line) { line.textContent = message || ""; }
}

const MAIL_SHAPE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$/;

/* Firebase is the only place that can say an address exists: the account has
 * to be created there and the player has to open the link sent to that
 * mailbox. Registration therefore sends the confirmation and reports it; the
 * form opens only once emailVerified is true. */
async function mail(kind, button) {
  const form = button.closest("[data-ga-game], .ga");
  const starter = button.closest("[data-ga-form]");
  const lang = context ? context.lang : "pt";
  const text = t(lang);
  if (!form || !starter || !auth) { return; }

  const addressField = starter.querySelector("input[type=email]");
  const passwordField = starter.querySelector("input[type=password]");
  const address = clean(addressField && addressField.value, 254);
  const password = (passwordField && passwordField.value) || "";

  if (!MAIL_SHAPE.test(address)) {
    mailStatus(form, text.mailBad);
    if (addressField) { addressField.focus(); }
    return;
  }
  if (kind !== "mailreset" && password.length < 6) {
    mailStatus(form, text.mailShort);
    if (passwordField) { passwordField.focus(); }
    return;
  }

  button.disabled = true;
  mailStatus(form, text.saving);

  try {
    if (kind === "mailreset") {
      await sendPasswordResetEmail(auth, address);
      mailStatus(form, text.mailSent);
      return;
    }
    if (kind === "mailup") {
      const created = await createUserWithEmailAndPassword(auth, address, password);
      await sendEmailVerification(created.user);
      mailStatus(form, text.mailVerify);
      return;
    }
    const signed = await signInWithEmailAndPassword(auth, address, password);
    if (signed.user && !signed.user.emailVerified) {
      await sendEmailVerification(signed.user).catch(function () {});
      mailStatus(form, text.mailVerify);
    } else {
      mailStatus(form, "");
    }
  } catch (error) {
    mailStatus(form, text.mailFail);
  } finally {
    button.disabled = false;
  }
}

function resend(button) {
  if (!auth || !auth.currentUser) { return; }
  const host = button.closest(".ga, [data-ga-game]");
  const text = t(context ? context.lang : "pt");
  const line = host && host.querySelector("[data-ga-mail], [data-ga-status]");
  button.disabled = true;
  sendEmailVerification(auth.currentUser).then(function () {
    if (line) { line.textContent = text.verifySent; }
  }).catch(function () {
    if (line) { line.textContent = text.failed; }
  }).finally(function () {
    button.disabled = false;
  });
}

/* Coming back from the inbox in another tab: reload the account and open the
 * form on the spot when the link has been used. */
function refreshVerification() {
  if (!user || user.emailVerified) { return; }
  user.reload().then(function () {
    if (user && user.emailVerified) {
      syncLevel();
      afterRender();
      document.dispatchEvent(new CustomEvent("ga:change"));
    }
  }).catch(function () {});
}

window.addEventListener("focus", refreshVerification);

function click(event) {
  const button = event.target.closest("[data-ga]");
  if (!button) { return false; }
  const action = button.getAttribute("data-ga");
  if (action === "email") {
    const menu = button.closest(".ga");
    const form = menu && menu.querySelector("[data-ga-form]");
    if (form) {
      form.hidden = !form.hidden;
      button.setAttribute("aria-expanded", form.hidden ? "false" : "true");
      const field = !form.hidden && form.querySelector("input[type=email]");
      if (field) { field.focus(); }
    }
    return true;
  }
  if (action === "mailin" || action === "mailup" || action === "mailreset") {
    mail(action, button);
    return true;
  }
  if (action === "verify") { resend(button); return true; }
  if (action === "out") {
    button.disabled = true;
    signOut(auth).catch(function () {}).finally(function () { button.disabled = false; });
    return true;
  }
  if (action === "post") { post(button); return true; }
  return false;
}

document.addEventListener("click", click);

document.addEventListener("submit", function (event) {
  if (!event.target.matches("[data-ga-form]")) { return; }
  event.preventDefault();
  const submit = event.target.querySelector("[data-ga='mailin']");
  if (submit) { mail("mailin", submit); }
});

window.GameAccount = { hud: hud, level: level, save: save, afterRender: afterRender, click: click };
