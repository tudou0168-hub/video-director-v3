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

      // Try stripping data-* from audio element in the iframe BEFORE player.init runs
      // But we can't intercept player.init directly...

      // Instead: Override audio.play to ALWAYS strip data-*
      const origAudioPlay = audio.play.bind(audio);
      audio.play = function() {
        this.removeAttribute('data-start');
        this.removeAttribute('data-duration');
        this.removeAttribute('data-track-index');
        console.log('audio.play called, stripped data-*');
        return origAudioPlay();
      };

      // Also override on HTMLAudioElement prototype for any new audio elements
      const origProtoPlay = HTMLAudioElement.prototype.play;
      HTMLAudioElement.prototype.play = function() {
        this.removeAttribute('data-start');
        this.removeAttribute('data-duration');
        this.removeAttribute('data-track-index');
        return origProtoPlay.call(this);
      };

      // Now call player.play
      console.log('Calling player.play()...');
      player?.play();

      setTimeout(() => {
        resolve({ muted: audio.muted, hasDataStart: audio.hasAttribute('data-start') });
      }, 4000);
    });
  });

  console.log('Result: muted=' + result.muted + ' hasDataStart=' + result.hasDataStart);
  console.log(result.muted === false ? 'PASS' : 'FAIL');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });