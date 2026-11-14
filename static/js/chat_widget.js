/*!
 * AI Sales Bot - embeddable chat widget (no dependencies, no Tailwind needed)
 *
 * Embed it on any website with ONE line, just before </body>:
 *
 *   <script src="https://YOUR-DOMAIN/static/js/chat_widget.js" data-key="CLIENT_KEY" defer></script>
 *
 * Optional attributes (all of them have defaults):
 *   data-api="https://api.example.com"   backend URL (default: same site the script is loaded from)
 *   data-title="Acme Assistant"          name shown in the header
 *   data-greeting="Hi! How can I help?"  first bot message
 *   data-color="#4F46E5"                 brand color (hex only, use a dark color)
 *   data-position="right"                "right" (default) or "left"
 *   data-placeholder="Type a message..." input placeholder
 *   data-privacy="Your chat is saved..." small note under the input
 *
 * Open or close it from your own button:  AISalesBot.open()  /  AISalesBot.close()
 */
(function () {
  "use strict";

  // Never load twice (e.g. if the script tag is pasted twice).
  if (window.AISalesBot) return;

  // ---------------------------------------------------------------------------
  // 1. SETTINGS: read from the <script> tag's data-* attributes
  // ---------------------------------------------------------------------------
  var script = document.currentScript || document.querySelector('script[src*="chat_widget.js"]');
  var attrs = (script && script.dataset) || {};

  var scriptOrigin = "";
  try { scriptOrigin = new URL(script.src, location.href).origin; } catch (e) { /* ignore */ }

  var CONFIG = {
    apiBase: (attrs.api || scriptOrigin).replace(/\/+$/, ""),
    clientKey: attrs.key || "",
    title: attrs.title || "AI Assistant",
    greeting: attrs.greeting || "Hi! How can I help you today?",
    placeholder: attrs.placeholder || "Type a message...",
    privacy: attrs.privacy || "Your chat is saved so our team can follow up.",
    // Only accept a plain hex color, so nothing else can be injected into the CSS.
    color: /^#[0-9a-fA-F]{3,8}$/.test(attrs.color || "") ? attrs.color : "#4F46E5",
    position: attrs.position === "left" ? "left" : "right",
  };

  var MAX_CHARS = 1000;      // must match the backend limit
  var MAX_SAVED = 50;        // messages kept in the browser between page loads
  var TIMEOUT_MS = 30000;    // give up waiting for the server after 30 seconds

  // ---------------------------------------------------------------------------
  // 2. STORAGE: remembers the chat while the tab is open (sessionStorage).
  //    Falls back to memory if the browser blocks storage.
  // ---------------------------------------------------------------------------
  var memory = {};
  var prefix = "aisb:" + (CONFIG.clientKey || "default") + ":";
  var store = {
    get: function (k) {
      try { return sessionStorage.getItem(prefix + k); } catch (e) { return memory[k] || null; }
    },
    set: function (k, v) {
      try { sessionStorage.setItem(prefix + k, v); } catch (e) { memory[k] = v; }
    },
    remove: function (k) {
      try { sessionStorage.removeItem(prefix + k); } catch (e) { delete memory[k]; }
    },
  };

  // ---------------------------------------------------------------------------
  // 3. STYLES + HTML (lives inside a Shadow DOM so the host website's CSS
  //    can never break the widget, and the widget can never break the site)
  // ---------------------------------------------------------------------------
  var CSS = [
    ":host{all:initial}",
    "*{box-sizing:border-box}",
    ".root{--c:" + CONFIG.color + ";font-family:system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1F2937}",

    /* floating button */
    ".launcher{position:fixed;bottom:20px;right:20px;width:60px;height:60px;border:0;border-radius:50%;background:var(--c);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.25);z-index:2147483000;transition:transform .2s}",
    ".launcher:hover{transform:scale(1.07)}",
    ".left .launcher{right:auto;left:20px}",

    /* chat window */
    ".window{position:fixed;bottom:92px;right:20px;width:380px;height:min(600px,calc(100vh - 120px));display:flex;flex-direction:column;background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 12px 40px rgba(67,56,202,.28);z-index:2147483000;opacity:0;visibility:hidden;transform:translateY(12px) scale(.98);transition:opacity .2s,transform .2s,visibility .2s}",
    ".left .window{right:auto;left:20px}",
    ".window.open{opacity:1;visibility:visible;transform:none}",

    /* header */
    ".header{display:flex;align-items:center;gap:12px;padding:14px 16px;background:var(--c);color:#fff}",
    ".avatar{flex:none;width:38px;height:38px;border-radius:50%;background:#fff;color:var(--c);font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center}",
    ".who{flex:1;min-width:0}",
    ".title{font-size:15px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
    ".status{display:flex;align-items:center;gap:6px;font-size:12px;opacity:.9;margin-top:2px}",
    ".dot{width:8px;height:8px;border-radius:50%;background:#34D399}",
    ".close{flex:none;width:36px;height:36px;border:0;border-radius:50%;background:transparent;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center}",
    ".close:hover{background:rgba(255,255,255,.18)}",

    /* messages */
    ".messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;background:#fff;overscroll-behavior:contain}",
    ".bubble{max-width:82%;padding:10px 14px;border-radius:14px;font-size:14px;line-height:1.45;white-space:pre-wrap;overflow-wrap:anywhere}",
    ".bot{align-self:flex-start;background:#F3F4F6;color:#1F2937;border-bottom-left-radius:4px}",
    ".user{align-self:flex-end;background:var(--c);color:#fff;border-bottom-right-radius:4px}",
    ".error{align-self:flex-start;background:#FEF2F2;color:#991B1B;border-bottom-left-radius:4px}",

    /* typing dots */
    ".typing{display:flex;gap:4px;padding:14px}",
    ".typing i{width:7px;height:7px;border-radius:50%;background:#9CA3AF;animation:bounce 1.2s infinite}",
    ".typing i:nth-child(2){animation-delay:.15s}",
    ".typing i:nth-child(3){animation-delay:.3s}",
    "@keyframes bounce{0%,60%,100%{transform:translateY(0);opacity:.5}30%{transform:translateY(-5px);opacity:1}}",

    /* input bar */
    ".composer{display:flex;gap:8px;padding:12px 12px 6px;background:#fff}",
    ".input{flex:1;min-width:0;height:40px;padding:0 16px;border:1px solid transparent;border-radius:20px;background:#F3F4F6;font:inherit;font-size:15px;color:#1F2937;outline:none}",
    ".input:focus{border-color:var(--c);background:#fff}",
    ".input::placeholder{color:#9CA3AF}",
    ".send{flex:none;width:40px;height:40px;border:0;border-radius:50%;background:var(--c);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center}",
    ".send:disabled{opacity:.5;cursor:not-allowed}",
    ".note{margin:0;padding:0 16px 10px;background:#fff;font-size:11px;color:#9CA3AF;text-align:center}",
    "button:focus-visible{outline:2px solid #fff;outline-offset:-4px}",
    ".launcher:focus-visible{outline:3px solid #A5B4FC;outline-offset:2px}",

    /* phones: chat takes the whole screen */
    "@media (max-width:480px){",
    ".window,.left .window{inset:0;width:100%;height:100%;border-radius:0}",
    ".input{font-size:16px}", /* 16px stops iPhones from zooming in on focus */
    ".open-mobile .launcher{display:none}",
    "}",

    "@media (prefers-reduced-motion:reduce){.window,.launcher{transition:none}.typing i{animation:none}}",
  ].join("\n");

  var ICON_CHAT =
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';
  var ICON_CLOSE =
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  var ICON_SEND =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';

  // Static markup only. Anything from settings or the server is added with textContent below.
  var HTML =
    '<div class="root">' +
    '<button class="launcher" type="button" aria-expanded="false" aria-controls="aisb-window">' + ICON_CHAT + "</button>" +
    '<section class="window" id="aisb-window" role="dialog" aria-modal="false">' +
    '<div class="header">' +
    '<div class="avatar" aria-hidden="true">AI</div>' +
    '<div class="who"><div class="title"></div><div class="status"><span class="dot"></span>Online now</div></div>' +
    '<button class="close" type="button" aria-label="Close chat">' + ICON_CLOSE + "</button>" +
    "</div>" +
    '<div class="messages" role="log" aria-live="polite"></div>' +
    '<form class="composer" autocomplete="off">' +
    '<input class="input" type="text" maxlength="' + MAX_CHARS + '" />' +
    '<button class="send" type="submit" aria-label="Send message">' + ICON_SEND + "</button>" +
    "</form>" +
    '<p class="note"></p>' +
    "</section></div>";

  // ---------------------------------------------------------------------------
  // 4. BUILD THE WIDGET
  // ---------------------------------------------------------------------------
  var els = {};   // references to the elements we need
  var state = {
    open: false,
    busy: false,                       // true while we wait for the bot
    token: store.get("token"),         // secret session token from the backend
    log: loadLog(),                    // [{from: "bot"|"user", text: "..."}]
  };

  function loadLog() {
    try {
      var saved = JSON.parse(store.get("log") || "[]");
      return Array.isArray(saved) ? saved : [];
    } catch (e) { return []; }
  }

  function saveLog() {
    store.set("log", JSON.stringify(state.log.slice(-MAX_SAVED)));
  }

  function build() {
    var host = document.createElement("div");
    host.id = "ai-sales-bot-widget";
    var shadow = host.attachShadow({ mode: "open" });
    shadow.innerHTML = "<style>" + CSS + "</style>" + HTML;
    document.body.appendChild(host);

    var $ = function (sel) { return shadow.querySelector(sel); };
    els.root = $(".root");
    els.launcher = $(".launcher");
    els.window = $(".window");
    els.close = $(".close");
    els.messages = $(".messages");
    els.form = $(".composer");
    els.input = $(".input");
    els.send = $(".send");

    // Settings go in as text (never as HTML) so they cannot inject markup.
    $(".title").textContent = CONFIG.title;
    $(".note").textContent = CONFIG.privacy;
    els.input.placeholder = CONFIG.placeholder;
    els.input.setAttribute("aria-label", CONFIG.placeholder);
    els.launcher.setAttribute("aria-label", "Chat with " + CONFIG.title);
    els.window.setAttribute("aria-label", "Chat with " + CONFIG.title);
    if (CONFIG.position === "left") els.root.classList.add("left");

    // Events
    els.launcher.addEventListener("click", function () { state.open ? close() : open(); });
    els.close.addEventListener("click", close);
    els.form.addEventListener("submit", onSubmit);
    shadow.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    // Show the greeting, then restore any earlier messages from this tab.
    addBubble("bot", CONFIG.greeting);
    state.log.forEach(function (m) { addBubble(m.from, m.text); });
  }

  // ---------------------------------------------------------------------------
  // 5. UI HELPERS
  // ---------------------------------------------------------------------------
  function open() {
    state.open = true;
    els.window.classList.add("open");
    els.root.classList.add("open-mobile");
    els.launcher.setAttribute("aria-expanded", "true");
    scrollDown();
    // Wait for the open animation (a hidden element can't take focus yet).
    // On phones we skip it: the keyboard would cover half the screen before the visitor reads the greeting.
    if (!window.matchMedia("(max-width: 480px)").matches) {
      setTimeout(function () { els.input.focus({ preventScroll: true }); }, 60);
    }
  }

  function close() {
    if (!state.open) return;
    state.open = false;
    els.window.classList.remove("open");
    els.root.classList.remove("open-mobile");
    els.launcher.setAttribute("aria-expanded", "false");
    els.launcher.focus({ preventScroll: true });
  }

  function addBubble(kind, text) {
    var div = document.createElement("div");
    div.className = "bubble " + kind;     // kind: "bot" | "user" | "error"
    div.textContent = text;               // textContent = always safe, no HTML is ever interpreted
    els.messages.appendChild(div);
    scrollDown();
    return div;
  }

  function remember(kind, text) {
    state.log.push({ from: kind, text: text });
    saveLog();
  }

  function showTyping() {
    var div = document.createElement("div");
    div.className = "bubble bot typing";
    div.setAttribute("aria-label", "The assistant is typing");
    div.innerHTML = "<i></i><i></i><i></i>";   // fixed markup, no user data
    els.messages.appendChild(div);
    scrollDown();
    return div;
  }

  function scrollDown() {
    els.messages.scrollTop = els.messages.scrollHeight;
  }

  function setBusy(isBusy) {
    state.busy = isBusy;
    els.send.disabled = isBusy;
    els.input.disabled = isBusy;
  }

  // ---------------------------------------------------------------------------
  // 6. TALKING TO THE BACKEND
  //    First message  -> POST /chat/          (returns session_token + reply)
  //    Later messages -> POST /chat/message   (send session_token + content)
  // ---------------------------------------------------------------------------
  function userError(message) {
    var err = new Error(message);
    err.isUserError = true;     // safe to show to the visitor
    return err;
  }

  async function readDetail(res) {
    try {
      var body = await res.json();
      return typeof body.detail === "string" ? body.detail : "";
    } catch (e) { return ""; }
  }

  async function askBot(text, isRetry) {
    var first = !state.token;
    var headers = { "Content-Type": "application/json" };
    if (CONFIG.clientKey) headers["X-Client-Key"] = CONFIG.clientKey;   // used later for multi-client support

    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, TIMEOUT_MS);

    var res;
    try {
      res = await fetch(CONFIG.apiBase + (first ? "/chat/" : "/chat/message"), {
        method: "POST",
        headers: headers,
        body: JSON.stringify(first ? { content: text } : { session_token: state.token, content: text }),
        signal: controller.signal,
      });
    } catch (e) {
      throw userError(e.name === "AbortError"
        ? "The assistant is taking too long to answer. Please try again."
        : "Can't reach the server. Please check your connection and try again.");
    } finally {
      clearTimeout(timer);
    }

    // The chat expired on the server: start a fresh one and resend once.
    if (res.status === 404 && !first && !isRetry) {
      state.token = null;
      store.remove("token");
      return askBot(text, true);
    }
    if (res.status === 429) {
      throw userError((await readDetail(res)) || "You're sending messages too fast. Please wait a moment.");
    }
    if (res.status === 422) {
      throw userError("Please send a shorter message (maximum " + MAX_CHARS + " characters).");
    }
    if (!res.ok) {
      throw userError("Sorry, something went wrong. Please try again.");
    }

    var data = await res.json();
    if (data.session_token) {            // only the first response contains it
      state.token = data.session_token;
      store.set("token", state.token);
    }
    return data.reply || "Sorry, I couldn't process that.";
  }

  async function onSubmit(event) {
    event.preventDefault();
    var text = els.input.value.trim();
    if (!text || state.busy) return;

    els.input.value = "";
    addBubble("user", text);
    remember("user", text);
    setBusy(true);
    var typing = showTyping();

    try {
      var reply = await askBot(text);
      typing.remove();
      addBubble("bot", reply);
      remember("bot", reply);
    } catch (err) {
      typing.remove();
      addBubble("error", err.isUserError ? err.message : "Sorry, something went wrong. Please try again.");
    } finally {
      setBusy(false);
      els.input.focus({ preventScroll: true });
    }
  }

  // ---------------------------------------------------------------------------
  // 7. START (wait for <body> to exist), and expose open/close for your own buttons
  // ---------------------------------------------------------------------------
  window.AISalesBot = {
    open: function () { if (els.window) open(); },
    close: function () { if (els.window) close(); },
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
