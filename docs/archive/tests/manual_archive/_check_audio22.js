const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check if t.bridgeVolume is accessible in any way
  const tBridgeVolumeCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Check if there's a t object somewhere
    // t is the closure variable in player.play()
    // Let's see if we can find it

    // Try to access through player internals
    const player = iframeWin.__player;
    const playerStr = player.play.toString();

    // Look for "t.bridgeVolume" in the source
    const hasBridgeVolume = playerStr.includes('bridgeVolume');
    const bridgeVolumeRefs = playerStr.match(/t\.bridgeVolume/g) || [];

    // Look for "I.play" to understand what I is
    const iPlayRef = playerStr.match(/I\.play\(\)/);

    // Look for what sets muted
    const setMutedRefs = playerStr.match(/muted[^=]*=/g) || [];

    return {
      hasBridgeVolume,
      bridgeVolumeRefs,
      iPlayRef: iPlayRef ? iPlayRef[0] : null,
      setMutedRefs,
      playerSourceLength: playerStr.length
    };
  });
  console.log('T BRIDGE VOLUME CHECK:', JSON.stringify(tBridgeVolumeCheck, null, 2));

  // Check if pe (playback engine) has a method to set bridge volume
  const peBridgeVolumeCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Look for pe in various places
    const player = iframeWin.__player;

    // Try to find pe by checking what player.play() closure references
    // We know from source: pe.startGeneration(), pe.decodeAudioElement(), pe.schedulePlayback()
    // pe should be in iframeWin scope

    const peKeys = Object.keys(iframeWin).filter(k =>
      k.startsWith('pe') || k.includes('PE') || k.includes('Playback')
    );

    // Check if pe is accessible via window
    let peObj = null;
    for (const k of Object.keys(iframeWin)) {
      if (typeof iframeWin[k] === 'object' && iframeWin[k] !== null) {
        if (iframeWin[k].schedulePlayback) {
          peObj = iframeWin[k];
          break;
        }
      }
    }

    if (peObj) {
      return {
        peFound: true,
        peKeys: Object.keys(peObj).slice(0, 20),
        hasSchedulePlayback: typeof peObj.schedulePlayback === 'function'
      };
    }
    return { peFound: false, peKeys };
  });
  console.log('PE BRIDGE VOLUME CHECK:', JSON.stringify(peBridgeVolumeCheck, null, 2));

  // Try to patch player.play to not mute
  const patchTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    // Store original play
    const originalPlay = player.play.bind(player);

    // Override player.play
    player.play = function() {
      // Call original but intercept
      const result = originalPlay();
      // After player.play(), force unmute
      setTimeout(() => {
        audio.muted = false;
        audio.volume = 1;
      }, 50);
      return result;
    };

    // Now call play
    audio.pause();
    audio.currentTime = 0;
    player.play();

    return { patched: true };
  });
  console.log('PATCH TEST: player.play patched');

  await page.waitForTimeout(2000);

  const afterPatch = await page.evaluate(() => {
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
  console.log('AFTER PATCH:', JSON.stringify(afterPatch, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });