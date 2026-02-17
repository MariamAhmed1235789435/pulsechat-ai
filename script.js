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

// === Contact Form Submission ===
document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("contact-form");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    var btn = form.querySelector('button[type="submit"]');
    var successDiv = document.getElementById("form-success");
    var successText = document.getElementById("success-text");
    var errorDiv = document.getElementById("form-error");
    var originalText = btn.innerHTML;

    // Hide previous messages
    successDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");

    // Show loading
    btn.innerHTML = '<i class="fas fa-spinner fa-spin ml-2"></i> جاري الإرسال...';
    btn.disabled = true;

    var data = {
      company_name: form.querySelector('[name="company_name"]').value,
      phone: form.querySelector('[name="phone"]').value,
      sector: form.querySelector('[name="sector"]').value,
    };

    try {
      var res = await fetch("/api/leads/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      var result = await res.json();

      if (res.ok) {
        successText.textContent = result.message || "تم استلام طلبك بنجاح!";
        successDiv.classList.remove("hidden");
        form.reset();
      } else {
        errorDiv.textContent = result.detail || "حدث خطأ، حاول مرة أخرى.";
        errorDiv.classList.remove("hidden");
      }
    } catch (err) {
      errorDiv.textContent = "حدث خطأ في الاتصال بالسيرفر.";
      errorDiv.classList.remove("hidden");
    }

    btn.innerHTML = originalText;
    btn.disabled = false;
  });
});
