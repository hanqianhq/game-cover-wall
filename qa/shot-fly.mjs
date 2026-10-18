import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 60000 });
await page.waitForTimeout(1200);

await page.evaluate(() => window.__openCoverById("dead-cells"));
await page.waitForSelector("#focus.show");
// wait for fly-out ease (~0.4s)
await page.waitForTimeout(900);

const info = await page.evaluate(() => ({
  title: document.querySelector("#focus-title")?.textContent,
  imgCount: document.querySelectorAll("#focus img").length,
  show: !!document.querySelector("#focus.show"),
}));
console.log(info);

await page.screenshot({ path: "qa/flyout-after.png", type: "png" });
fs.copyFileSync("qa/flyout-after.png", "C:/Users/Administrator/agent-tools/flyout-after.png");
console.log("saved", fs.statSync("C:/Users/Administrator/agent-tools/flyout-after.png").size);

const ok = info.show && info.title === "\u6b7b\u4ea1\u7ec6\u80de" && info.imgCount === 0;
console.log("QA_PASS", ok, "(no DOM cover img, 3D only)");
await browser.close();
process.exit(ok ? 0 : 2);
