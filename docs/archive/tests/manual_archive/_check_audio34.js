const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Watch for audio element replacement - using working pattern
  const watchAudioReplacement = await page.evaluate(() => {
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

    const originalAudioRef = audio;

    const mutingLog = [];
    let lastMuted = audio.muted;
    let lastAudioPtr = audio;

    // Poll to detect replacement
    const poll = setInterval(() => {
      const currentAudio = iframeDoc.querySelector('audio#voiceover');
      if (currentAudio !== lastAudioPtr) {
        mutingLog.push({
          event: 'audio_element_replaced',
          oldPtr: lastAudioPtr === originalAudioRef,
          newPtrIsOriginal: currentAudio === originalAudioRef,
          muted: currentAudio.muted,
          time: performance.now()
        });
        lastAudioPtr = currentAudio;
      }
      if (currentAudio.muted !== lastMuted) {
        mutingLog.push({
          event: 'muted_changed',
          from: lastMuted,
          to: currentAudio.muted,
          sameElement: currentAudio === lastAudioPtr,
          time: performance.now()
        });
        lastMuted = currentAudio.muted;
      }
    }, 100);

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Wait
    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        clearInterval(poll);
        resolve({
          mutingLog,
          finalMuted: iframeDoc.querySelector('audio#voiceover')?.muted
        });
      }, 3000);
    });
  });
  console.log('AUDIO REPLACEMENT WATCH:', JSON.stringify(watchAudioReplacement, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });