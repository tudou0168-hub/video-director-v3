const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get player.play() source
  const playerPlaySource = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || (iframe.contentWindow && iframe.contentWindow.document);
    const player = iframe.contentWindow.__player;

    try {
      const src = player.play.toString();
      return {
        length: src.length,
        firstLines: src.split('\n').slice(0, 20).join('\n')
      };
    } catch(e) {
      return { error: e.message };
    }
  });
  console.log('PLAYER PLAY SOURCE:', JSON.stringify(playerPlaySource, null, 2));

  // Check what happens when player.play() is called - try to intercept
  const interceptTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || (iframe.contentWindow && iframe.contentWindow.document);
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframe.contentWindow.__player;

    // Store original play
    const origPlay = audio.play.bind(audio);
    let muteSetByPlay = null;

    // Replace play
    audio.play = function() {
      // Before play, check muted
      muteSetByPlay = audio.muted;
      // After play is called, check again
      const afterMuted = audio.muted;
      const result = origPlay();
      // Check muted after async
      setTimeout(() => {
        console.log('ASYNC CHECK after play:', audio.muted, audio.currentTime);
      }, 100);
      return result;
    };

    // Reset audio
    audio.pause();
    audio.muted = false;
    audio.volume = 1;
    audio.currentTime = 0;

    // Call player.play
    player.play();

    return {
      muteBeforePlay: muteSetByPlay,
      muteAfterPlay: audio.muted,
      currentTimeAfter: audio.currentTime
    };
  });
  console.log('INTERCEPT TEST:', JSON.stringify(interceptTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });