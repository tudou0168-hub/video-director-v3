const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Clean test: remove ALL data-* first, then set what we need
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

    // CRITICAL: Remove ALL data-* first (clean slate)
    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

    // Now set what we need
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-duration', '71.78');
    audio.setAttribute('data-track-index', '0');

    // Also ensure root is correct
    if (root) root.setAttribute('data-duration', '71.78');

    // Reset audio state
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioCurrentTime: audio.currentTime,
          attrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])),
          rootDataDuration: root?.getAttribute('data-duration')
        });
      }, 5000);
    });
  });
  console.log('CLEAN TEST (all three after clean slate):', JSON.stringify(test, null, 2));
  console.log(test.audioMuted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });