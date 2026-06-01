const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // List all audio elements in iframe
  const allAudioElements = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };

    const allAudio = Array.from(iframeDoc.querySelectorAll('audio'));
    return allAudio.map(a => ({
      id: a.id,
      src: a.src ? a.src.substring(a.src.lastIndexOf('/') + 1) : null,
      muted: a.muted,
      volume: a.volume,
      paused: a.paused,
      currentTime: a.currentTime,
      duration: a.duration,
      readyState: a.readyState
    }));
  });
  console.log('ALL AUDIO ELEMENTS:', JSON.stringify(allAudioElements, null, 2));

  // Now let's see what objects in iframeWin have play/isPlaying
  const findI = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };

    // Find objects with play method
    const playObjects = [];
    for (const k of Object.keys(iframeWin)) {
      try {
        const v = iframeWin[k];
        if (v && typeof v === 'object' && typeof v.play === 'function') {
          playObjects.push({
            key: k,
            type: typeof v,
            hasIsPlaying: typeof v.isPlaying === 'function',
            hasNow: typeof v.now === 'function',
            hasSetDuration: typeof v.setDuration === 'function',
            isPlayingResult: typeof v.isPlaying === 'function' ? v.isPlaying() : 'N/A'
          });
        }
      } catch(e) {}
    }
    return playObjects;
  });
  console.log('FIND I (play objects):', JSON.stringify(findI, null, 2));

  // Most importantly: find the audio element that actually plays
  // by checking which audio has currentTime advancing
  const findPlayingAudio = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    // Reset all audio
    const allAudio = Array.from(iframeDoc.querySelectorAll('audio'));
    allAudio.forEach(a => {
      a.pause();
      a.currentTime = 0;
      a.muted = false;
    });

    // Call player.play()
    player.play();

    // Immediately check all audio states
    const states = allAudio.map(a => ({
      id: a.id,
      muted: a.muted,
      paused: a.paused,
      currentTime: a.currentTime
    }));

    return { states };
  });
  console.log('FIND PLAYING AUDIO:', JSON.stringify(findPlayingAudio, null, 2));

  await page.waitForTimeout(1000);

  const afterWait = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const allAudio = Array.from(iframeDoc.querySelectorAll('audio'));
    return allAudio.map(a => ({
      id: a.id,
      muted: a.muted,
      paused: a.paused,
      currentTime: a.currentTime
    }));
  });
  console.log('AFTER WAIT:', JSON.stringify(afterWait, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });