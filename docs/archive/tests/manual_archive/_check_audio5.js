const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get iframe's audio element and check state before play
  const beforePlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    return {
      id: audio.id,
      src: audio.currentSrc || audio.src,
      duration: audio.duration,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume
    };
  });
  console.log('BEFORE PLAY:', JSON.stringify(beforePlay, null, 2));

  // Now click the play button (which is aria-label="Play")
  const playBtn = await page.$('button[aria-label="Play"]');
  console.log('Play button found:', !!playBtn);
  if (playBtn) {
    await playBtn.click();
    console.log('Clicked Play');
    await page.waitForTimeout(2000);
  }

  // Check audio state after clicking play
  const afterPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    return {
      id: audio.id,
      src: audio.currentSrc || audio.src,
      duration: audio.duration,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume
    };
  });
  console.log('AFTER PLAY:', JSON.stringify(afterPlay, null, 2));

  // Check mute button state after play
  const muteBtnState = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    return muteBtn ? {
      ariaLabel: muteBtn.getAttribute('aria-label'),
      title: muteBtn.getAttribute('title')
    } : null;
  });
  console.log('MUTE BTN STATE:', JSON.stringify(muteBtnState, null, 2));

  // Try clicking the mute button
  const muteBtn = await page.$('button[aria-label="Mute audio"]');
  console.log('Mute button found:', !!muteBtn);
  if (muteBtn) {
    await muteBtn.click();
    console.log('Clicked Mute');
    await page.waitForTimeout(500);
  }

  // Check audio state after clicking mute
  const afterMute = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    return {
      id: audio.id,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume
    };
  });
  console.log('AFTER MUTE CLICK:', JSON.stringify(afterMute, null, 2));

  // Check mute button label after clicking
  const muteBtnStateAfter = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    return muteBtn ? { ariaLabel: muteBtn.getAttribute('aria-label') } : null;
  });
  console.log('MUTE BTN STATE AFTER:', JSON.stringify(muteBtnStateAfter, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });