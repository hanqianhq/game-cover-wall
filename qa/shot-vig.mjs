import { chromium } from "playwright";
import fs from "fs";

fs.mkdirSync("qa", { recursive: true });
fs.mkdirSync("C:/Users/Administrator/agent-tools", { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 30000 });
await page.waitForTimeout(1200);

await page.screenshot({ path: "qa/vignette-after.png", type: "png" });
fs.copyFileSync("qa/vignette-after.png", "C:/Users/Administrator/agent-tools/vignette-after.png");

const has = await page.locator("#vignette").count();
console.log("vignette el", has, "bytes", fs.statSync("C:/Users/Administrator/agent-tools/vignette-after.png").size);
await browser.close();
