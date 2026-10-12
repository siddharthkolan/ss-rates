// Shree SS Jewellers - rate relay (Cloudflare Worker)
// Original feed se har ~2 second me sirf EK baar rates leta hai, aur sab customers ko wahi copy deta hai.
// Isse original server par load customers ki sankhya se nahi badhta.
const ORIGIN = "https://bcast.bhavyalaxmibullion.com:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/bhavyalaxmi";
const FRESH_MS = 2000;      // itne der tak wahi copy do
const STALE_MS = 60000;     // origin band ho to itni der tak purani copy do
const CORS = { "access-control-allow-origin": "*", "access-control-allow-methods": "GET, OPTIONS", "access-control-allow-headers": "*" };

let last = { t: 0, body: "" };   // isolate ki memory me last good copy
let inflight = null;

async function refresh() {
  try {
    const r = await fetch(ORIGIN, { signal: AbortSignal.timeout(4000) });
    if (r.ok) {
      const body = await r.text();
      if (body.length > 20) last = { t: Date.now(), body };
    }
  } catch (e) { /* purani copy chalegi */ }
}

export default {
  async fetch(req) {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (req.method !== "GET") return new Response("method not allowed", { status: 405, headers: CORS });
    const age = Date.now() - last.t;
    if (age >= FRESH_MS) {
      inflight = inflight || refresh().finally(() => { inflight = null; });
      await inflight;
    }
    if (!last.body || Date.now() - last.t > STALE_MS)
      return new Response("upstream unavailable", { status: 502, headers: { ...CORS, "cache-control": "no-store" } });
    return new Response(last.body, { status: 200, headers: { ...CORS, "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" } });
  }
};
