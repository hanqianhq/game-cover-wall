# -*- coding: utf-8 -*-
import json, re, sys
from pathlib import Path

ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")

VIBES = {
  # cozy
  "dave-diver": "cozy", "stardew": "cozy", "terraria": "cozy", "celeste": "cozy",
  "undertale": "cozy", "animal-well": "cozy", "minecraft": "cozy", "sims4": "cozy",
  "pvz": "cozy", "among-us": "cozy", "balatro": "cozy", "hades": "cozy", "hades-2": "cozy",
  "it-takes-two": "cozy", "botw": "cozy", "totk": "cozy", "subnautica": "cozy",
  "outer-wilds": "cozy", "sea-of-thieves": "cozy", "dont-starve": "cozy",
  "against-storm": "cozy", "valheim": "cozy", "palworld": "cozy", "portal-2": "cozy",
  "slay-the-spire": "cozy",
  # neon
  "cyberpunk-2077": "neon", "control": "neon", "warframe": "neon", "apex": "neon",
  "death-stranding": "neon", "no-mans-sky": "neon", "starfield": "neon",
  "half-life-alyx": "neon",
  # souls
  "elden-ring": "souls", "sekiro": "souls", "ds3": "souls", "hollow-knight": "souls",
  "silksong": "souls", "nier-automata": "souls",
  # arcade
  "tekken-8": "arcade", "sf6": "arcade", "helldivers-2": "arcade", "doom-eternal": "arcade",
  "dmc5": "arcade", "rocket-league": "arcade", "cs2": "arcade", "pubg": "arcade",
  "l4d2": "arcade", "forza-horizon-5": "arcade", "deep-rock": "arcade", "naraka": "arcade",
  "vampire-survivors": "arcade", "dead-cells": "arcade", "isaac": "arcade",
  "lethal-company": "arcade", "phasmophobia": "arcade", "rust": "arcade",
  "sons-of-forest": "arcade",
  # epic — listed explicitly for clarity; fallback also epic
  "rdr2": "epic", "witcher-3": "epic", "baldurs-gate-3": "epic", "skyrim": "epic",
  "fallout-4": "epic", "hogwarts": "epic", "kcd2": "epic", "black-myth-wukong": "epic",
  "mhw": "epic", "mh-wilds": "epic", "gow": "epic", "gow-ragnarok": "epic",
  "ghost-of-tsushima": "epic", "uncharted": "epic", "ff7-remake": "epic",
  "spiderman": "epic", "spider-man-2": "epic", "tlou1": "epic", "tlou2": "epic",
  "horizon-zd": "epic", "re-village": "epic", "re2r": "epic", "re4r": "epic",
  "metro-exodus": "epic", "like-a-dragon": "epic", "detroit": "epic", "p5r": "epic",
  "p4g": "epic", "disco-elysium": "epic", "civ6": "epic", "bannerlord": "epic",
  "cities-skylines": "epic", "rimworld": "epic", "dyson-sphere": "epic", "tww3": "epic",
  "factorio": "epic", "satisfactory": "epic", "stellaris": "epic", "ck3": "epic",
  "aoe2": "epic", "gta5": "epic", "dos2": "epic",
}

def vibe_for(gid):
  return VIBES.get(gid, "epic")

# --- update manifests ---
for rel in ["games/manifest.json", "public/covers/manifest.json"]:
  path = ROOT / rel
  data = json.loads(path.read_text(encoding="utf-8"))
  missing = []
  counts = {}
  for g in data:
    v = vibe_for(g["id"])
    g["vibe"] = v
    counts[v] = counts.get(v, 0) + 1
    if g["id"] not in VIBES:
      missing.append(g["id"])
  path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  print(rel, "ok", counts, "unlisted→epic", missing)

# --- regenerate cardTexture.ts ---
data = json.loads((ROOT / "games/manifest.json").read_text(encoding="utf-8"))

def esc(s):
  return s.replace("\\", "\\\\").replace("'", "\\'")

lines = []
lines.append("/** Auto-generated from games/manifest.json */")
lines.append("export type CoverVibe = 'cozy' | 'neon' | 'epic' | 'souls' | 'arcade'")
lines.append("")
lines.append("export type CoverMeta = {")
lines.append("  id: string")
lines.append("  file: string")
lines.append("  titleZh: string")
lines.append("  titleEn: string")
lines.append("  blurb: string")
lines.append("  source: string")
lines.append("  type: 'steam-store-art' | 'stylized-placeholder'")
lines.append("  vibe: CoverVibe")
lines.append("}")
lines.append("")
lines.append("export const COVERS: CoverMeta[] = [")

for g in data:
  gid = g["id"]
  file = g["file"]
  zh = g["zh"]
  en = g["en"]
  blurb = g["blurb"]
  typ = g.get("type", "steam-store-art")
  vibe = g["vibe"]
  if typ == "stylized-placeholder":
    source = g.get("note") or "stylized placeholder"
  else:
    steam = g.get("steam")
    source = f"Steam CDN app/{steam}" if steam else (g.get("note") or "Steam CDN")
  lines.append("  {")
  lines.append(f"    id: '{esc(gid)}',")
  lines.append(f"    file: '{esc(file)}',")
  lines.append(f"    titleZh: '{esc(zh)}',")
  lines.append(f"    titleEn: '{esc(en)}',")
  lines.append(f"    blurb: '{esc(blurb)}',")
  lines.append(f"    source: '{esc(source)}',")
  lines.append(f"    type: '{typ}',")
  lines.append(f"    vibe: '{vibe}',")
  lines.append("  },")

lines.append("]")
lines.append("")
lines.append("export function coverUrl(file: string): string {")
lines.append("  return `${import.meta.env.BASE_URL}covers/${file}`")
lines.append("}")
lines.append("")

(ROOT / "src/cardTexture.ts").write_text("\n".join(lines), encoding="utf-8")
print("cardTexture.ts regenerated", len(data))

# verify dave vibe
assert next(g for g in data if g["id"]=="dave-diver")["vibe"]=="cozy"
assert next(g for g in data if g["id"]=="cyberpunk-2077")["vibe"]=="neon"
assert next(g for g in data if g["id"]=="elden-ring")["vibe"]=="souls"
assert next(g for g in data if g["id"]=="rdr2")["vibe"]=="epic"
print("vibe asserts ok")
print("TOTAL", {v: sum(1 for g in data if g["vibe"]==v) for v in ["cozy","neon","epic","souls","arcade"]})
