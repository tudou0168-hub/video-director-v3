const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Intercept ALL RAF callbacks and track which one sees audio.muted change
  const traceRAFtoMute = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    const origRAF = iframeWin.requestAnimationFrame.bind(iframeWin);
    const origCancel = iframeWin.cancelAnimationFrame.bind(iframeWin);

    let rafId = 0;
    const rafCallbacks = new Map();
    const rafLog = [];
    let muteHappenedAtRaf = null;

    iframeWin.requestAnimationFrame = function(cb) {
      const id = ++rafId;
      const wrapped = (t) => {
        const result = cb(t);
        // Check if audio got muted during this callback
        if (audio.muted === true && muteHappenedAtRaf === null) {
          muteHappenedAtRaf = id;
          rafLog.push({ id, event: 'mute_detected', time: performance.now() });
        }
        return result;
      };
      rafCallbacks.set(id, wrapped);
      return origRAF(wrapped);
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
        // Get source of callback that caused mute
        let muteCallbackSrc = null;
        if (muteHappenedAtRaf !== null) {
          const cb = rafCallbacks.get(muteHappenedAtRaf);
          if (cb) {
            muteCallbackSrc = cb.toString().slice(0, 500);
          }
        }

        resolve({
          muteHappenedAtRaf,
          rafLog,
          callbackCount: rafCallbacks.size,
          muteCallbackSrc,
          audioMuted: audio.muted
        });
      }, 4000);
    });
  });
  console.log('TRACE RAF TO MUTE:', JSON.stringify(traceRAFtoMute, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });