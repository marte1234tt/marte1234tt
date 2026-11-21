# Canal automatizado de curiosidades «¿No lo sabías?» — Diseño

Fecha: 2026-11-21 · Revisado tras las muestras · Estado: pendiente de aprobación

## Intención

Una cuenta de curiosidades **de todo tipo** en español, **@nolosabias672**, que se
alimente sola para **monetizar** en Instagram Reels, TikTok, YouTube Shorts y Facebook.
El usuario no quiere hacer nada, o casi nada, y **no quiere pagar nada aparte del plan
Claude Pro**. El primer reel (el pulpo) ya está publicado y es la referencia de estilo
y calidad.

## Objetivos

- Cada día, sin intervención, Claude:
  - elige un tema;
  - investiga y comprueba los datos;
  - escribe el guion;
  - dibuja al protagonista en dibujos animados;
  - anima cada dato sobre él;
  - pone voz, música y subtítulos;
  - entrega el vídeo terminado, con su portada y su texto de publicación.
- Las entregas llegan a Google Drive.
- Fase 2: publicación automática con el plan gratuito de Buffer.

## No objetivos (por ahora)

- Varias cuentas o nichos.
- Vídeo generado con IA de pago.
- Clonar la voz del usuario.

## Anti-objetivos (fracaso aunque "funcione")

- **Datos falsos o sin verificar.**
- **Vídeos que parezcan plantilla repetida.** YouTube desmonetiza el canal entero por
  "contenido no auténtico o repetitivo".
- **Música con copyright.**
- **Bots de publicación no oficiales.**
- **Cualquier coste extra.**
- **Ritmo lento o voz plana.** El usuario lo rechazó expresamente.
- **Ritmo atropellado.** También lo rechazó.

## Decisiones tomadas en las muestras

| Aspecto | Decisión |
|---|---|
| Estilo visual | **Dibujos animados**. Un protagonista dibujado (animal, objeto, planeta, órgano, personaje…) está en pantalla todo el vídeo y cada dato se ilustra sobre él, sincronizado con la palabra clave de la voz. Ejemplos: rayos X que muestran 3 corazones, sangre azul que corre por los brazos, el pulpo que se aplasta para pasar por una rendija. |
| Fotos de stock | Descartadas como base. Los bancos libres dieron muchas fotos erróneas (juguetes, otros animales, comida). |
| Voz | `edge-tts` (gratis), **es-ES-AlvaroNeural**, velocidad **+10 %** y **~0,3 s** de pausa añadida entre frases (≈0,55 s en total, ≈2,9 palabras/s). Cada frase se genera aparte con entonación propia: preguntas más agudas, exclamaciones con más energía. |
| Guion | Frases cortas, gancho de golpes ("¿Un alien? Nooo. Es el pulpo."), de 5 a 6 datos, encuesta A/B/C/D final y llamada a seguir la cuenta. |
| Duración | **61–80 s**, siempre más de 60 s (requisito de TikTok y Facebook para pagar). |
| Marca | Etiqueta superior **"¿NO LO SABÍAS?"**, barra de progreso amarilla, fondo azul marino con burbujas, tipografía Inter Display Black, subtítulos palabra a palabra con la palabra actual en amarillo. Cierre: "¡Síguenos en @nolosabias672!". |
| Temas | Curiosidades **de todo tipo**: ciencia, animales, cuerpo humano, espacio, historia, objetos cotidianos. |
| Portada | Imagen 1080×1920 por vídeo: el protagonista en su momento más llamativo y el titular grande. Todo lo importante cabe en el recorte 3:4 de la cuadrícula del perfil. |
| Publicación | Texto para Instagram (gancho, encuesta, 5 hashtags), TikTok (corto) y YouTube (título con #shorts). |
| Gemini TTS | Descartado. Al usuario le gustó más Álvaro. |

## Enfoques considerados

| Enfoque | Resultado |
|---|---|
| A. Fotos de stock | Descartado: genérico y con fotos erróneas. |
| B. Animación abstracta (contadores, gráficos) | Primera muestra. Al usuario le gustó, pero pidió un personaje. |
| **C. Personaje dibujado + efectos sincronizados (elegido)** | Segunda a cuarta muestras: aprobado. |
| Plugins de pago de vídeo IA | Descartados por coste. |

## Diseño

### Estructura del repositorio

```
.claude/skills/hacer-video/SKILL.md   ← receta paso a paso que sigue Claude
canal/
  config.json          ← voz, ritmo, marca, cuenta, carpeta de Drive
  motor/
    voz.py             ← edge-tts por frases + marcas de tiempo por palabra
    preparar.py        ← guion → voz, subtítulos (ASS), música, config de animación
    render.js          ← Chromium/Playwright: renderiza fotogramas en paralelo → MP4
    montar.sh          ← une vídeo, subtítulos, voz y música (ffmpeg)
    portada.js         ← genera la portada a partir de un instante del vídeo
  efectos/             ← CAJA DE EFECTOS reutilizable (JS/SVG)
    base.js            ← fondo, marca, título, burbujas, utilidades, easing
    personaje.js       ← cómo se monta un personaje: cuerpo, ojos, parpadeo, respiración, extremidades
    efectos.js         ← rayos X con órganos, etiquetas con flechas, gotas y comparaciones,
                         cambio de color, objetos que entran, extremidad que señala,
                         aplastar o estirar, bocadillo, encuesta A/B/C/D, contador
  personajes/          ← un archivo por personaje ya dibujado (pulpo.js…), reutilizable
  musica/              ← pistas libres de derechos (las pone el usuario; si falta, música sintetizada)
  temas/usados.json    ← historial para no repetir temas
  temas/cola.txt       ← temas pedidos por el usuario o por los seguidores (opcional)
  salida/              ← vídeos generados (ignorado por git)
```

### Flujo de un vídeo

1. **Tema.** Primero se mira `cola.txt`. Si está vacía, Claude busca curiosidades
   que estén funcionando y elige una que no esté en `usados.json`. Va alternando
   categorías para que el canal no se repita.
2. **Investigación.** Cada dato se confirma con al menos 2 fuentes fiables. Los
   datos dudosos se descartan.
3. **Guion** (`guion.json`), con 5–8 escenas. Cada escena lleva:
   - el texto narrado;
   - el título de pantalla;
   - las palabras clave que disparan las animaciones;
   - el efecto que toca.
4. **Personaje.** Si ya existe en `personajes/`, se reutiliza. Si no, Claude lo
   dibuja en SVG siguiendo `personaje.js` y la paleta de la marca: estilo plano,
   ojos grandes y mejillas. Claude revisa fotogramas sueltos antes de seguir.
5. **Voz y tiempos.** Se ejecuta `preparar.py`, que da la duración real. Si queda
   por debajo de 61 s, se añade un dato y se repite el paso.
6. **Render**, de unos 2 minutos, en 4 procesos en paralelo.
7. **Montaje.** Subtítulos quemados en el vídeo, música bajo la voz (que baja
   sola cuando habla) y volumen normalizado a -14 LUFS.
8. **Revisión automática.** Claude mira ~10 fotogramas y comprueba:
   - que no haya textos encima de otros ni cortados;
   - que el personaje se vea bien;
   - que dure entre 61 y 80 s;
   - que el archivo pese menos de 50 MB.

   Si algo falla, lo corrige y vuelve a renderizar.
9. **Portada y textos.** Se generan `portada.png`, `publicacion.txt` (Instagram,
   TikTok y YouTube) y `fuentes.md`.
10. **Entrega.** Todo va a Google Drive, en `¿No lo sabías?/AAAA-MM-DD tema/`. Después
    se actualiza `usados.json` y se hace commit y push, sin los `.mp4`.

### Variación anti-plantilla

- Cada vídeo tiene un protagonista y gags distintos.
- Se rota el estilo del gancho y la estructura del cierre.
- La paleta de acentos varía dentro de la marca.

### Automatización

- **Tarea programada diaria** (1 vídeo al día; el plan Pro permite 5 ejecuciones
  diarias). Abre una sesión nueva en el entorno `marte1234tt` con el conector de
  Google Drive concedido.
- **Script de inicio del entorno:** `pip install edge-tts`. Chromium, Playwright,
  ffmpeg y Python ya vienen instalados.
- **Red:** `speech.platform.bing.com`, ya permitido. Las demás entradas añadidas
  durante las pruebas (Openverse, Hugging Face, Gemini) se pueden quitar.

### Fase 2 — Buffer

Igual que en el diseño anterior. Se hace cuando el usuario valide unos días de vídeos.

## Lo que hace el usuario

1. Aprobar este diseño, el script de inicio y la tarea diaria.
2. Opcional: dejar pistas libres de derechos en `canal/musica/`.
3. Durante la Fase 1, publicar el vídeo diario desde el móvil con la portada y el
   texto que llegan a Drive (≈2 min).

## Decisiones del constructor (corregibles)

- Hora de la tarea: el vídeo se genera por la mañana para que esté listo antes de
  la franja de 19–21 h (hora de España), la mejor para publicar.
- El pulpo se guarda como primer personaje de la biblioteca. La mascota del perfil
  (bombilla o interrogación) puede aparecer en el cierre.
- Calidad mínima: si la revisión automática falla dos veces, el vídeo se entrega
  igualmente, marcado como "revisar" en el nombre de la carpeta.
