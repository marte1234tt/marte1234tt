// Mando de consola (genérico, sin marcas): protagonista de vídeos de videojuegos.
registrarPersonaje({
  nombre: "mando",
  cuerpo: "M -150,-260 L 150,-260 C 230,-260 260,-200 270,-120 C 285,-20 300,60 240,70 C 190,78 160,10 110,-20 L -110,-20 C -160,10 -190,78 -240,70 C -300,60 -285,-20 -270,-120 C -260,-200 -230,-260 -150,-260 Z",
  colores: { claro: "#FF9AD5", oscuro: "#C2378A", ext1: "#E86AB0", ext2: "#B02E7C", mano: "#FFFFFF", boca: "#5A1440" },
  detras: `<path d="M 0,-30 C 40,80 -50,160 10,280" fill="none" stroke="#2A2340" stroke-width="14" stroke-linecap="round"/>`,
  detalles: `
    <path d="M -195,-175 h 30 v -30 h 30 v 30 h 30 v 30 h -30 v 30 h -30 v -30 h -30 Z" fill="#2A2340"/>
    <circle cx="170" cy="-200" r="17" fill="#3BB273"/><circle cx="205" cy="-165" r="17" fill="#E63946"/>
    <circle cx="135" cy="-165" r="17" fill="#3A86FF"/><circle cx="170" cy="-130" r="17" fill="#FFD23F"/>
    <circle cx="-85" cy="-55" r="30" fill="#2A2340"/><circle cx="-85" cy="-55" r="18" fill="#4A4060"/>
    <circle cx="85" cy="-55" r="30" fill="#2A2340"/><circle cx="85" cy="-55" r="18" fill="#4A4060"/>`,
  brillo: [-120, -235, 60, 14, -8],
  ojos: [[-42, -185], [42, -185]], ojoTam: [30, 34],
  mejillas: [[-85, -125], [85, -125]],
  boca: [0, -118], bocaAncho: 20,
  extremidades: [
    { raiz: [-262, -150], angulo: 140, largo: 190, grosor: [26, 18], ondula: .25, curva: .3, mano: true },
    { raiz: [262, -150], angulo: 40, largo: 190, grosor: [26, 18], ondula: .25, curva: .3, mano: true },
  ],
  anclas: { cabeza: [0, -270] },
  escala: 1.15, sombraY: 300, baseCuerpo: 70,
});
