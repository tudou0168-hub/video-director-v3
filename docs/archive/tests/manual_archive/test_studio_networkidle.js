const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Disable JS for a moment to see the pure DOM
  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';

  // Use networkidle to wait for all network activity to stop
  await page.goto(studioUrl, { waitUntil: 'networkidle', timeout: 30000 });
  console.log('After networkidle, URL:', page.url());

  // Wait for iframe to appear
  await page.waitForSelector('iframe', { timeout: 10000 });
  console.log('iframe appeared');

  // Now grab the content IMMEDIATELY after
  const content = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return {
      count: iframes.length,
      srcs: iframes.map(f => f.src)
    };
  });
  console.log('Iframes:', content);

  await browser.close();
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });