const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Intercept ALL mute changes, including via events/timers
  const traceMute = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    const events = [];
    let frameRequestCallbacks = [];
    let intervals = [];
    let timeouts = [];

    // Intercept requestAnimationFrame to catch RAF-based loops
    const origRAF = iframeWin.requestAnimationFrame.bind(iframeWin);
    iframeWin.requestAnimationFrame = function(cb) {
      frameRequestCallbacks.push(cb);
      return origRAF(cb);
    };

    // Intercept setInterval
    const origSetInterval = iframeWin.setInterval.bind(iframeWin);
    iframeWin.setInterval = function(fn, delay, ...args) {
      intervals.push({ fn: fn.toString().slice(0, 100), delay });
      return origSetInterval(fn, delay, ...args);
    };

    // Intercept setTimeout
    const origSetTimeout = iframeWin.setTimeout.bind(iframeWin);
    iframeWin.setTimeout = function(fn, delay, ...args) {
      timeouts.push({ fn: fn.toString().slice(0, 100), delay });
      return origSetTimeout(fn, delay, ...args);
    };

    // Track audio property changes via proxy
    let muteChanges = [];
    let lastMuted = audio.muted;

    const checkMute = () => {
      if (audio.muted !== lastMuted) {
        muteChanges.push({
          from: lastMuted,
          to: audio.muted,
          time: performance.now(),
          currentTime: audio.currentTime
        });
        lastMuted = audio.muted;
      }
    };

    // Poll every 50ms
    const pollInterval = origSetInterval(checkMute, 50);

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Wait3 seconds with polling
    return new Promise(resolve => {
      origSetTimeout(() => {
        iframeWin.clearInterval(pollInterval);
        resolve({
          muteChanges,
          finalMuted: audio.muted,
          finalCurrentTime: audio.currentTime,
          intervals,
          timeouts,
          frameRequestCallbackCount: frameRequestCallbacks.length
        });
      }, 3000);
    });
  });
  console.log('TRACE MUTE:', JSON.stringify(traceMute, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });