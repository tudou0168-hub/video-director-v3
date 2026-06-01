const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Isolated test: only remove data-track-index, keep data-duration and data-start
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

    // Restore all first, then remove only data-track-index
    audio.setAttribute('data-duration', '72.0');
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-track-index', '0');
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
  console.log('TEST A (remove only data-track-index):', JSON.stringify(testA, null, 2));

  // Test B: only remove data-start, keep data-duration and data-track-index
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

    audio.setAttribute('data-duration', '72.0');
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-track-index', '0');
    audio.removeAttribute('data-start');

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
  console.log('TEST B (remove only data-start):', JSON.stringify(testB, null, 2));

  // Test C: change data-duration from 72.0 to 71.784 (match actual audio duration)
  const testC = await page.evaluate(() => {
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

    audio.setAttribute('data-duration', '72.0');
    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-track-index', '0');

    // Change to match actual audio duration
    audio.setAttribute('data-duration', '71.784');
    if (root) root.setAttribute('data-duration', '71.784');

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
          audioDataDuration: audio.getAttribute('data-duration'),
          rootDataDuration: root?.getAttribute('data-duration')
        });
      }, 3000);
    });
  });
  console.log('TEST C (data-duration=71.784):', JSON.stringify(testC, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });