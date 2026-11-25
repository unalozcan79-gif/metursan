"""A4 baskıya hazır ürün katalogları: /{dil}/katalog/  (build.py tarafından çağrılır)"""
import json
from html import escape as e

KAT = {
 "tr": dict(title="Ürün Kataloğu", sub="Ölçüye özel metal kabin, pano, kiosk ve konsol imalatı", pdf="PDF indir / Yazdır", back="metursan.com", contents="İçindekiler",
            models="model", feats="Özellikler", uses="Kullanım alanları", about="Hakkımızda", why="Neden Metursan?", services="Üretim imkânlarımız",
            cta="Projenize özel teklif için bize ulaşın", cta2="Tüm ürünler ölçüye özel üretilir; malzeme, ölçü, sac kalınlığı ve RAL rengi projeye göre belirlenir.",
            more="Ayrıntılar ve tüm fotoğraflar", page="Sayfa", tagline="METAL ÜRETİM SANAYİ", loading="Görseller yükleniyor…",
            hint="İpucu: Yazdır penceresinde Hedef “PDF olarak kaydet”, Kağıt A4, Kenar boşlukları “Yok” ve “Arka plan grafikleri” açık olsun.", lang="Dil", meta="Metursan ürün kataloğu: {n} model, {c} kategori. Ölçüye özel metal kabin, pano, kiosk ve konsol imalatı. PDF olarak indirin."),
 "en": dict(title="Product Catalogue", sub="Made-to-measure metal enclosures, panels, kiosks and consoles", pdf="Download PDF / Print", back="metursan.com", contents="Contents",
            models="models", feats="Features", uses="Applications", about="About us", why="Why Metursan?", services="Production capabilities",
            cta="Contact us for a project-specific quote", cta2="Every product is made to measure; material, dimensions, sheet thickness and RAL colour are set per project.",
            more="Details and all photos", page="Page", tagline="METAL MANUFACTURING INDUSTRY", loading="Loading images…",
            hint="Tip: in the print dialog choose “Save as PDF”, paper A4, margins “None” and enable “Background graphics”.", lang="Language", meta="Metursan product catalogue: {n} models in {c} categories. Made-to-measure metal enclosures, panels, kiosks and consoles. Download as PDF."),
 "de": dict(title="Produktkatalog", sub="Maßgefertigte Metallgehäuse, Schaltschränke, Kioske und Konsolen", pdf="PDF herunterladen / Drucken", back="metursan.com", contents="Inhalt",
            models="Modelle", feats="Merkmale", uses="Einsatzbereiche", about="Über uns", why="Warum Metursan?", services="Fertigungskompetenzen",
            cta="Fordern Sie Ihr projektbezogenes Angebot an", cta2="Alle Produkte werden nach Maß gefertigt; Material, Abmessungen, Blechstärke und RAL-Farbe richten sich nach Ihrem Projekt.",
            more="Details und alle Fotos", page="Seite", tagline="METALLFERTIGUNG", loading="Bilder werden geladen…",
            hint="Tipp: Im Druckdialog „Als PDF speichern“, Papier A4, Ränder „Keine“ und „Hintergrundgrafiken“ aktivieren.", lang="Sprache", meta="Metursan Produktkatalog: {n} Modelle in {c} Kategorien. Maßgefertigte Metallgehäuse, Schaltschränke, Kioske und Konsolen. Als PDF herunterladen."),
 "fr": dict(title="Catalogue produits", sub="Coffrets, armoires, bornes et pupitres métalliques sur mesure", pdf="Télécharger le PDF / Imprimer", back="metursan.com", contents="Sommaire",
            models="modèles", feats="Caractéristiques", uses="Applications", about="À propos", why="Pourquoi Metursan ?", services="Moyens de production",
            cta="Contactez-nous pour un devis adapté à votre projet", cta2="Tous les produits sont fabriqués sur mesure ; matériau, dimensions, épaisseur de tôle et teinte RAL sont définis selon le projet.",
            more="Détails et toutes les photos", page="Page", tagline="INDUSTRIE MÉTALLURGIQUE", loading="Chargement des images…",
            hint="Astuce : dans la fenêtre d’impression, choisissez « Enregistrer au format PDF », papier A4, marges « Aucune » et activez « Graphiques d’arrière-plan ».", lang="Langue", meta="Catalogue Metursan : {n} modèles en {c} catégories. Coffrets, armoires, bornes et pupitres métalliques sur mesure. Télécharger en PDF."),
 "ar": dict(title="كتالوج المنتجات", sub="تصنيع الخزائن واللوحات والأكشاك ووحدات التحكم المعدنية حسب المقاس", pdf="تنزيل PDF / طباعة", back="metursan.com", contents="المحتويات",
            models="طراز", feats="المواصفات", uses="مجالات الاستخدام", about="من نحن", why="لماذا ميتورسان؟", services="إمكانات الإنتاج",
            cta="تواصل معنا للحصول على عرض سعر خاص بمشروعك", cta2="تُصنع جميع المنتجات حسب المقاس؛ ويُحدَّد المعدن والأبعاد وسماكة الصاج ولون RAL وفق المشروع.",
            more="التفاصيل وجميع الصور", page="صفحة", tagline="صناعة المعادن", loading="جارٍ تحميل الصور…",
            hint="نصيحة: في نافذة الطباعة اختر «حفظ بتنسيق PDF»، والورق A4، والهوامش «بلا»، وفعّل «رسومات الخلفية».", lang="اللغة", meta="كتالوج ميتورسان: {n} طرازًا في {c} فئات. خزائن ولوحات وأكشاك معدنية حسب المقاس. نزّله بصيغة PDF."),
}
PER = 2  # sayfa başına ürün
PDF = {"tr": "Metursan-Urun-Katalogu-2026-TR", "en": "Metursan-Product-Catalogue-2026-EN", "de": "Metursan-Produktkatalog-2026-DE",
       "fr": "Metursan-Catalogue-Produits-2026-FR", "ar": "Metursan-Catalogue-2026-AR"}

def build(L, X):
    """X: build.py bağlamı (M, SITE, CATEGORIES, D, LANGS, ct, pt, img, wa, write, MARK, ld, org_ld, VER)"""
    M, SITE, CATS, D = X["M"], X["SITE"], X["CATEGORIES"], X["D"]
    ct, pt, img, K, m = X["ct"], X["pt"], X["img"], KAT[L], X["M"][L]
    rtl = m.DIR == "rtl"
    n_all = sum(len(c["items"]) for c in CATS)
    site = f"{D}/{L}/"
    # sayfa planı: 1 kapak, 2 hakkımızda+içindekiler, sonra kategoriler, sonda arka kapak
    plan, pg = [], 3
    for c in CATS:
        its = c["items"]; chunks = [its[i:i + PER] for i in range(0, len(its), PER)]
        plan.append((c, chunks, pg)); pg += len(chunks)
    total = pg
    def foot(n, label=""):
        return f'<div class="pf"><span>{e(label)}</span><span dir="ltr">metursan.com</span><span>{e(K["page"])} {n}</span></div>'
    logo = lambda cls="": f'<div class="klogo {cls}">{X["MARK"]}<div><b dir="ltr">MET<i>URSAN</i></b><small>{e(K["tagline"])}</small></div></div>'
    pages = []
    # 1) kapak
    covers = "".join(f'<figure><img src="{img(c["cover"], 700)}" alt="{e(ct(c, L)[0])}"><figcaption>{e(ct(c, L)[0])}</figcaption></figure>' for c in CATS[:4])
    pages.append(f'''<section class="page cover">{logo("big")}
<div class="ct"><p class="yr">2026</p><h1>{e(K["title"])}</h1><p class="sub">{e(K["sub"])}</p>
<p class="stat"><b>{n_all}</b> {e(K["models"])} · <b>{len(CATS)}</b> {e(M[L].UI["cats_n"])} · <span dir="ltr">1994</span></p></div>
<div class="mosaic">{covers}</div>
<div class="cbar"><span dir="ltr">metursan.com</span><span dir="ltr">{SITE["phone1"]}</span><span>{SITE["email"]}</span></div></section>''')
    # 2) hakkımızda + neden + içindekiler
    why = "".join(f'<li><b>{e(a)}</b> {e(b)}</li>' for a, b, _ in m.WHY[:5])
    toc = "".join(f'<li><span class="n">{e(ct(c, L)[0])}</span><span class="d"></span><span class="m">{len(c["items"])} {e(K["models"])}</span><span class="p">{p0}</span></li>' for c, _, p0 in plan)
    about = "".join(f"<p>{x}</p>" for x in m.ABOUT[:3])
    pages.append(f'''<section class="page intro"><div class="cols"><div><h2>{e(K["about"])}</h2>{about}<h3>{e(K["why"])}</h3><ul class="why">{why}</ul></div>
<div><h2>{e(K["contents"])}</h2><ol class="toc">{toc}</ol>
<div class="note">{e(K["cta2"])}</div></div></div>{foot(2)}</section>''')
    # 3) ürün sayfaları
    for c, chunks, p0 in plan:
        cn, cs, cintro, _ = ct(c, L)
        for k, chunk in enumerate(chunks):
            head = (f'<header class="chead"><p class="cc">{e(c["code"])}</p><h2>{e(cn)}</h2><p>{e(cs)}</p></header>' if k == 0
                    else f'<header class="chead small"><h2>{e(cn)}</h2></header>')
            prods = ""
            for p in chunk:
                pn, ps, pf, pu, pa = pt(p, L)
                thumbs = "".join(f'<img src="{img(x, 360)}" alt="">' for x in p["imgs"][1:3])
                url = f"{site}{p['cat']}/{p['slug']}/"
                prods += f'''<article class="prod"><div class="pi"><img class="main" src="{img(p["imgs"][0], 900)}" alt="{e(pn)}"><div class="th">{thumbs}</div></div>
<div class="pt"><p class="code" dir="ltr">{p["code"]}</p><h3>{e(pn)}</h3><p class="ps">{e(ps)}</p>
<h4>{e(K["feats"])}</h4><ul>{"".join(f"<li>{e(f)}</li>" for f in pf[:5])}</ul>
<p class="uses"><b>{e(K["uses"])}:</b> {e(", ".join(pu[:6]))}</p>
<a class="lnk" href="{url}">{e(K["more"])} ↗ <span dir="ltr">{url.replace("https://", "")}</span></a></div></article>'''
            pages.append(f'<section class="page prods">{head}{prods}{foot(p0 + k, cn)}</section>')
    # son) arka kapak
    srv = "".join(f"<li>{e(a)}</li>" for a, _ in m.SERVICES)
    pages.append(f'''<section class="page backc">{logo("big white")}
<div class="bc"><h2>{e(K["cta"])}</h2><p>{e(K["cta2"])}</p>
<div class="bgrid"><div><h3>{e(K["services"])}</h3><ul>{srv}</ul></div>
<div class="contact"><p><small>{e(M[L].UI["c_phone"])}</small><b dir="ltr">{SITE["phone1"]}</b><span dir="ltr">{SITE["phone2"]}</span></p>
<p><small>WhatsApp</small><b dir="ltr">{SITE["whatsapp_display"]}</b></p><p><small>E-mail</small><b>{SITE["email"]}</b></p>
<p><small>{e(M[L].UI["c_addr"])}</small><span>{e(SITE["street"])}<br>{SITE["postal"]} {e(SITE["city"])}, Türkiye</span></p>
<p><small>Web</small><b dir="ltr">metursan.com</b></p></div></div></div>
<p class="legal">© 2026 Metursan · {e(SITE["legal"])}</p></section>''')
    langs = "".join(f'<a href="../../{l}/katalog/" hreflang="{l}" lang="{l}"{" aria-current=true" if l == L else ""}>{e(M[l].NAME)}</a>' for l in X["LANGS"])
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{D}/{l}/katalog/">' for l in X["LANGS"])
    font = ("https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" if rtl
            else "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap")
    title = f'Metursan · {K["title"]} 2026'
    desc = K["meta"].format(n=n_all, c=len(CATS))
    import os, hashlib
    pf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "katalog", PDF[L] + ".pdf")
    pdf_link = (f'<a class="dl" href="../../static/katalog/{PDF[L]}.pdf?v={hashlib.md5(open(pf, "rb").read()).hexdigest()[:8]}" download>{e(K["pdf"].split(" / ")[0])} ↓ <small>{os.path.getsize(pf) // 1048576 + 1} MB</small></a>'
                if os.path.exists(pf) else "")
    html = f'''<!doctype html><html lang="{L}" dir="{m.DIR}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{D}/{L}/katalog/">{alts}
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{D}/static/logo/metursan-og.png">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://wsrv.nl" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="{font}">
<link rel="stylesheet" href="../../static/katalog.css?v={X["VER"]["kcss"]}">
{X["ld"]({"@context": "https://schema.org", "@type": "CreativeWork", "name": title, "inLanguage": L, "url": f"{D}/{L}/katalog/", "about": f"{D}/{L}/products.json", "publisher": {"@type": "Organization", "name": "Metursan", "url": D + "/"}})}
</head><body>
<div class="bar"><a href="../">← {e(K["back"])}</a><details class="kl"><summary>{e(K["lang"])}: {L.upper()}</summary><div>{langs}</div></details>
{pdf_link}<button id="pdf" type="button" class="sec">{e(K["pdf"].split(" / ")[-1])}</button><p class="hint">{e(K["hint"])}</p></div>
<div class="book">{"".join(pages)}</div>
<script>
(function(){{var b=document.getElementById('pdf'),t=b.textContent;
function fit(){{var w=Math.min(window.innerWidth-16,794);document.querySelector('.book').style.zoom=(w/794).toFixed(3)}}
if(window.innerWidth<820){{fit();addEventListener('resize',fit)}}
b.onclick=function(){{var im=[].slice.call(document.images).filter(function(i){{return !i.complete}});
if(!im.length)return print();b.textContent={json.dumps(K["loading"], ensure_ascii=False)};var n=im.length,done=function(){{if(--n<=0){{b.textContent=t;print()}}}};
im.forEach(function(i){{i.addEventListener('load',done);i.addEventListener('error',done)}});setTimeout(function(){{if(n>0){{n=0;b.textContent=t;print()}}}},15000)}};
if(location.hash=='#print')addEventListener('load',function(){{setTimeout(print,600)}});}})();
</script></body></html>'''
    X["write"](f"{L}/katalog/index.html", html)
    return total
