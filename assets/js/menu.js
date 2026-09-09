/* Tequilas menu board: search, filters, surprise me, item sheet.
   Runs against a prebuilt compact index (window.MENU_INDEX). Deferred. */
(function () {
  "use strict";
  var IDX = window.MENU_INDEX || [];
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // ---- search / filter overlay ----
  var q = "", active = {};
  var box = $("#msearch"), chipwrap = $("#mchips"), spread = $("#mspread"), results = $("#mresults");
  function norm(s) { return (s || "").toLowerCase(); }
  function matches(it) {
    if (q) {
      var hay = norm(it.n) + " " + norm(it.c) + " " + norm(it.d || "");
      if (hay.indexOf(q) === -1) return false;
    }
    for (var t in active) {
      if (!active[t]) continue;
      if (t === "Under $10") { if (!(it.p != null && it.p < 10)) return false; }
      else if (t === "Featured") { if (!it.f) return false; }
      else { if ((it.t || "").indexOf(t) === -1) return false; }
    }
    return true;
  }
  function render() {
    var any = q || Object.keys(active).some(function (k) { return active[k]; });
    if (!any) { if (spread) spread.style.display = ""; if (results) results.hidden = true; return; }
    var hits = IDX.filter(matches);
    if (spread) spread.style.display = "none";
    if (!results) return;
    results.hidden = false;
    var rows = hits.map(function (it) {
      var pv = it.v || (it.p != null ? "$" + it.p.toFixed(2) : "");
      return '<a class="rrow" href="' + it.u + '">' +
        '<span class="rn">' + esc(it.n) + '</span>' +
        '<span class="rc">' + esc(it.c) + '</span>' +
        '<span class="rp">' + esc(pv) + '</span></a>';
    }).join("");
    results.innerHTML = '<div class="rhead"><span>' + hits.length + ' item' + (hits.length === 1 ? '' : 's') +
      '</span><button type="button" id="mclear">Clear ✕</button></div>' +
      '<div class="rlist">' + (rows || '<p class="rempty">No items match.</p>') + '</div>';
    var c = $("#mclear"); if (c) c.onclick = clearAll;
  }
  function clearAll() {
    q = ""; active = {}; if (box) box.value = "";
    $$(".mchip").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    render();
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  if (box) box.addEventListener("input", function () { q = norm(box.value.trim()); render(); });
  if (chipwrap) $$(".mchip", chipwrap).forEach(function (b) {
    b.addEventListener("click", function () {
      var t = b.getAttribute("data-t"); active[t] = !(b.getAttribute("aria-pressed") === "true");
      b.setAttribute("aria-pressed", active[t] ? "true" : "false"); render();
    });
  });

  // ---- surprise me ----
  var sm = $("#msurprise");
  if (sm) sm.addEventListener("click", function () {
    if (!IDX.length) return; var it = IDX[Math.floor(Math.random() * IDX.length)];
    window.location.href = it.u;
  });

  // ---- item sheet (progressive enhancement of item rows) ----
  var sheet = $("#msheet"), scrim = $("#mscrim"), lastFocus = null;
  function openSheet(el) {
    if (!sheet) return;
    var v = JSON.parse(el.getAttribute("data-item") || "null"); if (!v) return;
    lastFocus = el;
    var photo = v.img ? '<div class="sh-photo"><img src="' + v.img + '-800.webp" alt="' + esc(v.n) + '" width="800" height="600" loading="lazy"></div>' : "";
    var variants = (v.vars || []).map(function (x) {
      return '<div class="sh-var"><span>' + esc(x.label) + '</span><span>' + esc(x.price) + '</span></div>';
    }).join("");
    var tags = (v.tags || []).map(function (t) { return '<span class="mtag">' + esc(t) + '</span>'; }).join("");
    sheet.innerHTML = photo +
      '<div class="sh-body"><div class="sh-ey">' + esc(v.c) + '</div>' +
      '<h2 class="sh-name disp">' + esc(v.n) + '</h2>' +
      '<div class="sh-vars">' + variants + '</div>' +
      (v.d ? '<p class="sh-desc">' + esc(v.d) + '</p>' : '') +
      (tags ? '<div class="sh-tags">' + tags + '</div>' : '') +
      '<a class="btn-red" href="' + v.order + '" target="_blank" rel="noopener">Add to online order</a>' +
      '<button type="button" class="sh-close" id="mshclose" aria-label="Close">Close ✕</button></div>';
    scrim.hidden = false; sheet.hidden = false; document.body.style.overflow = "hidden";
    var cl = $("#mshclose"); if (cl) { cl.focus(); cl.onclick = closeSheet; }
  }
  function closeSheet() {
    if (!sheet) return; sheet.hidden = true; scrim.hidden = true; document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  if (scrim) scrim.addEventListener("click", closeSheet);
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && sheet && !sheet.hidden) closeSheet(); });
  $$(".mrow[data-item]").forEach(function (el) {
    el.addEventListener("click", function (ev) { ev.preventDefault(); openSheet(el); });
  });
  // deep link: /menu/<cat>/#<itemslug> opens that item's sheet
  if (location.hash) {
    var target = document.getElementById(location.hash.slice(1));
    if (target && target.classList.contains("mrow")) setTimeout(function () { openSheet(target); }, 60);
  }
})();
