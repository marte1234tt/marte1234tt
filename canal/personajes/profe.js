// Profe: guía de los tutoriales con la cara de la foto del usuario (uso personal de estudio).
// La foto vive en personajes/privado/ (no se sube a git).
registrarPersonaje({
  nombre: "profe",
  cuerpo: "M 0,-240 Z",
  colores: { claro: "#F6D3B5", oscuro: "#E2AD87", ext1: "#FFFFFF", ext2: "#DCE3EA", mano: "#F1C6A2" },
  foto: { href: "../personajes/privado/profe.jpg", cx: 100, cy: 93, rx: 57, ry: 88, ancho: 200, alto_img: 200, alto: 160, centroY: -250 },
  detras: `
    <rect x="-34" y="-130" width="68" height="86" fill="#E8B48E"/>
    <path d="M -78,-62 L 78,-62 C 150,-50 185,-10 188,60 L 190,330 L -190,330 L -188,60 C -185,-10 -150,-50 -78,-62 Z" fill="#F8F9FB"/>
    <path d="M -34,-66 L 0,-10 L 34,-66 L 58,-58 L 18,10 L 0,-8 L -18,10 L -58,-58 Z" fill="#E6EBF1" stroke="#C7D0DA" stroke-width="3"/>
    <line x1="0" y1="-8" x2="0" y2="330" stroke="#D5DCE4" stroke-width="4"/>
    <circle cx="0" cy="60" r="6" fill="#C7D0DA"/><circle cx="0" cy="130" r="6" fill="#C7D0DA"/><circle cx="0" cy="200" r="6" fill="#C7D0DA"/>`,
  ojos: [], mejillas: [], boca: null,
  extremidades: [
    { raiz: [-140, -30], angulo: 110, largo: 240, grosor: [40, 22], ondula: .2, curva: .25, mano: true },
    { raiz: [140, -30], angulo: 70, largo: 240, grosor: [40, 22], ondula: .2, curva: .25, mano: true },
  ],
  anclas: { cabeza: [0, -420], boca: [0, -150] },
  sombraY: 360, baseCuerpo: 330,
});
