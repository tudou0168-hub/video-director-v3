const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();

  // Use addInitScript on context (like we did for test_proto_fresh.js)
  await context.addInitScript(() => {
    const origPlay = HTMLAudioElement.prototype.play;
    HTMLAudioElement.prototype.play = function() {
      this.removeAttribute('data-start');
      this.removeAttribute('data-duration');
      this.removeAttribute('data-track-index');
      console.log('FRESH: HTMLAudioElement.prototype.play stripped data-*');
      return origPlay.call(this);
    };
  });

  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

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

      console.log('audio data-start before play:', audio?.getAttribute('data-start'));
      console.log('Calling player.play()...');
      player?.play();

      setTimeout(() => {
        resolve({
          muted: audio.muted,
          hasDataStart: audio?.hasAttribute('data-start')
        });
      }, 4000);
    });
  });

  console.log('Result: muted=' + result.muted + ' hasDataStart=' + result.hasDataStart);
  console.log(result.muted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });