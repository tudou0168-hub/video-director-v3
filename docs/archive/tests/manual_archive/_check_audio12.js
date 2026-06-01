const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Try to directly set audio.muted = false and then play
  const test1 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Check what happens if we set muted=false directly on audio
    audio.muted = false;
    audio.volume = 1;

    // Try playing
    const playPromise = audio.play();
    return {
      before: { muted: audio.muted, volume: audio.volume, paused: audio.paused },
      playStarted: playPromise !== undefined
    };
  });
  console.log('TEST 1 (set muted=false, play):', JSON.stringify(test1, null, 2));
  await page.waitForTimeout(1500);

  const state1 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      paused: audio.paused,
      currentTime: audio.currentTime
    };
  });
  console.log('STATE AFTER TEST 1:', JSON.stringify(state1, null, 2));

  // Now try: pause the audio, set muted=false, then play via __player.play()
  await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    audio.pause();
    audio.muted = false;
    audio.volume = 1;
  });

  const test2 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Call __player.play() and see what it does to audio.muted
    iframeWin.__player.play();

    // Immediately check audio state
    const audio = iframeWin.document.querySelector('audio#voiceover');
    return {
      audioMuted: audio.muted,
      audioPaused: audio.paused
    };
  });
  console.log('TEST 2 (after pause+unmute, call player.play):', JSON.stringify(test2, null, 2));

  await page.waitForTimeout(500);
  const state2 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('STATE AFTER TEST 2:', JSON.stringify(state2, null, 2));

  // KEY TEST: Check if player.play() calls audio.muted = true internally
  const muteTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const audio = iframeWin.document.querySelector('audio#voiceover');

    audio.pause();
    audio.muted = false;
    audio.volume = 1;

    // Override audio.play to see if it sets muted
    const originalPlay = audio.play;
    let playMutedTheAudio = null;

    // Inject a wrapper
    audio.play = function() {
      playMutedTheAudio = audio.muted;
      return originalPlay.call(this);
    };

    iframeWin.__player.play();

    return {
      mutedBeforePlay: audio.muted,
      mutedDuringPlayIntercept: playMutedTheAudio
    };
  });
  console.log('MUTE TEST:', JSON.stringify(muteTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });