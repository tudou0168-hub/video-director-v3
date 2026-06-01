const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: data-start + data-duration (NO data-track-index)
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
    const root = iframeDoc.getElementById('root');

    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-duration', '71.78');
    // NO data-track-index
    if (root) root.setAttribute('data-duration', '71.78');

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioCurrentTime: audio.currentTime,
          attrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value]))
        });
      }, 5000);
    });
  });
  console.log('TEST1 (data-start + data-duration only):', test1.audioMuted === false ? 'PASS' : 'FAIL');

  // Test: data-start + data-track-index (NO data-duration)
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
    const root = iframeDoc.getElementById('root');

    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-track-index', '0');
    // NO data-duration
    if (root) root.setAttribute('data-duration', '71.78');

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioCurrentTime: audio.currentTime
        });
      }, 5000);
    });
  });
  console.log('TEST2 (data-start + data-track-index only):', test2.audioMuted === false ? 'PASS' : 'FAIL');

  // Test: data-duration + data-track-index (NO data-start)
  const test3 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    const root = iframeDoc.getElementById('root');

    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

    audio.setAttribute('data-duration', '71.78');
    audio.setAttribute('data-track-index', '0');
    // NO data-start
    if (root) root.setAttribute('data-duration', '71.78');

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioCurrentTime: audio.currentTime
        });
      }, 5000);
    });
  });
  console.log('TEST3 (data-duration + data-track-index only):', test3.audioMuted === false ? 'PASS' : 'FAIL');

  // Test: data-start + data-track-index (NO data-duration) - already tested above, was FAIL
  // Let's try data-start + data-duration + data-track-index with DIFFERENT ORDER
  // Actually, let me check: is it data-track-index that's causing the issue?

  // Test 4: data-start + data-duration + data-track-index with data-track-index REMOVED from query
  const test4 = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;
    const root = iframeDoc.getElementById('root');

    Array.from(audio.attributes).forEach(a => {
      if (a.name.startsWith('data-')) audio.removeAttribute(a.name);
    });

    audio.setAttribute('data-start', '0');
    audio.setAttribute('data-duration', '71.78');
    audio.setAttribute('data-track-index', '0');
    if (root) root.setAttribute('data-duration', '71.78');

    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          audioMuted: audio.muted,
          audioCurrentTime: audio.currentTime,
          note: 'all three data-* attrs set'
        });
      }, 5000);
    });
  });
  console.log('TEST4 (all three):', test4.audioMuted === false ? 'PASS' : 'FAIL');

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });