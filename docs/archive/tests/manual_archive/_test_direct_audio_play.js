const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: Call audio.play() directly, NOT player.play()
  const directAudioPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call audio.play() directly - NOT player.play()
    const result = audio.play();

    // Wait a bit
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          playReturned: typeof result,
          audioMuted: audio.muted,
          audioVolume: audio.volume,
          audioPaused: audio.paused,
          audioCurrentTime: audio.currentTime,
          note: 'This bypasses Studio player and uses raw HTML audio API'
        });
      }, 3000);
    });
  });
  console.log('DIRECT AUDIO PLAY:', JSON.stringify(directAudioPlay, null, 2));

  // Compare with player.play()
  const page2 = await browser.newPage();
  await page2.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page2.waitForTimeout(3000);

  const studioPlayerPlay = await page2.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play() like Studio normally does
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioVolume: audio.volume,
          audioPaused: audio.paused,
          audioCurrentTime: audio.currentTime,
          playerIsPlaying: player.isPlaying(),
          note: 'This uses Studio player.play()'
        });
      }, 3000);
    });
  });
  console.log('STUDIO PLAYER PLAY:', JSON.stringify(studioPlayerPlay, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });