const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test the exact timing of when muted=true happens relative to player.play()
  const exactMuteTiming = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    const t0 = performance.now();
    const events = [];

    // Intercept the muted setter
    const origDesc = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted');
    if (origDesc && origDesc.set) {
      const origSetter = origDesc.set;
      const origGetter = origDesc.get;
      Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
        get() { return origGetter.call(this); },
        set(val) {
          events.push({
            type: 'muted_set',
            val,
            t: performance.now() - t0,
            stack: new Error().stack.split('\n').slice(0, 4)
          });
          return origSetter.call(this, val);
        },
        configurable: true
      });
    }

    // Reset again after interceptor
    audio.muted = false;
    audio.currentTime = 0;

    // Call player.play()
    player.play();

    // Poll until5 seconds
    const pollStart = performance.now();
    while (performance.now() - pollStart < 5000) {
      if (audio.muted !== events[events.length - 1]?.val) {
        events.push({
          type: 'muted_poll',
          val: audio.muted,
          t: performance.now() - t0
        });
      }
    }

    return {
      events,
      finalMuted: audio.muted
    };
  });
  console.log('EXACT MUTE TIMING:', JSON.stringify(exactMuteTiming, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });