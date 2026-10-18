# -*- coding: utf-8 -*-
from pathlib import Path
s = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass\src\main.ts").read_text(encoding="utf-8")
print("dataset.vibe" in s, "VIBE_LABEL" in s, "focus-vibe-tag" in s)
i = s.find("dataset.vibe")
print(s[i-200:i+400])
print("--- html ---")
h = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass\index.html").read_text(encoding="utf-8")
print("focus-vibe-tag" in h, "data-vibe" in h)
print(h[h.find("id=\"focus\""):h.find("id=\"focus\"")+500])
print("--- cardTexture vibe ---")
ct = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass\src\cardTexture.ts").read_text(encoding="utf-8")
print("vibe:" in ct, ct.count("vibe:"))
# dave entry
i = ct.find("dave-diver")
print(ct[i:i+280])
