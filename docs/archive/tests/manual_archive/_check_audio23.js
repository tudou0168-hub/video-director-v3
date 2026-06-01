const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: patch player.play to NOT mute, and also intercept schedulePlayback
  const deepPatchTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    // Find pe object by checking player.play closure references
    // pe is used as: pe.startGeneration(), pe.decodeAudioElement(), pe.schedulePlayback()
    // These are called inside player.play

    // We need to find pe - it's a variable in the closure of player.play
    // Look for it in iframeWin scope

    let pe = null;
    for (const key of Object.keys(iframeWin)) {
      const val = iframeWin[key];
      if (val && typeof val === 'object' && typeof val.schedulePlayback === 'function') {
        pe = val;
        break;
      }
    }

    const playerOriginalPlay = player.play.bind(player);

    // Patch player.play to NOT mute audio
    player.play = function() {
      const result = playerOriginalPlay();
      // Directly set audio muted/volume after call
      audio.muted = false;
      audio.volume = 1;
      return result;
    };

    // If we find pe, also patch schedulePlayback
    if (pe) {
      const origSchedule = pe.schedulePlayback.bind(pe);
      pe.schedulePlayback = function(audioEl, buffer, startTime, playbackStart, now, volume, bridgeVol, playbackRate) {
        // Force volume to 1
        return origSchedule(audioEl, buffer, startTime, playbackStart, now, 1, 1, playbackRate);
      };
    }

    // Now call play
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    player.play();

    return {
      peFound: !!pe,
      peScheduleExists: pe ? typeof pe.schedulePlayback : null
    };
  });
  console.log('DEEP PATCH TEST:', JSON.stringify(deepPatchTest, null, 2));

  await page.waitForTimeout(1000);

  const afterDeepPatch = await page.evaluate(() => {
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
  console.log('AFTER DEEP PATCH:', JSON.stringify(afterDeepPatch, null, 2));

  // Now check: what does pe.schedulePlayback actually do with volume?
  const schedulePlaybackVolume = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    let pe = null;
    for (const key of Object.keys(iframeWin)) {
      const val = iframeWin[key];
      if (val && typeof val === 'object' && typeof val.schedulePlayback === 'function') {
        pe = val;
        break;
      }
    }

    if (!pe) return { peFound: false };

    // Get schedulePlayback source
    const src = pe.schedulePlayback.toString();
    // Look for volume handling
    const volLines = src.split('\n').filter(l => l.includes('volume') || l.includes('muted') || l.includes('gain'));
    return {
      peFound: true,
      volLines: volLines.slice(0, 10)
    };
  });
  console.log('SCHEDULE PLAYBACK VOLUME:', JSON.stringify(schedulePlaybackVolume, null, 2));

  // Most important test: does the audio actually PLAY (currentTime advancing) with muted=true?
  // And if we override muted to false, does it become audible?
  const finalTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Set state manually
    audio.pause();
    audio.currentTime = 0;
    audio.muted = true; // This is what player.play() does
    audio.volume = 1;

    // Now call player.play()
    iframeWin.__player.play();

    // Check currentTime - is audio actually playing (even though muted)?
    const t1 = audio.currentTime;

    return {
      whileMuted: {
        currentTime: t1,
        muted: audio.muted
      },
      ariaLabel: Array.from(document.querySelectorAll('button')).find(b =>
        b.getAttribute('aria-label')?.toLowerCase().includes('mute')
      )?.getAttribute('aria-label')
    };
  });
  console.log('FINAL TEST:', JSON.stringify(finalTest, null, 2));

  await page.waitForTimeout(1000);

  const afterFinalTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime
    };
  });
  console.log('AFTER FINAL TEST:', JSON.stringify(afterFinalTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });