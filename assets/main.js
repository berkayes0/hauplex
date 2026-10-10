(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.getElementById('nav-toggle');
  var links = document.getElementById('nav-links');

  function onScroll() { header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  function setMenu(open) {
    links.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Menüyü kapat' : 'Menüyü aç');
    toggle.querySelector('use').setAttribute('href', open ? '#i-close' : '#i-menu');
  }
  toggle.addEventListener('click', function () { setMenu(!links.classList.contains('open')); });
  links.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });

  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  // Form: validates in the browser, then sends via FormSubmit to the form's data-to address when served from the live site.
  var filters = document.querySelector('.filters');
  if (filters) {
    filters.addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-filter]');
      if (!btn) return;
      var f = btn.getAttribute('data-filter');
      filters.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      document.querySelectorAll('.refs.all .ref').forEach(function (card) {
        card.hidden = f !== 'all' && card.getAttribute('data-cat') !== f;
      });
    });
  }

  var form = document.getElementById('contact-form');
  var status = document.getElementById('form-status');
  var endpoint = form && /(^|\.)hauplex\.|\.github\.io$/.test(location.hostname) ? 'https://formsubmit.co/ajax/' + form.getAttribute('data-to') : '';
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    var missing = Array.prototype.filter.call(form.querySelectorAll('[required]'), function (el) { return !el.value.trim(); });
    var email = form.querySelector('#f-email');
    status.hidden = false;
    if (missing.length) {
      status.className = 'form-status error';
      status.textContent = 'Lütfen ad soyad, e-posta ve proje açıklaması alanlarını doldurun.';
      missing[0].focus();
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
      status.className = 'form-status error';
      status.textContent = 'E-posta adresi geçerli görünmüyor. Örnek: ad@firma.com';
      email.focus();
      return;
    }
    if (!endpoint) {
      status.className = 'form-status';
      status.textContent = 'Teşekkürler! Form doğru dolduruldu. (Bu önizlemede form henüz bir e-posta servisine bağlı değil, mesaj gönderilmedi.)';
      return;
    }
    fetch(endpoint, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
      .then(function (r) {
        if (!r.ok) throw new Error();
        status.className = 'form-status';
        status.textContent = 'Teşekkürler! Mesajınız bize ulaştı, en kısa sürede dönüş yapacağız.';
        form.reset();
      })
      .catch(function () {
        status.className = 'form-status error';
        status.textContent = 'Mesaj gönderilemedi. Lütfen tekrar deneyin ya da bize e-posta ile ulaşın.';
      });
  });
})();

// Intro video: custom play button over the poster
(function () {
  var v = document.getElementById('tanitim-video');
  if (!v) return;
  var frame = v.parentNode, btn = frame.querySelector('.video-play');
  btn.addEventListener('click', function () { frame.classList.add('playing'); v.controls = true; v.play(); });
  v.addEventListener('play', function () { frame.classList.add('playing'); v.controls = true; });
})();
