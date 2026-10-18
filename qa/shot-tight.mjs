import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 60000 });
await page.waitForTimeout(1000);

await page.evaluate(() => window.__openCoverById("dead-cells"));
await page.waitForSelector("#focus.show");
await page.waitForTimeout(1000);

const info = await page.evaluate(() => {
  const panel = document.querySelector(".focus-card");
  const r = panel.getBoundingClientRect();
  const imgs = document.querySelectorAll("#focus img").length;
  // count how many canvases / check no second cover img in DOM
  return {
    title: document.querySelector("#focus-title")?.textContent,
    imgCount: imgs,
    show: !!document.querySelector("#focus.show"),
    panel: { left: Math.round(r.left), top: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) },
    // sample canvas: ensure WebGL still drawing
    canvasOk: !!document.querySelector("#c"),
  };
});
console.log(JSON.stringify(info, null, 2));

// panel should not be stuck at far right (left should be < ~900 for 1440 wide)
const tight = info.panel.left < 980 && info.panel.left > 200;
const noImg = info.imgCount === 0;
console.log("tight-ish", tight, "noDomImg", noImg);

await page.screenshot({ path: "qa/flyout-tight.png", type: "png" });
fs.copyFileSync("qa/flyout-tight.png", "C:/Users/Administrator/agent-tools/flyout-tight.png");
console.log("saved", fs.statSync("C:/Users/Administrator/agent-tools/flyout-tight.png").size);

const ok = info.show && info.title === "\u6b7b\u4ea1\u7ec6\u80de" && noImg && tight;
console.log("QA_PASS", ok);
await browser.close();
process.exit(ok ? 0 : 2);
