# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass\qa\expand100.mjs")
print(p.read_text(encoding="utf-8")[3500:])
print("==== main COLS ====")
s = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass\src\main.ts").read_text(encoding="utf-8")
for key in ["COLS", "ROWS", "nCovers", "COVERS.length", "wrapIndex", "coverIndex"]:
    print(key, s.count(key))
# print relevant snippets
import re
for m in re.finditer(r".{0,40}(COLS|ROWS|nCovers|wrapIndex|coverIndex).{0,80}", s):
    line = m.group(0).replace("\n"," ")
    if "const COLS" in line or "const ROWS" in line or "nCovers" in line or "wrapIndex" in line or "coverIndex =" in line or "coverIndex:" in line:
        print(line[:160])
