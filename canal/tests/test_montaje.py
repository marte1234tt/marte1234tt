import json, os, re, subprocess
import pytest
from PIL import Image
from motor import preparar as P
from motor.synth_falso import synth_falso

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _probe(ruta):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate:format=duration,size", "-of", "json", ruta])
    return json.loads(out)


def test_js_del_tema_se_guarda_como_ruta_absoluta(tmp_path):
    g = {"tema": "x", "personaje": "pulpo", "js": "extra.js",
         "escenas": [{"titulo": "A", "texto": "Hola mundo.", "efectos": []}]}
    p = tmp_path / "guion.json"; p.write_text(json.dumps(g))
    cfg = P.preparar(str(p), str(tmp_path / "o"), synth=synth_falso)
    assert cfg["js"] == str(tmp_path / "extra.js")


@pytest.mark.lento
def test_hacer_pulpo_completo():
    r = subprocess.run(["bash", "motor/hacer.sh", "ejemplos/pulpo/guion.json"], cwd=RAIZ,
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    salida = re.search(r"^LISTO (.+)$", r.stdout, re.M).group(1).strip()
    info = _probe(os.path.join(salida, "video.mp4"))
    v = info["streams"][0]
    assert (v["width"], v["height"], v["r_frame_rate"]) == (1080, 1920, "30/1")
    assert 61 <= float(info["format"]["duration"]) <= 80
    assert int(info["format"]["size"]) < 50_000_000
    assert Image.open(os.path.join(salida, "portada.png")).size == (1080, 1920)
    pub = open(os.path.join(salida, "publicacion.txt"), encoding="utf-8").read()
    assert "INSTAGRAM" in pub and "#curiosidades" in pub and "TIKTOK" in pub and "YOUTUBE" in pub
    assert os.path.exists(os.path.join(salida, "fuentes.md"))
    assert len(os.listdir(os.path.join(salida, "fotogramas"))) == 10


def test_portada_banda_larga_no_se_sale(tmp_path):
    g = {"tema": "x", "personaje": "pulpo", "escenas": [{"titulo": "A", "texto": "Hola mundo bonito.", "efectos": []}],
         "portada": {"escena": 0, "t": 0.5, "linea1": "UNO", "linea2": "DOS",
                     "banda": "QUE DE LAS PIRÁMIDES DE EGIPTO 🔺", "color_banda": "#E63946"}}
    p = tmp_path / "guion.json"; p.write_text(json.dumps(g, ensure_ascii=False))
    P.preparar(str(p), str(tmp_path / "o"), synth=synth_falso)
    png = tmp_path / "portada.png"
    subprocess.run(["node", "motor/portada.js", str(tmp_path / "o" / "tmp" / "config.json"), str(png)], cwd=RAIZ, check=True)
    im = Image.open(png).convert("RGB")
    # ni el texto (blanco) ni la banda (rojo) pueden llegar a los 30 px de cada borde
    fuera = [(x, y) for x in list(range(0, 30)) + list(range(1050, 1080)) for y in range(1400, 1760, 3)
             if (lambda c: (min(c) > 225) or (c[0] > 180 and c[1] < 110 and c[2] < 110))(im.getpixel((x, y)))]
    assert fuera == [], f"la banda o su texto se salen: {fuera[:5]}"
