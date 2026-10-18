import { chromium } from "playwright";
import fs from "fs";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:5188/?v=final3", { waitUntil: "networkidle", timeout: 120000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 120000 });
await page.waitForTimeout(1200);

async function openId(id) {
  // force-clear focus state via Esc + wait for flyback to finish
  await page.keyboard.press("Escape");
  await page.waitForTimeout(1800);
  const opened = await page.evaluate((id) => {
    window.__openCoverById(id);
    return !!document.querySelector("#focus.show");
  }, id);
  if (!opened) {
    await page.waitForTimeout(1500);
    await page.evaluate((id) => window.__openCoverById(id), id);
  }
  await page.waitForSelector("#focus.show", { timeout: 20000 });
  await page.waitForTimeout(900);
  return page.evaluate(() => ({
    vibe: document.querySelector("#focus")?.getAttribute("data-vibe"),
    tag: document.querySelector("#focus-vibe-tag")?.textContent,
    title: document.querySelector("#focus-title")?.textContent,
  }));
}

for (const [id, vibe, file] of [
  ["rdr2", "epic", "vibe-epic-rdr2.png"],
  ["helldivers-2", "arcade", "vibe-arcade-helldivers.png"],
]) {
  const info = await openId(id);
  console.log(id, info, "ok", info.vibe === vibe);
  await page.screenshot({ path: "qa/"+file, type: "png" });
  fs.copyFileSync("qa/"+file, "C:/Users/Administrator/agent-tools/"+file);
}
await page.keyboard.press("Escape");
await page.waitForTimeout(1500);
await page.screenshot({ path: "qa/wall-150.png", type: "png" });
fs.copyFileSync("qa/wall-150.png", "C:/Users/Administrator/agent-tools/wall-150.png");
await browser.close();
console.log("DONE");
