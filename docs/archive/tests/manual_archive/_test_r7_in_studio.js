const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // R7 project name - check what projects are available
  const projects = await page.evaluate(() => {
    return Object.keys(window.__compositions || {}).concat(
      Object.keys(window.__timelines || {})
    );
  });
  console.log('Available:', projects);

  // Check if we can navigate to R7 URL
  await page.goto('http://localhost:3002/#project/g2-r7-audio-visual-sync?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  const r7Check = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;
    return {
      hasIframe: !!iframe,
      hasAudio: !!audio,
      audioSrc: audio?.src,
      audioMuted: audio?.muted,
      hasPlayer: !!player
    };
  });
  console.log('R7 CHECK:', JSON.stringify(r7Check, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });