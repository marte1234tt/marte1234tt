// Uso: node render.js config.json pulpo.html salida_dir [workers] [--stills t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const [cfgPath, htmlPath, outDir, nW = '4'] = process.argv.slice(2);
const stillsArg = process.argv.find(a => a.startsWith('--stills='));
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const FPS = 30, total = cfg.total, nFrames = Math.round(total * FPS);
fs.mkdirSync(outDir, { recursive: true });
async function page(browser) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  await p.goto('file://' + path.resolve(htmlPath));
  await p.evaluate(c => init(c), cfg);
  return p;
}
(async () => {
  const browser = await chromium.launch();
  if (stillsArg) {
    const p = await page(browser);
    for (const t of stillsArg.split('=')[1].split(',').map(Number)) {
      await p.evaluate(t => render(t), t);
      await p.screenshot({ path: path.join(outDir, `still_${t}.png`) });
    }
    await browser.close(); return;
  }
  const W = +nW, per = Math.ceil(nFrames / W);
  await Promise.all([...Array(W).keys()].map(async w => {
    const p = await page(browser), a = w * per, b = Math.min(nFrames, a + per);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', path.join(outDir, `parte${w}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      await p.evaluate(t => render(t), f / FPS);
      const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - a) % 300 === 0) console.log(`worker ${w}: ${f - a}/${b - a}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }));
  fs.writeFileSync(path.join(outDir, 'partes.txt'), [...Array(W).keys()].map(w => `file '${path.resolve(outDir, `parte${w}.mp4`)}'`).join('\n') + '\n');
  await browser.close();
})();
