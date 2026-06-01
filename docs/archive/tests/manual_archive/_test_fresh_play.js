const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForSelector('iframe', { timeout: 10000 });
  await page.waitForTimeout(3000);

  // Play without modifications
  const playResult = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframe.contentWindow.__player;

    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          paused: audio.paused
        });
      }, 5000);
    });
  });
  console.log('PLAY RESULT:', JSON.stringify(playResult, null, 2));
  console.log(playResult.muted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });