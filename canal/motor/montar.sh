#!/usr/bin/env bash
# Une fotogramas, subtítulos, voz y música. Uso: montar.sh <dir_tmp> <video.mp4>
set -euo pipefail
TMP="$1"; OUT="$2"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/partes.txt" -c copy "$TMP/mudo.mp4"
ffmpeg -y -loglevel error -i "$TMP/mudo.mp4" -i "$TMP/voz.wav" -i "$TMP/musica.wav" -filter_complex \
 "[0:v]ass=$TMP/subs.ass[v];[2:a]volume=0.16[m];[1:a]apad,asplit[va][vs];[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[va][md]amix=inputs=2:duration=shortest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
 -map "[v]" -map "[a]" -shortest -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -ar 44100 -movflags +faststart "$OUT"
