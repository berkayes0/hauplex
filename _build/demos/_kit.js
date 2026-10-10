function demoKit(root) {
  var host = root.querySelector('.d');
  var toasts = document.createElement('div');
  toasts.className = 'k-toasts';
  toasts.setAttribute('role', 'status');
  host.appendChild(toasts);

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function toast(msg, type) {
    var t = document.createElement('div');
    t.className = 'k-toast ' + (type || 'ok');
    t.textContent = msg;
    toasts.appendChild(t);
    setTimeout(function () { t.remove(); }, 3200);
  }

  // modal({ title, body: html, actions: [{ label, primary, onClick(close, el) }], form: { fields: [...], submit, onSubmit(data, close) } })
  function modal(o) {
    var back = document.createElement('div');
    back.className = 'k-back';
    var fields = '';
    if (o.form) {
      fields = o.form.fields.map(function (f, i) {
        var id = 'kf-' + Date.now() + '-' + i;
        var ctl;
        if (f.type === 'select') ctl = '<select id="' + id + '" name="' + f.name + '">' + f.options.map(function (op) { return '<option>' + esc(op) + '</option>'; }).join('') + '</select>';
        else if (f.type === 'textarea') ctl = '<textarea id="' + id + '" name="' + f.name + '"' + (f.required ? ' required' : '') + ' placeholder="' + esc(f.placeholder || '') + '"></textarea>';
        else ctl = '<input id="' + id + '" name="' + f.name + '" type="' + (f.type || 'text') + '"' + (f.required ? ' required' : '') + ' placeholder="' + esc(f.placeholder || '') + '" value="' + esc(f.value || '') + '">';
        return '<div class="k-field"><label for="' + id + '">' + esc(f.label) + '</label>' + ctl + '</div>';
      }).join('') + '<div class="k-err" hidden></div>';
    }
    var acts = (o.actions || []).map(function (a, i) { return '<button type="button" class="k-btn' + (a.primary ? ' p' : '') + '" data-k="' + i + '">' + esc(a.label) + '</button>'; }).join('');
    if (o.form) acts = '<button type="button" class="k-btn" data-k="cancel">Vazgeç</button><button type="submit" class="k-btn p">' + esc(o.form.submit || 'Gönder') + '</button>';
    var inner = '<div class="k-mh"><h3>' + esc(o.title) + '</h3><button type="button" class="k-x" aria-label="Kapat">×</button></div>' +
      '<div class="k-mb">' + (o.body || '') + fields + '</div>' + (acts ? '<div class="k-mf">' + acts + '</div>' : '');
    back.innerHTML = o.form ? '<form class="k-modal" role="dialog" aria-modal="true" novalidate>' + inner + '</form>' : '<div class="k-modal" role="dialog" aria-modal="true">' + inner + '</div>';
    host.appendChild(back);
    var box = back.firstChild;
    function close() { back.remove(); document.removeEventListener('keydown', onKey); }
    function onKey(e) { if (e.key === 'Escape') close(); }
    document.addEventListener('keydown', onKey);
    back.addEventListener('click', function (e) {
      if (e.target === back || e.target.closest('.k-x') || e.target.closest('[data-k="cancel"]')) { close(); return; }
      var b = e.target.closest('[data-k]');
      if (b && o.actions) { var a = o.actions[+b.getAttribute('data-k')]; if (a.onClick) a.onClick(close, box); else close(); }
    });
    if (o.form) {
      box.addEventListener('submit', function (e) {
        e.preventDefault();
        var err = box.querySelector('.k-err'), data = {}, bad = null;
        o.form.fields.forEach(function (f) {
          var el = box.querySelector('[name="' + f.name + '"]');
          data[f.name] = el.value.trim();
          if (!bad && f.required && !data[f.name]) bad = el;
          if (!bad && f.type === 'tel' && data[f.name] && data[f.name].replace(/\D/g, '').length < 10) bad = el;
          if (!bad && f.type === 'email' && data[f.name] && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data[f.name])) bad = el;
        });
        if (bad) { err.hidden = false; err.textContent = 'Lütfen işaretli alanı doğru doldurun: ' + bad.previousSibling.textContent + '.'; bad.focus(); return; }
        o.form.onSubmit(data, close);
      });
    }
    var first = box.querySelector('input,select,textarea') || box.querySelector('.k-x');
    if (first) first.focus();
    return box;
  }

  function money(n) { return '₺' + n.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  function go(sel) {
    var el = root.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // [data-go="#id"] scrolls; role=button elements respond to Enter and Space.
  root.addEventListener('click', function (e) {
    var g = e.target.closest('[data-go]');
    if (g) { e.preventDefault(); go(g.getAttribute('data-go')); }
  });
  root.addEventListener('keydown', function (e) {
    var b = e.target.closest && e.target.closest('[role="button"]');
    if (b && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); b.click(); }
  });
  root.querySelectorAll('[data-go],[data-act]').forEach(function (el) {
    if (el.tagName !== 'BUTTON' && el.tagName !== 'A' && !el.hasAttribute('role')) { el.setAttribute('role', 'button'); el.tabIndex = 0; }
  });

  return { toast: toast, modal: modal, money: money, go: go, esc: esc, host: host };
}
