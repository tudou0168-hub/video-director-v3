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

      const origPlay = player.play.bind(player);

      player.play = function() {
        return origPlay();
      };

      // Play
      player.play();

      // Strip immediately after
      audio.removeAttribute('data-start');
      audio.removeAttribute('data-duration');
      audio.removeAttribute('data-track-index');

      // Check at 1s, 2s, 3s
      setTimeout(() => resolve({ t1s: audio.muted }), 1000);
    });
  });

  console.log('t=1s muted=' + result.t1s + ' ' + (result.t1s === false ? 'PASS' : 'FAIL'));

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });