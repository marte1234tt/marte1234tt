// node --test canal/tests/efectos.test.mjs
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const cfgBase = (escenas) => ({ total: 10, cuenta: '@nolosabias672', etiqueta: '¿NO LO SABÍAS?', personaje: 'pulpo',
  encuesta: ['A', 'B', 'C', 'D'], escenas });
let browser;
before(async () => { browser = await chromium.launch(); });
after(async () => { await browser.close(); });

async function pagina(cfg) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const errores = [], avisos = [];
  p.on('pageerror', e => errores.push(String(e)));
  p.on('console', m => { if (m.type() === 'warning') avisos.push(m.text()); });
  await p.goto('file://' + path.join(RAIZ, 'efectos', 'pagina.html') + '?personaje=' + cfg.personaje);
  await p.evaluate(() => window.LISTO);
  await p.evaluate(c => init(c), cfg);
  return { p, errores, avisos };
}

test('sin errores de página con todos los efectos', async () => {
  const todos = [
    { tipo: 'entrada' }, { tipo: 'antenas', hasta: 1 }, { tipo: 'iconos', forma: 'corazon', n: 3, pos: [200, 600] },
    { tipo: 'senalar', extremidad: 7, objetivo: [900, 1100], hasta: 3 }, { tipo: 'mirar', x: 'vaiven' },
    { tipo: 'rayosX' }, { tipo: 'organo', id: 'corazon_izq' }, { tipo: 'organo', id: 'cerebro' }, { tipo: 'latido', velocidad: 2 },
    { tipo: 'flujo', color: '#5AA2FF' }, { tipo: 'luces' }, { tipo: 'agitar', intensidad: 1.8 },
    { tipo: 'etiqueta', texto: 'HOLA', ancla: 'corazon_izq', pos: [170, 500] },
    { tipo: 'comparacion', izq: { forma: 'gota', color: '#E63946', texto: 'A', sub: 'B' }, der: { forma: 'gota', color: '#3A86FF', texto: 'C', sub: 'D' }, desde_der: 1 },
    { tipo: 'bocadillo', texto: '¡Hola!', pos: [330, 560] }, { tipo: 'contador', numero: 3, etiqueta: 'X' },
  ];
  const segunda = [{ tipo: 'objeto', forma: 'cangrejo', pos: [900, 1230], entra: 'derecha', asustado: 1 },
    { tipo: 'alcanzar', extremidad: 7, objetivo: 'objeto' }, { tipo: 'saborear', extremidad: 7 },
    { tipo: 'gris', hasta: 1 }, { tipo: 'camuflaje', colores: ['#FF7F50', '#3BB273'], desde: 1 },
    { tipo: 'aplastar', escala: 0.62 }, { tipo: 'encuesta' }, { tipo: 'cierre' }];
  const cfg = cfgBase([{ titulo: 'UNO', start: 0, dur: 5, efectos: todos }, { titulo: 'DOS', start: 5, dur: 5, efectos: segunda }]);
  const { p, errores } = await pagina(cfg);
  for (let i = 0; i < 20; i++) await p.evaluate(T => render(T), i * 0.5);
  assert.deepEqual(errores, []);
  await p.close();
});

test('título largo cabe en 1000 px', async () => {
  const { p } = await pagina(cfgBase([{ titulo: '¿CEREBRO EN LOS BRAZOS? ¡INCREÍBLE!', start: 0, dur: 10, efectos: [] }]));
  await p.evaluate(() => render(2));
  const w = await p.evaluate(() => document.getElementById('title').getBBox().width);
  assert.ok(w <= 1000, `ancho ${w}`);
  await p.close();
});

test('texto especial se muestra literal', async () => {
  const raro = '<b>&"{}"';
  const { p, errores } = await pagina(cfgBase([{ titulo: 'X', start: 0, dur: 10, efectos: [{ tipo: 'etiqueta', texto: raro, pos: [540, 700] }] }]));
  await p.evaluate(() => render(2));
  const hay = await p.evaluate(r => [...document.querySelectorAll('#overlay text')].some(t => t.textContent === r), raro);
  assert.ok(hay); assert.deepEqual(errores, []);
  await p.close();
});

test('etiqueta inferior no pisa los subtítulos', async () => {
  const { p } = await pagina(cfgBase([{ titulo: 'X', start: 0, dur: 10, efectos: [{ tipo: 'etiqueta', texto: 'ABAJO', pos: [540, 1500] }] }]));
  await p.evaluate(() => render(2));
  const bottom = await p.evaluate(() => Math.max(...[...document.querySelectorAll('#overlay g')].map(g => g.getBoundingClientRect().bottom)));
  assert.ok(bottom <= 1445, `bottom ${bottom}`);
  await p.close();
});

test('efecto desconocido avisa sin romper', async () => {
  const { p, errores, avisos } = await pagina(cfgBase([{ titulo: 'X', start: 0, dur: 10, efectos: [{ tipo: 'zzz' }] }]));
  await p.evaluate(() => render(1));
  assert.deepEqual(errores, []);
  assert.ok(avisos.some(a => a.includes('zzz')));
  await p.close();
});
