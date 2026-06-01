const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test with correct attributes using setAttribute (simulating what HTML has)
  const test = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    const root = iframeDoc.getElementById('root');

    // Verify current state (what HTML has now)
    const currentAttrs = Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]));

    // Reset audio state
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          currentAttrs,
          rootDataDuration: root?.getAttribute('data-duration'),
          compDuration: iframeWin.__compositions?.['audio-driven-preview']?.duration,
          muted: audio.muted,
          currentTime: audio.currentTime,
          volume: audio.volume
        });
      }, 5000);
    });
  });
  console.log('CURRENT STATE:', JSON.stringify(test, null, 2));
  console.log(test.muted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });