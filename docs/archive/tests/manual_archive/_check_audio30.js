const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Intercept RAF and catch the one that sets muted
  const catchMutingRAF = await page.evaluate(() => {
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

    const origRAF = iframeWin.requestAnimationFrame.bind(iframeWin);
    const pendingCallbacks = new Map();
    let rafId = 0;
    let muteCaughtBy = null;

    iframeWin.requestAnimationFrame = function(cb) {
      const myId = ++rafId;
      const wrappedCb = function(timestamp) {
        const result = cb(timestamp);
        if (audio.muted === true && muteCaughtBy === null) {
          muteCaughtBy = myId;
        }
        return result;
      };
      pendingCallbacks.set(myId, wrappedCb);
      return origRAF(wrappedCb);
    };

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Wait for mute to happen
    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          muteCaughtBy,
          callbackCount: pendingCallbacks.size
        });
      }, 4000);
    });
  });
  console.log('CATCH MUTING RAF:', JSON.stringify(catchMutingRAF, null, 2));

  // List all functions in iframe window
  const windowFunctions = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };

    const functions = [];
    for (const k of Object.keys(iframeWin)) {
      if (typeof iframeWin[k] === 'function') {
        functions.push(k);
      }
    }
    return functions.slice(0, 50);
  });
  console.log('WINDOW FUNCTIONS:', windowFunctions);

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });