const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test1: Direct MP3 play in same browser/context
  const tabMuteCheck = await page.evaluate(() => {
    // Check if this page tab is muted
    const audio = document.querySelector('audio');
    if (!audio) return { error: 'no audio in main doc' };

    // Try playing
    audio.volume = 1;
    audio.muted = false;

    return {
      tabMuted: document.hidden,
      audioMuted: audio.muted,
      audioVolume: audio.volume,
      canPlay: typeof audio.play === 'function'
    };
  });
  console.log('TAB MUTE CHECK:', JSON.stringify(tabMuteCheck, null, 2));

  // Test 2: Play mp3 directly in browser - check if audio context allows it
  const page2 = await context.newPage();
  await page2.goto('http://localhost:3002/api/projects/hyperframes_timeline/preview/assets/voiceover.mp3');
  await page2.waitForTimeout(1000);

  const directPlayInfo = await page2.evaluate(() => {
    const audio = document.querySelector('audio') || document.createElement('audio');
    audio.src = location.href;
    audio.volume = 1;
    audio.muted = false;
    document.body.appendChild(audio);
    const p = audio.play();
    return {
      playReturned: typeof p,
      audioMuted: audio.muted,
      audioVolume: audio.volume,
      audioPaused: audio.paused,
      readyState: audio.readyState
    };
  });
  console.log('DIRECT MP3 PLAY:', JSON.stringify(directPlayInfo, null, 2));

  await page2.waitForTimeout(2000);

  const afterDirectPlay = await page2.evaluate(() => {
    const audio = document.querySelector('audio');
    return audio ? {
      muted: audio.muted,
      volume: audio.volume,
      paused: audio.paused,
      currentTime: audio.currentTime
    } : { error: 'no audio' };
  });
  console.log('AFTER DIRECT PLAY:', JSON.stringify(afterDirectPlay, null, 2));

  // Test 3: Check what __player methods are available for volume control
  const playerMethods = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // List all player methods
    const methods = Object.keys(player).filter(k => typeof player[k] === 'function');
    const volumeRelated = methods.filter(m =>
      m.toLowerCase().includes('volume') ||
      m.toLowerCase().includes('mute') ||
      m.toLowerCase().includes('audio') ||
      m.toLowerCase().includes('media')
    );

    return {
      allMethods: methods,
      volumeRelated
    };
  });
  console.log('PLAYER METHODS:', JSON.stringify(playerMethods, null, 2));

  // Test 4: Check if iframe sandbox attribute affects audio
  const sandboxInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    return {
      sandbox: iframe.getAttribute('sandbox'),
      allow: iframe.getAttribute('allow'),
      allowFullscreen: iframe.getAttribute('allowfullscreen')
    };
  });
  console.log('SANDBOX INFO:', JSON.stringify(sandboxInfo, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });