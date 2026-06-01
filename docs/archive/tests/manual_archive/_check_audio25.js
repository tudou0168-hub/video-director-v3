const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: watch for setAttribute calls on the audio element
  const watchSetAttribute = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    const setAttributeCalls = [];
    const originalSetAttribute = audio.setAttribute.bind(audio);
    audio.setAttribute = function(name, value) {
      if (name === 'muted' || name === 'volume') {
        setAttributeCalls.push({ name, value, time: performance.now() });
      }
      return originalSetAttribute(name, value);
    };

    // Also watch removeAttribute
    const removeAttributeCalls = [];
    const originalRemoveAttribute = audio.removeAttribute.bind(audio);
    audio.removeAttribute = function(name) {
      if (name === 'muted' || name === 'volume') {
        removeAttributeCalls.push({ name, time: performance.now() });
      }
      return originalRemoveAttribute(name);
    };

    // Also watch volume property
    let volumeSetCount = 0;
    let mutedSetCount = 0;

    // Try intercepting via prototype
    const origDescriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'volume');
    if (origDescriptor && origDescriptor.set) {
      Object.defineProperty(HTMLMediaElement.prototype, 'volume', {
        ...origDescriptor,
        set(value) {
          volumeSetCount++;
          console.log('VOLUME SET TO:', value, 'count:', volumeSetCount);
          return origDescriptor.set.call(this, value);
        }
      });
    }

    const origMutedDescriptor = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted');
    if (origMutedDescriptor && origMutedDescriptor.set) {
      Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
        ...origMutedDescriptor,
        set(value) {
          mutedSetCount++;
          console.log('MUTED SET TO:', value, 'count:', mutedSetCount);
          return origMutedDescriptor.set.call(this, value);
        }
      });
    }

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    iframeWin.__player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          setAttributeCalls,
          removeAttributeCalls,
          volumeSetCount,
          mutedSetCount,
          finalMuted: audio.muted,
          finalVolume: audio.volume
        });
      }, 2000);
    });
  });
  console.log('WATCH SET ATTRIBUTE:', JSON.stringify(watchSetAttribute, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });