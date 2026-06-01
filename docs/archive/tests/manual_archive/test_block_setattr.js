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

      // Override setAttribute to silently drop data-start, data-duration, data-track-index
      const origSetAttr = audio.setAttribute.bind(audio);
      audio.setAttribute = function(name, value) {
        if (name === 'data-start' || name === 'data-duration' || name === 'data-track-index') {
          console.log('Blocked setAttribute(' + name + ')');
          return;
        }
        return origSetAttr(name, value);
      };

      // Also override on prototype
      HTMLAudioElement.prototype.setAttribute = function(name, value) {
        if (name === 'data-start' || name === 'data-duration' || name === 'data-track-index') {
          console.log('Prototype blocked setAttribute(' + name + ')');
          return;
        }
        return origSetAttr.call(this, name, value);
      };

      console.log('Calling player.play()...');
      player?.play();

      setTimeout(() => {
        resolve({
          muted: audio.muted,
          hasDataStart: audio.hasAttribute('data-start'),
          audioAttrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]))
        });
      }, 4000);
    });
  });

  console.log('Result: muted=' + result.muted + ' hasDataStart=' + result.hasDataStart);
  console.log('Audio attrs:', Object.keys(result.audioAttrs).filter(k => k.startsWith('data')));
  console.log(result.muted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });