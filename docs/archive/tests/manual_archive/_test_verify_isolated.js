const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Exact replication of TEST2 from _test_single_attrs.js
  // which PASSED: data-start ONLY
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

    // Clear ALL data-* first
    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

    // Set ONLY data-start (exactly like TEST2)
    audio.setAttribute('data-start', '0');
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
          attrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])),
          rootDataDuration: root?.getAttribute('data-duration')
        });
      }, 5000);
    });
  });
  console.log('ISOLATED TEST (data-start ONLY + root 71.78):', JSON.stringify(test, null, 2));
  console.log(test.audioMuted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });