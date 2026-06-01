const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Navigate to Studio
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check for iframes
  const iframes = await page.evaluate(() => {
    const frames = Array.from(document.querySelectorAll('iframe'));
    return frames.map(f => ({ id: f.id, src: f.src, name: f.name }));
  });
  console.log('IFRAMES:', JSON.stringify(iframes));

  // Check for audio elements in main document
  const mainAudios = await page.evaluate(() => {
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
  console.log('MAIN AUDIOS:', JSON.stringify(mainAudios));

  // Check all audio elements including in shadow/iframe
  const allAudios = await page.evaluate(() => {
    const result = [];

    // Main doc
    document.querySelectorAll('audio').forEach((a, i) => {
      result.push({ scope: 'main', i, id: a.id, src: a.src, currentSrc: a.currentSrc, duration: a.duration, paused: a.paused, muted: a.muted, volume: a.volume });
    });

    // All iframes
    document.querySelectorAll('iframe').forEach((f, fi) => {
      try {
        const ifrDoc = f.contentDocument || f.contentWindow?.document;
        if (ifrDoc) {
          ifrDoc.querySelectorAll('audio').forEach((a, i) => {
            result.push({ scope: 'iframe-' + fi, i, id: a.id, src: a.src, currentSrc: a.currentSrc, duration: a.duration, paused: a.paused, muted: a.muted, volume: a.volume });
          });
        }
      } catch(e) {
        result.push({ scope: 'iframe-' + fi + '-error', msg: e.message });
      }
    });

    // Deep nested
    document.querySelectorAll('*').forEach(el => {
      if (el.shadowRoot) {
        el.shadowRoot.querySelectorAll('audio').forEach((a, i) => {
          result.push({ scope: 'shadow', tag: el.tagName, i, id: a.id, src: a.src, currentSrc: a.currentSrc, duration: a.duration, paused: a.paused, muted: a.muted, volume: a.volume });
        });
      }
    });

    return result;
  });
  console.log('ALL AUDIOS:', JSON.stringify(allAudios));

  // Try to click play button and re-check
  // First find if there's a play button
  const playButton = await page.$('button[aria-label*="play"], button[class*="play"], [class*="play-button"]');
  if (playButton) {
    console.log('Found play button, clicking...');
    await playButton.click();
    await page.waitForTimeout(1000);
  }

  // Check audio state again after play
  const afterPlay = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('audio')).map((a, i) => ({
      i,
      id: a.id,
      src: a.currentSrc || a.src,
      duration: a.duration,
      currentTime: a.currentTime,
      paused: a.paused,
      muted: a.muted,
      volume: a.volume,
      readyState: a.readyState,
      error: a.error ? { code: a.error.code } : null
    }));
  });
  console.log('AFTER PLAY:', JSON.stringify(afterPlay));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });