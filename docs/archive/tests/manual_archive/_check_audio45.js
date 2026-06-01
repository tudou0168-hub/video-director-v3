const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Override HTMLMediaElement.prototype.muted BEFORE page load
  await page.addInitScript(() => {
    const origDescriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted');
    if (!origDescriptor) return;

    const origGetter = origDescriptor.get;
    const origSetter = origDescriptor.set;

    // Block ALL muted=true sets (allow false)
    Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
      get() {
        return origGetter.call(this);
      },
      set(val) {
        if (val === true) {
          console.log('[MUTE BLOCKER] Blocking muted=true');
          return; // Block it
        }
        return origSetter.call(this, val);
      },
      configurable: true
    });
  });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test
  const muteBlockTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          paused: audio.paused
        });
      }, 3000);
    });
  });
  console.log('MUTE BLOCK TEST:', JSON.stringify(muteBlockTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });