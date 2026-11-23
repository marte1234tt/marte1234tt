# Contexto del proyecto (para Claude)

**Usuario:** estudiante de SMX (MP0225 Xarxes locals). Habla castellano; sus apuntes de clase están en catalán.
Prefiere respuestas cortas y prácticas. **Nada de Google Drive, tareas programadas ni automatizaciones raras**:
todo se hace en la conversación y los vídeos se entregan por aquí con `SendUserFile`.

## Dos tipos de vídeo
1. **Curiosidades** para la cuenta @nolosabias672 (Instagram/TikTok/YouTube Shorts) → skill `hacer-video`.
   - Dibujos animados: un protagonista dibujado por tema; datos animados sobre él, sincronizados con la voz.
   - Temas: sobre todo **historia y ciencia rara** (también cuerpo humano, espacio, objetos, comida, animales).
   - 61–80 s (TikTok/Facebook solo pagan > 60 s). Gancho, 5–6 datos, encuesta A/B/C/D, "¡Síguenos…!".
   - Todos los datos con ≥ 2 fuentes. Entregar vídeo + portada + publicacion.txt.
   - Hechos: el pulpo, Cleopatra (más cerca de la Luna que de las pirámides), Napoleón no era bajito.
   - Pendiente de decidir: tono más "callejero" (estilo vídeos virales de Murcia) — propuesto "picante sin tacos fuertes".
2. **Tutoriales de estudio** (personales, NO se publican) → skill `hacer-tutorial`.
   - Guía = "profe": cuerpo dibujado + **foto del usuario como cabeza** (`canal/personajes/privado/profe.jpg`, nunca a git).
   - Terminal Cisco IOS animada + pantalla tipo Packet Tracer (switch + 6 PCs). Ver `temas/tutorial-switch/`.
   - Hechos: configuración básica del switch; 3 VLANs (10 Vendes Fa0/1-2, 20 Compres Fa0/3-4, 30 Direccio Fa0/5-6).

## Decisiones fijas
- Voz: edge-tts `es-ES-AlvaroNeural`, velocidad +10 %, pausa 0,3 s entre frases (ritmo intermedio: ni lento ni atropellado).
- Marca: fondo azul marino, acento amarillo #FFD23F, Inter Display Black, subtítulos palabra a palabra en amarillo.
- Entorno de Claude Code: **marte1234tt** (tiene permitido speech.platform.bing.com para la voz).
- Código en la rama `ccr-a1090919-8ybl6i` del repo `marte1234tt/marte1234tt`.
