const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check player.play source to understand what I is
  const playSource = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    if (!player) return { error: 'no player' };

    const src = player.play.toString();

    // Find all variable declarations in the play function
    const letVars = src.match(/let\s+(\w+)/g) || [];
    const constVars = src.match(/const\s+(\w+)/g) || [];

    // Find I usage patterns
    const iUsages = src.match(/I\.\w+/g) || [];

    // Find what calls I.play
    const iPlayCalls = src.match(/I\.play\(/g) || [];

    // Check for I = or let I
    const iDeclaration = src.match(/let\s+I\b|const\s+I\b|var\s+I\b/g) || [];

    // Find the I.play() line
    const lines = src.split('\n');
    const iPlayLine = lines.find(l => l.includes('I.play'));

    return {
      srcLength: src.length,
      letVars: letVars.map(v => v.replace('let ', '')),
      constVars: constVars.map(v => v.replace('const ', '')),
      iUsages: [...new Set(iUsages)],
      iPlayCalls: iPlayCalls.length,
      iDeclaration,
      iPlayLine: iPlayLine ? iPlayLine.trim() : null,
      fullSource: src
    };
  });
  console.log('PLAY SOURCE:', JSON.stringify({
    srcLength: playSource.srcLength,
    letVars: playSource.letVars,
    constVars: playSource.constVars,
    iUsages: playSource.iUsages,
    iPlayCalls: playSource.iPlayCalls,
    iDeclaration: playSource.iDeclaration,
    iPlayLine: playSource.iPlayLine
  }, null, 2));

  // Now do a fresh test - reset audio, call player.play, immediately check
  const freshTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    const stateBefore = {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime
    };

    // Call player.play()
    player.play();

    // IMMEDIATELY check (before any async)
    const stateAfterPlay = {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime,
      paused: audio.paused
    };

    return { stateBefore, stateAfterPlay };
  });
  console.log('FRESH TEST:', JSON.stringify(freshTest, null, 2));

  // Wait and check again
  await page.waitForTimeout(1000);

  const afterWait = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime,
      paused: audio.paused
    };
  });
  console.log('AFTER WAIT:', JSON.stringify(afterWait, null, 2));

  // Most critical test: call player.play() and see if we can catch where muted=true happens
  const stepByStep = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const player = iframeWin.__player;

    // Store original play
    const origPlay = player.play.bind(player);

    // Intercept at the very first line of play
    let callCount = 0;
    player.play = function() {
      callCount++;
      console.log('player.play called, count:', callCount);
      return origPlay();
    };

    // Now also intercept on the audio element
    const origMutedGet = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted').get;
    const origMutedSet = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'muted').set;

    let muteSetLog = [];
    Object.defineProperty(HTMLMediaElement.prototype, 'muted', {
      get() {
        return origMutedGet.call(this);
      },
      set(val) {
        muteSetLog.push({ value: val, time: performance.now(), stack: new Error().stack });
        console.log('MUTED SET TO:', val, 'by caller');
        return origMutedSet.call(this, val);
      }
    });

    // Reset audio
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;

    // Call player.play()
    player.play();

    return {
      callCount,
      muteSetLog,
      audioMutedAfterPlay: audio.muted
    };
  });
  console.log('STEP BY STEP:', JSON.stringify(stepByStep, null, 2));

  await page.waitForTimeout(500);

  const finalState = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    return {
      muted: audio.muted,
      volume: audio.volume,
      currentTime: audio.currentTime
    };
  });
  console.log('FINAL STATE:', JSON.stringify(finalState, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });