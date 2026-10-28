// Alegrete Summit 2026 — A fábula de Kauã: ilustrações geradas, cenas por rolagem, conversa digitada e parallax
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";
  var lang = (document.documentElement.lang || "pt").slice(0, 2);
  var locale = { pt: "pt-BR", en: "en-US", es: "es-ES" }[lang] || "pt-BR";

  function rng(seed) {
    var s = seed || 1;
    return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  }
  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function shade(hex, f) {
    var n = parseInt(hex.slice(1), 16);
    var r = Math.round(((n >> 16) & 255) * f), g = Math.round(((n >> 8) & 255) * f), b = Math.round((n & 255) * f);
    return "rgb(" + r + "," + g + "," + b + ")";
  }

  // árvores da floresta: copas redondas de várias alturas e algumas palmeiras (açaí)
  document.querySelectorAll(".kf-trees").forEach(function (g) {
    var rand = rng(+g.getAttribute("data-seed") || 3);
    var yBase = +g.getAttribute("data-y");
    var h = g.getAttribute("data-h").split(",").map(Number);
    var color = g.getAttribute("data-c");
    var xs = g.getAttribute("data-xs");
    var list = [];
    if (xs) list = xs.split(",").map(Number);
    else {
      var n = +g.getAttribute("data-n");
      for (var i = 0; i < n; i++) list.push((i + rand() * 0.8) * (840 / n) - 20);
    }
    list.forEach(function (x) {
      var hh = h[0] + rand() * (h[1] - h[0]);
      var top = yBase - hh;
      if (rand() < 0.28) {
        el("path", { d: "M" + x + " " + yBase + " Q" + (x + 6) + " " + (top + hh * 0.5) + " " + (x + 2) + " " + top, stroke: shade(color, 0.8), "stroke-width": Math.max(3, hh * 0.03), fill: "none" }, g);
        for (var j = 0; j < 7; j++) {
          var a = -Math.PI + (j / 6) * Math.PI, len = hh * 0.3;
          var ex = x + 2 + Math.cos(a) * len, ey = top + Math.sin(a) * len * 0.5 + len * 0.35;
          el("path", { d: "M" + (x + 2) + " " + top + " Q" + ((x + 2 + ex) / 2) + " " + (top - len * 0.25) + " " + ex + " " + ey, stroke: color, "stroke-width": Math.max(3, hh * 0.035), fill: "none", "stroke-linecap": "round" }, g);
        }
      } else {
        var w = Math.max(4, hh * 0.06);
        el("rect", { x: x - w / 2, y: top + hh * 0.15, width: w, height: hh * 0.85 + 4, fill: shade(color, 0.7) }, g);
        var r = hh * (0.2 + rand() * 0.08);
        el("circle", { cx: x, cy: top + r * 0.6, r: r, fill: color }, g);
        el("circle", { cx: x - r * 0.7, cy: top + r * 0.95, r: r * 0.75, fill: color }, g);
        el("circle", { cx: x + r * 0.75, cy: top + r * 0.9, r: r * 0.7, fill: shade(color, 1.12) }, g);
      }
    });
  });

  // estrelas
  document.querySelectorAll(".kf-stars").forEach(function (g, k) {
    var rand = rng(97 + k * 13), n = +g.getAttribute("data-n"), hMax = +g.getAttribute("data-h");
    for (var i = 0; i < n; i++) {
      el("circle", { cx: rand() * 800, cy: rand() * hMax, r: (0.6 + rand() * 1.4).toFixed(2), fill: "#fff", opacity: (0.3 + rand() * 0.7).toFixed(2) }, g);
    }
  });

  // conversa com a IA: as mensagens aparecem uma a uma, como se estivessem sendo digitadas
  var chat = document.querySelector("[data-chat]");
  var msgs = chat ? Array.prototype.slice.call(chat.querySelectorAll(".kf-msg")) : [];
  var chatStarted = false;
  if (chat && !reduce) chat.classList.add("ready");
  function playChat() {
    if (chatStarted || !chat) return;
    chatStarted = true;
    if (reduce) return;
    var i = 0;
    function next() {
      if (i >= msgs.length) return;
      var m = msgs[i++];
      var full = m.innerHTML;
      m.classList.add("shown");
      if (m.classList.contains("code") || m.classList.contains("sys")) { setTimeout(next, 1100); return; }
      var text = m.textContent, pos = 0;
      m.textContent = "";
      m.classList.add("typing");
      var speed = m.classList.contains("me") ? 22 : 14;
      (function type() {
        pos += 2;
        m.textContent = text.slice(0, pos);
        if (pos < text.length) setTimeout(type, speed);
        else { m.innerHTML = full; m.classList.remove("typing"); setTimeout(next, 650); }
      })();
    }
    next();
  }

  // contadores do sucesso internacional
  function count(dd) {
    var target = +dd.getAttribute("data-count");
    var fmt = function (v) { return Math.round(v).toLocaleString(locale); };
    if (reduce) { dd.textContent = fmt(target); return; }
    var t0 = performance.now(), dur = 1800;
    (function step(t) {
      var p = Math.min(1, (t - t0) / dur);
      dd.textContent = fmt(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    })(t0);
  }

  // cenas: entram uma vez (.on) e só animam enquanto visíveis (.vis)
  var scenes = Array.prototype.slice.call(document.querySelectorAll("[data-scene]"));
  function enter(s) {
    if (s.classList.contains("on")) return;
    s.classList.add("on");
    if (s.querySelector("[data-chat]")) playChat();
    s.querySelectorAll("[data-count]").forEach(count);
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        e.target.classList.toggle("vis", e.isIntersecting);
        if (e.isIntersecting && e.intersectionRatio >= 0.25) enter(e.target);
      });
    }, { threshold: [0, 0.25, 0.5] });
    scenes.forEach(function (s) { io.observe(s); });
  } else {
    scenes.forEach(function (s) { s.classList.add("vis"); enter(s); });
  }

  // parallax das camadas da floresta e barra de progresso da história
  var story = document.querySelector(".kf-story");
  var bar = document.querySelector(".kf-progress span");
  var layers = Array.prototype.slice.call(document.querySelectorAll(".kf-layer"));
  var ticking = false;
  function frame() {
    ticking = false;
    var vh = window.innerHeight;
    if (!reduce) {
      layers.forEach(function (g) {
        var svg = g.ownerSVGElement, r = svg.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var off = (r.top + r.height / 2 - vh / 2) / vh;
        g.style.transform = "translateY(" + (off * 120 * +g.getAttribute("data-depth")).toFixed(1) + "px)";
      });
    }
    if (story && bar) {
      var sr = story.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, -sr.top / Math.max(1, sr.height - vh)));
      bar.style.transform = "scaleX(" + p.toFixed(4) + ")";
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  frame();
})();
