#!/usr/bin/env python3
"""Ek hi command se poora release: version bump -> build -> verify -> (optional) GitHub push.

  python3 release.py --bump "2.4" --notes "Kya naya hai"      # naya version
  python3 release.py                                           # wahi version dobara build + check
  python3 release.py --bump "2.4" --notes "..." --push         # build + check + GitHub par upload

Version sirf AndroidManifest.xml me badalta hai. make_app_html.py usi se padhta hai.
Koi bhi check fail ho to script ruk jati hai aur kuch upload nahi hota."""
import argparse, hashlib, json, os, re, struct, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SCR = os.environ.get("SS_TOOLS", "/tmp/claude-0/-home-claude/e604aac6-2c59-52c7-bf86-22759ea196e3/scratchpad")
AAPT = f"{SCR}/tools/aapt/bin/x64/linux/aapt2"
BUILD = f"{SCR}/build"
REPO = os.environ.get("SS_REPO", "/home/claude/ss-rates")
MAN = os.path.join(ROOT, "AndroidManifest.xml")
OUT = os.path.join(ROOT, "out", "SS-Rates.apk")
CERT_SHA = "671a88640d779030b80405889d75aa36d2743cc6d7a6cc32a72c94bec748b709"
APK_URL = "https://raw.githubusercontent.com/siddharthkolan/ss-rates/main/SS-Rates.apk"

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode: sys.exit(f"FAIL: {' '.join(cmd[:3])}...\n{r.stdout}{r.stderr}")
    return r.stdout

def fail(msg): sys.exit("CHECK FAILED: " + msg)

ap = argparse.ArgumentParser()
ap.add_argument("--bump"); ap.add_argument("--notes", default=""); ap.add_argument("--push", action="store_true")
a = ap.parse_args()

m = open(MAN).read()
code = int(re.search(r'android:versionCode="(\d+)"', m).group(1))
name = re.search(r'android:versionName="([^"]+)"', m).group(1)
if a.bump:
    code += 1; name = a.bump
    m = re.sub(r'android:versionCode="\d+"', f'android:versionCode="{code}"', m)
    m = re.sub(r'android:versionName="[^"]+"', f'android:versionName="{name}"', m)
    open(MAN, "w").write(m)
print(f"Release v{name} (code {code})")

# 1) UI (version manifest se baked hota hai, isliye manifest bump ke BAAD)
run([sys.executable, os.path.join(ROOT, "make_app_html.py")])
# 1b) dex: smali se hamesha dobara (MainActivity/ExtClient badle ho sakte hain)
J = f"{SCR}/tools/apktool/bin/apktool_2.4.1.jar"
run(["java", "-cp", f"{J}:{BUILD}/tools", "SmaliRun", os.path.join(ROOT, "src", "smali"), f"{BUILD}/classes.dex", "19"])
# 2) resources + manifest
os.path.exists(f"{BUILD}/res.zip") and os.remove(f"{BUILD}/res.zip")
run([AAPT, "compile", "--dir", os.path.join(ROOT, "res"), "-o", f"{BUILD}/res.zip"])
run([AAPT, "link", "-I", f"{BUILD}/fakefw.apk", "--manifest", MAN, "-R", f"{BUILD}/res.zip", "-o", f"{BUILD}/base.apk",
     "--compile-sdk-version-code", "34", "--compile-sdk-version-name", "14", "--emit-ids", f"{BUILD}/ids.txt", "--auto-add-overlay"])
# 3) assemble + sign
os.makedirs(os.path.dirname(OUT), exist_ok=True)
run([sys.executable, os.path.join(ROOT, "build_apk.py"), f"{BUILD}/base.apk", f"{BUILD}/classes.dex",
     os.path.join(ROOT, "assets"), OUT])

# ---------------- verify ----------------
badging = run([AAPT, "dump", "badging", OUT])
mm = re.search(r"versionCode='(\d+)' versionName='([^']+)'", badging)
if (int(mm.group(1)), mm.group(2)) != (code, name): fail(f"APK manifest {mm.groups()} != {(code, name)}")
for perm in ("android.permission.INTERNET", "android.permission.POST_NOTIFICATIONS", "android.permission.RECEIVE_BOOT_COMPLETED"):
    if f"uses-permission: name='{perm}'" not in badging: fail(f"manifest me {perm} nahi")
xt = run([AAPT, "dump", "xmltree", "--file", "AndroidManifest.xml", OUT])
if "banner" not in xt or "tv_banner" not in xt and "res/" not in xt: fail("TV banner manifest me nahi")
if "PollJob" not in xt or "android.permission.BIND_JOB_SERVICE" not in xt: fail("PollJob service/BIND_JOB_SERVICE manifest me nahi")
z = zipfile.ZipFile(OUT)
if not any(n.endswith("ic_stat.png") for n in z.namelist()): fail("ic_stat icon APK me nahi")
if not any("tv_banner" in n for n in z.namelist()): fail("tv_banner APK me nahi")
if z.testzip(): fail("zip corrupt")
html = z.read("assets/index.html").decode()
if f"const APP_VER = {code}," not in html: fail("app ke andar APP_VER manifest se alag hai")
if f"\u00B7  v{name}\"" not in html: fail("app ke andar versionName manifest se alag hai")
if 'id="updbar"' not in html or 'id="upd"' in html: fail("update bar/popup galat")
for need in ("https://whatsapp.com/channel/0029VbBrPE50bIdlNTKXtr1S", "instagram.com/ss_jewellers_jaora", "setTicker(", "loadCfg"):
    if need not in html: fail(f"index.html me {need} nahi mila")
if "ss__jewellers" in html: fail("purana instagram handle mila")
for e in z.infolist():
    if e.filename == "resources.arsc" and (e.compress_type != 0 or (e.header_offset + 30 + len(e.filename) + len(e.extra)) % 4): fail("resources.arsc stored/aligned nahi")
raw = open(OUT, "rb").read()
eo = raw.rfind(b"PK\x05\x06"); cds, cdo = struct.unpack("<II", raw[eo + 12: eo + 20])
if raw[cdo - 16:cdo] != b"APK Sig Block 42": fail("v2 signing block nahi mila")
bs = struct.unpack("<Q", raw[cdo - 24:cdo - 16])[0]; start = cdo - bs - 8
v2 = raw[start + 8 + 12: start + 8 + 8 + struct.unpack("<Q", raw[start + 8:start + 16])[0]]
def rd(b, o): n = struct.unpack("<I", b[o:o + 4])[0]; return b[o + 4:o + 4 + n], o + 4 + n
signer, _ = rd(rd(v2, 0)[0], 0); signed, o = rd(signer, 0); sigs, o = rd(signer, o); pub, o = rd(signer, o)
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
sg, _ = rd(sigs, 0); sig, _ = rd(sg, 4)
serialization.load_der_public_key(pub).verify(sig, signed, padding.PKCS1v15(), hashes.SHA256())
digs, _ = rd(signed, 0); d1, _ = rd(digs, 0); want = d1[8:]
certs, _ = rd(signed, rd(signed, 0)[1]); cert_der, _ = rd(certs, 0)
if x509.load_der_x509_certificate(cert_der).fingerprint(hashes.SHA256()).hex() != CERT_SHA: fail("signing key purani wali nahi hai! update install nahi hoga")
s3 = bytearray(raw[eo:]); s3[16:20] = struct.pack("<I", start); ds = []
for sec in (raw[:start], raw[cdo:eo], bytes(s3)):
    for i in range(0, len(sec), 1 << 20):
        c = sec[i:i + (1 << 20)]; ds.append(hashlib.sha256(b"\xa5" + struct.pack("<I", len(c)) + c).digest())
if hashlib.sha256(b"\x5a" + struct.pack("<I", len(ds)) + b"".join(ds)).digest() != want: fail("v2 digest mismatch")
dex = z.read("classes.dex")
for need in (b"onPause", b"onResume", b"setMediaPlaybackRequiresUserGesture", b"ExtClient", b"rateboard/Tv;", b"setRequestedOrientation", b"android.software.leanback", b"PollJob", b"Notifier", b"Sched", b"shop_msgs", b"ic_stat", b"JobInfo"):
    if need not in dex: fail(f"dex me {need.decode()} nahi mila")
import zlib
if zlib.adler32(dex[12:]) & 0xffffffff != struct.unpack("<I", dex[8:12])[0] or hashlib.sha1(dex[32:]).digest() != dex[12:32]: fail("dex checksum")
print("ALL CHECKS PASSED: version match, signature, cert, alignment, dex")

# ---------------- repo ----------------
if os.path.isdir(REPO):
    import shutil
    shutil.copy(OUT, os.path.join(REPO, "SS-Rates.apk"))
    vj = {"versionCode": code, "versionName": name, "apk": APK_URL, "notes": a.notes or json.load(open(f"{REPO}/version.json")).get("notes", "")}
    json.dump(vj, open(f"{REPO}/version.json", "w"), indent=2, ensure_ascii=False)
    src = os.path.join(REPO, "source"); shutil.rmtree(src, ignore_errors=True); os.makedirs(src)
    for f in ("AndroidManifest.xml", "make_icons.py", "make_app_html.py", "build_apk.py", "release.py", "setup_tools.py"):
        shutil.copy(os.path.join(ROOT, f), src)
    for d in ("src", "res", "fakefw", "tools"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(src, d))
    for f in ("rate_board.html", "logo.png", "serve.py", "start_board.bat"):
        shutil.copy(os.path.join(ROOT, "..", f), src)
    print("repo folder tayyar:", REPO)
    if a.push:
        env = dict(os.environ, GIT_AUTHOR_NAME="Claude", GIT_AUTHOR_EMAIL="noreply@anthropic.com",
                   GIT_COMMITTER_NAME="Claude", GIT_COMMITTER_EMAIL="noreply@anthropic.com")
        run(["git", "-C", REPO, "add", "-A"])
        msg = f"v{name}: {a.notes}\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01UVtmgbR4mQ45smCeuJHxCp"
        run(["git", "-C", REPO, "commit", "-m", msg], env=env)
        print(run(["git", "-C", REPO, "push", "origin", "main"]) or "pushed")
