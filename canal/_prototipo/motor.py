"""Prototipo (desechable) del motor de vídeos de curiosidades.

Uso: python3 motor.py guion.json carpeta_salida
"""
import asyncio, json, math, os, random, ssl, subprocess, sys, urllib.parse, urllib.request
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
PAUSA = 0.22  # silencio entre escenas (s)
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"

PALETA = {
    "fondo": (11, 19, 32), "fondo2": (22, 38, 64), "acento": (255, 210, 63),
    "acento2": (46, 196, 182), "blanco": (255, 255, 255), "gris": (150, 165, 185),
}

# ---------------------------------------------------------------- utilidades
def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def ease_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

_fonts = {}
def font(path, size):
    k = (path, size)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

_txt = {}
def texto_img(txt, size, color=(255, 255, 255), path=FONT_BLACK, sombra=True, max_w=980):
    """Devuelve una imagen RGBA con el texto (multilínea) centrado."""
    k = (txt, size, color, path, sombra, max_w)
    if k in _txt: return _txt[k]
    f = font(path, size)
    while True:
        lineas = txt.split("\n")
        anchos = [f.getbbox(l)[2] - f.getbbox(l)[0] for l in lineas]
        if max(anchos) <= max_w or size < 30: break
        size -= 4; f = font(path, size)
    asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.05)
    w = max(anchos) + 40; h = lh * len(lineas) + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lineas):
        lw = anchos[i]; x = (w - lw) // 2 - f.getbbox(l)[0]; y = 20 + i * lh
        if sombra:
            d.text((x + 5, y + 7), l, font=f, fill=(0, 0, 0, 150))
        d.text((x, y), l, font=f, fill=color + (255,) if len(color) == 3 else color)
    _txt[k] = im
    return im

def pegar(base, im, cx, cy, escala=1.0, alpha=1.0):
    if escala <= 0.01 or alpha <= 0.01: return
    if abs(escala - 1) > 0.01:
        im = im.resize((max(1, int(im.width * escala)), max(1, int(im.height * escala))), Image.BILINEAR)
    if alpha < 0.99:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def capa_draw(fr):
    """Capa transparente para dibujar formas semitransparentes (se fusiona con fusionar())."""
    c = Image.new("RGBA", fr.size, (0, 0, 0, 0)); return c, ImageDraw.Draw(c)

def corazon(d, cx, cy, s, fill):
    pts = []
    for i in range(60):
        t = i / 60 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    d.polygon(pts, fill=fill)

