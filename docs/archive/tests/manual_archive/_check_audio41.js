const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Find mute button in MAIN document (not iframe)
  const findMuteButton = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) {
      return {
        error: 'no mute button',
        allButtons: allButtons.map(b => ({
          ariaLabel: b.getAttribute('aria-label'),
          text: b.textContent?.trim().slice(0, 30)
        }))
      };
    }

    return {
      ariaLabel: muteBtn.getAttribute('aria-label'),
      id: muteBtn.id,
      className: muteBtn.className,
      outerHTML: muteBtn.outerHTML.slice(0, 200)
    };
  });
  console.log('FIND MUTE BUTTON (MAIN DOC):', JSON.stringify(findMuteButton, null, 2));

  // Now click mute button and see effect
  const clickMuteInMain = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    const labelBefore = muteBtn.getAttribute('aria-label');

    // Click it
    muteBtn.click();

    return {
      labelBefore,
      labelAfter: muteBtn.getAttribute('aria-label')
    };
  });
  console.log('CLICK MUTE IN MAIN:', JSON.stringify(clickMuteInMain, null, 2));

  // Check if audio in iframe changed
  const audioState = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime
    };
  });
  console.log('AUDIO STATE AFTER CLICK:', JSON.stringify(audioState, null, 2));

  // Find the actual mute/unmute function in the Studio
  const findMuteFunction = await page.evaluate(() => {
    // Look for functions that toggle mute
    const functions = [];
    for (const k of Object.keys(window)) {
      if (typeof window[k] === 'function' &&
          (k.toLowerCase().includes('mute') ||
           k.toLowerCase().includes('volume') ||
           k.toLowerCase().includes('audio'))) {
        functions.push(k);
      }
    }
    return functions.slice(0, 20);
  });
  console.log('MUTE FUNCTIONS:', JSON.stringify(findMuteFunction, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });