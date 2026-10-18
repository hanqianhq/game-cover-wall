import { chromium } from "playwright";
import fs from "fs";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", e => console.log("PAGEERROR", e.message));
await page.goto("http://127.0.0.1:5188/?v=150", { waitUntil: "networkidle", timeout: 120000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 120000 });
await page.waitForTimeout(1500);
await page.screenshot({ path: "qa/wall-150.png", type: "png" });
fs.copyFileSync("qa/wall-150.png", "C:/Users/Administrator/agent-tools/wall-150.png");

const shots = [
  ["cyberpunk-2077", "neon", "vibe-neon-cyberpunk.png"],
  ["elden-ring", "souls", "vibe-souls-elden.png"],
  ["rdr2", "epic", "vibe-epic-rdr2.png"],
  ["genshin", "neon", "vibe-neon-genshin.png"],
];
for (const [id, vibe, file] of shots) {
  await page.keyboard.press("Escape");
  await page.waitForTimeout(600);
  await page.evaluate((id) => window.__openCoverById(id), id);
  await page.waitForSelector("#focus.show", { timeout: 15000 });
  await page.waitForTimeout(900);
  const info = await page.evaluate(() => ({
    vibe: document.querySelector("#focus")?.getAttribute("data-vibe"),
    tag: document.querySelector("#focus-vibe-tag")?.textContent,
    title: document.querySelector("#focus-title")?.textContent,
  }));
  console.log(id, info, "expect", vibe, info.vibe===vibe);
  await page.screenshot({ path: "qa/"+file, type: "png" });
  fs.copyFileSync("qa/"+file, "C:/Users/Administrator/agent-tools/"+file);
}
const fill = await page.evaluate(() => {
  const c = document.querySelector("#c");
  const gl = c.getContext("webgl2") || c.getContext("webgl");
  const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight, midY = (h/2)|0;
  const lum = (x) => { const px=new Uint8Array(4); gl.readPixels(x,midY,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px); return 0.2126*px[0]+0.7152*px[1]+0.0722*px[2]; };
  return { L: Math.round(lum((w*0.06)|0)), R: Math.round(lum((w*0.94)|0)) };
});
console.log("edge", fill);
await browser.close();
console.log("FINAL_QA_DONE");
