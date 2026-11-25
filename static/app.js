/* Metursan — arama, galeri, kaydırma ve yapay zekâ ürün asistanı (çok dilli, bağımlılıksız) */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const T = window.T || {}, ROOT = document.body.dataset.root || "", PRETTY = document.body.dataset.pretty === "1", RTL = !!T.rtl;
  const WA = "905308855435";
  // İsteğe bağlı gerçek LLM uç noktası (extras/ai-worker.js). Boşsa asistan tarayıcıda yerel çalışır.
  const AI_ENDPOINT = (document.querySelector('meta[name="ai-endpoint"]') || {}).content || "";
  const link = p => ROOT + p.path + (PRETTY ? "" : "index.html");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /* menü */
  const nav = $(".nav"), burger = $(".burger");
  burger && burger.addEventListener("click", () => { const o = nav.classList.toggle("open"); burger.setAttribute("aria-expanded", o); });
  document.addEventListener("click", ev => { const d = $(".langsel[open]"); if (d && !ev.target.closest(".langsel")) d.open = false; });
  $$(".langsel a").forEach(a => a.addEventListener("click", () => { try { sessionStorage.setItem("mt-stay", "1"); } catch (e) {} }));

  /* şerit okları */
  $$(".st-pads").forEach(pd => {
    let r = pd.previousElementSibling;
    if (!r || !(r.classList.contains("st-row") || r.classList.contains("st-icons"))) r = pd.parentElement.querySelector(".st-icons");
    pd.addEventListener("click", ev => { const b = ev.target.closest(".st-pad"); if (b && r) r.scrollBy({ left: b.dataset.dir * (RTL ? -1 : 1) * r.clientWidth * .8, behavior: "smooth" }); });
  });

  /* galeri */
  const main = $("#pdimg");
  $$(".pd-gal .thumbs button").forEach(b => b.addEventListener("click", () => {
    main.src = b.dataset.src; $$(".pd-gal .thumbs button").forEach(x => x.setAttribute("aria-current", x === b));
  }));

  /* normalizasyon: küçük harf, aksan/hareke kaldırma, harf+rakam (tüm alfabeler) */
  const norm = s => String(s).toLocaleLowerCase(T.lang || "tr").replace(/ı/g, "i").normalize("NFD").replace(/[̀-ًͯ-ٰٟ]/g, "")
    .replace(/[أإآ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي").replace(/ß/g, "ss").replace(/[^\p{L}\p{N} ]+/gu, " ");
  let DATA = null;
  const load = () => DATA ? Promise.resolve(DATA) : fetch(ROOT + "products.json").then(r => r.json()).then(d => {
    d.products.forEach(p => { p._n = norm(p.name); p._t = norm([p.summary, p.features.join(" "), p.uses.join(" "), p.description, p.category_name, p.code].join(" ")); p._c = norm(p.category_name); });
    return DATA = d;
  });

  const STOP = new Set("bir ve ile icin bu su o da de mi mu ne nasil var yok olan gibi cok en daha ama veya istiyorum lazim gerek bana bize benim hangi ariyorum the a an and or for with of to in on is i we need want my our looking der die das und oder fur mit ein eine ich wir brauche le la les un une des et ou pour avec je nous besoin de du في من الى على و او ل مع اريد نحتاج".split(" "));
  // Türkçe eş anlamlılar (diğer diller doğrudan çeviri metinleriyle eşleşir)
  const SYN = {
    sarj: "sarj istasyon elektrikli arac", gemi: "gemi kopru konsol kaptan", yat: "gemi konsol", tekne: "gemi konsol", hastane: "medikal hastane paslanmaz",
    ameliyat: "laminer medikal", hijyen: "paslanmaz medikal gida", gida: "paslanmaz gida hijyen", ses: "kabin yalitim", gurultu: "kabin yalitim ses",
    odeme: "odeme kiosk banka kart", banka: "banka kiosk odeme", atm: "banka kiosk", bilgi: "info kiosk danisma", reklam: "totem led ekran", dokunmatik: "kiosk ekran",
    sigorta: "elektrik pano", salter: "elektrik pano", kumanda: "pano piyano konsol", muhafaza: "kutu kabin cihaz", konstruksiyon: "sase makine", masa: "tezgah calisma",
    inox: "paslanmaz", outdoor: "dis mekan", charger: "charger housing", ev: "ev tipi"
  };
  const stem = w => w.length > 5 ? w.slice(0, Math.max(5, w.length - 3)) : w;
  const tokens = q => { const t = norm(q).split(/\s+/).filter(w => w.length > 1 && !STOP.has(w)); const ex = [];
    if ((T.lang || "tr") === "tr") t.forEach(w => { const k = Object.keys(SYN).find(s => w.startsWith(s)); if (k) ex.push(...SYN[k].split(" ")); });
    const all = [...new Set([...t, ...ex])]; all.orig = new Set(t); return all; };
  const score = (p, ts) => ts.reduce((s, w) => { const st = stem(w), k = ts.orig.has(w) ? 2 : 1; return s + k * ((p._n.includes(st) ? 4 : 0) + (p._t.includes(st) ? 1 : 0) + (p._c.includes(st) ? 2 : 0)); }, 0);
  const search = (q, n = 8) => { const ts = tokens(q); return ts.length ? DATA.products.map(p => [score(p, ts), p]).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, n).map(x => x[1]) : []; };

  /* üst arama */
  const q = $("#q"), pop = $("#qpop"), res = $("#qres");
  if (q) {
    let sel = -1;
    const draw = () => {
      const v = q.value.trim(); if (!v) { pop.hidden = true; return; }
      load().then(() => {
        const r = search(v, 8); sel = -1;
        res.innerHTML = (r.length ? `<li class="srch-cnt">${r.length} ${esc(T.results)}</li>` + r.map(p => `<li><a href="${link(p)}"><img src="${p.image}" alt="" loading="lazy"><span class="t"><b>${esc(p.name)}</b><small>${esc(p.code)} · ${esc(p.category_name)}</small></span><span class="go">›</span></a></li>`).join("")
          : `<li class="srch-none">“${esc(v)}” ${esc(T.noresult)}</li>`) + `<li><button class="srch-ai" data-ai="${esc(v)}" data-raw="1">✦ ${esc(T.ask)}: “${esc(v)}”</button></li>`;
        pop.hidden = false;
      });
    };
    q.addEventListener("input", draw); q.addEventListener("focus", () => { load(); if (q.value) draw(); });
    q.addEventListener("keydown", ev => {
      const a = $$("a", res);
      if ((ev.key === "ArrowDown" || ev.key === "ArrowUp") && a.length) { ev.preventDefault(); sel = (sel + (ev.key === "ArrowDown" ? 1 : -1) + a.length) % a.length; a.forEach((x, i) => x.classList.toggle("on", i === sel)); }
      else if (ev.key === "Enter") { ev.preventDefault(); if (a[sel]) location.href = a[sel].href; else if (a[0]) location.href = a[0].href; else openAI(q.value); }
      else if (ev.key === "Escape") { pop.hidden = true; q.blur(); }
    });
    document.addEventListener("click", ev => { if (!ev.target.closest(".srch")) pop.hidden = true; });
    document.addEventListener("keydown", ev => { if (ev.key === "/" && !/input|textarea/i.test(document.activeElement.tagName)) { ev.preventDefault(); q.focus(); } });
    const pq = new URLSearchParams(location.search).get("q"); if (pq) { q.value = pq; draw(); }
  }

  /* ===== Yapay zekâ asistanı ===== */
  const box = $("#ai"), body = $("#aib"), form = $("#aif"), inp = $("#aii");
  const history = []; let greeted = false, lastProducts = [];
  const add = (html, who = "bot") => { const d = document.createElement("div"); d.className = "ai-m " + who; d.innerHTML = html; body.appendChild(d); body.scrollTop = body.scrollHeight; return d; };
  const pcard = p => `<a class="ai-p" href="${link(p)}"><img src="${p.image}" alt="" loading="lazy"><span><b>${esc(p.name)}</b><small><span dir="ltr">${esc(p.code)}</span> · ${esc(p.summary)}</small></span></a>`;
  const waLink = txt => `<a class="ai-wa" href="https://wa.me/${WA}?text=${encodeURIComponent(txt)}" target="_blank" rel="noopener">${esc(T.wa_btn)}</a>`;
  const chips = arr => `<div class="ai-chips">${arr.map(c => `<button type="button" data-chip="${esc(c)}">${esc(c)}</button>`).join("")}</div>`;
  function openAI(text) {
    box.hidden = false; document.body.classList.add("ai-open"); load();
    if (!greeted) { greeted = true; add(`<p>${esc(T.hi)}</p>` + chips(T.chips || [])); }
    if (text) ask(text); else setTimeout(() => inp.focus(), 50);
  }
  const closeAI = () => { box.hidden = true; document.body.classList.remove("ai-open"); };
  document.addEventListener("click", ev => {
    const t = ev.target.closest("[data-ai]");
    if (t) { ev.preventDefault(); if (pop) pop.hidden = true; const v = t.dataset.ai; openAI(v ? (t.dataset.raw ? v : v + T.about) : ""); }
    const c = ev.target.closest("[data-chip]"); if (c) ask(c.dataset.chip);
  });
  $("#aifab") && $("#aifab").addEventListener("click", () => openAI());
  $("#aix") && $("#aix").addEventListener("click", closeAI);
  document.addEventListener("keydown", ev => { if (ev.key === "Escape" && box && !box.hidden) closeAI(); });
  form && form.addEventListener("submit", ev => { ev.preventDefault(); const v = inp.value.trim(); if (v) { inp.value = ""; ask(v); } });

  function localReply(text) {
    const n = " " + norm(text) + " ", out = { html: "", products: [] };
    const has = k => (T[k] || []).some(x => n.includes(norm(x)));
    if (has("k_price")) out.html = `<p>${T.price}</p>`;
    else if (has("k_contact")) out.html = `<p><b>${esc(T.phone)}:</b> <span dir="ltr">${esc(DATA.contact.phone)}</span><br><b>WhatsApp:</b> <span dir="ltr">${esc(DATA.contact.whatsapp)}</span><br><b>${esc(T.email)}:</b> ${esc(DATA.contact.email)}<br><b>${esc(T.address)}:</b> ${esc(DATA.contact.address)}</p>`;
    else if (has("k_ship")) out.html = `<p>${esc(T.ship)}</p>`;
    else if (has("k_draw")) out.html = `<p>${esc(T.draw)}</p>`;
    const prods = search(text, 3);
    if (prods.length) {
      out.products = prods;
      out.html += `<p>${esc(out.html ? T.more : T.best)}</p>` + prods.map(pcard).join("");
      const tips = [];
      if (has("k_out")) tips.push(T.t_out);
      if (has("k_ss")) tips.push(T.t_ss);
      if (has("k_db")) tips.push(T.t_db);
      if (tips.length) out.html += `<p>${esc(tips.join(" "))}</p>`;
      out.html += `<p>${esc(T.measure)}</p>`;
    }
    if (!out.html) out.html = `<p>${esc(T.none)}</p>` + chips(DATA.categories.slice(0, 6).map(c => c.name));
    return out;
  }

  async function ask(text) {
    add(esc(text), "me"); history.push({ role: "user", content: text });
    const t = add(`<span class="ai-dot"></span><span class="ai-dot"></span><span class="ai-dot"></span>`);
    await load();
    let r = null;
    if (AI_ENDPOINT) {
      try {
        const res = await fetch(AI_ENDPOINT, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ lang: T.lang, messages: history.slice(-10) }) });
        if (res.ok) { const j = await res.json(); const ps = (j.products || []).map(c => DATA.products.find(p => p.code === c)).filter(Boolean);
          r = { html: j.reply.split(/\n\n+/).map(x => `<p>${esc(x).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n/g, "<br>")}</p>`).join("") + ps.map(pcard).join(""), products: ps }; }
      } catch (e) { r = null; }
    }
    if (!r) { await new Promise(s => setTimeout(s, 350)); r = localReply(text); }
    if (r.products.length) lastProducts = r.products;
    const asks = history.filter(h => h.role === "user").map(h => "• " + h.content).join("\n");
    const prodLine = lastProducts.length ? "\n" + T.wa_prod + " " + lastProducts.map(p => `${p.name} (${p.code})`).join(", ") : "";
    r.html += waLink(`${T.wa_intro}\n${asks}${prodLine}\n${T.wa_tail}`);
    t.innerHTML = r.html; history.push({ role: "assistant", content: t.innerText }); body.scrollTop = body.scrollHeight;
  }
})();
