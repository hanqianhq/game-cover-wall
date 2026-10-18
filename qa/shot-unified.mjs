import { chromium } from "playwright";
import fs from "fs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));
page.on("console", (m) => { if (m.type() === "error") console.log("CONSOLE", m.text()); });

await page.goto("http://127.0.0.1:5188/?v=unified2", { waitUntil: "networkidle", timeout: 120000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 120000 });
await page.waitForTimeout(1500);

const probe = await page.evaluate(() => ({
  hasHelper: typeof window.__openCoverById === "function",
  hasFocus: !!document.querySelector("#focus"),
  hasVibeTag: !!document.querySelector("#focus-vibe-tag"),
  hasFx: !!document.querySelector(".focus-fx"),
  hasDataVibe: document.querySelector("#focus")?.hasAttribute("data-vibe") ?? false,
  cssText: [...document.styleSheets].length,
}));
console.log("probe", JSON.stringify(probe));

await page.evaluate(() => {
  window.__openCoverById("dave-diver");
});
await page.waitForTimeout(1500);

const after = await page.evaluate(() => ({
  show: document.querySelector("#focus")?.classList.contains("show"),
  hidden: document.querySelector("#focus")?.hidden,
  title: document.querySelector("#focus-title")?.textContent,
  en: document.querySelector("#focus-en")?.textContent,
}));
console.log("after", JSON.stringify(after));

if (!after.show) {
  // try clicking center card as fallback
  await page.mouse.click(720, 450);
  await page.waitForTimeout(2000);
  const afterClick = await page.evaluate(() => ({
    show: document.querySelector("#focus")?.classList.contains("show"),
    title: document.querySelector("#focus-title")?.textContent,
  }));
  console.log("afterClick", JSON.stringify(afterClick));
}

await page.waitForSelector("#focus.show", { timeout: 10000 }).catch(() => null);
await page.waitForTimeout(900);

const info = await page.evaluate(() => {
  const card = document.querySelector(".focus-card");
  const cs = card ? getComputedStyle(card) : null;
  return {
    title: document.querySelector("#focus-title")?.textContent,
    en: document.querySelector("#focus-en")?.textContent,
    hasVibeAttr: document.querySelector("#focus")?.hasAttribute("data-vibe") ?? null,
    hasVibeTag: !!document.querySelector("#focus-vibe-tag"),
    hasFx: !!document.querySelector(".focus-fx"),
    bg: cs?.backgroundColor,
    radius: cs?.borderRadius,
    blur: cs?.backdropFilter || (cs)?.webkitBackdropFilter,
  };
});
console.log("info", JSON.stringify(info, null, 2));

await page.screenshot({ path: "qa/unified-dave.png", type: "png" });
fs.mkdirSync("C:/Users/Administrator/agent-tools", { recursive: true });
fs.copyFileSync("qa/unified-dave.png", "C:/Users/Administrator/agent-tools/unified-dave.png");
await browser.close();
console.log("SHOT_OK");