"""Guion → voz, tiempos por palabra, subtítulos, música y config de animación.

Uso: python3 -m motor.preparar <guion.json> <salida>
Sale con código 3 e imprime «DURACION_CORTA <s>» si el vídeo no llega al mínimo.
"""
import asyncio, difflib, json, os, re, sys, unicodedata

from motor.voz import cargar_config, frases, sintetizar, duracion
from motor.subtitulos import subtitulos
from motor.musica import musica

COLA = 1.4          # segundos extra al final
INICIO_DEFECTO = 0.3  # si una pista no aparece
CAMPOS_TIEMPO = ("desde", "hasta", "desde_der", "asustado", "aparece")  # campos de efectos que se dan como pista


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", s)


def tokens_guion(g):
    out = []
    for i, e in enumerate(g["escenas"]):
        for w in e["texto"].split():
            limpio = w.strip("¿¡.,:;!?…\"'()")
            if limpio:
                out.append((limpio, i))
    return out


def alinear(toks, recon):
    """Asigna a cada palabra del guion los tiempos de la voz (difflib + interpolación)."""
    a = [norm(t) for t, _ in toks]; b = [norm(w[2]) for w in recon]
    tiempos = [None] * len(a)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                tiempos[i1 + k] = (recon[j1 + k][0], recon[j1 + k][1])
        elif op == "replace" and j2 > j1:
            t0, t1 = recon[j1][0], recon[j2 - 1][1]
            n = i2 - i1
            for k in range(n):
                tiempos[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
    for k in range(len(tiempos)):
        if tiempos[k] is None:
            prev = next((tiempos[j][1] for j in range(k - 1, -1, -1) if tiempos[j]), 0.0)
            nxt = next((tiempos[j][0] for j in range(k + 1, len(tiempos)) if tiempos[j]), prev + 0.3)
            tiempos[k] = (prev, max(prev + 0.05, nxt))
    return tiempos


def _resolver(valor, idx, toks, tiempos, start, campo="desde"):
    """'palabra', 'palabra+0.5' o número → segundos desde el inicio de la escena."""
    if isinstance(valor, (int, float)):
        return float(valor)
    m = re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)?$", str(valor).strip())
    clave, desfase = m.group(1), float(m.group(2) or 0)
    k = next((k for k in idx if norm(toks[k][0]).startswith(norm(clave))), None)
    if k is None:
        print(f"AVISO pista no encontrada: {clave}")
        return INICIO_DEFECTO + desfase if campo == "desde" else None
    return tiempos[k][0] - start + desfase


def preparar(guion_path: str, salida_dir: str, synth=None) -> dict:
    cfg_canal = cargar_config()
    with open(guion_path, encoding="utf-8") as f:
        g = json.load(f)
    tmp = os.path.join(salida_dir, "tmp"); os.makedirs(tmp, exist_ok=True)
    v = cfg_canal["voz"]
    todas = [fr for e in g["escenas"] for fr in frases(e["texto"])]
    voz_wav, recon = asyncio.run(sintetizar(todas, v["nombre"], v["velocidad"], v["pausa"], tmp, synth=synth))
    total_voz = duracion(voz_wav)
    toks = tokens_guion(g); tiempos = alinear(toks, recon)
    escenas = []
    for i, e in enumerate(g["escenas"]):
        idx = [k for k, (_, s) in enumerate(toks) if s == i]
        start = 0.0 if i == 0 else max(0.0, tiempos[idx[0]][0] - 0.08)
        efectos = []
        def resolver_todo(x):
            if isinstance(x, list):
                return [resolver_todo(v) for v in x]
            if isinstance(x, dict):
                out = {k: (_resolver(v, idx, toks, tiempos, start, k) if k in CAMPOS_TIEMPO else resolver_todo(v)) for k, v in x.items()}
                return {k: v for k, v in out.items() if v is not None}
            return x
        for ef in e.get("efectos", []):
            ef = resolver_todo(ef)
            ef.setdefault("desde", 0.0)
            efectos.append(ef)
        escenas.append({"titulo": e["titulo"], "start": start, "efectos": efectos})
    total = total_voz + COLA
    for i, e in enumerate(escenas):
        e["dur"] = (escenas[i + 1]["start"] if i + 1 < len(escenas) else total) - e["start"]
    subtitulos([(t[0], t[1], w) for (w, _), t in zip(toks, tiempos)], os.path.join(tmp, "subs.ass"))
    musica(total, os.path.join(tmp, "musica.wav"))
    cfg = {"total": total, "cuenta": g.get("cuenta", cfg_canal["cuenta"]), "etiqueta": g.get("etiqueta", cfg_canal["etiqueta"]),
           "duracion": g.get("duracion", cfg_canal["duracion"]),
           "personaje": g.get("personaje"), "encuesta": g.get("encuesta", []),
           "js": os.path.join(os.path.dirname(os.path.abspath(guion_path)), g["js"]) if g.get("js") else None,
           "escenas": escenas}
    if g.get("portada"):
        por = dict(g["portada"]); i = int(por.get("escena", 0))
        idx = [k for k, (_, s) in enumerate(toks) if s == i]
        por["T"] = escenas[i]["start"] + _resolver(por.get("t", 1.0), idx, toks, tiempos, escenas[i]["start"])
        cfg["portada"] = por
    with open(os.path.join(tmp, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    return cfg


def main(argv):
    synth = None
    if os.environ.get("CANAL_SYNTH_FALSO"):
        from motor.synth_falso import synth_falso as synth
    cfg = preparar(argv[0], argv[1], synth=synth)
    minimo = cfg["duracion"]["min"]
    print(f"total {cfg['total']:.1f}s, {len(cfg['escenas'])} escenas")
    if cfg["total"] < minimo:
        print(f"DURACION_CORTA {cfg['total']:.1f}")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
