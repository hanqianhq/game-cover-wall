# -*- coding: utf-8 -*-
from pathlib import Path
ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")
s = (ROOT/"src/main.ts").read_text(encoding="utf-8")
i = s.find("function positionInfoBesideCover")
print(s[i:i+1800])
