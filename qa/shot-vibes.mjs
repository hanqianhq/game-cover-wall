import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const OUT = path.resolve("qa");
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync("C:/Users/Administrator/agent-tools", { recursive: true });

const shots = [
  { id: "dave-diver", vibe: "cozy", file: "vibe-cozy-dave.png" },
  { id: "cyberpunk-2077", vibe: "neon", file: "vibe-neon-cyberpunk.png" },
  { id: "elden-ring", vibe: "souls", file: "vibe-souls-elden.png" },
  { id: "rdr2", vibe: "epic", file: "vibe-epic-rdr2.png" },
  { id: "helldivers-2", vibe: "arcade", file: "vibe-arcade-helldivers.png" },
];

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 60000 });
await page.waitForTimeout(800);

const results = [];
for (const s of shots) {
  // close if open
  await page.evaluate(() => {
    const el = document.querySelector("#focus");
    if (el && el.classList.contains("show")) {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    }
  });
  await page.waitForTimeout(700);

  await page.evaluate((id) => window.__openCoverById(id), s.id);
  await page.waitForSelector("#focus.show", { timeout: 10000 });
  await page.waitForTimeout(900);

  const info = await page.evaluate(() => {
    const focus = document.querySelector("#focus");
    const panel = document.querySelector(".focus-card");
    const r = panel?.getBoundingClientRect();
    return {
      vibe: focus?.getAttribute("data-vibe"),
      title: document.querySelector("#focus-title")?.textContent,
      tag: document.querySelector("#focus-vibe-tag")?.textContent,
      show: !!document.querySelector("#focus.show"),
      panel: r ? { left: Math.round(r.left), top: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) } : null,
    };
  });
  const ok = info.show && info.vibe === s.vibe && info.panel && info.panel.w > 100;
  console.log(s.id, JSON.stringify(info), "OK", ok);
  results.push({ ...s, ok, info });

  const dest = path.join(OUT, s.file);
  await page.screenshot({ path: dest, type: "png" });
  fs.copyFileSync(dest, path.join("C:/Users/Administrator/agent-tools", s.file));
}

await browser.close();
const allOk = results.every((r) => r.ok);
console.log("QA_PASS", allOk);
console.log(JSON.stringify(results.map((r) => ({ id: r.id, vibe: r.vibe, ok: r.ok, got: r.info?.vibe, title: r.info?.title })), null, 2));
process.exit(allOk ? 0 : 2);
