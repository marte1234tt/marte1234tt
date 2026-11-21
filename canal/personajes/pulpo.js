// Pulpo: primer personaje del canal (reel del 21-11-2026).
registrarPersonaje({
  nombre: "pulpo",
  cuerpo: "M -215,-60 C -240,-300 -130,-385 0,-385 C 130,-385 240,-300 215,-60 C 200,20 120,62 0,62 C -120,62 -200,20 -215,-60 Z",
  colores: { claro: "#FF9EC0", oscuro: "#D9467F", ext1: "#F06A9C", ext2: "#C93D74", mancha: "#8A1E4E", boca: "#7A1F45" },
  manchas: [[-120, -260, 18], [-60, -320, 11], [135, -285, 14], [160, -200, 9], [-165, -180, 10]],
  brillo: [-95, -290, 55, 32, -25],
  ojos: [[-80, -120], [80, -120]], ojoTam: [56, 64],
  mejillas: [[-150, -45], [150, -45]],
  boca: [0, -30], bocaAncho: 30,
  extremidades: { tipo: "tentaculo", n: 8, raiz: { x0: -165, dx: 47, y: 25 }, largo: 330 },
  organos: {
    corazon_izq: { x: -120, y: -262, forma: "corazon", escala: .8 },
    corazon_der: { x: 120, y: -262, forma: "corazon", escala: .8 },
    corazon_centro: { x: 0, y: -300, forma: "corazon", escala: 1.15 },
    cerebro: { x: 0, y: -300, forma: "cerebro" },
  },
  vasos: ["M0,-300 C -60,-295 -100,-280 -120,-262", "M0,-300 C 60,-295 100,-280 120,-262",
          "M0,-300 C 0,-180 -40,-60 -150,40", "M0,-300 C 0,-180 40,-60 150,40",
          "M0,-300 C -10,-150 -10,-50 -50,60", "M0,-300 C 10,-150 10,-50 50,60"],
  anclas: { cabeza: [0, -385], pico: [0, -30] },
});
