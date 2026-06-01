const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: Change __compositions duration from 72.0 to 71.784
  const testCompositionDuration = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Change __compositions duration
    const comp = iframeWin.__compositions['audio-driven-preview'];
    const oldDuration = comp ? comp.duration : null;
    if (comp) comp.duration = 71.784;

    // Also update root data-duration
    const root = iframeDoc.getElementById('root');
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
          oldDuration,
          newCompositionDuration: iframeWin.__compositions['audio-driven-preview']?.duration,
          rootDataDuration: root?.getAttribute('data-duration'),
          playerDuration: player.getDuration ? player.getDuration() : null
        });
      }, 3000);
    });
  });
  console.log('TEST COMPOSITIONS DURATION FIX:', JSON.stringify(testCompositionDuration, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });