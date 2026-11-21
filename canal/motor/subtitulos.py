"""Subtítulos ASS palabra a palabra con la palabra actual resaltada en amarillo."""

W, H = 1080, 1920
AMARILLO = "&H3FD2FF&"  # #FFD23F en formato BGR de ASS


def escapar_ass(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def _t(s: float) -> str:
    h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def _bloques(palabras):
    """Agrupa en bloques de ≤3 palabras y ≤16 caracteres, cortando en pausas > 0,3 s."""
    bloques, act = [], []
    for w in palabras:
        if act and (len(act) >= 3 or sum(len(x[2]) for x in act) + len(w[2]) > 16 or w[0] - act[-1][1] > 0.3):
            bloques.append(act); act = []
        act.append(w)
    if act:
        bloques.append(act)
    return bloques


def subtitulos(palabras: list[tuple[float, float, str]], ruta: str) -> None:
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Display Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,2,60,60,340,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    bloques = _bloques(palabras)
    lineas = []
    for bi, b in enumerate(bloques):
        fin_bloque = bloques[bi + 1][0][0] if bi + 1 < len(bloques) else b[-1][1] + 0.4
        fin_bloque = min(fin_bloque, b[-1][1] + 0.5)
        for i, w in enumerate(b):
            ini = w[0]
            fin = b[i + 1][0] if i + 1 < len(b) else fin_bloque
            partes = []
            for j, x in enumerate(b):
                tx = escapar_ass(x[2].upper())
                partes.append("{\\c" + AMARILLO + "\\fscx108\\fscy108}" + tx + "{\\c&HFFFFFF&\\fscx100\\fscy100}" if j == i else tx)
            pop = "{\\t(0,80,\\fscx104\\fscy104)\\t(80,160,\\fscx100\\fscy100)}" if i == 0 else ""
            lineas.append(f"Dialogue: 0,{_t(ini)},{_t(fin)},Sub,,0,0,0,,{pop}{' '.join(partes)}")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(lineas) + "\n")
