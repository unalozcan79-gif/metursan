/**
 * Metursan — isteğe bağlı gerçek LLM asistanı (Cloudflare Worker)
 * Kurulum:
 *  1) Cloudflare > Workers > Create > bu dosyayı yapıştırın.
 *  2) Settings > Variables: ANTHROPIC_API_KEY (secret) ekleyin.
 *  3) Sitenin <head> kısmına: <meta name="ai-endpoint" content="https://WORKER-ADINIZ.workers.dev">
 * Uç nokta yoksa site, tarayıcıda çalışan yerel asistanı kullanır.
 */
const SITE = "https://metursan.com";
let CACHE = null;

export default {
  async fetch(req, env) {
    const cors = { "Access-Control-Allow-Origin": SITE, "Access-Control-Allow-Headers": "content-type", "Access-Control-Allow-Methods": "POST" };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });
    if (req.method !== "POST") return new Response("POST only", { status: 405, headers: cors });

    const { messages = [] } = await req.json();
    if (!CACHE) CACHE = await fetch(SITE + "/products.json").then(r => r.json());
    const catalog = CACHE.products.map(p => `${p.code} | ${p.name} | ${p.category_name} | ${p.summary} | Özellikler: ${p.features.join("; ")} | Kullanım: ${p.uses.join(", ")}`).join("\n");

    const system = `Sen Metursan'ın (Huzur Pano, İstanbul, 1994) satış asistanısın. Metal kiosk, pano, cihaz kutusu, şarj istasyonu gövdesi, gemi konsolu, endüstriyel kabin, şase, paslanmaz ve medikal ürünleri ÖLÇÜYE ÖZEL üretiyoruz.
Kurallar: Türkçe, kısa ve net yaz (en fazla 120 kelime). Yalnızca aşağıdaki katalogdan ürün öner. Fiyat verme; fiyatın ölçü, malzeme, adet ve aksesuara göre teklifle belirlendiğini söyle. Bilmediğin teknik iddiada bulunma.
Uygunsa müşteriden ölçü, adet, malzeme ve kullanım ortamını iste. İletişim: ${CACHE.contact.phone}, WhatsApp ${CACHE.contact.whatsapp}, ${CACHE.contact.email}.
Yanıtının EN SONUNA, önerdiğin ürün kodlarını şu biçimde ekle: [[KODLAR: MT-XXX-01, MT-YYY-02]] (yoksa [[KODLAR:]]).
KATALOG:
${catalog}`;

    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": env.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model: "claude-haiku-5-5", max_tokens: 500, system, messages: messages.slice(-10).map(m => ({ role: m.role, content: String(m.content).slice(0, 2000) })) })
    });
    if (!r.ok) return new Response(JSON.stringify({ error: "llm" }), { status: 502, headers: { ...cors, "content-type": "application/json" } });
    const j = await r.json();
    let text = (j.content || []).map(c => c.text || "").join("");
    const m = text.match(/\[\[KODLAR:([^\]]*)\]\]/);
    const products = m ? m[1].split(",").map(s => s.trim()).filter(Boolean) : [];
    text = text.replace(/\[\[KODLAR:[^\]]*\]\]/, "").trim();
    return new Response(JSON.stringify({ reply: text, products }), { headers: { ...cors, "content-type": "application/json" } });
  }
};
