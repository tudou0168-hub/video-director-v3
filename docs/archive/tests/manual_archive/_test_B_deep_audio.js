const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test B: Deep audio inspection before play
  const beforePlay = await page.evaluate(() => {
    const rows = [];

    function scan(root, label) {
      try {
        const audios = root.querySelectorAll ? Array.from(root.querySelectorAll('audio')) : [];
        audios.forEach((a, i) => {
          rows.push({
            label,
            index: i,
            id: a.id,
            src: a.src,
            currentSrc: a.currentSrc,
            duration: a.duration,
            currentTime: a.currentTime,
            paused: a.paused,
            muted: a.muted,
            volume: a.volume,
            readyState: a.readyState,
            networkState: a.networkState,
            error: a.error ? { code: a.error.code, message: a.error.message } : null
          });
        });
      } catch(e) {
        rows.push({ label, error: String(e) });
      }
    }

    scan(document, 'main');
    const iframes = Array.from(document.querySelectorAll('iframe'));
    iframes.forEach((f, idx) => {
      try {
        scan(f.contentDocument, 'iframe[' + idx + ']');
      } catch(e) {
        rows.push({ label: 'iframe[' + idx + ']', error: String(e) });
      }
    });

    return rows;
  });

  console.log('=== BEFORE PLAY ===');
  console.log('Audio elements found:', beforePlay.length);
  beforePlay.forEach(r => {
    console.log('\n---', r.label, '---');
    console.log('  id:', r.id);
    console.log('  src:', r.src ? r.src.substring(r.src.lastIndexOf('/') + 1) : null);
    console.log('  currentSrc:', r.currentSrc ? r.currentSrc.substring(r.currentSrc.lastIndexOf('/') + 1) : null);
    console.log('  duration:', r.duration);
    console.log('  currentTime:', r.currentTime);
    console.log('  paused:', r.paused);
    console.log('  muted:', r.muted);
    console.log('  volume:', r.volume);
    console.log('  readyState:', r.readyState, '(4=HAVE_CURRENT_DATA)');
    console.log('  networkState:', r.networkState, '(1=NETWORK_LOADING)');
    console.log('  error:', r.error);
  });

  // Now click play and wait 3 seconds
  const player = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    return iframeWin.__player;
  });

  await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeWin = iframe.contentWindow;
    const iframeDoc = iframe.contentDocument || iframeWin.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    audio.pause();
    audio.currentTime = 0;
    audio.muted = false;
    audio.volume = 1;
    iframeWin.__player.play();
  });

  await page.waitForTimeout(3000);

  const afterPlay = await page.evaluate(() => {
    const rows = [];
    function scan(root, label) {
      try {
        const audios = root.querySelectorAll ? Array.from(root.querySelectorAll('audio')) : [];
        audios.forEach((a, i) => {
          rows.push({
            label,
            index: i,
            id: a.id,
            src: a.src,
            currentSrc: a.currentSrc,
            duration: a.duration,
            currentTime: a.currentTime,
            paused: a.paused,
            muted: a.muted,
            volume: a.volume,
            readyState: a.readyState,
            networkState: a.networkState,
            error: a.error ? { code: a.error.code, message: a.error.message } : null
          });
        });
      } catch(e) {
        rows.push({ label, error: String(e) });
      }
    }
    scan(document, 'main');
    const iframes = Array.from(document.querySelectorAll('iframe'));
    iframes.forEach((f, idx) => {
      try {
        scan(f.contentDocument, 'iframe[' + idx + ']');
      } catch(e) {}
    });
    return rows;
  });

  console.log('\n=== AFTER PLAY (3s) ===');
  console.log('Audio elements found:', afterPlay.length);
  afterPlay.forEach(r => {
    console.log('\n---', r.label, '---');
    console.log('  id:', r.id);
    console.log('  currentTime:', r.currentTime);
    console.log('  paused:', r.paused);
    console.log('  muted:', r.muted);
    console.log('  volume:', r.volume);
    console.log('  readyState:', r.readyState);
    console.log('  networkState:', r.networkState);
    console.log('  error:', r.error);
  });

  await browser.close();
  console.log('\nDONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });