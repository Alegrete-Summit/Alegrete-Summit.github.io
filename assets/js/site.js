// Alegrete Summit 2026 — comportamento comum a todas as páginas
(function () {
  // menu em telas pequenas
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // contagem regressiva (horário de Brasília, UTC−3)
  var cd = document.querySelector("[data-countdown]");
  if (cd) {
    var start = new Date("2026-10-29T09:00:00-03:00");
    var end = new Date("2026-10-30T22:00:00-03:00");
    var now = new Date();
    var msg;
    if (now < start) {
      var days = Math.ceil((start - now) / 86400000);
      msg = days <= 1 ? "É amanhã! Começa às 9h do dia 29." : "Faltam " + days + " dias";
    } else if (now <= end) {
      msg = "Acontecendo agora no Sicredi Essência";
    } else {
      msg = "Obrigado por construir pontes com a gente! Até 2027.";
    }
    cd.textContent = msg;
  }

  // abas da programação
  var tabs = document.querySelectorAll("[role=tab]");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      tabs.forEach(function (t) {
        var sel = t === tab;
        t.setAttribute("aria-selected", sel ? "true" : "false");
        document.getElementById(t.getAttribute("aria-controls")).hidden = !sel;
      });
      try { history.replaceState(null, "", "#" + tab.getAttribute("aria-controls")); } catch (e) {}
    });
  });
  if (tabs.length && location.hash) {
    var target = document.querySelector('[aria-controls="' + location.hash.slice(1) + '"]');
    if (target) target.click();
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
