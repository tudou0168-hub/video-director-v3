const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get bridgeVolume value
  const bridgeVolumeCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const player = iframeWin = iframe.contentWindow;
    const playerObj = player.__player;

    // Get all numeric/string properties of player that could be volume-related
    const volProps = {};
    const keys = Object.keys(playerObj);
    keys.forEach(k => {
      if (k.toLowerCase().includes('vol') || k.toLowerCase().includes('bridge')) {
        try {
          const v = playerObj[k];
          volProps[k] = typeof v === 'object' ? JSON.stringify(v) : v;
        } catch(e) {}
      }
    });

    // Also check iframeWin for bridgeVolume
    const iframeWinProps = {};
    Object.keys(iframeWin).slice(0, 50).forEach(k => {
      if (k.toLowerCase().includes('bridge') || k.toLowerCase().includes('volume')) {
        try { iframeWinProps[k] = iframeWin[k]; } catch(e) {}
      }
    });

    return { volProps, iframeWinProps };
  });
  console.log('BRIDGE VOLUME CHECK:', JSON.stringify(bridgeVolumeCheck, null, 2));

  // Check t.bridgeVolume specifically
  const tBridgeVolume = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // t is the closure variable in player.play
    // We need to find what t is
    // Let's look at what t.capturedTimeline etc refers to

    // Check if there's a __timelines or __hfTypegpuTime that might be t
    const tCandidate = iframeWin.__hfTypegpuTime;
    if (tCandidate) {
      return {
        tFound: '__hfTypegpuTime',
        keys: Object.keys(tCandidate).filter(k => k.toLowerCase().includes('bridge') || k.toLowerCase().includes('vol')),
        bridgeVolume: tCandidate.bridgeVolume,
        audioVolume: tCandidate.audioVolume
      };
    }

    return { tFound: false };
  });
  console.log('T BRIDGE VOLUME:', JSON.stringify(tBridgeVolume, null, 2));

  // Check what t.currentTime, t.isPlaying are
  const tProps = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Look for any object that has isPlaying, currentTime, mediaForceSyncNextTick
    const candidates = [iframeWin.__hfTypegpuTime, iframeWin.__timelines, iframeWin.__hyperframes];
    const result = [];

    candidates.forEach(c => {
      if (c && typeof c === 'object') {
        const keys = Object.keys(c);
        const relevant = keys.filter(k => k.includes('Playing') || k.includes('CurrentTime') || k.includes('Volume') || k.includes('Bridge'));
        if (relevant.length) {
          const vals = {};
          relevant.forEach(k => { try { vals[k] = c[k]; } catch(e) {} });
          result.push({ name: keys.length > 0 ? 'found' : 'empty', vals });
        }
      }
    });

    return result;
  });
  console.log('T PROPS:', JSON.stringify(tProps, null, 2));

  // Check __timelines structure
  const timelinesInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const tl = iframeWin.__timelines;
    if (!tl) return { error: 'no __timelines' };
    return {
      keys: Object.keys(tl),
      hasbridgeVolume: 'bridgeVolume' in tl,
      bridgeVolume: tl.bridgeVolume
    };
  });
  console.log('TIMELINES INFO:', JSON.stringify(timelinesInfo, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });