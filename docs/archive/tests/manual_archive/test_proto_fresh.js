const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Inject prototype override into new document BEFORE page loads
  await context.addInitScript(() => {
    const origPlay = HTMLAudioElement.prototype.play;
    HTMLAudioElement.prototype.play = function() {
      this.removeAttribute('data-start');
      this.removeAttribute('data-duration');
      this.removeAttribute('data-track-index');
      console.log('FRESH: HTMLAudioElement.play intercepted, stripped data-*');
      return origPlay.call(this);
    };
  });

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

      console.log('Calling player.play()...');
      player?.play();

      setTimeout(() => {
        resolve({ muted: audio.muted, attrs: Object.keys(Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]))).filter(k => k.startsWith('data-')) });
      }, 4000);
    });
  });

  console.log('Prototype fresh load: muted=' + result.muted + ' ' + (result.muted === false ? 'PASS' : 'FAIL'));
  console.log('Remaining data-* attrs:', result.attrs);

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });