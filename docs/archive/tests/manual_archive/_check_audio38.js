const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  // Test WITHOUT tv=1 to see if mute still happens
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1');
  await page.waitForTimeout(3000);

  const testWithoutTV = await page.evaluate(() => {
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

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          url: location.href
        });
      }, 3000);
    });
  });
  console.log('WITHOUT TV=1:', JSON.stringify(testWithoutTV, null, 2));

  // Now test WITH tv=1
  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  const testWithTV = await page.evaluate(() => {
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

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return new Promise(resolve => {
      iframeWin.setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          url: location.href
        });
      }, 3000);
    });
  });
  console.log('WITH TV=1:', JSON.stringify(testWithTV, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });