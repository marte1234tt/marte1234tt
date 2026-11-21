---
name: hacer-video
description: Crea y entrega el vídeo diario de la cuenta de curiosidades @nolosabias672 (dibujos animados, voz, subtítulos, portada y textos) y lo sube a Google Drive. Úsala cuando pidan "el vídeo de hoy", un vídeo sobre un tema concreto, o cuando la tarea programada diaria lo indique.
---

# Hacer el vídeo de «¿No lo sabías?»

Todo vive en `canal/` (ejecuta los comandos desde ahí). Lee `canal/config.json` primero.
Ejemplo completo de guion: `canal/ejemplos/pulpo/guion.json` (animales) y `canal/ejemplos/cleopatra/guion.json` (historia).

## 1. Elegir el tema
1. Si `temas/cola.txt` tiene líneas, usa la primera (y quítala al terminar).
2. Si no, elige categoría con los pesos de `config.categorias` (historia y ciencia rara son las principales),
   **sin repetir la categoría de los 2 últimos** de `temas/usados.json`, y busca en la web una curiosidad
   sorprendente y verificable de esa categoría que **no esté ya en `usados.json`**.
3. Busca un tema con un "giro" (algo que la gente cree y no es, o una comparación que vuela la cabeza).

## 2. Investigar
- Cada dato del guion: **al menos 2 fuentes fiables** (prensa científica, museos, universidades, enciclopedias).
- Si un dato es discutido, dilo como tal ("según Plutarco…", "no se sabe seguro") o descártalo. Nunca inventes.
- Guarda las URLs para `fuentes`.

## 3. Escribir el guion
Crea `canal/temas/AAAA-MM-DD-<slug>/guion.json` con el formato del ejemplo:
- `tema`, `categoria`, `personaje`, `escenas[]` (`titulo` en MAYÚSCULAS y corto, `texto`, `efectos[]`),
  `encuesta` (4 opciones cortas), `publicacion` (`instagram` con gancho + encuesta A/B/C/D + "Síguenos…" + **5 hashtags**,
  `tiktok` corto con 6 hashtags, `youtube_titulo` con `#shorts #curiosidades`), `fuentes`, `portada`
  (`escena`, `t`, `linea1`, `linea2`, `color2`, `banda`, `color_banda`).
- **Ritmo**: frases cortas, gancho de golpes en la primera escena, 5–6 datos, penúltima escena con el dato más loco,
  última escena = encuesta + "¡Y síguenos para más curiosidades!" (efectos `encuesta` y `cierre` desde "síguenos").
- **Nunca uses "…"** en `texto` (provoca pausas largas). Escribe los números como se leen bien ("2.500", "1969").
- **Efectos disponibles** (todos con `desde`/`hasta`: palabra del texto de la escena, `"palabra+0.5"` o segundos;
  `desde: -1` = ya visible al empezar la escena, para efectos que continúan de la escena anterior):
  `entrada`, `mirar{x|"vaiven",y}`, `posicion{x,y,escala}`, `rayosX`, `organo{id}`, `latido{velocidad}`, `flujo{color}`,
  `luces`, `agitar{intensidad}`, `gris`, `camuflaje{colores}`, `senalar{extremidad,objetivo:[x,y]}`,
  `objeto{forma:"cangrejo"|"svg", svg, pos, entra, asustado}`, `alcanzar{extremidad,objetivo:"objeto"}`,
  `saborear{extremidad}`, `aplastar{escala}`, `antenas`, `iconos{forma,n,pos,color}`,
  `etiqueta{texto (admite \n),pos,ancla,fondo,color}`, `bocadillo{texto,pos}`, `comparacion{izq,der,desde_der}`,
  `contador{numero,etiqueta,pos}`, `sello{texto,pos,color,rot}`, `linea_tiempo{rango,y,puntos[{anio,etiqueta,icono,desde}],tramos[{de,a,texto,desde}]}`,
  `encuesta`, `cierre`.
- Emojis dentro de `objeto` svg (`<text font-size="160" text-anchor="middle" y="55">🌕</text>`) o de `icono` funcionan.
- Zonas: título arriba (y≈330), etiquetas entre y=420 y y=1400, **nada importante por debajo de 1400** (subtítulos).
- Si un efecto que necesitas no existe, puedes crear `extra.js` junto al guion (`"js": "extra.js"`) que añada
  `EFECTOS.mi_efecto = {estado(c,e,td,t){...}, dibujo(c,e,td,t){...}}` (mira `canal/efectos/efectos.js`).

## 4. Personaje
- Si ya existe en `canal/personajes/`, reutilízalo. Si no, créalo siguiendo `canal/personajes/LEEME.md`.
- Comprueba 3 capturas antes de seguir:
  `node -e` con `motor/render.js` (`abrir`) o ejecuta el vídeo y mira `fotogramas/`.

## 5. Fabricar
```bash
cd canal && bash motor/hacer.sh temas/<carpeta>/guion.json
```
- Código **3** (`DURACION_CORTA`): añade un dato (otra escena) y repite.
- Código **4** (`NO_CUMPLE`): corrige lo que diga (p. ej. si dura > 80 s, recorta texto) y repite.
- Al acabar imprime `LISTO <carpeta>`.

## 6. Revisar (obligatorio)
Mira las 10 imágenes de `<carpeta>/fotogramas/` y `portada.png`:
- ningún texto encima de otro, cortado o fuera de pantalla; nada tapando los subtítulos;
- el personaje se ve entero y bien; cada efecto encaja con lo que se dice;
- la portada se entiende en pequeño.
Corrige y repite como mucho 2 veces. Si sigue mal, entrega igualmente con " (revisar)" en el nombre de la carpeta de Drive.

## 7. Entregar
**El vídeo NO va a Drive** (el conector admite ~3 MB por llamada y los vídeos pesan ~8 MB).
1. **Vídeo:** envíalo con `SendUserFile` (`files: [<ruta>/video.mp4]`, `status: "proactive"`, `display: "render"`,
   `caption: "<tema> · <duración> s · listo para publicar"`). Le llega al usuario a la app con aviso al móvil.
2. **Drive** (portada y textos): busca la carpeta `config.drive_carpeta` con `mcp__Google_Drive__search_files`
   (`title contains 'No lo sabías' and mimeType = 'application/vnd.google-apps.folder'`); si no existe, créala
   (`create_file`, `contentMimeType: application/vnd.google-apps.folder`). Dentro, crea la subcarpeta `AAAA-MM-DD <tema>`.
3. Sube `portada.png` (`image/png`, `base64Content` = `sha256:<hash>:<ruta absoluta>`, hash con `sha256sum`,
   `disableConversionToGoogleType: true`). Si algún archivo pasa de 3 MB, no lo subas: mándalo también con `SendUserFile`.
4. Sube `publicacion.txt` y `fuentes.md` con `textContent` (`text/plain`, `disableConversionToGoogleType: true`).

## 8. Cerrar
- Añade a `temas/usados.json` `{fecha, tema, categoria, personaje}`; quita el tema de `cola.txt` si venía de ahí.
- Commit (guion, personaje nuevo, usados.json; nunca `salida/` ni `.mp4`) y push a la rama de trabajo.
- Termina con una línea: tema · duración · enlace a la carpeta de Drive (el vídeo ya va en el aviso de la app).
