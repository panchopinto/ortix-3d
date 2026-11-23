"""Verifica que el PNG y el SVG del QR contienen exactamente la URL esperada.

    python tools/verificar_qr.py https://USUARIO.github.io/ortix-3d/

El SVG se rasteriza con un intérprete mínimo de su propio formato (rectángulos
«M x y h w v 1 h -w z») y luego se decodifica con OpenCV, igual que el PNG.
También comprueba que el margen libre mida al menos 4 módulos.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
PX_SVG = 12


def rasterizar_svg(texto: str) -> np.ndarray:
    vista = re.search(r'viewBox="0 0 (\d+) (\d+)"', texto)
    if not vista:
        raise ValueError("SVG sin viewBox")
    lado = int(vista.group(1))
    imagen = np.full((lado * PX_SVG, lado * PX_SVG), 255, dtype=np.uint8)
    for x, y, ancho in re.findall(r"M(\d+) (\d+)h(\d+)v1h-\d+z", texto):
        x, y, ancho = int(x), int(y), int(ancho)
        imagen[y * PX_SVG:(y + 1) * PX_SVG, x * PX_SVG:(x + ancho) * PX_SVG] = 0
    return imagen


def margen_en_modulos(gris: np.ndarray) -> float:
    """Mide el margen blanco izquierdo usando el ancho del patrón de búsqueda (7 módulos)."""
    oscuros = np.argwhere(gris < 128)
    y0, x0 = oscuros.min(axis=0)
    fila = gris[y0 + 1, x0:] < 128
    tramo = int(np.argmin(fila)) if not fila.all() else len(fila)
    modulo = tramo / 7
    return x0 / modulo


def decodificar(gris: np.ndarray) -> str:
    ampliada = cv2.copyMakeBorder(gris, 0, 0, 0, 0, cv2.BORDER_CONSTANT, value=255)
    texto, _, _ = cv2.QRCodeDetector().detectAndDecode(ampliada)
    return texto


def comprobar(nombre: str, gris: np.ndarray, esperado: str) -> bool:
    leido = decodificar(gris)
    margen = margen_en_modulos(gris)
    ok = leido == esperado and margen >= 4
    estado = "OK " if ok else "FALLO"
    print(f"[{estado}] {nombre}: decodificado={leido!r} margen={margen:.2f} módulos")
    return ok


def main() -> int:
    analizador = argparse.ArgumentParser()
    analizador.add_argument("url")
    analizador.add_argument("--carpeta", type=Path, default=RAIZ / "qr")
    args = analizador.parse_args()

    png = cv2.imread(str(args.carpeta / "qr-ortix-3d.png"), cv2.IMREAD_GRAYSCALE)
    if png is None:
        print("No se pudo leer el PNG", file=sys.stderr)
        return 2
    svg = rasterizar_svg((args.carpeta / "qr-ortix-3d.svg").read_text(encoding="utf-8"))
    resultados = [comprobar("PNG", png, args.url), comprobar("SVG rasterizado", svg, args.url)]
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
