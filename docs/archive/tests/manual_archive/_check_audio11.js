const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get initial state - check what the mute button says
  const initialState = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    return {
      muteBtnLabel: muteBtn?.getAttribute('aria-label'),
      audioMuted: audio?.muted,
      audioVolume: audio?.volume
    };
  });
  console.log('INITIAL STATE:', JSON.stringify(initialState, null, 2));

  // Click mute button
  const muteBtn = await page.$('button[aria-label="Mute audio"]');
  console.log('Mute button found, clicking...');
  await muteBtn.click();
  await page.waitForTimeout(500);

  const afterMuteClick = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    return {
      muteBtnLabel: muteBtn?.getAttribute('aria-label'),
      audioMuted: audio?.muted,
      audioVolume: audio?.volume,
      audioPaused: audio?.paused
    };
  });
  console.log('AFTER MUTE CLICK:', JSON.stringify(afterMuteClick, null, 2));

  // Now click play via __player.play()
  await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    iframeWin.__player.play();
  });
  console.log('Called __player.play()');
  await page.waitForTimeout(1500);

  const afterPlayerPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    return {
      audioMuted: audio?.muted,
      audioPaused: audio?.paused,
      audioCurrentTime: audio?.currentTime,
      muteBtnLabel: Array.from(document.querySelectorAll('button')).find(b =>
        b.getAttribute('aria-label')?.toLowerCase().includes('mute')
      )?.getAttribute('aria-label')
    };
  });
  console.log('AFTER __player.play():', JSON.stringify(afterPlayerPlay, null, 2));

  // Now check: clicking the SAME button (which now says "Unmute audio") should unmute
  const unmuteBtn = await page.$('button[aria-label="Unmute audio"]');
  if (unmuteBtn) {
    console.log('Clicking Unmute audio button...');
    await unmuteBtn.click();
    await page.waitForTimeout(500);

    const afterUnmute = await page.evaluate(() => {
      const iframe = document.querySelector('iframe');
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const audio = iframeDoc.querySelector('audio#voiceover');

      return {
        audioMuted: audio?.muted,
        audioPaused: audio?.paused,
        audioCurrentTime: audio?.currentTime
      };
    });
    console.log('AFTER UNMUTE CLICK:', JSON.stringify(afterUnmute, null, 2));
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });