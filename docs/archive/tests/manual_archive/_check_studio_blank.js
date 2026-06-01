const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Load the blank template to compare audio setup
  await page.goto('http://localhost:3002/#project/blank?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Inspect audio in blank template
  const blankAudio = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const player = iframe.contentWindow.__player;
    const audios = Array.from(iframeDoc.querySelectorAll('audio'));
    const htmlContent = iframeDoc.documentElement.outerHTML.slice(0, 2000);
    return {
      audioCount: audios.length,
      audioInfos: audios.map(a => ({
        id: a.id,
        src: a.src,
        currentSrc: a.currentSrc,
        attributes: Array.from(a.attributes).map(attr => ({ name: attr.name, value: attr.value })),
        muted: a.muted,
        volume: a.volume,
        paused: a.paused,
        readyState: a.readyState,
        duration: a.duration
      })),
      playerExists: !!player,
      playerKeys: player ? Object.keys(player).slice(0, 15) : null,
      htmlPreview: htmlContent
    };
  });
  console.log('BLANK TEMPLATE AUDIO:', JSON.stringify(blankAudio, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });