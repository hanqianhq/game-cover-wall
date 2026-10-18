# -*- coding: utf-8 -*-
from pathlib import Path
ROOT = Path(r"D:\Code\visual-lab\sketches\2026-10-18-liquid-glass")

# --- index.html: add vibe frame elements inside focus-card ---
html = """<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, viewport-fit=cover\" />
    <meta name=\"description\" content=\"游戏封面墙\" />
    <title>游戏封面墙 · visual-lab</title>
  </head>
  <body>
    <div id=\"app\">
      <canvas id=\"c\"></canvas>
      <div id=\"vignette\" aria-hidden=\"true\"></div>
      <div id=\"hud\">
        <h1>游戏封面墙</h1>
        <p>拖动浏览封面 · 点击即可飞出</p>
        <p class=\"hint\" id=\"backend\">WebGL</p>
      </div>
      <div id=\"focus\" hidden data-vibe=\"epic\">
        <div class=\"focus-card\" role=\"dialog\" aria-modal=\"true\">
          <div class=\"focus-fx\" aria-hidden=\"true\"></div>
          <button type=\"button\" id=\"focus-close\" aria-label=\"关闭\">×</button>
          <p class=\"focus-vibe-tag\" id=\"focus-vibe-tag\"></p>
          <h2 id=\"focus-title\"></h2>
          <p id=\"focus-en\" class=\"focus-en\"></p>
          <p id=\"focus-blurb\"></p>
          <p class=\"focus-hint\">按 Esc / 点空白 / × · 飞回</p>
        </div>
      </div>
      <div id=\"fallback\" hidden>
        <strong>当前浏览器无法初始化 WebGL</strong>
        <p>请换 Chrome / Edge / Firefox 最新版再试。</p>
      </div>
    </div>
    <script type=\"module\" src=\"/src/main.ts\"></script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(html, encoding="utf-8")
print("index.html written")

css = r'''/* liquid-glass · vibe-aware focus panel */
:root {
  color-scheme: dark;
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, #app { width: 100%; height: 100%; overflow: hidden; background: #1a2030; }
#c { display: block; width: 100%; height: 100%; touch-action: none; cursor: grab; }
#c:active { cursor: grabbing; }
body.focus-open #c { cursor: pointer; }

#vignette {
  position: fixed; inset: 0; z-index: 1; pointer-events: none;
  background: radial-gradient(
    ellipse 72% 68% at 50% 48%,
    rgba(0,0,0,0) 0%,
    rgba(0,0,0,0) 42%,
    rgba(0,0,0,0.18) 68%,
    rgba(0,0,0,0.42) 86%,
    rgba(0,0,0,0.62) 100%
  );
}

#hud {
  position: fixed; left: 20px; bottom: 20px; z-index: 2;
  pointer-events: none; color: rgba(245,248,255,0.95);
  text-shadow: 0 1px 10px rgba(0,0,0,0.35);
  max-width: min(420px, 86vw);
}
#hud h1 { font-size: clamp(1.2rem, 2.2vw, 1.65rem); font-weight: 650; }
#hud p { margin-top: 6px; font-size: 0.92rem; opacity: 0.8; }
#hud .hint { font-size: 0.75rem; opacity: 0.55; }

/* Click-catcher — info strip is position:fixed, pinned to the 3D cover */
#focus {
  position: fixed; inset: 0; z-index: 4;
  background: rgba(4, 8, 16, 0);
  opacity: 0;
  transition: opacity 0.28s ease, background 0.4s ease;
  pointer-events: none;
  --vibe-accent: #c9a227;
  --vibe-accent-2: #8a7a6a;
}
#focus.show {
  opacity: 1; pointer-events: auto;
  background: rgba(4, 8, 16, 0.32);
}
#focus[hidden] { display: none; }

/* Ambient wash per vibe */
#focus.show[data-vibe="cozy"] {
  background: radial-gradient(ellipse 70% 60% at 55% 45%, rgba(126,200,200,0.22), rgba(18,28,32,0.38) 70%);
}
#focus.show[data-vibe="neon"] {
  background: radial-gradient(ellipse 70% 60% at 55% 45%, rgba(255,43,214,0.16), rgba(0,240,255,0.08) 40%, rgba(4,2,16,0.5) 75%);
}
#focus.show[data-vibe="epic"] {
  background: radial-gradient(ellipse 70% 55% at 50% 50%, rgba(20,16,10,0.15), rgba(0,0,0,0.55) 80%);
}
#focus.show[data-vibe="souls"] {
  background: radial-gradient(ellipse 70% 60% at 55% 55%, rgba(224,120,64,0.12), rgba(28,24,22,0.48) 72%);
}
#focus.show[data-vibe="arcade"] {
  background: radial-gradient(ellipse 70% 60% at 55% 45%, rgba(255,59,59,0.18), rgba(8,4,8,0.48) 75%);
}

.focus-card {
  position: fixed;
  left: 0; top: 0;
  width: min(300px, 34vw);
  padding: 20px 18px 16px;
  border-radius: 16px;
  background: rgba(14, 20, 32, 0.92);
  border: 1px solid rgba(255,255,255,0.14);
  color: #f4f7ff;
  z-index: 5;
  pointer-events: auto;
  opacity: 0;
  overflow: hidden;
  will-change: left, top, opacity, transform;
  isolation: isolate;
}
@media (max-width: 800px) {
  .focus-card { width: min(440px, 92vw); }
}

.focus-fx {
  position: absolute; inset: 0; pointer-events: none; z-index: 0;
  border-radius: inherit;
}
.focus-card > *:not(.focus-fx) { position: relative; z-index: 1; }

.focus-vibe-tag {
  display: inline-block;
  margin: 0 0 8px;
  padding: 2px 8px;
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-radius: 999px;
  opacity: 0.85;
  font-weight: 600;
}

#focus-close {
  position: absolute; top: 8px; right: 10px; z-index: 2;
  width: 32px; height: 32px; border: 0; border-radius: 999px;
  background: rgba(255,255,255,0.1); color: #fff;
  font-size: 1.3rem; line-height: 1; cursor: pointer;
}
#focus-close:hover { background: rgba(255,255,255,0.18); }
#focus-title { font-size: 1.22rem; font-weight: 700; padding-right: 34px; line-height: 1.25; }
.focus-en { margin-top: 3px; font-size: 0.78rem; opacity: 0.55; }
#focus-blurb { margin-top: 10px; font-size: 0.92rem; line-height: 1.55; opacity: 0.92; }
.focus-hint { margin-top: 12px; font-size: 0.7rem; opacity: 0.5; }

/* ========== COZY ========== */
#focus[data-vibe="cozy"] {
  --vibe-accent: #7ec8c8;
  --vibe-accent-2: #f5e6c8;
}
#focus[data-vibe="cozy"] .focus-card {
  background: linear-gradient(165deg, #f7efe0 0%, #e8f4f2 55%, #d9ebe8 100%);
  color: #2a3a38;
  border: 3px solid #7ec8c8;
  border-radius: 22px;
  box-shadow:
    0 0 0 4px #f5e6c8,
    0 16px 36px rgba(60, 100, 100, 0.28);
  backdrop-filter: none;
}
#focus[data-vibe="cozy"] .focus-fx {
  background:
    radial-gradient(circle at 12% 18%, rgba(126,200,200,0.35), transparent 42%),
    radial-gradient(circle at 88% 82%, rgba(245,230,200,0.45), transparent 40%);
}
#focus[data-vibe="cozy"] .focus-vibe-tag {
  background: #7ec8c8; color: #1e3534;
}
#focus[data-vibe="cozy"] #focus-close {
  background: rgba(126,200,200,0.35); color: #2a3a38;
}
#focus[data-vibe="cozy"] #focus-close:hover { background: rgba(126,200,200,0.55); }
#focus[data-vibe="cozy"] .focus-en { opacity: 0.55; color: #4a6460; }
#focus[data-vibe="cozy"] #focus-blurb { color: #334846; opacity: 1; }
#focus[data-vibe="cozy"] .focus-hint { color: #5a7874; opacity: 0.75; }
#focus.show[data-vibe="cozy"] .focus-card {
  animation: vibe-cozy-in 0.55s cubic-bezier(0.22, 1.2, 0.36, 1) both;
}
@keyframes vibe-cozy-in {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== NEON ========== */
#focus[data-vibe="neon"] {
  --vibe-accent: #00f0ff;
  --vibe-accent-2: #ff2bd6;
}
#focus[data-vibe="neon"] .focus-card {
  background: rgba(6, 4, 18, 0.92);
  color: #e8fcff;
  border: 1px solid #00f0ff;
  border-radius: 6px;
  box-shadow:
    0 0 0 1px #ff2bd6,
    0 0 22px rgba(0,240,255,0.35),
    0 0 40px rgba(255,43,214,0.22),
    0 18px 40px rgba(0,0,0,0.55);
  backdrop-filter: blur(10px);
  clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
}
#focus[data-vibe="neon"] .focus-fx {
  background:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,240,255,0.04) 2px,
      rgba(0,240,255,0.04) 3px
    ),
    linear-gradient(120deg, rgba(0,240,255,0.08), transparent 40%, rgba(255,43,214,0.1));
  mix-blend-mode: screen;
}
#focus[data-vibe="neon"] .focus-vibe-tag {
  background: transparent;
  color: #00f0ff;
  border: 1px solid #ff2bd6;
  letter-spacing: 0.14em;
  box-shadow: 0 0 8px rgba(255,43,214,0.4);
}
#focus[data-vibe="neon"] #focus-close {
  background: rgba(0,240,255,0.12); color: #00f0ff; border-radius: 2px;
  box-shadow: 0 0 8px rgba(0,240,255,0.3);
}
#focus[data-vibe="neon"] #focus-title {
  text-shadow: 0 0 12px rgba(0,240,255,0.45);
  font-weight: 750;
}
#focus[data-vibe="neon"] .focus-en { color: #ff2bd6; opacity: 0.8; }
#focus[data-vibe="neon"] .focus-hint { color: #7ad4e0; opacity: 0.65; }
#focus.show[data-vibe="neon"] .focus-card {
  animation: vibe-neon-in 0.42s cubic-bezier(0.2, 0.9, 0.25, 1) both;
}
@keyframes vibe-neon-in {
  from { opacity: 0; transform: translateX(36px); filter: brightness(1.4); }
  to { opacity: 1; transform: translateX(0); filter: brightness(1); }
}

/* ========== EPIC ========== */
#focus[data-vibe="epic"] {
  --vibe-accent: #c9a227;
  --vibe-accent-2: #8a7350;
}
#focus[data-vibe="epic"] .focus-card {
  background: linear-gradient(180deg, rgba(22,18,14,0.55) 0%, rgba(12,10,8,0.94) 28%, rgba(8,7,6,0.96) 100%);
  color: #f3ead8;
  border: none;
  border-top: 1px solid rgba(201,162,39,0.55);
  border-bottom: 1px solid rgba(201,162,39,0.25);
  border-radius: 2px;
  box-shadow:
    0 -1px 0 rgba(201,162,39,0.35),
    0 20px 50px rgba(0,0,0,0.65);
  backdrop-filter: blur(12px);
  padding-top: 22px;
}
#focus[data-vibe="epic"] .focus-fx {
  background:
    linear-gradient(90deg, transparent, rgba(201,162,39,0.15), transparent),
    linear-gradient(180deg, rgba(201,162,39,0.08), transparent 30%);
}
#focus[data-vibe="epic"] .focus-fx::after {
  content: "";
  position: absolute; left: 18px; right: 18px; top: 10px; height: 1px;
  background: linear-gradient(90deg, transparent, #c9a227, transparent);
  opacity: 0.7;
}
#focus[data-vibe="epic"] .focus-vibe-tag {
  background: transparent;
  color: #c9a227;
  border: 1px solid rgba(201,162,39,0.45);
  border-radius: 2px;
  letter-spacing: 0.16em;
  font-weight: 500;
}
#focus[data-vibe="epic"] #focus-close {
  background: transparent; color: #c9a227;
  border: 1px solid rgba(201,162,39,0.4); border-radius: 2px;
}
#focus[data-vibe="epic"] #focus-close:hover { background: rgba(201,162,39,0.15); }
#focus[data-vibe="epic"] #focus-title {
  font-weight: 600; letter-spacing: 0.02em;
  font-family: "Segoe UI Semibold", "PingFang SC", "Microsoft YaHei", serif;
}
#focus[data-vibe="epic"] .focus-en { opacity: 0.5; letter-spacing: 0.04em; }
#focus[data-vibe="epic"] .focus-hint { opacity: 0.45; color: #c9a227; }
#focus.show[data-vibe="epic"] .focus-card {
  animation: vibe-epic-in 0.7s ease both;
}
@keyframes vibe-epic-in {
  from { opacity: 0; transform: translateY(8px); filter: blur(2px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}

/* ========== SOULS ========== */
#focus[data-vibe="souls"] {
  --vibe-accent: #e07840;
  --vibe-accent-2: #8a7a6a;
}
#focus[data-vibe="souls"] .focus-card {
  background: linear-gradient(165deg, #3a3530 0%, #2a2622 45%, #1c1916 100%);
  color: #d8cfc4;
  border: 1px solid #8a7a6a;
  border-radius: 4px;
  box-shadow:
    0 0 0 1px rgba(224,120,64,0.25),
    0 0 28px rgba(224,120,64,0.12),
    0 18px 42px rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
}
#focus[data-vibe="souls"] .focus-fx {
  background:
    radial-gradient(ellipse at 50% 110%, rgba(224,120,64,0.28), transparent 55%),
    linear-gradient(180deg, rgba(138,122,106,0.12), transparent 40%);
}
#focus[data-vibe="souls"] .focus-vibe-tag {
  background: rgba(224,120,64,0.15);
  color: #e07840;
  border: 1px solid rgba(224,120,64,0.4);
  border-radius: 2px;
  letter-spacing: 0.12em;
}
#focus[data-vibe="souls"] #focus-close {
  background: rgba(138,122,106,0.25); color: #e07840; border-radius: 2px;
}
#focus[data-vibe="souls"] #focus-title {
  font-weight: 650; color: #ebe4da;
  text-shadow: 0 0 18px rgba(224,120,64,0.25);
}
#focus[data-vibe="souls"] .focus-en { color: #8a7a6a; opacity: 0.9; }
#focus[data-vibe="souls"] #focus-blurb { color: #c4b8a8; }
#focus[data-vibe="souls"] .focus-hint { color: #e07840; opacity: 0.55; }
#focus.show[data-vibe="souls"] .focus-card {
  animation: vibe-souls-in 0.65s ease both;
}
@keyframes vibe-souls-in {
  from { opacity: 0; transform: translateY(28px); }
  40% { opacity: 0.35; }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== ARCADE ========== */
#focus[data-vibe="arcade"] {
  --vibe-accent: #ff3b3b;
  --vibe-accent-2: #ffe566;
}
#focus[data-vibe="arcade"] .focus-card {
  background: #120808;
  color: #fff8e8;
  border: 4px solid #ff3b3b;
  border-radius: 4px;
  box-shadow:
    0 0 0 3px #ffe566,
    0 0 0 6px #120808,
    6px 6px 0 #ff3b3b,
    0 16px 36px rgba(0,0,0,0.5);
  backdrop-filter: none;
  transform-origin: center center;
}
#focus[data-vibe="arcade"] .focus-fx {
  background:
    repeating-linear-gradient(
      -12deg,
      transparent,
      transparent 10px,
      rgba(255,229,102,0.04) 10px,
      rgba(255,229,102,0.04) 12px
    );
}
#focus[data-vibe="arcade"] .focus-vibe-tag {
  background: #ff3b3b;
  color: #ffe566;
  border-radius: 2px;
  letter-spacing: 0.12em;
  font-weight: 800;
  box-shadow: 2px 2px 0 #ffe566;
}
#focus[data-vibe="arcade"] #focus-close {
  background: #ffe566; color: #120808; border-radius: 2px; font-weight: 800;
}
#focus[data-vibe="arcade"] #focus-close:hover { background: #ff3b3b; color: #ffe566; }
#focus[data-vibe="arcade"] #focus-title {
  font-weight: 850; letter-spacing: 0.01em;
  text-shadow: 2px 2px 0 #ff3b3b;
}
#focus[data-vibe="arcade"] .focus-en { color: #ffe566; opacity: 0.9; font-weight: 600; }
#focus[data-vibe="arcade"] .focus-hint { color: #ff3b3b; opacity: 0.75; font-weight: 600; }
#focus.show[data-vibe="arcade"] .focus-card {
  animation: vibe-arcade-in 0.38s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
@keyframes vibe-arcade-in {
  from { opacity: 0; transform: scale(0.82); }
  70% { transform: scale(1.04); }
  to { opacity: 1; transform: scale(1); }
}

#fallback {
  position: fixed; inset: 0; z-index: 5;
  display: grid; place-content: center; gap: 10px;
  padding: 24px; text-align: center; background: #121722; color: #e8eef8;
}
#fallback[hidden] { display: none; }
'''
(ROOT / "src/style.css").write_text(css, encoding="utf-8")
print("style.css written", len(css))
