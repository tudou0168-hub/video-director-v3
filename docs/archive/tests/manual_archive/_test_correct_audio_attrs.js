const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: audio with CORRECT data-start AND CORRECT data-duration=71.78 (match actual)
  const testCorrectAttrs = await page.evaluate(() => {
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

    // Set CORRECT attributes matching actual audio duration
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-duration', '71.78');
    audio.setAttribute('data-track-index', '0');
    // Also set data-volume to match actual
    audio.setAttribute('data-volume', '0.92');

    // Ensure root data-duration matches
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
          audioAttrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])),
          rootDataDuration: root?.getAttribute('data-duration')
        });
      }, 5000);
    });
  });
  console.log('TEST CORRECT DATA-ATTRS (data-duration=71.78):', JSON.stringify(testCorrectAttrs, null, 2));
  console.log(testCorrectAttrs.audioMuted === false ? 'PASS: muted=false' : 'FAIL: muted=' + testCorrectAttrs.audioMuted);

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });