# Cómo pedir vídeos a Claude Code (sin perder nada)

## Lo importante
Todo lo que hemos construido (estilo, voz, personajes, terminal, Packet Tracer, recetas) está **guardado en el código**,
no en la memoria del chat. Una conversación nueva lo hace igual si le pegas el mensaje de abajo.

**Abre una conversación NUEVA para cada vídeo o tanda** (gasta mucho menos):
claude.ai/code → **Nueva sesión** → repositorio **marte1234tt/marte1234tt** → entorno **marte1234tt** (no "Default").

---

## A) Vídeo de estudio (tutorial con tu cara)
1. Adjunta **tus apuntes** (.docx/.pdf) y **tu foto** (la misma de siempre).
2. Pega esto y cambia lo de MAYÚSCULAS:

```
Ejecuta primero:
git fetch origin ccr-a1090919-8ybl6i && git checkout FETCH_HEAD -- canal .claude && pip install -q edge-tts==7.3.1

Lee canal/CONTEXTO.md y .claude/skills/hacer-tutorial/SKILL.md enteros y síguelos.
Copia la foto que te adjunto a canal/personajes/privado/profe.jpg (no la subas a git).
Hazme un vídeo de estudio explicando: TEMA (por ejemplo: "dúplex, velocidad y apagar puertos" de los apuntes adjuntos).
Detalles del ejercicio: DETALLES (o bórralo).
Mándame el vídeo por aquí.
```

## B) Vídeo de curiosidades para la cuenta
```
Ejecuta primero:
git fetch origin ccr-a1090919-8ybl6i && git checkout FETCH_HEAD -- canal .claude && pip install -q edge-tts==7.3.1

Lee canal/CONTEXTO.md y .claude/skills/hacer-video/SKILL.md enteros y síguelos para hacer un vídeo de @nolosabias672.
TEMA: TEMA (o borra esta línea para que lo elijas tú)
Temas ya hechos (no los repitas): el pulpo, Cleopatra, Napoleón no era bajito
Mándame por aquí el vídeo, la portada y el texto de publicación. No uses Google Drive.
```
Después de cada vídeo de curiosidades, añade el tema a "Temas ya hechos".

---

## Si prefieres seguir en ESTA conversación
Escribe esto para resumirla y gastar menos:
```
/compact Conserva: el proyecto está en canal/ (rama ccr-a1090919-8ybl6i); contexto en canal/CONTEXTO.md; recetas en .claude/skills/hacer-video y .claude/skills/hacer-tutorial; la foto del profe está en canal/personajes/privado/profe.jpg; entrego vídeos por SendUserFile, sin Drive.
```
