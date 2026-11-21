"""Voz (edge o gemini) + alineado de palabras + subtítulos + música + config de animación.
Uso: python3 prep3.py guion3.json salida edge|gemini
"""
import asyncio, base64, difflib, json, os, re, ssl, subprocess, sys, unicodedata, urllib.request, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from motor import subtitulos, musica, duracion

def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", s)

def tokens_guion(g):
    """Palabras del guion con su escena: [(texto_limpio, escena)]."""
    out = []
    for i, e in enumerate(g["escenas"]):
        for w in e["texto"].split():
            limpio = w.strip("¿¡.,:;!?…\"'")
            if limpio: out.append((limpio, i))
    return out

def alinear(guion_tok, recon):
    """Asigna tiempos (de la voz reconocida) a cada palabra del guion."""
    a = [norm(t) for t, _ in guion_tok]; b = [norm(w[2]) for w in recon]
    tiempos = [None] * len(a)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): tiempos[i1 + k] = (recon[j1 + k][0], recon[j1 + k][1])
        elif op == "replace" and j2 > j1:
            t0, t1 = recon[j1][0], recon[j2 - 1][1]
            for k in range(i2 - i1):
                tiempos[i1 + k] = (t0 + (t1 - t0) * k / (i2 - i1), t0 + (t1 - t0) * (k + 1) / (i2 - i1))
    # huecos (insertadas): interpolar entre vecinos
    for k in range(len(tiempos)):
        if tiempos[k] is None:
            prev = next((tiempos[j][1] for j in range(k - 1, -1, -1) if tiempos[j]), 0.0)
            nxt = next((tiempos[j][0] for j in range(k + 1, len(tiempos)) if tiempos[j]), prev + 0.3)
            tiempos[k] = (prev, max(prev + 0.05, nxt))
    return tiempos

# ------------------------------------------------------------ voz edge (por frases, con prosodia)
def frases(t):
    return [f.strip() for f in re.findall(r"[^.!?]*[.!?]", t) if f.strip()]

def prosodia(f, i, base):
    r, p = base, 0
    if "?" in f: p += 6
    if "!" in f: p += 4; r += 6
    if len(f.split()) <= 3: r += 4
    p += [0, -2, 2, -1][i % 4]
    return f"+{r}%", f"{p:+d}Hz"

async def voz_edge(g, tmp):
    import edge_tts, edge_tts.communicate as ec
    ec._SSL_CTX = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
    cfg = g["voz_edge"]; wavs, recon, t_acum, n = [], [], 0.0, 0
    for e in g["escenas"]:
        for f in frases(e["texto"]):
            rate, pitch = prosodia(f, n, cfg["velocidad"])
            mp3 = f"{tmp}/f{n}.mp3"; ws = []
            c = edge_tts.Communicate(f, cfg["voz"], rate=rate, pitch=pitch, boundary="WordBoundary", proxy=os.environ["HTTPS_PROXY"])
            with open(mp3, "wb") as fh:
                async for ch in c.stream():
                    if ch["type"] == "audio": fh.write(ch["data"])
                    elif ch["type"] == "WordBoundary": ws.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
            a, b = max(0, ws[0][0] - 0.02), ws[-1][1] + 0.07
            wav = f"{tmp}/f{n}.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", f"atrim={a}:{b},asetpts=N/SR/TB,apad=pad_dur={cfg.get('pausa', 0.05)}",
                            "-ar", "44100", "-ac", "1", wav], check=True)
            recon += [(x0 - a + t_acum, x1 - a + t_acum, tx) for x0, x1, tx in ws]
            t_acum += duracion(wav); wavs.append(wav); n += 1
    open(f"{tmp}/l.txt", "w").write("".join(f"file '{os.path.abspath(w)}'\n" for w in wavs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/l.txt", f"{tmp}/voz.wav"], check=True)
    return recon

# ------------------------------------------------------------ voz gemini (una sola petición) + whisper
def voz_gemini(g, tmp):
    cfg = g["voz_gemini"]
    texto = " ".join(e["texto"] for e in g["escenas"])
    modelo = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
    body = {"contents": [{"parts": [{"text": f"{cfg['estilo']}\n\n{texto}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": cfg["voz"]}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    resp = json.load(urllib.request.urlopen(req, timeout=300))
    pcm = base64.b64decode(resp["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    raw = f"{tmp}/gemini.wav"
    with wave.open(raw, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    # quitar silencios largos (>0,25 s) que meta el modelo
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.25:stop_threshold=-45dB",
                    "-ar", "44100", "-ac", "1", f"{tmp}/voz.wav"], check=True)
    return whisper_palabras(f"{tmp}/voz.wav")

def whisper_palabras(path):
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    m = WhisperModel("small", device="cpu", compute_type="int8", download_root=os.path.join(os.path.dirname(__file__), "whisper_models"))
    segs, _ = m.transcribe(np.frombuffer(raw, np.int16).astype(np.float32) / 32768, language="es", word_timestamps=True)
    return [(float(w.start), float(w.end), w.word.strip()) for s in segs for w in s.words]

# ------------------------------------------------------------
def main(guion_path, outdir, motor_voz):
    g = json.load(open(guion_path)); tmp = os.path.join(outdir, "tmp"); os.makedirs(tmp, exist_ok=True)
    recon = asyncio.run(voz_edge(g, tmp)) if motor_voz == "edge" else voz_gemini(g, tmp)
    total = duracion(f"{tmp}/voz.wav")
    toks = tokens_guion(g); tiempos = alinear(toks, recon)
    palabras = [(t[0], t[1], w) for (w, _), t in zip(toks, tiempos)]
    # límites de escena = primera palabra de cada escena
    escenas = []
    for i, e in enumerate(g["escenas"]):
        idx = [k for k, (_, s) in enumerate(toks) if s == i]
        start = 0.0 if i == 0 else max(0.0, tiempos[idx[0]][0] - 0.08)
        cues = {}
        for clave in e["pistas"]:
            k = next((k for k in idx if norm(toks[k][0]).startswith(norm(clave))), None)
            if k is None: print("  aviso: pista no encontrada", clave)
            else: cues[clave] = tiempos[k][0] - start
        escenas.append({"tipo": e["anim"], "titulo": e["titulo"], "start": start, "cues": cues})
    for i, e in enumerate(escenas):
        e["dur"] = (escenas[i + 1]["start"] if i + 1 < len(escenas) else total + 1.4) - e["start"]
    total += 1.4
    subtitulos(palabras, f"{tmp}/subs.ass")
    musica(total, f"{tmp}/musica.wav")
    json.dump({"total": total, "escenas": escenas, "extra": g.get("extra", {})}, open(f"{tmp}/config.json", "w"), ensure_ascii=False, indent=1)
    print(f"voz {motor_voz}: total {total:.1f}s, {len(palabras)} palabras, {len(palabras) / total:.2f} pal/s")
    for e in escenas: print(" ", e["tipo"], round(e["start"], 2), round(e["dur"], 2), {k: round(v, 2) for k, v in e["cues"].items()})

if __name__ == "__main__":
    main(*sys.argv[1:4])
