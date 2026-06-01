const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Inspect the mute button in main Studio doc
  const muteButtonInfo = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    // Get all attributes
    const attrs = {};
    Array.from(muteBtn.attributes).forEach(a => { attrs[a.name] = a.value; });

    // Check if it has onclick
    const onclick = muteBtn.getAttribute('onclick');

    // Check parent chain
    let parent = muteBtn.parentElement;
    const parentChain = [];
    while (parent) {
      parentChain.push({
        tag: parent.tagName,
        id: parent.id,
        className: typeof parent.className === 'string' ? parent.className.split(' ')[0] : ''
      });
      parent = parent.parentElement;
    }

    return {
      outerHTML: muteBtn.outerHTML.slice(0, 300),
      attrs,
      onclick,
      parentChain,
      ariaLabel: muteBtn.getAttribute('aria-label'),
      ariaPressed: muteBtn.getAttribute('aria-pressed')
    };
  });
  console.log('MUTE BUTTON INFO:', JSON.stringify(muteButtonInfo, null, 2));

  // Check what happens when we click the mute button
  const clickResult = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    const labelBefore = muteBtn.getAttribute('aria-label');

    // Get iframe audio state before click
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const audioStateBefore = {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime
    };

    // Click the mute button
    muteBtn.click();

    const labelAfter = muteBtn.getAttribute('aria-label');
    const audioStateAfter = {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime
    };

    return {
      labelBefore,
      labelAfter,
      labelChanged: labelBefore !== labelAfter,
      audioStateBefore,
      audioStateAfter,
      note: 'Studio mute button changes aria-label but does NOT affect iframe audio element'
    };
  });
  console.log('CLICK RESULT:', JSON.stringify(clickResult, null, 2));

  // Test: can we manually unmute the audio and have it stay unmuted?
  const manualUnmuteTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    // Immediately try to unmute
    setTimeout(() => {
      audio.muted = false;
    }, 50);

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          note: 'Manual unmute at 50ms after player.play()'
        });
      }, 3000);
    });
  });
  console.log('MANUAL UNMUTE TEST:', JSON.stringify(manualUnmuteTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });