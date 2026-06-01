const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  await page.goto('http://localhost:3002/#project/hyperframes_timeline?v=1&t=5&tab=design&rc=1&tv=1');
  await page.waitForTimeout(3000);

  // Deep inspect audio element's DOM position and parent chain
  const audioDomPosition = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!iframeDoc) return { error: 'no iframeDoc' };
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    // Build parent chain
    const parentChain = [];
    let el = audio;
    while (el) {
      parentChain.push({
        tag: el.tagName,
        id: el.id,
        className: typeof el.className === 'string' ? el.className.split(' ')[0] : '',
        display: el.style.display,
        visibility: el.style.visibility
      });
      el = el.parentElement;
    }

    // Check if audio is in root
    const root = iframeDoc.getElementById('root');
    const rootChildren = root ? Array.from(root.children).map(c => c.tagName + (c.id ? '#'+c.id : '')) : [];

    // Check root wrapper
    const rootWrapper = iframeDoc.querySelector('.root-wrapper, #root, [class*="root"]');
    const rootWrapperInfo = rootWrapper ? {
      tag: rootWrapper.tagName,
      id: rootWrapper.id,
      className: rootWrapper.className
    } : null;

    return {
      parentChain,
      rootChildren,
      rootWrapperInfo,
      audioIsConnected: audio.isConnected,
      audioParentTag: audio.parentElement?.tagName,
      audioParentId: audio.parentElement?.id,
      audioParentDisplay: audio.parentElement?.style.display,
      audioTagName: audio.tagName
    };
  });
  console.log('AUDIO DOM POSITION:', JSON.stringify(audioDomPosition, null, 2));

  // Check audio element attributes and properties
  const audioDetails = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    const allAttrs = Array.from(audio.attributes).map(a => ({ name: a.name, value: a.value }));
    const audioProps = {
      id: audio.id,
      tagName: audio.tagName,
      src: audio.src,
      currentSrc: audio.currentSrc,
      preload: audio.preload,
      muted: audio.muted,
      volume: audio.volume,
      paused: audio.paused,
      currentTime: audio.currentTime,
      duration: audio.duration,
      readyState: audio.readyState,
      networkState: audio.networkState,
      autoplay: audio.autoplay,
      loop: audio.loop,
      controls: audio.controls,
      defaultMuted: audio.defaultMuted,
      defaultPlaybackRate: audio.defaultPlaybackRate,
      playbackRate: audio.playbackRate,
      error: audio.error ? audio.error.code : null,
     湖区: audio.error ? audio.error.message : null
    };

    // Check if audio is visible
    const rect = audio.getBoundingClientRect();

    return { allAttrs, audioProps, boundingRect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height } };
  });
  console.log('AUDIO DETAILS:', JSON.stringify(audioDetails, null, 2));

  // Check what's around the audio element in the HTML
  const audioHtmlContext = await page.evaluate(() => {
    const iframe = document.querySelector('iframe');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    const audio = iframeDoc.querySelector('audio#voiceover');
    if (!audio) return { error: 'no audio' };

    const outerHTML = audio.outerHTML;
    const prevElement = audio.previousElementSibling;
    const nextElement = audio.nextElementSibling;
    const parentOuterHTML = audio.parentElement?.outerHTML?.slice(0, 300);

    return {
      audioOuterHTML: outerHTML,
      prevSibling: prevElement ? prevElement.tagName + (prevElement.id ? '#'+prevElement.id : '') : null,
      nextSibling: nextElement ? nextElement.tagName + (nextElement.id ? '#'+nextElement.id : '') : null,
      parentOuterHTML
    };
  });
  console.log('AUDIO HTML CONTEXT:', JSON.stringify(audioHtmlContext, null, 2));

  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message, e.stack); process.exit(1); });