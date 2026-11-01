(function () {
  "use strict";
  var d = document.documentElement;
  var METIN = {
    tr: {
      title: "Ali Berk · Veri Analizi",
      kopya: "Bağlantı kopyalandı",
      yakinda: "Bu bağlantı yakında eklenecek",
      paylas: "Ali Berk · Veri analizi (Excel, Power BI, SQL)"
    },
    en: {
      title: "Ali Berk · Data Analysis",
      kopya: "Link copied",
      yakinda: "This link is coming soon",
      paylas: "Ali Berk · Data analysis (Excel, Power BI, SQL)"
    }
  };
  var dil = function () { return d.getAttribute("data-lang") === "en" ? "en" : "tr"; };

  /* Bildirim */
  var toast = document.querySelector(".toast"), tz;
  function bildir(s) {
    toast.textContent = s;
    toast.classList.add("on");
    clearTimeout(tz);
    tz = setTimeout(function () { toast.classList.remove("on"); }, 2200);
  }

  /* Dil */
  var butonlar = document.querySelectorAll(".lang button");
  function dilKoy(l, yumusak) {
    function uygula() {
      d.setAttribute("data-lang", l);
      d.lang = l;
      document.title = METIN[l].title;
      butonlar.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.set === l)); });
      try { localStorage.setItem("lang", l); } catch (e) {}
    }
    var azHareket = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!yumusak || azHareket) return uygula();
    d.classList.add("swap");
    setTimeout(function () {
      uygula();
      requestAnimationFrame(function () { d.classList.remove("swap"); });
    }, 180);
  }
  butonlar.forEach(function (b) {
    b.addEventListener("click", function () { if (b.dataset.set !== dil()) dilKoy(b.dataset.set, true); });
  });
  dilKoy(dil(), false);

  /* Henüz bağlanmamış düğmeler */
  document.querySelectorAll('[data-todo]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (a.getAttribute("href") === "#" || a.dataset.todo === "cv") {
        e.preventDefault();
        bildir(METIN[dil()].yakinda);
      }
    });
  });

  /* Paylaş: telefonda yerel paylaşım menüsü, yoksa kopyala */
  document.getElementById("paylas").addEventListener("click", function () {
    var url = "https://aliberk.cv/";
    if (navigator.share) {
      navigator.share({ title: "Ali Berk", text: METIN[dil()].paylas, url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () { bildir(METIN[dil()].kopya); });
    } else {
      prompt("", url);
    }
  });

  /* Kartlar ekrana girdikçe belirsin */
  var kartlar = document.querySelectorAll(".r");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (girdiler) {
      girdiler.forEach(function (g) {
        if (g.isIntersecting) { g.target.classList.add("in"); io.unobserve(g.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    kartlar.forEach(function (k, i) {
      k.style.transitionDelay = Math.min(i, 2) * 70 + "ms";
      io.observe(k);
    });
  } else {
    kartlar.forEach(function (k) { k.classList.add("in"); });
  }

  document.getElementById("yil").textContent = new Date().getFullYear();
})();
