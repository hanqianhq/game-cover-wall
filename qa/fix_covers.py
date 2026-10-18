# -*- coding: utf-8 -*-
import json, ssl, urllib.request, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")
COVER = ROOT / "public" / "covers"
CTX = ssl.create_default_context()

def fetch(url, dest, min_size=8000):
    req = urllib.request.Request(url, headers={"User-Agent": "visual-lab/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        data = r.read()
    if len(data) < min_size:
        raise RuntimeError("small %s" % len(data))
    dest.write_bytes(data)
    return len(data)

def steam_cover(appid, dest):
    urls = [
        "https://cdn.cloudflare.steamstatic.com/steam/apps/%s/library_600x900_2x.jpg" % appid,
        "https://cdn.cloudflare.steamstatic.com/steam/apps/%s/library_600x900.jpg" % appid,
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/%s/library_600x900_2x.jpg" % appid,
        "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/%s/library_600x900.jpg" % appid,
    ]
    last = None
    for u in urls:
        try:
            n = fetch(u, dest)
            return n, u
        except Exception as e:
            last = e
    raise RuntimeError(last)

def font(size):
    for name in [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]:
        p = Path(name)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()

def make_cover(path, bg_top, bg_bot, accent, title_zh, title_en, motif="hill"):
    W, H = 600, 900
    im = Image.new("RGB", (W, H), bg_bot)
    dr = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        r = int(bg_top[0] * (1 - t) + bg_bot[0] * t)
        g = int(bg_top[1] * (1 - t) + bg_bot[1] * t)
        b = int(bg_top[2] * (1 - t) + bg_bot[2] * t)
        dr.line([(0, y), (W, y)], fill=(r, g, b))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = W // 2, int(H * 0.28)
    for rad, a in [(180, 40), (120, 70), (70, 110)]:
        gd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(*accent, a))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    dr = ImageDraw.Draw(im)
    if motif == "hill":
        dr.polygon([(0, 720), (120, 560), (260, 640), (400, 500), (520, 610), (600, 540), (600, 900), (0, 900)], fill=(34, 72, 48))
        dr.polygon([(0, 780), (180, 650), (340, 730), (480, 620), (600, 700), (600, 900), (0, 900)], fill=(22, 52, 36))
    elif motif == "islands":
        for (x, y, w, h, c) in [(80, 420, 160, 50, (70, 110, 70)), (320, 360, 200, 60, (90, 130, 80)), (200, 520, 180, 45, (50, 90, 60)), (420, 560, 140, 40, (60, 100, 55))]:
            dr.ellipse([x, y, x + w, y + h], fill=c)
            dr.rectangle([x + int(w * 0.2), y + int(h * 0.5), x + int(w * 0.8), y + h + 80], fill=(40, 70, 50))
        dr.rectangle([0, 780, W, H], fill=(28, 40, 55))
    elif motif == "blocks":
        colors = [(106, 168, 79), (121, 85, 58), (92, 64, 42), (70, 70, 70)]
        bs = 50
        random.seed(42)
        for row, y in enumerate(range(500, H, bs)):
            for x in range(0, W, bs):
                c = colors[min(row, 3)]
                j = random.randint(-8, 8)
                cc = tuple(max(0, min(255, ch + j)) for ch in c)
                dr.rectangle([x, y, x + bs - 1, y + bs - 1], fill=cc, outline=(0, 0, 0))
        dr.ellipse([420, 80, 520, 180], fill=(255, 220, 80))
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rectangle([0, 700, W, H], fill=(10, 12, 16, 200))
    im = Image.alpha_composite(im.convert("RGBA"), plate).convert("RGB")
    dr = ImageDraw.Draw(im)
    f1 = font(42)
    f2 = font(22)
    def center_text(text, y, f, fill):
        bbox = dr.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        dr.text(((W - tw) / 2, y), text, font=f, fill=fill)
    center_text(title_zh, 720, f1, (245, 248, 240))
    center_text(title_en, 780, f2, accent)
    dr.rectangle([8, 8, W - 9, H - 9], outline=(220, 220, 220), width=2)
    im.save(path, "PNG" if path.suffix.lower() == ".png" else "JPEG", quality=92)
    print("placeholder", path.name, path.stat().st_size)

print("--- fix animal-well ---")
n, u = steam_cover(813230, COVER / "animal-well.jpg")
print("animal-well", n, u)

print("--- regen placeholders ---")
make_cover(COVER / "botw.png", (120, 180, 200), (30, 60, 50), (180, 220, 140), "\u65f7\u91ce\u4e4b\u606f", "Breath of the Wild", "hill")
make_cover(COVER / "totk.png", (90, 140, 200), (40, 50, 70), (220, 190, 100), "\u738b\u56fd\u4e4b\u6cea", "Tears of the Kingdom", "islands")
make_cover(COVER / "minecraft.png", (135, 206, 235), (80, 140, 90), (106, 168, 79), "\u6211\u7684\u4e16\u754c", "Minecraft", "blocks")

# patch animal-well steam id in both manifests
for rel in ["games/manifest.json", "public/covers/manifest.json"]:
    path = ROOT / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    for g in data:
        if g["id"] == "animal-well":
            g["steam"] = 813230
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("patched", rel)

print("DONE_FIX_COVERS")