const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Try: Intercept the audio element's muted property setter
  // We want to find any code that sets audio.muted and prevent it
  const interceptMutedSetter = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Track all attempts to set muted
    const setAttempts = [];

    // Override Object.defineProperty for 'muted' on audio
    let muteCount = 0;
    const originalMutedDescriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted');

    try {
      Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
        ...originalMutedDescriptor,
        set(value) {
          muteCount++;
          setAttempts.push({ count: muteCount, value, time: performance.now() });
          // Still set it but we can observe
          return originalMutedDescriptor.set.call(this, value);
        },
        get() {
          return originalMutedDescriptor.get.call(this);
        }
      });
    } catch(e) {
      return { error: 'Cannot override muted property: ' + e.message };
    }

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    iframeWin.__player.play();

    // Wait a bit
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          setAttempts,
          muteCount,
          finalMuted: audio.muted
        });
      }, 2000);
    });
  });
  console.log('INTERCEPT MUTED SETTER:', JSON.stringify(interceptMutedSetter, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });