const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: only remove data-duration (keep data-start and data-track-index)
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

    // Ensure all are set first
    audio.setAttribute('data-duration', '72.0');
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-track-index', '0');

    // Only remove data-duration
    audio.removeAttribute('data-duration');

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
          attrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]))
        });
      }, 3000);
    });
  });
  console.log('TEST1 (remove only data-duration):', JSON.stringify(test1, null, 2));

  // Test: remove both data-duration AND data-track-index (keep data-start)
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

    audio.setAttribute('data-duration', '72.0');
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-track-index', '0');

    audio.removeAttribute('data-duration');
    audio.removeAttribute('data-track-index');

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
          attrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]))
        });
      }, 3000);
    });
  });
  console.log('TEST2 (remove data-duration+data-track-index):', JSON.stringify(test2, null, 2));

  // Test: the exact R7 pattern - audio with ONLY id, preload, src (no data-* at all)
  const testR7pattern = await page.evaluate(() => {
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

    // Remove ALL data-* from audio
    audio.removeAttribute('data-duration');
    audio.removeAttribute('data-start');
    audio.removeAttribute('data-track-index');

    // Also check if root has data-duration causing issues
    if (root) root.removeAttribute('data-duration');
    root?.removeAttribute('data-start');
    root?.removeAttribute('data-composition-id');

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
          rootAttrs: root ? Object.fromEntries(Array.from(root.attributes).map(a => [a.name, a.value])) : null
        });
      }, 3000);
    });
  });
  console.log('TEST R7 PATTERN (no data-* at all):', JSON.stringify(testR7pattern, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });