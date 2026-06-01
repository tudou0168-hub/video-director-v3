const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Verify the fix
  const verifyFix = await page.evaluate(() => {
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

    const audioAttrs = Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]));
    const rootAttrs = root ? Object.fromEntries(Array.from(root.attributes).map(a => [a.name, a.value])) : null;
    const compDuration = iframeWin.__compositions?.['audio-driven-preview']?.duration;

    return {
      audioAttrs,
      rootAttrs,
      compDuration,
      playerDuration: player.getDuration ? player.getDuration() : null,
      audioDuration: audio.duration
    };
  });
  console.log('FIX VERIFICATION (before play):', JSON.stringify(verifyFix, null, 2));

  // Now play and check
  const playTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioVolume: audio.volume,
          audioCurrentTime: audio.currentTime,
          audioPaused: audio.paused,
          audioDuration: audio.duration,
          playerIsPlaying: player.isPlaying()
        });
      }, 5000);
    });
  });
  console.log('PLAY TEST (5s after play):', JSON.stringify(playTest, null, 2));

  await browser.close();
  console.log(playTest.audioMuted === false && playTest.audioCurrentTime > 0 ? 'PASS: audio unmuted and playing' : 'FAIL');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });