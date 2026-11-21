import asyncio, os, subprocess
import pytest
from motor import voz


def test_frases_corta_por_puntuacion():
    assert voz.frases("¿Un alien? Nooo. ¡Es el pulpo!") == ["¿Un alien?", "Nooo.", "¡Es el pulpo!"]


def test_prosodia_pregunta():
    assert voz.prosodia("¿Un alien?", 0, 10) == ("+14%", "+6Hz")


def test_prosodia_exclamacion():
    assert voz.prosodia("¡Y saborea con los brazos!", 1, 10) == ("+16%", "+2Hz")


def _synth_falso(fallos=0):
    estado = {"n": 0}

    async def synth(texto, nombre, rate, pitch, mp3):
        estado["n"] += 1
        if estado["n"] <= fallos:
            raise ConnectionError("red caída")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", "1", mp3], check=True)
        return [(0.10, 0.50, texto.split()[0])]
    return synth, estado


def test_sintetizar_tiempos_absolutos(tmp_path):
    synth, _ = _synth_falso()
    wav, palabras = asyncio.run(voz.sintetizar(["Hola mundo.", "Adiós."], "x", 10, 0.3, str(tmp_path), synth=synth))
    assert os.path.exists(wav)
    # primera frase recortada: de 0.08 a 0.57 (+0.3 de pausa) => 0.79 s
    assert palabras[0][0] == pytest.approx(0.02, abs=0.01)
    assert palabras[1][0] - palabras[0][0] == pytest.approx(0.79, abs=0.03)


def test_sintetizar_reintenta(tmp_path, monkeypatch):
    monkeypatch.setattr(voz, "ESPERAS", [0, 0, 0])
    synth, estado = _synth_falso(fallos=2)
    wav, palabras = asyncio.run(voz.sintetizar(["Hola."], "x", 10, 0.3, str(tmp_path), synth=synth))
    assert estado["n"] == 3 and len(palabras) == 1
