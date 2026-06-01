const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test A: set root data-duration FIRST, then add all three data-* to audio
  const testA = await page.evaluate(() => {
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

    // Step 1: Set root data-duration FIRST (before any audio changes)
    if (root) root.setAttribute('data-duration', '71.78');

    // Step 2: Now add all three data-* to audio
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-duration', '71.78');
    audio.setAttribute('data-track-index', '0');

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
  console.log('TEST A (root first, then all audio data-*):', testA.audioMuted === false ? 'PASS' : 'FAIL');

  // Test B: same but remove data-track-index
  const testB = await page.evaluate(() => {
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
    audio.setAttribute('data-duration', '71.78');
    // NO data-track-index

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
  console.log('TEST B (root first, data-start + data-duration):', testB.audioMuted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });