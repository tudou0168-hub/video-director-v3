const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function screenshotScene(name, htmlPath, outputPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1920 });
  await page.goto('file://' + htmlPath);
  await page.waitForTimeout(800);
  await page.screenshot({ path: outputPath, fullPage: false });
  const dims = await page.evaluate(() => ({ w: document.body.offsetWidth, h: document.body.offsetHeight }));
  const stats = fs.statSync(outputPath);
  await browser.close();
  console.log(name + ': ' + dims.w + 'x' + dims.h + ' | ' + Math.round(stats.size / 1024) + 'KB');
}

(async () => {
  const base = 'outputs/hyperframes_p26_s3_polished';
  const htmlDir = base + '/html';
  const framesDir = base + '/frames';
  const scenes = [
    ['scene_01_hook', 'scene_01_hook.html'],
    ['scene_02_pain_table', 'scene_02_pain_table.html'],
    ['scene_03_process_chain', 'scene_03_process_chain.html'],
    ['scene_04_toolflow', 'scene_04_toolflow.html'],
    ['scene_05_before_after', 'scene_05_before_after.html'],
    ['scene_06_action_list', 'scene_06_action_list.html'],
  ];
  for (const [name, file] of scenes) {
    const htmlPath = path.resolve(htmlDir, file);
    const outPath = path.resolve(framesDir, 'frame_' + name + '.png');
    await screenshotScene(name, htmlPath, outPath);
  }
  console.log('Done.');
})();