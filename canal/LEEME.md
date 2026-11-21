# ¿No lo sabías? — fábrica de vídeos (@nolosabias672)

Cada día una tarea programada de Claude abre una sesión, sigue la receta `.claude/skills/hacer-video/SKILL.md`
y te entrega un vídeo de curiosidades en dibujos animados.

## Qué recibes
- **El vídeo** (calidad completa): aviso en el móvil y el archivo en la app de Claude, listo para publicar.
- **En Google Drive → `¿No lo sabías?/AAAA-MM-DD tema · categoría · personaje/`**: `portada.png`,
  `publicacion.txt` (textos para Instagram, TikTok y YouTube) y `fuentes.md`.

## Cómo pedir temas
Escribe en el documento **`Temas pendientes`** de esa carpeta de Drive, uno por línea debajo de `----- TEMAS -----`.
Si está vacío, Claude elige (sobre todo historia y ciencia rara; ajusta los pesos en `config.json` → `categorias`).

## Cómo cambiar cosas
| Quiero… | Dónde |
|---|---|
| otra voz o ritmo | `config.json` → `voz` (`nombre`, `velocidad` en %, `pausa` en segundos) |
| otra duración | `config.json` → `duracion` (mínimo 61 s para cobrar en TikTok/Facebook) |
| música propia | archivos libres de derechos en `musica/` |
| cambiar el nombre de la cuenta | `config.json` → `cuenta` y `etiqueta` |

## Hacer un vídeo a mano
```bash
cd canal && bash motor/hacer.sh ejemplos/cleopatra/guion.json   # → salida/AAAA-MM-DD-cleopatra/
```

## Tests
```bash
cd canal && python3 -m pytest -m "not lento" && node --test tests/efectos.test.mjs
python3 -m pytest -m lento      # fabrica el vídeo del pulpo entero (~2,5 min)
```
