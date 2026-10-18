import { chromium } from "playwright";
import fs from "fs";
import path from "path";

fs.mkdirSync("qa", { recursive: true });
fs.mkdirSync("C:/Users/Administrator/agent-tools", { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 30000 });
await page.waitForTimeout(1500);

// Wall shot
await page.screenshot({ path: "qa/sharp-wall.png", type: "png" });

// Click center cover to open focus panel
await page.locator("#c").click({ position: { x: 720, y: 450 } });
await page.waitForTimeout(900);
const focusVisible = await page.locator("#focus.show").count();
const title = await page.locator("#focus-title").innerText().catch(() => "");
console.log("focusVisible", focusVisible, "title", title);

await page.screenshot({ path: "qa/sharp-after.png", type: "png" });

// If focus didn't open, try a few nearby points
if (!focusVisible) {
  for (const [x, y] of [[720, 400], [650, 450], [800, 450], [720, 520]]) {
    await page.locator("#c").click({ position: { x, y } });
    await page.waitForTimeout(700);
    if (await page.locator("#focus.show").count()) break;
  }
  await page.screenshot({ path: "qa/sharp-after.png", type: "png" });
}

const finalTitle = await page.locator("#focus-title").innerText().catch(() => "");
const finalShow = await page.locator("#focus.show").count();
console.log("final focus", finalShow, finalTitle);

// Copy to agent-tools
for (const name of ["sharp-after.png", "sharp-wall.png"]) {
  const src = path.join("qa", name);
  const dst = path.join("C:/Users/Administrator/agent-tools", name);
  fs.copyFileSync(src, dst);
  console.log("copied", dst, fs.statSync(dst).size);
}

// Pixel check: center region should not be mostly black when focused
const sample = await page.evaluate(() => {
  const c = document.querySelector("canvas");
  const off = document.createElement("canvas");
  off.width = c.width; off.height = c.height;
  const g = off.getContext("2d");
  g.drawImage(c, 0, 0);
  let bright = 0, total = 0;
  for (let y = 3; y < 7; y++) {
    for (let x = 5; x < 9; x++) {
      const px = Math.floor(((x + 0.5) / 14) * c.width);
      const py = Math.floor(((y + 0.5) / 10) * c.height);
      const d = g.getImageData(px, py, 1, 1).data;
      const lum = 0.2126 * d[0] + 0.7152 * d[1] + 0.0722 * d[2];
      total++;
      if (lum > 40) bright++;
    }
  }
  return { coverage: bright / total, hasFocusDom: !!document.querySelector("#focus.show") };
});
console.log("sample", sample);
await browser.close();
process.exit(sample.hasFocusDom && sample.coverage > 0.3 ? 0 : 2);
