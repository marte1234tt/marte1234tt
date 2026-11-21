// Caja de efectos: cada efecto del guion es {tipo, desde, hasta?, ...parámetros}.
// estado(ctx, e, td, t) modifica el personaje (ctx.P) antes de dibujarlo;
// dibujo(ctx, e, td, t) pinta encima, ya con el personaje colocado.
// td = segundos desde que empezó el efecto; t = segundos desde que empezó la escena.

const vis = (e, t, d = .35) => win(t, e.desde ?? 0, e.hasta ?? 1e9, d);

// ---------------------------------------------------------------- piezas de dibujo
function etiqueta(OV, texto, x, y, o = {}) {
  const a = o.alpha ?? 1; if (a <= .01) return;
  const fs = o.size || 46, s = o.scale ?? 1, lineas = String(texto).split("\n"), lh = fs * 1.15;
  const alto = fs * 1.5 + (lineas.length - 1) * lh;
  y = Math.min(y, Y_MAX_ETIQUETA - alto / 2 + fs * .5);
  const g = el("g", { transform: `translate(${x},${y}) scale(${s})`, opacity: a }, OV);
  const fondo = el("rect", { fill: o.fondo || "#fff" }, g);
  let w = 0;
  lineas.forEach((l, i) => {
    const t = el("text", { "text-anchor": "middle", "font-size": fs, "font-weight": 900, fill: o.color || "#0B1320", y: fs * .35 + (i - (lineas.length - 1) / 2) * lh }, g);
    t.textContent = l; w = Math.max(w, t.getComputedTextLength());
  });
  w += fs; fondo.setAttribute("x", -w / 2); fondo.setAttribute("y", -alto / 2); fondo.setAttribute("width", w); fondo.setAttribute("height", alto); fondo.setAttribute("rx", Math.min(alto / 2, fs * .75));
  return [x, y];
}
function guia(OV, x1, y1, x2, y2, a, color = "#fff") {
  if (a <= .01) return; const k = easeOut(a);
  el("line", { x1, y1, x2: lerp(x1, x2, k), y2: lerp(y1, y2, k), stroke: color, "stroke-width": 5, "stroke-dasharray": "2 12", "stroke-linecap": "round", opacity: a }, OV);
  el("circle", { cx: x1, cy: y1, r: 10, fill: color, opacity: a }, OV);
}
function forma(OV, f, x, y, tam, color, a, sc = 1) {
  if (a <= .01) return;
  const g = el("g", { transform: `translate(${x},${y}) scale(${sc})`, opacity: a }, OV);
  const d = f === "gota" ? FORMAS.gota(tam) : f === "estrella" ? FORMAS.estrella(tam) : FORMAS.corazon(tam / 50);
  el("path", { d, fill: color, stroke: "#fff", "stroke-width": 5 }, g);
  return g;
}
function cangrejo(OV, x, y, asustado) {
  const g = el("g", { transform: `translate(${x},${y})` }, OV);
  for (const sx of [-1, 1]) {
    for (let k = 0; k < 3; k++) el("line", { x1: sx * 40, y1: 10 + k * 14, x2: sx * 85, y2: 30 + k * 18, stroke: "#E85D3A", "stroke-width": 9, "stroke-linecap": "round" }, g);
    el("circle", { cx: sx * 78, cy: -38, r: 26, fill: "#FF6B42" }, g);
    el("path", { d: `M${sx * 70},-50 L${sx * 100},-62 L${sx * 92},-30 Z`, fill: "#0B1320" }, g);
    el("line", { x1: sx * 20, y1: -30, x2: sx * 24, y2: -70, stroke: "#E85D3A", "stroke-width": 7 }, g);
    el("circle", { cx: sx * 24, cy: -78, r: asustado ? 15 : 12, fill: "#fff" }, g);
    el("circle", { cx: sx * 24, cy: -78, r: asustado ? 5 : 7, fill: "#111" }, g);
  }
  el("ellipse", { rx: 62, ry: 42, fill: "#FF6B42" }, g);
  el("path", { d: asustado ? "M-14,8 Q0,-4 14,8" : "M-14,2 Q0,14 14,2", fill: "none", stroke: "#7A1F10", "stroke-width": 6, "stroke-linecap": "round" }, g);
}

// ---------------------------------------------------------------- efectos
const EFECTOS = {
  entrada: { estado(c, e, td) { c.P.y = lerp(1900, c.P.y, easeBack(td / .8)); } },
  mirar: { estado(c, e) { c.P.lookX = e.x === "vaiven" ? Math.sin(c.t * 2.2) * .8 : (e.x ?? c.P.lookX); c.P.lookY = e.y ?? c.P.lookY; } },
  rayosX: { estado(c, e, td, t) { c.P.xray = Math.max(c.P.xray, easeOut(td / .6) * (e.hasta != null ? clamp((e.hasta - t) / .5) : 1)); } },
  organo: { estado(c, e, td, t) { c.P.organos[e.id] = easeBack(td / .5) * (e.hasta != null ? clamp((e.hasta - t) / .35) : 1); } },
  latido: { estado(c, e, td) { if (td >= 0) c.P.beat = e.velocidad || 2; } },
  flujo: { estado(c, e, td, t) { c.P.flujo = easeOut(td / .6) * (e.hasta != null ? clamp((e.hasta - t) / .35) : 1); if (e.color) c.P.flujoColor = e.color; } },
  luces: { estado(c, e, td, t) { c.P.luces = easeOut(td / .6) * (e.hasta != null ? clamp((e.hasta - t) / .35) : 1); } },
  agitar: { estado(c, e, td) { c.P.wave = 1 + ((e.intensidad || 1.8) - 1) * easeOut(td / .6); } },
  gris: { estado(c, e, td, t) { c.P.gris = vis(e, t, .5); } },
  camuflaje: {
    estado(c, e, td) {
      if (td <= 0) return; const cols = e.colores || ["#FF7F50", "#3BB273", "#E9C46A", "#9B5DE5"];
      const f = td / 1.1, i0 = Math.floor(f) % cols.length; c.P.color = mix(cols[i0], cols[(i0 + 1) % cols.length], easeInOut(f % 1)); c.P.tint = .38 * clamp(td / .5);
    },
  },
  senalar: {
    estado(c, e, td, t) {
      if (td <= 0) return; const fin = e.hasta != null ? 1 - easeInOut((t - e.hasta) / .5) : 1;
      c.P.objetivos[e.extremidad] = { g: e.objetivo, w: (e.fuerza ?? .7) * easeInOut(td / .5) * fin };
    },
  },
  objeto: {
    estado(c, e, td, t) {
      const [x, y] = e.pos; const dx = e.entra === "izquierda" ? -350 : 350;
      e._o = { x: lerp(x + dx, x, easeOut(td / .8)), y, asustado: e.asustado != null && t >= e.asustado };
      if (td >= 0) c.objeto = e._o;  // el último objeto visible es el que se puede alcanzar
    },
    dibujo(c, e, td) {
      if (td < 0) return; const o = e._o;
      const g = el("g", { "data-objeto": 1, transform: `translate(${o.x},${o.y})` }, c.OV);
      if (e.forma === "svg") g.innerHTML = e.svg; else cangrejo(g, 0, 0, o.asustado);
    },
  },
  alcanzar: {
    estado(c, e, td, t) {
      if (td <= 0) return; const obj = e.objetivo === "objeto" && c.objeto ? [c.objeto.x - 70, c.objeto.y - 30] : e.objetivo;
      const fin = e.hasta != null ? 1 - easeInOut((t - e.hasta) / .6) : 1;
      c.P.objetivos[e.extremidad] = { g: obj, w: easeInOut(td / 1.0) * fin };
    },
  },
  saborear: {
    estado(c, e, td) {
      if (td <= 0) return; c.P.saborAmt = easeOut(td / .4);
      Personaje.ext.forEach((_, i) => c.P.sabor[i] = i === e.extremidad ? 1 : .35);
      if (c.P.saborAmt > .5) c.P.boca = "abierta";
      c.P.lookX = .8; c.P.lookY = .7;
    },
  },
  aplastar: {
    estado(c, e, td) {
      const P = c.P; P.s = e.escala ?? .62; P.y = e.y ?? 880; P.lookX = 1; P.lookY = 0; P.wave = 1.4;
      const t0 = td;
      P.x = t0 < 1.2 ? lerp(250, 540, easeInOut(t0 / 1.2)) : t0 < 2.0 ? 540 + 6 * Math.sin(t0 * 40) : lerp(540, 840, easeInOut((t0 - 2.0) / 1.0));
      P.sy = lerp(.28, 1, clamp((Math.abs(P.x - 540) - 60) / 220)); P.sx = 1 + (1 - P.sy) * .25;
    },
    dibujo(c, e, td, t) {
      if (e.pared === false) return; const a = clamp(t / .4);
      for (const [y0, y1] of [[440, 835], [925, 1340]]) {
        el("rect", { x: 495, y: y0, width: 90, height: y1 - y0, rx: 26, fill: "#5B6C7F", opacity: a }, c.OV);
        for (let j = 0; j < 5; j++) el("circle", { cx: 520 + (j % 2) * 38, cy: y0 + 40 + j * (y1 - y0 - 80) / 4, r: 10, fill: "#46566A", opacity: a }, c.OV);
      }
    },
  },
  encuesta: {
    estado(c, e, td) {
      const k = easeInOut(td / .7), P = c.P; P.y = lerp(P.y, 690, k); P.s = lerp(P.s, P.s * .5, k); P.lookX = .7; P.lookY = .8;
      const n = (c.cfg.encuesta || []).length; if (td > 2 && n && Personaje.ext.length) {
        const j = Math.floor(clamp((td - 2.2) / .9, 0, n - .01)); c.P.objetivos[Personaje.ext.length - 1] = { g: [1000, 930 + j * 120], w: .6 };
      }
    },
    dibujo(c, e, td) {
      (c.cfg.encuesta || []).forEach((o, j) => {
        const a = easeOut((td - .5 - j * .25) / .45); if (a <= 0) return;
        const g = el("g", { transform: `translate(${lerp(1400, 540, a)},${930 + j * 120})` }, c.OV);
        el("rect", { x: -420, y: -48, width: 840, height: 96, rx: 48, fill: "#fff", "fill-opacity": .12, stroke: "#fff", "stroke-opacity": .4, "stroke-width": 3 }, g);
        el("circle", { cx: -370, cy: 0, r: 34, fill: "#FFD23F" }, g);
        el("text", { x: -370, y: 15, "text-anchor": "middle", "font-size": 40, "font-weight": 900, fill: "#0B1320" }, g).textContent = "ABCDEF"[j];
        el("text", { x: -315, y: 16, "font-size": 46, "font-weight": 700, fill: "#fff" }, g).textContent = o;
      });
    },
  },
  cierre: { dibujo(c, e, td, t) { if (td < 0) return; etiqueta(c.OV, c.cfg.cuenta, 540, 1390, { fondo: "#FFD23F", size: 50, alpha: vis(e, t), scale: easeBack(td / .45) }); } },
  antenas: {
    dibujo(c, e, td, t) {
      const fin = e.hasta ?? 1e9, a = 1 - easeOut((t - fin) / .5); if (a <= .01) return;
      const [hx, hy] = Personaje.def.anclas?.cabeza || [0, -385];
      const g = el("g", { opacity: a, transform: `translate(0,${-(1 - a) * 160}) rotate(${Math.sin(c.T * 9) * 6 * a} ${hx} ${hy})` }, $("octFx"));
      for (const sx of [-1, 1]) { el("line", { x1: hx + sx * 70, y1: hy + 25, x2: hx + sx * 110, y2: hy - 85, stroke: "#7CFC9A", "stroke-width": 10, "stroke-linecap": "round" }, g); el("circle", { cx: hx + sx * 110, cy: hy - 93, r: 22, fill: "#7CFC9A" }, g); }
    },
  },
  iconos: {
    dibujo(c, e, td, t) {
      const a = vis(e, t); const [x, y] = e.pos; const n = e.n || 1;
      for (let j = 0; j < n; j++) forma(c.OV, e.forma || "corazon", x + (j - (n - 1) / 2) * 55, y + (j % 2) * 30, e.forma === "gota" ? 42 : 34, e.color || "#FF3B5C", a, easeBack((td - j * .12) / .4) * (e.forma === "gota" ? 1 : 1.3));
    },
  },
  etiqueta: {
    dibujo(c, e, td, t) {
      const a = vis(e, t); if (a <= .01) return; const [x, y] = e.pos;
      if (e.ancla) { const [ax, ay] = Personaje.ancla(c.P, e.ancla); guia(c.OV, ax, ay, x, y, a, e.fondo && e.fondo !== "#fff" ? e.fondo : "#fff"); }
      etiqueta(c.OV, e.texto, x, y, { alpha: a, fondo: e.fondo, color: e.color, size: e.size || (String(e.texto).length > 14 ? 40 : 46), scale: e.pop === false ? 1 : easeBack(td / .45) });
    },
  },
  bocadillo: {
    dibujo(c, e, td, t) {
      const a = vis(e, t, .3); if (a <= .01) return; const [x, y] = e.pos;
      const g = el("g", { transform: `translate(${x},${y}) scale(${lerp(.6, 1, easeBack(td / .4))})`, opacity: a }, c.OV);
      const tx = el("text", { "text-anchor": "middle", "font-size": 48, "font-weight": 900, fill: "#0B1320", y: 17 }, g); tx.textContent = e.texto;
      const w = tx.getComputedTextLength() + 60;
      g.insertBefore(el("path", { d: `M${-w / 2 + 30},-45 H${w / 2 - 30} Q${w / 2},-45 ${w / 2},-15 V15 Q${w / 2},45 ${w / 2 - 30},45 H-10 L-50,85 L-40,45 H${-w / 2 + 30} Q${-w / 2},45 ${-w / 2},15 V-15 Q${-w / 2},-45 ${-w / 2 + 30},-45 Z`, fill: "#fff" }), tx);
    },
  },
  comparacion: {
    dibujo(c, e, td, t) {
      const lados = [[e.izq, 170, e.desde ?? 0], [e.der, 910, e.desde_der ?? (e.desde ?? 0) + 1.5]];
      for (const [l, x, d0] of lados) {
        const a = win(t, d0, e.hasta ?? 1e9); if (a <= .01 || !l) continue;
        forma(c.OV, l.forma || "gota", x, 690, 60, l.color, a, easeBack((t - d0) / .45));
        etiqueta(c.OV, l.texto, x, 800, { alpha: a, size: 38 });
        if (l.sub) etiqueta(c.OV, l.sub, x, 560, { alpha: a, size: 38, fondo: l.color, color: "#fff" });
      }
    },
  },
  posicion: {
    estado(c, e, td) {
      const k = easeInOut(td / (e.duracion ?? .7)), P = c.P;
      if (e.x != null) P.x = lerp(P.x, e.x, k); if (e.y != null) P.y = lerp(P.y, e.y, k);
      if (e.escala != null) P.s = lerp(P.s, P.s * e.escala, k);
    },
  },
  sello: {
    dibujo(c, e, td, t) {
      const a = vis(e, t, .15); if (a <= .01) return; const [x, y] = e.pos || [540, 700], col = e.color || "#E63946";
      const s = lerp(2.2, 1, easeOut(td / .25));
      const g = el("g", { transform: `translate(${x},${y}) rotate(${e.rot ?? -12}) scale(${s})`, opacity: a }, c.OV);
      const tx = el("text", { "text-anchor": "middle", y: (e.size || 110) * .36, "font-size": e.size || 110, "font-weight": 900, fill: col, "letter-spacing": 6 }, g);
      tx.textContent = e.texto; const w = tx.getComputedTextLength() + 70, h = (e.size || 110) * 1.35;
      g.insertBefore(el("rect", { x: -w / 2, y: -h / 2, width: w, height: h, rx: 18, fill: "#fff", "fill-opacity": .92, stroke: col, "stroke-width": 12 }), tx);
    },
  },
  linea_tiempo: {
    dibujo(c, e, td, t) {
      const a = vis(e, t); if (a <= .01) return;
      const [r0, r1] = e.rango, y = e.y ?? 1180, X = an => 120 + (an - r0) / (r1 - r0) * 840;
      const OV = c.OV, k = easeOut(td / .6);
      el("line", { x1: 120, y1: y, x2: lerp(120, 960, k), y2: y, stroke: "#fff", "stroke-width": 8, "stroke-linecap": "round", opacity: a }, OV);
      (e.tramos || []).forEach((tr, j) => {
        const b = win(t, tr.desde ?? 0); if (b <= .01) return; const x1 = X(tr.de), x2 = X(tr.a), col = tr.color || ["#FFD23F", "#2EC4B6", "#FF7F50"][j % 3];
        const kk = easeOut((t - (tr.desde ?? 0)) / .6), yy = y - 95;
        el("path", { d: `M${x1},${yy + 25} V${yy} H${lerp(x1, x2, kk)} V${yy + 25}`, fill: "none", stroke: col, "stroke-width": 8, "stroke-linejoin": "round", opacity: b }, OV);
        etiqueta(OV, tr.texto, (x1 + x2) / 2, yy - 45, { alpha: b, fondo: col, size: 40, scale: easeBack((t - (tr.desde ?? 0)) / .45) });
      });
      (e.puntos || []).forEach(pt => {
        const b = win(t, pt.desde ?? 0); if (b <= .01) return; const x = X(pt.anio), s = easeBack((t - (pt.desde ?? 0)) / .4);
        const g = el("g", { "data-punto": 1, opacity: b }, OV);
        el("circle", { cx: x, cy: y, r: 18 * s, fill: pt.color || "#FFD23F", stroke: "#0B1320", "stroke-width": 5 }, g);
        if (pt.icono) el("text", { x, y: y + 105, "text-anchor": "middle", "font-size": 64 * s }, g).textContent = pt.icono;
        const tx = el("text", { x, y: y + 150, "text-anchor": "middle", "font-size": 36, "font-weight": 900, fill: "#fff", stroke: "#0B1320", "stroke-width": 6, "paint-order": "stroke" }, g);
        tx.textContent = pt.etiqueta ?? String(pt.anio);
      });
    },
  },
  contador: {
    dibujo(c, e, td, t) {
      const a = vis(e, t); if (a <= .01) return; const [x, y] = e.pos || [540, 560];
      const tx = el("text", { x, y, "text-anchor": "middle", "font-size": 300, "font-weight": 900, fill: "#FFD23F", stroke: "#0B1320", "stroke-width": 16, "paint-order": "stroke", opacity: a }, c.OV);
      tx.textContent = Math.round((e.numero || 0) * easeOut(td / .9));
      if (e.etiqueta) etiqueta(c.OV, e.etiqueta, x, y + 110, { alpha: a, size: 56 });
    },
  },
};
window.EFECTOS = EFECTOS;
