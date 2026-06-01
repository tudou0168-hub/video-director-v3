const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Verify audio state before play
  const beforePlay = await page.evaluate(() => {
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

    return {
      audioAttrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])),
      rootDataDuration: root?.getAttribute('data-duration'),
      compDuration: iframeWin.__compositions?.['audio-driven-preview']?.duration,
      playerDuration: player.getDuration ? player.getDuration() : null,
      audioDuration: audio.duration
    };
  });
  console.log('BEFORE PLAY:', JSON.stringify(beforePlay, null, 2));

  // Play for 5 seconds
  const playResult = await page.evaluate(() => {
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
          currentTime: audio.currentTime,
          paused: audio.paused,
          playerIsPlaying: player.isPlaying()
        });
      }, 5000);
    });
  });
  console.log('PLAY RESULT (5s):', JSON.stringify(playResult, null, 2));
  console.log(playResult.muted === false ? 'PASS: audio unmuted' : 'FAIL: muted=' + playResult.muted);

  // Check scenes
  const sceneCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    return ['scene01','scene02','scene03','scene04','scene05','scene06'].map(id => ({
      id,
      exists: !!iframeDoc.getElementById(id)
    }));
  });
  console.log('SCENES:', sceneCheck.every(s => s.exists) ? 'ALL EXIST' : 'MISSING');

  await browser.close();
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });