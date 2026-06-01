const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check for WebAudio nodes that might be silencing audio
  const webAudioInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    const AC = iframeWin.AudioContext || iframeWin.webkitAudioContext;
    const hasAC = !!AC;

    // Look for GainNodes with value 0
    const gainNodes = [];
    const audioContextNodes = [];

    if (hasAC) {
      // Find all GainNodes
      for (const k of Object.keys(iframeWin)) {
        try {
          const v = iframeWin[k];
          if (v && v.context instanceof AC) {
            if (v.type === 'gain') {
              gainNodes.push({
                key: k,
                gain: v.gain ? v.gain.value : 'N/A'
              });
            }
            audioContextNodes.push({
              key: k,
              type: v.type,
              contextState: v.context ? v.context.state : 'N/A'
            });
          }
        } catch(e) {}
      }

      // Check if audio element is connected to any audio context
      const audioContext = audio._context;
      const dest = audio._dest;
    }

    // Also check if browser tab is muted
    const mediaDevices = navigator.mediaDevices;

    return {
      hasAudioContext: hasAC,
      gainNodes,
      audioContextNodes,
      // Check audio element's _context and _dest if they exist
      audioContext: audio._context ? 'exists' : 'none',
      audioDest: audio._dest ? 'exists' : 'none'
    };
  });
  console.log('WEB AUDIO INFO:', JSON.stringify(webAudioInfo, null, 2));

  // Most importantly: check if audio.currentTime actually advances DURING PLAY
  const timeAdvanceCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    player.play();

    const times = [];
    const start = performance.now();

    // Sample currentTime every100ms for 2 seconds
    const origRAF = iframeWin.requestAnimationFrame.bind(iframeWin);
    let sampleIndex = 0;

    function sampleTime(timestamp) {
      times.push({
        t: performance.now() - start,
        currentTime: audio.currentTime,
        muted: audio.muted
      });
      sampleIndex++;
      if (sampleIndex < 20) {
        origRAF(sampleTime);
      }
    }

    origRAF(sampleTime);

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ times });
      }, 2500);
    });
  });
  console.log('TIME ADVANCE CHECK:', JSON.stringify(timeAdvanceCheck, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });