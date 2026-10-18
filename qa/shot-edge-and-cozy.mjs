import { chromium } from "playwright";
import fs from "fs";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:5188/?r="+Date.now(), { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 90000 });
await page.waitForTimeout(1200);
const fill = await page.evaluate(() => {
  const c = document.querySelector("#c");
  const gl = c.getContext("webgl2") || c.getContext("webgl");
  const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
  const midY = Math.floor(h * 0.5);
  const lum = (x) => { const px = new Uint8Array(4); gl.readPixels(x, midY, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); return 0.2126*px[0]+0.7152*px[1]+0.0722*px[2]; };
  return { leftIn: Math.round(lum(Math.floor(w*0.06))), rightIn: Math.round(lum(Math.floor(w*0.94))), center: Math.round(lum(Math.floor(w*0.5))) };
});
console.log("fill", fill);
await page.screenshot({ path: "qa/edge-fill-after.png", type: "png" });
fs.copyFileSync("qa/edge-fill-after.png", "C:/Users/Administrator/agent-tools/edge-fill-after.png");
// open dave cozy vibe
await page.evaluate(() => window.__openCoverById("dave-diver"));
await page.waitForSelector("#focus.show");
await page.waitForTimeout(800);
const vibe = await page.evaluate(() => ({ vibe: document.querySelector("#focus")?.getAttribute("data-vibe"), tag: document.querySelector("#focus-vibe-tag")?.textContent, title: document.querySelector("#focus-title")?.textContent }));
console.log("cozy focus", vibe);
await page.screenshot({ path: "qa/vibe-cozy-dave.png", type: "png" });
fs.copyFileSync("qa/vibe-cozy-dave.png", "C:/Users/Administrator/agent-tools/vibe-cozy-dave.png");
await browser.close();
console.log("SHOTS_OK");
