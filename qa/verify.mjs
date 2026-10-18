import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 30000 });
await page.waitForTimeout(1800);
await page.screenshot({ path: "qa/after.png", type: "png" });

const sample = await page.evaluate(() => {
  const c = document.querySelector("canvas");
  const off = document.createElement("canvas");
  off.width = c.width; off.height = c.height;
  const g = off.getContext("2d");
  g.drawImage(c, 0, 0);
  let bright = 0, total = 0, maxLum = 0;
  const heat = [];
  for (let y = 0; y < 10; y++) {
    const row = [];
    for (let x = 0; x < 14; x++) {
      const px = Math.floor(((x + 0.5) / 14) * c.width);
      const py = Math.floor(((y + 0.5) / 10) * c.height);
      const d = g.getImageData(px, py, 1, 1).data;
      const lum = 0.2126 * d[0] + 0.7152 * d[1] + 0.0722 * d[2];
      total++;
      if (lum > 35) bright++;
      if (lum > maxLum) maxLum = lum;
      row.push(lum > 50 ? "#" : lum > 25 ? "." : " ");
    }
    heat.push(row.join(""));
  }
  const cx = Math.floor(c.width / 2), cy = Math.floor(c.height / 2);
  const center = g.getImageData(cx, cy, 1, 1).data;
  const centerLum = 0.2126 * center[0] + 0.7152 * center[1] + 0.0722 * center[2];
  // also check a 120px neighborhood around center for any bright pixel
  let near = 0;
  for (let dy = -60; dy <= 60; dy += 20) {
    for (let dx = -60; dx <= 60; dx += 20) {
      const d = g.getImageData(cx + dx, cy + dy, 1, 1).data;
      const lum = 0.2126 * d[0] + 0.7152 * d[1] + 0.0722 * d[2];
      if (lum > 40) near++;
    }
  }
  return { coverage: bright / total, maxLum, centerLum, near, heat };
});

console.log("coverage", sample.coverage.toFixed(3), "centerLum", sample.centerLum.toFixed(1), "nearCenterBright", sample.near, "maxLum", sample.maxLum.toFixed(1));
console.log(sample.heat.join("\n"));
console.log("bytes", fs.statSync("qa/after.png").size);

// Pass: wall fills most of frame; center area has cover content nearby
const ok = sample.coverage > 0.45 && sample.near >= 3 && sample.maxLum > 80;
console.log("QA_PASS", ok);
await browser.close();
process.exit(ok ? 0 : 2);
