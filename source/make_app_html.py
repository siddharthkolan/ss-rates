#!/usr/bin/env python3
"""rate_board.html -> assets/index.html (bina Python proxy, seedha feed se)."""
import re, sys, os
root = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(root, "..", "rate_board.html"), encoding="utf-8").read()
FEED = sys.argv[1] if len(sys.argv) > 1 else "https://bcast.bhavyalaxmibullion.com:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/bhavyalaxmi"

def once(s, old, new):
    assert s.count(old) == 1, (old[:40], s.count(old))
    return s.replace(old, new)

# 1) vw -> calc(N * var(--u)) (sirf <style> ke andar)
a, b = src.index("<style>"), src.index("</style>")
css = src[a:b]
css = re.sub(r"(-?\d*\.?\d+)vw", lambda m: f"calc({m.group(1)} * var(--u))", css)
css = once(css, "  :root{\n", "  :root{\n    --u:min(1vw,1.7778vh);\n")
src = src[:a] + css + src[b:]

# 2) tick() replace
t0 = src.index("async function tick(){")
t1 = src.index("/* Logo:")
new_tick = '''const FEED_URL = "%s";
let lastGood = 0, busy = false;
function tick(){
  if (busy) return; busy = true;
  const x = new XMLHttpRequest();
  x.open("GET", FEED_URL + "?_=" + Date.now(), true);
  x.timeout = 5000;
  x.onload = function(){
    busy = false;
    if (x.status === 200 && x.responseText && x.responseText.length > 20){
      lastGood = Date.now(); noteOK();
      try{ render(parseFeed(x.responseText)); }catch(e){}
      document.getElementById("foot").textContent = "Feed updated " + hhmmss(lastGood);
    }
    updBadge();
  };
  x.onerror = x.ontimeout = function(){ busy = false; updBadge(); };
  x.send();
}
function updBadge(){
  if (!lastGood){ setBadge("off", "FEED OFFLINE"); noteFail(); return; }
  const age = (Date.now() - lastGood) / 1000;
  if (age >= 8) noteFail();
  if (age < 10) setBadge("live", "\\u25CF LIVE");
  else if (age < 60) setBadge("stale", "DATA " + Math.round(age) + "s OLD");
  else setBadge("off", "FEED OFFLINE");
}
setInterval(updBadge, 1000);

''' % FEED
src = src[:t0] + new_tick + src[t1:]

# 2b) portrait layout (phone)
PORTRAIT = """
  @media (orientation: portrait){
    :root{--u:2.2vw}
    html,body{height:auto;min-height:100%;overflow-y:auto;overflow-x:hidden}
    body{padding:calc(1.6 * var(--u)) calc(1.4 * var(--u));gap:calc(1.4 * var(--u))}
    header{flex-direction:column;align-items:stretch;gap:calc(1 * var(--u))}
    #logo{height:calc(5.5 * var(--u))}
    .brand h1{font-size:calc(1.7 * var(--u))}
    .brand p{font-size:calc(.8 * var(--u));letter-spacing:.06em}
    .clock{justify-content:space-between}
    .clock .t{font-size:calc(2.2 * var(--u));text-align:left}
    .clock .d{font-size:calc(.95 * var(--u));text-align:left}
    .badge{font-size:calc(.95 * var(--u))}
    .main{display:flex;flex-direction:column;gap:calc(1.4 * var(--u));flex:none}
    .left{display:flex;flex-direction:column;gap:calc(.9 * var(--u))}
    .row{grid-template-columns:1.15fr 1fr 1fr;padding:calc(1.1 * var(--u)) calc(1.2 * var(--u))}
    .n1{font-size:calc(1.15 * var(--u))}
    .n3{font-size:calc(.85 * var(--u))}
    .big{font-size:calc(2.9 * var(--u))}
    .lbl{font-size:calc(.85 * var(--u))}
    .right{display:flex;flex-direction:column;gap:calc(1.2 * var(--u))}
    .gcard{padding:calc(1.3 * var(--u))}
    .gtop h3{font-size:calc(1.3 * var(--u))}
    .tiles{flex:none;margin-top:calc(1 * var(--u))}
    .tile{padding:calc(.9 * var(--u)) calc(.8 * var(--u))}
    .tile .k{font-size:calc(1.05 * var(--u))}
    .tile .v{font-size:calc(2.5 * var(--u))}
    .tile .g{font-size:calc(.85 * var(--u))}
    .strip{display:grid;grid-template-columns:1fr 1fr;gap:calc(.9 * var(--u))}
    .si{padding:calc(.9 * var(--u)) calc(1.1 * var(--u))}
    .sn{font-size:calc(.95 * var(--u))}
    .sv{font-size:calc(1.5 * var(--u))}
    footer{font-size:calc(.9 * var(--u))}
  }
"""
src = once(src, "</style>", PORTRAIT + "</style>")
# 2c) glass theme + floating dock (sirf app me)
WA_URL  = "https://whatsapp.com/channel/0029VbBrPE50bIdlNTKXtr1S"   # WhatsApp channel
IG_URL  = "https://www.instagram.com/ss_jewellers_jaora/"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=Shree+SS+Jewellers+Azad+Chowk+Jaora"
GLASS = """
  /* ===== glass floating theme ===== */
  html{background:var(--bg);background-image:
    radial-gradient(60% 40% at 12% 6%, rgba(214,168,74,.34), transparent 70%),
    radial-gradient(55% 38% at 95% 32%, rgba(236,170,150,.26), transparent 70%),
    radial-gradient(60% 40% at 8% 78%, rgba(255,222,150,.42), transparent 70%),
    radial-gradient(50% 35% at 92% 96%, rgba(190,160,90,.25), transparent 70%);
    background-attachment:fixed}
  body{background:transparent}
  .card,.si{background:rgba(255,255,255,.52);border:1px solid rgba(255,255,255,.75);
    -webkit-backdrop-filter:blur(16px) saturate(1.5);backdrop-filter:blur(16px) saturate(1.5);
    box-shadow:0 calc(.6 * var(--u)) calc(2.4 * var(--u)) rgba(120,95,40,.14),inset 0 1px 0 rgba(255,255,255,.9)}
  .tile{background:rgba(248,236,200,.55);border:1px solid rgba(255,255,255,.65);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.8)}
  .unit{background:rgba(255,255,255,.6)}
  #notice{-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}

  /* floating dock */
  .dock{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(env(safe-area-inset-bottom,0px) + 2 * var(--u));
    z-index:20;display:flex;gap:calc(1 * var(--u));padding:calc(.8 * var(--u)) calc(1.2 * var(--u));
    border-radius:calc(4 * var(--u));background:rgba(255,255,255,.38);
    border:1px solid rgba(255,255,255,.8);
    -webkit-backdrop-filter:blur(22px) saturate(1.7);backdrop-filter:blur(22px) saturate(1.7);
    box-shadow:0 calc(1 * var(--u)) calc(3.4 * var(--u)) rgba(60,45,15,.25),inset 0 1px 0 rgba(255,255,255,.95)}
  .dock a{display:flex;flex-direction:column;align-items:center;gap:calc(.3 * var(--u));text-decoration:none;
    color:var(--ink);font-size:calc(1.1 * var(--u));font-weight:600;letter-spacing:.02em;
    padding:calc(.4 * var(--u)) calc(1.3 * var(--u));border-radius:calc(3 * var(--u));
    -webkit-tap-highlight-color:transparent;transition:transform .15s,background .15s}
  .dock a:active{transform:scale(.92);background:rgba(255,255,255,.55)}
  .dock .ib{width:calc(5 * var(--u));height:calc(5 * var(--u));border-radius:50%;display:grid;place-items:center;
    background:rgba(255,255,255,.7);border:1px solid rgba(255,255,255,.9);
    box-shadow:0 calc(.3 * var(--u)) calc(1 * var(--u)) rgba(60,45,15,.15)}
  .dock svg{width:calc(2.7 * var(--u));height:calc(2.7 * var(--u))}
  body{padding-bottom:calc(14 * var(--u))}
"""
DOCK = """<nav class="dock" aria-label="Contact">
  <a href="%s" aria-label="WhatsApp Channel"><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#1faa59" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21l1.6-4.6A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 8.5c0 3.4 3.1 6.5 6.5 6.5l1.2-1.6-2.2-1.1-.9.8c-1-.4-1.9-1.3-2.3-2.3l.8-.9-1.1-2.2z" fill="#1faa59" stroke="none"/></svg></span>Channel</a>
  <a href="%s" aria-label="Instagram"><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#d6249f" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.3" cy="6.7" r="1" fill="#d6249f" stroke="none"/></svg></span>Instagram</a>
  <a href="%s" aria-label="Location"><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#d2403a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6" fill="#d2403a" stroke="none"/></svg></span>Location</a>
</nav>
""" % (WA_URL, IG_URL, MAP_URL)
# 2d) row: High/Low buy-sell ke neeche, bade fonts
src = once(src, '        <div class="n3">High ${it.high} · Low ${it.low}</div>\n      </div>\n      <div class="px"><span class="lbl">BUY</span>',
    '      </div>\n      <div class="px pb"><span class="lbl">BUY</span>')
src = once(src, '<span class="big ${it.p.bc}">${it.buy}</span></div>', '<span class="big ${it.p.bc}">${it.buy}</span><span class="hs">L - ${it.low}</span></div>')
src = once(src, '<div class="px"><span class="lbl">SELL</span><span class="big ${it.p.sc}">${it.sell}</span></div>\n    </div>`;',
    '<div class="px ps"><span class="lbl">SELL</span><span class="big ${it.p.sc}">${it.sell}</span><span class="hs">H - ${it.high}</span></div>\n      \n    </div>`;')
src = once(src, '      <div>\n        <div class="n1">', '      <div class="nm">\n        <div class="n1">')
BIG = """
  .hs{font-size:calc(1.15 * var(--u));font-weight:600;color:var(--muted);font-variant-numeric:tabular-nums;margin-top:calc(.15 * var(--u))}
  @media (orientation: portrait){
    .brand p{font-size:calc(1 * var(--u))}
    .clock .d{font-size:calc(1.2 * var(--u))}
    .n1{font-size:calc(1.8 * var(--u));line-height:1.15}
    .unit,.st{font-size:calc(1.15 * var(--u))}
    .row{grid-template-columns:1.1fr 1fr 1fr}
    .unit,.st{font-size:calc(1.05 * var(--u))}
    .lbl{font-size:calc(1.05 * var(--u))}
    .hs{font-size:calc(1.3 * var(--u))}
    .gtop h3{font-size:calc(1.55 * var(--u))}
    .gtop .src{font-size:calc(1.1 * var(--u))}
    .tile .k{font-size:calc(1.25 * var(--u))}
    .tile .ut{font-size:calc(.95 * var(--u))}
    .tile .v{font-size:calc(2.6 * var(--u))}
    .tile .g{font-size:calc(1.05 * var(--u))}
    .sn{font-size:calc(1.15 * var(--u))}
    .sv{font-size:calc(1.6 * var(--u))}
    footer{font-size:calc(1.05 * var(--u))}
    .dock a{font-size:calc(1.25 * var(--u))}
  }
"""
GLASS = GLASS + BIG
src = once(src, "</style>", GLASS + "</style>")
src = once(src, '<footer id="foot">', DOCK + '<footer id="foot">')

# 2e) tile label: "SILVER 90%" -> "SILVER"
assert src.count('label: "SILVER 90%"') == 2
src = src.replace('label: "SILVER 90%"', 'label: "SILVER"')
# 2f) app update checker (GitHub se version.json)
vm = re.search(r'android:versionCode="(\d+)"', open(os.path.join(root, "AndroidManifest.xml")).read())
VC = int(vm.group(1))
VER_URL = "https://raw.githubusercontent.com/siddharthkolan/ss-rates/main/version.json"
UPD_CSS = """
  #upd{position:fixed;inset:0;z-index:40;display:flex;align-items:center;justify-content:center;
    background:rgba(42,36,24,.35);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);padding:calc(2 * var(--u))}
  #upd[hidden]{display:none}
  #upd .ubox{width:100%;max-width:calc(36 * var(--u));text-align:center;padding:calc(2.6 * var(--u)) calc(2.2 * var(--u));
    border-radius:calc(2.4 * var(--u));background:rgba(255,255,255,.62);border:1px solid rgba(255,255,255,.85);
    -webkit-backdrop-filter:blur(22px) saturate(1.6);backdrop-filter:blur(22px) saturate(1.6);
    box-shadow:0 calc(1 * var(--u)) calc(4 * var(--u)) rgba(60,45,15,.3),inset 0 1px 0 rgba(255,255,255,.95)}
  #upd .uic{font-size:calc(4 * var(--u));line-height:1}
  #upd h2{font-size:calc(2 * var(--u));margin-top:calc(1 * var(--u));color:var(--gold)}
  #upd p{font-size:calc(1.35 * var(--u));color:var(--muted);margin-top:calc(.7 * var(--u));white-space:pre-line}
  #upd .ubtn{display:block;width:100%;margin-top:calc(1.4 * var(--u));padding:calc(1.2 * var(--u));border-radius:calc(3 * var(--u));
    font:600 calc(1.5 * var(--u)) inherit;font-family:inherit;text-decoration:none;text-align:center;border:0;cursor:pointer;
    background:linear-gradient(135deg,#c79a3b,#a67a22);color:#fff;box-shadow:0 calc(.4 * var(--u)) calc(1.4 * var(--u)) rgba(166,122,34,.4)}
  #upd .ubtn.ghost{background:rgba(255,255,255,.7);color:var(--ink);box-shadow:none;border:1px solid rgba(255,255,255,.9)}
"""
UPD_HTML = """<div id="upd" hidden><div class="ubox"><div class="uic">\u2B06\uFE0F</div>
  <h2>Naya version available</h2><p id="upv"></p><p id="upn"></p>
  <a id="upgo" class="ubtn" href="#">Update karein</a><button id="uplater" class="ubtn ghost" type="button">Baad me</button></div></div>
"""
UPD_JS = """
/* ---- app update check ---- */
const APP_VER = %d, VER_URL = "%s";
let updSkipped = false;
function showUpdate(j){
  document.getElementById("upv").textContent = "Aapke paas v" + APP_VER_NAME + " hai. Naya v" + j.versionName + " taiyar hai.";
  document.getElementById("upn").textContent = j.notes || "";
  document.getElementById("upgo").setAttribute("href", j.apk);
  document.getElementById("upd").hidden = false;
}
function checkUpdate(){
  if (updSkipped) return;
  const x = new XMLHttpRequest();
  x.open("GET", VER_URL + "?_=" + Date.now(), true); x.timeout = 8000;
  x.onload = function(){
    try{ if (x.status !== 200) return; const j = JSON.parse(x.responseText);
      if (j.versionCode > APP_VER && j.apk) showUpdate(j); }catch(e){}
  };
  x.send();
}
document.getElementById("uplater").addEventListener("click", function(){
  updSkipped = true; document.getElementById("upd").hidden = true;
});
setTimeout(checkUpdate, 4000);
setInterval(checkUpdate, 6 * 3600 * 1000);
document.addEventListener("visibilitychange", function(){ if (!document.hidden) setTimeout(checkUpdate, 1500); });
""" % (VC, VER_URL)
VN = re.search(r'android:versionName="([^"]+)"', open(os.path.join(root, "AndroidManifest.xml")).read()).group(1)
UPD_JS = UPD_JS.replace("APP_VER_NAME", '"%s"' % VN).replace('"v" + "' + VN + '" + "', 'v' + VN) if False else UPD_JS.replace('" + APP_VER_NAME + "', VN)
src = once(src, "</style>", UPD_CSS + "</style>")
src = once(src, '<footer id="foot">', UPD_HTML + '<footer id="foot">')
src = once(src, "</script>\n</body>", UPD_JS + "</script>\n</body>")

# 3) logo relative
src = once(src, 'img.src = "/" + names[i]', 'img.src = names[i]')
src = once(src, 'img.src = "/" + names[0]', 'img.src = names[0]')
# 4) footer
src = src.replace("   ·   F = full screen", "").replace("F = full screen", "")
os.makedirs(os.path.join(root, "assets"), exist_ok=True)
open(os.path.join(root, "assets", "index.html"), "w", encoding="utf-8").write(src)
print("ok", len(src))
