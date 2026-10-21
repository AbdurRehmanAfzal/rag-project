/* AI Engineering Learning Hub — client behaviour (no framework, no build step) */
(function () {
  'use strict';

  var READ_KEY = 'learnhub:read';
  var THEME_KEY = 'learnhub:theme';

  function safeGet(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }
  function safeSet(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode etc. */ }
  }

  /* ---------- Theme ---------- */
  function currentTheme() {
    var stored = safeGet(THEME_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    var btn = document.getElementById('themeToggle');
    if (btn) btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  var themeBtn = document.getElementById('themeToggle');
  if (themeBtn) {
    applyTheme(currentTheme());
    themeBtn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      safeSet(THEME_KEY, next);
      applyTheme(next);
    });
  }

  /* ---------- Reading progress ---------- */
  function readSet() {
    try { return new Set(JSON.parse(safeGet(READ_KEY) || '[]')); } catch (e) { return new Set(); }
  }

  var page = document.body.getAttribute('data-page');
  var topicId = document.body.getAttribute('data-topic-id');

  if (page === 'topic' && topicId) {
    var set = readSet();
    set.add(topicId);
    safeSet(READ_KEY, JSON.stringify(Array.from(set)));
  }

  if (page === 'index') {
    var read = readSet();
    var cards = document.querySelectorAll('.topic-card[data-id]');
    var count = 0;
    cards.forEach(function (card) {
      if (read.has(card.getAttribute('data-id'))) {
        card.classList.add('is-read');
        count++;
      }
    });
    var counter = document.getElementById('readCount');
    if (counter) counter.textContent = String(count);
  }

  /* ---------- Search + category filter (index only) ---------- */
  var searchInput = document.getElementById('searchInput');
  if (searchInput) {
    var chips = document.querySelectorAll('.chip[data-cat]');
    var sections = document.querySelectorAll('.category-section[data-cat]');
    var allCards = document.querySelectorAll('.topic-card[data-search]');
    var emptyState = document.getElementById('emptyState');
    var activeCat = 'all';

    function applyFilter() {
      var q = searchInput.value.trim().toLowerCase();
      var visibleTotal = 0;
      sections.forEach(function (section) {
        var cat = section.getAttribute('data-cat');
        var catMatch = activeCat === 'all' || activeCat === cat;
        var visibleInSection = 0;
        section.querySelectorAll('.topic-card[data-search]').forEach(function (card) {
          var match = catMatch && (!q || card.getAttribute('data-search').indexOf(q) !== -1);
          card.classList.toggle('hidden', !match);
          if (match) visibleInSection++;
        });
        section.classList.toggle('hidden', visibleInSection === 0);
        visibleTotal += visibleInSection;
      });
      if (emptyState) emptyState.classList.toggle('show', visibleTotal === 0);
    }

    searchInput.addEventListener('input', applyFilter);

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        activeCat = chip.getAttribute('data-cat');
        chips.forEach(function (c) { c.classList.toggle('active', c === chip); });
        applyFilter();
      });
    });

    // Support /learn/?s=query deep links (e.g. from the portfolio or social posts)
    var params = new URLSearchParams(window.location.search);
    var preset = params.get('s');
    if (preset) {
      searchInput.value = preset;
      applyFilter();
    }

    // "/" focuses search, like GitHub
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });

    void allCards;
  }

  /* ---------- Copy code ---------- */
  document.querySelectorAll('.copy-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.parentElement.querySelector('pre');
      var text = pre ? pre.textContent : '';
      var done = function () {
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        var ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (e) { /* ignore */ }
        document.body.removeChild(ta);
        done();
      }
    });
  });

  /* ---------- Newsletter signup ---------- */
  document.querySelectorAll('form.subscribe-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = form.querySelector('input[type="email"]');
      var hp = form.querySelector('input[name="website"]');
      var msg = form.querySelector('.form-msg');
      var btn = form.querySelector('button[type="submit"]');
      if (!email || !email.value) return;

      btn.disabled = true;
      msg.className = 'form-msg';
      msg.textContent = 'Subscribing…';

      fetch('/api/learn/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.value.trim(),
          website: hp ? hp.value : '',
          source: form.getAttribute('data-source') || window.location.pathname
        })
      })
        .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
        .then(function (r) {
          if (r.ok && r.data && r.data.ok) {
            msg.className = 'form-msg ok';
            msg.textContent = 'You are in. New topics will land in your inbox.';
            email.value = '';
          } else {
            msg.className = 'form-msg err';
            msg.textContent = (r.data && r.data.detail) || 'Something went wrong. Please try again.';
          }
        })
        .catch(function () {
          msg.className = 'form-msg err';
          msg.textContent = 'Network error. Please try again.';
        })
        .finally(function () { btn.disabled = false; });
    });
  });
})();
