const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

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
    if (!player) return { error: 'no player' };

    // Check what data attributes the audio has
    const dataAttrs = {};
    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) {
        dataAttrs[a.name] = a.value;
      }
    });

    // Check what data attributes the root has
    const root = iframeDoc.getElementById('root');
    const rootDataAttrs = {};
    if (root) {
      Array.from(root.attributes).forEach(a => {
        if (a.name.startsWith('data-')) {
          rootDataAttrs[a.name] = a.value;
        }
      });
    }

    // Check __compositions
    const compositions = iframeWin.__compositions;
    const composition = compositions ? Object.values(compositions)[0] : null;

    // Check player.getDuration()
    const playerDuration = player.getDuration ? player.getDuration() : null;

    return {
      audioDataAttrs: dataAttrs,
      rootDataAttrs: rootDataAttrs,
      playerDuration,
      composition: composition ? {
        id: composition.id,
        duration: composition.duration,
        fps: composition.fps
      } : null,
      audioDuration: audio.duration,
      audioReadyState: audio.readyState
    };
  });
  console.log('DATA DURATION TEST:', JSON.stringify(test, null, 2));

  // Test: remove data attributes and play
  const removeTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Remove data-duration, data-track-index, data-start
    audio.removeAttribute('data-duration');
    audio.removeAttribute('data-track-index');
    audio.removeAttribute('data-start');

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioVolume: audio.volume,
          audioCurrentTime: audio.currentTime,
          note: 'After removing data-* from audio'
        });
      }, 3000);
    });
  });
  console.log('REMOVE DATA TEST:', JSON.stringify(removeTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });