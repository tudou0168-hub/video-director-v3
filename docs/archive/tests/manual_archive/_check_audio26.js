const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=10&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Check what I is and I.play()
  const iPlayInfo = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;

    // Get player.play source to find I
    const playSrc = player.play.toString();
    // Find all variable declarations in play closure
    const varsDeclared = playSrc.match(/let\s+(\w+)/g) || [];

    // Check which of these are in scope at iframeWin level
    const foundVars = {};
    varsDeclared.forEach(v => {
      const name = v.replace('let ', '');
      if (iframeWin[name] !== undefined) {
        foundVars[name] = typeof iframeWin[name];
      }
    });

    // Get I.play source
    // I is used as: I.isPlaying(), I.setDuration(), I.play(), I.now()
    // I must be accessible from player scope

    // Find I by checking player object for properties that match
    // I has methods: isPlaying, setDuration, play, now, etc.
    const playerKeys = Object.keys(player).filter(k => !k.startsWith('_'));
    const iCandidate = player.I;
    if (iCandidate) {
      return {
        iFound: true,
        iType: typeof iCandidate,
        iKeys: typeof iCandidate === 'object' ? Object.keys(iCandidate).slice(0, 20) : null
      };
    }

    // Check if there's a getI or similar
    return { iFound: false, playerKeys: playerKeys.slice(0, 15), foundVars };
  });
  console.log('I PLAY INFO:', JSON.stringify(iPlayInfo, null, 2));

  // Check I.play source
  const iPlaySource = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;
    const i = player.I;

    if (!i) return { error: 'I not found' };

    return {
      iPlayExists: typeof i.play === 'function',
      iPlaySource: typeof i.play === 'function' ? i.play.toString().slice(0, 400) : null
    };
  });
  console.log('I PLAY SOURCE:', JSON.stringify(iPlaySource, null, 2));

  // Check if I is the actual audio-playing object
  const iAudioTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;
    const i = player.I;

    if (!i) return { error: 'I not found' };

    // Check I's audio-related properties
    const iKeys = Object.keys(i).filter(k =>
      k.toLowerCase().includes('audio') ||
      k.toLowerCase().includes('mute') ||
      k.toLowerCase().includes('volume') ||
      k.toLowerCase().includes('sound') ||
      k.toLowerCase().includes('media')
    );

    return {
      iHasAudioProps: iKeys.length > 0,
      iKeys: iKeys.slice(0, 10)
    };
  });
  console.log('I AUDIO TEST:', JSON.stringify(iAudioTest, null, 2));

  // Most importantly: check if player.I and audio element are the same
  const iVsAudioTest = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const iframeWin = iframe.contentWindow;
    const player = iframeWin.__player;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const i = player.I;

    if (!i) return { error: 'I not found' };

    // Check if I === audio
    const sameObject = i === audio;

    // Check if I has audio element properties
    const iHasAudioProps = i.tagName !== undefined;

    return {
      sameObject,
      iHasAudioProps,
      iTagName: i.tagName
    };
  });
  console.log('I VS AUDIO TEST:', JSON.stringify(iVsAudioTest, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });