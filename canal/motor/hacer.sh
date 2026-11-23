#!/usr/bin/env bash
# Fabrica un vídeo completo a partir de un guion.
# Uso: bash motor/hacer.sh <guion.json>   (desde canal/)
# Códigos: 0 = listo · 3 = duración corta (añadir un dato) · 4 = el vídeo no cumple los requisitos
set -uo pipefail
[ -f "${1:-}" ] || { echo "No encuentro el guion: ${1:-}"; exit 2; }
GUION="$(realpath "$1")"
cd "$(dirname "$0")/.."
TEMA=$(python3 -c "import json,sys,unicodedata,re; t=json.load(open(sys.argv[1]))['tema']; t=unicodedata.normalize('NFD',t.lower()); t=''.join(c for c in t if unicodedata.category(c)!='Mn'); print(re.sub(r'[^a-z0-9]+','-',t).strip('-'))" "$GUION")
OUT="salida/$(date +%Y-%m-%d)-$TEMA"
mkdir -p "$OUT"
echo "== preparar"; python3 -m motor.preparar "$GUION" "$OUT"; rc=$?
[ $rc -ne 0 ] && exit $rc
echo "== render"; node motor/render.js "$OUT/tmp/config.json" "$OUT/tmp" 4 || exit 1
echo "== montar"; bash motor/montar.sh "$OUT/tmp" "$OUT/video.mp4" || exit 1
echo "== portada"; node motor/portada.js "$OUT/tmp/config.json" "$OUT/portada.png" || exit 1
python3 -m motor.textos "$GUION" "$OUT" || exit 1
rm -rf "$OUT/fotogramas"; mkdir -p "$OUT/fotogramas"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/video.mp4")
for i in $(seq 0 9); do
  T=$(python3 -c "print(round($DUR*($i+0.5)/10,2))")
  ffmpeg -loglevel error -y -ss "$T" -i "$OUT/video.mp4" -frames:v 1 -vf scale=540:-1 "$OUT/fotogramas/$(printf %02d $i)_${T}s.png"
done
python3 - "$OUT/video.mp4" "$OUT/tmp/config.json" <<'PY' || exit 4
import json, subprocess, sys
cfg = json.load(open(sys.argv[2]))
info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
      "stream=width,height,r_frame_rate:format=duration,size", "-of", "json", sys.argv[1]]))
v, f = info["streams"][0], info["format"]
errores = []
if (v["width"], v["height"]) != (1080, 1920): errores.append(f"resolución {v['width']}x{v['height']}")
if v["r_frame_rate"] != "30/1": errores.append(f"fps {v['r_frame_rate']}")
d = float(f["duration"])
if not cfg["duracion"]["min"] <= d <= cfg["duracion"]["max"]: errores.append(f"duración {d:.1f}s")
if int(f["size"]) >= 50_000_000: errores.append(f"tamaño {int(f['size'])/1e6:.1f} MB")
if errores: print("NO_CUMPLE " + ", ".join(errores)); sys.exit(4)
print(f"OK {d:.1f}s {int(f['size'])/1e6:.1f} MB")
PY
rm -rf "$OUT/tmp/parte"*.mp4 "$OUT/tmp/mudo.mp4" "$OUT/tmp"/f*.mp3 "$OUT/tmp"/f*.wav
echo "LISTO $(pwd)/$OUT"
