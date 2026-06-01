const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check if audio playback works directly via JS in iframe
  const directPlayTest = await page.evaluate(async () => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    // Try calling audio.play() directly
    let playResult = null;
    let playError = null;
    try {
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playResult = 'play returned promise';
        await Promise.race([playPromise, new Promise(r => setTimeout(r, 500))]);
      }
    } catch(e) {
      playError = e.message;
    }

    return {
      beforePlay: {
        paused: audio.paused,
        currentTime: audio.currentTime,
        muted: audio.muted
      },
      playResult,
      playError,
      afterDirectPlay: {
        paused: audio.paused,
        currentTime: audio.currentTime
      }
    };
  });
  console.log('DIRECT PLAY TEST:', JSON.stringify(directPlayTest, null, 2));

  // Check what timeline controls look like
  const timelineInfo = await page.evaluate(() => {
    // Check if there's a preview iframe
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

    // Look for window.__timelines or __compositions
    const hasTimelines = '__timelines' in iframe.contentWindow;
    const hasCompositions = '__compositions' in iframe.contentWindow;

    // Check for any global state
    const globals = Object.keys(iframe.contentWindow).filter(k => k.startsWith('__') || k.includes('audio') || k.includes('Audio'));

    return {
      hasTimelines,
      hasCompositions,
      timelineKeys: globals
    };
  });
  console.log('TIMELINE INFO:', JSON.stringify(timelineInfo, null, 2));

  // Now test: click Play, then after 2s check audio again
  const playBtn = await page.$('button[aria-label="Play"]');
  if (playBtn) {
    await playBtn.click();
    await page.waitForTimeout(2000);

    const afterPlay2s = await page.evaluate(() => {
      const iframe = document.querySelector('iframe');
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const audio = iframeDoc.querySelector('audio#voiceover');
      if (!audio) return { error: 'no audio' };
      return {
        paused: audio.paused,
        currentTime: audio.currentTime,
        muted: audio.muted,
        volume: audio.volume
      };
    });
    console.log('AFTER PLAY 2S:', JSON.stringify(afterPlay2s, null, 2));
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });