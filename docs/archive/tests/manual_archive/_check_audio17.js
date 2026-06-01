const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check what the Unmute audio button click actually does
  const unmuteClickEffect = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const iframeWin = iframe.contentWindow;
    const audio = iframeDoc.querySelector('audio#voiceover');

    // First, have audio playing (muted)
    iframeWin.__player.play();

    return {
      beforeUnmute: {
        audioMuted: audio.muted,
        audioVolume: audio.volume,
        ariaLabel: Array.from(document.querySelectorAll('button')).find(b =>
          b.getAttribute('aria-label')?.toLowerCase().includes('mute')
        )?.getAttribute('aria-label')
      }
    };
  });
  console.log('BEFORE UNMUTE:', JSON.stringify(unmuteClickEffect, null, 2));

  // Click Unmute
  const unmuteBtn = await page.$('button[aria-label="Unmute audio"]');
  if (unmuteBtn) {
    await unmuteBtn.click();
    await page.waitForTimeout(1000);
  }

  const afterUnmuteClick = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    return {
      audioMuted: audio.muted,
      audioVolume: audio.volume,
      audioPaused: audio.paused,
      ariaLabel: Array.from(document.querySelectorAll('button')).find(b =>
        b.getAttribute('aria-label')?.toLowerCase().includes('mute')
      )?.getAttribute('aria-label')
    };
  });
  console.log('AFTER UNMUTE CLICK:', JSON.stringify(afterUnmuteClick, null, 2));

  // KEY: Now directly set audio.muted = false and check if it unmutes
  await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    console.log('Directly setting audio.muted = false');
    audio.muted = false;
    audio.volume = 1;
    console.log('audio.muted now:', audio.muted);
  });

  const afterDirectMuteFalse = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      audioMuted: audio.muted,
      audioVolume: audio.volume,
      ariaLabel: Array.from(document.querySelectorAll('button')).find(b =>
        b.getAttribute('aria-label')?.toLowerCase().includes('mute')
      )?.getAttribute('aria-label')
    };
  });
  console.log('AFTER DIRECT audio.muted=false:', JSON.stringify(afterDirectMuteFalse, null, 2));

  // Check if there's a Web Audio API graph that might be affecting volume
  const webAudioCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;

    // Check if there's a MediaElementAudioSourceNode connected to a GainNode
    if (iframeWin.AudioContext || iframeWin.webkitAudioContext) {
      const ctx = new (iframeWin.AudioContext || iframeWin.webkitAudioContext)();
      // Check if audio element is connected to context
      const audio = iframeWin.document.querySelector('audio#voiceover');
      try {
        const mediaElSource = ctx.createMediaElementSource(audio);
        const gainNode = ctx.createGain();
        mediaElSource.connect(gainNode);
        gainNode.connect(ctx.destination);
        return {
          hasWebAudio: true,
          gainValue: gainNode.gain.value
        };
      } catch(e) {
        return { hasWebAudio: true, error: e.message };
      }
    }
    return { hasWebAudio: false };
  });
  console.log('WEB AUDIO CHECK:', JSON.stringify(webAudioCheck, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });