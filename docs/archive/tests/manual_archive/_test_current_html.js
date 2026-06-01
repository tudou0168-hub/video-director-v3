const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Load the page ONCE - HTML already has correct attributes baked in
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check what the audio has on fresh load
  const check = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const root = iframeDoc.getElementById('root');
    const player = iframeWin.__player;

    return {
      audioAttrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])),
      rootDataDuration: root?.getAttribute('data-duration'),
      compDuration: iframeWin.__compositions?.['audio-driven-preview']?.duration,
      audioMutedOnLoad: audio.muted
    };
  });
  console.log('ON FRESH LOAD:', JSON.stringify(check, null, 2));

  // Now play without any modifications
  const playResult = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // DON'T reset or modify - just play
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          paused: audio.paused
        });
      }, 5000);
    });
  });
  console.log('PLAY (no modifications):', JSON.stringify(playResult, null, 2));
  console.log(playResult.muted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });