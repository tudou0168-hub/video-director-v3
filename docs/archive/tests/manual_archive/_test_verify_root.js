const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check what root data-duration is on fresh load
  const rootCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const root = iframeDoc.getElementById('root');
    return {
      rootDataDuration: root?.getAttribute('data-duration'),
      rootAttrs: root ? Object.fromEntries(Array.from(root.attributes).map(a => [a.name, a.value])) : null
    };
  });
  console.log('ROOT ON FRESH LOAD:', JSON.stringify(rootCheck, null, 2));

  // Test: set root to71.78, no data-* on audio
  const test1 = await page.evaluate(() => {
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

    // Set root data-duration to 71.78
    if (root) root.setAttribute('data-duration', '71.78');

    // Remove all data-* from audio
    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

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
          rootDataDuration: root?.getAttribute('data-duration')
        });
      }, 5000);
    });
  });
  console.log('TEST (R7 style + root71.78):', test1.audioMuted === false ? 'PASS' : 'FAIL');

  // Test 2: add data-start to audio
  const test2 = await page.evaluate(() => {
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

    if (root) root.setAttribute('data-duration', '71.78');

    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });
    audio.setAttribute('data-start', '0');

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioCurrentTime: audio.currentTime
        });
      }, 5000);
    });
  });
  console.log('TEST (R7 + data-start only):', test2.audioMuted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });