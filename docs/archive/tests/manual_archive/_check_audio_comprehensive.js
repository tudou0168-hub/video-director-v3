const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test 1: Play audio, check stays unmuted for 8 seconds
  console.log('--- Test 1: Audio Unmuted for 8s ---');
  const test1 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          unmuted: !audio.muted,
          volume: audio.volume,
          currentTime: Math.round(audio.currentTime * 10) / 10,
          playing: !audio.paused
        });
      }, 8000);
    });
  });
  console.log('Result:', JSON.stringify(test1));
  console.log(test1.unmuted && test1.playing ? 'PASS' : 'FAIL');

  // Test 2: Pause and resume
  console.log('\n--- Test 2: Pause/Resume ---');
  const test2 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    player.pause();
    const t1 = audio.currentTime;
    const wasPaused = audio.paused;

    player.play();
    const t2 = audio.currentTime;
    const wasPlaying = !audio.paused;

    return { wasPaused, wasPlaying, t1: Math.round(t1*10)/10, t2: Math.round(t2*10)/10 };
  });
  console.log('Result:', JSON.stringify(test2));
  console.log(test2.wasPaused && test2.wasPlaying ? 'PASS' : 'FAIL');

  // Test 3: Subtitle updates
  console.log('\n--- Test 3: Subtitles ---');
  const test3 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const subtitle = iframeDoc.getElementById('subtitleText');
    return {
      hasSubtitle: !!subtitle,
      text: subtitle?.textContent || '',
      length: subtitle?.textContent?.length || 0
    };
  });
  console.log('Result:', JSON.stringify(test3));
  console.log(test3.hasSubtitle && test3.length > 0 ? 'PASS' : 'FAIL');

  // Test 4: Scenes exist and are controlled
  console.log('\n--- Test 4: Scenes ---');
  const test4 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const scenes = ['scene01','scene02','scene03','scene04','scene05','scene06'];
    const results = scenes.map(id => ({
      id,
      exists: !!iframeDoc.getElementById(id)
    }));
    const s01 = iframeDoc.getElementById('scene01');
    return { results, s01Display: s01?.style.display };
  });
  console.log('Result:', JSON.stringify(test4));
  console.log(test4.results.every(r => r.exists) ? 'PASS' : 'FAIL');

  await browser.close();
  console.log('\n=== ALL TESTS COMPLETE ===');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });