# -*- coding: utf-8 -*-
"""Metursan çok dilli statik site üreticisi (tr, en, de, fr, ar).
python3 build.py          -> dist/ (temiz linkler, canlı sunucu için)
python3 build.py --files  -> dist_preview/ (…/index.html linkleri, dosya önizlemesi için)
"""
import json, os, re, shutil, sys, html, importlib
from urllib.parse import quote
from datetime import date
from data import SITE, CATEGORIES, P, SOCIAL

PRETTY = "--files" not in sys.argv
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "dist_preview" if not PRETTY else "dist")
D = SITE["domain"]
TODAY = date.today().isoformat()
UP = "https://huzurpano.com/wp-content/uploads/"
LANGS = ["tr", "en", "de", "fr", "ar"]
e = lambda s: html.escape(str(s), quote=True)
M = {l: importlib.import_module("lang." + l) for l in LANGS}

def F(s, **kw):
    for k, v in kw.items(): s = s.replace("{" + k + "}", str(v))
    return s
CTX = dict(legal=SITE["legal"], founded=SITE["founded"], wa=SITE["whatsapp_display"], email=SITE["email"], phone=SITE["phone1"])

# Kendi fotoğraflarınız: static/img/<urun-slug>/ klasörüne konan .jpg/.jpeg/.png/.webp dosyaları
# (ör. Photoroom çıktıları) huzurpano.com görsellerinin yerine, dosya adı sırasıyla kullanılır.
LOCAL_IMG = os.path.join(BASE, "static", "img")
def local_imgs(slug):
    d = os.path.join(LOCAL_IMG, slug)
    if not os.path.isdir(d): return None
    fs = sorted(f for f in os.listdir(d) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    return [f"/static/img/{slug}/{quote(f)}" for f in fs] or None

# ---------- veri ----------
CAT = {c["slug"]: c for c in CATEGORIES}
BASEP = []
counters = {}
for (slug, cat, name, short, feats, uses, about, imgs, yt) in P:
    counters[cat] = counters.get(cat, 0) + 1
    imgs = local_imgs(slug) or imgs
    BASEP.append(dict(slug=slug, cat=cat, imgs=imgs, yt=yt, code=f"MT-{CAT[cat]['code']}-{counters[cat]:02d}", ym=max((i[:7] for i in imgs if not i.startswith("/")), default="2026/11"),
                      tr=(name, short, feats, uses, about)))
for c in CATEGORIES:
    c["items"] = [p for p in BASEP if p["cat"] == c["slug"]]
    c["cover"] = c["items"][0]["imgs"][0]
    c["tr"] = (c["name"], c["short"], c["intro"], c["faq"])
NEWEST = sorted(BASEP, key=lambda p: p["ym"], reverse=True)[:12]

def ct(c, L):  # kategori metni
    return c["tr"] if L == "tr" else M[L].CATS[c["slug"]]
def pt(p, L):  # ürün metni
    return p["tr"] if L == "tr" else M[L].PRODS[p["slug"]]

def img(path, w=800):
    src = D + path if path.startswith("/") else UP + path   # "/static/img/..." = kendi deponuzdaki fotoğraf
    return "https://wsrv.nl/?url=" + quote(src, safe="") + f"&w={w}&output=webp&q=82"


CHAT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2a9.8 9.8 0 0 0-8.5 14.7L2.2 21.8l5-1.3A9.8 9.8 0 1 0 12 2.2zm0 1.8a8 8 0 1 1-4.2 14.8l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0 1 12 4zm-3.1 4.2c-.2 0-.5 0-.7.3-.3.3-.9.9-.9 2.2s1 2.6 1.1 2.7c.1.2 1.9 3 4.7 4.1 2.3.9 2.8.7 3.3.7s1.6-.7 1.8-1.3.2-1.2.2-1.3-.2-.2-.5-.3l-1.7-.8c-.3-.1-.4-.2-.6.1l-.8 1c-.2.2-.3.2-.6.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.3-.4.7-1.2.1-.2 0-.3 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4z"/></svg>'
SOCIAL_SVG = {
 'Instagram': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/></svg>',
 'Facebook': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21z"/></svg>',
 'X': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.8 3h3l-6.6 7.6L22 21h-6.1l-4.8-6.3L5.6 21h-3l7.1-8.1L2.3 3h6.2l4.3 5.7zm-1 16.2h1.7L7.3 4.7H5.5z"/></svg>',
 'YouTube': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4a2.5 2.5 0 0 0-1.8 1.8C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8c1.6.4 7.8.4 7.8.4s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15.1V8.9l5.2 3.1z"/></svg>',
 'LinkedIn': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zm6.5 0h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.1c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/></svg>',
 'WhatsApp': CHAT,
}
SOCIAL_SVG = {k: v.replace('<svg viewBox="0 0 24 24"', '<svg width="18" height="18" viewBox="0 0 24 24"', 1) for k, v in SOCIAL_SVG.items()}

def wa(text): return f"https://wa.me/{SITE['whatsapp']}?text=" + quote(text)
def tail(): return "" if PRETTY else "index.html"
import hashlib
from katalog import KAT, build as build_catalog
from yorum import section as review_section, js_strings as review_js
def _v(f): return hashlib.md5(open(os.path.join(BASE, "static", f), "rb").read()).hexdigest()[:8]
VER = {"css": _v("style.css"), "js": _v("app.js"), "kcss": _v("katalog.css")}

# ---------- sayfa bağlamı ----------
class Pg:
    """Bir sayfanın dil, derinlik ve yol bilgisi. path: dil köküne göre ('' , 'urunler', 'kat/urun')."""
    def __init__(s, L, path):
        s.L, s.path, s.T, s.m = L, path, M[L].UI, M[L]
        depth = len([x for x in path.split("/") if x])
        s.R = "../" * depth            # dil kökü
        s.A = "../" * (depth + 1)      # site kökü
    def h(s, *parts):
        p = "/".join(x for x in parts if x)
        return s.R + (p + "/" if p else "") + tail() or "./"
    def other(s, L2):
        return s.A + L2 + "/" + (s.path + "/" if s.path else "") + tail()
    def url(s, *parts, L=None):
        p = "/".join(x for x in parts if x)
        return f"{D}/{L or s.L}/" + (p + "/" if p else "")

LOGO = '<svg viewBox="0 0 100 100" aria-hidden="true"><rect x="0" y="0" width="100" height="100" rx="22.00" fill="#ee6510"/><polygon points="21.00,78.00 21.00,24.00 33.00,24.00 33.00,78.00" fill="#fff"/><polygon points="21.00,24.00 33.00,24.00 50.00,49.00 50.00,66.00" fill="#ffd2b0"/><polygon points="79.00,24.00 67.00,24.00 50.00,49.00 50.00,66.00" fill="#fff"/><polygon points="67.00,24.00 79.00,24.00 79.00,78.00 67.00,78.00" fill="#ffd2b0"/></svg>'
WA_SVG = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C9 3 3.4 8.6 3.4 15.6c0 2.3.6 4.5 1.8 6.4L3 29l7.2-2.2c1.8 1 3.8 1.5 5.8 1.5 7 0 12.6-5.6 12.6-12.6S23 3 16 3zm0 23c-1.9 0-3.7-.5-5.3-1.5l-.4-.2-4.3 1.3 1.4-4.2-.3-.4a10.4 10.4 0 1 1 8.9 5zm5.7-7.8c-.3-.2-1.8-.9-2.1-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.5 8.5 0 0 1-4.2-3.7c-.3-.5.3-.5.9-1.6.1-.2 0-.4 0-.5l-1-2.3c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4s-1 1-1 2.5 1.1 2.9 1.2 3.1 2.1 3.2 5.1 4.5c1.9.8 2.6.9 3.6.7.6-.1 1.8-.7 2-1.4s.3-1.3.2-1.4-.3-.2-.6-.3z"/></svg>'
SPARK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>'
GLOBE = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/></svg>'

def org_ld(L):
    return {"@context": "https://schema.org", "@type": ["Organization", "LocalBusiness"], "@id": D + "/#org", "name": SITE["brand"], "legalName": SITE["legal"],
            "url": D + "/", "logo": D + "/static/logo/metursan-logo-512.png", "foundingDate": SITE["founded"], "email": SITE["email"], "telephone": SITE["phone1"],
            "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "postalCode": SITE["postal"], "addressLocality": "Sancaktepe", "addressRegion": "İstanbul", "addressCountry": "TR"},
            "contactPoint": [{"@type": "ContactPoint", "telephone": SITE["phone1"], "contactType": "sales", "availableLanguage": ["tr", "en", "de", "fr", "ar"]}],
            "areaServed": ["TR", "EU", "MENA"], "sameAs": ["https://www.huzurpano.com/"] + [u for _, _, u, _ in SOCIAL]}

def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>"
def crumbs_ld(items): return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]})
def faq_ld(qa, L): return ld({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": L, "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
def faq_html(qa): return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa) + "</div>"

def head(g, title, desc, extra="", og_img=None, cur="", noindex=False):
    T = g.T
    og = og_img or img(CATEGORIES[0]["cover"], 1200)
    canon = g.url(g.path) if g.path else g.url()
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{D}/{l}/{g.path + "/" if g.path else ""}">' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{D}/tr/{g.path + "/" if g.path else ""}">'
    nav = [("urunler", T["nav_products"]), ("hizmetler", T["nav_services"]), ("hakkimizda", T["nav_about"]), ("iletisim", T["nav_contact"])]
    lis = "".join(f'<li><a href="{g.h(s)}"{" aria-current=page" if cur == s else ""}>{e(t)}</a></li>' for s, t in nav)
    langs = "".join(f'<a href="{g.other(l)}" hreflang="{l}" lang="{l}"{" aria-current=true" if l == g.L else ""}>{e(M[l].NAME)}</a>' for l in LANGS)
    js = dict(T["js"], lang=g.L, rtl=M[g.L].DIR == "rtl", rv=review_js(g.L))
    font = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap">' if g.L == "ar" else ""
    return f"""<!doctype html>
<html lang="{g.L}" dir="{M[g.L].DIR}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">{alts}
<meta name="robots" content="{'noindex' if noindex else 'index,follow,max-image-preview:large'}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Metursan">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{og}"><meta property="og:locale" content="{M[g.L].LOCALE}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#fbfbfd">
<link rel="icon" href="{g.A}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="text/markdown" title="LLM" href="{g.A}llms.txt">
<link rel="alternate" type="application/json" title="Products" href="{g.R}products.json">
<link rel="preconnect" href="https://wsrv.nl" crossorigin>{font}
<link rel="stylesheet" href="{g.A}static/style.css?v={VER['css']}">
{ld(org_ld(g.L))}
{extra}
<script>window.T={json.dumps(js, ensure_ascii=False)}</script>
</head>
<body data-root="{g.R}" data-pretty="{1 if PRETTY else 0}">
<a class="skip" href="#main">{e(T['skip'])}</a>
<header class="nav"><div class="wrap">
<a class="logo" href="{g.h()}" aria-label="Metursan">{LOGO}<span dir="ltr">MET<b>URSAN</b></span></a>
<nav aria-label="Menu"><ul>{lis}</ul></nav>
<div class="srch" role="search">
 <label class="srch-f"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
 <span class="sr">{e(T['search_label'])}</span><input id="q" type="search" placeholder="{e(T['search_ph'])}" autocomplete="off" enterkeyhint="search"><kbd>/</kbd></label>
 <div class="srch-pop" id="qpop" hidden><ul class="srch-res" id="qres"></ul></div>
</div>
<details class="langsel"><summary aria-label="{e(T['lang'])}">{GLOBE}<span>{g.L.upper()}</span></summary><div class="menu">{langs}</div></details>
<a class="btn btn-p btn-sm" href="{wa(T['wa_quote'])}" target="_blank" rel="noopener">{e(T['quote'])}</a>
<button class="burger" aria-label="{e(T['menu'])}" aria-expanded="false"><span></span><span></span></button>
</div></header>
<main id="main">
"""

def foot(g):
    T = g.T
    cats = "".join(f'<li><a href="{g.h(c["slug"])}">{e(ct(c, g.L)[0])}</a></li>' for c in CATEGORIES[:6])
    srv = "".join(f'<li><a href="{g.h("hizmetler")}#s{i+1}">{e(n)}</a></li>' for i, (n, _) in enumerate(g.m.SERVICES))
    langs = " · ".join(f'<a href="{g.other(l)}" lang="{l}">{e(M[l].NAME)}</a>' for l in LANGS)
    return f"""</main>
<footer><div class="wrap">
<div class="fgrid">
 <div><a class="logo" href="{g.h()}">{LOGO}<span dir="ltr">MET<b>URSAN</b></span></a>
 <p style="margin-top:12px;max-width:320px">{e(F(T['f_about'], **CTX))}</p>
 <div class="social">{"".join(f'<a class="s-{t}" href="{u}" aria-label="{n}" title="{n}" rel="noopener me" target="_blank">{SOCIAL_SVG[k]}</a>' for n, t, u, k in SOCIAL)}<a class="s-whatsapp" href="https://wa.me/{SITE['whatsapp']}" aria-label="WhatsApp" title="WhatsApp" rel="noopener" target="_blank">{SOCIAL_SVG['WhatsApp']}</a></div></div>
 <div><h2>{e(T['nav_products'])}</h2><ul>{cats}<li><a href="{g.h('urunler')}">{e(T['all'])}</a></li></ul></div>
 <div><h2>{e(T['nav_services'])}</h2><ul>{srv}</ul></div>
 <div><h2>{e(T['nav_contact'])}</h2><ul><li><a href="tel:{SITE['tel']}" dir="ltr">{SITE['phone1']}</a></li><li><a href="https://wa.me/{SITE['whatsapp']}">WhatsApp <span dir="ltr">{SITE['whatsapp_display']}</span></a></li><li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li><li>{e(SITE['street'])}, {SITE['postal']} {e(SITE['city'])}</li><li><a href="{g.h('katalog')}">{e(KAT[g.L]['title'])} (PDF)</a></li><li><a href="{g.A}llms.txt">{e(T['f_llms'])}</a></li></ul></div>
</div>
<div class="bottom"><span>© {date.today().year} Metursan · {SITE['legal']}. {e(T['f_rights'])}</span><span class="langs">{langs}</span></div>
<p style="padding-top:10px">{e(T['f_disc'])}</p>
</div></footer>
<a class="wa" href="{wa(T['wa_hello'])}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_SVG}</a>
<button class="ai-fab" id="aifab" aria-haspopup="dialog">{SPARK}<span>{e(T['ai_fab'])}</span></button>
<section class="ai" id="ai" role="dialog" aria-label="{e(T['ai_dialog'])}" hidden>
 <div class="ai-h"><div class="av">{SPARK}</div><div><b>{e(T['ai_title'])}</b><small>{e(T['ai_sub'])}</small></div><button id="aix" aria-label="{e(T['ai_close'])}">✕</button></div>
 <div class="ai-b" id="aib" aria-live="polite"></div>
 <form class="ai-f" id="aif"><input id="aii" placeholder="{e(T['ai_ph'])}" autocomplete="off" aria-label="{e(T['ai_ph'])}"><button aria-label="{e(T['ai_send'])}">↑</button></form>
</section>
<script src="{g.A}static/app.js?v={VER['js']}" defer></script>
</body></html>"""

def card(g, p, eb=None, w=640):
    n, s = pt(p, g.L)[:2]
    return (f'<a class="st-card st-sm" href="{g.h(p["cat"], p["slug"])}"><div class="tx"><span class="eb" dir="ltr">{e(eb or p["code"])}</span>'
            f'<h3>{e(n)}</h3><p class="pr">{e(s)}</p></div>'
            f'<img src="{img(p["imgs"][0], w)}" alt="{e(n)}" loading="lazy" decoding="async" width="{w}" height="{int(w*.75)}"></a>')

def row(inner, pads=True):
    pd = '<div class="wrap st-pads"><button class="st-pad" data-dir="-1" aria-label="‹">‹</button><button class="st-pad" data-dir="1" aria-label="›">›</button></div>' if pads else ""
    return f'<div class="st-row">{inner}</div>{pd}'

def icons(g, cur=None):
    a = "".join(f'<a href="{g.h(c["slug"])}"{" class=cur aria-current=page" if cur == c["slug"] else ""}><span class="ic"><img src="{img(c["cover"], 220)}" alt="" loading="lazy" width="104" height="104"></span><b>{e(ct(c, g.L)[0])}</b></a>' for c in CATEGORIES)
    return f'<nav class="st-icons" aria-label="{e(g.T["nav_products"])}">{a}</nav>'

def sec(t, inner, extra_cls="", link=None):
    em, rest = t if isinstance(t, tuple) else (t, "")
    l = f'<a href="{link[0]}">{e(link[1])} ›</a>' if link else ""
    return f'<section class="st-sec {extra_cls}"><div class="wrap"><h2 class="st-h2 st-hl"><em>{e(em)}</em> {e(rest)}{l}</h2></div>{inner}</section>'

def why_row(g):
    out = []
    for i, (eb, h, p) in enumerate(g.m.WHY):
        lk = f'<a href="{wa(g.T["wa_expert"])}" target="_blank" rel="noopener">{e(g.T["wa_write"])}</a>' if i == 0 else ""
        out.append(f'<div class="st-card st-tc"><div class="tx"><span class="eb n">{e(eb)}</span><h3>{e(h)}</h3><p>{e(p)}</p>{lk}</div></div>')
    return sec(g.T["s_why"], row("".join(out)), "st-acc")

def steps_row(g):
    out = "".join(f'<div class="st-card st-tc"><div class="tx"><span class="num">{i+1}</span><h3>{e(h)}</h3><p>{e(p)}</p></div></div>' for i, (h, p) in enumerate(g.m.STEPS))
    return sec(g.T["s_steps"], row(out, False))

def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(content)

def crumbs(g, items):
    li = "".join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in items[:-1]) + f'<li aria-current="page">{e(items[-1][0])}</li>'
    return f'<div class="wrap crumbs"><ol>{li}</ol></div>'

# ---------- sayfalar ----------
def page_home(L):
    g = Pg(L, ""); T = g.T
    cats = "".join(f'<a class="st-card" href="{g.h(c["slug"])}"><div class="tx"><span class="eb n">{len(c["items"])} {e(T["model"])}</span><h3>{e(ct(c, L)[0])}</h3><p>{e(ct(c, L)[1])}</p></div><img src="{img(c["cover"], 800)}" alt="{e(ct(c, L)[0])}" loading="lazy" width="800" height="600"></a>' for c in CATEGORIES)
    cats += f'<a class="st-card st-more" href="{g.h("urunler")}"><div class="tx"><span class="eb">{len(BASEP)} {e(T["model"])}</span><h3>{e(T["all"])}</h3><p>{e(T["all_p"])}</p></div><span class="arr">→</span></a>'
    newest = "".join(card(g, p, eb=T["new"]) for p in NEWEST)
    def catrow(slug, t): return sec(t, row("".join(card(g, p) for p in CAT[slug]["items"])), link=(g.h(slug), T["see_all"]))
    srv = "".join(f'<div class="st-card st-tc"><div class="tx"><svg class="ico" viewBox="0 0 24 24"><path d="M4 20h16M6 16l6-12 6 12M9 11h6"/></svg><h3>{e(n)}</h3><p>{e(t)}</p><a href="{g.h("hizmetler")}#s{i+1}">{e(T["details"])}</a></div></div>' for i, (n, t) in enumerate(g.m.SERVICES))
    bimgs = [CAT["kiosk-ve-totem"]["items"][0]["imgs"][0], CAT["gemi-ve-kontrol-konsollari"]["cover"], CAT["endustriyel-kabinler"]["items"][2]["imgs"][0]]
    banner = f"""<div class="wrap"><div class="st-banner"><div><span class="eb">{e(T['b_eb'])}</span><h3>{e(T['b_h'])}</h3><p>{e(T['b_p'])}</p><button class="lnk" data-ai>{e(T['b_btn'])} {SPARK.replace('<svg', '<svg width=18 height=18')}</button></div>
<div class="st-bk" aria-hidden="true">{''.join(f'<img class="p{i}" src="{img(x, 640)}" alt="" loading="lazy">' for i, x in enumerate(bimgs))}</div></div></div>"""
    ql = "".join(f'<a href="{g.h(c["slug"])}">{e(ct(c, L)[0])}</a>' for c in CATEGORIES)
    body = f"""<div class="st">
<div class="wrap st-top"><h1 class="st-h1"><span dir="ltr">Metursan</span><small>{e(T['tagline'])}</small></h1>
<div class="st-intro"><p>{e(T['intro'])}</p><a href="{wa(T['wa_expert'])}" target="_blank" rel="noopener">{e(T['expert'])}</a><a href="#" data-ai>{e(T['ask_ai'])}</a></div></div>
{icons(g)}
<div class="wrap st-pads" style="margin-top:-18px"><button class="st-pad" data-dir="-1" aria-label="‹">‹</button><button class="st-pad" data-dir="1" aria-label="›">›</button></div>
{sec(T['s_cats'], row(cats))}
{sec(T['s_new'], row(newest), "st-acc")}
{catrow("kiosk-ve-totem", T['s_kiosk'])}
{catrow("gemi-ve-kontrol-konsollari", T['s_ship'])}
{catrow("endustriyel-kabinler", T['s_cab'])}
{sec(T['s_box'], row("".join(card(g, p) for p in CAT["elektrik-panolari"]["items"] + CAT["cihaz-kutulari"]["items"] + CAT["sarj-istasyonu-kutulari"]["items"])))}
{banner}
{why_row(g)}
{sec(T['s_srv'], row(srv, False))}
{steps_row(g)}
<section class="st-sec"><div class="wrap"><h2 class="st-h2"><em>{e(T['s_ql'])}</em></h2><div class="st-ql">{ql}<a href="{g.h('urunler')}">{e(T['all'])}</a><a href="{g.h('iletisim')}">{e(T['nav_contact'])}</a></div></div></section>
<section class="st-sec st-faq"><div class="wrap"><h2 class="st-h2"><em>{e(T['s_faq'])}</em></h2>{faq_html(g.m.GEN_FAQ)}</div></section>
<section class="st-sec"><div class="wrap"><h2 class="st-h2"><em>{e(T['cta_h'])}</em> {e(T['cta_p'])}</h2>
<div class="pd-btns"><a class="btn btn-p" href="{wa(T['wa_quote'])}" target="_blank" rel="noopener">{e(T['cta_wa'])}</a><a class="btn btn-s" href="tel:{SITE['tel']}">{e(T['cta_call'])} · <span dir="ltr">{SITE['phone1']}</span></a><a class="btn btn-s" href="mailto:{SITE['email']}">{e(T['cta_mail'])}</a></div></div></section>
</div>"""
    extra = ld({"@context": "https://schema.org", "@type": "WebSite", "@id": D + "/#web", "url": D + "/", "name": "Metursan", "inLanguage": LANGS, "publisher": {"@id": D + "/#org"},
                "potentialAction": {"@type": "SearchAction", "target": f"{D}/{L}/urunler/?q={{search_term_string}}", "query-input": "required name=search_term_string"}}) + faq_ld(g.m.GEN_FAQ, L)
    write(f"{L}/index.html", head(g, T["m_home_t"], T["m_home_d"], extra) + body + foot(g))

def page_all(L):
    g = Pg(L, "urunler"); T = g.T
    blocks = "".join(sec((ct(c, L)[0] + ".", f"{len(c['items'])} {T['models']}"), row("".join(card(g, p) for p in c["items"])), link=(g.h(c["slug"]), T["see_all"])) for c in CATEGORIES)
    body = f"""<div class="st">{crumbs(g, [(T['home'], g.h()), (T['all'], '')])}
<div class="wrap st-top st-top-s"><h1 class="st-h1 ink">{e(T['all'])}</h1><div class="st-intro"><span class="cnt">{len(BASEP)} {e(T['models'])} · {len(CATEGORIES)} {e(T['cats_n'])}</span><p>{e(T['not_found'])}</p><a href="#" data-ai>{e(T['tell_ai'])}</a> <a href="{g.h('katalog')}">{e(KAT[L]['pdf'])} ↓</a></div></div>
{icons(g)}{blocks}{why_row(g)}</div>"""
    extra = crumbs_ld([(T["home"], g.url()), (T["all"], g.url("urunler"))]) + ld({"@context": "https://schema.org", "@type": "ItemList", "numberOfItems": len(BASEP),
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": g.url(p["cat"], p["slug"]), "name": pt(p, L)[0]} for i, p in enumerate(BASEP)]})
    write(f"{L}/urunler/index.html", head(g, f"{T['all']} · Metursan", F(T["m_all_d"], n=len(BASEP)), extra, cur="urunler") + body + foot(g))

def page_cat(L, c):
    g = Pg(L, c["slug"]); T = g.T
    name, short, intro, faq = ct(c, L)
    grid = "".join(card(g, p) for p in c["items"])
    body = f"""<div class="st">{crumbs(g, [(T['home'], g.h()), (T['nav_products'], g.h('urunler')), (name, '')])}
<div class="wrap st-top st-top-s"><h1 class="st-h1 ink">{e(name)}</h1><div class="st-intro"><span class="cnt">{len(c['items'])} {e(T['models'])}</span><p>{e(short)}</p><a href="{wa(F(T['wa_cat'], cat=name))}" target="_blank" rel="noopener">{e(T['cat_quote'])}</a><a href="#" data-ai>{e(T['ask_ai2'])}</a></div></div>
{icons(g, c['slug'])}
<section class="st-sec" id="modeller"><div class="wrap"><h2 class="st-h2"><em>{e(T['all_models'])}</em> {e(name)}</h2><p class="lead2">{e(intro)}</p><div class="st-grid">{grid}</div></div></section>
<section class="st-sec st-faq"><div class="wrap"><h2 class="st-h2"><em>{e(T['faq_t'])}</em> {e(name)}</h2>{faq_html(faq)}</div></section>
{why_row(g)}</div>"""
    extra = crumbs_ld([(T["home"], g.url()), (T["nav_products"], g.url("urunler")), (name, g.url(c["slug"]))]) + faq_ld(faq, L) + ld({
        "@context": "https://schema.org", "@type": "CollectionPage", "name": name, "description": intro, "url": g.url(c["slug"]), "inLanguage": L,
        "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": g.url(c["slug"], p["slug"]), "name": pt(p, L)[0]} for i, p in enumerate(c["items"])]}})
    write(f"{L}/{c['slug']}/index.html", head(g, f"{name} · Metursan", F(T["m_cat_d"], cat=name, short=short), extra, img(c["cover"], 1200)) + body + foot(g))

def page_prod(L, p):
    c = CAT[p["cat"]]
    g = Pg(L, f"{c['slug']}/{p['slug']}"); T = g.T
    cname, _, _, cfaq = ct(c, L)
    name, short, feats, uses, about = pt(p, L)
    main = p["imgs"][0]
    thumbs = "".join(f'<button type="button" data-src="{img(x, 1200)}"{" aria-current=true" if i == 0 else ""} aria-label="{i+1}"><img src="{img(x, 200)}" alt="" loading="lazy" width="84" height="64"></button>' for i, x in enumerate(p["imgs"])) if len(p["imgs"]) > 1 else ""
    fl = "".join(f"<li>{e(f)}</li>" for f in list(feats) + [T["feat_x"]])
    ul = "".join(f"<li>{e(u)}</li>" for u in uses)
    tl = "".join(f"<li>{e(x)}</li>" for x in T["tech_l"])
    vid = f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{p["yt"]}" title="{e(name)} {e(T["video"])}" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>' if p["yt"] else ""
    rel = [x for x in c["items"] if x["slug"] != p["slug"]]
    if len(rel) < 4: rel += [x for x in BASEP if x["cat"] != c["slug"]][: 6 - len(rel)]
    kw = dict(CTX, name=name, code=p["code"])
    qa = [(F(T["pq1"], **kw), F(T["pa1"], **kw)), (F(T["pq2"], **kw), F(T["pa2"], **kw))] + list(cfaq[:2])
    body = f"""<div class="st">{crumbs(g, [(T['home'], g.h()), (T['nav_products'], g.h('urunler')), (cname, g.h(c['slug'])), (name, '')])}
<div class="wrap"><article class="pd">
<div class="pd-gal"><div class="pd-main"><img id="pdimg" src="{img(main, 1200)}" alt="{e(name)}" width="1200" height="900" fetchpriority="high"></div><div class="thumbs">{thumbs}</div></div>
<div class="pd-info"><a class="pd-eb" href="{g.h(c['slug'])}">{e(cname)}</a><h1>{e(name)}</h1><p class="pd-code">{e(T['code'])}: <span dir="ltr">{p['code']}</span></p><p class="pd-sum">{e(short)}</p>
<div class="pd-box"><b>{e(T['mtm_b'])}</b><span>{e(T['mtm_s'])}</span></div>
<div class="pd-btns"><a class="btn btn-p" href="{wa(F(T['wa_prod'], **kw))}" target="_blank" rel="noopener">{e(T['p_quote'])}</a><a class="btn btn-s" href="tel:{SITE['tel']}">{e(T['p_call'])}</a><button class="btn btn-s" data-ai="{e(name)}">{e(T['p_ai'])}</button></div>
<h2 class="pd-h">{e(T['feats'])}</h2><ul class="pd-hl">{fl}</ul>
<p class="note">{e(T['note'])}</p></div>
</article>
<div class="pd-more"><div class="pd-about"><h2 class="pd-h" style="margin-top:0">{e(T['about_h'])}</h2><p>{e(about)}</p><p>{e(F(T['about2'], **kw))}</p>{vid}</div>
<aside class="pd-uses"><h3>{e(T['uses'])}</h3><ul>{ul}</ul><h3 style="margin-top:22px">{e(T['tech'])}</h3><ul>{tl}</ul></aside></div>
</div>
{review_section(L, p['slug'], name)}
<section class="st-sec st-faq"><div class="wrap"><h2 class="st-h2"><em>{e(T['faq_t'])}</em> {e(name)}</h2>{faq_html(qa)}</div></section>
{sec(T['same_cat'], row("".join(card(g, x) for x in rel[:12])), link=(g.h(c['slug']), T['see_all']))}
</div>"""
    # Fiyat yayımlanmadığı için Product yerine Service (ölçüye özel imalat): Google "ürün snippet'i" hatası üretmez, bilgi korunur
    prod_ld = {"@context": "https://schema.org", "@type": "Service", "serviceType": cname, "name": name, "description": short + " " + about, "image": [img(x, 1200) for x in p["imgs"]],
               "category": cname, "url": g.url(c["slug"], p["slug"]), "inLanguage": L, "identifier": p["code"], "brand": {"@type": "Brand", "name": "Metursan"},
               "provider": {"@id": D + "/#org"}, "areaServed": ["TR", "EU", "Middle East"],
               "additionalProperty": [{"@type": "PropertyValue", "name": T["mtm_b"], "value": "true"}] + [{"@type": "PropertyValue", "name": T["feats"], "value": f} for f in feats] +
                                     [{"@type": "PropertyValue", "name": T["uses"], "value": u} for u in uses]}
    extra = ld(prod_ld) + crumbs_ld([(T["home"], g.url()), (T["nav_products"], g.url("urunler")), (cname, g.url(c["slug"])), (name, g.url(c["slug"], p["slug"]))]) + faq_ld(qa, L)
    write(f"{L}/{c['slug']}/{p['slug']}/index.html", head(g, f"{name} · {cname} · Metursan", F(T["m_prod_d"], name=name, code=p["code"], short=short), extra, img(main, 1200)) + body + foot(g))

def simple(L, slug, title, desc, inner, cur):
    g = Pg(L, slug); T = g.T
    body = f'<div class="st">{crumbs(g, [(T["home"], g.h()), (title, "")])}{inner(g)}</div>'
    write(f"{L}/{slug}/index.html", head(g, f"{title} · Metursan", desc, crumbs_ld([(T["home"], g.url()), (title, g.url(slug))]), cur=cur) + body + foot(g))

def pages_static(L):
    T = M[L].UI; m = M[L]
    def srv(g):
        items = "".join(f'<div class="st-card st-tc" id="s{i+1}" style="flex:none"><div class="tx"><span class="num">{i+1}</span><h3>{e(n)}</h3><p>{e(t)}</p></div></div>' for i, (n, t) in enumerate(m.SERVICES))
        return f"""<div class="wrap st-top st-top-s"><h1 class="st-h1 ink">{e(T['srv_t'])}</h1><div class="st-intro"><p>{e(T['srv_i'])}</p><a href="{wa(T['wa_fason'])}" target="_blank" rel="noopener">{e(T['srv_l'])}</a></div></div>
<section class="st-sec"><div class="wrap"><div class="st-grid" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr))">{items}</div><p class="lead2" style="margin-top:32px">{e(T['srv_p'])}</p></div></section>{steps_row(g)}{why_row(g)}"""
    def about(g):
        ps = "".join(f"<p>{x}</p>" for x in m.ABOUT)
        return f'<div class="wrap st-top st-top-s"><h1 class="st-h1 ink">{e(T["about_t"])}</h1></div><section class="st-sec" style="padding-top:0"><div class="wrap prose">{ps}</div></section>{why_row(g)}{steps_row(g)}'
    def contact(g):
        q = quote(f"{SITE['street']} {SITE['postal']} {SITE['city']}")
        return f"""<div class="wrap st-top st-top-s"><h1 class="st-h1 ink">{e(T['contact_t'])}</h1><div class="st-intro"><p>{e(T['cta_h'])}</p><a href="{wa(T['wa_quote'])}" target="_blank" rel="noopener">{e(T['cta_wa'])} ↗</a></div></div>
<section class="st-sec" style="padding-top:0"><div class="wrap"><div class="cgrid">
<div class="cbox"><h2>{e(T['c_phone'])}</h2><a href="tel:{SITE['tel']}" dir="ltr">{SITE['phone1']}</a><a href="tel:{SITE['tel2']}" dir="ltr">{SITE['phone2']}</a><a href="tel:{SITE['tel3']}" dir="ltr">{SITE['phone3']}</a></div>
<div class="cbox"><h2>{e(T['c_wa'])}</h2><a href="https://wa.me/{SITE['whatsapp']}" target="_blank" rel="noopener" dir="ltr">{SITE['whatsapp_display']}</a><a href="mailto:{SITE['email']}">{SITE['email']}</a></div>
<div class="cbox"><h2>{e(T['c_addr'])}</h2><p>{e(SITE['street'])}<br>{SITE['postal']} {e(SITE['city'])}</p><a style="font-size:15px;margin-top:8px;color:var(--acc-t)" href="https://www.google.com/maps/search/?api=1&query={q}" target="_blank" rel="noopener">{e(T['c_dir'])}</a></div>
</div><div class="map"><iframe title="{e(T['c_map'])}" loading="lazy" src="https://www.google.com/maps?q={q}&output=embed"></iframe></div></div></section>
<section class="st-sec st-faq"><div class="wrap"><h2 class="st-h2"><em>{e(T['s_faq'])}</em></h2>{faq_html(m.GEN_FAQ[1:])}</div></section>"""
    simple(L, "hizmetler", T["srv_t"], T["m_srv_d"], srv, "hizmetler")
    simple(L, "hakkimizda", T["about_t"], T["m_about_d"], about, "hakkimizda")
    simple(L, "iletisim", T["contact_t"], F(T["m_contact_d"], **CTX), contact, "iletisim")

# ---------- kök sayfalar ----------
def root_files():
    # dil seçici + tarayıcı diline göre yönlendirme
    links = "".join(f'<a href="{l}/{tail()}" hreflang="{l}" lang="{l}">{e(M[l].NAME)}</a>' for l in LANGS)
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{D}/{l}/">' for l in LANGS)
    write("index.html", f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Metursan · Metal kabin, pano ve kiosk imalatı · Metal enclosures & kiosks</title>
<meta name="description" content="Metursan: ölçüye özel metal kabin, pano, kiosk ve konsol imalatı. Made-to-measure metal enclosures, panels and kiosks from Istanbul since 1994.">
<link rel="canonical" href="{D}/">{alts}<link rel="alternate" hreflang="x-default" href="{D}/">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="static/style.css?v={VER['css']}">{ld(org_ld('tr'))}
<script>(function(){{try{{if(location.search.indexOf('stay')>-1||sessionStorage.getItem('mt-stay'))return;var L=['tr','en','de','fr','ar'],n=(navigator.languages||[navigator.language||'tr']);for(var i=0;i<n.length;i++){{var c=(n[i]||'').slice(0,2).toLowerCase();if(L.indexOf(c)>-1){{location.replace(c+'/{tail()}');return}}}}location.replace('en/{tail()}')}}catch(e){{}}}})();</script>
</head><body><main class="chooser"><div><a class="logo" href="./">{LOGO}<span>MET<b>URSAN</b></span></a>
<p style="margin-top:14px;color:var(--mute)">Metal kabin, pano ve kiosk imalatı · Metal enclosures, panels and kiosks</p>
<div class="list">{links}</div></div></main></body></html>""")
    # 404 (Türkçe + dil bağlantıları)
    g = Pg("tr", ""); g.R = "/tr/"; g.A = "/"
    if not PRETTY: g.R, g.A = "tr/", ""
    T = g.T
    body = f'<div class="st"><div class="wrap st-top"><h1 class="st-h1">404<small>{e(T["e404"])}</small></h1><div class="st-intro"><p>{e(T["e404p"])}</p><a href="{g.R}">{e(T["back"])}</a>' + "".join(f'<a href="{g.A}{l}/">{e(M[l].NAME)}</a>' for l in LANGS if l != "tr") + '</div></div></div>'
    write("404.html", head(g, "404 · Metursan", T["e404"], noindex=True) + body + foot(g))
    write("favicon.svg", LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))

# ---------- yapay zekâ / makine okunur dosyalar ----------
def machine_files():
    for L in LANGS:
        m = M[L]; T = m.UI
        data = {"brand": "Metursan", "manufacturer": SITE["legal"], "language": L, "url": f"{D}/{L}/", "updated": TODAY,
                "contact": {"phone": SITE["phone1"], "whatsapp": "+" + SITE["whatsapp"], "email": SITE["email"], "address": f"{SITE['street']}, {SITE['postal']} {SITE['city']}, Türkiye"},
                "categories": [{"slug": c["slug"], "name": ct(c, L)[0], "summary": ct(c, L)[1], "description": ct(c, L)[2], "url": f"{D}/{L}/{c['slug']}/", "count": len(c["items"]),
                                "faq": [{"q": q, "a": a} for q, a in ct(c, L)[3]]} for c in CATEGORIES],
                "products": [{"code": p["code"], "slug": p["slug"], "name": pt(p, L)[0], "category": p["cat"], "category_name": ct(CAT[p["cat"]], L)[0], "summary": pt(p, L)[1],
                              "features": list(pt(p, L)[2]), "uses": list(pt(p, L)[3]), "description": pt(p, L)[4], "url": f"{D}/{L}/{p['cat']}/{p['slug']}/",
                              "path": p["cat"] + "/" + p["slug"] + "/", "image": img(p["imgs"][0], 400), "images": [img(x, 1200) for x in p["imgs"]], "made_to_measure": True} for p in BASEP],
                "faq": [{"q": q, "a": a} for q, a in m.GEN_FAQ]}
        write(f"{L}/products.json", json.dumps(data, ensure_ascii=False, indent=1))
        Fl = [f"# Metursan ({m.NAME})", "", f"{D}/{L}/ · {TODAY}", ""]
        for c in CATEGORIES:
            n, s, intro, faq = ct(c, L)
            Fl += [f"## {n}", "", intro, "", f"URL: {D}/{L}/{c['slug']}/", ""] + [x for q, a in faq for x in (f"**{q}**", a, "")]
            for p in c["items"]:
                pn, ps, pf, pu, pa = pt(p, L)
                Fl += [f"### {pn} ({p['code']})", "", ps, "", pa, "", "- " + "\n- ".join(pf), "", T["uses"] + ": " + ", ".join(pu), f"URL: {D}/{L}/{p['cat']}/{p['slug']}/", ""]
        Fl += ["## FAQ", ""] + [x for q, a in m.GEN_FAQ for x in (f"**{q}**", a, "")]
        write(f"{L}/llms-full.txt", "\n".join(Fl))
    en = M["en"]
    Lx = ["# Metursan", "", f"> Metursan is the metal enclosure brand of {SITE['legal']} (Istanbul, Türkiye; founded {SITE['founded']}). It designs and manufactures made-to-measure kiosk and totem housings, electrical and machine panels, electronic enclosures, EV charger housings, marine and laboratory consoles, industrial cabins, machine frames, stainless/medical products, workbenches and cabinets. {len(BASEP)} models in {len(CATEGORIES)} categories, produced in its own {SITE['factory_m2'].replace('.', ',')} m² factory in Sancaktepe, Istanbul. Website in Turkish, English, German, French and Arabic.", "",
          "## Key facts", "", f"- Manufacturer: {SITE['legal']} (brand: Metursan), since {SITE['founded']}, Istanbul, Türkiye", "- All products are made to measure; material (mild steel, stainless 304/316, aluminium), size and colour chosen per project",
          "- In-house: CNC laser cutting, CNC punching, CNC bending, MIG/MAG and TIG welding, powder coating, installation", "- Prototype to series; delivery to Türkiye, Europe and the Middle East", "- Prices are not published; quotes per project",
          f"- Contact: {SITE['phone1']} · WhatsApp {SITE['whatsapp_display']} · {SITE['email']}", f"- Address: {SITE['street']}, {SITE['postal']} {SITE['city']}, Türkiye", "", "## Languages", ""]
    Lx += [f"- [{M[l].NAME}]({D}/{l}/) · [products.json]({D}/{l}/products.json) · [llms-full.txt]({D}/{l}/llms-full.txt)" for l in LANGS]
    Lx += ["", "## Categories (EN)", ""] + [f"- [{ct(c, 'en')[0]}]({D}/en/{c['slug']}/): {ct(c, 'en')[1]} ({len(c['items'])} models)" for c in CATEGORIES]
    Lx += ["", "## Products (EN)", ""] + [f"- [{pt(p, 'en')[0]}]({D}/en/{p['cat']}/{p['slug']}/) ({p['code']}): {pt(p, 'en')[1]}" for p in BASEP]
    Lx += ["", "## Ürünler (TR)", ""] + [f"- [{pt(p, 'tr')[0]}]({D}/tr/{p['cat']}/{p['slug']}/) ({p['code']}): {pt(p, 'tr')[1]}" for p in BASEP]
    write("llms.txt", "\n".join(Lx) + "\n")
    # sitemap (hreflang alternatifleriyle)
    paths = [""] + ["urunler", "hizmetler", "hakkimizda", "iletisim", "katalog"] + [c["slug"] for c in CATEGORIES] + [f"{p['cat']}/{p['slug']}" for p in BASEP]
    pim = {f"{p['cat']}/{p['slug']}": p["imgs"][:5] for p in BASEP}
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for pth in paths:
        alt = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{D}/{l}/{pth + "/" if pth else ""}"/>' for l in LANGS)
        ims = "".join(f"<image:image><image:loc>{e(img(x, 1200))}</image:loc></image:image>" for x in pim.get(pth, []))
        for l in LANGS:
            sm.append(f"<url><loc>{D}/{l}/{pth + '/' if pth else ''}</loc><lastmod>{TODAY}</lastmod>{alt}{ims}</url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm))
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot", "Googlebot"]
    write("robots.txt", "User-agent: *\nAllow: /\nDisallow: /yonetim\nDisallow: /api/\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {D}/sitemap.xml\n# LLM: {D}/llms.txt\n")
    write("_headers", "/static/*\n  Cache-Control: public, max-age=31536000, immutable\n/*.json\n  Access-Control-Allow-Origin: *\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")

if __name__ == "__main__":
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(BASE, "static"), os.path.join(OUT, "static"))
    # root/ klasöründeki dosyalar (arama motoru doğrulama dosyaları vb.) sitenin köküne kopyalanır
    if os.path.isdir(os.path.join(BASE, "root")):
        for f in os.listdir(os.path.join(BASE, "root")): shutil.copy(os.path.join(BASE, "root", f), os.path.join(OUT, f))
    for L in LANGS:
        page_home(L); page_all(L); pages_static(L)
        for c in CATEGORIES: page_cat(L, c)
        for p in BASEP: page_prod(L, p)
        build_catalog(L, dict(M=M, SITE=SITE, CATEGORIES=CATEGORIES, D=D, LANGS=LANGS, ct=ct, pt=pt, img=img, write=write, MARK=LOGO, ld=ld, VER=VER))
    root_files(); machine_files()
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print(f"OK: {len(LANGS)} dil × {len(BASEP)} ürün, {n} dosya -> {OUT} (pretty={PRETTY})")
