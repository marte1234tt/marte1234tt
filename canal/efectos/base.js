// Base: utilidades, fondo, marca, título y bucle de render.
const NS = "http://www.w3.org/2000/svg";
const $ = id => document.getElementById(id);
const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const easeInOut = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const easeBack = x => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
// visible entre a y b, con transición de d segundos
const win = (t, a = 0, b = 1e9, d = .35) => clamp((t - a) / d) * clamp((b - t) / d);
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
const mix = (c1, c2, k) => { const a = hex(c1), b = hex(c2); return "#" + a.map((v, i) => Math.round(lerp(v, b[i], k)).toString(16).padStart(2, "0")).join(""); };
const bob0 = T => 10 * Math.sin(T * 1.6);
const Y_MAX_ETIQUETA = 1400;  // por debajo empiezan los subtítulos

const Base = {
  cfg: null,
  init(cfg) {
    this.cfg = cfg;
    const B = $("bubbles"); B.innerHTML = ""; this.bub = [];
    for (let i = 0; i < 22; i++) { const r = 6 + (i * 37 % 20); this.bub.push({ x: (i * 197) % 1080, y: (i * 613) % 1920, v: 25 + (i * 13 % 45), c: el("circle", { r, fill: "none", stroke: "#fff", "stroke-opacity": .14, "stroke-width": 3 }, B) }); }
    const M = $("marca"); M.innerHTML = "";
    el("rect", { x: 0, y: 0, width: 1080, height: 14, fill: "#fff", opacity: .15 }, M);
    this.prog = el("rect", { x: 0, y: 0, width: 0, height: 14, fill: "#FFD23F" }, M);
    const g = el("g", { transform: "translate(540,138)" }, M);
    const pr = el("rect", { y: -32, height: 64, rx: 32, fill: "#FFD23F" }, g);
    const tx = el("text", { y: 14, "text-anchor": "middle", "font-size": 38, "font-weight": 900, fill: "#0B1320" }, g);
    tx.textContent = cfg.etiqueta || "¿NO LO SABÍAS?";
    const w = tx.getComputedTextLength() + 70; pr.setAttribute("x", -w / 2); pr.setAttribute("width", w);
  },
  frame(T, esc, t) {
    this.prog.setAttribute("width", (1080 * clamp(T / this.cfg.total)).toFixed(1));
    this.bub.forEach(b => { b.c.setAttribute("cx", (b.x + 12 * Math.sin(T * 1.3 + b.y)).toFixed(1)); b.c.setAttribute("cy", (((b.y - b.v * T) % 2000 + 2000) % 2000 - 40).toFixed(1)); });
    const tt = $("title"); tt.textContent = esc.titulo || "";
    let fs = 96; tt.setAttribute("font-size", fs); tt.setAttribute("stroke-width", 14);
    while (fs > 40 && tt.getComputedTextLength() > 980) { fs -= 4; tt.setAttribute("font-size", fs); }
    $("titleG").setAttribute("transform", `translate(540,330) scale(${lerp(.5, 1, easeBack(t / .45))})`);
    $("titleG").setAttribute("opacity", clamp(t / .15));
  },
};

// ---------------------------------------------------------------- bucle principal
function escenaEn(T) { const S = Base.cfg.escenas; let i = 0; while (i < S.length - 1 && T >= S[i + 1].start) i++; return S[i]; }

function init(cfg) {
  Base.init(cfg);
  Personaje.crear(window.PERSONAJE_DEF, cfg);
}

function render(T) {
  const esc = escenaEn(T), t = T - esc.start;
  const OV = $("overlay"); OV.innerHTML = ""; $("fondoFx").innerHTML = "";
  const P = Personaje.estadoInicial(T);
  const ctx = { P, T, t, esc, cfg: Base.cfg, OV, fondo: $("fondoFx") };
  Base.frame(T, esc, t);
  for (const e of esc.efectos || []) {
    const fx = EFECTOS[e.tipo];
    if (!fx) { if (!render._avisado?.[e.tipo]) { console.warn("efecto desconocido: " + e.tipo); (render._avisado ||= {})[e.tipo] = 1; } continue; }
    fx.estado && fx.estado(ctx, e, t - (e.desde ?? 0), t);
  }
  Personaje.dibujar(P, T);
  for (const e of esc.efectos || []) { const fx = EFECTOS[e.tipo]; fx && fx.dibujo && fx.dibujo(ctx, e, t - (e.desde ?? 0), t); }
  $("tint").setAttribute("fill", P.color || "#000"); $("tint").setAttribute("opacity", P.tint);
  $("s").style.filter = P.gris > 0.001 ? `grayscale(${P.gris})` : "";
}
window.init = init; window.render = render;
