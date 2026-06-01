const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Start fresh
  await page.goto('about:blank');
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1', { waitUntil: 'networkidle' });

  await page.waitForSelector('iframe', { timeout: 10000 });
  await page.waitForTimeout(2000);

  const result = await page.evaluate(async () => {
    return new Promise(async (resolve) => {
      const iframe = document.querySelector('iframe');
      const iframeWin = iframe.contentWindow;
      const iframeDoc = iframeWin.document;
      const audio = iframeDoc.querySelector('audio#voiceover');
      const player = iframeWin.__player;

      // Intercept player._i or whatever is called on play
      let callCount = 0;
      const origPlay = player.play.bind(player);

      player.play = function() {
        callCount++;
        console.log('player.play called, call #', callCount);
        return origPlay();
      };

      // Play
      player.play();

      // Strip data-* right after play returns
      await new Promise(r => setTimeout(r, 0));
      audio.removeAttribute('data-start');
      audio.removeAttribute('data-duration');
      audio.removeAttribute('data-track-index');

      console.log('Stripped data-* immediately after play()');

      // Check every 500ms for 5 seconds
      let checks = [];
      let checkCount = 0;
      const interval = setInterval(() => {
        checks.push({ t: checkCount * 500, muted: audio.muted });
        checkCount++;
        if (checkCount >= 10) {
          clearInterval(interval);
          resolve({ checks, finalMuted: audio.muted });
        }
      }, 500);
    });
  });

  console.log('Checks:');
  result.checks.forEach(c => console.log(`  t=${c.t}ms: muted=${c.muted}`));
  console.log('Final: muted=' + result.finalMuted + ' ' + (result.finalMuted === false ? 'PASS' : 'FAIL'));

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });