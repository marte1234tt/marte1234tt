"""Sintetizador falso para tests: 0,3 s por palabra, sin red."""
import subprocess


async def synth_falso(texto, voz, rate, pitch, mp3):
    palabras = texto.split()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=220:r=24000",
                    "-t", f"{len(palabras) * 0.3 + 0.2:.2f}", mp3], check=True)
    return [(k * 0.3 + 0.05, k * 0.3 + 0.3, w.strip("¿¡.,:;!?")) for k, w in enumerate(palabras)]
