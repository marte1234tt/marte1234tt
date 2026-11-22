// Napoleón Bonaparte (vídeo de historia: «no era bajito»).
registrarPersonaje({
  nombre: "napoleon",
  cuerpo: "M -125,-235 C -125,-350 125,-350 125,-235 C 125,-150 78,-100 0,-100 C -78,-100 -125,-150 -125,-235 Z",
  colores: { claro: "#F8D6B6", oscuro: "#E2AC84", ext1: "#2B4FB0", ext2: "#1F3A93", mano: "#F8D6B6", boca: "#8A3B2E" },
  detras: `
    <path d="M -132,-250 C -140,-330 140,-330 132,-250 L 138,-170 L -138,-170 Z" fill="#3B2416"/>
    <rect x="-36" y="-130" width="72" height="90" fill="#E8B48C"/>
    <path d="M -72,-60 L 72,-60 L 190,330 L -190,330 Z" fill="#1F3A93"/>
    <path d="M -40,-58 L 40,-58 L 70,330 L -70,330 Z" fill="#F4F4F4"/>
    <path d="M -40,-58 L 0,40 L 40,-58" fill="none" stroke="#C9CED6" stroke-width="6"/>
    <circle cx="0" cy="90" r="9" fill="#FFD23F"/><circle cx="0" cy="150" r="9" fill="#FFD23F"/><circle cx="0" cy="210" r="9" fill="#FFD23F"/>
    <path d="M -72,-60 L -40,-58 L -70,160 Z" fill="#E63946"/><path d="M 72,-60 L 40,-58 L 70,160 Z" fill="#E63946"/>
    <ellipse cx="-92" cy="-48" rx="42" ry="18" fill="#FFD23F"/><ellipse cx="92" cy="-48" rx="42" ry="18" fill="#FFD23F"/>
    <path d="M -130,-44 l 8,26 M -116,-40 l 6,26 M -102,-38 l 4,26 M 130,-44 l -8,26 M 116,-40 l -6,26 M 102,-38 l -4,26" stroke="#E0A800" stroke-width="5" stroke-linecap="round"/>`,
  detalles: `
    <path d="M -62,-318 C -30,-300 -10,-270 -30,-250 C -5,-268 20,-300 40,-318 Z" fill="#3B2416"/>
    <path d="M -78,-250 L -28,-240 M 78,-250 L 28,-240" stroke="#3B2416" stroke-width="9" stroke-linecap="round"/>
    <path d="M -205,-298 Q 0,-480 205,-298 Q 0,-345 -205,-298 Z" fill="#151515"/>
    <path d="M -205,-298 Q 0,-345 205,-298" fill="none" stroke="#FFD23F" stroke-width="7"/>
    <circle cx="70" cy="-370" r="26" fill="#2B4FB0"/><circle cx="70" cy="-370" r="17" fill="#FFFFFF"/><circle cx="70" cy="-370" r="8" fill="#E63946"/>`,
  brillo: [-60, -290, 36, 16, -20],
  ojos: [[-48, -210], [48, -210]], ojoTam: [30, 36],
  mejillas: [[-80, -165], [80, -165]],
  boca: [0, -150], bocaAncho: 22,
  extremidades: [
    { raiz: [-78, -35], angulo: 110, largo: 255, grosor: [40, 30], ondula: .22, curva: .25, mano: true },
    { raiz: [78, -35], angulo: 70, largo: 255, grosor: [40, 30], ondula: .22, curva: .25, mano: true },
  ],
  organos: { cerebro: { x: 0, y: -250, forma: "cerebro", escala: .9 } },
  anclas: { cabeza: [0, -425], boca: [0, -150] },
  sombraY: 360, baseCuerpo: 330,
});
