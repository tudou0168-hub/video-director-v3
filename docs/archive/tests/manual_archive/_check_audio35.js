const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Patch player.play() to unmute AND cancel RAF loops
  const patchPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    const origPlay = player.play.bind(player);
    const origRAF = iframeWin.requestAnimationFrame.bind(iframeWin);
    const origCancel = iframeWin.cancelAnimationFrame.bind(iframeWin);

    // Collect RAF IDs to cancel
    let activeRAFIds = new Set();
    let cancelCount = 0;

    iframeWin.requestAnimationFrame = function(cb) {
      const id = origRAF(cb);
      activeRAFIds.add(id);
      return id;
    };

    iframeWin.cancelAnimationFrame = function(id) {
      if (activeRAFIds.has(id)) {
        cancelCount++;
        activeRAFIds.delete(id);
      }
      return origCancel(id);
    };

    player.play = function() {
      const result = origPlay();
      // Immediately unmute
      audio.muted = false;
      audio.volume = 1;
      // Cancel all active RAF callbacks after a tick
      iframeWin.setTimeout(() => {
        const ids = [...activeRAFIds];
        ids.forEach(id => {
          iframeWin.cancelAnimationFrame(id);
        });
      }, 0);
      return result;
    };

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call patched player.play()
    player.play();

    return { patched: true, cancelCount };
  });
  console.log('PATCH PLAY:', JSON.stringify(patchPlay, null, 2));

  // Wait and check
  await page.waitForTimeout(3000);

  const afterWait = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('AFTER WAIT:', JSON.stringify(afterWait, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });