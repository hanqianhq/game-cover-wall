import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
m=json.load(open("games/manifest.json",encoding="utf-8"))
print("manifest", len(m))
ct=Path("src/cardTexture.ts").read_text(encoding="utf-8")
print("vibe fields", ct.count("vibe:"))
print("animal", next(g for g in m if g["id"]=="animal-well"))
ids=[g["id"] for g in m]
for i in ["genshin","star-rail","zzz","honkai-3rd","wuthering-waves","reverse-1999","pgr","dave-diver"]:
    print(i, "in", i in ids)
vc={}
for g in m: vc[g["vibe"]]=vc.get(g["vibe"],0)+1
print(vc)
print("covers files", len(list(Path("public/covers").glob("*.*"))))
