const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check __player audio control
  const playerAudioInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // Enumerate all player properties
    const playerProps = Object.keys(player).filter(k =>
      k.toLowerCase().includes('audio') ||
      k.toLowerCase().includes('mute') ||
      k.toLowerCase().includes('volume') ||
      k.toLowerCase().includes('sound') ||
      k.toLowerCase().includes('play')
    );

    const playerState = {};
    playerProps.forEach(k => {
      try {
        const v = player[k];
        if (typeof v === 'function') playerState[k] = '[function]';
        else if (typeof v === 'object' && v !== null) playerState[k] = JSON.stringify(v);
        else playerState[k] = v;
      } catch(e) {
        playerState[k] = '[error]';
      }
    });

    return playerProps.length ? playerState : { noAudioProps: true };
  });
  console.log('PLAYER AUDIO PROPS:', JSON.stringify(playerAudioInfo, null, 2));

  // Check if player has audio element reference
  const playerAudioRef = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // Check if player has a reference to the audio element
    const playerStr = player.toString ? player.toString() : '';
    return {
      hasAudioInPlayer: playerStr.includes('audio'),
      playerKeys: Object.keys(player).slice(0, 30)
    };
  });
  console.log('PLAYER AUDIO REF:', JSON.stringify(playerAudioRef, null, 2));

  // Check the __player.play() and __player.pause()
  const playerControls = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    return {
      playFn: typeof player.play,
      pauseFn: typeof player.pause,
      stopFn: typeof player.stop,
      seekFn: typeof player.seek,
      getAudioCurrentTime: typeof player.getAudioCurrentTime,
      getCurrentTime: typeof player.getCurrentTime,
      getTime: typeof player.getTime
    };
  });
  console.log('PLAYER CONTROLS:', JSON.stringify(playerControls, null, 2));

  // Check the Studio's bottom play bar
  const bottomBarInfo = await page.evaluate(() => {
    // Find bottom control bar
    const bottomBar = document.querySelector('[class*="bottom"], [class*="footer"], [class*="controls"], [class*="player-bar"]');
    if (!bottomBar) return { error: 'no bottom bar found' };

    const buttons = Array.from(bottomBar.querySelectorAll('button, input')).map(b => ({
      tag: b.tagName,
      ariaLabel: b.getAttribute('aria-label'),
      type: b.type,
      value: b.value
    }));

    return {
      class: bottomBar.className,
      buttons
    };
  });
  console.log('BOTTOM BAR:', JSON.stringify(bottomBarInfo, null, 2));

  // Check the timeline audio track
  const timelineTrack = await page.evaluate(() => {
    // Look for timeline component with audio track
    const timelineEl = document.querySelector('[class*="timeline"], [class*="Timeline"]');
    if (!timelineEl) return { error: 'no timeline' };

    const audioTrack = timelineEl.querySelector('[class*="audio"], [class*="track"], audio');
    return {
      timelineClass: timelineEl.className,
      hasAudioTrack: !!audioTrack
    };
  });
  console.log('TIMELINE TRACK:', JSON.stringify(timelineTrack, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });