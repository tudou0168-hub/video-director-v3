const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get player element volume method signature
  const playerVolumeMethod = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // Get setElementVolume signature
    const fn = player.setElementVolume.toString();
    return fn;
  });
  console.log('setElementVolume:', playerVolumeMethod);

  // Find the audio element's ID in the player context
  const playerElementInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Check if player has a reference to the audio element by checking what elements it manages
    // Check if there's a player-level element registry
    const player = iframe.contentWindow.__player;

    // Get the main timeline
    const timeline = player.getMainTimeline ? player.getMainTimeline() : null;
    if (timeline) {
      return {
        timelineExists: true,
        timelineKeys: Object.keys(timeline).slice(0, 20)
      };
    }
    return { timelineExists: false };
  });
  console.log('PLAYER ELEMENT INFO:', JSON.stringify(playerElementInfo, null, 2));

  // Check if there's a mute button for audio element specifically
  const audioMuteBtn = await page.evaluate(() => {
    // Look in the iframe for mute button
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

    const muteBtn = iframeDoc.querySelector('button[aria-label*="mute"], button[aria-label*="audio"]');
    if (muteBtn) {
      return {
        found: true,
        parent: muteBtn.parentElement?.tagName + '.' + muteBtn.parentElement?.className?.split(' ')[0],
        ariaLabel: muteBtn.getAttribute('aria-label')
      };
    }
    return { found: false };
  });
  console.log('AUDIO MUTE BTN IN IFRAME:', JSON.stringify(audioMuteBtn, null, 2));

  // Check the mute button's click handler
  const muteBtnClickHandler = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase() === 'mute audio'
    );
    if (!muteBtn) return { error: 'no mute button' };

    // Check if it has an onclick or event listener
    const listeners = [];
    ['click', 'mousedown', 'touchstart'].forEach(evt => {
      const handler = muteBtn[`on${evt}`];
      if (handler) listeners.push({ event: evt, handler: handler.toString().slice(0, 100) });
    });

    // Check data attributes
    const dataAttrs = {};
    Array.from(muteBtn.attributes).forEach(attr => {
      if (attr.name.startsWith('data-') || attr.name.startsWith('@')) {
        dataAttrs[attr.name] = attr.value;
      }
    });

    return {
      ariaLabel: muteBtn.getAttribute('aria-label'),
      dataAttrs
    };
  });
  console.log('MUTE BTN CLICK HANDLER:', JSON.stringify(muteBtnClickHandler, null, 2));

  // Now test: use __player to get the audio element and call play
  const playerPlayTest = await page.evaluate(async () => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // Check if player has audio track binding
    const audioEl = iframeWin.document.querySelector('audio#voiceover');

    // Try calling player.play()
    try {
      const result = player.play();
      return {
        playResult: result,
        audioPaused: audioEl.paused,
        audioCurrentTime: audioEl.currentTime,
        audioMuted: audioEl.muted
      };
    } catch(e) {
      return { playError: e.message };
    }
  });
  console.log('PLAYER PLAY TEST:', JSON.stringify(playerPlayTest, null, 2));

  await page.waitForTimeout(1000);

  const afterPlayerPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      paused: audio.paused,
      currentTime: audio.currentTime,
      muted: audio.muted
    };
  });
  console.log('AFTER PLAYER.PLAY():', JSON.stringify(afterPlayerPlay, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });