// Shared behaviour for the "start by role" pages: EN/RU switch + click-to-copy.
// Each page defines `window.I18N = { en:{...}, ru:{...} }` before loading this.
(function () {
  var I18N = window.I18N || {};

  function setLang(lang) {
    if (!I18N[lang]) lang = 'en';
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = I18N[lang][el.getAttribute('data-i18n')];
      if (v != null) el.innerHTML = v;
    });
    document.querySelectorAll('#langtog button').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-lang') === lang);
    });
    try { localStorage.setItem('dm_lang', lang); } catch (e) {}
  }
  document.querySelectorAll('#langtog button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
  });
  if (Object.keys(I18N).length) {
    var saved = 'en';
    try { saved = localStorage.getItem('dm_lang') || 'en'; } catch (e) {}
    setLang(saved);
  }

  // Click-to-copy: only command lines (with a prompt), prompt + comments stripped.
  function cmdText(pre) {
    return pre.innerHTML.split('\n').filter(function (line) {
      return line.indexOf('class="p"') !== -1;
    }).map(function (line) {
      var d = document.createElement('div');
      d.innerHTML = line;
      d.querySelectorAll('.p,.c').forEach(function (n) { n.remove(); });
      return d.textContent.replace(/^\s+|\s+$/g, '');
    }).filter(Boolean).join('\n');
  }
  document.querySelectorAll('main pre').forEach(function (pre) {
    var text = cmdText(pre);
    if (!text) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'copybtn'; b.textContent = 'copy';
    b.setAttribute('aria-label', 'Copy command');
    b.addEventListener('click', function () {
      function done() { b.textContent = 'copied'; b.classList.add('done'); setTimeout(function () { b.textContent = 'copy'; b.classList.remove('done'); }, 1200); }
      function fallback() { var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.top = '-999px'; document.body.appendChild(ta); ta.focus(); ta.select(); try { document.execCommand('copy'); } catch (e) {} document.body.removeChild(ta); done(); }
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(done, fallback); }
      else fallback();
    });
    pre.appendChild(b);
  });
})();
