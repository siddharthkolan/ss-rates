#!/usr/bin/env python3
"""base.apk (aapt2) + classes.dex + assets -> aligned, v2-signed APK.
Use: build_apk.py base.apk classes.dex assets_dir out.apk [key.pem cert.pem]"""
import sys, os, struct, zipfile, hashlib, datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

base, dex, assets, out = sys.argv[1:5]
keyp = sys.argv[5] if len(sys.argv) > 5 else os.path.join(os.path.dirname(out) or ".", "ssrates.key.pem")

# ---------- key / cert ----------
if os.path.exists(keyp):
    key = serialization.load_pem_private_key(open(keyp, "rb").read(), None)
    cert = x509.load_pem_x509_certificate(open(keyp.replace("key", "cert"), "rb").read())
else:
    key = rsa.generate_private_key(65537, 2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Shree SS Jewellers"),
                      x509.NameAttribute(NameOID.COUNTRY_NAME, "IN")])
    now = datetime.datetime(2026, 1, 1)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=36500))
            .sign(key, hashes.SHA256()))
    open(keyp, "wb").write(key.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    open(keyp.replace("key", "cert"), "wb").write(cert.public_bytes(serialization.Encoding.PEM))

# ---------- collect entries ----------
entries = []   # (name, bytes, stored?)
with zipfile.ZipFile(base) as z:
    for n in z.namelist():
        if n.endswith("/"): continue
        entries.append((n, z.read(n), n == "resources.arsc"))
entries.append(("classes.dex", open(dex, "rb").read(), False))
for fn in sorted(os.listdir(assets)):
    entries.append(("assets/" + fn, open(os.path.join(assets, fn), "rb").read(), False))
# manifest first, resources.arsc stored
entries.sort(key=lambda e: (e[0] != "AndroidManifest.xml", e[0]))

# ---------- write aligned zip ----------
tmp = out + ".unsigned"
with zipfile.ZipFile(tmp, "w") as zf:
    for n, data, stored in entries:
        zi = zipfile.ZipInfo(n, (2026, 1, 1, 0, 0, 0))
        zi.create_system = 3
        zi.external_attr = 0o644 << 16
        if stored:
            zi.compress_type = zipfile.ZIP_STORED
            off = zf.fp.tell() + 30 + len(n.encode())
            pad = (-off) % 4
            if pad:
                p = pad + 4
                zi.extra = struct.pack("<HH", 0xd935, p - 4) + b"\x00" * (p - 4)
        else:
            zi.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(zi, data)
raw = open(tmp, "rb").read()

# ---------- parse EOCD ----------
eocd = raw.rfind(b"PK\x05\x06")
cd_size, cd_off = struct.unpack("<II", raw[eocd + 12: eocd + 20])
assert cd_off + cd_size == eocd
sections = [raw[:cd_off], raw[cd_off:eocd], raw[eocd:]]

def chunks(b):
    for i in range(0, len(b), 1 << 20):
        yield b[i:i + (1 << 20)]
def apk_digest(s1, s2, s3):
    s3 = s3[:16] + struct.pack("<I", len(s1)) + s3[20:]   # cd offset = start of sig block
    ds = []
    for sec in (s1, s2, s3):
        for c in chunks(sec):
            ds.append(hashlib.sha256(b"\xa5" + struct.pack("<I", len(c)) + c).digest())
    return hashlib.sha256(b"\x5a" + struct.pack("<I", len(ds)) + b"".join(ds)).digest()

digest = apk_digest(*sections)
def lp(b): return struct.pack("<I", len(b)) + b
ALGO = 0x0103
cert_der = cert.public_bytes(serialization.Encoding.DER)
signed = lp(lp(struct.pack("<II", ALGO, 32) + digest)) + lp(lp(cert_der)) + lp(b"")
sig = key.sign(signed, padding.PKCS1v15(), hashes.SHA256())
pub = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
signer = lp(signed) + lp(lp(struct.pack("<I", ALGO) + lp(sig))) + lp(pub)
v2 = lp(lp(signer))
pair = struct.pack("<Q", 4 + len(v2)) + struct.pack("<I", 0x7109871a) + v2
blk_size = len(pair) + 8 + 16
block = struct.pack("<Q", blk_size) + pair + struct.pack("<Q", blk_size) + b"APK Sig Block 42"

new_cd_off = cd_off + len(block)
eocd_b = bytearray(sections[2]); eocd_b[16:20] = struct.pack("<I", new_cd_off)
open(out, "wb").write(sections[0] + block + sections[1] + bytes(eocd_b))
os.remove(tmp)
print("signed ->", out, os.path.getsize(out), "bytes; cert sha256", cert.fingerprint(hashes.SHA256()).hex())
