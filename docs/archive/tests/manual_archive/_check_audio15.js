const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check player.bridgeVolume
  const bridgeVolume = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;
    return {
      bridgeVolume: player.bridgeVolume,
      tBridgeVolume: player.t?.bridgeVolume
    };
  });
  console.log('BRIDGE VOLUME:', JSON.stringify(bridgeVolume, null, 2));

  // Check the pe (playback engine) object
  const peInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Get pe from player.play closure
    // The player.play source references "pe" which is the playback engine
    // We need to find it in the iframe context
    const player = iframeWin.__player;

    // Look for pe in player
    const playerStr = player.play.toString();
    // Extract variable names from closure
    const vars = playerStr.match(/[a-z]+=/gi) || [];
    const uniqueVars = [...new Set(vars.map(v => v.replace('=', '')))];

    // Check which of these exist in iframeWin
    const found = {};
    uniqueVars.forEach(v => {
      if (iframeWin[v] !== undefined) found[v] = typeof iframeWin[v];
    });

    return { vars: uniqueVars.slice(0, 30), found };
  });
  console.log('PE INFO:', JSON.stringify(peInfo, null, 2));

  // Check for audio context and gain node
  const audioContextInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // Check if there's a Web Audio API context controlling this audio
    // In HyperFrames, audio might be connected through a GainNode
    const hasWebAudio = iframeWin.AudioContext || iframeWin.webkitAudioContext;

    return {
      audioMuted: audio.muted,
      audioVolume: audio.volume,
      audioPaused: audio.paused,
      hasWebAudio: !!hasWebAudio,
      // Check if there's a MediaElementAudioSourceNode
      htmlMediaElement: audio.tagName
    };
  });
  console.log('AUDIO CONTEXT INFO:', JSON.stringify(audioContextInfo, null, 2));

  // Check if pe is in iframeWin
  const peExists = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Look for pe object (playback engine)
    // It might be named differently
    const names = ['pe', 'playbackEngine', 'audioEngine', 'mediaEngine'];
    const result = {};
    names.forEach(n => {
      if (iframeWin[n] !== undefined) result[n] = typeof iframeWin[n];
    });

    // Check __hyperframes
    if (iframeWin.__hyperframes) {
      const keys = Object.keys(iframeWin.__hyperframes).slice(0, 20);
      result.__hyperframes = keys;
    }

    return result;
  });
  console.log('PE EXISTS:', JSON.stringify(peExists, null, 2));

  // Check the schedulePlayback function to understand what it does with volume
  const schedulePlaybackInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Find schedulePlayback
    if (iframeWin.pe?.schedulePlayback) {
      return {
        found: true,
        source: iframeWin.pe.schedulePlayback.toString().slice(0, 300)
      };
    }

    // Look for schedulePlayback anywhere
    const allKeys = Object.keys(iframeWin).filter(k => k.includes('schedule') || k.includes('playback') || k.includes('audio'));
    return { keys: allKeys };
  });
  console.log('SCHEDULE PLAYBACK INFO:', JSON.stringify(schedulePlaybackInfo, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });