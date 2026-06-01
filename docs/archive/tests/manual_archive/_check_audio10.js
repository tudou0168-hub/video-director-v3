const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: click mute button and then play via __player.play()
  const muteBtn = await page.$('button[aria-label="Mute audio"]');
  if (muteBtn) {
    console.log('Clicking Mute audio button...');
    await muteBtn.click();
    await page.waitForTimeout(500);
  }

  // Now test player.play()
  const playResult = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    try {
      const result = player.play();
      return {
        playResult: result !== undefined ? 'returned' : 'void',
        playerKeys: Object.keys(player).slice(0, 15)
      };
    } catch(e) {
      return { error: e.message };
    }
  });
  console.log('PLAY RESULT:', JSON.stringify(playResult, null, 2));

  await page.waitForTimeout(1000);

  // Check audio state after player.play()
  const afterPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    return {
      paused: audio.paused,
      currentTime: audio.currentTime,
      muted: audio.muted,
      volume: audio.volume
    };
  });
  console.log('AFTER PLAY:', JSON.stringify(afterPlay, null, 2));

  // Also check mute button state
  const muteBtnState = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    return muteBtn ? { ariaLabel: muteBtn.getAttribute('aria-label') } : null;
  });
  console.log('MUTE BTN STATE:', JSON.stringify(muteBtnState, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });