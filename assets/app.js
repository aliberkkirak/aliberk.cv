(function () {
  "use strict";
  var d = document.documentElement;
  var azHareket = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var METIN = {
    tr: {
      title: "Ali Berk Kırak · Veri Analizi",
      kopya: "Bağlantı kopyalandı",
      yakinda: "Bu bağlantı yakında eklenecek",
      paylas: "Ali Berk Kırak · Veri analizi (Excel, Power BI, SQL)"
    },
    en: {
      title: "Ali Berk Kırak · Data Analysis",
      kopya: "Link copied",
      yakinda: "This link is coming soon",
      paylas: "Ali Berk Kırak · Data analysis (Excel, Power BI, SQL)"
    }
  };
  var dil = function () { return d.getAttribute("data-lang") === "en" ? "en" : "tr"; };
  var $ = function (s, k) { return (k || document).querySelector(s); };
  var $$ = function (s, k) { return Array.prototype.slice.call((k || document).querySelectorAll(s)); };

  /* Bildirim */
  var toast = $(".toast"), tz;
  function bildir(s) {
    toast.textContent = s; toast.classList.add("on");
    clearTimeout(tz); tz = setTimeout(function () { toast.classList.remove("on"); }, 2200);
  }

  /* Dil */
  var butonlar = $$(".lang button");
  function dilKoy(l, yumusak) {
    function uygula() {
      d.setAttribute("data-lang", l); d.lang = l;
      document.title = METIN[l].title;
      butonlar.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.set === l)); });
      try { localStorage.setItem("lang", l); } catch (e) {}
    }
    if (!yumusak || azHareket) return uygula();
    d.classList.add("swap");
    setTimeout(function () { uygula(); requestAnimationFrame(function () { d.classList.remove("swap"); }); }, 180);
  }
  butonlar.forEach(function (b) {
    b.addEventListener("click", function () { if (b.dataset.set !== dil()) dilKoy(b.dataset.set, true); });
  });
  dilKoy(dil(), false);

  /* Henüz bağlanmamış düğmeler */
  $$("[data-todo]").forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); bildir(METIN[dil()].yakinda); });
  });

  /* Paylaş: telefonda yerel paylaşım menüsü, yoksa kopyala */
  $("#paylas").addEventListener("click", function () {
    var url = "https://aliberk.cv/" + (dil() === "en" ? "?lang=en" : "");
    if (navigator.share) {
      navigator.share({ title: "Ali Berk Kırak", text: METIN[dil()].paylas, url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () { bildir(METIN[dil()].kopya); });
    } else { prompt("", url); }
  });

  /* Sayarak artan rakamlar */
  function say(el) {
    var hedef = +el.dataset.hedef, bas = null, sure = 1400;
    var yaz = function (n) { el.textContent = Math.round(n).toLocaleString("tr-TR"); };
    if (azHareket) return yaz(hedef);
    function adim(t) {
      if (!bas) bas = t;
      var p = Math.min(1, (t - bas) / sure);
      yaz(hedef * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(adim);
    }
    yaz(0); requestAnimationFrame(adim);
  }

  /* Kartlar ekrana girdikçe belirsin */
  var kartlar = $$(".r");
  function goster(k) {
    if (k.classList.contains("in")) return;
    k.classList.add("in");
    $$(".say", k).forEach(say);
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (g) {
      g.forEach(function (x) { if (x.isIntersecting) { goster(x.target); io.unobserve(x.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    kartlar.forEach(function (k, i) { k.style.transitionDelay = Math.min(i, 2) * 80 + "ms"; io.observe(k); });
  } else { kartlar.forEach(goster); }

  /* Proje kaydırıcısı: noktalar */
  var car = $("#carousel"), noktalar = $$(".dots i");
  if (car && noktalar.length) {
    var kartP = $$(".project", car);
    car.addEventListener("scroll", function () {
      var i = Math.round(car.scrollLeft / (kartP[0].offsetWidth + 12));
      noktalar.forEach(function (n, j) { n.classList.toggle("on", j === i); });
    }, { passive: true });
  }

  /* Tam ekran görsel */
  var lb = $("#lb"), lbImg = $(".lb-sahne img"), lbAlt = $(".lb-alt"), lbSay = $(".lb-say");
  var resimler = $$(".shot img"), basliklar = $$(".project h3"), simdiki = 0;
  function ac(i) {
    simdiki = (i + resimler.length) % resimler.length;
    lbImg.src = resimler[simdiki].src; lbImg.alt = resimler[simdiki].alt;
    var h = basliklar[simdiki].querySelector('[data-l="' + dil() + '"]');
    lbAlt.textContent = h ? h.textContent : "";
    lbSay.textContent = (simdiki + 1) + " / " + resimler.length;
  }
  $$(".shot").forEach(function (b) {
    b.addEventListener("click", function () {
      ac(+b.dataset.i);
      if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
      d.style.overflow = "hidden";
    });
  });
  function kapat() { if (lb.close) lb.close(); else lb.removeAttribute("open"); }
  lb.addEventListener("close", function () { d.style.overflow = ""; });
  $(".lb-x").addEventListener("click", kapat);
  $(".lb-onceki").addEventListener("click", function () { ac(simdiki - 1); });
  $(".lb-sonraki").addEventListener("click", function () { ac(simdiki + 1); });
  document.addEventListener("keydown", function (e) {
    if (!lb.open) return;
    if (e.key === "ArrowLeft") ac(simdiki - 1);
    if (e.key === "ArrowRight") ac(simdiki + 1);
  });
  /* Kaydırarak geç (tek parmak; iki parmak yakınlaştırmaya kalır) */
  var sx = null, sy = 0;
  lb.addEventListener("touchstart", function (e) {
    if (e.touches.length === 1) { sx = e.touches[0].clientX; sy = e.touches[0].clientY; } else sx = null;
  }, { passive: true });
  lb.addEventListener("touchend", function (e) {
    if (sx === null || (window.visualViewport && window.visualViewport.scale > 1.05)) return;
    var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) ac(simdiki + (dx < 0 ? 1 : -1));
    sx = null;
  }, { passive: true });

  /* Kartvizit: dokununca döner, eğilince ışık kayar */
  var kart = $("#kart"), kutu = $(".kart-kutu");
  if (kart) {
    var cevir = function () {
      var acik = kart.getAttribute("aria-pressed") === "true";
      kart.setAttribute("aria-pressed", String(!acik));
      $(".on-yuz").setAttribute("aria-hidden", String(!acik));
      $(".arka-yuz").setAttribute("aria-hidden", String(acik));
    };
    kart.addEventListener("click", function (e) { if (!e.target.closest("a")) cevir(); });
    var ip = $(".ipucu"); if (ip) ip.addEventListener("click", cevir);
    kart.addEventListener("keydown", function (e) {
      if ((e.key === "Enter" || e.key === " ") && !e.target.closest("a")) { e.preventDefault(); cevir(); }
    });
    var egil = function (x, y) { // x, y: -1..1
      kutu.style.setProperty("--ry", (x * 9).toFixed(2) + "deg");
      kutu.style.setProperty("--rx", (-y * 7).toFixed(2) + "deg");
      kart.style.setProperty("--isik", (-30 + (x + 1) * 40).toFixed(1) + "%");
    };
    if (!azHareket) {
      kutu.addEventListener("pointermove", function (e) {
        if (e.pointerType !== "mouse") return;
        var r = kutu.getBoundingClientRect();
        egil((e.clientX - r.left) / r.width * 2 - 1, (e.clientY - r.top) / r.height * 2 - 1);
      });
      kutu.addEventListener("pointerleave", function () { egil(0, 0); kart.style.removeProperty("--isik"); });
      /* Telefonda (izin istemeyen tarayıcılarda) cihaz eğildikçe kart da eğilir */
      if (window.DeviceOrientationEvent && typeof DeviceOrientationEvent.requestPermission !== "function") {
        var ilk = null;
        window.addEventListener("deviceorientation", function (e) {
          if (e.beta == null) return;
          if (!ilk) ilk = { b: e.beta, g: e.gamma };
          var x = Math.max(-1, Math.min(1, (e.gamma - ilk.g) / 25));
          var y = Math.max(-1, Math.min(1, (e.beta - ilk.b) / 25));
          egil(x, y);
        }, { passive: true });
      }
    }
  }

  $("#yil").textContent = new Date().getFullYear();
})();
