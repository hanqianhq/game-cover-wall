import { chromium } from "playwright";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle", timeout: 60000 });
await page.waitForTimeout(3000);
const sample = await page.evaluate(() => {
  const c = document.querySelector("canvas");
  const ctx = document.createElement("canvas");
  ctx.width = c.width; ctx.height = c.height;
  const g = ctx.getContext("2d");
  g.drawImage(c, 0, 0);
  const pts = [[0.5,0.5],[0.2,0.3],[0.8,0.3],[0.2,0.7],[0.8,0.7],[0.5,0.2],[0.1,0.1],[0.9,0.1]];
  return pts.map(([u,v]) => {
    const x = Math.floor(u * c.width), y = Math.floor(v * c.height);
    const d = g.getImageData(x, y, 1, 1).data;
    return { u, v, rgb: [d[0],d[1],d[2]] };
  });
});
console.log(JSON.stringify(sample, null, 2));
await browser.close();
