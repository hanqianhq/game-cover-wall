import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 60000 });
await page.waitForTimeout(1000);

const info = await page.evaluate(() => {
  // expose via scanning COVERS if available - pull from module not easy
  return {
    title: document.title,
    ready: window.__coverReady,
  };
});
console.log(info);
await page.screenshot({ path: "qa/wall-missing-check.png", type: "png" });
fs.copyFileSync("qa/wall-missing-check.png", "C:/Users/Administrator/agent-tools/wall-missing-check.png");
console.log("saved wall-missing-check.png");
await browser.close();
