document.addEventListener("DOMContentLoaded", function () {
  // ---- intro splash (real-plant growth animation, runs once per browser tab) ----
  var splash = document.getElementById("intro-splash");
  if (splash) {
    var seen = sessionStorage.getItem("verdant_intro_seen");
    if (seen) {
      splash.classList.add("hide");
    } else {
      sessionStorage.setItem("verdant_intro_seen", "1");
      setTimeout(function () {
        splash.classList.add("hide");
      }, 2600);
    }
    splash.addEventListener("click", function () {
      splash.classList.add("hide");
    });
  }

  // ---- mobile nav toggle ----
  var toggle = document.querySelector(".mobile-nav-toggle");
  var mobileNav = document.querySelector(".mobile-nav");
  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      mobileNav.classList.toggle("open");
    });
  }

  // ---- FAQ accordion ----
  document.querySelectorAll(".faq-question").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".faq-item");
      var wasOpen = item.classList.contains("open");
      document.querySelectorAll(".faq-item.open").forEach(function (i) {
        i.classList.remove("open");
      });
      if (!wasOpen) item.classList.add("open");
    });
  });

  // ---- deals countdown (pure JS, resets nightly, no backend dependency) ----
  var countdownEl = document.getElementById("deal-countdown");
  if (countdownEl) {
    function nextMidnight() {
      var d = new Date();
      d.setHours(24, 0, 0, 0);
      return d;
    }
    var target = nextMidnight();
    function tick() {
      var diff = Math.max(0, target - new Date());
      var h = Math.floor(diff / 3600000);
      var m = Math.floor((diff % 3600000) / 60000);
      var s = Math.floor((diff % 60000) / 1000);
      var pad = function (n) {
        return String(n).padStart(2, "0");
      };
      countdownEl.querySelector("[data-h]").textContent = pad(h);
      countdownEl.querySelector("[data-m]").textContent = pad(m);
      countdownEl.querySelector("[data-s]").textContent = pad(s);
      if (diff <= 0) target = nextMidnight();
    }
    tick();
    setInterval(tick, 1000);
  }

  // ---- password visibility toggle (login/register/password-reset forms) ----
  document.querySelectorAll(".password-toggle-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var targetId = btn.getAttribute("data-target");
      var input = document.getElementById(targetId);
      if (!input) return;
      var showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.classList.toggle("showing", !showing);
      btn.setAttribute(
        "aria-label",
        showing ? "Show password" : "Hide password",
      );
    });
  });

  // ---- quick add-to-cart (AJAX, updates header badge without reload) ----
  document.querySelectorAll(".quick-add-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var formData = new FormData(form);
      fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: formData,
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, data: data };
          });
        })
        .then(function (result) {
          var badge = document.getElementById("cart-count-badge");
          if (result.ok && result.data.ok) {
            if (badge) badge.textContent = result.data.cart_item_count;
            var btn = form.querySelector("button");
            var original = btn.textContent;
            btn.textContent = "Added ✓";
            setTimeout(function () {
              btn.textContent = original;
            }, 1400);
          } else {
            window.location.reload();
          }
        })
        .catch(function () {
          form.submit();
        });
    });
  });
});
