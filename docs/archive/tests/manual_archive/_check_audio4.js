const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Navigate to Studio
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get the iframe's audio element state from parent page context
  const parentAudioInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };

    // The iframe contentWindow's audio
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;

    const audio = iframeDoc.querySelector('audio#voiceover') || iframeDoc.querySelector('audio');
    if (!audio) return { error: 'no audio in iframe' };

    return {
      inIframe: true,
      id: audio.id,
      src: audio.src,
      currentSrc: audio.currentSrc,
      duration: audio.duration,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume,
      readyState: audio.readyState,
      networkState: audio.networkState
    };
  });
  console.log('PARENT CONTEXT AUDIO:', JSON.stringify(parentAudioInfo, null, 2));

  // Check parent page for player controls and mute state
  const parentPageInfo = await page.evaluate(() => {
    // Find mute/unmute button
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute') ||
      b.getAttribute('aria-label')?.toLowerCase().includes('audio') ||
      b.textContent?.toLowerCase().includes('mute')
    );

    // Check for play/pause button
    const playBtn = allButtons.find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('play') ||
      b.textContent?.toLowerCase().includes('play')
    );

    // Check for volume control
    const volumeSlider = document.querySelector('input[type="range"]');

    return {
      buttonsFound: allButtons.slice(0, 10).map(b => ({
        text: b.textContent?.trim().slice(0, 30),
        ariaLabel: b.getAttribute('aria-label')
      })),
      muteButtonFound: muteBtn ? {
        text: muteBtn.textContent?.trim(),
        ariaLabel: muteBtn.getAttribute('aria-label'),
        title: muteBtn.getAttribute('title')
      } : null,
      playButtonFound: playBtn ? {
        text: playBtn.textContent?.trim(),
        ariaLabel: playBtn.getAttribute('aria-label')
      } : null,
      volumeSlider: volumeSlider ? {
        min: volumeSlider.min,
        max: volumeSlider.max,
        value: volumeSlider.value
      } : null
    };
  });
  console.log('PARENT PAGE INFO:', JSON.stringify(parentPageInfo, null, 2));

  // Try clicking the mute button if found
  if (parentPageInfo.muteButtonFound) {
    console.log('Clicking mute button...');
    const muteBtn = await page.$('button[aria-label*="mute"], button[title*="mute"], button[aria-label*="audio"]');
    if (muteBtn) {
      await muteBtn.click();
      await page.waitForTimeout(1000);

      // Re-check audio state
      const afterClick = await page.evaluate(() => {
        const iframe = document.querySelector('iframe');
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const audio = iframeDoc.querySelector('audio#voiceover') || iframeDoc.querySelector('audio');
        if (!audio) return { error: 'no audio' };
        return {
          muted: audio.muted,
          volume: audio.volume,
          paused: audio.paused,
          currentTime: audio.currentTime
        };
      });
      console.log('AFTER CLICKING MUTE:', JSON.stringify(afterClick, null, 2));
    }
  }

  // Check if there's a player control panel
  const playerControls = await page.evaluate(() => {
    // Look for the HyperFrames player controls
    const playerEl = document.querySelector('[class*="player"], [class*="Player"], [class*="audio"], [class*="Audio"]');
    if (!playerEl) return { error: 'no player element found' };
    return {
      tag: playerEl.tagName,
      class: playerEl.className,
      rect: playerEl.getBoundingClientRect()
    };
  });
  console.log('PLAYER CONTROLS:', JSON.stringify(playerControls, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });