const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get audio state in iframe
  const audioState = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    return {
      id: audio.id,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime,
      duration: audio.duration,
      src: audio.currentSrc,
      // Check the iframe's audio context
      audioContextState: iframe.contentWindow.AudioContext ? 'exists' : 'no AudioContext'
    };
  });
  console.log('AUDIO STATE:', JSON.stringify(audioState, null, 2));

  // Test: click mute button and see what happens to audio.muted
  const muteBtn = await page.$('button[aria-label="Mute audio"]');
  if (muteBtn) {
    await muteBtn.click();
    await page.waitForTimeout(500);

    const afterMute = await page.evaluate(() => {
      const iframe = document.querySelector('iframe');
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const audio = iframeDoc.querySelector('audio#voiceover');
      return {
        audioMuted: audio.muted,
        audioVolume: audio.volume
      };
    });
    console.log('AFTER MUTE CLICK AUDIO STATE:', JSON.stringify(afterMute, null, 2));

    const newMuteBtnLabel = await muteBtn.getAttribute('aria-label');
    console.log('MUTE BUTTON LABEL NOW:', newMuteBtnLabel);
  }

  // Check if there's a tab audio indicator (speaker icon in tab)
  const tabAudioIndicator = await page.evaluate(() => {
    // Check document.hidden and other page states
    return {
      hidden: document.hidden,
      title: document.title,
      // Check if media keys are being used
      hasMediaSession: 'mediaSession' in navigator
    };
  });
  console.log('TAB INFO:', JSON.stringify(tabAudioIndicator, null, 2));

  // Try to get player info from iframe
  const playerInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Look for player object
    if (iframeWin.__player) {
      const p = iframeWin.__player;
      return {
        playerExists: true,
        playerType: typeof p,
        hasAudioTrack: true,
        // Try to get audio-related properties
        audioMuted: p.audioMuted,
        audioVolume: p.audioVolume
      };
    }
    return { playerExists: false };
  });
  console.log('PLAYER INFO:', JSON.stringify(playerInfo, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });