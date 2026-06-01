const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // KEY TEST: After __player.play() sets audio.muted=true, can we override it?
  const overrideTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Reset
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    iframeWin.__player.play();

    // Immediately after, check and try to override
    const afterPlayerPlay = {
      muted: audio.muted,
      volume: audio.volume,
      paused: audio.paused
    };

    // Now try to override muted
    audio.muted = false;

    return {
      afterPlayerPlay,
      afterOverride: {
        muted: audio.muted,
        volume: audio.volume
      }
    };
  });
  console.log('OVERRIDE TEST:', JSON.stringify(overrideTest, null, 2));

  await page.waitForTimeout(1000);

  const afterOverride = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('AFTER OVERRIDE (1s later):', JSON.stringify(afterOverride, null, 2));

  // Now test: what if we set audio.muted=false BEFORE calling player.play()?
  const beforePlayOverrideTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Reset
    audio.pause();
    audio.currentTime = 0;

    // Set muted=false BEFORE play
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    iframeWin.__player.play();

    return {
      afterPlayerPlay: {
        muted: audio.muted,
        volume: audio.volume,
        paused: audio.paused
      }
    };
  });
  console.log('BEFORE PLAY OVERRIDE TEST:', JSON.stringify(beforePlayOverrideTest, null, 2));

  await page.waitForTimeout(500);

  const afterBeforePlayOverride = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('AFTER BEFORE PLAY OVERRIDE:', JSON.stringify(afterBeforePlayOverride, null, 2));

  // Check if there is any periodic/interval that keeps resetting muted
  const intervalCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Check if there are any intervals that might be resetting mute
    const intervals = [];
    let win = iframeWin;
    while (win !== window) {
      // Check setInterval
      win.setInterval(() => {}, 1000); // just to verify setInterval works
      // Look for any interval IDs in the window
      const keys = Object.keys(win).filter(k => k.includes('Interval') || k.includes('timer'));
      if (keys.length) intervals.push(...keys);
      win = Object.getPrototypeOf(win);
    }

    return { intervals };
  });
  console.log('INTERVAL CHECK:', JSON.stringify(intervalCheck, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });