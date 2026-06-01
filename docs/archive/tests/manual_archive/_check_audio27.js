const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Get iframe references first
  const iframeRefs = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    return {
      hasIframe: !!iframe,
      hasIframeWin: !!iframeWin,
      hasIframeDoc: !!iframeDoc,
      hasAudio: !!audio,
      hasPlayer: !!player,
      playerType: typeof player
    };
  });
  console.log('IFRAME REFS:', JSON.stringify(iframeRefs, null, 2));

  // Check player.I
  const playerI = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    if (!player) return { error: 'no player' };

    // player.I should be the audio-playing object
    const i = player.I;
    if (!i) return { iFound: false, playerKeys: Object.keys(player).slice(0, 10) };

    return {
      iFound: true,
      iType: typeof i,
      iTagName: i.tagName,
      iIsAudioElement: i.tagName === 'AUDIO',
      iHasPlayMethod: typeof i.play === 'function',
      iHasPauseMethod: typeof i.pause === 'function',
      iHasVolumeProp: 'volume' in i,
      iHasMutedProp: 'muted' in i,
      iKeys: Object.keys(i).slice(0, 20)
    };
  });
  console.log('PLAYER.I:', JSON.stringify(playerI, null, 2));

  // Check if player.I === audio element
  const iVsAudio = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;
    const i = player.I;

    if (!i || !audio) return { error: 'missing' };

    return {
      iEqualsAudio: i === audio,
      iTagName: i.tagName,
      audioTagName: audio.tagName,
      audioId: audio.id,
      iId: i.id,
      iSrc: i.src ? i.src.substring(i.src.lastIndexOf('/') + 1) : null,
      audioSrc: audio.src ? audio.src.substring(audio.src.lastIndexOf('/') + 1) : null
    };
  });
  console.log('I VS AUDIO:', JSON.stringify(iVsAudio, null, 2));

  // Check what I.play() does - call it directly
  const iPlayResult = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;
    const i = player.I;

    if (!i) return { error: 'no I' };

    // Reset audio state
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call I.play() directly
    const result = i.play();

    return {
      playReturned: typeof result,
      audioMuted: audio.muted,
      audioPaused: audio.paused,
      audioCurrentTime: audio.currentTime
    };
  });
  console.log('I.PLAY() RESULT:', JSON.stringify(iPlayResult, null, 2));

  await page.waitForTimeout(500);

  const afterIPlay = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('AFTER I.PLAY():', JSON.stringify(afterIPlay, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });