const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: after __player.play(), immediately set audio.muted = false
  const fixTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const audio = iframeWin.document.querySelector('audio#voiceover');

    // Pause and reset
    audio.pause();
    audio.muted = false;
    audio.volume = 1;
    audio.currentTime = 0;

    // Call player.play() then immediately set muted=false
    iframeWin.__player.play();
    // Small delay to let player.play() run
    const t1 = audio.currentTime;

    // Now unmute
    audio.muted = false;
    const t2 = audio.currentTime;
    const muted2 = audio.muted;

    return { t1, t2, muted2, paused: audio.paused };
  });
  console.log('FIX TEST:', JSON.stringify(fixTest, null, 2));

  await page.waitForTimeout(2000);

  const afterFix = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('AFTER FIX:', JSON.stringify(afterFix, null, 2));

  // Now check if the issue is in the player source
  // Check if there's a player.play() implementation that does mute
  const playerPlaySource = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // Get the source of player.play
    try {
      const src = player.play.toString();
      return { length: src.length, firstLines: src.split('\n').slice(0, 5).join('\n') };
    } catch(e) {
      return { error: e.message };
    }
  });
  console.log('PLAYER PLAY SOURCE:', JSON.stringify(playerPlaySource, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });