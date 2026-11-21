# Canal automatizado de curiosidades — Diseño

Fecha: 2026-11-21 · Estado: pendiente de aprobación

## Intención

Tener un canal de curiosidades ("¿Sabías que…?") en español que se alimente solo,
para **monetizar** cuentas en Instagram Reels, TikTok, YouTube Shorts y Facebook.
El usuario no quiere hacer nada, o casi nada, y **no quiere pagar nada aparte del
plan Claude Pro**.

## Objetivos

- Cada día, sin intervención, Claude elige un tema, investiga, escribe el guion y
  produce un vídeo vertical terminado: voz, animación, fotos, música y subtítulos.
- El vídeo y el texto de publicación (descripción y hashtags) llegan a Google Drive.
- Fase 2: publicación automática mediante el plan gratuito de Buffer.

## No objetivos (por ahora)

- Varios nichos o cuentas. Se empieza con uno; la carpeta se clona después.
- Vídeo generado por IA (Kling, Veo, Sora…): es de pago.
- Miniaturas personalizadas y vídeos largos.

## Anti-objetivos (fracaso aunque "funcione")

- Datos falsos o sin verificar: un error en un dato hunde la credibilidad.
- Vídeos que parezcan plantilla repetida: YouTube desmonetiza el canal entero por
  "contenido no auténtico o repetitivo".
- Música con copyright: el vídeo pierde la monetización o se silencia.
- Bots de publicación no oficiales: riesgo de baneo.
- Cualquier coste extra.

## Restricciones

- Solo herramientas gratuitas. El único pago es el plan Claude Pro.
- El plan Pro permite 5 ejecuciones automáticas (tareas programadas) al día.
- Duración de **61–90 s**: TikTok y Facebook solo pagan vídeos de más de 1 minuto.
- Formato 1080×1920, 30 fps, H.264 + AAC, por debajo de ~50 MB.
- La red del entorno está limitada. Hay que permitir, con aprobación del usuario:
  `speech.platform.bing.com` (voz), `api.pexels.com`, `images.pexels.com` y
  `videos.pexels.com` (fotos). En la Fase 2, además, `api.buffer.com`.
- Los vídeos (`.mp4`) **no** se guardan en git, solo en Drive.

## Enfoques considerados

| Enfoque | Ventaja | Inconveniente |
|---|---|---|
| A. Solo fotos y clips de stock | Aspecto documental | Igual que miles de cuentas; riesgo de "contenido repetitivo" |
| B. Solo animación por código | Estilo propio, no depende de nada externo | Menos impacto en temas concretos (animales, lugares) |
| **C. Híbrido (elegido)** | Identidad visual propia y fotos reales cuando ayudan | Más trabajo de montaje inicial, que se hace una vez |
| Plugins de pago (ManyMotions, Abracadabrax) | Vídeo IA llamativo | De pago por créditos; descartado |

Para publicar, se eligió hacerlo en dos fases: primero Drive y publicación manual,
después Buffer gratis. Las APIs oficiales de TikTok y YouTube publican solo en
privado hasta pasar una auditoría, y los bots no oficiales arriesgan la cuenta.

## Diseño

### Estructura

```
.claude/skills/hacer-video/SKILL.md   ← instrucciones que sigue Claude
canal-curiosidades/
  config.json        ← voz, colores, tipografía, duración, carpeta de Drive
  temas/usados.json  ← historial para no repetir temas
  temas/cola.txt     ← temas que el usuario quiera forzar (opcional)
  musica/            ← pistas libres de derechos (las pone el usuario)
  motor/             ← scripts Python: voz, visuales, subtítulos, montaje
  salida/            ← vídeos generados (ignorado por git)
```

### Flujo de un vídeo

1. **Tema.** Si hay temas en `cola.txt`, se usa el primero. Si no, Claude busca en
   la web qué curiosidades están funcionando y elige uno que no esté en `usados.json`.
2. **Investigación.** Cada dato se confirma con al menos 2 fuentes fiables. Si un
   dato no se puede confirmar, se descarta. Las fuentes se guardan en `fuentes.md`.
3. **Guion** (`guion.json`), de unas 170–230 palabras:
   - gancho de 1–2 s;
   - de 3 a 5 datos encadenados;
   - cierre con pregunta para provocar comentarios.

   Cada escena lleva el texto narrado, el texto grande en pantalla, la palabra
   clave resaltada y el tipo de visual: animación (cifra, comparación, icono o
   título) o foto (con su búsqueda para Pexels).
4. **Voz.** `edge-tts` con voz neuronal en español (por defecto
   `es-ES-AlvaroNeural`, configurable). Sus marcas de tiempo por palabra
   sincronizan los subtítulos sin necesidad de Whisper.
5. **Visuales.** Escenas de animación generadas con Python (Pillow) y `ffmpeg`,
   con la plantilla propia del canal: colores, tipografía, entradas con
   movimiento y contadores. Las escenas con foto usan Pexels con zoom lento y
   capa de color de marca. Si falla Pexels, la escena pasa a ser animación.
6. **Subtítulos.** Palabra a palabra, grandes y centrados, con la palabra
   actual resaltada. Formato ASS, quemado con `ffmpeg`/libass.
7. **Música.** Una pista aleatoria de `musica/`, con el volumen bajado bajo la
   voz. Si la carpeta está vacía, el vídeo sale sin música.
8. **Variación anti-plantilla.** Cada vídeo varía la paleta (entre varias de la
   marca), el orden y tipo de transiciones y la estructura del gancho.
9. **Comprobación final.** Antes de entregar se verifica que:
   - la duración está entre 61 y 90 s;
   - el audio y los subtítulos van sincronizados (se revisan fotogramas sueltos);
   - el archivo pesa menos de 50 MB.
10. **Entrega.** En la carpeta "Canal Curiosidades" de Google Drive se crea una
    subcarpeta `AAAA-MM-DD tema` con `video.mp4`, `publicacion.txt` (descripción
    y hashtags) y `fuentes.md`. Después se actualiza `usados.json` y se hace
    commit y push.

### Automatización

- Una **tarea programada diaria** (1 vídeo al día, ampliable a 2–3 dentro del
  límite de 5) abre una sesión nueva y ejecuta la skill `hacer-video`. Lleva el
  conector de Google Drive concedido.
- **Script de inicio del entorno:** instala `edge-tts` para que cada sesión
  automática arranque lista.
- **Clave de Pexels:** se guarda como credencial del entorno, nunca en el
  repositorio.

### Fase 2 — Buffer (después de validar la calidad)

- El usuario crea una cuenta gratuita de Buffer, conecta Instagram, TikTok
  (cuenta Business) y YouTube, y genera una clave de API.
- Tras el paso 10, Claude añade el vídeo a la cola de los tres canales con su
  descripción.
- Hay que comprobar en ese momento si Buffer acepta la URL de Drive como origen
  del vídeo o necesita otra URL pública.

## Lo que hace el usuario (una sola vez)

1. Aprobar los permisos de red y el script de inicio cuando se le pidan.
2. Crear una clave gratuita en pexels.com/api y meterla en el formulario seguro.
3. Opcional: dejar 5–10 pistas libres de derechos en `musica/`.
4. Durante la Fase 1, publicar el vídeo diario desde el móvil (≈1 min).

## Decisiones del constructor (propuestas, corregibles)

- Voz por defecto `es-ES-AlvaroNeural` (masculina, España). Se puede cambiar en `config.json`.
- Hora de la tarea diaria: tarde, fuera de la franja de 6–9 h del Pacífico, que
  suele ir saturada.
- Paleta de marca y tipografía: las elige Claude y se enseñan en el primer vídeo.
