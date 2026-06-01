const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';
  await page.goto(studioUrl, { waitUntil: 'load', timeout: 30000 });

  // Wait briefly for iframe
  try {
    await page.waitForSelector('iframe', { state: 'attached', timeout: 3000 });
    console.log('iframe: found');
  } catch {
    console.log('iframe: NOT found within 3s');
    await browser.close();
    process.exit(1);
  }

  // IMMEDIATELY get iframe info before any React re-render
  const result = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return {
      count: iframes.length,
      srcs: iframes.map(f => ({ src: f.src.substring(0, 120) }))
    };
  });
  console.log('Iframe count (immediate):', result.count);
  console.log('Sources:', JSON.stringify(result.srcs, null, 2));

  await browser.close();
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });