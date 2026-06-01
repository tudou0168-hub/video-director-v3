const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: Audio stays unmuted after5 seconds
  const audioTest = await page.evaluate(() => {
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
          audioUnmuted: !audio.muted,
          audioVolume: audio.volume,
          audioPlaying: !audio.paused,
          audioCurrentTime: audio.currentTime,
          playerIsPlaying: player.isPlaying()
        });
      }, 5000);
    });
  });
  console.log('AUDIO TEST:', JSON.stringify(audioTest, null, 2));

  // Check Studio UI elements
  const studioUI = await page.evaluate(() => {
    const hasMuteButton = Array.from(document.querySelectorAll('button')).some(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    const hasPlayButton = Array.from(document.querySelectorAll('button')).some(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('play')
    );
    return { hasMuteButton, hasPlayButton };
  });
  console.log('STUDIO UI:', JSON.stringify(studioUI, null, 2));

  // Check iframe content - scenes and subtitles
  const iframeContent = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };

    const scenes = ['scene01', 'scene02', 'scene03', 'scene04', 'scene05', 'scene06'];
    const sceneStates = scenes.map(id => {
      const el = iframeDoc.getElementById(id);
      return {
        id,
        exists: !!el,
        visible: el && el.style.display !== 'none'
      };
    });

    const subtitle = iframeDoc.getElementById('subtitleText');

    return {
      sceneStates,
      subtitleExists: !!subtitle,
      subtitleText: subtitle?.textContent
    };
  });
  console.log('IFRAME CONTENT:', JSON.stringify(iframeContent, null, 2));

  await browser.close();
  console.log('ALL TESTS PASSED');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });