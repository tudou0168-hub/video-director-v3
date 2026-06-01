const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test 1: Audio stays unmuted for5 seconds
  const unmutedTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          muted: audio.muted,
          volume: audio.volume,
          currentTime: audio.currentTime,
          paused: audio.paused
        });
      }, 5000);
    });
  });
  console.log('UNMUTED TEST (5s):', JSON.stringify(unmutedTest, null, 2));

  // Test 2: Studio UI still works - check if scenes are visible
  const scenesTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };

    const scenes = ['scene01', 'scene02', 'scene03', 'scene04', 'scene05', 'scene06'];
    const visibleScenes = scenes.filter(id => {
      const el = iframeDoc.getElementById(id);
      return el && el.style.display !== 'none';
    });

    return { visibleScenes };
  });
  console.log('SCENES TEST:', JSON.stringify(scenesTest, null, 2));

  // Test 3: Check subtitle element exists
  const subtitleTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const subtitle = iframeDoc.getElementById('subtitleText');
    return { exists: !!subtitle, text: subtitle?.textContent };
  });
  console.log('SUBTITLE TEST:', JSON.stringify(subtitleTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });