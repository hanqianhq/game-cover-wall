import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 30000 });
await page.waitForTimeout(1200);

await page.evaluate(() => window.__openCoverById && window.__openCoverById("dead-cells"));
await page.waitForTimeout(1000);
const title = await page.locator("#focus-title").innerText();
const en = await page.locator("#focus-en").innerText();
console.log("opened", title, en, "show", await page.locator("#focus.show").count());

await page.screenshot({ path: "qa/sharp-after.png", type: "png" });
fs.copyFileSync("qa/sharp-after.png", "C:/Users/Administrator/agent-tools/sharp-after.png");
fs.copyFileSync("qa/sharp-wall.png", "C:/Users/Administrator/agent-tools/sharp-wall.png");
console.log("saved", fs.statSync("qa/sharp-after.png").size);
await browser.close();
