const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Intercept the muted setter on HTMLMediaElement.prototype BEFORE player.play runs
  const interceptMutedSetter = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    const origDescriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted');
    if (!origDescriptor) return { error: 'no descriptor' };

    const callLog = [];
    const origSetter = origDescriptor.set;
    const origGetter = origDescriptor.get;

    try {
      Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
        get() {
          const v = origGetter.call(this);
          return v;
        },
        set(val) {
          callLog.push({
            val,
            time: performance.now(),
            stack: new Error().stack.split('\n').slice(0, 8)
          });
          return origSetter.call(this, val);
        },
        configurable: true
      });
    } catch(e) {
      return { error: 'Cannot define property: ' + e.message };
    }

    // Reset audio - but after we defined the property above
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Wait a bit
    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          callLog,
          audioMuted: audio.muted
        });
      }, 3000);
    });
  });
  console.log('INTERCEPT MUTED SETTER:', JSON.stringify(interceptMutedSetter, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });