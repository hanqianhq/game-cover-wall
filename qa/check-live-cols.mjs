import { chromium } from "playwright";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto("http://127.0.0.1:5188/?t=" + Date.now(), { waitUntil: "networkidle", timeout: 90000 });
await page.waitForFunction(() => window.__coverReady === true, null, { timeout: 60000 });
const info = await page.evaluate(() => {
  // count meshes roughly via canvas ok; pull constants from a probe if we expose them
  return {
    body: document.body.innerText.slice(0,80),
    focusVibe: !!document.querySelector('#focus-vibe-tag'),
  };
});
// fetch main.ts text from page context
const mainTxt = await page.evaluate(async () => {
  const r = await fetch('/src/main.ts');
  return await r.text();
});
console.log('live COLS14', /const COLS = 14/.test(mainTxt));
console.log('live HALF frac', /\(COLS - 1\) \/ 2/.test(mainTxt));
console.log('live FOV46', /PerspectiveCamera\(46/.test(mainTxt));
console.log('info', info);
await browser.close();
