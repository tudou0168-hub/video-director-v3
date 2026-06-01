const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';

  await page.goto(studioUrl, { waitUntil: 'load', timeout: 30000 });
  console.log('Loaded, URL:', page.url());

  // Wait 10 seconds to see if iframe appears later
  await page.waitForTimeout(10000);

  const result = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return {
      count: iframes.length,
      srcs: iframes.map(f => f.src.substring(0, 100)),
      bodyChildren: document.body.childElementCount
    };
  });
  console.log('After 10s wait:', result);

  await browser.close();
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });