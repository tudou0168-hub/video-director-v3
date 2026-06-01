const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: intercept audio.muted setter
  const muteSetterIntercept = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Store original muted value
    let lastMuted = audio.muted;
    let muteChangeCount = 0;
    let muteChanges = [];

    // Override the muted property descriptor
    const handler = {
      get(target, prop) {
        return target[prop];
      },
      set(target, prop, value) {
        if (prop === 'muted' && value !== target[prop]) {
          muteChangeCount++;
          muteChanges.push({ time: Date.now(), value, stack: new Error().stack });
          console.log('MUTED CHANGED TO:', value, 'count:', muteChangeCount);
        }
        target[prop] = value;
        return true;
      }
    };

    const proxiedAudio = new Proxy(audio, handler);

    // Also check if there's an interval or raf resetting it
    let intervalCount = 0;
    const intervalId = setInterval(() => {
      intervalCount++;
      if (audio.muted !== lastMuted) {
        console.log('INTERVAL:', intervalCount, 'audio.muted changed to', audio.muted, 'from', lastMuted);
        lastMuted = audio.muted;
      }
    }, 100);

    // Call player.play()
    iframeWin.__player.play();

    // Wait and observe
    return new Promise(resolve => {
      setTimeout(() => {
        clearInterval(intervalId);
        resolve({
          muteChangeCount,
          muteChanges: muteChanges.slice(0, 5),
          finalMuted: audio.muted,
          intervalCount
        });
      }, 3000);
    });
  });
  console.log('MUTE SETTER INTERCEPT:', JSON.stringify(muteSetterIntercept, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });