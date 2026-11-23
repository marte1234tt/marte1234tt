// Personaje genérico: cuerpo, ojos, boca, extremidades, órganos (rayos X) y vasos.
// Cada personaje concreto vive en canal/personajes/<nombre>.js y llama a registrarPersonaje(def).
function registrarPersonaje(def) { window.PERSONAJE_DEF = def; }

const FORMAS = {
  corazon(s = 1) { let d = ""; for (let i = 0; i <= 40; i++) { const t = i / 40 * 2 * Math.PI; const x = 16 * Math.pow(Math.sin(t), 3), y = 13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t); d += (i ? "L" : "M") + (x * 3.1 * s).toFixed(1) + "," + (-y * 3.1 * s).toFixed(1); } return d + "Z"; },
  cerebro(s = 1) { return `M${-55 * s},${0} C${-80 * s},${-40 * s} ${-20 * s},${-70 * s} 0,${-45 * s} C${20 * s},${-70 * s} ${80 * s},${-40 * s} ${55 * s},0 C${75 * s},${30 * s} ${30 * s},${55 * s} 0,${38 * s} C${-30 * s},${55 * s} ${-75 * s},${30 * s} ${-55 * s},0 Z`; },
  gota(r) { return `M0,${-r * 2.1} C ${r * .6},${-r * 1.2} ${r},${-r * .6} ${r},0 A ${r} ${r} 0 0 1 ${-r},0 C ${-r},${-r * .6} ${-r * .6},${-r * 1.2} 0,${-r * 2.1} Z`; },
  estrella(r) { let d = ""; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; d += (i ? "L" : "M") + (Math.cos(a) * rr).toFixed(1) + "," + (Math.sin(a) * rr).toFixed(1); } return d + "Z"; },
};

const Personaje = {
  def: null,
  expandirExtremidades(x) {
    if (Array.isArray(x)) return x;
    if (!x) return [];
    const n = x.n || 8, mid = (n - 1) / 2, ab = x.abanico || 11.5;
    return [...Array(n).keys()].map(i => ({
      raiz: [x.raiz.x0 + i * x.raiz.dx, x.raiz.y], angulo: 90 + (mid - i) * ab, largo: x.largo || 330,
      grosor: x.grosor || [46, 7], ondula: x.ondula ?? .55, curva: x.curva ?? .9,
      ventosas: x.tipo === "tentaculo", mano: x.tipo === "brazo",
    }));
  },
  crear(def, cfg) {
    if (!def) throw new Error("no hay personaje registrado");
    this.def = def; this.ext = this.expandirExtremidades(def.extremidades);
    const O = $("oct"); O.innerHTML = "";
    $("cuerpoClipPath").setAttribute("d", def.cuerpo);
    el("ellipse", { cx: 0, cy: def.sombraY ?? 420, rx: 260, ry: 34, fill: "#000", opacity: .25, filter: "url(#soft)" }, O);
    const A = el("g", {}, O); this.limbs = this.ext.map((e, i) => {
      const g = el("g", {}, A);
      const body = el("path", { fill: "url(#armGrad)" }, g);
      const blood = el("path", { fill: "none", "stroke-width": 8, "stroke-linecap": "round", "stroke-dasharray": "22 26", opacity: 0 }, g);
      const mano = e.mano ? el("circle", { fill: e.manoColor || def.colores?.mano || "url(#armGrad)" }, g) : null;
      const sc = e.ventosas ? [...Array(9)].map(() => el("circle", { fill: "#FFD3E2", stroke: "#E2789F", "stroke-width": 2 }, g)) : [];
      const ng = el("g", { filter: "url(#glow)" }, g), nc = [...Array(4)].map(() => el("circle", { r: 9, fill: "#FFE66D" }, ng));
      return { body, blood, mano, sc, nc };
    });
    const C = el("g", { id: "cuerpoG" }, O); this.C = C;
    if (def.detras) { const g = el("g", {}, C); g.innerHTML = def.detras; }
    this.cuerpo = el("path", { d: def.cuerpo, fill: "url(#bodyGrad)" }, C);
    if (def.manchas) { const m = el("g", { fill: def.colores?.mancha || "#000", opacity: .18 }, C); def.manchas.forEach(([x, y, r]) => el("circle", { cx: x, cy: y, r }, m)); }
    if (def.brillo) { const [x, y, rx, ry, rot] = def.brillo; el("ellipse", { cx: x, cy: y, rx, ry, fill: "#fff", opacity: .28, transform: `rotate(${rot || 0} ${x} ${y})` }, C); }
    if (def.foto) {  // cabeza con foto recortada en óvalo
      const f = def.foto, s = (f.alto || 150) / f.ry, cy = f.centroY ?? -240;
      const cp = el("clipPath", { id: "fotoClip" }, $("s").querySelector("defs"));
      el("ellipse", { cx: 0, cy, rx: f.rx * s, ry: f.ry * s }, cp);
      this.fotoG = el("g", {}, C);
      el("ellipse", { cx: 0, cy: cy + 6, rx: f.rx * s + 10, ry: f.ry * s + 10, fill: "#000", opacity: .25 }, this.fotoG);
      el("image", { href: f.href, x: -f.cx * s, y: cy - f.cy * s, width: f.ancho * s, height: f.alto_img * s, "clip-path": "url(#fotoClip)", preserveAspectRatio: "none" }, this.fotoG);
      el("ellipse", { cx: 0, cy, rx: f.rx * s, ry: f.ry * s, fill: "none", stroke: "#fff", "stroke-width": 8 }, this.fotoG);
      this.fotoCy = cy;
    }
    if (def.detalles) { const g = el("g", {}, C); g.innerHTML = def.detalles; }
    const X = el("g", { "clip-path": "url(#cuerpoClip)", opacity: 0 }, C); this.X = X;
    el("rect", { x: -600, y: -900, width: 1200, height: 1400, fill: "#2A0F3D", opacity: .55 }, X);
    this.vasos = el("g", { fill: "none", "stroke-width": 9, "stroke-linecap": "round", "stroke-dasharray": "18 18", opacity: 0 }, X);
    (def.vasos || []).forEach(d => el("path", { d }, this.vasos));
    this.organos = {};
    for (const [id, o] of Object.entries(def.organos || {})) {
      const g = el("g", { transform: `translate(${o.x},${o.y}) scale(0)` }, X);
      if (o.forma === "svg") g.innerHTML = o.svg;
      else if (o.forma === "circulo") el("circle", { r: 40 * (o.escala || 1), fill: o.color || "#FFB3C7", stroke: "#fff", "stroke-width": 4 }, g);
      else el("path", { d: FORMAS[o.forma || "corazon"](o.escala || 1), fill: o.color || (o.forma === "cerebro" ? "#FFB3C7" : "#FF3B5C"), stroke: "#fff", "stroke-width": o.forma === "cerebro" ? 4 : 5, filter: o.forma === "cerebro" ? null : "url(#glow)" }, g);
      this.organos[id] = { g, ...o };
    }
    const tam = def.ojoTam || [56, 64];
    this.ojos = (def.ojos || []).map(([x, y]) => {
      const g = el("g", { transform: `translate(${x},${y})` }, C), lid = el("g", {}, g);
      el("ellipse", { rx: tam[0], ry: tam[1], fill: "#fff" }, lid);
      const pu = el("circle", { r: tam[0] * .55, fill: "#1B1B2F" }, lid), sp = el("circle", { r: tam[0] * .18, fill: "#fff" }, lid);
      return { lid, pu, sp };
    });
    (def.mejillas || []).forEach(([x, y]) => el("ellipse", { cx: x, cy: y, rx: 32, ry: 18, fill: "#FF5C8A", opacity: .55 }, C));
    this.boca = el("path", { fill: "none", stroke: def.colores?.boca || "#7A1F45", "stroke-width": 9, "stroke-linecap": "round", opacity: def.boca === null ? 0 : 1 }, C);
    this.fx = el("g", { id: "octFx" }, O);
    if (def.extra) def.extra(C);
  },
  estadoInicial(T) {
    const d = this.def || {};
    $("octFx") && ($("octFx").innerHTML = "");
    return { x: d.posicion?.[0] ?? 540, y: d.posicion?.[1] ?? 960, s: d.escala ?? .95, sx: 1, sy: 1, wave: 1, curl: 1,
      xray: 0, flujo: 0, flujoColor: "#5AA2FF", luces: 0, sabor: {}, saborAmt: 0, organos: {}, beat: 1,
      lookX: Math.sin(T * .7) * .4, lookY: .1, color: null, tint: 0, gris: 0, objetivos: {}, boca: null };
  },
  // coordenadas locales → pantalla, con el estado actual
  aPantalla(P, lx, ly) { return [P.x + lx * P.s * P.sx, P.y + bob0(P.T || 0) + ly * P.s * P.sy]; },
  ancla(P, nombre) {
    const d = this.def, o = this.organos[nombre];
    let l = o ? [o.x, o.y] : d.anclas?.[nombre];
    if (!l && nombre === "ojo_izq") l = d.ojos[0];
    if (!l && nombre === "ojo_der") l = d.ojos[1] || d.ojos[0];
    if (!l && nombre === "boca") l = d.boca;
    if (!l) { console.warn("ancla desconocida: " + nombre); l = [0, 0]; }
    return this.aPantalla(P, l[0], l[1]);
  },
  puntos(i, T, P) {
    const e = this.ext[i], N = 24, seg = e.largo / N, side = e.angulo > 90 ? 1 : -1;
    let [x, y] = e.raiz; const pts = [[x, y]], base = e.angulo * Math.PI / 180, ph = i * 1.37;
    for (let k = 1; k <= N; k++) {
      const s = k / N, th = base + P.wave * e.ondula * s * Math.sin(T * 2.1 + ph - 3.2 * s) + side * e.curva * s * s * P.curl;
      x += Math.cos(th) * seg; y += Math.sin(th) * seg; pts.push([x, y]);
    }
    const ob = P.objetivos[i];
    if (ob && ob.w > 0) {
      const tx = (ob.g[0] - P.x) / (P.s * P.sx), ty = (ob.g[1] - P.y - bob0(T)) / (P.s * P.sy), [rx, ry] = e.raiz;
      for (let k = 1; k <= N; k++) {
        const s = k / N, bx = lerp(rx, tx, s), by = lerp(ry, ty, s) - Math.sin(s * Math.PI) * 60, w = ob.w * Math.pow(s, .6);
        pts[k][0] = lerp(pts[k][0], bx, w); pts[k][1] = lerp(pts[k][1], by, w);
      }
    }
    return pts;
  },
  dibujarExtremidad(i, T, P) {
    const e = this.ext[i], L = this.limbs[i], pts = this.puntos(i, T, P), N = pts.length - 1;
    const W = s => (e.grosor[0] - e.grosor[1]) * Math.pow(1 - s, .85) + e.grosor[1];
    const izq = [], der = [];
    for (let k = 0; k <= N; k++) {
      const a = pts[Math.max(0, k - 1)], b = pts[Math.min(N, k + 1)];
      let nx = -(b[1] - a[1]), ny = b[0] - a[0]; const l = Math.hypot(nx, ny) || 1; nx /= l; ny /= l;
      const w = W(k / N) / 2; izq.push([pts[k][0] + nx * w, pts[k][1] + ny * w]); der.push([pts[k][0] - nx * w, pts[k][1] - ny * w]); pts[k].n = [nx, ny];
    }
    const f = p => p[0].toFixed(1) + "," + p[1].toFixed(1);
    L.body.setAttribute("d", "M" + izq.map(f).join("L") + `A 4 4 0 0 1 ${f(der[N])}` + "L" + der.reverse().map(f).join("L") + "Z");
    L.blood.setAttribute("d", "M" + pts.slice(1, N - 2).map(f).join("L"));
    L.blood.setAttribute("stroke", P.flujoColor); L.blood.setAttribute("opacity", P.flujo); L.blood.setAttribute("stroke-dashoffset", (-T * 90).toFixed(1));
    if (L.mano) { L.mano.setAttribute("cx", pts[N][0]); L.mano.setAttribute("cy", pts[N][1]); L.mano.setAttribute("r", e.grosor[1] * 1.6); }
    const side = e.angulo > 90 ? -1 : 1, sab = P.saborAmt * (P.sabor[i] ?? 0);
    L.sc.forEach((c, j) => {
      const k = 4 + j * 2, p = pts[k], w = W(k / N);
      c.setAttribute("cx", (p[0] + p.n[0] * w * .22 * side).toFixed(1)); c.setAttribute("cy", (p[1] + p.n[1] * w * .22 * side).toFixed(1)); c.setAttribute("r", (w * .2).toFixed(1));
      const gl = sab * (0.6 + 0.4 * Math.sin(T * 12 - j));
      c.setAttribute("fill", gl > .05 ? mix("#FFD3E2", "#FFE66D", clamp(gl)) : "#FFD3E2"); c.setAttribute("filter", gl > .3 ? "url(#glow)" : "");
    });
    L.nc.forEach((c, j) => {
      const s = ((j / 4 + T * .35 + i * .13) % 1) * .85 + .08, p = pts[Math.round(s * N)];
      c.setAttribute("cx", p[0].toFixed(1)); c.setAttribute("cy", p[1].toFixed(1)); c.setAttribute("opacity", (P.luces * (.6 + .4 * Math.sin(T * 6 + j * 2 + i))).toFixed(2));
    });
  },
  dibujar(P, T) {
    P.T = T; const d = this.def, breath = 1 + .02 * Math.sin(T * 2.3);
    $("oct").setAttribute("transform", `translate(${P.x},${P.y + bob0(T)}) scale(${P.s * P.sx},${P.s * P.sy})`);
    const by = d.baseCuerpo ?? 62;
    this.C.setAttribute("transform", `translate(0,${by}) scale(${1 / breath},${breath}) translate(0,${-by})`);
    this.ext.forEach((_, i) => this.dibujarExtremidad(i, T, P));
    const c = d.colores || {};
    const claro = c.claro || "#FF9EC0", oscuro = c.oscuro || "#D9467F";
    $("bc1").setAttribute("stop-color", P.color ? mix(P.color, "#ffffff", .3) : claro);
    $("bc2").setAttribute("stop-color", P.color || oscuro);
    $("ac1").setAttribute("stop-color", P.color ? mix(P.color, "#ffffff", .15) : (c.ext1 || claro));
    $("ac2").setAttribute("stop-color", P.color ? mix(P.color, "#000000", .15) : (c.ext2 || oscuro));
    this.cuerpo.setAttribute("fill-opacity", 1 - .35 * P.xray);
    this.X.setAttribute("opacity", P.xray);
    this.vasos.setAttribute("opacity", P.flujo); this.vasos.setAttribute("stroke", P.flujoColor);
    [...this.vasos.children].forEach(p => p.setAttribute("stroke-dashoffset", (-T * 70).toFixed(1)));
    Object.entries(this.organos).forEach(([id, o], j) => {
      const k = clamp(P.organos[id] ?? 0, 0, 1.4), late = (o.forma || "corazon") === "corazon" ? 1 + .13 * Math.pow(Math.max(0, Math.sin(T * 7 * P.beat + j * .6)), 6) : 1;
      o.g.setAttribute("transform", `translate(${o.x},${o.y}) scale(${k * late})`);
    });
    const parp = (T % 3.3) < .13 ? .1 : 1;
    this.ojos.forEach(o => {
      o.lid.setAttribute("transform", `scale(1,${parp})`);
      const r = parseFloat(o.pu.getAttribute("r"));
      o.pu.setAttribute("cx", P.lookX * r * .5); o.pu.setAttribute("cy", P.lookY * r * .58);
      o.sp.setAttribute("cx", P.lookX * r * .5 + r * .32); o.sp.setAttribute("cy", P.lookY * r * .58 - r * .38);
    });
    if (this.fotoG) this.fotoG.setAttribute("transform", `rotate(${(Math.sin(T * 2.6) * 3).toFixed(2)} 0 ${this.fotoCy + 140})`);
    const [mx, my] = d.boca || [0, -30], mw = d.bocaAncho || 30;
    this.boca.setAttribute("d", P.boca === "abierta" ? `M${mx - mw - 4},${my - 4} Q${mx},${my + 40} ${mx + mw + 4},${my - 4} Q${mx},${my + 20} ${mx - mw - 4},${my - 4}` : `M${mx - mw},${my} Q${mx},${my + 30} ${mx + mw},${my}`);
    this.boca.setAttribute("fill", P.boca === "abierta" ? (d.colores?.boca || "#7A1F45") : "none");
  },
};
window.registrarPersonaje = registrarPersonaje; window.Personaje = Personaje; window.FORMAS = FORMAS;
