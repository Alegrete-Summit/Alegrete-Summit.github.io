// Alegrete Summit 2026 — comportamento comum a todas as páginas
(function () {
  var lang = (document.documentElement.lang || "pt").slice(0, 2);

  var T = {
    pt: {
      faltam: function (d) { return "Faltam " + d + " dias"; },
      amanha: "É amanhã! Começa às 9h do dia 29.",
      agora: "Acontecendo agora no Sicredi Essência",
      depois: "Obrigado por construir pontes com a gente! Até 2027."
    },
    en: {
      faltam: function (d) { return d + " days to go"; },
      amanha: "It's tomorrow! Starts at 9:00 on October 29.",
      agora: "Happening now at Sicredi Essência",
      depois: "Thank you for building bridges with us! See you in 2027."
    },
    es: {
      faltam: function (d) { return "Faltan " + d + " días"; },
      amanha: "¡Es mañana! Empieza a las 9:00 del 29 de octubre.",
      agora: "Sucediendo ahora en Sicredi Essência",
      depois: "¡Gracias por construir puentes con nosotros! Hasta 2027."
    }
  }[lang] || null;

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { return null; }
  }

  // menu em telas pequenas e médias
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  function setMenu(open) {
    nav.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () { setMenu(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { setMenu(false); toggle.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (nav.classList.contains("open") && !e.target.closest(".site-header")) setMenu(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1240 && nav.classList.contains("open")) setMenu(false);
    });
  }

  // lembra o idioma escolhido no seletor
  document.querySelectorAll(".lang a, .lang-foot a[hreflang]").forEach(function (a) {
    a.addEventListener("click", function () { store("summit-lang", a.getAttribute("hreflang").slice(0, 2)); });
  });

  // sugere a versão no idioma do navegador (só na versão em português, sem redirecionar)
  if (lang === "pt" && !store("summit-lang")) {
    var pref = (navigator.languages && navigator.languages[0]) || navigator.language || "";
    pref = pref.slice(0, 2).toLowerCase();
    var link = document.querySelector('.lang a[hreflang="' + pref + '"]');
    if ((pref === "en" || pref === "es") && link) {
      var msg = pref === "en" ? "This site is also available in English." : "Este sitio también está disponible en español.";
      var go = pref === "en" ? "View in English" : "Ver en español";
      var bar = document.createElement("div");
      bar.className = "lang-hint";
      bar.setAttribute("role", "region");
      bar.setAttribute("aria-label", pref === "en" ? "Language" : "Idioma");
      bar.innerHTML = '<span></span><a class="btn solid"></a><button type="button" aria-label="Fechar">×</button>';
      bar.querySelector("span").textContent = msg;
      var a = bar.querySelector("a");
      a.textContent = go;
      a.href = link.getAttribute("href");
      a.addEventListener("click", function () { store("summit-lang", pref); });
      bar.querySelector("button").addEventListener("click", function () { store("summit-lang", "pt"); bar.remove(); });
      document.body.appendChild(bar);
    }
  }

  // contagem regressiva (horário de Brasília, UTC−3)
  var cd = document.querySelector("[data-countdown]");
  if (cd && T) {
    var start = new Date("2026-10-29T09:00:00-03:00");
    var end = new Date("2026-10-30T22:00:00-03:00");
    var now = new Date();
    if (now < start) {
      var days = Math.ceil((start - now) / 86400000);
      cd.textContent = days <= 1 ? T.amanha : T.faltam(days);
    } else if (now <= end) {
      cd.textContent = T.agora;
    } else {
      cd.textContent = T.depois;
    }
  }

  // abas da programação (clique e setas do teclado)
  var tabs = Array.prototype.slice.call(document.querySelectorAll("[role=tab]"));
  function select(tab) {
    tabs.forEach(function (t) {
      var sel = t === tab;
      t.setAttribute("aria-selected", sel ? "true" : "false");
      t.tabIndex = sel ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !sel;
    });
    try { history.replaceState(null, "", "#" + tab.getAttribute("aria-controls")); } catch (e) {}
  }
  tabs.forEach(function (tab, i) {
    tab.addEventListener("click", function () { select(tab); });
    tab.addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!d) return;
      var next = tabs[(i + d + tabs.length) % tabs.length];
      select(next);
      next.focus();
    });
  });
  if (tabs.length && location.hash) {
    var target = document.querySelector('[aria-controls="' + location.hash.slice(1) + '"]');
    if (target) select(target);
  }

  // revelar ao rolar
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }
})();
