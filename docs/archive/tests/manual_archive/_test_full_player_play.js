const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  const fullSrc = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };
    return { src: player.play.toString() };
  });
  console.log('FULL PLAYER PLAY SOURCE:\n' + fullSrc.src);

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });