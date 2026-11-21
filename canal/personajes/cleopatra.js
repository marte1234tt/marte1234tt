// Cleopatra VII: reina de Egipto (vídeo de historia).
registrarPersonaje({
  nombre: "cleopatra",
  cuerpo: "M -130,-240 C -130,-360 130,-360 130,-240 C 130,-150 80,-95 0,-95 C -80,-95 -130,-150 -130,-240 Z",
  colores: { claro: "#F6CFA4", oscuro: "#D69A66", ext1: "#EDB98A", ext2: "#C98A55", boca: "#8A3B2E" },
  detras: `
    <path d="M -178,-250 C -190,-430 190,-430 178,-250 L 188,-62 L -188,-62 Z" fill="#1B1420"/>
    <rect x="-38" y="-130" width="76" height="92" fill="#DDA270"/>
    <path d="M -62,-55 L 62,-55 L 178,330 L -178,330 Z" fill="#F5F1E6"/>
    <path d="M -10,-40 L 10,-40 L 40,330 L -40,330 Z" fill="#E8E1CF"/>
    <rect x="-118" y="150" width="236" height="24" rx="6" fill="#FFD23F"/>
    <path d="M -112,-60 Q 0,62 112,-60" stroke="#2EC4B6" stroke-width="24" fill="none" stroke-linecap="round"/>
    <path d="M -96,-64 Q 0,36 96,-64" stroke="#FFD23F" stroke-width="18" fill="none" stroke-linecap="round"/>
    <path d="M -80,-66 Q 0,14 80,-66" stroke="#E63946" stroke-width="10" fill="none" stroke-linecap="round"/>`,
  detalles: `
    <path d="M -140,-238 C -152,-400 152,-400 140,-238 Q 0,-272 -140,-238 Z" fill="#1B1420"/>
    <path d="M -142,-294 Q 0,-326 142,-294 L 142,-276 Q 0,-308 -142,-276 Z" fill="#FFD23F"/>
    <path d="M -12,-298 C -24,-342 24,-352 12,-322 C 6,-310 16,-302 12,-292 Z" fill="#FFB800" stroke="#B8860B" stroke-width="3"/>
    <circle cx="0" cy="-332" r="6" fill="#3A86FF"/>
    <path d="M -80,-212 Q -98,-216 -112,-230 Q -100,-204 -82,-198 Z" fill="#1B1420"/>
    <path d="M 80,-212 Q 98,-216 112,-230 Q 100,-204 82,-198 Z" fill="#1B1420"/>
    <circle cx="-134" cy="-158" r="13" fill="#FFD23F"/><circle cx="134" cy="-158" r="13" fill="#FFD23F"/>`,
  brillo: [-70, -300, 40, 18, -20],
  ojos: [[-52, -205], [52, -205]], ojoTam: [30, 36],
  mejillas: [[-82, -160], [82, -160]],
  boca: [0, -145], bocaAncho: 22,
  extremidades: [
    { raiz: [-70, -35], angulo: 112, largo: 260, grosor: [34, 24], ondula: .22, curva: .25, mano: true },
    { raiz: [70, -35], angulo: 68, largo: 260, grosor: [34, 24], ondula: .22, curva: .25, mano: true },
  ],
  organos: { cerebro: { x: 0, y: -250, forma: "cerebro", escala: .9 } },
  anclas: { cabeza: [0, -395], boca: [0, -145] },
  sombraY: 360, baseCuerpo: 330,
});
