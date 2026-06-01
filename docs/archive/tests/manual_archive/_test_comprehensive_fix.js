const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test 1: Audio state after 5 seconds
  const test1 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
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
          muted: audio.muted,
          volume: audio.volume,
          currentTime: Math.round(audio.currentTime * 10) / 10,
          paused: audio.paused,
          playerIsPlaying: player.isPlaying()
        });
      }, 5000);
    });
  });
  console.log('TEST 1 (5s play):', JSON.stringify(test1));
  console.log(test1.muted === false && test1.currentTime > 0 ? 'PASS' : 'FAIL');

  // Test 2: Pause and resume
  const test2 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    player.pause();
    const t1 = audio.currentTime;
    const wasPaused = audio.paused;
    player.play();
    const t2 = audio.currentTime;
    const nowPlaying = !audio.paused;

    return { wasPaused, nowPlaying, t1: Math.round(t1*10)/10, t2: Math.round(t2*10)/10 };
  });
  console.log('TEST 2 (pause/resume):', JSON.stringify(test2));
  console.log(test2.wasPaused && test2.nowPlaying ? 'PASS' : 'FAIL');

  // Test 3: All 6 scenes exist
  const test3 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const scenes = ['scene01','scene02','scene03','scene04','scene05','scene06'];
    const exists = scenes.map(id => ({ id, exists: !!iframeDoc.getElementById(id) }));
    return { exists, allExist: exists.every(s => s.exists) };
  });
  console.log('TEST 3 (scenes):', JSON.stringify(test3));
  console.log(test3.allExist ? 'PASS' : 'FAIL');

  // Test 4: Subtitle element exists and has text
  const test4 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const subtitle = iframeDoc.getElementById('subtitleText');
    return { exists: !!subtitle, hasText: subtitle?.textContent?.length > 0 };
  });
  console.log('TEST 4 (subtitle):', JSON.stringify(test4));
  console.log(test4.exists && test4.hasText ? 'PASS' : 'FAIL');

  // Test 5: Studio mute button still works
  const test5 = await page.evaluate(() => {
    const allButtons = Array.from(document.querySelectorAll('button'));
    const muteBtn = allButtons.find(b => {
      const label = b.getAttribute('aria-label');
      return label && label.toLowerCase().includes('mute');
    });
    if (!muteBtn) return { error: 'no mute button' };
    const labelBefore = muteBtn.getAttribute('aria-label');
    muteBtn.click();
    const labelAfter = muteBtn.getAttribute('aria-label');
    return { labelBefore, labelAfter, changed: labelBefore !== labelAfter };
  });
  console.log('TEST 5 (mute button):', JSON.stringify(test5));
  console.log(test5.changed ? 'PASS' : 'FAIL');

  // Test 6: Audio attributes are clean (R7 style)
  const test6 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const attrs = Array.from(audio.attributes).map(a => a.name);
    return {
      attrs,
      hasNoDataDuration: !attrs.includes('data-duration'),
      hasNoDataTrackIndex: !attrs.includes('data-track-index'),
      hasNoDataStart: !attrs.includes('data-start'),
      hasCorrectSrc: attrs.includes('src'),
      hasPreload: attrs.includes('preload')
    };
  });
  console.log('TEST 6 (R7 audio style):', JSON.stringify(test6));
  console.log(test6.hasNoDataDuration && test6.hasNoDataTrackIndex && test6.hasNoDataStart ? 'PASS' : 'FAIL');

  await browser.close();
  console.log('\n=== ALL TESTS COMPLETE ===');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });