// Portada 1080×1920 del vídeo: el personaje en su momento más llamativo y el titular grande.
// Uso: node motor/portada.js <config.json> <portada.png>
const { chromium } = require('playwright');
const fs = require('fs');
const { abrir } = require('./render.js');

(async () => {
  const [cfgPath, out] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  const por = cfg.portada || {};
  const T = por.T ?? cfg.total * 0.3;
  const browser = await chromium.launch();
  const p = await abrir(browser, cfg);
  await p.evaluate(({ T, por }) => {
    render(T);
    const svg = document.getElementById('s');
    document.getElementById('overlay').innerHTML = '';
    document.getElementById('titleG').style.display = 'none';
    const marca = document.getElementById('marca');
    marca.children[0].style.display = 'none'; marca.children[1].style.display = 'none';  // barra de progreso
    marca.children[2].setAttribute('transform', 'translate(540,300)');
    const P = Personaje.estadoInicial(T); P.s = (P.s || .95) * 1.3; P.y = 1130;
    document.getElementById('oct').setAttribute('transform', `translate(540,1130) scale(${P.s})`);
    const texto = (txt, y, size, fill) => { if (!txt) return; const t = el('text', { x: 540, y, 'text-anchor': 'middle', 'font-size': size, 'font-weight': 900, fill, stroke: '#0B1320', 'stroke-width': size * .16, 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, svg); t.textContent = txt; while (t.getComputedTextLength() > 1000 && size > 50) { size -= 6; t.setAttribute('font-size', size); t.setAttribute('stroke-width', size * .16); } };
    const l1 = por.linea1 || (escenaEn(T).titulo || '');
    texto(l1, 480, 150, '#FFFFFF');
    texto(por.linea2, 630, 150, por.color2 || '#FFD23F');
    if (por.banda) {
      const g = el('g', { transform: 'translate(540,1560) rotate(-3)' }, svg);
      const r = el('rect', { y: -70, height: 140, rx: 30, fill: por.color_banda || '#3A86FF' }, g);
      const t = el('text', { y: 30, 'text-anchor': 'middle', 'font-size': 84, 'font-weight': 900, fill: '#fff' }, g); t.textContent = por.banda;
      const w = Math.min(1000, t.getComputedTextLength() + 120); r.setAttribute('x', -w / 2); r.setAttribute('width', w);
    }
  }, { T, por });
  await p.screenshot({ path: out });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
