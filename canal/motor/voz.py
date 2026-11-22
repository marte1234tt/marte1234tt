"""Voz del canal: edge-tts frase a frase, con entonación propia y pausas controladas."""
import asyncio, json, os, re, ssl, subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESPERAS = [2, 4, 8]  # segundos entre reintentos si falla la red


def cargar_config() -> dict:
    with open(os.path.join(RAIZ, "config.json"), encoding="utf-8") as f:
        return json.load(f)


def frases(texto: str) -> list[str]:
    """Corta en . ! ? seguidos de espacio (así «2.500» o «¿¡Cómo!?» no se parten) y conserva el final sin punto."""
    trozos = re.split(r"(?<=[.!?…])\s+", texto.strip())
    return [t.strip() for t in trozos if re.search(r"\w", t)]


def prosodia(frase: str, i: int, base: int) -> tuple[str, str]:
    """Velocidad y tono para una frase: preguntas más agudas, exclamaciones con más energía."""
    rate, pitch = base, 0
    if "?" in frase:
        pitch += 6
    if "!" in frase:
        pitch += 4
        rate += 6
    if len(frase.split()) <= 3:
        rate += 4
    pitch += [0, -2, 2, -1][i % 4]
    return f"{rate:+d}%", f"{pitch:+d}Hz"


async def _edge(texto, nombre, rate, pitch, mp3):
    import edge_tts, edge_tts.communicate as ec
    if os.environ.get("SSL_CERT_FILE"):
        ec._SSL_CTX = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
    c = edge_tts.Communicate(texto, nombre, rate=rate, pitch=pitch, boundary="WordBoundary",
                             proxy=os.environ.get("HTTPS_PROXY"))
    ws = []
    with open(mp3, "wb") as fh:
        async for ch in c.stream():
            if ch["type"] == "audio":
                fh.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                ws.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    return ws


def duracion(path: str) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())


async def _con_reintentos(synth, *args):
    for intento in range(len(ESPERAS) + 1):
        try:
            return await synth(*args)
        except Exception as e:  # red, servicio caído…
            if intento == len(ESPERAS):
                raise RuntimeError(f"La voz falló {intento + 1} veces seguidas: {e}") from e
            await asyncio.sleep(ESPERAS[intento])


async def sintetizar(frases_: list[str], voz: str, base: int, pausa: float, tmp: str, synth=None):
    """Genera voz.wav en tmp y devuelve (ruta, [(inicio, fin, palabra)]) con tiempos absolutos."""
    synth = synth or _edge
    os.makedirs(tmp, exist_ok=True)
    wavs, palabras, t = [], [], 0.0
    for i, f in enumerate(frases_):
        rate, pitch = prosodia(f, i, base)
        mp3, wav = os.path.join(tmp, f"f{i}.mp3"), os.path.join(tmp, f"f{i}.wav")
        ws = await _con_reintentos(synth, f, voz, rate, pitch, mp3)
        a, b = max(0.0, ws[0][0] - 0.02), ws[-1][1] + 0.07
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af",
                        f"atrim={a}:{b},asetpts=N/SR/TB,apad=pad_dur={pausa}", "-ar", "44100", "-ac", "1", wav], check=True)
        palabras += [(x0 - a + t, x1 - a + t, tx) for x0, x1, tx in ws]
        t += duracion(wav)
        wavs.append(wav)
    lista = os.path.join(tmp, "frases.txt")
    with open(lista, "w") as fh:
        fh.write("".join(f"file '{os.path.abspath(w)}'\n" for w in wavs))
    salida = os.path.join(tmp, "voz.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, salida], check=True)
    return salida, palabras
