import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/?v=steam-meta", { waitUntil: "networkidle", timeout: 120000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 120000 });
await page.waitForTimeout(800);

const shots = [
  ["dave-diver", "qa/steam-dave.png"],
  ["cyberpunk-2077", "qa/steam-cyberpunk.png"],
];

for (const [id, path] of shots) {
  await page.evaluate(() => {
    const close = document.querySelector("#focus-close");
    if (close && document.querySelector("#focus")?.classList.contains("show")) close.click();
  });
  await page.waitForTimeout(700);
  await page.evaluate((coverId) => window.__openCoverById(coverId), id);
  await page.waitForSelector("#focus.show", { timeout: 8000 });
  await page.waitForTimeout(1100);
  const info = await page.evaluate(() => {
    const card = document.querySelector(".focus-card");
    const cs = card ? getComputedStyle(card) : null;
    return {
      title: document.querySelector("#focus-title")?.textContent,
      tags: [...document.querySelectorAll("#focus-tags span")].map((n) => n.textContent),
      tagsHidden: document.querySelector("#focus-tags")?.hidden ?? null,
      review: document.querySelector("#focus-review")?.textContent,
      year: document.querySelector("#focus-year")?.textContent,
      vibeTag: !!document.querySelector("#focus-vibe-tag"),
      dataVibe: document.querySelector("#focus")?.getAttribute("data-vibe") ?? null,
      panelW: card ? Math.round(card.getBoundingClientRect().width) : null,
      panelH: card ? Math.round(card.getBoundingClientRect().height) : null,
      blur: cs?.backdropFilter || "",
    };
  });
  console.log(id, JSON.stringify(info));
  await page.screenshot({ path, type: "png" });
}

await browser.close();
console.log("SHOT_OK");
