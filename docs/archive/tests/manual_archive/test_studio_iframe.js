const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Go to Studio
  const studioUrl = 'http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1';
  await page.goto(studioUrl, { waitUntil: 'load', timeout: 30000 });

  // Wait for iframe to be stable
  await page.waitForSelector('iframe', { state: 'attached', timeout: 10000 });
  await page.waitForTimeout(2000);

  // Immediately evaluate before any navigation can happen
  const iframeInfo = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return {
      count: iframes.length,
      srcs: iframes.map(f => ({ src: f.src.substring(0, 100), loaded: f.contentDocument?.readyState }))
    };
  });
  console.log('Iframe count:', iframeInfo.count);
  console.log('Iframes:', JSON.stringify(iframeInfo.srcs, null, 2));

  if (iframeInfo.count > 0) {
    // Get audio info
    const audioInfo = await page.evaluate(() => {
      try {
        const iframe = document.querySelector('iframe');
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
        const audio = iframeDoc?.querySelector('audio#voiceover') || iframeDoc?.querySelector('audio');
        const player = iframe.contentWindow?.__player;
        const root = iframeDoc?.getElementById('root');
        return {
          hasAudio: !!audio,
          audioMuted: audio?.muted,
          audioSrc: audio?.getAttribute('src')?.split('/').pop(),
          playerExists: !!player,
          rootDuration: root?.getAttribute('data-duration'),
          compId: root?.getAttribute('data-composition-id')
        };
      } catch(e) {
        return { error: e.message };
      }
    });
    console.log('Audio info:', JSON.stringify(audioInfo, null, 2));
  }

  await browser.close();
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });