# -*- coding: utf-8 -*-
import json, ssl, urllib.request, random, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")
COVER = ROOT / "public" / "covers"
CTX = ssl.create_default_context()

def U(*codes):
    return "".join(chr(c) for c in codes)

def fetch(url, dest, min_size=5000):
    req = urllib.request.Request(url, headers={"User-Agent": "visual-lab/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=35) as r:
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
            return fetch(u, dest), u
        except Exception as e:
            last = e
    raise RuntimeError(str(last))

def font(size):
    for name in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\arial.ttf"]:
        if Path(name).exists():
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                pass
    return ImageFont.load_default()

def make_placeholder(path, title_zh, title_en, vibe):
    palettes = {
        "neon": ((10, 5, 40), (0, 240, 255), (255, 43, 214)),
        "arcade": ((20, 5, 5), (255, 59, 59), (255, 229, 102)),
        "epic": ((15, 12, 8), (201, 162, 39), (240, 220, 180)),
        "souls": ((30, 25, 22), (224, 120, 64), (138, 122, 106)),
        "cozy": ((40, 60, 55), (126, 200, 200), (245, 230, 200)),
    }
    bg, a1, a2 = palettes.get(vibe, palettes["epic"])
    W, H = 600, 900
    im = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(bg[i] * (1 - t * 0.5) + a1[i] * t * 0.15) for i in range(3))
        dr.line([(0, y), (W, y)], fill=col)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rad, a, c in [(200, 50, a1), (120, 80, a2)]:
        gd.ellipse([300 - rad, 280 - rad, 300 + rad, 280 + rad], fill=(*c, a))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    dr = ImageDraw.Draw(im)
    # decorative geometry instead of empty black bar
    dr.polygon([(0, 620), (150, 540), (300, 600), (450, 520), (600, 580), (600, 900), (0, 900)], fill=tuple(max(0, c - 20) for c in bg))
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rectangle([0, 700, W, H], fill=(8, 8, 12, 210))
    im = Image.alpha_composite(im.convert("RGBA"), plate).convert("RGB")
    dr = ImageDraw.Draw(im)
    f1, f2 = font(40), font(20)
    def center(text, y, f, fill):
        bb = dr.textbbox((0, 0), text, font=f)
        dr.text(((W - (bb[2] - bb[0])) / 2, y), text, font=f, fill=fill)
    center(title_zh, 720, f1, (245, 248, 255))
    center(title_en, 780, f2, a1)
    dr.rectangle([6, 6, W - 7, H - 7], outline=a1, width=3)
    path = Path(path)
    if path.suffix.lower() == ".png":
        im.save(path, "PNG")
    else:
        im.save(path, "JPEG", quality=90)
    print("placeholder", path.name, path.stat().st_size)

NEW = [
    {"id":"genshin","zh":U(0x539f,0x795e),"en":"Genshin Impact","steam":None,"blurb":U(0x63d0,0x74e6,0x7279,0x81ea,0x7531,0x65c5,0x884c,0x3002),"vibe":"neon","placeholder":True},
    {"id":"star-rail","zh":U(0x5d29,0x574f,0xff1a,0x661f,0x7a79,0x94c1,0x9053),"en":"Honkai: Star Rail","steam":None,"blurb":U(0x94f6,0x6cb3,0x5217,0x8f66,0x4e0b,0x4e00,0x7ad9,0x3002),"vibe":"neon","placeholder":True},
    {"id":"zzz","zh":U(0x7edd,0x533a,0x96f6),"en":"Zenless Zone Zero","steam":4162040,"blurb":U(0x65b0,0x827e,0x5229,0x90fd,0x59d4,0x6258,0x65e5,0x3002),"vibe":"neon"},
    {"id":"honkai-3rd","zh":U(0x5d29,0x574f)+"3","en":"Honkai Impact 3rd","steam":1671200,"blurb":U(0x5973,0x6b66,0x795e,0x51fa,0x51fb,0x3002),"vibe":"arcade"},
    {"id":"wuthering-waves","zh":U(0x9e23,0x6f6e),"en":"Wuthering Waves","steam":3513350,"blurb":U(0x6f02,0x6cca,0x8005,0x82cf,0x9192,0x3002),"vibe":"neon"},
    {"id":"reverse-1999","zh":U(0x91cd,0x8fd4,0x672a,0x6765,0xff1a)+"1999","en":"Reverse: 1999","steam":3092660,"blurb":U(0x66b4,0x96e8,0x5012,0x8f6c,0x65f6,0x5149,0x3002),"vibe":"cozy"},
    {"id":"pgr","zh":U(0x6218,0x53cc,0x5e15,0x5f25,0x4ec0),"en":"Punishing: Gray Raven","steam":4125930,"blurb":U(0x6784,0x9020,0x4f53,0x4e09,0x6d88,0x3002),"vibe":"arcade"},
    {"id":"nikke","zh":U(0x80dc,0x5229,0x5973,0x795e,0xff1a,0x59ae,0x59ec),"en":"Goddess of Victory: NIKKE","steam":3596190,"blurb":U(0x56de,0x6536,0x5730,0x7403,0x3002),"vibe":"neon"},
    {"id":"blue-archive","zh":U(0x851a,0x84dd,0x6863,0x6848),"en":"Blue Archive","steam":3557620,"blurb":U(0x57fa,0x6c83,0x6258,0x65af,0x3002),"vibe":"cozy"},
    {"id":"arknights-endfield","zh":U(0x660e,0x65e5,0x65b9,0x821f,0xff1a,0x7ec8,0x672b,0x5730),"en":"Arknights: Endfield","steam":4732690,"blurb":U(0x65b9,0x821f,0x5b87,0x5b99,0x3002),"vibe":"epic"},
    {"id":"lies-of-p","zh":"P"+U(0x7684,0x8c0e,0x8a00),"en":"Lies of P","steam":1627720,"blurb":U(0x9b42,0x7cfb,0x6728,0x5076,0x3002),"vibe":"souls"},
    {"id":"armored-core-6","zh":U(0x88c5,0x7532,0x6838,0x5fc3)+"6","en":"ARMORED CORE VI","steam":1888160,"blurb":"FromSoftware mech"+U(0x3002),"vibe":"souls"},
    {"id":"remnant-2","zh":U(0x9057,0x8ff9)+"2","en":"Remnant II","steam":1282100,"blurb":U(0x67aa,0x68b0,0x9b42,0x7cfb,0x3002),"vibe":"souls"},
    {"id":"dragons-dogma-2","zh":U(0x9f99,0x4e4b,0x4fe1,0x6761)+"2","en":"Dragons Dogma 2","steam":2054970,"blurb":U(0x722a,0x7259,0x540c,0x884c,0x3002),"vibe":"epic"},
    {"id":"alan-wake-2","zh":U(0x5fc3,0x7075,0x6740,0x624b)+"2","en":"Alan Wake 2","steam":1937780,"blurb":U(0x624b,0x7535,0x7b52,0x6b66,0x5668,0x3002),"vibe":"epic"},
    {"id":"stellar-blade","zh":U(0x5251,0x661f),"en":"Stellar Blade","steam":3489700,"blurb":U(0x723d,0x5feb,0x8fde,0x62db,0x3002),"vibe":"arcade"},
    {"id":"ff16","zh":U(0x6700,0x7ec8,0x5e7b,0x60f3)+"16","en":"FINAL FANTASY XVI","steam":2515020,"blurb":U(0x53ec,0x5524,0x517d,0x5bf9,0x51b3,0x3002),"vibe":"epic"},
    {"id":"expedition-33","zh":U(0x660e,0x6697)+"33","en":"Clair Obscur: Expedition 33","steam":1903340,"blurb":U(0x6cd5,0x5f0f,0x56de,0x5408,0x5236,0x3002),"vibe":"epic"},
    {"id":"enshrouded","zh":U(0x96fe,0x9501,0x738b,0x56fd),"en":"Enshrouded","steam":1203620,"blurb":U(0x4f53,0x7d20,0x5efa,0x9020,0x3002),"vibe":"cozy"},
    {"id":"v-rising","zh":U(0x591c,0x65cf,0x5d1b,0x8d77),"en":"V Rising","steam":1604030,"blurb":U(0x5438,0x8840,0x9b3c,0x57ce,0x5821,0x3002),"vibe":"souls"},
    {"id":"core-keeper","zh":U(0x6838,0x5fc3,0x5b88,0x62a4,0x8005),"en":"Core Keeper","steam":1621690,"blurb":U(0x5730,0x4e0b,0x6316,0x6316,0x6316,0x3002),"vibe":"cozy"},
    {"id":"grounded","zh":U(0x7981,0x95ed,0x6c42,0x751f),"en":"Grounded","steam":962130,"blurb":U(0x7f29,0x5c0f,0x540e,0x9662,0x3002),"vibe":"cozy"},
    {"id":"once-human","zh":"Once Human","en":"Once Human","steam":2139460,"blurb":U(0x5f02,0x80fd,0x5e9f,0x571f,0x3002),"vibe":"epic"},
    {"id":"hellblade-2","zh":U(0x5730,0x72f1,0x4e4b,0x5203)+"2","en":"Hellblade II","steam":2461850,"blurb":U(0x5fc3,0x7406,0x6050,0x6016,0x3002),"vibe":"souls"},
    {"id":"persona-3-reload","zh":U(0x4eba,0x683c,0x5f71,0x5b50)+"3 Reload","en":"Persona 3 Reload","steam":2161700,"blurb":U(0x6708,0x591c,0x5b66,0x56ed,0x3002),"vibe":"epic"},
    {"id":"metaphor","zh":U(0x5e7b,0x9038,0x4f20,0x8bf4),"en":"Metaphor: ReFantazio","steam":2679460,"blurb":U(0x5e7b,0x60f3,0x5f0f,0x52c7,0x8005,0x3002),"vibe":"epic"},
    {"id":"black-myth-wait","zh":"x","en":"x","steam":0},
]

# more fillers to reach 50
MORE = [
    ("space-marine-2", U(0x6218,0x7a7a,0x58eb,0x5b98)+"2", "Warhammer 40K Space Marine 2", 2183900, U(0x5de8,0x578b,0x6740,0x622e,0x3002), "arcade"),
    ("tekken-wait", "x", "x", 0, "x", "arcade"),
]
