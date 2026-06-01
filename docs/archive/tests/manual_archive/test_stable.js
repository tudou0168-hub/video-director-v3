const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // First load a blank page
  await page.goto('about:blank');
  await page.waitForTimeout(500);

  console.log('Loading target page...');
  const response = await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1', { waitUntil: 'domcontentloaded' });
  console.log('Response status:', response?.status());

  // Wait for iframe
  await page.waitForSelector('iframe', { timeout: 10000 });
  console.log('Iframe found');

  await page.waitForTimeout(3000);

  // Check page is stable
  const isStable = await page.evaluate(() => {
    return document.readyState;
  });
  console.log('Ready state:', isStable);

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });