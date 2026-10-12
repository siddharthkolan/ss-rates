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
