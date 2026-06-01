const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Capture console messages
  const consoleLogs = [];
  page.on('console', msg => {
    consoleLogs.push({ type: msg.type(), text: msg.text().substring(0, 200) });
  });

  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';
  await page.goto(studioUrl, { waitUntil: 'load', timeout: 30000 });
  console.log('Loaded');

  await page.waitForTimeout(5000);

  // Get any console errors
  const errors = consoleLogs.filter(l => l.type === 'error');
  const warnings = consoleLogs.filter(l => l.type === 'warning');

  console.log(`Console errors: ${errors.length}`);
  errors.forEach(e => console.log('  ERROR:', e.text));
  console.log(`Console warnings: ${warnings.length}`);

  // Check DOM
  const result = await page.evaluate(() => {
    return {
      count: document.querySelectorAll('iframe').length,
      rootHTML: document.getElementById('root')?.innerHTML.substring(0, 300),
      title: document.title
    };
  });
  console.log('DOM:', JSON.stringify(result, null, 2));

  await browser.close();
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });