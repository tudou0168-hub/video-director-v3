const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Find and click the mute button
  const clickMuteButton = await page.evaluate(() => {
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

    // Find mute button
    const muteBtn = Array.from(iframeDoc.querySelectorAll('button')).find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button', buttons: Array.from(iframeDoc.querySelectorAll('button')).map(b => b.getAttribute('aria-label')) };

    const btnLabelBefore = muteBtn.getAttribute('aria-label');

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Wait for mute to happen
    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        const stateBeforeClick = {
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime
        };

        // Click the mute button
        muteBtn.click();

        const stateAfterClick = {
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          btnLabel: muteBtn.getAttribute('aria-label')
        };

        resolve({ stateBeforeClick, stateAfterClick, btnLabelBefore });
      }, 3000);
    });
  });
  console.log('CLICK MUTE BUTTON:', JSON.stringify(clickMuteButton, null, 2));

  // Check what the mute button's click handler does
  const muteButtonHandler = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };

    const muteBtn = Array.from(iframeDoc.querySelectorAll('button')).find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    // Check if button has onclick or event listeners
    const outerHTML = muteBtn.outerHTML;
    const hasOnClick = muteBtn.onclick !== null;
    const id = muteBtn.id;
    const classes = muteBtn.className;

    return {
      outerHTML,
      hasOnClick,
      id,
      classes,
      ariaLabel: muteBtn.getAttribute('aria-label')
    };
  });
  console.log('MUTE BUTTON HANDLER:', JSON.stringify(muteButtonHandler, null, 2));

  // Check what functions are called when mute button is clicked
  const interceptClickHandler = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    // Reset audio first
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    const muteBtn = Array.from(iframeDoc.querySelectorAll('button')).find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    // Intercept addEventListener
    const origAddEventListener = Element.prototype.addEventListener;
    const clickHandlers = [];

    Element.prototype.addEventListener = function(type, handler, options) {
      if (type === 'click' && this === muteBtn) {
        clickHandlers.push(handler.toString().slice(0, 200));
      }
      return origAddEventListener.call(this, type, handler, options);
    };

    // Also try getEventListeners from devtools style if available

    muteBtn.click();

    return {
      clickHandlers,
      audioMuted: audio.muted,
      audioVolume: audio.volume
    };
  });
  console.log('INTERCEPT CLICK HANDLER:', JSON.stringify(interceptClickHandler, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });