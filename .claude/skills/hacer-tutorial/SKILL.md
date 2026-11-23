---
name: hacer-tutorial
description: Crea vídeos tutoriales de estudio (uso personal, no para publicar) a partir del material de clase del usuario, con terminal animada de Cisco IOS, pantalla tipo Packet Tracer y un guía animado (el "profe" con la foto del usuario). Úsala cuando pida un vídeo para estudiar, explicar comandos o un tema de clase.
---

# Tutorial de estudio (uso personal)

Todo vive en `canal/` (ejecuta desde ahí). Ejemplo completo y probado: `canal/temas/tutorial-switch/generar.py`
(genera `basica.json` y `vlans.json`). **Copia ese patrón**: función `tutorial()`, constante `ROBOT` (posición del guía
en las escenas de terminal), escenas con `lineas` (terminal) o `topo` (Packet Tracer) o `efectos` libres.

## 1. Material
- El usuario adjunta apuntes / cheat sheet (.docx, .pdf). Cópialo a una carpeta temporal y extrae el texto
  (`pandoc -t plain` o `python3 -I` leyendo `word/document.xml`). Usa **exactamente** los comandos, nombres y ejemplos del material
  (suelen estar en catalán: no los traduzcas; la narración va en castellano).
- Si algo del ejercicio no está claro (números de VLAN, puertos, nombres), **pregunta antes** de fabricar.

## 2. Guía (personaje)
- `personaje: "profe"` = cuerpo de dibujos con camisa blanca y **la foto del usuario como cabeza**.
  La foto debe estar en `canal/personajes/privado/profe.jpg` (carpeta ignorada por git: **nunca la subas**).
  Si no existe, pídele al usuario que la adjunte y cópiala ahí. Si no la tiene, usa `personaje: "robot"`.

## 3. Guion (preferencias del usuario)
- Uno o dos vídeos cortos (60–100 s cada uno) mejor que uno largo. `etiqueta: "TUTORIAL · <TEMA>"`, `duracion: {min: 30, max: 300}`.
- Primera escena: el guía grande presentando. Si hay red, una escena `topo` con la pantalla de Packet Tracer.
- Luego, escenas de terminal **paso a paso**: cada comando aparece cuando la voz lo dice; explica para qué sirve cada uno
  y en qué modo estás. Termina comprobando (`show ...`) y guardando (`copy running-config startup-config`).
- Hazlo **como pide el ejercicio**: si son varios puertos concretos, configúralos uno a uno (no uses `interface range`
  salvo que el ejercicio lo pida o tenga sentido y lo expliques).
- Títulos ≤ 24 caracteres; líneas de terminal ≤ 50 caracteres (si no, se cortan); sin "…" en la narración.

## 4. Efectos específicos
- `terminal`: `{lineas: [{prompt, cmd, desde, salida?: [..], aparece?}], titulo, y1, extremidad, senala}`.
  El chip de modo (USUARIO / PRIVILEGIADO / CONFIG. GLOBAL / LÍNEA / INTERFAZ / VLAN) sale solo del prompt.
  En el generador, cada escena hereda las últimas líneas de la anterior (historial).
- `topologia`: switch en el centro y 6 PCs (PC0-PC1 izquierda apilados, PC2 encima y PC3 debajo del switch,
  PC4-PC5 derecha apilados). Parámetros: `puertos: [6 etiquetas]`, `vlans: [{num, nombre, color, desde}]` (colorea
  de dos en dos: PC0-1, PC2-3, PC4-5 y añade leyenda), `pings: [{de, a, ok, desde}]` (sobre que viaja; ✓ / ✗),
  `clic: "palabra"` (cursor que hace clic en el switch y abre la pestaña CLI).
- `desde` de cada línea = una palabra **única** de la narración de esa escena, `"palabra+1.2"`, o segundos (número).
  Deja ≥ 1,2 s entre comandos largos para que no se pisen.

## 5. Fabricar y revisar
```bash
cd canal && python3 temas/<tema>/generar.py
python3 -m motor.preparar temas/<tema>/<x>.json salida/prueba   # ningún "AVISO pista no encontrada"
bash motor/hacer.sh temas/<tema>/<x>.json                       # → LISTO salida/<fecha-tema>/
```
Mira `fotogramas/` (nada cortado ni tapado). Corrige y repite.

## 6. Entregar
`SendUserFile` con el/los `video.mp4` (calidad completa). Nada de Drive. Commit + push solo del código y guiones
(nunca `salida/`, `.mp4` ni `personajes/privado/`).
