const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Override setAttribute on the audio element BEFORE player.play
  const interceptSetAttribute = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    const callLog = [];
    const origSetAttribute = Element.prototype.setAttribute;
    const origRemoveAttribute = Element.prototype.removeAttribute;

    // Override on Element.prototype so it catches ALL elements
    Element.prototype.setAttribute = function(name, value) {
      if (this === audio && (name === 'muted' || name === 'volume')) {
        callLog.push({
          method: 'setAttribute',
          name,
          value,
          time: performance.now(),
          stack: new Error().stack.split('\n').slice(0, 6)
        });
      }
      return origSetAttribute.call(this, name, value);
    };

    Element.prototype.removeAttribute = function(name) {
      if (this === audio && (name === 'muted' || name === 'volume')) {
        callLog.push({
          method: 'removeAttribute',
          name,
          time: performance.now(),
          stack: new Error().stack.split('\n').slice(0, 6)
        });
      }
      return origRemoveAttribute.call(this, name);
    };

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Wait
    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          callLog,
          audioMuted: audio.muted,
          audioVolume: audio.volume
        });
      }, 3000);
    });
  });
  console.log('INTERCEPT SET ATTRIBUTE:', JSON.stringify(interceptSetAttribute, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });