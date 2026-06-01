const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Navigate to Studio
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get iframe element
  const iframe = await page.$('iframe');
  if (!iframe) {
    console.log('NO IFRAME FOUND');
    await browser.close();
    return;
  }

  const iframeSrc = await iframe.getAttribute('src');
  console.log('IFRAME SRC:', iframeSrc);

  // Try to access iframe content
  const frameHandle = await page.frameLocator('iframe').first();

  // Check audio inside iframe
  const iframeAudios = await frameHandle.evaluate(() => {
    return Array.from(document.querySelectorAll('audio')).map((a, i) => ({
      i,
      id: a.id,
      src: a.src,
      currentSrc: a.currentSrc,
      duration: a.duration,
      currentTime: a.currentTime,
      paused: a.paused,
      muted: a.muted,
      volume: a.volume,
      readyState: a.readyState,
      networkState: a.networkState,
      error: a.error ? { code: a.error.code, message: a.error.message } : null
    }));
  });
  console.log('IFRAME AUDIOS:', JSON.stringify(iframeAudios, null, 2));

  // Check audio element parent and location
  const audioDetails = await frameHandle.evaluate(() => {
    const audio = document.querySelector('audio#voiceover') || document.querySelector('audio');
    if (!audio) return { error: 'no audio found' };
    return {
      id: audio.id,
      src: audio.src,
      currentSrc: audio.currentSrc,
      parent: audio.parentElement.tagName + '#' + audio.parentElement.id,
      grandparent: audio.parentElement.parentElement?.tagName + '#' + audio.parentElement.parentElement?.id,
      duration: audio.duration,
      muted: audio.muted,
      volume: audio.volume,
      readyState: audio.readyState,
      networkState: audio.networkState,
      error: audio.error ? { code: audio.error.code } : null
    };
  });
  console.log('AUDIO DETAILS:', JSON.stringify(audioDetails, null, 2));

  // Check if there's a play control in the iframe
  const playControls = await frameHandle.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    return buttons.map(b => ({ text: b.textContent?.trim(), ariaLabel: b.getAttribute('aria-label'), class: b.className })).slice(0, 10);
  });
  console.log('PLAY CONTROLS:', JSON.stringify(playControls, null, 2));

  // Click play in the iframe
  const playBtn = await frameHandle.$('button[aria-label*="play"], [class*="play"], [class*="Play"]');
  if (playBtn) {
    console.log('Clicking play button inside iframe');
    await playBtn.click();
    await page.waitForTimeout(2000);
  }

  // Check audio state after play
  const afterPlay = await frameHandle.evaluate(() => {
    const audio = document.querySelector('audio#voiceover') || document.querySelector('audio');
    if (!audio) return { error: 'no audio found' };
    return {
      id: audio.id,
      src: audio.currentSrc || audio.src,
      duration: audio.duration,
      currentTime: audio.currentTime,
      paused: audio.paused,
      muted: audio.muted,
      volume: audio.volume,
      readyState: audio.readyState,
      error: audio.error ? { code: audio.error.code } : null
    };
  });
  console.log('AFTER PLAY:', JSON.stringify(afterPlay, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });