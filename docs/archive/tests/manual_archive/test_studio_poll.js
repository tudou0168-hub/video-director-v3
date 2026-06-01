const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';
  await page.goto(studioUrl, { waitUntil: 'load', timeout: 30000 });

  // Poll every 500ms for 15 seconds to catch the iframe when it exists
  let iframeFound = false;
  for (let i = 0; i < 30; i++) {
    const result = await page.evaluate(() => {
      const iframes = Array.from(document.querySelectorAll('iframe'));
      return {
        count: iframes.length,
        srcs: iframes.map(f => f.src.substring(0, 100)),
        bodyChildCount: document.body.childElementCount,
        url: window.location.href
      };
    });

    if (result.count > 0) {
      console.log(`t=${i * 500}ms: iframe FOUND, count=${result.count}`);
      console.log('  srcs:', result.srcs);
      iframeFound = true;
      break;
    }

    if (i % 4 === 0) {
      console.log(`t=${i * 500}ms: no iframe yet, body children=${result.bodyChildCount}, url=${result.url.substring(0, 60)}`);
    }

    await page.waitForTimeout(500);
  }

  if (!iframeFound) {
    console.log('No iframe found in 15 seconds');
  }

  await browser.close();
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });