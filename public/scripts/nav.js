// Header interactivity, served as a static file so it satisfies `script-src 'self'`
// (an Astro-inlined component <script> is `unsafe-inline` and the site's CSP blocks it).
// Desktop mega-panels also open on CSS hover/focus-within; this adds click-to-pin,
// close-on-outside/Escape, and the mobile drawer.
(function () {
  var header = document.querySelector("[data-header]");
  var drawerToggle = document.querySelector("[data-drawer-toggle]");
  var groups = Array.prototype.slice.call(document.querySelectorAll("[data-group]"));
  var mq = window.matchMedia("(max-width: 56rem)");

  function setGroup(group, open) {
    group.dataset.open = String(open);
    var t = group.querySelector("[data-trigger]");
    if (t) t.setAttribute("aria-expanded", String(open));
  }
  function closeGroups(except) {
    for (var i = 0; i < groups.length; i++) {
      if (groups[i] !== except) setGroup(groups[i], false);
    }
  }
  function toggleDrawer(open) {
    if (!header) return;
    header.dataset.drawer = open ? "open" : "closed";
    if (drawerToggle) {
      drawerToggle.setAttribute("aria-expanded", String(open));
      drawerToggle.textContent = open ? "Close" : "Menu";
    }
    document.body.style.overflow = open ? "hidden" : "";
  }

  groups.forEach(function (group) {
    var trigger = group.querySelector("[data-trigger]");
    if (!trigger) return;
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      var open = group.dataset.open === "true";
      closeGroups(group);
      setGroup(group, !open);
    });
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest("[data-group]")) closeGroups();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    closeGroups();
    if (header && header.dataset.drawer === "open") toggleDrawer(false);
  });

  if (drawerToggle) {
    drawerToggle.addEventListener("click", function () {
      toggleDrawer(!header || header.dataset.drawer !== "open");
    });
  }

  mq.addEventListener("change", function (e) {
    if (!e.matches) {
      toggleDrawer(false);
      closeGroups();
    }
  });
})();
