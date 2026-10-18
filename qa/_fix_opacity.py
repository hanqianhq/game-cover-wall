# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass\src\style.css")
css = p.read_text(encoding="utf-8")
# Fix base opacity so exit fades with #focus parent
old = """  pointer-events: auto;
  opacity: 0;
  overflow: hidden;"""
new = """  pointer-events: auto;
  opacity: 1;
  overflow: hidden;"""
if old not in css:
    raise SystemExit("opacity block not found")
p.write_text(css.replace(old, new, 1), encoding="utf-8")
print("opacity fixed")
