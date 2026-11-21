# Canal «¿No lo sabías?» — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Objetivo:** convertir el prototipo del vídeo del pulpo en un sistema reutilizable que, cada día y sin intervención, genere un vídeo de curiosidades en dibujos animados y lo deje en Google Drive con su portada y su texto de publicación.

**Arquitectura:** el pipeline de Python (`canal/motor/`) convierte un `guion.json` en voz, marcas de tiempo, subtítulos, música y un `config.json` de animación. Una página HTML/SVG (`canal/efectos/`) dibuja el personaje y aplica una **línea de tiempo declarativa de efectos** que va leyendo de ese config. `render.js` captura los fotogramas con Chromium en 4 procesos y `montar.sh` une todo con ffmpeg. Una skill (`hacer-video`) es la receta que Claude sigue en la tarea programada diaria.

**Tecnologías:** Python 3.13 (edge-tts, numpy, pytest), Node 22 (playwright, `node:test`), Chromium preinstalado, ffmpeg con libass.

**Diseño:** `docs/superpowers/specs/2026-11-21-canal-curiosidades-design.md`

**Prototipo de referencia** (solo existe en esta sesión; se copia al repo en la Tarea 1):
`/tmp/claude-0/-home-user-marte1234tt/00255a41-ed7a-5c5c-96b1-5cc00bb45c73/scratchpad/spike/`
con `motor.py`, `prep3.py`, `pulpo3.html`, `render.js`, `perfil2.html` y `guion4.json`.

## Restricciones globales

- Coste extra: **0 €**. Solo herramientas gratuitas, más el plan Claude Pro.
- Voz: `es-ES-AlvaroNeural`, `velocidad` **+10 %**, `pausa` **0,3 s** tras cada frase. Prosodia por frase: si lleva `?`, tono +6 Hz; si lleva `!`, tono +4 Hz y velocidad +6; si tiene ≤3 palabras, velocidad +4; y una microvariación de tono `[0,-2,2,-1][i%4]` Hz.
- Vídeo: 1080×1920, 30 fps, H.264 yuv420p CRF 21, AAC 160k a 44,1 kHz, `+faststart`, volumen −14 LUFS, **61–80 s** y **< 50 MB**.
- Subtítulos: estilo ASS `Inter Display Black`, tamaño 92, contorno 7, `MarginV` 340, bloques de ≤3 palabras y ≤16 caracteres, palabra actual en `&H3FD2FF&` (amarillo).
- Marca:
  - etiqueta superior: texto "¿NO LO SABÍAS?", en `#FFD23F` sobre `#0B1320`;
  - fondo con degradado radial de `#18304F` a `#0B1320`;
  - acento `#FFD23F`;
  - tipografía Inter Display 900;
  - cierre: "¡Síguenos en @nolosabias672!".
- Los títulos de escena caben en 1000 px de ancho (la fuente se reduce si hace falta). Las etiquetas de abajo nunca bajan de y = 1400, para no pisar los subtítulos.
- Los `.mp4`, `salida/` y los modelos descargados no se suben a git.
- Prohibido: música con copyright, datos con menos de 2 fuentes, bots no oficiales.

## Puntos de revisión

1. **Una pista (palabra clave) que no aparece en la voz** debe hacer que el efecto empiece al principio de la escena (+0,3 s), no que no aparezca nunca. El prototipo usaba 1e9 y el efecto desaparecía. La prueba está en la Tarea 2.
2. **Un guion que se queda corto (< 61 s)** debe hacer que `preparar.py` termine con código 3 y el mensaje `DURACION_CORTA <segundos>`, para que la receta añada un dato. La prueba está en la Tarea 2.
3. **Caracteres especiales en textos** (`{`, `}`, `\`, comillas, emojis) no deben romper los subtítulos ASS ni el SVG. La prueba está en la Tarea 2 (ASS) y la Tarea 3 (SVG, con `textContent`).
4. **Un fallo de red temporal en edge-tts** debe reintentarse 3 veces, esperando 2, 4 y 8 s, antes de fallar con un mensaje claro. La prueba está en la Tarea 2, con un sintetizador falso que falla dos veces.
5. **Un título largo** (por ejemplo "¿CEREBRO EN LOS BRAZOS?") debe medir ≤ 1000 px. La prueba está en la Tarea 3.

---

### Task 1: Estructura, configuración y voz por frases

**Archivos:**
- Crear `canal/config.json`, `canal/.gitignore`, `canal/motor/__init__.py`, `canal/motor/voz.py` y `canal/tests/test_voz.py`.
- Crear `canal/_prototipo/`, con una copia de los archivos del prototipo listados arriba. Se borra en la Tarea 6.

**Interfaces:**
- Produce:
  - `cargar_config() -> dict`, que lee `canal/config.json`;
  - `frases(texto: str) -> list[str]`;
  - `prosodia(frase: str, i: int, base: int) -> tuple[str, str]`, que devuelve, por ejemplo, `("+16%", "+6Hz")`;
  - `async sintetizar(frases: list[str], voz: str, base: int, pausa: float, tmp: str, synth=None) -> tuple[str, list[tuple[float, float, str]]]`, que devuelve la ruta de `voz.wav` y las palabras reconocidas con sus tiempos absolutos. `synth` es una función inyectable, `async synth(texto, voz, rate, pitch, mp3_path) -> list[(ini, fin, palabra)]`; por defecto usa edge-tts a través del proxy.
- Contenido de `config.json`:
  ```json
  {"cuenta": "@nolosabias672", "etiqueta": "¿NO LO SABÍAS?",
   "voz": {"nombre": "es-ES-AlvaroNeural", "velocidad": 10, "pausa": 0.3},
   "duracion": {"min": 61, "max": 80}, "drive_carpeta": "¿No lo sabías?"}
  ```

- [ ] **Paso 1: tests** en `test_voz.py`:
  - `test_frases_corta_por_puntuacion`: `frases("¿Un alien? Nooo. ¡Es el pulpo!") == ["¿Un alien?", "Nooo.", "¡Es el pulpo!"]`.
  - `test_prosodia_pregunta`: `prosodia("¿Un alien?", 0, 10) == ("+14%", "+6Hz")`. Son ≤3 palabras, así que +4 de velocidad; pregunta, +6 de tono; `i=0`, +0.
  - `test_prosodia_exclamacion`: `prosodia("¡Y saborea con los brazos!", 1, 10) == ("+16%", "+2Hz")`.
  - `test_sintetizar_tiempos_absolutos`: con un `synth` falso que devuelve una palabra en (0,10–0,50) y genera un mp3 de 1 s de silencio con ffmpeg, dos frases dan palabras cuyo segundo inicio es igual a la duración del primer wav recortado, y `voz.wav` existe.
  - `test_sintetizar_reintenta`: un `synth` que lanza `ConnectionError` dos veces y luego funciona termina bien. Se parchea `voz.ESPERAS = [0, 0, 0]` para que el test no espere.
- [ ] **Paso 2:** `cd canal && python3 -m pytest tests/test_voz.py -v`. Esperado: FAIL (no existe el módulo).
- [ ] **Paso 3: implementación.** Portar `frases`, `prosodia` y `voz_edge` desde `_prototipo/prep3.py`. Ajustes:
  - el recorte de cada frase es `atrim=max(0,ini-0.02):fin+0.07` y después `apad=pad_dur=pausa`;
  - reintentos con `ESPERAS = [2, 4, 8]`;
  - el certificado del proxy se toma de `SSL_CERT_FILE` (`ec._SSL_CTX`) y el proxy, de `HTTPS_PROXY`.
- [ ] **Paso 4:** ejecutar los tests. Esperado: PASS.
- [ ] **Paso 5:** commit, `feat(canal): config y voz por frases con prosodia`.

### Task 2: Preparar — guion → tiempos, subtítulos, música y config de animación

**Archivos:**
- Crear `canal/motor/preparar.py`, `canal/motor/subtitulos.py`, `canal/motor/musica.py` y `canal/tests/test_preparar.py`.
- Crear `canal/ejemplos/pulpo/guion.json`, que es el `_prototipo/guion4.json` convertido al formato nuevo (ver abajo).

**Interfaces:**
- Consume `sintetizar` y `cargar_config` (Tarea 1).
- Produce:
  - `subtitulos(palabras, ruta)`, portado del prototipo, más `escapar_ass(texto) -> str`, que escapa `{`, `}` y `\`;
  - `musica(duracion, ruta)`: si `canal/musica/*.mp3|wav` tiene pistas, elige una al azar y la corta o repite con fundido de salida; si no, usa el sintetizador del prototipo;
  - `preparar(guion_path, salida_dir, synth=None) -> dict`, que escribe en `salida_dir/tmp/` los archivos `voz.wav`, `subs.ass`, `musica.wav` y `config.json`;
  - CLI `python3 -m motor.preparar <guion> <salida>`, que sale con código 3 e imprime `DURACION_CORTA 52.4` si el total es menor que `duracion.min`.
- **Formato del guion** (es también el contrato con la Tarea 3):
  ```json
  {"tema": "El pulpo", "personaje": "pulpo",
   "escenas": [{"titulo": "3 CORAZONES", "texto": "…",
                "efectos": [{"tipo": "rayosX", "desde": "tres"},
                            {"tipo": "organo", "id": "corazon_izq", "desde": "Dos"}]}],
   "encuesta": ["3 corazones", "Brazos que piensan", "Saborear al tocar", "Cuerpo sin huesos"],
   "publicacion": {"instagram": "…", "tiktok": "…", "youtube_titulo": "…"},
   "fuentes": ["…"], "portada": {"t": "sangre+4.0", "linea1": "TIENE 3", "linea2": "CORAZONES", "banda": "¡Y SANGRE AZUL!"}}
  ```
  `desde` y `hasta` pueden ser una palabra del texto de la escena, un número de segundos desde el inicio de la escena o `"palabra+0.5"`.
- **Formato de `config.json`:** `{"total", "cuenta", "etiqueta", "personaje", "encuesta", "escenas": [{"titulo", "start", "dur", "efectos": [... con desde/hasta ya en segundos locales]}]}`. Si una palabra no se encuentra, se usa 0,3 y se imprime `AVISO pista no encontrada: <palabra>`.
- Al final del total se añaden 1,4 s de cola.

- [ ] **Paso 1: tests**, con un `synth` falso que asigna 0,3 s por palabra:
  - `test_resuelve_pistas_a_segundos_locales`: la segunda escena, con `desde: "Dos"`, da el inicio local de esa palabra (±0,01).
  - `test_pista_inexistente_usa_inicio`: `desde: "zzz"` da 0,3.
  - `test_pista_con_desfase`: `"Dos+0.5"` da el inicio de "Dos" + 0,5.
  - `test_duracion_corta_sale_con_3`: un guion de 5 palabras, ejecutado con subprocess y un synth falso (activado con la variable `CANAL_SYNTH_FALSO=1`), termina con código 3 y "DURACION_CORTA" en la salida.
  - `test_escapar_ass`: `escapar_ass("a{b}\\c") == "a\\{b\\}\\\\c"`, y un `subs.ass` generado con "{hola}" contiene `\{HOLA\}`.
  - `test_escenas_contiguas`: `start[i+1] == start[i] + dur[i]` y la suma de las duraciones es igual a `total`.
- [ ] **Paso 2:** ejecutar. Esperado: FAIL.
- [ ] **Paso 3: implementación.**
  - Portar `tokens_guion`, `alinear` y el bloque de escenas de `_prototipo/prep3.py`.
  - Portar `subtitulos` y `musica` de `_prototipo/motor.py`, con `MarginV 340`.
  - Las pistas se resuelven aquí, no en el JS.
- [ ] **Paso 4:** ejecutar los tests (PASS). Después ejecutar `python3 -m motor.preparar ejemplos/pulpo/guion.json salida/pulpo` con la voz real. Esperado: total entre 70 y 73 s y ningún `AVISO`.
- [ ] **Paso 5:** commit, `feat(canal): preparar guion → tiempos, subtítulos, música y config`.

### Task 3: Caja de efectos y personaje pulpo

**Archivos:**
- Crear `canal/efectos/pagina.html`. Solo contiene el `<svg>` raíz y carga los scripts siguientes, más `personajes/<nombre>.js`, por medio de `?personaje=`.
- Crear `canal/efectos/base.js`: utilidades (`el`, `clamp`, `lerp`, `easeOut`, `easeBack`, `easeInOut`, `win`, `mix`), fondo, burbujas, barra de progreso, etiqueta de marca y `titulo(texto, t)`, que reduce la fuente hasta que `getBBox().width ≤ 1000`.
- Crear `canal/efectos/personaje.js`: `crearPersonaje(def)` y las extremidades tipo tentáculo, brazo o pata (`armPoints` y `drawArm` del prototipo, generalizados con `def.extremidades`).
- Crear `canal/efectos/efectos.js`: un registro `EFECTOS[tipo] = (ctx, e, t) => void`.
- Crear `canal/personajes/pulpo.js` y `canal/tests/efectos.test.mjs`.

**Interfaces:**
- **Consume:** el `config.json` de la Tarea 2.
- **Produce:**
  - En la página: `window.init(config)` y `window.render(T)`, igual que el prototipo, para que `render.js` no cambie.
  - **Contrato de personaje** (lo que Claude escribe para cada personaje nuevo):
    ```js
    registrarPersonaje({
      nombre: "pulpo",
      cuerpo: "<path d=…>",              // en coordenadas locales, origen en la base del cuerpo
      colores: {claro: "#FF9EC0", oscuro: "#D9467F"},
      ojos: [[-80,-120],[80,-120]], boca: [0,-30],
      extremidades: {tipo: "tentaculo", n: 8, raiz: {x0: -165, dx: 47, y: 25}, largo: 330},
      organos: {corazon_izq: {x:-120,y:-262,forma:"corazon",escala:.8}, …, cerebro: {…}},
      vasos: ["M0,-300 C…", …],
      anclas: {cabeza: [0,-330], pico: [0,-30]},
      extra: (g) => {}                   // opcional: antenas, sombrero…
    })
    ```
  - **Efectos** (cada uno recibe `desde`, `hasta` opcional y sus parámetros):
    - `entrada`: el personaje sube con rebote.
    - `rayosX`: cuerpo translúcido.
    - `organo {id}`: el órgano aparece y late si es un corazón.
    - `etiqueta {texto, ancla|x,y, pos:[x,y], color, fondo}`: con línea guía desde el ancla.
    - `flujo {color}`: sangre o energía por los vasos y las extremidades.
    - `luces`: puntos que viajan por las extremidades.
    - `iconos {forma: corazon|gota|estrella, n, pos}`.
    - `comparacion {izq:{forma,color,texto,sub}, der:{…}, desde_der}`.
    - `objeto {svg|forma:"cangrejo", pos, entra:"derecha"}`.
    - `alcanzar {extremidad, objetivo:[x,y]|"objeto"}`.
    - `senalar {extremidad, objetivo}`.
    - `bocadillo {texto}`.
    - `gris`: la pantalla pierde el color.
    - `camuflaje {colores:[…]}`.
    - `aplastar {pared:true}`.
    - `antenas`: el gag de la intro, con caída.
    - `mirar {x,y}`.
    - `encuesta`: usa `config.encuesta`; el personaje se encoge arriba y señala las opciones.
    - `cierre`: muestra `config.cuenta` con la mascota de perfil.
  - **Escape:** si un guion trae `"js": "extra.js"`, la página lo carga después de `efectos.js`, para que Claude añada efectos propios de un tema sin tocar la caja.
- **Tests** en `efectos.test.mjs`, con `node --test` y playwright cargando `pagina.html?personaje=pulpo` con un config de prueba:
  - `sin errores de página`: `init` y `render` en 20 instantes no lanzan `pageerror`.
  - `título largo cabe`: con el título "¿CEREBRO EN LOS BRAZOS?", `#title.getBBox().width <= 1000`.
  - `texto especial`: una etiqueta con `<b>&"{}"` se muestra literal (`textContent`), sin romper el SVG.
  - `etiqueta inferior no pisa subtítulos`: una etiqueta pedida en y = 1500 acaba en y ≤ 1400.
  - `efecto desconocido`: `{"tipo":"zzz"}` muestra un aviso en consola, sin error.
- [ ] **Paso 1:** escribir los tests. Ejecutar `node --test canal/tests/efectos.test.mjs`. Esperado: FAIL.
- [ ] **Paso 2:** implementar `base.js`, `personaje.js`, `efectos.js` y `pulpo.js`, portando la lógica de `_prototipo/pulpo3.html`. Cada bloque `if (sc.tipo === …)` del prototipo pasa a ser uno o más efectos genéricos.
- [ ] **Paso 3:** ejecutar los tests. Esperado: PASS.
- [ ] **Paso 4: regresión visual.** Pasar `canal/ejemplos/pulpo/guion.json` (Tarea 2) a la nueva lista de efectos. Capturar fotogramas fijos en los mismos instantes que el prototipo y compararlos a ojo con la muestra 4. Tiene que verse el mismo contenido: corazones, sangre, neuronas, cangrejo, rendija, camuflaje y encuesta.
- [ ] **Paso 5:** commit, `feat(canal): caja de efectos declarativa y personaje pulpo`.

### Task 4: Render, montaje y portada

**Archivos:**
- Crear `canal/motor/render.js`, portado de `_prototipo/render.js`. Recibe `config.json`, `pagina.html`, el personaje y el directorio de salida.
- Crear `canal/motor/montar.sh`, con el comando ffmpeg de mezcla de la muestra 4 (sidechain, loudnorm −14).
- Crear `canal/motor/portada.js`: renderiza el instante `portada.t` y superpone `linea1`, `linea2` y `banda`, con la misma maquetación que `portada-reel1.png`.
- Crear `canal/motor/hacer.sh`, que ejecuta preparar → render → montar → portada → textos y termina con la salida `LISTO <ruta>`.
- Crear `canal/tests/test_montaje.py`.

**Interfaces:**
- Consume `preparar` (Tarea 2) y `pagina.html` (Tarea 3).
- Produce `canal/salida/<AAAA-MM-DD-slug>/`, con `video.mp4`, `portada.png`, `publicacion.txt` (secciones INSTAGRAM, TIKTOK y YOUTUBE, con los textos del guion), `fuentes.md` y `fotogramas/` (10 capturas para revisar).
- `hacer.sh <guion.json>`:
  - sale con código 3 si `preparar` dio `DURACION_CORTA`;
  - sale con código 4 si el vídeo final no cumple duración, tamaño o resolución.

- [ ] **Paso 1: test** `test_hacer_pulpo_completo`. Marcado como lento (`@pytest.mark.lento`, ≈3 min). Ejecuta `hacer.sh ejemplos/pulpo/guion.json` y comprueba con ffprobe:
  - 1080×1920 y 30 fps;
  - duración entre 61 y 80;
  - < 50 MB;
  - `portada.png` de 1080×1920;
  - `publicacion.txt` contiene "INSTAGRAM" y "#curiosidades".
- [ ] **Paso 2:** ejecutar. Esperado: FAIL.
- [ ] **Paso 3:** implementar.
- [ ] **Paso 4:** ejecutar el test (PASS). Después, mirar 4 fotogramas de `fotogramas/`.
- [ ] **Paso 5:** commit, `feat(canal): render paralelo, montaje, portada y script hacer.sh`.

### Task 5: Skill `hacer-video` y datos de temas

**Archivos:**
- Crear `.claude/skills/hacer-video/SKILL.md`, `canal/temas/usados.json` (con `[{"fecha":"2026-11-21","tema":"El pulpo","categoria":"animales"}]`), `canal/temas/cola.txt` (vacío) y `canal/musica/LEEME.md`.
- Crear `canal/personajes/LEEME.md`, con el contrato de personaje (Tarea 3) y una lista de comprobación de estilo: trazo plano, ojos grandes con brillo, mejillas, colores saturados que contrasten con el fondo azul marino.

**Contenido de SKILL.md** (receta, en este orden):
1. Leer `canal/config.json`, `usados.json` y `cola.txt`.
2. **Tema:** el primero de la cola, o buscar en la web curiosidades actuales.
   - Rotar categorías: animales, cuerpo humano, espacio, historia, objetos cotidianos, comida y ciencia. No repetir la categoría de los 2 últimos vídeos.
3. **Investigar:** al menos 2 fuentes fiables por dato; descartar lo que no se confirme.
4. **Guion:** con el formato de la Tarea 2.
   - Gancho de golpes cortos, 5–6 datos y frases cortas.
   - Penúltima escena: un dato sorprendente. Última: la encuesta, más "¡Síguenos en @nolosabias672!".
   - Sin "…" (provoca pausas largas).
5. **Personaje:** reutilizar uno de `personajes/` o crear uno nuevo con el contrato. Revisar 3 capturas antes de seguir.
6. Ejecutar `canal/motor/hacer.sh`.
   - Código 3: añadir un dato y repetir.
   - Código 4: arreglarlo y repetir.
7. **Revisión:** mirar los 10 fotogramas. Comprobar que no haya textos montados, cortados o vacíos y que cada efecto encaje con lo que se dice. Corregir y repetir como mucho 2 veces. Si sigue mal, entregar con el sufijo " (revisar)".
8. **Entrega en Drive** con `mcp__Google_Drive__create_file`:
   - la carpeta `config.drive_carpeta` (buscarla con `search_files` y crearla si no existe);
   - dentro, una subcarpeta `AAAA-MM-DD tema`;
   - subir `video.mp4` y `portada.png` como referencia `sha256:<hash>:<ruta>` con `disableConversionToGoogleType: true`;
   - subir `publicacion.txt` y `fuentes.md` como texto.
9. Añadir el tema a `usados.json` y quitarlo de la cola. Commit y push (sin `salida/`).
10. Terminar con un resumen de una línea: tema, duración y enlace de Drive.

- [ ] **Paso 1:** escribir los archivos.
- [ ] **Paso 2: verificar a mano.** Seguir la skill de principio a fin con un **tema nuevo y un personaje nuevo**, para demostrar que la caja de efectos sirve para otros temas. Esperado:
  - el vídeo llega a Drive con portada y textos;
  - `usados.json` tiene 2 entradas;
  - hay un archivo nuevo en `personajes/`.
- [ ] **Paso 3:** enviar el vídeo al usuario. Commit, `feat(canal): skill hacer-video y segundo personaje`.

### Task 6: Automatización diaria y limpieza

**Archivos:**
- Borrar `canal/_prototipo/`.
- Crear `canal/LEEME.md`: cómo pedir un tema (`cola.txt`), cómo cambiar la voz o el ritmo (`config.json`) y dónde llegan los vídeos.

- [ ] **Paso 1: script de inicio.** Ejecutar desde el directorio padre del repo `pip install edge-tts` y comprobar que funciona. Proponer con `update_environment` el script:
  ```bash
  pip install -q edge-tts
  ```
  Proponer en la misma llamada quitar los hosts que ya no se usan: Openverse, Flickr, Wikimedia, Pexels, Hugging Face y Gemini.
- [ ] **Paso 2: tarea programada.** `create_trigger`:
  - `create_new_session_on_fire: true` y `connectors: ["Google Drive"]`;
  - todos los días a las 10:41, hora de Madrid: `CRON_TZ=Europe/Madrid 41 10 * * *`;
  - el prompt dice: "Usa la skill hacer-video del repositorio marte1234tt/marte1234tt (rama de trabajo) para crear y entregar el vídeo de hoy.";
  - `notifications: {push: true}`.
- [ ] **Paso 3:** lanzarla una vez con `fire_trigger`. Comprobar que la sesión termina con un vídeo nuevo en Drive.
- [ ] **Paso 4:** commit, `chore(canal): limpieza y documentación de uso`. Push.
