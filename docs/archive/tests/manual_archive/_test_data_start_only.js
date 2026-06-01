const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: audio with ONLY data-start="0" (no data-duration, no data-track-index)
  const testDataStartOnly = await page.evaluate(() => {
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

    // Set audio to have ONLY data-start="0" (like linter wants)
    audio.setAttribute('data-start', '0');
    audio.removeAttribute('data-duration');
    audio.removeAttribute('data-track-index');

    // Root has data-duration=71.78
    if (root) root.setAttribute('data-duration', '71.78');

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
      }, 4000);
    });
  });
  console.log('TEST DATA-START ONLY:', JSON.stringify(testDataStartOnly, null, 2));
  console.log(testDataStartOnly.audioMuted === false ? 'PASS: muted=false' : 'FAIL: muted=' + testDataStartOnly.audioMuted);

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });