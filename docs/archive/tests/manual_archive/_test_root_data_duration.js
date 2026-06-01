const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: ONLY remove data-duration from root div (keep audio data-* intact)
  const testRootDuration = await page.evaluate(() => {
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

    // Remove ONLY data-duration from root (keep data-composition-id, data-width, data-height)
    if (root) root.removeAttribute('data-duration');

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
          audioDuration: audio.duration,
          rootAttrs: root ? Object.fromEntries(Array.from(root.attributes).map(a => [a.name, a.value])) : null,
          playerDuration: player.getDuration ? player.getDuration() : null,
          note: 'Removed only data-duration from root, kept audio data-* intact'
        });
      }, 3000);
    });
  });
  console.log('TEST ROOT DATA-DURATION REMOVED:', JSON.stringify(testRootDuration, null, 2));

  // Test: Change root data-duration from 72.0 to 71.78 (match audio file)
  const testMatchDuration = await page.evaluate(() => {
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

    // Change root data-duration to match actual audio duration
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
          rootDataDuration: root?.getAttribute('data-duration'),
          playerDuration: player.getDuration ? player.getDuration() : null
        });
      }, 3000);
    });
  });
  console.log('TEST ROOT DURATION=71.78:', JSON.stringify(testMatchDuration, null, 2));

  // Test: the FULL fix - remove data-duration from audio, change root data-duration to 71.78
  const testFullFix = await page.evaluate(() => {
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

    // Remove data-duration from audio (like R7)
    audio.removeAttribute('data-duration');
    // Change root data-duration to71.78
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
          audioDuration: audio.duration,
          rootDataDuration: root?.getAttribute('data-duration'),
          playerDuration: player.getDuration ? player.getDuration() : null,
          note: 'Removed audio data-duration, root data-duration=71.78'
        });
      }, 3000);
    });
  });
  console.log('TEST FULL FIX:', JSON.stringify(testFullFix, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });