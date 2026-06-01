const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Test: open mp3 directly in browser and try to play it
  const url = 'http://localhost:3002/api/projects/hyperframes_timeline/preview/assets/voiceover.mp3';
  await page.goto(url, { timeout: 10000 });

  // Wait for media to load
  await page.waitForTimeout(2000);

  // Try to play via JS
  const playResult = await page.evaluate(() => {
    // Find any audio element on the page
    const audio = document.querySelector('audio');
    if (!audio) {
      // No audio element, try creating one
      const a = document.createElement('audio');
      a.src = location.href;
      document.body.appendChild(a);
      a.volume = 1;
      a.muted = false;
      const p = a.play();
      return {
        created: true,
        hasAudioElement: false,
        playStarted: p !== undefined,
        audioState: {
          muted: a.muted,
          volume: a.volume,
          paused: a.paused,
          readyState: a.readyState,
          currentSrc: a.currentSrc
        }
      };
    }
    audio.volume = 1;
    audio.muted = false;
    const p = audio.play();
    return {
      hasAudioElement: true,
      playStarted: p !== undefined,
      audioState: {
        muted: audio.muted,
        volume: audio.volume,
        paused: audio.paused,
        readyState: audio.readyState
      }
    };
  });

  console.log('DIRECT MP3 PLAY RESULT:', JSON.stringify(playResult, null, 2));

  // Also check console errors
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('CONSOLE ERROR:', msg.text());
  });

  await page.waitForTimeout(2000);

  const finalState = await page.evaluate(() => {
    const audio = document.querySelector('audio');
    if (!audio) return { noAudio: true };
    return {
      muted: audio.muted,
      volume: audio.volume,
      paused: audio.paused,
      currentTime: audio.currentTime,
      readyState: audio.readyState
    };
  });
  console.log('FINAL STATE:', JSON.stringify(finalState, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });