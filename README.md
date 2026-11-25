# metursan.com

Metursan (Huzur Pano) çok dilli statik sitesi — TR, EN, DE, FR, AR.

- Ürünler ve iletişim: `data.py` · Çeviriler: `lang/*.py` · Tasarım: `static/style.css` · Asistan/arama: `static/app.js`
- Üretim: `python3 build.py` → `dist/`
- Cloudflare Pages: build command `python3 build.py`, output directory `dist`. `main` dalına her push otomatik yayınlanır.