def gota(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    d.polygon([(cx - r * 0.86, cy - r * 0.5), (cx + r * 0.86, cy - r * 0.5), (cx, cy - r * 2.1)], fill=fill)

# ---------------------------------------------------------------- fondo
def fondo_base(seed):
    """Degradado radial + viñeta; se calcula una vez por escena."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W * 0.5) / W) ** 2 + ((y - H * 0.38) / H) ** 2)
    t = np.clip(r * 1.6, 0, 1)[..., None]
    c1 = np.array(PALETA["fondo2"], np.float32); c2 = np.array(PALETA["fondo"], np.float32)
    arr = c1 * (1 - t) + c2 * t
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")

def burbujas(seed, n=22):
    rnd = random.Random(seed)
    return [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(6, 26), rnd.uniform(25, 70)) for _ in range(n)]

def dibuja_burbujas(fr, bs, t):
    c, d = capa_draw(fr)
    for x, y0, r, v in bs:
        y = (y0 - v * t) % (H + 60) - 30
        xx = x + 12 * math.sin(t * 1.3 + y0)
        d.ellipse([xx - r, y - r, xx + r, y + r], outline=(255, 255, 255, 34), width=3)
    fr.alpha_composite(c)

# ---------------------------------------------------------------- escenas
def capa_comun(fr, t, dur, inicio_total, total, idx):
    c, dc = capa_draw(fr); dc.rectangle([0, 0, W, 14], fill=(255, 255, 255, 40)); fr.alpha_composite(c)
    d = ImageDraw.Draw(fr)
    # barra de progreso superior
    p = (inicio_total + t) / total
    d.rectangle([0, 0, int(W * p), 14], fill=PALETA["acento"] + (255,))
    # etiqueta de marca
    tag = texto_img("¿SABÍAS QUE…?", 40, PALETA["fondo"], FONT_BLACK, sombra=False)
    pw, ph = tag.width + 30, tag.height - 6
    x0, y0 = (W - pw) // 2, 110
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=ph // 2, fill=PALETA["acento"] + (255,))
    fr.alpha_composite(tag, (x0 + 15, y0 - 3))

CARD_W = 940
def escena_foto(fr, t, dur, v, ctx):
    fr.paste(ctx["fondo_foto"], (0, 0))
    img, cw, ch = ctx["foto"], ctx["card_w"], ctx["card_h"]
    # zoom lento dentro de la tarjeta
    z = 1.0 + 0.12 * (t / dur)
    sw, sh = img.width / z, img.height / z
    ox = (img.width - sw) * (0.5 + 0.3 * math.sin(t / dur * math.pi - math.pi / 2) / 2); oy = (img.height - sh) / 2
    crop = img.crop((int(ox), int(oy), int(ox + sw), int(oy + sh))).resize((cw, ch), Image.BILINEAR).convert("RGBA")
    crop.putalpha(ctx["mascara"])
    a = ease_back(t / 0.5)
    card = Image.new("RGBA", (cw + 24, ch + 24), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, cw + 23, ch + 23], radius=52, fill=(255, 255, 255, 255))
    card.alpha_composite(crop, (12, 12))
    pegar(fr, ctx["sombra_card"], W / 2 + 10, 820 + 24, 0.85 + 0.15 * a, min(1, t / 0.25))
    pegar(fr, card, W / 2, 820, 0.85 + 0.15 * a, min(1, t / 0.25))
    pegar(fr, texto_img(v["titulo"], 108, PALETA["acento"]), W / 2, 330, 0.6 + 0.4 * ease_back(t / 0.45), min(1, t / 0.2))

def escena_contador(fr, t, dur, v, ctx):
    n = v["numero"]; k = ease_out(t / 0.9)
    val = int(round(n * k))
    pegar(fr, texto_img(str(val), 420, PALETA["acento"]), W / 2, 560, 0.7 + 0.3 * ease_back(t / 0.5))
    pegar(fr, texto_img(v["etiqueta"], 96), W / 2, 830, 1, min(1, t / 0.4))
    d = ImageDraw.Draw(fr)
    for i in range(n):
        ti = t - 0.9 - i * 0.35
        if ti <= 0: continue
        s = 5.2 * ease_back(ti / 0.4)
        latido = 1 + 0.06 * math.sin(t * 7 + i)
        corazon(d, W / 2 + (i - (n - 1) / 2) * 260, 1080, s * latido, (230, 57, 70, 255))

def escena_comparacion(fr, t, dur, v, ctx):
    d = ImageDraw.Draw(fr)
    for i, lado in enumerate([v["izq"], v["der"]]):
        ti = t - i * 1.6
        if ti <= 0: continue
        a = ease_back(ti / 0.5); cx = W * (0.28 if i == 0 else 0.72)
        gota(d, cx, 720, 150 * a, hex2rgb(lado["color"]) + (255,))
        pegar(fr, texto_img(lado["texto"], 78), cx, 960, 1, min(1, ti / 0.3))
        pegar(fr, texto_img(lado["sub"], 52, PALETA["gris"], FONT_BOLD), cx, 1050, 1, min(1, ti / 0.3))
    if t > 1.6:
        pegar(fr, texto_img("VS", 90, PALETA["acento"]), W / 2, 700, ease_back((t - 1.6) / 0.4))

def escena_tarta(fr, t, dur, v, ctx):
    cx, cy, r = W / 2, 640, 290
    c, dc = capa_draw(fr); dc.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 30)); fr.alpha_composite(c)
    d = ImageDraw.Draw(fr)
    ang = 360 * v["fraccion"] * ease_out((t - 0.2) / 1.4)
    if ang > 0.5:
        d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + ang, fill=PALETA["acento2"] + (255,))
    ri = r * 0.58
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=PALETA["fondo2"] + (255,))
    pegar(fr, texto_img(v["grande"], 170, PALETA["blanco"]), cx, cy, ease_back(t / 0.5))
    pegar(fr, texto_img(v["etiqueta"], 70), W / 2, 1110, 1, min(1, (t - 0.6) / 0.4))

def escena_colores(fr, t, dur, v, ctx):
    pegar(fr, texto_img(v["titulo"], 120, PALETA["acento"]), W / 2, 330, ease_back(t / 0.45))
    cols = [(230, 57, 70), (255, 159, 28), (255, 210, 63), (46, 196, 182), (58, 134, 255), (131, 56, 236),
            (255, 0, 110), (6, 214, 160), (17, 138, 178)]
    d = ImageDraw.Draw(fr)
    gris = 0.5 + 0.5 * math.sin(t * 1.6 - 1.5)  # pasa de color a gris y vuelve
    for i, c in enumerate(cols):
        ti = t - 0.3 - i * 0.07
        if ti <= 0: continue
        s = ease_back(ti / 0.4); g = sum(c) / 3
        cc = tuple(int(ch * (1 - gris) + g * gris) for ch in c)
        x = W / 2 + (i % 3 - 1) * 230; y = 790 + (i // 3 - 1) * 230; h = 95 * s
        d.rounded_rectangle([x - h, y - h, x + h, y + h], radius=int(28 * s) + 1, fill=cc + (255,))
    pegar(fr, texto_img(v["sub"], 56, PALETA["gris"], FONT_BOLD), W / 2, 1170, 1, min(1, (t - 0.8) / 0.4))

def escena_encuesta(fr, t, dur, v, ctx):
    pegar(fr, texto_img(v["titulo"], 120, PALETA["acento"]), W / 2, 330, ease_back(t / 0.45))
    d = ImageDraw.Draw(fr); letras = "ABCD"
    for i, op in enumerate(v["opciones"]):
        ti = t - 0.4 - i * 0.3
        if ti <= 0: continue
        a = ease_out(ti / 0.45); y = 540 + i * 165; x0 = 110 + (1 - a) * 600
        c, dc = capa_draw(fr)
        dc.rounded_rectangle([x0, y - 62, x0 + 860, y + 62], radius=34, fill=(255, 255, 255, int(28 + 20 * a)),
                             outline=(255, 255, 255, 90), width=3)
        fr.alpha_composite(c)
        d.ellipse([x0 + 22, y - 44, x0 + 110, y + 44], fill=PALETA["acento"] + (255,))
        li = texto_img(letras[i], 54, PALETA["fondo"], sombra=False); fr.alpha_composite(li, (int(x0 + 66 - li.width / 2), int(y - li.height / 2)))
        oi = texto_img(op, 56, sombra=False, path=FONT_BOLD); fr.alpha_composite(oi, (int(x0 + 130), int(y - oi.height / 2)))

ESCENAS = {"foto": escena_foto, "contador": escena_contador, "comparacion": escena_comparacion,
           "tarta": escena_tarta, "colores": escena_colores, "encuesta": escena_encuesta}

def render_escena(args):
    idx, v, dur, inicio, total, foto_path, out = args
    ctx = {}
    base = fondo_base(idx)
    if v["tipo"] == "foto":
        im = Image.open(foto_path).convert("RGB")
        # fondo: la misma foto, desenfocada y oscurecida
        esc = max(W / im.width, H / im.height)
        bg = im.resize((int(im.width * esc) + 1, int(im.height * esc) + 1), Image.BILINEAR)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = bg.filter(ImageFilter.GaussianBlur(40))
        bg = Image.blend(bg, Image.new("RGB", (W, H), PALETA["fondo"]), 0.55)
        ctx["fondo_foto"] = bg.convert("RGBA")
        # tarjeta con la foto
        cw = CARD_W; ch = min(1000, int(cw * im.height / im.width))
        esc = max(cw * 1.0 / im.width, ch * 1.0 / im.height)
        ctx["foto"] = im.resize((int(im.width * esc) + 1, int(im.height * esc) + 1), Image.LANCZOS)
        if ctx["foto"].height > ch:  # recorta al alto de la tarjeta
            f = ctx["foto"]; y0 = (f.height - ch) // 2; ctx["foto"] = f.crop((0, y0, f.width, y0 + ch))
        ctx["card_w"], ctx["card_h"] = cw, ch
        m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=42, fill=255)
        ctx["mascara"] = m
        s = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle([40, 40, cw + 40, ch + 40], radius=52, fill=(0, 0, 0, 160))
        ctx["sombra_card"] = s.filter(ImageFilter.GaussianBlur(22))
    bs = burbujas(idx)
    n = int(round(dur * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        fr = base.copy()
        if v["tipo"] != "foto": dibuja_burbujas(fr, bs, t + idx * 3)
        ESCENAS[v["tipo"]](fr, t, dur, v, ctx)
        capa_comun(fr, t, dur, inicio, total, idx)
        # transición de entrada: barrido de color
        if t < 0.18 and idx > 0:
            k = 1 - t / 0.18
            ImageDraw.Draw(fr).rectangle([0, 0, W, int(H * k)], fill=PALETA["acento"] + (255,))
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    return out

# ---------------------------------------------------------------- voz
async def tts(texto, voz, vel, out):
    import edge_tts, edge_tts.communicate as ec
    ec._SSL_CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE"))
    c = edge_tts.Communicate(texto, voz, rate=vel, boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY"))
    words = []
    with open(out, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    return words

def duracion(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())

# ---------------------------------------------------------------- imágenes
UA = {"User-Agent": "Mozilla/5.0 (compatible; curiosidades-bot/0.1)"}
def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()

def buscar_foto(v, out):
    """Descarga la foto elegida (v['id'] de Openverse) a tamaño completo vía el proxy de Openverse."""
    if "id" in v:
        r = json.loads(_get(f"https://api.openverse.org/v1/images/{v['id']}/"))
    else:
        url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
            {"q": v["busqueda"], "license_type": "commercial,modification", "page_size": 20, "category": "photograph"})
        r = next(x for x in json.loads(_get(url))["results"] if (x.get("width") or 0) >= 1000)
    raw = _get(f"https://api.openverse.org/v1/images/{r['id']}/thumb/?full_size=true")
    Image.open(BytesIO(raw)).verify(); open(out, "wb").write(raw)
    return f'"{r["title"]}" de {r.get("creator") or "autor desconocido"} ({r["license"].upper()} {r.get("license_version") or ""}) — {r.get("foreign_landing_url")}'

# ---------------------------------------------------------------- subtítulos
def ass_time(s):
    h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"

def subtitulos(palabras, out):
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
    # agrupar en bloques de hasta 3 palabras / 16 caracteres, cortando en pausas
    bloques, act = [], []
    for w in palabras:
        if act and (len(act) >= 3 or sum(len(x[2]) for x in act) + len(w[2]) > 16 or w[0] - act[-1][1] > 0.3):
            bloques.append(act); act = []
        act.append(w)
    if act: bloques.append(act)
    lineas = []
    for bi, b in enumerate(bloques):
        fin_bloque = bloques[bi + 1][0][0] if bi + 1 < len(bloques) else b[-1][1] + 0.4
        fin_bloque = min(fin_bloque, b[-1][1] + 0.5)
        for i, w in enumerate(b):
            ini = w[0]; fin = b[i + 1][0] if i + 1 < len(b) else fin_bloque
            partes = []
            for j, x in enumerate(b):
                tx = x[2].upper()
                partes.append("{\\c&H3FD2FF&\\fscx108\\fscy108}" + tx + "{\\c&HFFFFFF&\\fscx100\\fscy100}" if j == i else tx)
            pop = "{\\fad(0,0)\\t(0,80,\\fscx104\\fscy104)\\t(80,160,\\fscx100\\fscy100)}" if i == 0 else ""
            lineas.append(f"Dialogue: 0,{ass_time(ini)},{ass_time(fin)},Sub,,0,0,0,,{pop}{' '.join(partes)}")
    open(out, "w").write(cab + "\n".join(lineas) + "\n")

# ---------------------------------------------------------------- música (sintetizada para la muestra)
def musica(dur, out, sr=44100):
    t = np.arange(int(dur * sr)) / sr
    acordes = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    y = np.zeros_like(t)
    seg = 4.0
    for k in range(int(dur / seg) + 1):
        notas = acordes[k % 4]; t0 = k * seg
        m = (t >= t0) & (t < t0 + seg + 1.5); tt = t[m] - t0
        env = np.minimum(tt / 0.8, 1) * np.exp(-np.maximum(tt - seg, 0) * 3)
        for n in notas:
            f = 440 * 2 ** ((n - 69) / 12)
            y[m] += env * (np.sin(2 * np.pi * f * tt) * 0.5 + np.sin(2 * np.pi * f * 2 * tt) * 0.12)
        # arpegio suave
        for j in range(8):
            tn = t0 + j * 0.5; mm = (t >= tn) & (t < tn + 0.9); ta = t[mm] - tn
            f = 440 * 2 ** ((notas[j % 3] + 12 - 69) / 12)
            y[mm] += np.exp(-ta * 5) * np.sin(2 * np.pi * f * ta) * 0.35
    y = y / np.max(np.abs(y)) * 0.5
    fade = np.minimum(np.minimum(t / 1.5, 1), np.minimum((dur - t) / 2.0, 1))
    y = (y * fade * 32767).astype(np.int16)
    import wave
    with wave.open(out, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(y.tobytes())

# ---------------------------------------------------------------- principal
def main(guion_path, outdir):
    g = json.load(open(guion_path)); os.makedirs(outdir, exist_ok=True); tmp = os.path.join(outdir, "tmp"); os.makedirs(tmp, exist_ok=True)
    escenas = g["escenas"]
    print("1/5 voz…")
    palabras, durs, audios = [], [], []
    t_acum = 0.0
    for i, e in enumerate(escenas):
        mp3 = os.path.join(tmp, f"voz{i}.mp3")
        ws = asyncio.run(tts(e["narracion"], g["voz"], g.get("velocidad", "+0%"), mp3))
        d = duracion(mp3) + PAUSA
        palabras += [(a + t_acum, b + t_acum, x) for a, b, x in ws]
        durs.append(d); audios.append(mp3); t_acum += d
    total = t_acum
    print(f"   duración total: {total:.1f}s")
    lista = os.path.join(tmp, "voz.txt")
    # cada trozo con su pausa
    partes = []
    for i, a in enumerate(audios):
        w = os.path.join(tmp, f"voz{i}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-af", f"apad=pad_dur={PAUSA}", "-ar", "44100", "-ac", "1", w], check=True)
        partes.append(w)
    open(lista, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in partes))
    voz = os.path.join(tmp, "voz.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, voz], check=True)

    print("2/5 imágenes…")
    creditos = []
    fotos = {}
    for i, e in enumerate(escenas):
        if e["visual"]["tipo"] == "foto":
            p = os.path.join(tmp, f"foto{i}.jpg")
            creditos.append(buscar_foto(e["visual"], p)); fotos[i] = p

    print("3/5 animación…")
    trabajos, ini = [], 0.0
    for i, e in enumerate(escenas):
        trabajos.append((i, e["visual"], durs[i], ini, total, fotos.get(i), os.path.join(tmp, f"esc{i}.mp4"))); ini += durs[i]
    with ProcessPoolExecutor(4) as ex:
        clips = list(ex.map(render_escena, trabajos))
    open(os.path.join(tmp, "clips.txt"), "w").write("".join(f"file '{os.path.abspath(c)}'\n" for c in clips))
    mudo = os.path.join(tmp, "mudo.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "clips.txt"), "-c", "copy", mudo], check=True)

    print("4/5 subtítulos y música…")
    ass = os.path.join(tmp, "subs.ass"); subtitulos(palabras, ass)
    mus = os.path.join(tmp, "musica.wav"); musica(total, mus)

    print("5/5 montaje final…")
    final = os.path.join(outdir, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mudo, "-i", voz, "-i", mus, "-filter_complex",
                    f"[0:v]ass={ass}[v];[2:a]volume=0.16[m];[1:a]volume=1.0,asplit[va][vs];"
                    "[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];"
                    "[va][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", final], check=True)
    pub = g["publicacion"] + "\n\nImágenes: " + " | ".join(creditos) + "\n"
    open(os.path.join(outdir, "publicacion.txt"), "w").write(pub)
    open(os.path.join(outdir, "fuentes.md"), "w").write("# Fuentes\n\n" + "\n".join("- " + f for f in g["fuentes"]) + "\n")
    print("listo:", final, f"{duracion(final):.1f}s", f"{os.path.getsize(final)/1e6:.1f} MB")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
