const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/blank?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  const blankInfo = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    const audios = Array.from(document.querySelectorAll('audio'));
    const player = window.__player;
    return {
      iframeCount: iframes.length,
      audioCount: audios.length,
      playerExists: !!player,
      playerKeys: player ? Object.keys(player).slice(0, 15) : null
    };
  });
  console.log('BLANK INFO:', JSON.stringify(blankInfo, null, 2));

  const mainDocAudio = await page.evaluate(() => {
    const allAudios = Array.from(document.querySelectorAll('audio'));
    return allAudios.map(a => ({
      id: a.id,
      src: a.src,
      muted: a.muted,
      volume: a.volume,
      paused: a.paused,
      duration: a.duration,
      readyState: a.readyState,
      parent: a.parentElement ? a.parentElement.tagName + (a.parentElement.id ? '#'+a.parentElement.id : '') : 'N/A'
    }));
  });
  console.log('MAIN DOC AUDIO:', JSON.stringify(mainDocAudio, null, 2));

  // Check what URL the blank project maps to
  const projectUrl = page.url();
  console.log('PROJECT URL:', projectUrl);

  // Check if there's an iframe with the preview
  const iframeInfo = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return iframes.map((f, i) => ({
      index: i,
      id: f.id,
      src: f.src ? f.src.substring(0, 100) : null,
      width: f.width,
      height: f.height
    }));
  });
  console.log('IFRAMES:', JSON.stringify(iframeInfo, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });