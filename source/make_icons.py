#!/usr/bin/env python3
"""logo.png (heart mark) se launcher icons banata hai: safed square, thoda padding."""
import os, sys
from PIL import Image, ImageDraw

root = os.path.dirname(os.path.abspath(__file__))
logo_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "..", "logo.png")
sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}

logo = Image.open(logo_path).convert("RGBA")
for name, px in sizes.items():
    canvas = Image.new("RGBA", (px, px), (255, 255, 255, 255))
    inner = int(px * 0.80)                      # 10% padding har side
    mark = logo.copy()
    mark.thumbnail((inner, inner), Image.LANCZOS)
    canvas.paste(mark, ((px - mark.width) // 2, (px - mark.height) // 2), mark)
    out_dir = os.path.join(root, "res", f"mipmap-{name}")
    os.makedirs(out_dir, exist_ok=True)
    # gol kinare (rounded square), bahar ka hissa transparent
    big = 4
    mask = Image.new("L", (px * big, px * big), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, px * big - 1, px * big - 1), radius=int(px * big * 0.26), fill=255)
    mask = mask.resize((px, px), Image.LANCZOS)
    canvas.putalpha(mask)
    canvas.save(os.path.join(out_dir, "ic_launcher.png"), optimize=True)
    print("icon", name, px)

# --- notification status-bar icon: mota safed heart silhouette (status bar me patli line dikhti nahi) ---
import math
stat = {"mdpi": 24, "hdpi": 36, "xhdpi": 48, "xxhdpi": 72, "xxxhdpi": 96}
for name, px in stat.items():
    big = 8; N = px * big
    pts = []
    for k in range(720):
        t = 2 * math.pi * k / 720
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        pts.append((N / 2 + x * N * 0.027 * 1.0 * 1.55 / 1.0 * 0.62, N * 0.47 - y * N * 0.027 * 1.55 * 0.62))
    m = Image.new("L", (N, N), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    m = m.resize((px, px), Image.LANCZOS)
    sil = Image.new("RGBA", (px, px), (255, 255, 255, 0)); sil.putalpha(m)
    sil = Image.merge("RGBA", (Image.new("L",(px,px),255),)*3 + (m,))
    d = os.path.join(root, "res", f"drawable-{name}"); os.makedirs(d, exist_ok=True)
    sil.save(os.path.join(d, "ic_stat.png"), optimize=True)
    print("stat", name, px)

# --- Android TV banner (home screen par app ka card): 320x180 dp ---
from PIL import ImageFont
BANNER_FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
for name, w in {"mdpi": 320, "hdpi": 480, "xhdpi": 640, "xxhdpi": 960}.items():
    h = w * 9 // 16; k = w / 320
    img = Image.new("RGB", (w, h), (251, 246, 234))
    d = ImageDraw.Draw(img)
    for y in range(h):                                   # halka sunehra gradient
        t = y / h; d.line([(0, y), (w, y)], fill=(int(251 - 10 * t), int(246 - 22 * t), int(234 - 52 * t)))
    mark = logo.copy().convert("RGBA"); sz = int(112 * k); mark.thumbnail((sz, sz), Image.LANCZOS)
    mx, my = int(22 * k), (h - mark.height) // 2
    img.paste(mark, (mx, my), mark)
    f1 = ImageFont.truetype(BANNER_FONT, int(21 * k)); f2 = ImageFont.truetype(BANNER_FONT, int(10.5 * k))
    tx = mx + mark.width + int(14 * k)
    d.text((tx, int(h / 2 - 30 * k)), "SHREE SS", font=f1, fill=(166, 122, 34))
    d.text((tx, int(h / 2 - 6 * k)), "JEWELLERS", font=f1, fill=(166, 122, 34))
    d.text((tx, int(h / 2 + 26 * k)), "LIVE GOLD & SILVER RATES", font=f2, fill=(125, 112, 90))
    dd = os.path.join(root, "res", f"drawable-{name}"); os.makedirs(dd, exist_ok=True)
    img.save(os.path.join(dd, "tv_banner.png"), optimize=True); print("banner", name, w, h)
