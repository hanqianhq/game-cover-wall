# -*- coding: utf-8 -*-
import json, ssl, urllib.request, time
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
    center(title_en[:42], 780, f2, a1)
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
    {"id":"armored-core-6","zh":U(0x88c5,0x7532,0x6838,0x5fc3)+"6","en":"ARMORED CORE VI","steam":1888160,"blurb":"FromSoftware"+U(0x3002),"vibe":"souls"},
    {"id":"remnant-2","zh":U(0x9057,0x8ff9)+"2","en":"Remnant II","steam":1282100,"blurb":U(0x67aa,0x68b0,0x9b42,0x7cfb,0x3002),"vibe":"souls"},
    {"id":"dragons-dogma-2","zh":U(0x9f99,0x4e4b,0x4fe1,0x6761)+"2","en":"Dragons Dogma 2","steam":2054970,"blurb":U(0x722a,0x7259,0x540c,0x884c,0x3002),"vibe":"epic"},
    {"id":"alan-wake-2","zh":U(0x5fc3,0x7075,0x6740,0x624b)+"2","en":"Alan Wake 2","steam":1937780,"blurb":U(0x624b,0x7535,0x7b52,0x3002),"vibe":"epic"},
    {"id":"stellar-blade","zh":U(0x5251,0x661f),"en":"Stellar Blade","steam":3489700,"blurb":U(0x723d,0x5feb,0x8fde,0x62db,0x3002),"vibe":"arcade"},
    {"id":"ff16","zh":U(0x6700,0x7ec8,0x5e7b,0x60f3)+"16","en":"FINAL FANTASY XVI","steam":2515020,"blurb":U(0x53ec,0x5524,0x517d,0x3002),"vibe":"epic"},
    {"id":"expedition-33","zh":U(0x660e,0x6697)+"33","en":"Clair Obscur Expedition 33","steam":1903340,"blurb":U(0x6cd5,0x5f0f,0x56de,0x5408,0x5236,0x3002),"vibe":"epic"},
    {"id":"enshrouded","zh":U(0x96fe,0x9501,0x738b,0x56fd),"en":"Enshrouded","steam":1203620,"blurb":U(0x4f53,0x7d20,0x5efa,0x9020,0x3002),"vibe":"cozy"},
    {"id":"v-rising","zh":U(0x591c,0x65cf,0x5d1b,0x8d77),"en":"V Rising","steam":1604030,"blurb":U(0x5438,0x8840,0x9b3c,0x3002),"vibe":"souls"},
    {"id":"core-keeper","zh":U(0x6838,0x5fc3,0x5b88,0x62a4,0x8005),"en":"Core Keeper","steam":1621690,"blurb":U(0x5730,0x4e0b,0x6316,0x6316,0x3002),"vibe":"cozy"},
    {"id":"grounded","zh":U(0x7981,0x95ed,0x6c42,0x751f),"en":"Grounded","steam":962130,"blurb":U(0x7f29,0x5c0f,0x540e,0x9662,0x3002),"vibe":"cozy"},
    {"id":"once-human","zh":"Once Human","en":"Once Human","steam":2139460,"blurb":U(0x5f02,0x80fd,0x5e9f,0x571f,0x3002),"vibe":"epic"},
    {"id":"hellblade-2","zh":U(0x5730,0x72f1,0x4e4b,0x5203)+"2","en":"Hellblade II","steam":2461850,"blurb":U(0x5fc3,0x7406,0x6050,0x6016,0x3002),"vibe":"souls"},
    {"id":"persona-3-reload","zh":U(0x4eba,0x683c)+"3R","en":"Persona 3 Reload","steam":2161700,"blurb":U(0x6708,0x591c,0x5b66,0x56ed,0x3002),"vibe":"epic"},
    {"id":"metaphor","zh":U(0x5e7b,0x9038,0x4f20,0x8bf4),"en":"Metaphor ReFantazio","steam":2679460,"blurb":U(0x5e7b,0x60f3,0x52c7,0x8005,0x3002),"vibe":"epic"},
    {"id":"space-marine-2","zh":U(0x6218,0x7a7a,0x58eb,0x5b98)+"2","en":"Space Marine 2","steam":2183900,"blurb":U(0x5de8,0x578b,0x6740,0x622e,0x3002),"vibe":"arcade"},
    {"id":"destiny-2","zh":U(0x547d,0x8fd0)+"2","en":"Destiny 2","steam":1085660,"blurb":U(0x5c04,0x624b,0x79d1,0x5e7b,0x3002),"vibe":"neon"},
    {"id":"pathfinder-wotr","zh":U(0x8def,0x5f84,0x5bfb,0x8005),"en":"Pathfinder WotR","steam":1184370,"blurb":U(0x75c5,0x6bd2,0x4e0e,0x5929,0x4f7f,0x3002),"vibe":"epic"},
    {"id":"code-vein","zh":U(0x554a,0x54d2,0x4e4b,0x8840),"en":"CODE VEIN","steam":678960,"blurb":U(0x5438,0x8840,0x9b3c,0x9b42,0x7cfb,0x3002),"vibe":"souls"},
]


FILLERS = [
    ("nioh-2", U(0x4ec1,0x738b)+"2", "Nioh 2", 1325200, U(0x5fc3,0x9b42,0x6b66,0x58eb,0x3002), "souls"),
    ("team-fortress-2", U(0x56e2,0x961f,0x5821,0x5792)+"2", "Team Fortress 2", 440, U(0x5e3d,0x5b50,0x5c04,0x51fb,0x3002), "arcade"),
    ("dota-2", "Dota 2", "Dota 2", 570, U(0x5206,0x8def,0x5bf9,0x6297,0x3002), "arcade"),
    ("mhrise", U(0x602a,0x7269,0x730e,0x4eba,0x5d1b,0x8d77), "Monster Hunter Rise", 1446780, U(0x5927,0x5251,0x730e,0x9f99,0x3002), "epic"),
    ("sea-of-stars", U(0x661f,0x4e4b,0x6d77), "Sea of Stars", 1244090, U(0x50cf,0x7d20,0x52c7,0x8005,0x3002), "cozy"),
    ("slay-spire-2", U(0x5c60,0x6740,0x5c16,0x5854)+"2", "Slay the Spire 2", 2868840, U(0x5361,0x724c,0x8089,0x9e3d,0x3002), "cozy"),
    ("peak", "PEAK", "PEAK", 3527290, U(0x722c,0x5c71,0x8054,0x673a,0x3002), "cozy"),
    ("repo", "R.E.P.O.", "R.E.P.O.", 3241660, U(0x6050,0x6016,0x5408,0x4f5c,0x3002), "arcade"),
    ("inzoi", "inZOI", "inZOI", 2456740, U(0x4eba,0x751f,0x6a21,0x62df,0x3002), "cozy"),
    ("frostpunk-2", U(0x971c,0x6c14,0x670b,0x514b)+"2", "Frostpunk 2", 1601580, U(0x51b0,0x5c01,0x57ce,0x5e02,0x3002), "epic"),
    ("manor-lords", U(0x9886,0x4e3b), "Manor Lords", 1363080, U(0x4e2d,0x4e16,0x7eaa,0x5efa,0x57ce,0x3002), "epic"),
    ("civ7", U(0x6587,0x660e)+"7", "Civilization VII", 1295660, U(0x4e00,0x66f4,0x56de,0x5408,0x3002), "epic"),
    ("silent-hill-2", U(0x5bc2,0x9759,0x5cad)+"2", "SILENT HILL 2", 2124490, U(0x6050,0x6016,0x91cd,0x5236,0x3002), "souls"),
    ("until-dawn", U(0x76f4,0x5230,0x9ece,0x660e), "Until Dawn", 2176490, U(0x9009,0x62e9,0x652f,0x6050,0x6016,0x3002), "epic"),
    ("marvel-rivals", U(0x6f2b,0x5a01,0x4e89,0x950b), "Marvel Rivals", 2767030, U(0x8d85,0x51e1,0x5bf9,0x6297,0x3002), "arcade"),
    ("delta-force", U(0x4e09,0x89d2,0x6d32), "Delta Force", 2507950, U(0x5c04,0x624b,0x8fdb,0x653b,0x3002), "arcade"),
    ("the-finals", "THE FINALS", "THE FINALS", 2073850, U(0x7834,0x574f,0x5c04,0x51fb,0x3002), "arcade"),
    ("age-of-mythology-retold", U(0x795e,0x8bdd,0x65f6,0x4ee3), "Age of Mythology Retold", 1934680, U(0x795e,0x8bdd,0x79d1,0x5e7b,0x3002), "epic"),
    ("nightreign", U(0x57c3,0x5c14,0x767b)+U(0x591c,0x5e55), "ELDEN RING NIGHTREIGN", 2778580, U(0x9b42,0x7cfb,0x8054,0x673a,0x3002), "souls"),
    ("warhammer-tw3", U(0x5168,0x6218)+"WH3", "Total War WARHAMMER III", 1142710, U(0x5947,0x5e7b,0x519b,0x56e2,0x3002), "epic"),
    ("infinity-nikki", U(0x65e0,0x9650,0x6696,0x6696), "Infinity Nikki", 2783950, U(0x6362,0x88c5,0x5f00,0x653e,0x4e16,0x754c,0x3002), "cozy"),
    ("snowbreak", U(0x5c18,0x767d,0x7981,0x533a), "Snowbreak", 2668080, U(0x4e09,0x6d88,0x5c04,0x624b,0x3002), "neon"),
    ("girls-frontline-2", U(0x5c11,0x5973,0x524d,0x7ebf)+"2", "Girls Frontline 2", 2592150, U(0x67aa,0x68b0,0x5c11,0x5973,0x3002), "neon"),
]

def build_new():
    items = list(NEW)
    for fid, zh, en, steam, blurb, vibe in FILLERS:
        if any(x["id"] == fid for x in items):
            continue
        items.append({"id": fid, "zh": zh, "en": en, "steam": steam, "blurb": blurb, "vibe": vibe})
    if len(items) < 50:
        raise SystemExit("need 50, have %s" % len(items))
    return items[:50]

def regen_card_texture(data):
    lines = []
    lines.append("/** Auto-generated from games/manifest.json */")
    lines.append("export type CoverVibe = 'cozy' | 'neon' | 'epic' | 'souls' | 'arcade'")
    lines.append("")
    lines.append("export type CoverMeta = {")
    for f in ["id: string","file: string","titleZh: string","titleEn: string","blurb: string","source: string","type: 'steam-store-art' | 'stylized-placeholder'","vibe: CoverVibe"]:
        lines.append("  " + f)
    lines.append("}")
    lines.append("")
    lines.append("export const COVERS: CoverMeta[] = [")
    def esc(s):
        return s.replace("\\", "\\\\").replace("'", "\\'")
    for g in data:
        typ = g.get("type", "steam-store-art")
        if typ == "stylized-placeholder":
            source = g.get("note") or "stylized placeholder"
        else:
            steam = g.get("steam")
            source = ("Steam CDN app/%s" % steam) if steam else (g.get("note") or "Steam CDN")
        lines.append("  {")
        lines.append("    id: '%s'," % esc(g["id"]))
        lines.append("    file: '%s'," % esc(g["file"]))
        lines.append("    titleZh: '%s'," % esc(g["zh"]))
        lines.append("    titleEn: '%s'," % esc(g["en"]))
        lines.append("    blurb: '%s'," % esc(g["blurb"]))
        lines.append("    source: '%s'," % esc(source))
        lines.append("    type: '%s'," % typ)
        lines.append("    vibe: '%s'," % g["vibe"])
        lines.append("  },")
    lines.append("]")
    lines.append("")
    lines.append("export function coverUrl(file: string): string {")
    lines.append("  return `${import.meta.env.BASE_URL}covers/${file}`")
    lines.append("}")
    lines.append("")
    (ROOT / "src/cardTexture.ts").write_text("\n".join(lines), encoding="utf-8")

def main():
    existing = json.loads((ROOT / "games/manifest.json").read_text(encoding="utf-8"))
    have = {g["id"] for g in existing}
    fresh = [g for g in build_new() if g["id"] not in have]
    print("to add", len(fresh), "existing", len(existing))
    added_ids = []
    failed = []
    for g in fresh:
        gid = g["id"]
        vibe = g["vibe"]
        placeholder = g.get("placeholder") or not g.get("steam")
        if placeholder:
            fpath = COVER / ("%s.png" % gid)
            make_placeholder(fpath, g["zh"], g["en"], vibe)
            entry = {"id": gid, "zh": g["zh"], "en": g["en"], "steam": None, "blurb": g["blurb"], "file": "%s.png" % gid, "type": "stylized-placeholder", "note": g.get("note") or "stylized placeholder", "vibe": vibe}
        else:
            fpath = COVER / ("%s.jpg" % gid)
            try:
                n, u = steam_cover(g["steam"], fpath)
                print("ok", gid, n)
                entry = {"id": gid, "zh": g["zh"], "en": g["en"], "steam": g["steam"], "blurb": g["blurb"], "file": "%s.jpg" % gid, "type": "steam-store-art", "vibe": vibe}
            except Exception as e:
                print("FAIL steam", gid, e, "-> placeholder")
                failed.append(gid)
                fpath = COVER / ("%s.png" % gid)
                make_placeholder(fpath, g["zh"], g["en"], vibe)
                entry = {"id": gid, "zh": g["zh"], "en": g["en"], "steam": g.get("steam"), "blurb": g["blurb"], "file": "%s.png" % gid, "type": "stylized-placeholder", "note": "store art unavailable; stylized placeholder", "vibe": vibe}
        existing.append(entry)
        added_ids.append(gid)
        time.sleep(0.05)
    for g in existing:
        g.setdefault("vibe", "epic")
    if len(existing) > 150:
        existing = existing[:150]
    print("TOTAL", len(existing))
    for rel in ["games/manifest.json", "public/covers/manifest.json"]:
        (ROOT / rel).write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    regen_card_texture(existing)
    counts = {}
    for g in existing:
        counts[g["vibe"]] = counts.get(g["vibe"], 0) + 1
    mihoyo = [x for x in added_ids if x in {"genshin","star-rail","zzz","honkai-3rd","wuthering-waves","reverse-1999","pgr","nikke","blue-archive","arknights-endfield","infinity-nikki","snowbreak","girls-frontline-2"}]
    (ROOT / "qa/added-150.json").write_text(json.dumps({"total": len(existing), "added": added_ids, "failed_steam": failed, "vibe_counts": counts, "mihoyo_erciyou": mihoyo}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VIBES", counts)
    print("MIHOYO", mihoyo)
    print("DONE_EXPAND150")

if __name__ == "__main__":
    main()
