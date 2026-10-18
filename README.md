# Infinite Liquid Glass ? Game Cover Wall

Browser-playable liquid-glass wall of **8 unique Steam store covers** (no placeholders, no duplicates). Drag to browse, click a cover to pop it forward with title + blurb.

## Run

```bash
cd D:\Code\visual-lab\sketches\2026-10-18-liquid-glass
pnpm install
pnpm dev
```

http://localhost:5188

## Build / share

```bash
pnpm build
pnpm preview
```

Static output in `dist/` (includes `covers/`). Drop on any static host (`base: './'`).

## Covers (Steam CDN only)

| Game | File | Source |
|---|---|---|
| NieR:Automata | nier-automata.jpg | app/524220 |
| Monster Hunter Wilds | monster-hunter-wilds.jpg | app/2246340 |
| Cyberpunk 2077 | cyberpunk-2077.jpg | app/1091500 |
| Stellar Blade | stellar-blade.jpg | app/3489700 |
| Elden Ring | elden-ring.jpg | app/1245620 |
| Black Myth: Wukong | black-myth-wukong.jpg | app/2358720 |
| Baldur's Gate 3 | baldurs-gate-3.jpg | app/1086940 |
| The Witcher 3 | witcher-3.jpg | app/292030 |

See `public/covers/manifest.json`. Store art for demo/share; check platform rules before public deploy.

## References

- Effect: [Codrops Infinite Liquid Glass](https://tympanus.net/codrops/2026/09/08/building-an-infinite-liquid-glass-grid-with-three-js-webgpu-and-tsl/)
- Demo: https://infinite-liquid-glass.shader.se/
- Covers: Steam CDN `library_600x900_2x.jpg`

From-scratch WebGL remix for visual-engineering sharing.
