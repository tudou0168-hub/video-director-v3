const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Check what the200 URL actually returns
  const resp = await page.goto('http://localhost:3002/project/hyperframes_timeline/assets/voiceover.mp3', { timeout: 10000 });
  console.log('Status:', resp.status());
  console.log('Content-Type:', resp.headers()['content-type']);
  console.log('Content-Length:', resp.headers()['content-length']);

  const body = await page.evaluate(() => document.body.innerText);
  console.log('Body preview:', body.slice(0, 200));

  // Now check the iframe URL approach
  const page2 = await browser.newPage();
  await page2.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page2.waitForTimeout(3000);

  const audioInfo = await page2.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    return {
      src: audio.src,
      currentSrc: audio.currentSrc,
      srcLoaded: audio.readyState,
      networkState: audio.networkState
    };
  });
  console.log('\nAUDIO IN IFRAME:', JSON.stringify(audioInfo, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });