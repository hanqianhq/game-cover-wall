import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5189/?v=panel-h", { waitUntil: "networkidle", timeout: 120000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 120000 });
await page.waitForTimeout(600);
await page.evaluate(() => window.__openCoverById("rdr2"));
await page.waitForSelector("#focus.show", { timeout: 8000 });
await page.waitForTimeout(1200);

const info = await page.evaluate(() => {
  const card = document.querySelector(".focus-card");
  const cs = getComputedStyle(card);
  const r = card.getBoundingClientRect();
  return {
    title: document.querySelector("#focus-title")?.textContent,
    tags: [...document.querySelectorAll("#focus-tags span")].map((n) => n.textContent),
    review: document.querySelector("#focus-review")?.textContent,
    styleH: card.style.height,
    rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), b: Math.round(r.bottom) },
    display: cs.display,
    flexDir: cs.flexDirection,
    blurbFlex: getComputedStyle(document.querySelector("#focus-blurb")).flexGrow,
    hintMarginTop: getComputedStyle(document.querySelector(".focus-hint")).marginTop,
    blur: cs.backdropFilter,
    vibe: document.querySelector("#focus")?.getAttribute("data-vibe"),
  };
});
console.log(JSON.stringify(info, null, 2));
await page.screenshot({ path: "qa/panel-match-height.png", type: "png" });
await browser.close();
