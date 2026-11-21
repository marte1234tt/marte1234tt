"""Textos de publicación y fuentes a partir del guion."""
import json, os, sys


def escribir(guion_path: str, salida: str) -> None:
    with open(guion_path, encoding="utf-8") as f:
        g = json.load(f)
    pub = g.get("publicacion", {})
    partes = [f"=== INSTAGRAM ===\n{pub.get('instagram', '')}",
              f"=== TIKTOK ===\n{pub.get('tiktok', '')}",
              f"=== YOUTUBE ===\nTítulo: {pub.get('youtube_titulo', '')}\n\nDescripción:\n{pub.get('instagram', '')}"]
    with open(os.path.join(salida, "publicacion.txt"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(partes) + "\n")
    with open(os.path.join(salida, "fuentes.md"), "w", encoding="utf-8") as f:
        f.write(f"# Fuentes — {g.get('tema', '')}\n\n" + "".join(f"- {x}\n" for x in g.get("fuentes", [])))


if __name__ == "__main__":
    escribir(sys.argv[1], sys.argv[2])
