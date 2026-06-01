const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Load the Studio URL which should contain an iframe to the composition
  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';
  console.log(`Loading: ${studioUrl}`);

  await page.goto(studioUrl, { waitUntil: 'load', timeout: 30000 });
  console.log('URL after load:', page.url());

  // Wait for Studio to fully initialize
  await page.waitForTimeout(5000);

  // Check what's in the DOM now
  const bodySnapshot = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    const divs = Array.from(document.querySelectorAll('div')).slice(0, 5).map(d => d.id || d.className);
    return {
      iframeCount: iframes.length,
      iframeSrcs: iframes.map(f => f.src.substring(0, 80)),
      someDivs: divs,
      bodyChildCount: document.body.childElementCount
    };
  });
  console.log('DOM snapshot:', JSON.stringify(bodySnapshot, null, 2));

  // Try waiting for iframe specifically
  try {
    await page.waitForSelector('iframe[src*="hyperframes"]', { timeout: 5000 });
    console.log('Found iframe with hyperframes in src');
  } catch {
    console.log('No iframe with hyperframes in src found');
  }

  await browser.close();
  process.exit(0);
})().catch(e => { console.error('FATAL:', e.message, e.stack); process.exit(1); });