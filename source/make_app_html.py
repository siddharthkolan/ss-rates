#!/usr/bin/env python3
"""rate_board.html -> assets/index.html (bina Python proxy, seedha feed se)."""
import re, sys, os
root = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(root, "..", "rate_board.html"), encoding="utf-8").read()
DESKTOP = "--desktop" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
FEED = args[0] if args else "https://bcast.bhavyalaxmibullion.com:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/bhavyalaxmi"

def once(s, old, new):
    assert s.count(old) == 1, (old[:40], s.count(old))
    return s.replace(old, new)

# 1) vw -> calc(N * var(--u)) (sirf <style> ke andar)
a, b = src.index("<style>"), src.index("</style>")
css = src[a:b]
css = re.sub(r"(-?\d*\.?\d+)vw", lambda m: f"calc({m.group(1)} * var(--u))", css)
css = once(css, "  :root{\n", "  :root{\n    --u:min(1vw,1.7778vh);\n")
src = src[:a] + css + src[b:]

# 2) tick() replace (desktop: laptop ka apna /feed wala tick rehta hai)
if not DESKTOP:
    t0 = src.index("async function tick(){")
    t1 = src.index("/* Logo:")
    new_tick = '''const FEED_DEFAULT = "%s";
    let FEED_URL = FEED_DEFAULT, fails = 0, directUntil = 0;
    let lastGood = 0, busy = false, lastErr = "";
    let ticks = 0, busyAt = 0, dX = "-", dF = "-", dG = "-", dE = "-";
    function gotFeed(txt){
      fails = 0; lastGood = Date.now(); noteOK();
      try{ render(parseFeed(txt)); }catch(e){}
      document.getElementById("foot").textContent = "Feed updated " + hhmmss(lastGood);
      updBadge();
    }
    /* fetch() se bhi koshish (kuch TV boxes par XHR chup baith jata hai) + github ping sirf jaanch ke liye */
    function viaFetch(url, tag){
      try{
        const c = (typeof AbortController !== "undefined") ? new AbortController() : null;
        const tm = setTimeout(function(){ try{ c && c.abort(); }catch(e){} }, 7000);
        fetch(url + "?_=" + Date.now(), {cache: "no-store", signal: c ? c.signal : undefined})
          .then(function(r){ clearTimeout(tm); if (tag === "F") dF = "http " + r.status; else dG = "http " + r.status;
            return r.text().then(function(t){ if (tag === "F" && r.status === 200 && t && t.length > 20) gotFeed(t); }); })
          .catch(function(e){ clearTimeout(tm); const m = String((e && e.name || "") + ":" + (e && e.message || e)).slice(0, 40); if (tag === "F") dF = m; else dG = m; });
      }catch(e){ if (tag === "F") dF = "exc"; else dG = "exc"; }
    }
    let useNative = false;
    window.ssNet = function(st, txt){
      busy = false;
      if (st === 200 && txt && txt.length > 20){ gotFeed(txt); }
      else { fails++; lastErr = "native " + st + " " + String(txt).slice(0, 50); updBadge(); }
    };
    function tick(){
      ticks++;
      if (!lastGood && (ticks & 3) === 2){ viaFetch(FEED_DEFAULT, "F"); }
      if (!lastGood && (ticks & 7) === 3){ try{ viaFetch(VER_URL, "G"); }catch(e){} }
      if (busy && Date.now() - busyAt > 9000){ busy = false; fails++; lastErr = lastErr || "stuck"; }
      if (busy) return;
      if (fails >= 5){ directUntil = Date.now() + 60000; fails = 0; }
      if (window.SSNet && (useNative || (fails >= 3 && !lastGood))){
        useNative = true; busy = true; busyAt = Date.now(); dX = "native";
        try{ window.SSNet.get((Date.now() < directUntil ? FEED_DEFAULT : FEED_URL) + "?_=" + Date.now()); }
        catch(e){ busy = false; fails++; lastErr = "native exc"; }
        return;
      }
      busy = true; busyAt = Date.now();
      try{
      const x = new XMLHttpRequest();
      /* relay (config feedUrl) 5 baar lagatar fail ho to us waqt seedha original feed se le lo, taaki rates band na hon */
      if (fails >= 5){ directUntil = Date.now() + 60000; fails = 0; }
      x.open("GET", (Date.now() < directUntil ? FEED_DEFAULT : FEED_URL) + "?_=" + Date.now(), true);
      x.timeout = 5000; dX = "sent";
      dE = "";
      x.onreadystatechange = function(){ dX = "rs" + x.readyState + " st" + x.status + " len" + ((x.readyState === 4 && x.responseText) ? x.responseText.length : 0); };
      ["loadstart", "load", "error", "abort", "timeout", "loadend"].forEach(function(n){ x.addEventListener(n, function(){ dE += n.slice(0, 4) + " "; }); });
      x.onload = function(){
        busy = false;
        if (x.status === 200 && x.responseText && x.responseText.length > 20){
          gotFeed(x.responseText);
        } else { fails++; lastErr = "HTTP " + x.status + " len " + (x.responseText ? x.responseText.length : 0); }
        updBadge();
      };
      x.onerror = function(){ busy = false; fails++; lastErr = "network/ssl error"; updBadge(); };
      x.onabort = function(){ busy = false; fails++; lastErr = "aborted"; updBadge(); };
      x.ontimeout = function(){ busy = false; fails++; lastErr = "timeout"; updBadge(); };
      x.send();
      }catch(e){ busy = false; fails++; lastErr = "exc " + String(e).slice(0, 60); updBadge(); }
    }
    function updBadge(){
      if (!lastGood){ setBadge("off", "FEED OFFLINE"); noteFail(); document.getElementById("foot").textContent = "Feed error: " + (lastErr || "no reply") + " t" + ticks + (document.hidden ? " hidden" : "") + " " + (FEED_URL === FEED_DEFAULT ? "def" : "cfg") + " | " + ((navigator.userAgent.match(/Android [0-9.]+|Chrome\/[0-9]+/g) || []).join(" ")) + " | X:" + dX + " E:" + dE + " F:" + dF + " G:" + dG; return; }
      const age = (Date.now() - lastGood) / 1000;
      if (age >= 8) noteFail();
      if (age < 10) setBadge("live", "\\u25CF LIVE");
      else if (age < 60) setBadge("stale", "DATA " + Math.round(age) + "s OLD");
      else setBadge("off", "FEED OFFLINE");
    }
    setInterval(updBadge, 1000);

    ''' % FEED
    src = src[:t0] + new_tick + src[t1:]
    # poll rate: app me 3 sec (laptop 1 sec), config se 2-6 sec
    src = once(src, "const REFRESH_MS = 1000;", "let REFRESH_MS = 1000;")
    src = once(src, "setInterval(tick, REFRESH_MS); tick();", "(function loop(){ tick(); setTimeout(loop, REFRESH_MS); })();")


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
CALL_URL = "tel:+919009087382"
DOCK = """<nav class="dock" aria-label="Contact">
  <a id="dk-channel" href="%s" aria-label="WhatsApp Channel"><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#1faa59" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21l1.6-4.6A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 8.5c0 3.4 3.1 6.5 6.5 6.5l1.2-1.6-2.2-1.1-.9.8c-1-.4-1.9-1.3-2.3-2.3l.8-.9-1.1-2.2z" fill="#1faa59" stroke="none"/></svg></span><span class="lb">Channel</span></a>
  <a id="dk-instagram" href="%s" aria-label="Instagram"><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#d6249f" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.3" cy="6.7" r="1" fill="#d6249f" stroke="none"/></svg></span><span class="lb">Instagram</span></a>
  <a id="dk-location" href="%s" aria-label="Location"><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#d2403a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6" fill="#d2403a" stroke="none"/></svg></span><span class="lb">Location</span></a>
  <a id="dk-call" href="%s" aria-label="Call" hidden><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#2a6fdb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg></span><span class="lb">Call</span></a>
  <a id="dk-chat" href="%s" aria-label="WhatsApp chat" hidden><span class="ib"><svg viewBox="0 0 24 24" fill="none" stroke="#1faa59" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.4A8 8 0 1 1 21 12z"/></svg></span><span class="lb">Chat</span></a>
</nav>
""" % (WA_URL, IG_URL, MAP_URL, CALL_URL, "https://wa.me/919009087382")
# 2d) row: High/Low buy-sell ke neeche, bade fonts
src = once(src, '        <div class="n3">High ${it.high} · Low ${it.low}</div>\n      </div>\n      <div class="px"><span class="lbl">BUY</span>',
    '      </div>\n      <div class="px pb"><span class="lbl">BUY</span>')
src = once(src, '<span class="big ${it.p.bc}">${it.buy}</span></div>', '<span class="big ${it.p.bc}">${it.buy}</span><span class="hs">L - ${it.low}</span></div>')
src = once(src, '<div class="px"><span class="lbl">SELL</span><span class="big ${it.p.sc}">${it.sell}</span></div>\n    </div>`;',
    '<div class="px ps"><span class="lbl">SELL</span><span class="big ${it.p.sc}">${it.sell}</span><span class="hs">H - ${it.high}</span></div>\n      \n    </div>`;')
src = once(src, '      <div>\n        <div class="n1">', '      <div class="nm">\n        <div class="n1">')
# app: sirf SELL dikhao (BUY aur L line hata do); laptop me dono rehte hain
if not DESKTOP:
    src = once(src, '      <div class="px pb"><span class="lbl">BUY</span><span class="big ${it.p.bc}">${it.buy}</span><span class="hs">L - ${it.low}</span></div>\n', '')
    src = once(src, '<span class="hs">H - ${it.high}</span></div>', '<span class="hs lh"><span>L - ${it.low}</span><span>H - ${it.high}</span></span></div>')
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
HDR = """
  /* shop naam: bada, poori width bharta hai, sone jaisi chamak (shimmer) + logo halka dhadakta hai */
  .brand{align-items:center}
  .brand .bt{flex:1;min-width:0}
  @media (orientation: portrait){
    .brand h1{font-size:calc(2.6 * var(--u));letter-spacing:.06em;line-height:1.1;white-space:nowrap}
    .brand p{font-size:calc(1.15 * var(--u));letter-spacing:.05em;margin-top:calc(.35 * var(--u))}
    #logo{height:calc(6.4 * var(--u))}
  }
  #shopname{position:relative;padding-right:calc(.9 * var(--u));color:transparent;-webkit-text-fill-color:transparent;
    animation:nameIn .9s cubic-bezier(.2,.9,.3,1.2) both}
  #shopname::after{content:attr(data-text);position:absolute;left:0;top:0;z-index:2;padding-right:calc(.9 * var(--u));
    background:linear-gradient(100deg,var(--gold) 0%,var(--gold) 38%,#f2b705 50%,var(--gold) 62%,var(--gold) 100%);background-size:260% 100%;
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;animation:nameShine 3s ease-in-out infinite}
  #shopname::before{content:attr(data-text);position:absolute;left:0;top:0;z-index:1;padding-right:calc(.9 * var(--u));
    -webkit-text-fill-color:#825813;color:#825813;background:none;-webkit-background-clip:border-box;
    text-shadow:calc(0.075 * var(--u)) calc(0.085 * var(--u)) 0 #8a5f14,calc(0.150 * var(--u)) calc(0.170 * var(--u)) 0 #7d5412,calc(0.225 * var(--u)) calc(0.255 * var(--u)) 0 #70490f,calc(0.300 * var(--u)) calc(0.340 * var(--u)) 0 #633f0d,calc(.5 * var(--u)) calc(.7 * var(--u)) calc(.7 * var(--u)) rgba(80,50,5,.3)}
  #logo{animation:logoBeat 2.8s ease-in-out infinite;transform-origin:50% 55%;filter:drop-shadow(0 0 calc(.5 * var(--u)) rgba(199,154,59,.35))}
  #subtitle{animation:nameIn 1.1s .25s ease both}
  @keyframes nameShine{0%{background-position:130% 0}70%,100%{background-position:-30% 0}}
  @keyframes nameIn{from{opacity:0;transform:translateY(calc(-1 * var(--u))) scale(.96)}to{opacity:1;transform:none}}
  @keyframes logoBeat{0%,100%{transform:scale(1)}45%{transform:scale(1.07)}}
"""
SELLONLY = """
  /* app: sirf SELL, bade fonts */
  @media (orientation: portrait){
    .row{grid-template-columns:1fr auto;gap:calc(1.2 * var(--u));padding:calc(1.5 * var(--u)) calc(1.8 * var(--u))}
    .n1{font-size:calc(2.25 * var(--u))}
    .unit,.st{font-size:calc(1.3 * var(--u))}
    .lbl{font-size:calc(1.3 * var(--u));letter-spacing:.14em}
    .big{font-size:calc(4.7 * var(--u))}
    .hs{font-size:calc(1.75 * var(--u))}
    .hs.lh{display:flex;gap:calc(1.4 * var(--u));font-size:calc(1.5 * var(--u))}
  }
"""
TVCSS = """
  /* ===== Android TV (landscape): laptop jaisa layout, sirf SELL, dock nahi ===== */
  @media (orientation: landscape){
    body{padding-bottom:calc(1.5 * var(--u))}
    .dock{display:none}
    .left{grid-template-rows:none;grid-auto-rows:1fr}
    .row{grid-template-columns:1fr auto;gap:calc(2 * var(--u));padding:calc(.7 * var(--u)) calc(2 * var(--u))}
    .n1{font-size:calc(2.3 * var(--u))}
    .big{font-size:calc(3.7 * var(--u))}
    .lbl{font-size:calc(1 * var(--u))}
    .unit,.st{font-size:calc(1.15 * var(--u))}
    .hs.lh{display:flex;gap:calc(1.6 * var(--u));font-size:calc(1.35 * var(--u))}
    .brand h1{font-size:calc(3 * var(--u));letter-spacing:.08em;white-space:nowrap}
    #upgo{display:none}
  }
"""
GLASS = GLASS + BIG + HDR
if not DESKTOP: GLASS += SELLONLY + TVCSS
if DESKTOP: GLASS = GLASS.replace('  body{padding-bottom:calc(14 * var(--u))}\n', '')
src = once(src, "</style>", GLASS + "</style>")
if not DESKTOP: src = once(src, '<footer id="foot">', DOCK + '<footer id="foot">')

# 2e) tile label: "SILVER 90%" -> "SILVER"
assert src.count('label: "SILVER 90%"') == 2
src = src.replace('label: "SILVER 90%"', 'label: "SILVER"')
# 2f) app update checker (GitHub se version.json)
vm = re.search(r'android:versionCode="(\d+)"', open(os.path.join(root, "AndroidManifest.xml")).read())
VC = int(vm.group(1))
VER_URL = "https://raw.githubusercontent.com/siddharthkolan/ss-rates/main/version.json"
UPD_CSS = """
  #updbar{display:flex;align-items:center;gap:calc(1 * var(--u));border-radius:calc(2 * var(--u));padding:calc(.55 * var(--u)) calc(.6 * var(--u)) calc(.55 * var(--u)) 0;
    background:rgba(255,248,225,.62);border:1px solid rgba(255,255,255,.9);overflow:hidden;
    -webkit-backdrop-filter:blur(14px) saturate(1.5);backdrop-filter:blur(14px) saturate(1.5);
    box-shadow:0 calc(.4 * var(--u)) calc(1.6 * var(--u)) rgba(166,122,34,.2)}
  #updbar[hidden]{display:none}
  #updbar .umq{flex:1;min-width:0;overflow:hidden}
  #uptxt{display:inline-block;white-space:nowrap;padding-left:100%;font-weight:600;color:var(--ink);
    font-size:calc(1.35 * var(--u));animation:tkmove var(--dur,18s) linear infinite}
  #upgo{flex:none;display:inline-block;padding:calc(.8 * var(--u)) calc(1.6 * var(--u));border-radius:calc(3 * var(--u));
    font-family:inherit;font-weight:700;font-size:calc(1.3 * var(--u));text-decoration:none;white-space:nowrap;
    background:linear-gradient(135deg,#c79a3b,#a67a22);color:#fff;box-shadow:0 calc(.3 * var(--u)) calc(1 * var(--u)) rgba(166,122,34,.4)}
"""
UPD_HTML = ""
UPD_BAR = """<div id="updbar" hidden><div class="umq"><span id="uptxt"></span></div><a id="upgo" href="#">Update \U0001F389</a></div>
"""
UPD_JS = """
/* ---- app update check: sirf ek line + Update button (popup nahi, app roke bina chalti hai) ---- */
const APP_VER = %d, VER_URL = "%s";
const UPD_FUN = [
  "\U0001F680 Naya version aa gaya! Phone me nayi chamak lagwa lo \u2728",
  "\U0001F381 Surprise! Update taiyar hai, ek tap me naye features \U0001F60D",
  "\U0001F4AA App ne gym join kar liya! Naya version aur fit hai \U0001F60E",
  "\U0001F947 Sone jaisa naya update! Chamak badhane ke liye update karein \u2728",
  "\U0001F389 Party shuru! Naya version aaya, bas ek tap \U0001F973"
];
let updVar = 0;
function showUpdate(j){
  const t = document.getElementById("uptxt");
  if (document.getElementById("updbar").hidden){
    t.textContent = UPD_FUN[updVar++ %% UPD_FUN.length] + "   \u00B7   v" + j.versionName + " available" +
      (matchMedia("(orientation: landscape)").matches ? "   \u00B7   Downloader app me link kholein" : "");
    document.getElementById("updbar").hidden = false;
    const w = t.offsetWidth || 900; t.style.setProperty("--dur", Math.max(10, w / 70) + "s");
  }
  document.getElementById("upgo").setAttribute("href", j.apk);
}
function checkUpdate(){
  if (document.hidden) return;
  const x = new XMLHttpRequest();
  x.open("GET", VER_URL + "?_=" + Date.now(), true); x.timeout = 8000;
  x.onload = function(){
    try{ if (x.status !== 200) return; const j = JSON.parse(x.responseText);
      window.ssLatest = "  \\u00B7  latest v" + String(j.versionName).slice(0, 12);
      if (j.versionCode > APP_VER && j.apk) showUpdate(j); }catch(e){}
  };
  x.send();
}
/* pehli check fail ho (net abhi ready nahi) to 6 ghante rukna nahi: 4s, 20s, 60s par aur phir har 5 minute */
setTimeout(checkUpdate, 4000); setTimeout(checkUpdate, 20000); setTimeout(checkUpdate, 60000);
setInterval(checkUpdate, 5 * 60 * 1000);
document.addEventListener("visibilitychange", function(){ if (!document.hidden) setTimeout(checkUpdate, 1500); });
""" % (VC, VER_URL)
VN = re.search(r'android:versionName="([^"]+)"', open(os.path.join(root, "AndroidManifest.xml")).read()).group(1)
src = once(src, "</style>", UPD_CSS + "</style>")
if not DESKTOP: src = once(src, "</script>\n</body>", UPD_JS + "</script>\n</body>")
# footer me app version bhi
if not DESKTOP:
    src = once(src, '"Feed updated " + hhmmss(lastGood);', '"Feed updated " + hhmmss(lastGood) + "  \u00B7  v%s" + (window.ssLatest || "");' % VN)
    src = once(src, "</script>\n</body>", 'document.getElementById("foot").textContent = "v%s";\n' % VN + "</script>\n</body>")

# 2g) config.json (sirf data: text, links, rates, rang). Code kabhi download nahi hota.
CFG_URL = "https://raw.githubusercontent.com/siddharthkolan/ss-rates/main/config.json"
src = once(src, "<h1>SHREE SS JEWELLERS</h1>", '<h1 id="shopname">SHREE SS JEWELLERS</h1>')
src = once(src, "<p>JAORA (M.P.)", '<p id="subtitle">JAORA (M.P.)')
src = once(src, "</header>\n", '</header>\n<div id="banner" hidden></div>\n')
src = once(src, '"No internet connection"', 'MSG.net.t')
src = once(src, '"Please connect with internet."', 'MSG.net.p')
src = once(src, '"Rates will be updated soon"', 'MSG.soon.t')
src = once(src, '"Please try again after some time."', 'MSG.soon.p')
src = once(src, ":root{--u:2.2vw}", ":root{--fs:1;--u:calc(2.2vw * var(--fs))}")
CFG_CSS = """
  .dock a[hidden]{display:none}
  .dock .lb{display:block}
  #banner{padding:calc(1 * var(--u)) calc(1.6 * var(--u));border-radius:calc(2 * var(--u));text-align:center;
    font-weight:600;font-size:calc(1.5 * var(--u));color:var(--gold);white-space:pre-line;
    background:rgba(255,255,255,.5);border:1px solid rgba(255,255,255,.85);
    -webkit-backdrop-filter:blur(14px) saturate(1.5);backdrop-filter:blur(14px) saturate(1.5);
    box-shadow:0 calc(.5 * var(--u)) calc(2 * var(--u)) rgba(120,95,40,.14)}
  #banner[hidden]{display:none}
"""
CFG_JS = """
/* ---- config.json: sirf data (text, link, rates, rang). Har cheez check hoke lagti hai, code nahi chalta ---- */
const CFG_URL = "%s";
const MSG = {net:{t:"No internet connection", p:"Please connect with internet."},
             soon:{t:"Rates will be updated soon", p:"Please try again after some time."}};
function cS(v,n){ return (typeof v === "string") ? v.slice(0, n || 80) : null; }
function cEsc(s){ return s.replace(/[&<>"'`]/g, function(c){ return "&#" + c.charCodeAt(0) + ";"; }); }
function cN(v,lo,hi){ return (typeof v === "number" && isFinite(v) && v >= lo && v <= hi) ? v : null; }
function cCol(v){ return (typeof v === "string" && /^#[0-9a-fA-F]{6}$/.test(v)) ? v : null; }
function cUrl(v){ return (typeof v === "string" && v.length < 400 && /^(https:\\/\\/|tel:\\+?\\d{6,15}$)/.test(v)) ? v : null; }
function cId(v){ return (typeof v === "string" && /^\\d{1,6}$/.test(v)) ? v : null; }
function cIds(a){ if (!Array.isArray(a)) return null; const o = []; a.slice(0, 12).forEach(function(v){ const k = cId(v); if (k) o.push(k); }); return o; }
function devCfg(c){
  try{
    const tv = (window.SSNet && window.SSNet.tv) ? !!window.SSNet.tv() : window.matchMedia("(orientation: landscape)").matches;
    const o = tv ? c.tv : c.phone;
    const r = {}; for (const k in c) if (k !== "tv" && k !== "phone") r[k] = c[k];
    if (o && typeof o === "object") for (const k2 in o) r[k2] = o[k2];
    return r;
  }catch(e){ return c; }
}
function applyCfg(c){
  c = devCfg(c);
  if (!c || typeof c !== "object") return;
  let s, n;
  if ((s = cS(c.shopName, 40))) { document.getElementById("shopname").textContent = s; fitName(); }
  if ((s = cS(c.subtitle, 70))) document.getElementById("subtitle").textContent = s;
  const bn = document.getElementById("banner");
  if (c.banner && c.banner.show === true && (s = cS(c.banner.text, 200))){
    bn.textContent = s; bn.style.color = cCol(c.banner.color) || ""; bn.hidden = false;
  } else { bn.hidden = true; }
  if (c.links && typeof c.links === "object"){
    ["channel","instagram","location","call","chat"].forEach(function(k){
      const l = c.links[k], a = document.getElementById("dk-" + k);
      if (!l || !a) return;
      if (typeof l.show === "boolean") a.hidden = !l.show;
      if ((s = cS(l.label, 14))) a.querySelector(".lb").textContent = s;
      if ((s = cUrl(l.url))) a.setAttribute("href", s);
    });
  }
  let ids;
  if ((ids = cIds(c.leftIds)) && ids.length) LEFT_IDS.splice(0, LEFT_IDS.length, ...ids);
  if ((ids = cIds(c.hideIds))) HIDE_IDS.splice(0, HIDE_IDS.length, ...ids);
  if (c.adjust && typeof c.adjust === "object"){
    Object.keys(ADJUST).forEach(function(k){ delete ADJUST[k]; });
    Object.keys(c.adjust).slice(0, 30).forEach(function(k){ const v = cN(c.adjust[k], -100000, 100000); if (cId(k) && v !== null) ADJUST[k] = v; });
  }
  if (Array.isArray(c.jewellery)){
    const cards = [];
    c.jewellery.slice(0, 4).forEach(function(cd){
      if (!cd || !Array.isArray(cd.items)) return;
      const t = cS(cd.title, 20), g = cN(cd.gst, 0, 28), items = [];
      cd.items.slice(0, 4).forEach(function(it){
        const src_ = cId(it && it.src), lb = cS(it && it.label, 14), f = cN(it && it.factor, 0.05, 2);
        const u = it && (it.unit === "10g" || it.unit === "kg") ? it.unit : null;
        if (src_ && lb && f !== null && u) items.push({src: src_, label: cEsc(lb), factor: f, unit: u});
      });
      if (t && g !== null && items.length) cards.push({title: cEsc(t), gst: g, items: items});
    });
    if (cards.length) JEWELLERY.splice(0, JEWELLERY.length, ...cards);
  }
  const th = c.theme;
  if (th && typeof th === "object"){
    const root = document.documentElement.style;
    ["gold","ink","muted","up","down","bg"].forEach(function(k){ const v = cCol(th[k]); if (v) root.setProperty("--" + k, v); });
    if ((n = cN(th.fontScale, 0.85, 1.25)) !== null) root.setProperty("--fs", String(n));
  }
  const m = c.messages;
  if (m && typeof m === "object"){
    ["net","soon"].forEach(function(k){ const e = m[k]; if (!e) return;
      if ((s = cS(e.title, 40))) MSG[k].t = s; if ((s = cS(e.text, 80))) MSG[k].p = s; });
  }
}
(function(){ try{ const c = localStorage.getItem("ssrates_cfg"); if (c) applyCfg(JSON.parse(c)); }catch(e){} })();
function loadCfg(){
  const x = new XMLHttpRequest();
  x.open("GET", CFG_URL + "?_=" + Date.now(), true); x.timeout = 8000;
  x.onload = function(){
    try{ if (x.status !== 200) return; const c = JSON.parse(x.responseText);
      if (typeof c !== "object" || c === null) return;
      applyCfg(c); localStorage.setItem("ssrates_cfg", x.responseText); }catch(e){}
  };
  x.send();
}
setTimeout(loadCfg, 1500);
setInterval(loadCfg, 10 * 60 * 1000);
document.addEventListener("visibilitychange", function(){ if (!document.hidden) setTimeout(loadCfg, 1000); });
""" % CFG_URL
src = once(src, "</style>", CFG_CSS + "</style>")
src = once(src, "</script>\n</body>", CFG_JS + "</script>\n</body>")

# 2h) funny popup + sound + "rates wapas aa gaye" toast
FUN_CSS = """
  @keyframes wob{0%,100%{transform:rotate(-8deg) translateY(0)}50%{transform:rotate(8deg) translateY(-6%)}}
  @keyframes bounce{0%,100%{transform:translateY(0) scale(1)}40%{transform:translateY(-22%) scale(1.08)}60%{transform:translateY(0) scale(.96)}}
  @keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-8%)}40%{transform:translateX(8%)}60%{transform:translateX(-5%)}80%{transform:translateX(5%)}}
  @keyframes popin{0%{transform:scale(.6);opacity:0}100%{transform:scale(1);opacity:1}}
  @keyframes drop{0%{transform:translate(-50%,-160%);opacity:0}15%{transform:translate(-50%,0);opacity:1}85%{transform:translate(-50%,0);opacity:1}100%{transform:translate(-50%,-160%);opacity:0}}
  #notice .box{animation:popin .35s ease-out;white-space:pre-line}
  #notice .ic{display:inline-block;font-size:calc(7 * var(--u));line-height:1.1}
  #notice.net .ic{animation:shake .7s infinite}
  #notice.soon .ic{animation:wob 1.2s ease-in-out infinite}
  #notice h2{font-size:calc(2.1 * var(--u))}
  #notice p{font-size:calc(1.5 * var(--u))}
  #notice .box{position:relative}
  #notice .nx{position:absolute;top:calc(.9 * var(--u));right:calc(.9 * var(--u));width:calc(3.6 * var(--u));height:calc(3.6 * var(--u));border:0;border-radius:50%;
    background:rgba(0,0,0,.07);color:#6b6254;font-size:calc(2 * var(--u));line-height:1;cursor:pointer;padding:0;font-family:inherit}
  #notice .nx:focus,#notice .snd:focus{outline:calc(.3 * var(--u)) solid #c79a3b}
  #notice .snd{margin-top:calc(1.4 * var(--u));border:0;border-radius:calc(2 * var(--u));padding:calc(.7 * var(--u)) calc(1.4 * var(--u));
    background:rgba(0,0,0,.06);color:var(--muted);font:inherit;font-size:calc(1.2 * var(--u));cursor:pointer}
  #back{position:fixed;left:50%;top:calc(env(safe-area-inset-top,0px) + 2 * var(--u));z-index:60;transform:translate(-50%,-260%);visibility:hidden;
    padding:calc(1.1 * var(--u)) calc(2 * var(--u));border-radius:calc(3 * var(--u));font-weight:700;font-size:calc(1.6 * var(--u));
    color:var(--up);background:rgba(255,255,255,.75);border:1px solid rgba(255,255,255,.9);white-space:nowrap;
    -webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);box-shadow:0 calc(.8 * var(--u)) calc(3 * var(--u)) rgba(60,45,15,.25)}
  #back.show{visibility:visible;animation:drop 5s ease-in-out forwards}
  #back .em{display:inline-block;animation:bounce .8s infinite}
"""
FUN_HTML = '<div id="back" role="status"></div>\n'
FUN_JS = """
/* ---- funny popup, sound, aur "rates wapas" toast ---- */
let ssMuted = false, ssDown = false, ssAc = null, ssVar = 0;
try{ ssMuted = localStorage.getItem("ss_mute") === "1"; }catch(e){}
function ssCtx(){ try{ ssAc = ssAc || new (window.AudioContext || window.webkitAudioContext)();
  if (ssAc.state === "suspended") ssAc.resume(); }catch(e){} return ssAc; }
document.addEventListener("touchstart", function(){ ssCtx(); }, {once:true});
document.addEventListener("click", function(){ ssCtx(); }, {once:true});
function ssTone(f1, f2, t0, d, type, vol){
  const a = ssCtx(); if (!a) return;
  const o = a.createOscillator(), g = a.createGain(), t = a.currentTime + t0;
  o.type = type; o.frequency.setValueAtTime(f1, t); if (f2 !== f1) o.frequency.exponentialRampToValueAtTime(f2, t + d);
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(g); g.connect(a.destination); o.start(t); o.stop(t + d + 0.05);
}
function ssSfx(kind){
  if (ssMuted || document.hidden) return;
  if (kind === "net"){            /* halki, meethi ding-dong (public jagah par bhi theek) */
    ssTone(659, 659, 0, .55, "sine", .06); ssTone(1318, 1318, 0, .35, "sine", .015);
    ssTone(523, 523, .3, .8, "sine", .06); ssTone(1046, 1046, .3, .45, "sine", .015);
  } else if (kind === "soon"){    /* boop boop boing */
    ssTone(660, 660, 0, .09, "square", .05); ssTone(880, 880, .14, .09, "square", .05);
    ssTone(660, 660, .28, .09, "square", .05); ssTone(300, 800, .45, .3, "sine", .12);
  } else {                        /* tada: C E G C */
    ssTone(523, 523, 0, .13, "triangle", .13); ssTone(659, 659, .12, .13, "triangle", .13);
    ssTone(784, 784, .24, .13, "triangle", .13); ssTone(1047, 1047, .36, .5, "triangle", .14);
    ssTone(1568, 1568, .5, .35, "sine", .05);
  }
}
const FUN = {
  net: {em: ["\\uD83D\\uDCE1", "\\uD83D\\uDE35\\u200D\\uD83D\\uDCAB", "\\uD83C\\uDFC3\\uD83D\\uDCA8"], v: [
    ["Arre! Internet bhaag gaya \\uD83C\\uDFC3\\uD83D\\uDCA8", "Net ko pakad ke wapas laao, tab tak rates chhutti par hain \\uD83D\\uDE34"],
    ["Net ne chhutti le li \\uD83C\\uDFD6\\uFE0F", "WiFi ya data on karo, phir milte hain \\uD83D\\uDE0E"],
    ["Hello? Koi hai? \\uD83D\\uDC40", "Internet ghar chhod ke chala gaya lagta hai \\uD83E\\uDD72"]]},
  soon: {em: ["\\u23F3", "\\uD83D\\uDC22", "\\u2615"], v: [
    ["Rates chai peene gaye hain \\u2615", "Bas aate hi honge, thoda sabr rakho \\uD83D\\uDE4F"],
    ["Rates kachhua ki speed se aa rahe hain \\uD83D\\uDC22", "Ek-do minute baad dobara dekhna \\uD83D\\uDE09"],
    ["Sone ko bhi aaram chahiye \\uD83D\\uDE34\\u2728", "Rates jaldi hi fresh hokar aayenge \\uD83D\\uDCAB"]]}
};
let ssDismissed = false;
showNotice = function(kind){
  const n = document.getElementById("notice");
  if (document.hidden || ssDismissed || (!n.hidden && n.className === kind)) return;
  ssDown = true;
  const f = FUN[kind], i = ssVar++ % f.v.length, m = MSG[kind];
  const ic = document.getElementById("nic"); ic.textContent = f.em[i];
  document.getElementById("nh").textContent = f.v[i][0];
  document.getElementById("np").textContent = f.v[i][1] + "\\n\\n" + m.t + "\\n" + m.p;
  let b = document.getElementById("snd");
  if (!b){ b = document.createElement("button"); b.id = "snd"; b.type = "button"; b.className = "snd";
    b.addEventListener("click", function(){ ssMuted = !ssMuted; try{ localStorage.setItem("ss_mute", ssMuted ? "1" : "0"); }catch(e){}
      b.textContent = ssMuted ? "\\uD83D\\uDD07 Sound off" : "\\uD83D\\uDD0A Sound on"; if (!ssMuted) ssSfx(document.getElementById("notice").className); });
    document.querySelector("#notice .box").appendChild(b); }
  b.textContent = ssMuted ? "\\uD83D\\uDD07 Sound off" : "\\uD83D\\uDD0A Sound on";
  let x = document.getElementById("nx");
  if (!x){ x = document.createElement("button"); x.id = "nx"; x.type = "button"; x.className = "nx"; x.textContent = "\\u2715"; x.setAttribute("aria-label", "Close");
    x.addEventListener("click", function(){ ssDismissed = true; ssDown = false; hideNotice(); });
    document.querySelector("#notice .box").appendChild(x); }
  n.className = kind; n.hidden = false;
  try{ x.focus(); }catch(e){}
  ssSfx(kind);
};
noteOK = function(){
  okAt = Date.now(); hideNotice(); ssDismissed = false;
  if (ssDown){
    ssDown = false;
    const t = document.getElementById("back");
    t.innerHTML = '<span class="em">\\uD83C\\uDF89</span> Rates wapas aa gaye! Ab ekdum fresh \\uD83D\\uDD25';
    t.classList.remove("show"); void t.offsetWidth; t.classList.add("show");
    ssSfx("back");
  }
};
""" 
src = once(src, "</style>", FUN_CSS + "</style>")
src = once(src, '<footer id="foot">', FUN_HTML + '<footer id="foot">')
src = once(src, "</script>\n</body>", FUN_JS + "</script>\n</body>")

# 2i) running line (ticker) header ke neeche
TK_TEXT = "Sometimes rates mai kuch difference aa sakta hai. Ek baar 100% accurate rates ke liye contact zarur kar lijiye. Dhanyavaad \U0001F64F"
TK_CSS = """
  #ticker{overflow:hidden;border-radius:calc(2 * var(--u));padding:calc(.8 * var(--u)) 0;
    background:rgba(255,255,255,.5);border:1px solid rgba(255,255,255,.85);
    -webkit-backdrop-filter:blur(14px) saturate(1.5);backdrop-filter:blur(14px) saturate(1.5);
    box-shadow:0 calc(.4 * var(--u)) calc(1.6 * var(--u)) rgba(120,95,40,.12)}
  #ticker[hidden]{display:none}
  #tk{display:inline-block;white-space:nowrap;padding-left:100%;font-weight:600;color:var(--gold);
    font-size:calc(1.35 * var(--u));animation:tkmove var(--dur,22s) linear infinite}
  @keyframes tkmove{to{transform:translateX(-100%)}}
"""
src = once(src, '<div id="banner" hidden></div>\n', '<div id="ticker"><span id="tk"></span></div>\n' + UPD_BAR + '<div id="banner" hidden></div>\n')
src = once(src, "</style>", TK_CSS + "</style>")
TK_JS = """
/* ---- running line ---- */
function fitName(){
  const h = document.getElementById("shopname"); if (!h) return;
  h.style.fontSize = ""; h.setAttribute("data-text", h.textContent);
  const box = h.parentElement; let fs = parseFloat(getComputedStyle(h).fontSize), n = 0;
  while (h.scrollWidth > box.clientWidth + 1 && fs > 10 && n++ < 40){ fs -= 1; h.style.fontSize = fs + "px"; }
}
window.addEventListener("resize", fitName);
if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitName);
setTimeout(fitName, 300);
function setTicker(text){
  const t = document.getElementById("tk"); t.textContent = text;
  const w = t.offsetWidth || 1200; t.style.setProperty("--dur", Math.max(10, w / 70) + "s");
}
setTicker(%s);
""" % __import__("json").dumps(TK_TEXT)
src = once(src, "</script>\n</body>", TK_JS + "</script>\n</body>")
src = once(src, '  const bn = document.getElementById("banner");',
 '  if (c.ticker && typeof c.ticker === "object"){\n'
 '    document.getElementById("ticker").hidden = (c.ticker.show === false);\n'
 '    if ((s = cS(c.ticker.text, 300))) setTicker(s);\n'
 '  }\n'
 '  if (typeof FEED_DEFAULT !== "undefined"){\n'
 '  FEED_URL = (typeof c.feedUrl === "string" && /^https:\\/\\/[^\\s"\'<>]{4,290}$/.test(c.feedUrl)) ? c.feedUrl : FEED_DEFAULT;\n'
 '  if (typeof c.refreshMs === "number" && c.refreshMs >= 1000 && c.refreshMs <= 6000) REFRESH_MS = Math.round(c.refreshMs);\n'
 '  }\n'
 '  const bn = document.getElementById("banner");')

# 2j) app background (recents / app switch) me popup, sound aur check band
BG_JS = """
/* ---- background guard: app recents me ho to na popup, na sound, na polling ---- */
const ssNoteFail = noteFail;
noteFail = function(){ if (document.hidden) return; ssNoteFail(); };
document.addEventListener("visibilitychange", function(){
  if (document.hidden){
    ssDown = false; hideNotice();
    try{ if (ssAc) ssAc.suspend(); }catch(e){}
  } else {
    okAt = Date.now();          /* wapas aane par 6 sec ka grace, tab tak koi popup nahi */
    hideNotice(); ssDown = false;
    try{ if (ssAc) ssAc.resume(); }catch(e){}
    setTimeout(tick, 200);
  }
});
"""
src = once(src, "</script>\n</body>", BG_JS + "</script>\n</body>")
# kacchi silver (7634) panel hide
src = once(src, 'const LEFT_IDS   = ["7291", "7386", "7627", "7363", "7634"];', 'const LEFT_IDS   = ["7291", "7386", "7627", "7363"];')
src = once(src, "const HIDE_IDS   = [];", 'const HIDE_IDS   = ["7634"];')

DESK_MENU_HTML = """<div id="mn" hidden>
  <button id="mnb" type="button" aria-label="Menu">\u22EE</button>
  <div id="mnp" hidden>
    <div class="mrow"><div><div class="mt">PC ke saath auto start</div><div class="ms" id="mns">...</div></div>
      <button id="mnt" type="button" role="switch" aria-checked="false" aria-label="Auto start"><span></span></button></div>
  </div>
</div>
"""
DESK_MENU_JS = """
/* ---- 3 dot menu: auto start on/off (sirf .exe wale board me dikhta hai) ---- */
(function(){
  const box = document.getElementById("mn"), b = document.getElementById("mnb"), p = document.getElementById("mnp"),
        t = document.getElementById("mnt"), st = document.getElementById("mns"); let tm = 0;
  const H = {"X-SS-Board": "1"};
  function ui(on){ t.setAttribute("aria-checked", on ? "true" : "false"); t.className = on ? "on" : "";
    st.textContent = on ? "ON \u2014 PC chalu hote hi board khul jayega" : "OFF \u2014 board haath se kholna padega"; }
  function arm(){ clearTimeout(tm); tm = setTimeout(function(){ p.hidden = true; }, 10000); }
  fetch("/api/startup", {headers: H, cache: "no-store"}).then(function(r){ return r.ok ? r.json() : Promise.reject(); })
    .then(function(j){ ui(!!j.on); box.hidden = false; }).catch(function(){});
  b.addEventListener("click", function(e){ e.stopPropagation(); p.hidden = !p.hidden; if (!p.hidden) arm(); });
  p.addEventListener("click", function(e){ e.stopPropagation(); arm(); });
  document.addEventListener("click", function(){ p.hidden = true; });
  t.addEventListener("click", function(){
    const want = t.getAttribute("aria-checked") !== "true"; t.disabled = true;
    fetch("/api/startup", {method: "POST", headers: {"X-SS-Board": "1", "Content-Type": "application/json"}, body: JSON.stringify({on: want})})
      .then(function(r){ return r.ok ? r.json() : Promise.reject(); }).then(function(j){ ui(!!j.on); })
      .catch(function(){ st.textContent = "Badal nahi paya, dobara try karein"; }).then(function(){ t.disabled = false; });
  });
})();
"""
DESK_UPD_JS = """
/* ---- exe update check: sirf ek line + Update button (naya .exe aane par) ---- */
const EXE_VER = /*EXE_VER*/0, EXE_NAME = "/*EXE_NAME*/", EXE_VER_URL = "https://raw.githubusercontent.com/siddharthkolan/ss-rates/main/desktop-version.json";
const UPD_FUN = [
  "\U0001F680 Naya version aa gaya! Rate board me nayi chamak \u2728",
  "\U0001F381 Surprise! Update taiyar hai, naye features \U0001F60D",
  "\U0001F4AA Board ne gym join kar liya! Naya version aur fit hai \U0001F60E",
  "\U0001F389 Party shuru! Naya version aaya, bas ek click \U0001F973"
];
let updVar = 0;
function checkUpdate(){
  if (!EXE_VER || document.hidden) return;   // .exe ke bahar (serve.py) kuch nahi
  const x = new XMLHttpRequest();
  x.open("GET", EXE_VER_URL + "?_=" + Date.now(), true); x.timeout = 8000;
  x.onload = function(){
    try{ if (x.status !== 200) return; const j = JSON.parse(x.responseText);
      if (j.versionCode > EXE_VER && typeof j.exe === "string" && /^https:\\/\\//.test(j.exe)){
        const t = document.getElementById("uptxt"), bar = document.getElementById("updbar");
        if (bar.hidden){
          t.textContent = UPD_FUN[updVar++ %% UPD_FUN.length] + "   \u00B7   v" + String(j.versionName).slice(0, 12) + " available";
          bar.hidden = false;
          const w = t.offsetWidth || 900; t.style.setProperty("--dur", Math.max(10, w / 70) + "s");
        }
        const a = document.getElementById("upgo"); a.setAttribute("href", j.exe); a.setAttribute("target", "_blank"); a.setAttribute("rel", "noopener");
      } }catch(e){}
  };
  x.send();
}
setTimeout(checkUpdate, 4000); setTimeout(checkUpdate, 20000); setTimeout(checkUpdate, 60000);
setInterval(checkUpdate, 5 * 60 * 1000);
document.addEventListener("visibilitychange", function(){ if (!document.hidden) setTimeout(checkUpdate, 1500); });
""".replace("%%", "%")
DESK_CSS = """
  /* ===== desktop / TV (landscape) ===== */
  @media (orientation: landscape){
    html,body{height:100%}
    .left{grid-template-rows:none;grid-auto-rows:1fr}
    #ticker{margin:0}
    .brand h1{font-size:calc(3 * var(--u));letter-spacing:.08em}
  }
  #mn{position:fixed;right:calc(1.2 * var(--u));bottom:calc(.8 * var(--u));z-index:30}
  #mn[hidden],#mnp[hidden]{display:none}
  #mnb{width:calc(3.2 * var(--u));height:calc(3.2 * var(--u));border-radius:50%;border:1px solid rgba(255,255,255,.8);
    background:rgba(255,255,255,.45);color:var(--ink);font-size:calc(2.2 * var(--u));line-height:1;cursor:pointer;opacity:.35;transition:opacity .2s;
    -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
  #mn:hover #mnb,#mnb:focus{opacity:1}
  #mnp{position:absolute;right:0;bottom:calc(4 * var(--u));width:calc(26 * var(--u));padding:calc(1.4 * var(--u)) calc(1.6 * var(--u));
    border-radius:calc(1.6 * var(--u));background:rgba(255,255,255,.82);border:1px solid rgba(255,255,255,.95);
    -webkit-backdrop-filter:blur(18px) saturate(1.5);backdrop-filter:blur(18px) saturate(1.5);box-shadow:0 calc(.8 * var(--u)) calc(3 * var(--u)) rgba(60,45,15,.25)}
  #mnp .mrow{display:flex;align-items:center;justify-content:space-between;gap:calc(1.2 * var(--u))}
  #mnp .mt{font-weight:700;font-size:calc(1.15 * var(--u));color:var(--ink)}
  #mnp .ms{font-size:calc(.9 * var(--u));color:var(--muted);margin-top:calc(.3 * var(--u))}
  #mnt{flex:none;position:relative;width:calc(4.6 * var(--u));height:calc(2.6 * var(--u));border-radius:calc(2 * var(--u));border:0;background:#c9c2b0;cursor:pointer;transition:background .2s}
  #mnt span{position:absolute;top:calc(.3 * var(--u));left:calc(.3 * var(--u));width:calc(2 * var(--u));height:calc(2 * var(--u));border-radius:50%;background:#fff;transition:transform .2s;box-shadow:0 1px 3px rgba(0,0,0,.3)}
  #mnt.on{background:#1f9d62}
  #mnt.on span{transform:translateX(calc(2 * var(--u)))}
"""
src_menu = True
# 2k) sirf jewellery rates (left khali) => center me, bade, orientation ke hisab se
JONLY_CSS = """
  /* sirf jewellery rates: left khali ho to rates center me, size auto */
  .jonly .left{display:none}
  @media (orientation: landscape){
    .jonly .main{display:flex;align-items:stretch}
    .jonly .right{flex:1;display:grid;grid-template-columns:repeat(var(--jc,1),1fr);grid-template-rows:repeat(var(--jr,2),1fr);gap:calc(1.4 * var(--u))}
    .jonly .gcard{padding:calc(1.2 * var(--u)) calc(1.8 * var(--u));justify-content:center}
    .jonly .gtop h3{font-size:calc(2.2 * var(--u))}
    .jonly .gtop .src{font-size:calc(1.3 * var(--u))}
    .jonly .tiles{margin-top:calc(1 * var(--u));gap:calc(1.2 * var(--u))}
    .jonly .tile{padding:calc(.6 * var(--u)) calc(1.4 * var(--u))}
    .jonly .tile .k{font-size:calc(1.7 * var(--u))}
    .jonly .tile .ut{font-size:calc(1.2 * var(--u))}
    .jonly .tile .v{font-size:calc(5 * var(--u))}
    .jonly .tile .g{font-size:calc(1.5 * var(--u))}
    .jonly.jc2 .gtop h3{font-size:calc(1.6 * var(--u))}
    .jonly.jc2 .tile .k{font-size:calc(1.2 * var(--u))}
    .jonly.jc2 .tile .v{font-size:calc(3.2 * var(--u))}
    .jonly.jc2 .tile .g{font-size:calc(1.1 * var(--u))}
  }
  @media (orientation: portrait){
    .jonly .main{flex:1;justify-content:center}
    .jonly .gtop h3{font-size:calc(1.5 * var(--u))}
    .jonly .tile .v{font-size:calc(2.9 * var(--u))}
  }
"""
JONLY_JS = """  { const lf = document.getElementById("left"), rg = document.getElementById("right");
    document.body.classList.toggle("jonly", lf.children.length === 0 && rg.children.length > 0);
    const n = rg.children.length, cols = n > 2 ? 2 : 1;
    rg.style.setProperty("--jc", cols); rg.style.setProperty("--jr", Math.max(Math.ceil(n / cols), 1));
    document.body.classList.toggle("jc2", cols === 2); }
  /* BOTTOM STRIP: baaki rates */"""
src = once(src, "  /* BOTTOM STRIP: baaki rates */", JONLY_JS)
src = once(src, "</style>", JONLY_CSS + "</style>")
# 3) logo relative
if not DESKTOP:
    src = once(src, 'img.src = "/" + names[i]', 'img.src = names[i]')
    src = once(src, 'img.src = "/" + names[0]', 'img.src = names[0]')
# 3b) error footer par bhi version dikhe
if not DESKTOP: src = once(src, '"Feed error: " + (lastErr', '"v%s  Feed error: " + (lastErr' % VN)
# 4) footer
src = src.replace("   ·   F = full screen", "").replace("F = full screen", "")
os.makedirs(os.path.join(root, "assets"), exist_ok=True)
if DESKTOP:
    src = src.replace("<title>Shree SS Jewellers - Live Rates</title>", '<title>Shree SS Jewellers - Rate Board</title>\n<link rel="icon" type="image/png" href="/favicon.png">', 1)
    src = once(src, "</style>", DESK_CSS + "</style>")
    src = once(src, '<footer id="foot">', DESK_MENU_HTML + '<footer id="foot">')
    src = once(src, "</script>\n</body>", DESK_MENU_JS + DESK_UPD_JS + "</script>\n</body>")
    src = once(src, 'hhmmss(j.fetched_at*1000) + "";', 'hhmmss(j.fetched_at*1000) + (EXE_VER ? "  \\u00B7  v" + EXE_NAME : "");')
    open(os.path.join(root, "..", "rate_board_desktop.html"), "w", encoding="utf-8").write(src)
    print("desktop page ready"); sys.exit(0)
open(os.path.join(root, "assets", "index.html"), "w", encoding="utf-8").write(src)
print("ok", len(src))
