/* ========================================
   PulseChat AI - Main Script
   ======================================== */

// === Initialize AOS Animations ===
document.addEventListener("DOMContentLoaded", function () {
  if (typeof AOS !== "undefined") {
    AOS.init({ duration: 800, once: true, offset: 100 });
  } else {
    var checkAOS = setInterval(function () {
      if (typeof AOS !== "undefined") {
        AOS.init({ duration: 800, once: true, offset: 100 });
        clearInterval(checkAOS);
      }
    }, 100);
  }
});

// === Mobile Menu Toggle ===
function toggleMenu() {
  var menu = document.getElementById("mobile-menu");
  menu.classList.toggle("hidden");
}

// === Close Mobile Menu on Link Click ===
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("#mobile-menu a").forEach(function (link) {
    link.addEventListener("click", function () {
      document.getElementById("mobile-menu").classList.add("hidden");
    });
  });
});

// === Navbar Shadow on Scroll ===
window.addEventListener("scroll", function () {
  var navbar = document.getElementById("navbar");
  if (window.scrollY > 50) {
    navbar.classList.add("shadow-lg");
  } else {
    navbar.classList.remove("shadow-lg");
  }
});
