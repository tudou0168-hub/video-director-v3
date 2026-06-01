const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check audio playback state
  const audioPlaybackState = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || (iframe.contentWindow && iframe.contentWindow.document);
    if (!iframeDoc) return { error: 'no iframe doc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    return {
      readyState: audio.readyState,
      networkState: audio.networkState,
      duration: audio.duration,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume,
      src: audio.currentSrc
    };
  });
  console.log('AUDIO PLAYBACK STATE:', JSON.stringify(audioPlaybackState, null, 2));

  // Check if audio is connected to Web Audio API - look for gain nodes
  const webAudioNodes = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Check if audio element has any web audio connections
    // The audio element itself won't tell us, but we can look at the context
    const ctx = iframeWin.AudioContext || iframeWin.webkitAudioContext;

    // Get the audio context's current time
    if (ctx) {
      return {
        ctxState: ctx.state,
        ctxSampleRate: ctx.sampleRate,
        ctxCurrentTime: ctx.currentTime,
        audioElementMuted: audio.muted,
        audioElementVolume: audio.volume
      };
    }
    return { ctx: null };
  });
  console.log('WEB AUDIO NODES:', JSON.stringify(webAudioNodes, null, 2));

  // KEY TEST: directly call audio.play() WITHOUT going through __player
  const directPlayTest = await page.evaluate(async () => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Reset state
    audio.pause();
    audio.muted = false;
    audio.volume = 1;
    audio.currentTime = 0;

    // Try direct play
    try {
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        await Promise.race([playPromise, new Promise(r => setTimeout(r, 1000))]);
      }
    } catch(e) {
      return { playError: e.message };
    }

    return {
      afterDirectPlay: {
        paused: audio.paused,
        currentTime: audio.currentTime,
        muted: audio.muted,
        volume: audio.volume
      }
    };
  });
  console.log('DIRECT PLAY TEST:', JSON.stringify(directPlayTest, null, 2));

  await page.waitForTimeout(1000);

  const afterDirectPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      paused: audio.paused,
      currentTime: audio.currentTime,
      muted: audio.muted,
      volume: audio.volume
    };
  });
  console.log('AFTER DIRECT PLAY:', JSON.stringify(afterDirectPlay, null, 2));

  // Test: with audio playing via direct play, check if __player controls affect it
  // First unmute the button
  const unmuteBtn = await page.$('button[aria-label="Unmute audio"]');
  if (unmuteBtn) {
    await unmuteBtn.click();
    await page.waitForTimeout(500);
  }

  const afterUnmuteBtnClick = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      audioMuted: audio.muted,
      audioVolume: audio.volume,
      currentTime: audio.currentTime
    };
  });
  console.log('AFTER UNMUTE BTN CLICK:', JSON.stringify(afterUnmuteBtnClick, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });