# -*- coding: utf-8 -*-
from pathlib import Path
ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")
path = ROOT / "src/main.ts"
s = path.read_text(encoding="utf-8")

# Update import to include CoverVibe if useful
old_import = "import { COVERS, coverUrl, type CoverMeta } from './cardTexture'"
new_import = "import { COVERS, coverUrl, type CoverMeta, type CoverVibe } from './cardTexture'"
if old_import not in s:
    raise SystemExit("import not found")
s = s.replace(old_import, new_import, 1)

# Add focusVibeTag after focusClose
needle = "  const focusClose = document.querySelector<HTMLButtonElement>('#focus-close')!"
if needle not in s:
    raise SystemExit("focusClose not found")
insert = needle + "\n  const focusVibeTag = document.querySelector<HTMLElement>('#focus-vibe-tag')!\n  const VIBE_LABEL: Record<CoverVibe, string> = {\n    cozy: '治愈',\n    neon: '赛博',\n    epic: '史诗',\n    souls: '魂系',\n    arcade: '街机',\n  }"
s = s.replace(needle, insert, 1)

# Patch openFocus body to set vibe
old_open = """    hideDuplicateCovers(card)
    focusTitle.textContent = cover.titleZh
    if (focusEn) focusEn.textContent = cover.titleEn
    focusBlurb.textContent = cover.blurb
    focusEl.hidden = false
    focusEl.classList.add('show')
    document.body.classList.add('focus-open')
  }"""

new_open = """    hideDuplicateCovers(card)
    const vibe: CoverVibe = cover.vibe ?? 'epic'
    focusEl.dataset.vibe = vibe
    if (focusVibeTag) focusVibeTag.textContent = VIBE_LABEL[vibe]
    focusTitle.textContent = cover.titleZh
    if (focusEn) focusEn.textContent = cover.titleEn
    focusBlurb.textContent = cover.blurb
    // retrigger entrance animation for this vibe
    const cardEl = document.querySelector<HTMLElement>('.focus-card')
    if (cardEl) {
      cardEl.style.animation = 'none'
      void cardEl.offsetWidth
      cardEl.style.animation = ''
    }
    focusEl.hidden = false
    focusEl.classList.add('show')
    document.body.classList.add('focus-open')
  }"""

if old_open not in s:
    raise SystemExit("openFocus block not found")
s = s.replace(old_open, new_open, 1)

# On close, keep data-vibe until hidden (ambient wash stays consistent during fade)
old_close_tail = """    focusDir = -1
    focusT = 0
    focusEl.classList.remove('show')
    document.body.classList.remove('focus-open')
  }"""
# leave as-is — fine

path.write_text(s, encoding="utf-8")
print("main.ts patched")
# sanity
assert "dataset.vibe" in s
assert "VIBE_LABEL" in s
assert "CoverVibe" in s
print("ok")
