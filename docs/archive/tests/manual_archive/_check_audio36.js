const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check for Web Audio API usage
  const webAudioCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    if (!player) return { error: 'no player' };

    // Check if AudioContext exists
    const hasAudioContext = 'AudioContext' in iframeWin || 'webkitAudioContext' in iframeWin;

    // Look for any GainNode or audio processing
    let gainNodes = [];
    let audioContexts = [];

    if (hasAudioContext) {
      const AC = iframeWin.AudioContext || iframeWin.webkitAudioContext;
      // Find all audio contexts
      for (const k of Object.keys(iframeWin)) {
        const v = iframeWin[k];
        if (v instanceof AC) {
          audioContexts.push({
            key: k,
            state: v.state,
            sampleRate: v.sampleRate
          });
        }
      }
      // Check GainNodes
      for (const k of Object.keys(iframeWin)) {
        const v = iframeWin[k];
        if (v && v.context && v.type === 'gain') {
          gainNodes.push({
            key: k,
            gain: v.gain ? v.gain.value : 'N/A'
          });
        }
      }
    }

    // Check if audio has audioTracks
    const audioTracks = audio.audioTracks ? Array.from(audio.audioTracks).map(t => ({
      kind: t.kind,
      label: t.label,
      enabled: t.enabled
    })) : [];

    // Check for MediaElementAudioSourceNode
    let mediaSourceNodes = [];
    if (hasAudioContext) {
      const AC = iframeWin.AudioContext || iframeWin.webkitAudioContext;
      for (const k of Object.keys(iframeWin)) {
        const v = iframeWin[k];
        if (v && v.context instanceof AC && v.type === 'mediaElementAudioSourceNode') {
          mediaSourceNodes.push({ key: k });
        }
      }
    }

    return {
      hasAudioContext,
      audioContexts,
      gainNodes,
      mediaSourceNodes,
      audioTracks
    };
  });
  console.log('WEB AUDIO CHECK:', JSON.stringify(webAudioCheck, null, 2));

  // Most importantly: check if directly setting audio volume to 0 vs muted
  // Sometimes "muted" is implemented by setting volume to 0
  const volumeVsMuted = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          effectiveVolume: audio.effectiveVolume,
          currentTime: audio.currentTime
        });
      }, 3000);
    });
  });
  console.log('VOLUME VS MUTED:', JSON.stringify(volumeVsMuted, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });