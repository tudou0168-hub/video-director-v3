const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Test the actual audio URL that the iframe uses
  const url = 'http://localhost:3002/api/projects/hyperframes_timeline/preview/assets/voiceover.mp3';
  const resp = await page.goto(url, { timeout: 10000 });
  console.log('URL:', url);
  console.log('Status:', resp.status());
  console.log('Content-Type:', resp.headers()['content-type']);
  console.log('Content-Length:', resp.headers()['content-length']);

  // Also test the server root for assets
  const resp2 = await page.goto('http://localhost:3002/api/projects/hyperframes_timeline/preview/', { timeout: 10000 });
  console.log('\nPreview root status:', resp2.status());

  // Also test without preview in path
  const resp3 = await page.goto('http://localhost:3002/api/projects/hyperframes_timeline/assets/voiceover.mp3', { timeout: 10000 });
  console.log('\n/api/projects/hyperframes_timeline/assets/voiceover.mp3');
  console.log('Status:', resp3.status());
  console.log('Content-Type:', resp3.headers()['content-type']);

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });