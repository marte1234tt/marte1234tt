// Renderiza los fotogramas de un vídeo con Chromium en paralelo.
// Uso: node motor/render.js <config.json> <dir_salida> [procesos=4]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');

const PAGINA = path.resolve(__dirname, '..', 'efectos', 'pagina.html');
const FPS = 30;

function url(cfg) {
  const q = new URLSearchParams({ personaje: cfg.personaje || 'pulpo' });
  if (cfg.js) q.set('js', 'file://' + cfg.js);
  return 'file://' + PAGINA + '?' + q.toString();
}

async function abrir(browser, cfg) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  p.avisos = [];
  p.on('pageerror', e => { console.error('ERROR DE PÁGINA', e); process.exit(1); });
  p.on('console', m => { if (m.type() === 'warning' || m.type() === 'error') { if (!p.avisos.includes(m.text())) { p.avisos.push(m.text()); console.error('AVISO_PAGINA ' + m.text()); } } });
  await p.goto(url(cfg));
  await p.evaluate(() => window.LISTO);
  await p.evaluate(c => init(c), cfg);
  return p;
}

async function main() {
  const [cfgPath, outDir, nW = '4'] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  const total = Math.round(cfg.total * FPS), W = +nW, per = Math.ceil(total / W);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  await Promise.all([...Array(W).keys()].map(async w => {
    const p = await abrir(browser, cfg), a = w * per, b = Math.min(total, a + per);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', path.join(outDir, `parte${w}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      await p.evaluate(t => render(t), f / FPS);
      const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }));
  fs.writeFileSync(path.join(outDir, 'partes.txt'), [...Array(W).keys()].map(w => `file '${path.resolve(outDir, `parte${w}.mp4`)}'`).join('\n') + '\n');
  await browser.close();
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
module.exports = { abrir, url };
