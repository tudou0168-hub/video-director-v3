const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Find pe object in iframe
  const findPe = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    // Try to find pe by looking at all window objects
    const candidates = [];
    for (const k of Object.keys(iframeWin)) {
      try {
        const v = iframeWin[k];
        if (v && typeof v === 'object') {
          const keys = Object.keys(v);
          if (keys.some(k2 => k2.includes('schedule') || k2.includes('decode') || k2.includes('Generation'))) {
            candidates.push({
              key: k,
              keys: keys.slice(0, 20),
              type: typeof v
            });
          }
        }
      } catch(e) {}
    }

    // Also look for any function that has 'pe' in its name
    const peFunctions = [];
    for (const k of Object.keys(iframeWin)) {
      try {
        if (typeof iframeWin[k] === 'function' && k.toLowerCase().includes('pe')) {
          peFunctions.push(k);
        }
      } catch(e) {}
    }

    // Try to get pe from player internals
    const playerStr = player.play.toString();
    const peRefs = playerStr.match(/pe\.\w+/g) || [];

    return {
      candidates,
      peFunctions,
      peRefs: [...new Set(peRefs)],
      playerSrcLen: playerStr.length
    };
  });
  console.log('FIND PE:', JSON.stringify(findPe, null, 2));

  // Also check if there's a separate audio controller
  const findAudioController = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    // Check for any object that looks like an audio engine
    const audioEngineKeys = Object.keys(iframeWin).filter(k => {
      const v = iframeWin[k];
      return v && typeof v === 'object' &&
        (k.includes('audio') || k.includes('media') || k.includes('player') || k.includes('engine'));
    });

    return {
      audioEngineKeys: audioEngineKeys.slice(0, 20)
    };
  });
  console.log('AUDIO CONTROLLER:', JSON.stringify(findAudioController, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });