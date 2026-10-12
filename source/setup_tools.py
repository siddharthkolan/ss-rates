#!/usr/bin/env python3
"""Naye session / naye computer par build ke tools taiyar karta hai (aapt2, apktool, fake framework, smali runner).
Use:  SS_TOOLS=/kisi/folder python3 setup_tools.py      (phir release.py chalao, wahi SS_TOOLS ke saath)
Chahiye: node + npm, java (JDK, javac), python3."""
import os, subprocess, sys, tarfile, glob, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SCR = os.environ.get("SS_TOOLS") or sys.exit("SS_TOOLS folder set karo")
T, BUILD, DL = f"{SCR}/tools", f"{SCR}/build", f"{SCR}/dl"
for d in (T, BUILD, f"{BUILD}/tools", f"{BUILD}/fw", DL): os.makedirs(d, exist_ok=True)

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode: sys.exit(f"FAIL {cmd}\n{r.stdout}{r.stderr}")
    return r.stdout

def npm_pkg(name, version, dest):
    shutil.rmtree(dest, ignore_errors=True)
    tgz = run(["npm", "pack", f"{name}@{version}", "--silent"], cwd=DL).strip().splitlines()[-1]
    with tarfile.open(f"{DL}/{tgz}") as t:
        t.extractall(f"{DL}/x_{name}")
    shutil.move(f"{DL}/x_{name}/package", dest)

npm_pkg("aaptjs3", "latest", f"{T}/aapt")
npm_pkg("apktool-jar", "2.4.1", f"{T}/apktool")
aapt = f"{T}/aapt/bin/x64/linux/aapt2"; os.chmod(aapt, 0o755)
jar = f"{T}/apktool/bin/apktool_2.4.1.jar"
assert os.path.exists(jar) and os.path.exists(aapt)

# smali runner
run(["javac", "-cp", jar, "-d", f"{BUILD}/tools", f"{ROOT}/tools/SmaliRun.java"])
# fake framework (manifest ke android:* attributes ko asli IDs dene ke liye)
fw = f"{ROOT}/fakefw"
for f in glob.glob(f"{BUILD}/fw/*"): os.remove(f)
run([aapt, "compile", f"{fw}/res/values/attrs.xml", f"{fw}/res/values/public.xml", "-o", f"{BUILD}/fw/"])
run([aapt, "link", "--manifest", f"{fw}/AndroidManifest.xml", "-o", f"{BUILD}/fakefw.apk",
     "--min-sdk-version", "24", "--target-sdk-version", "34"] + glob.glob(f"{BUILD}/fw/*.flat"))
print("tools taiyar:", SCR)
