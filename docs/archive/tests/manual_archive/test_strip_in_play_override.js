const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('about:blank');
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1', { waitUntil: 'load' });

  await page.waitForSelector('iframe', { timeout: 10000 });
  await page.waitForTimeout(2000);

  const result = await page.evaluate(async () => {
    return new Promise(async (resolve) => {
      const iframe = document.querySelector('iframe');
      const iframeWin = iframe.contentWindow;
      const iframeDoc = iframeWin.document;
      const audio = iframeDoc.querySelector('audio#voiceover');
      const player = iframeWin.__player;

      // Intercept player.play - strip data-* BEFORE calling original play
      const origPlay = player.play.bind(player);
      player.play = function() {
        audio.removeAttribute('data-start');
        audio.removeAttribute('data-duration');
        audio.removeAttribute('data-track-index');
        return origPlay();
      };

      // Now call play
      player.play();

      // Check at various times
      setTimeout(() => resolve({ t1s: audio.muted }), 1000);
    });
  });

  console.log('t=1s muted=' + result.t1s + ' ' + (result.t1s === false ? 'PASS' : 'FAIL'));

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });