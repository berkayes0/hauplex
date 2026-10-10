#!/usr/bin/env python3
"""Builds the Hauplex static pages from _build/parts.

    python3 _build/build.py [preview-output.html]

Writes index.html, hizmetler.html, referanslar.html, hakkimizda.html, iletisim.html and demos/*.html
next to assets/. With an argument, also writes a single-file preview (all pages in one
file with a small hash router) for publishing as an Artifact.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, '_build', 'parts')

def part(name):
    with open(os.path.join(PARTS, name + '.html'), encoding='utf-8') as f:
        return f.read()

def links(html):
    return (html.replace('href="#iletisim"', 'href="iletisim.html"')
                .replace('href="#hizmetler"', 'href="hizmetler.html"')
                .replace(' style="padding-top:0"', ''))

ARROW = '<svg aria-hidden="true"><use href="#i-arrow"/></svg>'

NAV = [('hizmetler', 'Hizmetler'), ('referanslar', 'Referanslar'), ('hakkimizda', 'Hakkımızda'), ('iletisim', 'İletişim')]

def header(active):
    items = '\n'.join(
        f'      <a href="{k}.html"{" aria-current=\"page\"" if k == active else ""}>{v}</a>' for k, v in NAV)
    return f'''<header class="site-header" id="top">
  <div class="wrap nav">
    <a class="brand" href="index.html" aria-label="Hauplex ana sayfa">
      <svg class="brand-mark" aria-hidden="true"><use href="#i-mark"/></svg>
      <span class="brand-name">hauplex</span>
    </a>
    <button class="nav-toggle" id="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Menüyü aç">
      <svg aria-hidden="true"><use href="#i-menu"/></svg>
    </button>
    <nav class="nav-links" id="nav-links" aria-label="Ana menü">
{items}
      <a class="btn btn-primary" href="iletisim.html">Teklif alın</a>
    </nav>
  </div>
</header>
'''

FOOTER = '''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html" aria-label="Hauplex ana sayfa">
          <svg class="brand-mark" aria-hidden="true"><use href="#i-mark"/></svg>
          <span class="brand-name">hauplex</span>
        </a>
        <p>İşletmeler için web siteleri, B2B portallar ve otomasyon sistemleri.</p>
      </div>
      <div>
        <h4>Hizmetler</h4>
        <ul>
          <li><a href="hizmetler.html#web-siteleri">Kurumsal web siteleri</a></li>
          <li><a href="hizmetler.html#b2b-portal">B2B portallar</a></li>
          <li><a href="hizmetler.html#otomasyon">Otomasyon</a></li>
          <li><a href="hizmetler.html#ek-hizmetler">E-ticaret ve bakım</a></li>
        </ul>
      </div>
      <div>
        <h4>Şirket</h4>
        <ul>
          <li><a href="hakkimizda.html">Hakkımızda</a></li>
          <li><a href="referanslar.html">Referanslar</a></li>
          <li><a href="hakkimizda.html#surec">Çalışma süreci</a></li>
          <li><a href="iletisim.html#sss">SSS</a></li>
        </ul>
      </div>
      <div>
        <h4>İletişim</h4>
        <ul>
          <li><a href="iletisim.html">Teklif alın</a></li>
          <li><a href="mailto:info@hauplex.com">info@hauplex.com</a></li>
          <li><a href="tel:+905425474169">+90 542 547 41 69</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> Hauplex. Tüm hakları saklıdır.</span>
      <span><a href="#">KVKK Aydınlatma Metni</a> · <a href="#">Çerez Politikası</a></span>
    </div>
  </div>
</footer>
'''

def page_hero(crumb, eyebrow, title, lead, extra=''):
    return f'''  <section class="page-hero">
    <div class="wrap">
      <nav class="crumbs" aria-label="Konum"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>{crumb}</span></nav>
      <span class="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{lead}</p>{extra}
    </div>
  </section>
'''

def cta(title, text, secondary=None):
    sec = f'\n          <a class="btn btn-ghost" href="{secondary[0]}">{secondary[1]}</a>' if secondary else ''
    return f'''  <section class="section" style="padding-top:0">
    <div class="wrap">
      <div class="cta">
        <div><h2>{title}</h2><p>{text}</p></div>
        <div class="cta-actions">
          <a class="btn btn-primary" href="iletisim.html">Ücretsiz keşif görüşmesi {ARROW}</a>{sec}
        </div>
      </div>
    </div>
  </section>
'''

DEMOS = [
    # slug, name, kind, filter category, card text, thumbnail hue, thumbnail background, thumbnail layout
    ('insaat', 'Kuzeyhan Yapı', 'İnşaat · Kurumsal web sitesi', 'web',
     'Proje portföyü, inşaat ilerleme takibi ve teklif alanı olan kurumsal site.', '#C99A0E', '#FBF4DE', 'a'),
    ('gida', 'Bereket Gıda', 'Toptan gıda · B2B bayi portalı', 'b2b',
     'Bayiye özel fiyat, cari hesap, kampanya ve hızlı sipariş ekranı olan portal.', '#1F5A40', '#EAF2EC', 'b'),
    ('uretim', 'Ersan Metal', 'Üretim · Sipariş ve fatura otomasyonu', 'oto',
     'Siparişten e-faturaya kadar elle veri girişi gerektirmeyen operasyon paneli.', '#FF7A1A', '#1F2229', 'c'),
    ('klinik', 'Lavin Diş Kliniği', 'Sağlık · Klinik web sitesi ve online randevu', 'web',
     'Tedavi tanıtımı, hekim profilleri ve uygun saati seçerek online randevu.', '#0F5C58', '#EEF5F2', 'd'),
    ('otomotiv', 'Parçam Oto', 'Otomotiv yedek parça · B2B sipariş portalı', 'b2b',
     'Araç ya da plakaya göre uyumlu parça arama, depo bazında stok ve net fiyat.', '#D7263D', '#EEF0F4', 'e'),
    ('lojistik', 'Rota Lojistik', 'Lojistik · Stok ve kargo bildirimleri', 'oto',
     'Gönderi takibi, kritik stok uyarıları ve müşteriye otomatik WhatsApp mesajları.', '#4A2C82', '#F1ECF9', 'f'),
    ('finans', 'Atlas Dağıtım', 'Finans · Nakit akışı ve tahsilat otomasyonu', 'oto',
     'Vadesi gelen alacaklara otomatik hatırlatma, banka hareketlerinden tahsilat eşleştirme ve 90 günlük nakit tahmini.', '#0E7C66', '#E8F4F0', 'a'),
    ('mutabakat', 'Kardelen Mobilya', 'Muhasebe · Fatura okuma ve banka mutabakatı', 'oto',
     'Gelen faturaları okuyup muhasebeye işleyen, banka ekstresini cari hesaplarla otomatik eşleştiren panel.', '#1D4ED8', '#EEF2FB', 'b'),
    ('rakip', 'Modaev', 'E-ticaret · Rakip fiyat ve pazar analizi', 'oto',
     'Rakiplerin fiyat, stok ve kampanyalarını izleyip fiyatları kurallara göre otomatik güncelleyen sistem.', '#E11D48', '#FDF0F3', 'c'),
    ('rota', 'Yolda Dağıtım', 'Lojistik · Rota optimizasyonu ve filo takibi', 'oto',
     'Teslimatları araçlara dağıtan, en kısa rotayı çıkaran ve gecikmeleri müşteriye bildiren planlama ekranı.', '#EA580C', '#FFF3EA', 'd'),
    ('talep', 'Tazemarket', 'Perakende · Talep tahmini ve otomatik satın alma', 'oto',
     'Satış geçmişi, hava durumu ve kampanyalara göre talebi tahmin edip tedarikçiye sipariş taslağı hazırlayan sistem.', '#65A30D', '#F2F7E8', 'e'),
    ('pazaryeri', 'Nova Kozmetik', 'E-ticaret · Çok kanallı pazaryeri yönetimi', 'oto',
     'Trendyol, Hepsiburada, Amazon ve kendi sitesindeki stok, fiyat ve siparişleri tek ekrandan yöneten panel.', '#7C3AED', '#F4EFFD', 'f'),
]

THUMBS = {
    'a': '<b class="blk h"></b><b class="blk t"></b><b class="blk t2"></b><div class="row"><b></b><b></b><b></b></div>',
    'b': '<b class="blk h"></b><div class="tbl"><b></b><b></b><b></b><b></b><b></b></div>',
    'c': '<div class="row"><b></b><b></b><b></b></div><b class="blk t"></b><b class="blk t2"></b><div class="tbl"><b></b><b></b><b></b></div>',
    'd': '<div class="row"><b></b><b></b><b></b></div><b class="blk h"></b><b class="blk t"></b>',
    'e': '<div class="tbl"><b></b><b></b><b></b></div><div class="row"><b></b><b></b><b></b></div>',
    'f': '<b class="blk h"></b><div class="row"><b></b><b></b><b></b></div><div class="tbl"><b></b><b></b></div>',
}

def ref_card(d):
    slug, name, kind, cat, desc, hue, bg, layout = d
    return f'''        <article class="ref" data-cat="{cat}" style="--hue:{hue};--hue-bg:{bg}">
          <a class="ref-link" href="demos/{slug}.html" aria-label="{name} demosunu açın">
            <div class="ref-shot" aria-hidden="true">
              <div class="ref-bar"><i></i><i></i><i></i><span></span></div>
              <img class="ref-img" src="assets/refs/{slug}.webp" width="960" height="640" loading="lazy" decoding="async" alt="">
              <span class="demo-badge">Demo</span><span class="ref-open">Demoyu aç</span>
            </div>
          </a>
          <div class="ref-meta">
            <small>{kind}</small>
            <h3>{name}</h3>
            <p>{desc}</p>
            <a class="text-link" href="demos/{slug}.html">Demoyu inceleyin {ARROW}</a>
          </div>
        </article>
'''

def cards(items):
    return ''.join(ref_card(d) for d in items)

DEMOBAR_CSS = """
.demobar{position:sticky;top:env(safe-area-inset-top,0px);z-index:60;background:#0E1420;color:#E8ECF2;font:500 14px/1.3 "Instrument Sans","Segoe UI",system-ui,sans-serif;border-bottom:1px solid #263042}
.demobar-in{max-width:1240px;margin:0 auto;padding:10px clamp(16px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:12px 20px;flex-wrap:wrap}
.demobar a{color:inherit;text-decoration:none}
.demobar-l{display:flex;align-items:center;gap:12px;min-width:0;flex-wrap:wrap}
.demobar-brand{display:inline-flex;align-items:center;gap:8px;font-family:"Bricolage Grotesque","Segoe UI",sans-serif;font-weight:700;font-size:17px;letter-spacing:-.02em}
.demobar-brand svg{width:24px;height:24px}
.demobar-tag{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;text-transform:uppercase;letter-spacing:.08em;padding:4px 8px;border-radius:5px;background:#F2B4551f;color:#F2B455}
.demobar-name{color:#8E98AB}.demobar-name b{color:#E8ECF2;font-weight:600}
.demobar-r{display:flex;gap:8px;flex-wrap:wrap}
.demobar-r a{padding:8px 14px;border-radius:999px;border:1px solid #263042;font-weight:600;font-size:13px;white-space:nowrap}
.demobar-r a:hover{border-color:#E8ECF2}
.demobar-r a.go{background:#7086FF;border-color:#7086FF;color:#0B0F16}
@media (max-width:640px){.demobar-name{display:none}}
"""

MARK_SVG = '<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="none" stroke="#7086FF" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 6v19M10 17.5a6 6 0 0 1 12 0v4.4"/></g><circle cx="10" cy="5" r="3.6" fill="#7086FF"/><circle cx="22" cy="25.6" r="3.3" fill="none" stroke="#7086FF" stroke-width="2.8"/></svg>'

def demobar(d, prefix):
    return f'''<div class="demobar"><div class="demobar-in">
  <div class="demobar-l"><a class="demobar-brand" href="{prefix}index.html">{MARK_SVG}hauplex</a><span class="demobar-tag">Demo tasarım</span><span class="demobar-name"><b>{d[1]}</b> · {d[2]}</span></div>
  <div class="demobar-r"><a href="{prefix}referanslar.html">← Tüm referanslar</a><a class="go" href="{prefix}iletisim.html">Benzerini isteyin</a></div>
</div></div>
'''

def demo_file(name):
    with open(os.path.join(ROOT, '_build', 'demos', name), encoding='utf-8') as f:
        return f.read()

def demo_src(slug):
    """Returns (markup, meta, script) for _build/demos/<slug>.html.

    meta comes from the leading <!--meta ...--> comment; script is the body of the trailing <script>,
    run as function (root, kit) where root is the document or the preview's shadow root and kit is _kit.js.
    The shared _kit.css is prepended to the markup."""
    src = demo_file(slug + '.html')
    end = src.index('-->')
    meta = dict(re.findall(r'(\w+)="([^"]*)"', src[:end]))
    body = src[end + 3:]
    script = ''
    if '<script>' in body:
        i = body.index('<script>')
        script = body[i + 8:body.index('</script>', i)].strip()
        body = body[:i]
    return '<style>\n' + demo_file('_kit.css') + '</style>\n' + body.strip(), meta, script

import json as _json
INTEG = _json.load(open(os.path.join(ROOT, '_build', 'integrations.json'), encoding='utf-8'))
INTEG_COUNT = sum(len(g['items']) for g in INTEG)

def integ_chip(it):
    if it['path']:
        return (f'<li class="ig"><span class="ig-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="{it["hex"]}" d="{it["path"]}"/></svg></span>'
                f'<span>{it["name"]}</span></li>')
    return f'<li class="ig text"><span>{it["name"]}</span></li>'

def integrations_strip():
    items = [it for g in INTEG for it in g['items']]
    half = (len(items) + 1) // 2
    rows = ''
    for k, chunk in enumerate((items[:half], items[half:])):
        chips = ''.join(integ_chip(it) for it in chunk)
        rows += f'      <div class="marquee{" rev" if k else ""}"><ul>{chips}</ul><ul aria-hidden="true">{chips}</ul></div>\n'
    return f"""  <section class="integrations" aria-label="Entegrasyonlar">
    <div class="wrap integ-head">
      <p>Bağlandığımız sistemler</p>
      <span class="integ-count"><b>{INTEG_COUNT}</b> sistem ve uygulama</span>
      <a class="text-link" href="hizmetler.html#entegrasyonlar">Tümünü görün {ARROW}</a>
    </div>
{rows}  </section>
"""

def integrations_grid():
    groups = ''.join(f'<article class="ig-group"><h3>{g["group"]}<small>{len(g["items"])}</small></h3><ul>{"".join(integ_chip(it) for it in g["items"])}</ul></article>' for g in INTEG)
    return f"""  <section class="section" id="entegrasyonlar" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Entegrasyonlar</span>
        <h2>{INTEG_COUNT} sistemle konuşan çözümler</h2>
        <p>Kullandığınız muhasebe programını, ödeme altyapısını, pazaryerlerini ve iletişim kanallarını değiştirmeniz gerekmez. Sitenizi, portalınızı ve otomasyonlarınızı mevcut sistemlerinize bağlıyoruz. Listede olmayan bir sistem kullanıyorsanız, API'si olan hemen her yazılıma bağlanabiliriz.</p>
      </div>
      <div class="ig-grid">{groups}</div>
    </div>
  </section>
"""

def home():
    services = links(part('services'))
    for anchor, old in [('web-siteleri', 'Web sitesi teklifi alın'), ('b2b-portal', 'B2B portal teklifi alın'), ('otomasyon', 'Otomasyon teklifi alın')]:
        services = services.replace(f'href="iletisim.html">{old}', f'href="hizmetler.html#{anchor}">Detayları inceleyin')
    services = services[:services.index('      <ul class="extras">')] + f'''      <div class="section-foot"><a class="text-link" href="hizmetler.html">E-ticaret, SEO, hosting ve bakım hizmetlerimiz {ARROW}</a></div>
    </div>
  </section>
'''
    refs = links(part('refs')).replace('{{CARDS_HOME}}', cards([d for d in DEMOS if d[0] in ('insaat', 'gida', 'rakip')]))
    refs = refs.replace('      </div>\n    </div>\n  </section>', f'      </div>\n      <div class="section-foot"><a class="text-link" href="referanslar.html">Tüm referansları görün {ARROW}</a></div>\n    </div>\n  </section>', 1)
    return (links(part('hero')) + integrations_strip() + part('video') + services + links(part('band')) + refs
            + cta('Projenizi birlikte planlayalım.', 'Ne yapmak istediğinizi anlatın; ihtiyacınıza uygun çözümü ve net bir teklifi birlikte çıkaralım.', ('hizmetler.html', 'Hizmetleri inceleyin')))

def hizmetler():
    jump = '\n      <div class="jump"><a href="#web-siteleri">Web siteleri</a><a href="#b2b-portal">B2B portallar</a><a href="#otomasyon">Otomasyon</a><a href="#entegrasyonlar">Entegrasyonlar</a><a href="#ek-hizmetler">Ek hizmetler</a></div>'
    detail = part('svc-detail').replace('<section class="section" style="padding-top:0">', '<section class="section" id="ek-hizmetler" style="padding-top:0">')
    return (page_hero('Hizmetler', 'Hizmetler', 'Siteden sisteme, işinizin tüm dijital altyapısı.',
                      'Üç ana alanda çalışıyoruz ve bunları birbirine bağlıyoruz: müşteriyi getiren web sitesi, siparişi alan B2B portal ve arka planda işleri yürüten otomasyonlar.', jump)
            + detail.replace('  <section class="section" id="ek-hizmetler"', integrations_grid() + '  <section class="section" id="ek-hizmetler"', 1)
            + cta('Hangi hizmetin size uygun olduğundan emin değil misiniz?', 'Keşif görüşmesinde mevcut durumunuzu dinleyip en çok kazandıracak adımı birlikte belirleyelim.'))

def referanslar():
    return (page_hero('Referanslar', 'Referanslar', 'Örnek projeler ve canlı demolar.',
                      'Farklı sektörler için hazırladığımız web sitesi, B2B portal ve otomasyon demoları. Bir karta tıklayın, o projenin nasıl çalıştığını kendiniz görün.')
            + part('refs-all').replace('{{CARDS_ALL}}', cards(DEMOS))
            + cta('Bunlardan birine benzer bir şey mi istiyorsunuz?', 'Demoları işletmenize göre uyarlıyoruz. Ücretsiz keşif görüşmesinde neye ihtiyacınız olduğunu konuşalım.'))

def hakkimizda():
    about = links(part('about')).replace('<span class="eyebrow">Hakkımızda</span>\n        <h2>', '<h2>')
    return (page_hero('Hakkımızda', 'Hakkımızda', 'Teknolojiyi işletmeler için sadeleştiriyoruz.',
                      'Hauplex, web sitesi, B2B portal ve otomasyon ihtiyaçlarını tek bir ekipten karşılamak isteyen işletmeler için kuruldu.')
            + about + links(part('process')).replace('<section class="section" id="surec">', '<section class="section" id="surec" style="padding-top:0">')
            + cta('Tanışalım.', 'İşletmenizi ve hedeflerinizi dinlemek için bir kahve kadar kısa, ücretsiz bir görüşme yeterli.'))

def iletisim():
    contact = links(part('contact')).replace('<h2>Projenizi konuşalım.</h2>', '<h2>Size nasıl yardımcı olabiliriz?</h2>')
    steps = '''  <section class="section" style="padding-top:0">
    <div class="wrap">
      <div class="section-head" style="margin-bottom:0">
        <span class="eyebrow">Sonraki adımlar</span>
        <h2>Formu gönderdikten sonra</h2>
      </div>
      <ol class="next-steps">
        <li><strong>Dönüş yapıyoruz</strong><span>Mesajınızı inceleyip bir iş günü içinde sizi arıyor ya da e-posta gönderiyoruz.</span></li>
        <li><strong>Keşif görüşmesi</strong><span>Yaklaşık 30 dakikalık ücretsiz bir görüşmede ihtiyacınızı ve hedeflerinizi konuşuyoruz.</span></li>
        <li><strong>Net teklif</strong><span>Kapsamı, takvimi ve fiyatı belli yazılı bir teklif hazırlıyoruz.</span></li>
      </ol>
    </div>
  </section>
'''
    return (page_hero('İletişim', 'İletişim', 'Projenizi konuşalım.',
                      'Formu doldurun ya da doğrudan e-posta veya telefonla ulaşın. Keşif görüşmesi ücretsizdir ve herhangi bir taahhüt gerektirmez.')
            + contact + steps + part('faq'))

PAGES = [
    ('index', None, 'Hauplex | Web Siteleri, B2B Portallar ve Otomasyon',
     'Hauplex; işletmeler için kurumsal web siteleri, B2B sipariş portalları ve iş süreci otomasyonları geliştirir. Ücretsiz keşif görüşmesi için bize ulaşın.', home),
    ('hizmetler', 'hizmetler', 'Hizmetler | Hauplex',
     'Kurumsal web siteleri, B2B sipariş portalları, iş süreci otomasyonu, e-ticaret, SEO, hosting ve bakım hizmetleri.', hizmetler),
    ('referanslar', 'referanslar', 'Referanslar | Hauplex',
     'Hauplex olarak farklı sektörlerden işletmeler için kurduğumuz web siteleri, B2B portallar ve otomasyon projeleri.', referanslar),
    ('hakkimizda', 'hakkimizda', 'Hakkımızda | Hauplex',
     'Hauplex, işletmelerin web sitesi, B2B portal ve otomasyon ihtiyaçlarını tek bir ekipten karşılar.', hakkimizda),
    ('iletisim', 'iletisim', 'İletişim | Hauplex',
     'Hauplex ile iletişime geçin, ücretsiz keşif görüşmesi planlayın ve projeniz için net bir teklif alın.', iletisim),
]

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap">'''

FAVICON = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2232%22 height=%2232%22 viewBox=%220 0 32 32%22 xmlns:c2pa=%22http://c2pa.org/manifest%22%3E%3Cmetadata%3E%3Cc2pa:manifest%3EAAAWgmp1bWIAAAAeanVtZGMycGEAEQAQgAAAqgA4m3EDYzJwYQAAABZcanVtYgAAAEdqdW1kYzJtYQARABCAAACqADibcQN1cm46YzJwYTo1ODMxMDk0YS03NmFmLTQzOTctYTJjMC1hMWI2MjI5Y2VlMWIAAAADl2p1bWIAAAApanVtZGMyYXMAEQAQgAAAqgA4m3EDYzJwYS5hc3NlcnRpb25zAAAAALxqdW1iAAAARGp1bWRjYm9yABEAEIAAAKoAOJtxE2MycGEuaW5ncmVkaWVudC52MwAAAAAYYzJzaK81mBHbTk9w%2BFrl9%2BlK2oEAAABwY2JvcqNpZGM6Zm9ybWF0bWltYWdlL3N2Zyt4bWxqaW5zdGFuY2VJRHgseG1wOmlpZDo0ZGNkNWEwYS1jZTdhLTQ2ODgtODgxYy1mMTVkMGU5OWI5MWJscmVsYXRpb25zaGlwaHBhcmVudE9mAAAB4mp1bWIAAABBanVtZGNib3IAEQAQgAAAqgA4m3ETYzJwYS5hY3Rpb25zLnYyAAAAABhjMnNo9JU%2BJ3CN52//6ZHVsOHP4AAAAZljYm9yomdhY3Rpb25zgqJmYWN0aW9ua2MycGEub3BlbmVkanBhcmFtZXRlcnOha2luZ3JlZGllbnRzgaJjdXJseC1zZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmluZ3JlZGllbnQudjNkaGFzaFggOALOs0bC6c9qwF2jLDxeIjE%2Bu/LjWiVm4vRLygZhRnWkZmFjdGlvbngdY29tLmFudGhyb3BpYy5jbGF1ZGUucHJvdmlkZWRqcGFyYW1ldGVyc6F4H2NvbS5hbnRocm9waWMub3JpZ2luLWNvbmZpZGVuY2VndW5rbm93bmtkZXNjcmlwdGlvbnhmQ2xhdWRlIHByb3ZpZGVkIHRoaXMgZmlsZSBhdCB0aGUgcmVxdWVzdCBvZiBhIHVzZXIgYW5kIG1heSBoYXZlIGNyZWF0ZWQgb3IgbW9kaWZpZWQgdGhlIGZpbGUgY29udGVudHMubXNvZnR3YXJlQWdlbnShZG5hbWVmQ2xhdWRlcmFsbEFjdGlvbnNJbmNsdWRlZPUAAADIanVtYgAAAEBqdW1kY2JvcgARABCAAACqADibcRNjMnBhLmhhc2guZGF0YQAAAAAYYzJzaBQJj3aVjFue5ewbs0S9ovcAAACAY2JvcqVjYWxnZnNoYTI1NmNwYWRNAAAAAAAAAAAAAAAAAGRoYXNoWCAfwCXyHIdXVaQD7N39F7Q3pMMpWbUWaZABRwoq4HtGi2RuYW1lbmp1bWJmIG1hbmlmZXN0amV4Y2x1c2lvbnOBomVzdGFydBiSZmxlbmd0aBkeBAAAAj5qdW1iAAAAJ2p1bWRjMmNsABEAEIAAAKoAOJtxA2MycGEuY2xhaW0udjIAAAACD2Nib3KlY2FsZ2ZzaGEyNTZpc2lnbmF0dXJleE1zZWxmI2p1bWJmPS9jMnBhL3VybjpjMnBhOjU4MzEwOTRhLTc2YWYtNDM5Ny1hMmMwLWExYjYyMjljZWUxYi9jMnBhLnNpZ25hdHVyZWppbnN0YW5jZUlEeCx4bXA6aWlkOmRkZDE1NGM4LTI1N2YtNDFlYy1iNWIxLTAxOGY0ZmUwYjQyZnJjcmVhdGVkX2Fzc2VydGlvbnODomN1cmx4LXNlbGYjanVtYmY9YzJwYS5hc3NlcnRpb25zL2MycGEuaW5ncmVkaWVudC52M2RoYXNoWCA4As6zRsLpz2rAXaMsPF4iMT678uNaJWbi9EvKBmFGdaJjdXJseCpzZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmFjdGlvbnMudjJkaGFzaFggJ9zmNADvyhyK7JPMqjuuos/CSyTSIBJFsVZ1nxVj%2BGSiY3VybHgpc2VsZiNqdW1iZj1jMnBhLmFzc2VydGlvbnMvYzJwYS5oYXNoLmRhdGFkaGFzaFggk56B955C3cOMHVIeAni5Up2m3uoxsRBikxuSTa0K%2BRh0Y2xhaW1fZ2VuZXJhdG9yX2luZm%2BjZG5hbWVvQW50aHJvcGljIEZpbGVzZ3ZlcnNpb25lMS4wLjBrc3BlY1ZlcnNpb25lMi40LjAAABA4anVtYgAAAChqdW1kYzJjcwARABCAAACqADibcQNjMnBhLnNpZ25hdHVyZQAAABAIY2JvctKEWQISogEmGCFZAgowggIGMIIBjaADAgECAhRA5aAK7sI50L64g/oGQgU9Z1UTADAKBggqhkjOPQQDAzBJMRcwFQYDVQQKEw5BbnRocm9waWMsIFBCQzEuMCwGA1UEAxMlQW50aHJvcGljIENvbnRlbnQgQ3JlZGVudGlhbHMgUm9vdCBDQTAeFw0yNjA4MDcxODQzNTZaFw0yODA4MDYxOTQzNTZaMEQxFzAVBgNVBAoTDkFudGhyb3BpYywgUEJDMSkwJwYDVQQDEyBBbnRocm9waWMgQ2xhdWRlIENvbnRlbnQgU2lnbmluZzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJh6CmvLUBgFFNU0vUKlOVtE6djd17L5SuwX0LemFisBM3dkd/3cyjxFA3Qo5S46fX0/ihY0VZ7mfb9KF703t5OjWDBWMA4GA1UdDwEB/wQEAwIHgDAVBgNVHSUEDjAMBgorBgEEAYPoXgIBMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUzlHiBIFOZFsj%2BOPEz5o%2BnMHXXMIwCgYIKoZIzj0EAwMDZwAwZAIwMXMdFJ4BetLLVY7ORuE9noqbbAZOZn/aArXyTwFAZfKrPzxF2vPoJNf1%2BUCdg1XGAjBwX1zd9WGqYkqmL5SFqw1QySjr1zJfpJM9%2B1rdDwSPLMOPOjKuiXjoU/pUUeG9RwmhY3BhZFkNngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPZYQLquS1CsjLCVX0/POQqSlNqDuq4Njbkymw9Sk1mZH6oUUvV61ppUPQx1i1vVMPPo2AQj82O6GKrBkYoRfX0pMa4=%3C/c2pa:manifest%3E%3C/metadata%3E%3Crect width=%2232%22 height=%2232%22 rx=%228%22 fill=%22%232340E8%22/%3E%3Cg transform=%22translate%2816 16%29 scale%28.8%29 translate%28-16 -15.6%29%22%3E%3Cg fill=%22none%22 stroke=%22%23FFFFFF%22 stroke-width=%224%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22%3E%3Cpath d=%22M10 6v19M10 17.5a6 6 0 0 1 12 0v4.4%22/%3E%3C/g%3E%3Ccircle cx=%2210%22 cy=%225%22 r=%223.6%22 fill=%22%23FFFFFF%22/%3E%3Ccircle cx=%2222%22 cy=%2225.6%22 r=%223.3%22 fill=%22none%22 stroke=%22%23FFFFFF%22 stroke-width=%222.8%22/%3E%3C/g%3E%3C/svg%3E'

def asset_ver(name):
    # Content hash so browsers fetch the new file after each change instead of a cached copy
    import hashlib
    return hashlib.sha1(open(os.path.join(ROOT, 'assets', name), 'rb').read()).hexdigest()[:8]

def site_page(slug, active, title, desc, body):
    return f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta name="theme-color" content="#2340E8">
<link rel="icon" href="{FAVICON}">
<link rel="icon" href="assets/logo/favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="assets/logo/apple-touch-icon.png">
<meta property="og:image" content="assets/logo/hauplex-paylasim-gorseli.png">
{FONTS}
<link rel="stylesheet" href="assets/style.css?v={asset_ver('style.css')}">
</head>
<body>
{part('defs')}
{header(active)}
<main>
{body}</main>

{FOOTER}
<script src="assets/main.js?v={asset_ver('main.js')}"></script>
</body>
</html>
'''

def demo_page(d):
    body, meta, script = demo_src(d[0])
    return f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{d[1]} · Hauplex demo</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={meta['fonts']}&family=Bricolage+Grotesque:opsz,wght@12..96,700&family=Instrument+Sans:wght@500;600&family=JetBrains+Mono:wght@500&display=swap">
<style>body{{margin:0}}{DEMOBAR_CSS}</style>
</head>
<body>
{demobar(d, '../')}
{body}
<script>
{demo_file('_kit.js')}
(function (root, kit) {{
{script}
}})(document, demoKit(document));
</script>
</body>
</html>
'''

# Preview only: every page lives in one file. Demo pages render inside shadow roots so their CSS stays isolated.
ROUTER = '''
(function () {
  document.querySelectorAll('.demo-host').forEach(function (host) {
    var tpl = document.getElementById('tpl-' + host.getAttribute('data-demo'));
    var slug = host.getAttribute('data-demo');
    var shadow = host.attachShadow({ mode: 'open' });
    shadow.appendChild(tpl.content.cloneNode(true));
    if (DEMO_JS[slug]) DEMO_JS[slug](shadow, demoKit(shadow));
  });
  var pages = document.querySelectorAll('.page');
  var navLinks = document.querySelectorAll('.nav-links a:not(.btn)');
  function show(name, frag) {
    var target = document.querySelector('.page[data-page="' + name + '"]') || pages[0];
    pages.forEach(function (p) { p.hidden = p !== target; });
    document.body.classList.toggle('in-demo', target.classList.contains('demo-page'));
    navLinks.forEach(function (a) {
      if (a.getAttribute('href') === target.getAttribute('data-page') + '.html') a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    try { history.replaceState(null, '', '#' + target.getAttribute('data-page')); } catch (e) {}
    var el = frag && target.querySelector('[id="' + frag + '"]');
    if (el) el.scrollIntoView(); else window.scrollTo(0, 0);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href');
    var d = href.match(/^demos\\/([a-z]+)\\.html$/);
    if (d) { e.preventDefault(); show('demo-' + d[1]); return; }
    var m = href.match(/^([a-z]+)\\.html(?:#(.+))?$/);
    if (m) { e.preventDefault(); show(m[1], m[2]); return; }
    if (href.charAt(0) === '#' && href.length > 1) {
      var cur = document.querySelector('.page:not([hidden])');
      var el = cur && cur.querySelector('[id="' + href.slice(1) + '"]');
      e.preventDefault();
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  });
  show((location.hash || '#index').slice(1));
})();
'''

def preview(path):
    css = open(os.path.join(ROOT, 'assets', 'style.css'), encoding='utf-8').read()
    js = open(os.path.join(ROOT, 'assets', 'main.js'), encoding='utf-8').read()
    mains = ''.join(f'<div class="page" data-page="{slug}"{"" if slug == "index" else " hidden"}>\n{fn()}</div>\n' for slug, _, _, _, fn in PAGES)
    demo_mains = ''.join(f'<div class="page demo-page" data-page="demo-{d[0]}" hidden>\n{demobar(d, "")}<div class="demo-host" data-demo="{d[0]}"></div>\n</div>\n' for d in DEMOS)
    demo_js = 'var DEMO_JS = {\n' + ',\n'.join(f'{d[0]}: function (root, kit) {{\n{demo_src(d[0])[2]}\n}}' for d in DEMOS) + '\n};\n' + demo_file('_kit.js')
    templates = ''.join(f'<template id="tpl-{d[0]}">\n{demo_src(d[0])[0]}\n</template>\n' for d in DEMOS)
    demo_fonts = '&family='.join(demo_src(d[0])[1]['fonts'] for d in DEMOS)
    out = f'''<title>Hauplex Web Sitesi</title>
{FONTS}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={demo_fonts}&display=swap">
<style>
{css}
{DEMOBAR_CSS}
.in-demo .site-header, .in-demo .site-footer {{ display: none; }}
.demo-host {{ display: block; }}
</style>
{part('defs')}
{header(None)}
<main>
{mains}{demo_mains}</main>
{templates}
{FOOTER}
<script>
{js}
{demo_js}
{ROUTER}
</script>
'''
    import base64
    for d in DEMOS:
        b64 = base64.b64encode(open(os.path.join(ROOT, 'assets', 'refs', d[0] + '.webp'), 'rb').read()).decode()
        out = out.replace(f'src="assets/refs/{d[0]}.webp"', f'src="data:image/webp;base64,{b64}"')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)

if __name__ == '__main__':
    for slug, active, title, desc, fn in PAGES:
        with open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8') as f:
            f.write(site_page(slug, active, title, desc, fn()))
    nf = site_page('404', None, 'Sayfa bulunamadı | Hauplex', 'Aradığınız sayfa bulunamadı.',
                   page_hero('404', 'Hata 404', 'Bu sayfa bulunamadı.', 'Adres değişmiş ya da yanlış yazılmış olabilir. Ana sayfadan devam edebilirsiniz.',
                             '\n      <p style="margin-top:28px"><a class="btn btn-primary" href="index.html">Ana sayfaya dön</a></p>'))
    with open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8') as f:
        f.write(nf.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<script>document.write(\'<base href="\' + (/\\.github\\.io$/.test(location.hostname) ? \'/\' + location.pathname.split(\'/\')[1] + \'/\' : \'/\') + \'">\')</script>\n<meta name="robots" content="noindex">', 1))
    os.makedirs(os.path.join(ROOT, 'demos'), exist_ok=True)
    for d in DEMOS:
        with open(os.path.join(ROOT, 'demos', d[0] + '.html'), 'w', encoding='utf-8') as f:
            f.write(demo_page(d))
    if len(sys.argv) > 1:
        preview(sys.argv[1])
    print('ok')
