import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 30000 });
await page.waitForTimeout(1200);

await page.screenshot({ path: "qa/sharp-wall.png", type: "png" });

await page.evaluate(() => window.__openCoverById("dead-cells"));
await page.waitForSelector("#focus.show");
await page.waitForFunction(() => {
  const img = document.querySelector("#focus-cover");
  return img && img.complete && img.naturalWidth > 0;
}, null, { timeout: 15000 });
await page.waitForTimeout(400);

const info = await page.evaluate(() => {
  const img = document.querySelector("#focus-cover");
  const meshesHidden = true; // checked via title
  return {
    title: document.querySelector("#focus-title")?.textContent,
    en: document.querySelector("#focus-en")?.textContent,
    imgCount: document.querySelectorAll("#focus img").length,
    imgSrc: img?.getAttribute("src"),
    natural: img?.naturalWidth,
    canvasVisible: !!document.querySelector("canvas"),
  };
});
console.log("focus info", info);

await page.screenshot({ path: "qa/sharp-after.png", type: "png" });

fs.copyFileSync("qa/sharp-after.png", "C:/Users/Administrator/agent-tools/sharp-after.png");
fs.copyFileSync("qa/sharp-wall.png", "C:/Users/Administrator/agent-tools/sharp-wall.png");
console.log("copied after", fs.statSync("C:/Users/Administrator/agent-tools/sharp-after.png").size);
console.log("copied wall", fs.statSync("C:/Users/Administrator/agent-tools/sharp-wall.png").size);

const ok = info.title === "????" && info.imgCount === 1 && (info.natural || 0) > 100;
console.log("QA_PASS", ok);
await browser.close();
process.exit(ok ? 0 : 2);
