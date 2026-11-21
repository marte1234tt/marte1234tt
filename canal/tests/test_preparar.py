import json, os, subprocess, sys
import pytest
from motor import preparar as P
from motor.subtitulos import escapar_ass, subtitulos
from motor.synth_falso import synth_falso

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _guion(tmp_path, efectos2):
    g = {"tema": "Prueba", "personaje": "pulpo",
         "escenas": [{"titulo": "UNO", "texto": "Hola amigos del canal.", "efectos": []},
                     {"titulo": "DOS", "texto": "Tiene tres. Dos bombean sangre.", "efectos": efectos2}],
         "encuesta": ["A", "B"]}
    p = tmp_path / "guion.json"
    p.write_text(json.dumps(g, ensure_ascii=False))
    return str(p)


def _prep(tmp_path, efectos2):
    return P.preparar(_guion(tmp_path, efectos2), str(tmp_path / "out"), synth=synth_falso)


def test_resuelve_pistas_a_segundos_locales(tmp_path):
    cfg = _prep(tmp_path, [{"tipo": "organo", "desde": "Dos"}])
    # "Dos" es la primera palabra de la 2.ª frase de la escena: su inicio local debe ser > 0.5 s
    assert 0.5 < cfg["escenas"][1]["efectos"][0]["desde"] < 1.6


def test_pista_inexistente_usa_inicio(tmp_path, capsys):
    cfg = _prep(tmp_path, [{"tipo": "organo", "desde": "zzz"}])
    assert cfg["escenas"][1]["efectos"][0]["desde"] == pytest.approx(0.3)
    assert "AVISO pista no encontrada: zzz" in capsys.readouterr().out


def test_pista_con_desfase(tmp_path):
    a = _prep(tmp_path, [{"tipo": "organo", "desde": "Dos"}])["escenas"][1]["efectos"][0]["desde"]
    b = _prep(tmp_path, [{"tipo": "organo", "desde": "Dos+0.5"}])["escenas"][1]["efectos"][0]["desde"]
    assert b == pytest.approx(a + 0.5, abs=0.001)


def test_hasta_numerico(tmp_path):
    cfg = _prep(tmp_path, [{"tipo": "organo", "desde": 1, "hasta": "Dos"}])
    e = cfg["escenas"][1]["efectos"][0]
    assert e["desde"] == 1.0 and e["hasta"] > 0.5


def test_escenas_contiguas(tmp_path):
    cfg = _prep(tmp_path, [])
    es = cfg["escenas"]
    assert es[0]["start"] == 0
    assert es[1]["start"] == pytest.approx(es[0]["start"] + es[0]["dur"])
    assert sum(e["dur"] for e in es) == pytest.approx(cfg["total"])
    for f in ("voz.wav", "subs.ass", "musica.wav", "config.json"):
        assert os.path.exists(tmp_path / "out" / "tmp" / f)


def test_config_lleva_marca(tmp_path):
    cfg = _prep(tmp_path, [])
    assert cfg["cuenta"] == "@nolosabias672" and cfg["etiqueta"] == "¿NO LO SABÍAS?"
    assert cfg["personaje"] == "pulpo" and cfg["encuesta"] == ["A", "B"]


def test_duracion_corta_sale_con_3(tmp_path):
    env = dict(os.environ, CANAL_SYNTH_FALSO="1")
    r = subprocess.run([sys.executable, "-m", "motor.preparar", _guion(tmp_path, []), str(tmp_path / "o")],
                       cwd=RAIZ, env=env, capture_output=True, text=True)
    assert r.returncode == 3 and "DURACION_CORTA" in r.stdout


def test_escapar_ass(tmp_path):
    assert escapar_ass("a{b}\\c") == "a\\{b\\}\\\\c"
    ruta = tmp_path / "s.ass"
    subtitulos([(0.0, 0.5, "{hola}")], str(ruta))
    assert "\\{HOLA\\}" in ruta.read_text()


def test_portada_se_resuelve_a_tiempo_absoluto(tmp_path):
    g = json.loads(open(_guion(tmp_path, [])).read())
    g["portada"] = {"escena": 1, "t": "Dos", "linea1": "A"}
    p = tmp_path / "g2.json"; p.write_text(json.dumps(g, ensure_ascii=False))
    cfg = P.preparar(str(p), str(tmp_path / "o2"), synth=synth_falso)
    esc = cfg["escenas"][1]
    assert esc["start"] < cfg["portada"]["T"] < esc["start"] + esc["dur"]
    assert cfg["portada"]["linea1"] == "A"


def test_resuelve_campos_de_tiempo_secundarios(tmp_path):
    cfg = _prep(tmp_path, [{"tipo": "comparacion", "desde": 0, "desde_der": "Dos"},
                           {"tipo": "objeto", "desde": 0, "asustado": "Dos+0.2"}])
    ef = cfg["escenas"][1]["efectos"]
    assert isinstance(ef[0]["desde_der"], float) and isinstance(ef[1]["asustado"], float)
    assert ef[1]["asustado"] == pytest.approx(ef[0]["desde_der"] + 0.2)


def test_resuelve_tiempos_anidados(tmp_path):
    cfg = _prep(tmp_path, [{"tipo": "linea_tiempo", "desde": 0,
                            "puntos": [{"anio": -2560, "desde": "Dos"}],
                            "tramos": [{"de": -2560, "a": -30, "desde": "Dos+0.5"}]}])
    e = cfg["escenas"][1]["efectos"][0]
    assert isinstance(e["puntos"][0]["desde"], float)
    assert e["tramos"][0]["desde"] == pytest.approx(e["puntos"][0]["desde"] + 0.5)
