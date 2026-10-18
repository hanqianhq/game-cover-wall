import { chromium } from "playwright";
import fs from "fs";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:5188/?v=final2", { waitUntil: "networkidle", timeout: 120000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 120000 });
await page.waitForTimeout(1000);

async function openId(id) {
  await page.evaluate(() => {
    const el = document.querySelector("#focus");
    if (el?.classList.contains("show")) {
      document.querySelector("#focus-close")?.click();
    }
  });
  await page.waitForTimeout(900);
  await page.waitForFunction(() => !document.querySelector("#focus.show"), null, { timeout: 10000 }).catch(()=>{});
  await page.evaluate((id) => window.__openCoverById(id), id);
  await page.waitForSelector("#focus.show", { timeout: 15000 });
  await page.waitForTimeout(850);
  return page.evaluate(() => ({
    vibe: document.querySelector("#focus")?.getAttribute("data-vibe"),
    tag: document.querySelector("#focus-vibe-tag")?.textContent,
    title: document.querySelector("#focus-title")?.textContent,
  }));
}

for (const [id, vibe, file] of [
  ["rdr2", "epic", "vibe-epic-rdr2.png"],
  ["helldivers-2", "arcade", "vibe-arcade-helldivers.png"],
  ["dave-diver", "cozy", "vibe-cozy-dave.png"],
]) {
  const info = await openId(id);
  console.log(id, info, info.vibe === vibe);
  await page.screenshot({ path: "qa/"+file, type: "png" });
  fs.copyFileSync("qa/"+file, "C:/Users/Administrator/agent-tools/"+file);
}
await page.screenshot({ path: "qa/wall-150.png", type: "png" });
fs.copyFileSync("qa/wall-150.png", "C:/Users/Administrator/agent-tools/wall-150.png");
await browser.close();
console.log("DONE");
