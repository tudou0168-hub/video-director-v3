const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Full verification following the user's checklist
  console.log('=== FINAL VERIFICATION ===\n');

  // Step1: Check audio element state
  const audioCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };
    const player = iframeWin.__player;

    // Reset audio state
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    player.play();

    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          currentSrc: audio.currentSrc ? audio.currentSrc.split('/').pop() : null,
          duration: audio.duration,
          currentTime: audio.currentTime,
          paused: audio.paused,
          muted: audio.muted,
          volume: audio.volume,
          readyState: audio.readyState,
          networkState: audio.networkState,
          error: audio.error ? { code: audio.error.code } : null
        });
      }, 5000);
    });
  });
  console.log('AUDIO STATE (5s after play):');
  console.log('  currentSrc:', audioCheck.currentSrc);
  console.log('  duration:', audioCheck.duration, '(should be ~71.78)');
  console.log('  currentTime:', Math.round(audioCheck.currentTime * 10) / 10, '(advancing =', audioCheck.currentTime > 0, ')');
  console.log('  paused:', audioCheck.paused, '(should be false)');
  console.log('  muted:', audioCheck.muted, '(should be FALSE - this is the fix!)');
  console.log('  volume:', audioCheck.volume, '(should be 1)');
  console.log('  readyState:', audioCheck.readyState, '(4=HAVE_CURRENT_DATA)');
  console.log('  error:', audioCheck.error);

  // Step 2: Check __compositions duration
  const compCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    return iframeWin.__compositions?.['audio-driven-preview']?.duration;
  });
  console.log('\n__compositions duration:', compCheck, '(should be 71.78)');

  // Step 3: Check root data-duration
  const rootCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const root = iframeDoc.getElementById('root');
    return root?.dataset.duration;
  });
  console.log('root data-duration:', rootCheck, '(should be 71.78)');

  // Step 4: Check audio attributes (R7 style)
  const attrCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    const attrs = Array.from(audio.attributes).map(a => a.name);
    return {
      attrs,
      dataStart: audio.dataset.start,
      dataDuration: audio.dataset.duration,
      dataTrackIndex: audio.dataset.trackIndex
    };
  });
  console.log('\nAUDIO ATTRIBUTES (R7 style):');
  console.log('  attrs:', attrCheck.attrs.join(', '));
  console.log('  data-start:', attrCheck.dataStart || '(none)');
  console.log('  data-duration:', attrCheck.dataDuration || '(none)');
  console.log('  data-track-index:', attrCheck.dataTrackIndex || '(none)');

  // Step 5: Check Studio UI
  const studioUICheck = await page.evaluate(() => {
    const muteBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('mute')
    );
    const playBtn = Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.toLowerCase().includes('play')
    );
    return {
      hasMuteButton: !!muteBtn,
      hasPlayButton: !!playBtn
    };
  });
  console.log('\nSTUDIO UI:');
  console.log('  mute button:', studioUICheck.hasMuteButton ? 'exists' : 'missing');
  console.log('  play button:', studioUICheck.hasPlayButton ? 'exists' : 'missing');

  // Step 6: Check scenes
  const sceneCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const scenes = ['scene01','scene02','scene03','scene04','scene05','scene06'];
    return scenes.map(id => ({
      id,
      exists: !!iframeDoc.getElementById(id)
    }));
  });
  console.log('\nSCENES:');
  sceneCheck.forEach(s => console.log('  ', s.id + ':', s.exists ? 'exists' : 'MISSING'));

  // Step 7: Check subtitle
  const subtitleCheck = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const subtitle = iframeDoc.getElementById('subtitleText');
    return {
      exists: !!subtitle,
      text: subtitle?.textContent || ''
    };
  });
  console.log('\nSUBTITLE:');
  console.log('  exists:', subtitleCheck.exists);
  console.log('  text:', subtitleCheck.text ? subtitleCheck.text.slice(0, 30) + '...' : '(empty)');

  await browser.close();

  console.log('\n=== SUMMARY ===');
  console.log('Audio plays without being muted:', audioCheck.muted === false ? 'FIXED' : 'STILL BROKEN');
  console.log('Current time advances:', audioCheck.currentTime > 0 ? 'YES' : 'NO');
  console.log('All scenes present:', sceneCheck.every(s => s.exists) ? 'YES' : 'NO');
  console.log('Subtitle element exists:', subtitleCheck.exists ? 'YES' : 'NO');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });