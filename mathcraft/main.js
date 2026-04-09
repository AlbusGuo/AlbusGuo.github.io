/* MathCraft Landing – Interactions */
(function () {
  "use strict";

  /* ── Nav scroll shadow ── */
  var nav = document.getElementById("nav");
  if (nav) {
    window.addEventListener("scroll", function () {
      nav.classList.toggle("scrolled", window.scrollY > 10);
    }, { passive: true });
  }

  /* ── Showcase tab ↔ image switching ── */
  var tabs = document.querySelectorAll(".showcase-tab");
  var imgs = document.querySelectorAll(".showcase-img");

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      tabs.forEach(function (t) { t.classList.remove("active"); });
      tab.classList.add("active");
      var key = tab.getAttribute("data-demo");
      imgs.forEach(function (img) {
        img.classList.toggle("active", img.getAttribute("data-demo") === key);
      });
    });
  });

  /* ── Smooth scroll for anchor links ── */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var target = document.querySelector(a.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  /* ── Theme toggle ── */
  var html = document.documentElement;
  var themeBtn = document.getElementById("themeToggle");
  var stored = localStorage.getItem("theme");
  if (stored === "dark" || (!stored && window.matchMedia("(prefers-color-scheme:dark)").matches)) {
    html.classList.add("dark");
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      html.classList.toggle("dark");
      localStorage.setItem("theme", html.classList.contains("dark") ? "dark" : "light");
    });
  }
})();
