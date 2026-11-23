// Robot técnico de redes: guía de los tutoriales.
registrarPersonaje({
  nombre: "robot",
  cuerpo: "M -150,-380 Q -150,-420 -110,-420 L 110,-420 Q 150,-420 150,-380 L 150,-170 Q 150,-130 110,-130 L -110,-130 Q -150,-130 -150,-170 Z",
  colores: { claro: "#7FF0E3", oscuro: "#22A699", ext1: "#A4B1C4", ext2: "#6B7A90", mano: "#9AA7B8", boca: "#0D1117" },
  detras: `
    <rect x="-40" y="-140" width="80" height="40" fill="#6B7A90"/>
    <rect x="-140" y="-110" width="280" height="350" rx="44" fill="#2B4FB0"/>
    <rect x="-100" y="-60" width="200" height="120" rx="16" fill="#1F3A93"/>
    ${[0, 1, 2, 3].map(i => `<rect x="${-85 + i * 45}" y="-35" width="34" height="30" rx="4" fill="#FFD23F"/><rect x="${-79 + i * 45}" y="-29" width="22" height="16" fill="#0D1117"/><circle cx="${-68 + i * 45}" cy="20" r="6" fill="${i < 3 ? '#27C93F' : '#FF5F56'}"/>`).join("")}
    <rect x="-95" y="240" width="70" height="90" rx="14" fill="#6B7A90"/><rect x="25" y="240" width="70" height="90" rx="14" fill="#6B7A90"/>`,
  detalles: `
    <rect x="-122" y="-370" width="244" height="168" rx="34" fill="#0D1117"/>
    <line x1="0" y1="-420" x2="0" y2="-478" stroke="#6B7A90" stroke-width="10"/><circle cx="0" cy="-488" r="17" fill="#FF5F56"/>
    <circle cx="-160" cy="-275" r="16" fill="#6B7A90"/><circle cx="160" cy="-275" r="16" fill="#6B7A90"/>`,
  ojos: [[-50, -286], [50, -286]], ojoTam: [32, 38],
  mejillas: [[-104, -168], [104, -168]],
  boca: [0, -168], bocaAncho: 26,
  extremidades: [
    { raiz: [-130, -70], angulo: 112, largo: 220, grosor: [30, 26], ondula: .22, curva: .25, mano: true },
    { raiz: [130, -70], angulo: 68, largo: 220, grosor: [30, 26], ondula: .22, curva: .25, mano: true },
  ],
  anclas: { cabeza: [0, -500], boca: [0, -168] },
  sombraY: 360, baseCuerpo: 330,
});
