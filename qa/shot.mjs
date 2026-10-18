import { chromium } from "playwright";
import fs from "fs";
fs.mkdirSync("qa", { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
page.on("console", (m) => { if (m.type() === "error") console.log("CONSOLE", m.text()); });
await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForTimeout(2500);
await page.screenshot({ path: "qa/before.png", fullPage: false });
const stats = await page.evaluate(() => {
  const c = document.querySelector("canvas");
  return { canvas: !!c, w: c?.width, h: c?.height, body: document.body.innerText.slice(0, 200) };
});
console.log("stats", JSON.stringify(stats));
await browser.close();
console.log("saved qa/before.png", fs.statSync("qa/before.png").size);
