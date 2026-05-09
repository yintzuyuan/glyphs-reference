(function () {
  'use strict';

  const root = document.documentElement;
  const STORAGE_LANG = 'gr-lang';
  const STORAGE_THEME = 'gr-theme';

  /* --------- i18n: 雙語切換 --------- */
  function applyLang(lang) {
    const attr = lang === 'zh' ? 'data-zh' : 'data-en';
    document.querySelectorAll('[' + attr + ']').forEach(function (el) {
      const text = el.getAttribute(attr);
      if (text != null) el.textContent = text;
    });
    root.dataset.lang = lang;
    root.lang = lang === 'zh' ? 'zh-Hant' : 'en';

    document.querySelectorAll('[data-lang-set]').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-lang-set') === lang);
    });

    try { localStorage.setItem(STORAGE_LANG, lang); } catch (e) {}
  }

  /* --------- Theme toggle (icon 切換由 CSS 依 dataset.theme 處理) --------- */
  function applyTheme(theme) {
    root.dataset.theme = theme;
    try { localStorage.setItem(STORAGE_THEME, theme); } catch (e) {}
  }

  /* --------- Header scroll shadow --------- */
  function setupHeaderScroll() {
    const header = document.getElementById('site-header');
    if (!header) return;
    const onScroll = function () {
      header.classList.toggle('scrolled', window.scrollY > 4);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* --------- Fade-in 進場動畫 --------- */
  function setupFadeIn() {
    const targets = document.querySelectorAll('.fade-in');
    if (!targets.length) return;

    if (!('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('visible'); });
      return;
    }

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    targets.forEach(function (el) { observer.observe(el); });
  }

  /* --------- 卡片進場（每個 section 內部 stagger） --------- */
  function setupCardStagger() {
    const groups = ['.skills-grid', '.compare-grid', '.steps-grid', '.req-list'];
    groups.forEach(function (selector) {
      const grid = document.querySelector(selector);
      if (!grid) return;
      const items = grid.children;
      if (!('IntersectionObserver' in window)) {
        Array.from(items).forEach(function (it) { it.classList.add('visible'); });
        return;
      }
      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            const idx = Array.prototype.indexOf.call(grid.children, entry.target);
            entry.target.style.transitionDelay = (idx * 60) + 'ms';
            entry.target.classList.add('fade-in', 'visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

      Array.from(items).forEach(function (it) {
        it.classList.add('fade-in');
        observer.observe(it);
      });
    });
  }

  /* --------- 程式碼 copy 按鈕 --------- */
  function setupCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const targetId = btn.getAttribute('data-copy-target');
        const target = targetId && document.getElementById(targetId);
        if (!target) return;
        const text = target.textContent.trim();
        const onSuccess = function () {
          const original = btn.textContent;
          btn.classList.add('copied');
          btn.textContent = root.dataset.lang === 'zh' ? '已複製' : 'Copied';
          setTimeout(function () {
            btn.classList.remove('copied');
            btn.textContent = original;
          }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(onSuccess).catch(fallback);
        } else {
          fallback();
        }
        function fallback() {
          const ta = document.createElement('textarea');
          ta.value = text;
          ta.setAttribute('readonly', '');
          ta.style.position = 'absolute';
          ta.style.left = '-9999px';
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand('copy'); onSuccess(); } catch (e) {}
          document.body.removeChild(ta);
        }
      });
    });
  }

  /* --------- 事件繫結 --------- */
  function setupLangSwitcher() {
    document.querySelectorAll('[data-lang-set]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const lang = btn.getAttribute('data-lang-set');
        applyLang(lang);
      });
    });
  }

  function setupThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }

  /* --------- 初始化 --------- */
  function init() {
    applyLang(root.dataset.lang || 'en');
    applyTheme(root.dataset.theme || 'light');
    setupLangSwitcher();
    setupThemeToggle();
    setupHeaderScroll();
    setupFadeIn();
    setupCardStagger();
    setupCopyButtons();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
