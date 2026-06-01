const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Find and click mute button in main doc
  const clickMuteButton = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    const labelBefore = muteBtn.getAttribute('aria-label');

    // Click mute button
    muteBtn.click();

    const labelAfter = muteBtn.getAttribute('aria-label');

    // Check iframe audio state
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    return {
      labelBefore,
      labelAfter,
      audioMuted: audio.muted,
      audioVolume: audio.volume
    };
  });
  console.log('CLICK MUTE BUTTON:', JSON.stringify(clickMuteButton, null, 2));

  // Click again to toggle back
  const clickAgain = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });

    if (!muteBtn) return { error: 'no mute button' };

    muteBtn.click();

    const labelAfter = muteBtn.getAttribute('aria-label');
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');

    return {
      labelAfter,
      audioMuted: audio.muted
    };
  });
  console.log('CLICK AGAIN:', JSON.stringify(clickAgain, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });