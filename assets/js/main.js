/* ==========================================================================
   Liberty Collective — Complete Site-Wide JavaScript
   Nav, carousels, modals, forms, map, video controls, widgets
   ========================================================================== */
(function () {
  'use strict';

  /* -----------------------------------------------------------------------
     CONFIG — Endpoints and timing
     ----------------------------------------------------------------------- */
  var CONFIG = {
    formEndpoint: '/api/contact',       /* POST target for all forms */
    newsletterEndpoint: '/api/newsletter',
    birthdayEndpoint: '/api/birthday',
    newsletterDelay: 15000,             /* ms before newsletter popup */
    newsletterScrollThreshold: 0.5,     /* 50% scroll triggers popup */
    galleryInterval: 2000,
    reviewInterval: 6000,
    mobileBarDelay: 4000,
    mapCenter: [39.381306, -84.373826],
    mapZoom: 14,
    accentColor: '#ff0003'
  };
  /* Per-client overrides injected by generate.js */
  if (window.SITE_CONFIG) { for (var k in window.SITE_CONFIG) CONFIG[k] = window.SITE_CONFIG[k]; }

  /* -----------------------------------------------------------------------
     UTILITY HELPERS
     ----------------------------------------------------------------------- */
  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return (ctx || document).querySelectorAll(sel); }
  function on(el, evt, fn, opts) { if (el) el.addEventListener(evt, fn, opts || false); }
  function addClass(el, cls) { if (el) el.classList.add(cls); }
  function removeClass(el, cls) { if (el) el.classList.remove(cls); }
  function toggleClass(el, cls) { if (el) return el.classList.toggle(cls); }
  function hasClass(el, cls) { return el && el.classList.contains(cls); }

  /* -----------------------------------------------------------------------
     HEADER SCROLL — Add shadow on scroll
     ----------------------------------------------------------------------- */
  var header = document.getElementById('site-header');
  window.addEventListener('scroll', function () {
    if (header) header.classList.toggle('scrolled', window.scrollY > 50);
  }, { passive: true });

  /* -----------------------------------------------------------------------
     SCROLL REVEAL — feature bands swoop in when they enter the viewport
     ----------------------------------------------------------------------- */
  (function () {
    var els = document.querySelectorAll('.feature-band');
    if (!els.length || !('IntersectionObserver' in window)) return;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in-view'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.18 });
    els.forEach(function (el) { obs.observe(el); });
  })();

  /* -----------------------------------------------------------------------
     MOBILE NAV — Hamburger toggle + full-screen overlay
     ----------------------------------------------------------------------- */
  var toggle = document.getElementById('nav-toggle');
  var mobileMenu = document.getElementById('mobile-menu');

  function closeMobileMenu() {
    if (toggle && mobileMenu) {
      removeClass(toggle, 'active');
      removeClass(mobileMenu, 'active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  }

  if (toggle && mobileMenu) {
    on(toggle, 'click', function () {
      var open = toggleClass(toggle, 'active');
      toggleClass(mobileMenu, 'active');
      toggle.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
    });

    /* Close menu when clicking any non-dropdown link */
    qsa('a:not(.mobile-dropdown-toggle)', mobileMenu).forEach(function (a) {
      on(a, 'click', closeMobileMenu);
    });
  }

  /* Mobile dropdown sub-menu toggles */
  qsa('.mobile-dropdown-toggle').forEach(function (btn) {
    on(btn, 'click', function (e) {
      e.preventDefault();
      var sub = btn.nextElementSibling;
      if (sub) toggleClass(sub, 'active');
      toggleClass(btn, 'active');
    });
  });

  /* -----------------------------------------------------------------------
     HERO VIDEO CONTROLS — Play/pause + mute/unmute
     ----------------------------------------------------------------------- */
  var video = qs('.hero-video');
  var playBtn = qs('.video-controls-btn');
  var muteBtn = qs('.video-volume-btn');

  if (video && playBtn) {
    on(playBtn, 'click', function () {
      var icoPause = qs('.ico-pause', playBtn);
      var icoPlay = qs('.ico-play', playBtn);
      if (video.paused) {
        video.play();
        if (icoPause) icoPause.style.display = '';
        if (icoPlay) icoPlay.style.display = 'none';
      } else {
        video.pause();
        if (icoPause) icoPause.style.display = 'none';
        if (icoPlay) icoPlay.style.display = '';
      }
    });
  }

  if (video && muteBtn) {
    on(muteBtn, 'click', function () {
      video.muted = !video.muted;
      var icoMuted = qs('.ico-muted', muteBtn);
      var icoUnmuted = qs('.ico-unmuted', muteBtn);
      if (icoMuted) icoMuted.style.display = video.muted ? '' : 'none';
      if (icoUnmuted) icoUnmuted.style.display = video.muted ? 'none' : '';
    });
  }

  /* -----------------------------------------------------------------------
     GALLERY CAROUSEL — Auto-play with prev/next and pause
     ----------------------------------------------------------------------- */
  var galleryTrack = document.getElementById('gallery-track');
  var galleryPrev = document.getElementById('gallery-prev');
  var galleryNext = document.getElementById('gallery-next');
  var galleryPauseBtn = document.getElementById('gallery-pause');
  var galleryPaused = false;
  var galleryIndex = 0;
  var galleryTimer = null;

  function getVisibleCount() {
    if (window.innerWidth <= 768) return 1;
    if (window.innerWidth <= 1024) return 2;
    return 3;
  }

  function moveGallery() {
    if (!galleryTrack) return;
    var slides = galleryTrack.children;
    if (!slides.length) return;
    var visible = getVisibleCount();
    var max = Math.max(0, slides.length - visible);
    if (galleryIndex > max) galleryIndex = 0;
    if (galleryIndex < 0) galleryIndex = max;
    var slideW = slides[0].offsetWidth;
    var gap = 20;
    galleryTrack.style.transform = 'translateX(-' + (galleryIndex * (slideW + gap)) + 'px)';
  }

  if (galleryPrev) on(galleryPrev, 'click', function () { galleryIndex--; moveGallery(); });
  if (galleryNext) on(galleryNext, 'click', function () { galleryIndex++; moveGallery(); });
  if (galleryPauseBtn) {
    on(galleryPauseBtn, 'click', function () {
      galleryPaused = !galleryPaused;
      var ico = qs('.fa', galleryPauseBtn);
      if (ico) {
        ico.className = galleryPaused ? 'fa fa-play' : 'fa fa-pause';
      }
    });
  }

  galleryTimer = setInterval(function () {
    if (!galleryPaused && galleryTrack) {
      galleryIndex++;
      moveGallery();
    }
  }, CONFIG.galleryInterval);

  /* -----------------------------------------------------------------------
     REVIEWS CAROUSEL — Auto-rotate with dots, arrows, pause
     ----------------------------------------------------------------------- */
  var reviewSlides = qsa('.review-slide');
  var reviewDots = qsa('.dot');
  var reviewPrevBtn = document.getElementById('review-prev');
  var reviewNextBtn = document.getElementById('review-next');
  var reviewPauseBtn = document.getElementById('review-pause');
  var reviewIndex = 0;
  var reviewsPaused = false;

  function showReview(idx) {
    if (!reviewSlides.length) return;
    idx = ((idx % reviewSlides.length) + reviewSlides.length) % reviewSlides.length;
    reviewSlides.forEach(function (s, i) {
      s.classList.toggle('active', i === idx);
    });
    reviewDots.forEach(function (d, i) {
      d.classList.toggle('active', i === idx);
    });
    reviewIndex = idx;
  }

  if (reviewPrevBtn) on(reviewPrevBtn, 'click', function () {
    showReview(reviewIndex - 1);
  });
  if (reviewNextBtn) on(reviewNextBtn, 'click', function () {
    showReview(reviewIndex + 1);
  });
  reviewDots.forEach(function (dot) {
    on(dot, 'click', function () {
      showReview(parseInt(dot.dataset.index, 10));
    });
  });
  if (reviewPauseBtn) on(reviewPauseBtn, 'click', function () {
    reviewsPaused = !reviewsPaused;
    var ico = qs('.fa', reviewPauseBtn);
    if (ico) {
      ico.className = reviewsPaused ? 'fa fa-play' : 'fa fa-pause';
    }
  });

  setInterval(function () {
    if (!reviewsPaused && reviewSlides.length > 0) {
      showReview(reviewIndex + 1);
    }
  }, CONFIG.reviewInterval);

  /* -----------------------------------------------------------------------
     MODAL SYSTEM — Open, close, escape, overlay click
     ----------------------------------------------------------------------- */
  function openModal(modalId) {
    var overlay = document.getElementById(modalId);
    if (!overlay) return;
    overlay.style.display = 'flex';
    /* Force reflow for transition */
    overlay.offsetHeight;
    addClass(overlay, 'active');
    document.body.style.overflow = 'hidden';
  }

  function closeModal(modalId) {
    var overlay = document.getElementById(modalId);
    if (!overlay) return;
    removeClass(overlay, 'active');
    document.body.style.overflow = '';
    /* Wait for fade-out then hide */
    setTimeout(function () {
      if (!hasClass(overlay, 'active')) {
        overlay.style.display = 'none';
      }
    }, 300);
  }

  function closeAllModals() {
    qsa('.modal-overlay').forEach(function (overlay) {
      removeClass(overlay, 'active');
      document.body.style.overflow = '';
      setTimeout(function () {
        if (!hasClass(overlay, 'active')) {
          overlay.style.display = 'none';
        }
      }, 300);
    });
  }

  /* Close buttons inside modals */
  qsa('.modal-close').forEach(function (btn) {
    on(btn, 'click', function () {
      var overlay = btn.closest('.modal-overlay');
      if (overlay) closeModal(overlay.id);
    });
  });

  /* Close on overlay background click */
  qsa('.modal-overlay').forEach(function (overlay) {
    on(overlay, 'click', function (e) {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });

  /* Close on Escape key */
  on(document, 'keydown', function (e) {
    if (e.key === 'Escape') closeAllModals();
  });

  /* Expose open/close globally for inline onclick handlers */
  window.openModal = openModal;
  window.closeModal = closeModal;

  /* -----------------------------------------------------------------------
     CONTACT MODAL — Radio selector switches between 3 form panels
     ----------------------------------------------------------------------- */
  var contactRadios = qsa('#contact-type-group input[type="radio"]');
  var contactPanels = qsa('.contact-form-panel');

  function switchContactPanel(type) {
    contactPanels.forEach(function (panel) {
      panel.classList.toggle('active', panel.dataset.type === type);
    });
  }

  contactRadios.forEach(function (input) {
    on(input, 'change', function () {
      switchContactPanel(input.value);
    });
  });

  /* Handle data-modal links that also set contact type (e.g. Jobs link) */
  qsa('[data-modal="contact-modal"][data-contact-type]').forEach(function (el) {
    on(el, 'click', function (e) {
      e.preventDefault();
      var type = el.dataset.contactType;
      contactRadios.forEach(function (r) { r.checked = r.value === type; });
      switchContactPanel(type);
      openModal('contact-modal');
    });
  });

  /* -----------------------------------------------------------------------
     CONTACT FAB BUTTON — Opens contact modal
     ----------------------------------------------------------------------- */
  var fabContact = qs('.fab-contact');
  if (fabContact) {
    on(fabContact, 'click', function () {
      openModal('contact-modal');
    });
  }

  /* -----------------------------------------------------------------------
     BIRTHDAY WIDGET — Opens birthday modal
     ----------------------------------------------------------------------- */
  var bdayPill = qs('.bday-pill');
  if (bdayPill) {
    on(bdayPill, 'click', function (e) {
      e.preventDefault();
      openModal('bday-modal');
    });
  }

  /* -----------------------------------------------------------------------
     NEWSLETTER POPUP — Triggered after delay or scroll threshold
     ----------------------------------------------------------------------- */
  var newsletterShown = false;
  var nlModalId = 'newsletter-modal';

  function maybeShowNewsletter() {
    if (newsletterShown) return;
    if (!document.getElementById(nlModalId)) return;
    /* Don't show if another modal is already open */
    var anyOpen = qs('.modal-overlay.active');
    if (anyOpen) return;
    /* Respect if user has dismissed it this session */
    try {
      if (sessionStorage.getItem('nl_dismissed')) return;
    } catch (e) { /* storage unavailable */ }
    newsletterShown = true;
    openModal(nlModalId);
  }

  /* Timer-based trigger */
  setTimeout(maybeShowNewsletter, CONFIG.newsletterDelay);

  /* Scroll-based trigger */
  window.addEventListener('scroll', function () {
    if (newsletterShown) return;
    var scrollPercent = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
    if (scrollPercent >= CONFIG.newsletterScrollThreshold) {
      maybeShowNewsletter();
    }
  }, { passive: true });

  /* Mark as dismissed when closed */
  var nlCloseBtn = qs('#newsletter-modal .modal-close');
  if (nlCloseBtn) {
    on(nlCloseBtn, 'click', function () {
      try { sessionStorage.setItem('nl_dismissed', '1'); } catch (e) {}
    });
  }

  /* -----------------------------------------------------------------------
     FORM SUBMISSION HANDLER — POST to configurable endpoint
     ----------------------------------------------------------------------- */
  /* Posts contact / catering / parties / jobs forms to the shared chowdown-forms
     Worker (multipart so a resume can ride along). The Worker resolves the
     destination server-side from the client id, so nothing sensitive is in the page. */
  function handleFormSubmit(form) {
    var submitBtn = qs('button[type="submit"], .btn[type="submit"]', form);
    var successEl = qs('.form-success', form.parentNode) || qs('.form-success', form);
    var errorEl = qs('.form-error', form.parentNode) || qs('.form-error', form);
    var fcfg = CONFIG.forms || {};

    if (!fcfg.endpoint || !fcfg.client) {
      if (successEl) { addClass(successEl, 'visible'); successEl.textContent = 'Online submissions are coming soon. Please call us and we\'ll take care of you.'; }
      return;
    }

    if (submitBtn) addClass(submitBtn, 'loading');
    if (successEl) removeClass(successEl, 'visible');
    if (errorEl) removeClass(errorEl, 'visible');

    var fd = new FormData(form);                 // multipart -> carries the resume file
    fd.append('client', fcfg.client);
    if (!fd.get('type')) fd.append('type', form.getAttribute('data-form-type') || 'contact');

    fetch(fcfg.endpoint, { method: 'POST', body: fd })   // no Content-Type: browser sets the multipart boundary
      .then(function (r) { return r.json().catch(function () { throw new Error('status ' + r.status); }); })
      .then(function (res) {
        if (submitBtn) removeClass(submitBtn, 'loading');
        if (!res || res.ok === false) throw new Error((res && res.error) || 'error');
        if (successEl) { addClass(successEl, 'visible'); successEl.textContent = 'Thank you! We\'ll be in touch soon.'; }
        form.reset();
      })
      .catch(function (err) {
        if (submitBtn) removeClass(submitBtn, 'loading');
        if (errorEl) { addClass(errorEl, 'visible'); errorEl.textContent = 'Something went wrong. Please try again or call us directly.'; }
        console.error('Form submission error:', err);
      });
  }

  /* Contact / catering / parties / jobs forms -> shared forms Worker. Newsletter
     stays visual-only (its own onsubmit=return false) until Forms->GHL ships. */
  /* VIP loyalty signup -> ChowdownOS -> Boomerangme. Issues the wallet pass on
     OUR site (no external bounce); on success the form is swapped for the
     Apple/Google Wallet install buttons. */
  function handleVipSubmit(form) {
    var submitBtn = qs('button[type="submit"], .btn[type="submit"]', form);
    var errorEl = qs('.form-error', form);
    var vcfg = CONFIG.vip || {};
    var result = qs('.vip-result', form.parentNode);
    var btns = result ? qs('.vip-wallet-btns', result) : null;
    var hp = form.querySelector('input[name="_gotcha"]');
    if (hp && hp.value) return;                                  // honeypot
    if (!vcfg.endpoint || !vcfg.client) {
      if (errorEl) { addClass(errorEl, 'visible'); errorEl.textContent = 'VIP signup isn\'t set up yet — please check back soon.'; }
      return;
    }
    if (submitBtn) addClass(submitBtn, 'loading');
    if (errorEl) removeClass(errorEl, 'visible');
    var payload = { client: vcfg.client };
    ['firstName', 'lastName', 'phone', 'email', 'dateOfBirth'].forEach(function (k) {
      var el = form.querySelector('[name="' + k + '"]'); payload[k] = el ? el.value : '';
    });
    fetch(vcfg.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { return r.json().catch(function () { throw new Error('status ' + r.status); }); })
      .then(function (res) {
        if (submitBtn) removeClass(submitBtn, 'loading');
        if (!res || res.ok === false || !res.install) throw new Error((res && res.error) || 'error');
        if (btns) {
          var ins = res.install, html = '';
          if (ins.apple) html += '<a class="btn vip-wallet" href="' + ins.apple + '">Add to Apple Wallet</a>';
          if (ins.google) html += '<a class="btn vip-wallet" href="' + ins.google + '">Add to Google Wallet</a>';
          if (!ins.apple && !ins.google && ins.universal) html += '<a class="btn vip-wallet" href="' + ins.universal + '">Add to your phone</a>';
          btns.innerHTML = html;
        }
        if (result) { form.style.display = 'none'; result.hidden = false; }
      })
      .catch(function (err) {
        if (submitBtn) removeClass(submitBtn, 'loading');
        if (errorEl) {
          addClass(errorEl, 'visible');
          errorEl.textContent = (err && ('' + err.message).indexOf('member') > -1)
            ? "Looks like you're already a member!" : 'Something went wrong. Please try again.';
        }
        console.error('VIP signup error:', err);
      });
  }

  qsa('.lead-form, .contact-form-panel, .careers-form').forEach(function (form) {
    on(form, 'submit', function (e) {
      e.preventDefault();
      if (hasClass(form, 'vip-form')) handleVipSubmit(form);
      else handleFormSubmit(form);
    });
  });

  /* -----------------------------------------------------------------------
     MOBILE FOOTER BAR — Show after delay
     ----------------------------------------------------------------------- */
  var mobileFooterBar = qs('.mobile-footer-bar');
  if (mobileFooterBar) {
    setTimeout(function () {
      addClass(mobileFooterBar, 'show-bottom-nav');
    }, CONFIG.mobileBarDelay);
  }

  /* -----------------------------------------------------------------------
     LEAFLET MAP
     ----------------------------------------------------------------------- */
  function initMap() {
    if (typeof L === 'undefined' || !document.getElementById('map')) return;
    var map = L.map('map', {
      scrollWheelZoom: false,
      dragging: !L.Browser.mobile,
      tap: !L.Browser.mobile
    }).setView(CONFIG.mapCenter, CONFIG.mapZoom);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    L.marker(CONFIG.mapCenter).addTo(map)
      .bindPopup('<strong>Liberty Collective</strong><br>6735 Lakota Lane<br>Liberty Township, OH 45044');
  }

  if (document.readyState === 'complete') {
    initMap();
  } else {
    window.addEventListener('load', initMap);
  }

  /* -----------------------------------------------------------------------
     SMOOTH SCROLL — Anchor links with offset for fixed header
     ----------------------------------------------------------------------- */
  qsa('a[href^="#"]').forEach(function (anchor) {
    on(anchor, 'click', function (e) {
      var targetId = anchor.getAttribute('href');
      if (!targetId || targetId === '#') return;
      var target = qs(targetId);
      if (!target) return;
      e.preventDefault();
      var headerHeight = header ? header.offsetHeight : 0;
      var targetPos = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
      window.scrollTo({ top: targetPos, behavior: 'smooth' });

      /* Close mobile menu if open */
      closeMobileMenu();

      /* Update URL without jump */
      if (history.pushState) {
        history.pushState(null, null, targetId);
      }
    });
  });

  /* -----------------------------------------------------------------------
     MENU TABS — switch food/drink menu panels
     ----------------------------------------------------------------------- */
  qsa('[data-menu-tab]').forEach(function (tab) {
    on(tab, 'click', function () {
      var idx = tab.getAttribute('data-menu-tab');
      qsa('[data-menu-tab]').forEach(function (t) { t.classList.toggle('active', t === tab); });
      qsa('[data-menu-panel]').forEach(function (p) { p.classList.toggle('active', p.getAttribute('data-menu-panel') === idx); });
    });
  });

  /* -----------------------------------------------------------------------
     MENU SECTION FILTER — each chip reveals only its section (no page jumping)
     ----------------------------------------------------------------------- */
  qsa('.menu-chip').forEach(function (chip) {
    on(chip, 'click', function () {
      var catId = chip.getAttribute('data-cat');
      var panel = chip.closest('.menu-panel');
      if (!panel) return;
      qsa('.menu-chip', panel).forEach(function (c) { c.classList.toggle('active', c === chip); });
      if (catId === 'all') {
        // Full menu, text only.
        panel.classList.add('all-mode');
        qsa('.menu-category', panel).forEach(function (sec) { sec.classList.remove('is-hidden'); });
      } else {
        // Single section, with its photos.
        panel.classList.remove('all-mode');
        qsa('.menu-category', panel).forEach(function (sec) {
          sec.classList.toggle('is-hidden', sec.id !== catId);
        });
      }
      // keep the active chip centered in the scrollable filter bar
      var track = chip.parentElement;
      track.scrollLeft = chip.offsetLeft - track.clientWidth / 2 + chip.clientWidth / 2;
    });
  });

  /* -----------------------------------------------------------------------
     EVENTS FEED — live calendar layer (opt-in via SITE_CONFIG.eventsFeed).
     Fetches upcoming events from the client's Google Calendar at load, so the
     page is always current and past events drop off automatically. Talks
     straight to Google (no server dependency); fails quietly to an empty state.
     ----------------------------------------------------------------------- */
  (function () {
    var mount = document.getElementById('events-feed');
    if (!mount) return;
    var cfg = (window.SITE_CONFIG && window.SITE_CONFIG.eventsFeed) || {};
    function esc(s) { var d = document.createElement('div'); d.textContent = (s == null ? '' : String(s)); return d.innerHTML; }
    function empty(msg) {
      mount.innerHTML = '<div class="events-empty"><h2>No Upcoming Events</h2><p>' + esc(msg || 'Check back soon!') + '</p></div>';
    }
    if (!cfg.calendarId || !cfg.apiKey) {
      if (cfg.calendarId && !cfg.apiKey) console.warn('[events] calendarId set but no apiKey — live feed disabled');
      empty(); return;
    }
    // Render in the restaurant's timezone (cfg.timezone), not the visitor's, so an
    // out-of-town diner sees the local event time. All-day events stay floating.
    var TZ = cfg.timezone || undefined;
    function iso(p) { return p.dateTime || (p.date ? p.date + 'T00:00:00' : null); }
    function fmtDate(p) {
      var tz = p.date ? undefined : TZ, d = new Date(iso(p));
      var day = parseInt(d.toLocaleDateString('en-US', { day: 'numeric', timeZone: tz }), 10);
      var suf = (day % 10 === 1 && day !== 11) ? 'st' : (day % 10 === 2 && day !== 12) ? 'nd' : (day % 10 === 3 && day !== 13) ? 'rd' : 'th';
      return d.toLocaleDateString('en-US', { weekday: 'long', timeZone: tz }) + '<br>' +
             d.toLocaleDateString('en-US', { month: 'long', timeZone: tz }) + ' ' + day + suf;
    }
    function fmtTime(ev) {
      if (ev.start.date) return 'All day';
      var o = { hour: 'numeric', minute: '2-digit', timeZone: TZ };
      var s = new Date(ev.start.dateTime).toLocaleTimeString('en-US', o);
      var e = (ev.end && ev.end.dateTime) ? new Date(ev.end.dateTime).toLocaleTimeString('en-US', o) : '';
      return e ? (s + ' - ' + e) : s;
    }
    function calStamp(p) {
      if (p.date) return p.date.replace(/-/g, '');
      return new Date(p.dateTime).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
    }
    function gcalUrl(ev) {
      return 'https://calendar.google.com/calendar/render?action=TEMPLATE' +
        '&text=' + encodeURIComponent(ev.summary || '') +
        '&dates=' + calStamp(ev.start) + '/' + calStamp(ev.end || ev.start) +
        '&details=' + encodeURIComponent(ev.description || '') +
        '&location=' + encodeURIComponent(ev.location || '');
    }
    var url = 'https://www.googleapis.com/calendar/v3/calendars/' + encodeURIComponent(cfg.calendarId) +
      '/events?key=' + encodeURIComponent(cfg.apiKey) +
      '&singleEvents=true&orderBy=startTime&maxResults=20&timeMin=' + encodeURIComponent(new Date().toISOString());
    fetch(url).then(function (r) { return r.ok ? r.json() : Promise.reject(); }).then(function (data) {
      var items = (data.items || []).filter(function (e) { return e.start && (e.start.dateTime || e.start.date); });
      if (!items.length) { empty(); return; }
      mount.innerHTML = items.map(function (ev) {
        var time = fmtTime(ev);
        return '<div class="event-card"><div class="event-date">' + fmtDate(ev.start) + '</div>' +
          '<div class="event-body"><h2>' + esc(ev.summary || 'Event') + '</h2>' +
          (time ? '<p class="event-time">' + esc(time) + '</p>' : '') +
          (ev.description ? '<p>' + esc(ev.description) + '</p>' : '') +
          '<a class="evt-add" href="' + gcalUrl(ev) + '" target="_blank" rel="noopener">+ Add to calendar</a>' +
          '</div></div>';
      }).join('');
    }).catch(function () { empty(); });
  })();

  /* -----------------------------------------------------------------------
     BREADCRUMB INTERACTIONS — Active state on current page
     ----------------------------------------------------------------------- */
  var breadcrumbLinks = qsa('.breadcrumbs a');
  var currentPath = window.location.pathname.replace(/\/$/, '');
  breadcrumbLinks.forEach(function (link) {
    var linkPath = link.getAttribute('href');
    if (linkPath) {
      linkPath = linkPath.replace(/\/$/, '');
      if (linkPath === currentPath) {
        addClass(link, 'current');
      }
    }
  });

  /* -----------------------------------------------------------------------
     NAV ACTIVE STATE — Highlight current page in navigation
     ----------------------------------------------------------------------- */
  function setActiveNav() {
    var path = window.location.pathname;
    /* Desktop nav */
    qsa('.nav-left a, .nav-right > li > a, .dropdown li a').forEach(function (link) {
      var href = link.getAttribute('href');
      if (!href) return;
      var linkPath = href.replace(/\/$/, '');
      var pagePath = path.replace(/\/$/, '');
      if (linkPath && pagePath && (pagePath === linkPath || pagePath.indexOf(linkPath + '/') === 0) && linkPath !== '') {
        addClass(link, 'active');
      }
    });
    /* Mobile nav */
    qsa('.mobile-menu a').forEach(function (link) {
      var href = link.getAttribute('href');
      if (!href) return;
      var linkPath = href.replace(/\/$/, '');
      var pagePath = path.replace(/\/$/, '');
      if (linkPath && pagePath && pagePath === linkPath && linkPath !== '') {
        link.style.color = CONFIG.accentColor;
      }
    });
  }
  setActiveNav();

})();
