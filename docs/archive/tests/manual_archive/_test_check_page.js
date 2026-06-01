const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Load page
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');

  // Wait for iframe to be present
  await page.waitForSelector('iframe', { timeout: 10000 });
  await page.waitForTimeout(3000);

  // Check what's in the page
  const pageInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return {
      hasIframe: !!iframe,
      iframeCount: iframes.length,
      iframeSrc: iframe?.src,
      iframeSrcLength: iframe?.src?.length
    };
  });
  console.log('PAGE INFO:', JSON.stringify(pageInfo, null, 2));

  // Check iframe content
  const iframeCheck = await page.evaluate(() => {
    try {
      const iframe = document.querySelector('iframe');
      const iframeDoc = iframe.contentDocument;
      const audio = iframeDoc?.querySelector('audio#voiceover');
      const root = iframeDoc?.getElementById('root');
      return {
        hasIframeDoc: !!iframeDoc,
        hasAudio: !!audio,
        hasRoot: !!root,
        audioAttrs: audio ? Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])) : null
      };
    } catch(e) {
      return { error: e.message };
    }
  });
  console.log('IFRAME CHECK:', JSON.stringify(iframeCheck, null, 2));

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });