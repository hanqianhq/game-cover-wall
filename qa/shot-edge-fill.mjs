import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 60000 });
await page.waitForTimeout(1200);

// Sample left/right edge pixels from the WebGL canvas (exclude HUD)
const fill = await page.evaluate(() => {
  const c = document.querySelector("#c");
  const gl = c.getContext("webgl2") || c.getContext("webgl");
  if (!gl) return { err: "no gl" };
  const w = gl.drawingBufferWidth;
  const h = gl.drawingBufferHeight;
  const midY = Math.floor(h * 0.5);
  const readCol = (x) => {
    const px = new Uint8Array(4);
    gl.readPixels(x, midY, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return [px[0], px[1], px[2]];
  };
  // sample a strip near edges (canvas may have letterbox of dark bg)
  const leftSamples = [];
  const rightSamples = [];
  for (let i = 4; i < 40; i += 4) {
    leftSamples.push(readCol(i));
    rightSamples.push(readCol(w - 1 - i));
  }
  const lum = ([r,g,b]) => 0.2126*r + 0.7152*g + 0.0722*b;
  const leftAvg = leftSamples.reduce((a,p)=>a+lum(p),0) / leftSamples.length;
  const rightAvg = rightSamples.reduce((a,p)=>a+lum(p),0) / rightSamples.length;
  // also sample further in (where cards should definitely be)
  const leftIn = lum(readCol(Math.floor(w * 0.08)));
  const rightIn = lum(readCol(Math.floor(w * 0.92)));
  const center = lum(readCol(Math.floor(w * 0.5)));
  return {
    w, h,
    leftEdge: Math.round(leftAvg),
    rightEdge: Math.round(rightAvg),
    leftIn: Math.round(leftIn),
    rightIn: Math.round(rightIn),
    center: Math.round(center),
    // cards are bright; empty dark bg ~26 (0x1a2030)
    leftHasContent: leftIn > 40,
    rightHasContent: rightIn > 40,
    edgeBalance: Math.abs(leftIn - rightIn),
  };
});
console.log("fill", JSON.stringify(fill, null, 2));

await page.screenshot({ path: "qa/edge-fill-after.png", type: "png" });
fs.copyFileSync("qa/edge-fill-after.png", "C:/Users/Administrator/agent-tools/edge-fill-after.png");

const ok = fill.leftHasContent && fill.rightHasContent && fill.edgeBalance < 50;
console.log("EDGE_QA_PASS", ok, "balance", fill.edgeBalance);
await browser.close();
process.exit(ok ? 0 : 2);
