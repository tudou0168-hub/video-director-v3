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

  // Access iframe using frame()
  const frame = page.frame({ url: /preview\/comp/ });
  if (!frame) {
    console.log('FRAME NOT FOUND via url');
    // Try by name/index
    const frames = page.frames();
    console.log('All frames:', frames.map(f => ({ url: f.url(), name: f.name() })));
  } else {
    console.log('Found frame by url');

    // Check audio inside iframe
    const iframeAudios = await frame.evaluate(() => {
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

    // Check audio element details
    const audioDetails = await frame.evaluate(() => {
      const audio = document.querySelector('audio#voiceover') || document.querySelector('audio');
      if (!audio) return { error: 'no audio found' };
      return {
        id: audio.id,
        src: audio.src,
        currentSrc: audio.currentSrc,
        parent: audio.parentElement.tagName + '#' + (audio.parentElement.id || audio.parentElement.className),
        duration: audio.duration,
        muted: audio.muted,
        volume: audio.volume,
        readyState: audio.readyState,
        networkState: audio.networkState,
        error: audio.error ? { code: a.error.code } : null
      };
    });
    console.log('AUDIO DETAILS:', JSON.stringify(audioDetails, null, 2));

    // Click play button inside iframe
    const buttons = await frame.$$('button');
    console.log('BUTTONS IN IFRAME:', buttons.length);
    for (const btn of buttons.slice(0, 5)) {
      const txt = await btn.textContent();
      const aria = await btn.getAttribute('aria-label');
      console.log('  button:', JSON.stringify({ text: txt?.trim(), ariaLabel: aria }));
    }

    const playBtn = await frame.$('button[aria-label*="play"], [class*="play"], [class*="Play"]');
    if (playBtn) {
      console.log('Clicking play button...');
      await playBtn.click();
      await page.waitForTimeout(2000);

      // Check audio state after play
      const afterPlay = await frame.evaluate(() => {
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
          readyState: audio.readyState
        };
      });
      console.log('AFTER PLAY AUDIO:', JSON.stringify(afterPlay, null, 2));
    } else {
      console.log('No play button found');
    }
  }

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });