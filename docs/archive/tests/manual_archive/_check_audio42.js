const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox']
  });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check initial mute state BEFORE any play
  const initialState = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    return {
      initialMuted: audio.muted,
      initialVolume: audio.volume,
      initialPaused: audio.paused,
      isPlaying: player.isPlaying(),
      playerKeys: Object.keys(player)
    };
  });
  console.log('INITIAL STATE:', JSON.stringify(initialState, null, 2));

  // Now reset and play, checking every 500ms
  const timedCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    const checks = [];
    for (let i = 0; i < 8; i++) {
      const t = i * 500;
      const state = {
        t,
        muted: audio.muted,
        volume: audio.volume,
        currentTime: audio.currentTime,
        paused: audio.paused
      };
      checks.push(state);
    }

    return new Promise(resolve => {
      checks.forEach((check, i) => {
        setTimeout(() => {
          if (i === checks.length - 1) resolve({ checks });
        }, check.t + 50);
      });
    });
  });
  console.log('TIMED CHECK:', JSON.stringify(timedCheck, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });