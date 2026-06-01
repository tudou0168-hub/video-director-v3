const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check the audio element's actual state - is it playing?
  const audioPlaybackState = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Check if audio is actually decoded and ready
    return {
      readyState: audio.readyState, // 0=nothing, 1=meta, 2=currentData, 3=dataAvailable, 4=canPlay
      networkState: audio.networkState, // 0=empty, 1=loading, 2=loaded, 3=error
      duration: audio.duration,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume,
      src: audio.currentSrc
    };
  });
  console.log('AUDIO PLAYBACK STATE:', JSON.stringify(audioPlaybackState, null, 2));

  // Check the actual audio buffer - has it been decoded?
  const audioDecodeCheck = await page.evaluate(async () => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Try to decode audio using AudioContext
    try {
      const ctx = new (iframeWin.AudioContext || iframeWin.webkitAudioContext)();
      const arrayBuffer = await fetch(audio.src).then(r => r.arrayBuffer());
      const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
      return {
        decoded: true,
        duration: audioBuffer.duration,
        sampleRate: audioBuffer.sampleRate,
        numberOfChannels: audioBuffer.numberOfChannels
      };
    } catch(e) {
      return { decoded: false, error: e.message };
    }
  });
  console.log('AUDIO DECODE CHECK:', JSON.stringify(audioDecodeCheck, null, 2));

  // Check if there's an audio context running and what's connected to it
  const activeAudioContext = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Check for any active AudioContext
    const contexts = [];
    // Check if audio element itself is connected to an AudioContext
    const audio = iframeWin.document.querySelector('audio#voiceover');

    // Check context state
    if (iframeWin.AudioContext || iframeWin.webkitAudioContext) {
      const ctx = new (iframeWin.AudioContext || iframeWin.webkitAudioContext)();
      return {
        contextExists: true,
        contextState: ctx.state,
        sampleRate: ctx.sampleRate
      };
    }
    return { contextExists: false };
  });
  console.log('ACTIVE AUDIO CONTEXT:', JSON.stringify(activeAudioContext, null, 2));

  // Check browser tab audio indicator
  const tabAudioCheck = await page.evaluate(async () => {
    // Check if we can detect if audio is actually playing
    // Use mediaSession API
    if (navigator.mediaSession) {
      const state = navigator.mediaSession.playbackState;
      return { mediaSession: true, playbackState: state };
    }
    return { mediaSession: false };
  });
  console.log('TAB AUDIO CHECK:', JSON.stringify(tabAudioCheck, null, 2));

  // Try: open a new page to the audio URL directly and see if it plays
  const page2 = await browser.newPage();
  await page2.goto('http://localhost:3002/project/hyperframes_timeline/assets/voiceover.mp3');
  await page2.waitForTimeout(1000);
  const directAudioState = await page2.evaluate(() => {
    const audio = document.querySelector('audio');
    if (audio) {
      return {
        hasAudio: true,
        src: audio.src,
        muted: audio.muted,
        volume: audio.volume
      };
    }
    return { hasAudio: false };
  });
  console.log('DIRECT AUDIO PAGE STATE:', JSON.stringify(directAudioState, null, 2));

  await page2.close();
  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });