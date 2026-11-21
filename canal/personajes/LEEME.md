# Personajes

Cada vídeo tiene un protagonista dibujado. Un personaje es un archivo `<nombre>.js` que llama a
`registrarPersonaje({...})`. Se reutilizan entre vídeos: antes de crear uno nuevo, mira si ya existe.

## Contrato (coordenadas locales: x a la derecha, y hacia abajo, origen cerca de la base del cuerpo)

| Campo | Qué es |
|---|---|
| `nombre` | igual que el archivo |
| `cuerpo` | path SVG de la parte principal (se rellena con el degradado `colores.claro → colores.oscuro`; es también la zona de "rayos X") |
| `colores` | `{claro, oscuro, ext1, ext2, mancha, boca}` |
| `detras` | SVG (texto) que va detrás del cuerpo: pelo, cuello, ropa, caparazón… |
| `detalles` | SVG (texto) que va delante del cuerpo: flequillo, corona, gafas… |
| `manchas`, `brillo` | opcionales: `[[x,y,r]...]`, `[x,y,rx,ry,rot]` |
| `ojos`, `ojoTam` | `[[x,y],[x,y]]`, `[rx, ry]` (ojos grandes = más simpático) |
| `mejillas`, `boca`, `bocaAncho` | posiciones |
| `extremidades` | atajo `{tipo:"tentaculo", n, raiz:{x0,dx,y}, largo}` o lista `[{raiz:[x,y], angulo, largo, grosor:[base,punta], ondula, curva, mano:true, ventosas:false}]` (ángulo en grados, 90 = hacia abajo). La ÚLTIMA extremidad es la que señala en la encuesta. |
| `organos` | `{id: {x, y, forma: "corazon"|"cerebro"|"circulo"|"svg", escala, color, svg}}` para `rayosX` + `organo` |
| `vasos` | paths para el efecto `flujo` |
| `anclas` | `{cabeza:[x,y], ...}` puntos con nombre para etiquetas y antenas |
| `escala`, `posicion`, `sombraY`, `baseCuerpo` | tamaño (0.95), centro en pantalla ([540,960]), sombra, punto fijo al "respirar" |

## Estilo de la marca

- Dibujo plano, formas redondeadas, **ojos grandes con brillo**, mejillas rosadas, sonrisa.
- Colores saturados que contrasten con el fondo azul marino (`#0B1320`); evita azules oscuros en el cuerpo.
- Alto total en pantalla ≈ 700 px (de y≈580 a y≈1280 con escala 0.95): deja libre arriba el título y abajo los subtítulos.
- Comprueba siempre 3 capturas antes de renderizar el vídeo entero.
