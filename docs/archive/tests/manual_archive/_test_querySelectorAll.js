const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Test: check what document.querySelectorAll("audio[data-start]") returns in current R9
  // and what D() function returns
  const checkQuerySelector = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeWin = iframe.contentWindow;
    if (!iframeWin) return { error: 'no iframeWin' };
    const iframeDoc = iframeWin.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };

    // What does querySelectorAll("audio[data-start]") return?
    const audioWithDataStart = Array.from(iframeDoc.querySelectorAll('audio[data-start]'));
    const allAudio = Array.from(iframeDoc.querySelectorAll('audio'));

    // What does D() return? D is used in player.play() to get the root element
    // Let's try to find it
    // In the player.play() source: let h=D(),b=Number(h?.getAttribute("data-duration")??0)
    // D() seems to return the root div

    // Check div#root
    const root = iframeDoc.getElementById('root');
    const rootDataDuration = root?.getAttribute('data-duration');
    const rootDataStart = root?.getAttribute('data-start');

    return {
      audioWithDataStart: audioWithDataStart.length,
      allAudio: allAudio.length,
      rootDataDuration,
      rootDataStart,
      rootTagName: root?.tagName,
      rootId: root?.id
    };
  });
  console.log('QUERY SELECTOR CHECK:', JSON.stringify(checkQuerySelector, null, 2));

  // Now test: what happens if we change root data-duration to 71.78 AND remove audio data-duration?
  const testR7Style = await page.evaluate(() => {
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

    // R7 style: remove all data-* from audio, keep only id/preload/src
    audio.removeAttribute('data-duration');
    audio.removeAttribute('data-start');
    audio.removeAttribute('data-track-index');

    // R7 style: root has no data-duration either
    if (root) root.removeAttribute('data-duration');

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
          audioAttrs: Object.fromEntries(Array.from(audio.attributes).map(a => [a.name, a.value])),
          rootAttrs: root ? Object.fromEntries(Array.from(root.attributes).map(a => [a.name, a.value])) : null,
          playerDuration: player.getDuration ? player.getDuration() : null
        });
      }, 4000);
    });
  });
  console.log('R7 STYLE TEST:', JSON.stringify(testR7Style, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });