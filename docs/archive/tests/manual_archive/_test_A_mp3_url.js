const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  const urls = [
    'http://localhost:3002/api/projects/hyperframes_timeline/assets/voiceover.mp3',
    'http://localhost:3002/assets/voiceover.mp3',
    'http://localhost:3002/project/hyperframes_timeline/assets/voiceover.mp3'
  ];

  const results = [];

  for (const url of urls) {
    try {
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
      const status = response ? response.status() : 'no response';
      const contentLength = response ? response.headers()['content-length'] : null;
      results.push({
        url,
        status,
        contentLength,
        accessible: status === 200
      });
    } catch(e) {
      results.push({
        url,
        error: e.message,
        accessible: false
      });
    }
  }

  console.log('TEST A RESULTS:');
  results.forEach(r => {
    console.log(`  ${r.url}`);
    console.log(`    Status: ${r.status || r.error}`);
    console.log(`    Content-Length: ${r.contentLength || 'N/A'}`);
    console.log(`    Accessible: ${r.accessible}`);
  });

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });