"""Música de fondo: una pista libre de derechos de canal/musica/ o, si no hay, una sintetizada."""
import glob, os, random, subprocess, wave
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pistas():
    d = os.path.join(RAIZ, "musica")
    return sorted(glob.glob(os.path.join(d, "*.mp3")) + glob.glob(os.path.join(d, "*.wav")))


def musica(dur: float, ruta: str) -> None:
    pistas = _pistas()
    if pistas:
        p = random.choice(pistas)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", p, "-t", f"{dur:.2f}",
                        "-af", f"afade=in:d=1.0,afade=out:st={max(0, dur - 2):.2f}:d=2", "-ar", "44100", "-ac", "1", ruta],
                       check=True)
        return
    _sintetizada(dur, ruta)


def _sintetizada(dur, ruta, sr=44100):
    t = np.arange(int(dur * sr)) / sr
    acordes = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    y = np.zeros_like(t)
    seg = 4.0
    for k in range(int(dur / seg) + 1):
        notas, t0 = acordes[k % 4], k * seg
        m = (t >= t0) & (t < t0 + seg + 1.5); tt = t[m] - t0
        env = np.minimum(tt / 0.8, 1) * np.exp(-np.maximum(tt - seg, 0) * 3)
        for n in notas:
            f = 440 * 2 ** ((n - 69) / 12)
            y[m] += env * (np.sin(2 * np.pi * f * tt) * 0.5 + np.sin(2 * np.pi * f * 2 * tt) * 0.12)
        for j in range(8):
            tn = t0 + j * 0.5; mm = (t >= tn) & (t < tn + 0.9); ta = t[mm] - tn
            f = 440 * 2 ** ((notas[j % 3] + 12 - 69) / 12)
            y[mm] += np.exp(-ta * 5) * np.sin(2 * np.pi * f * ta) * 0.35
    y = y / (np.max(np.abs(y)) or 1) * 0.5
    fade = np.minimum(np.minimum(t / 1.5, 1), np.minimum((dur - t) / 2.0, 1))
    y = (y * np.clip(fade, 0, 1) * 32767).astype(np.int16)
    with wave.open(ruta, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(y.tobytes())
