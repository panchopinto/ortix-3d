"""Generador reproducible del código QR de ORTIX 3D.

Uso (desde la raíz del repositorio):

    python -m pip install -r tools/requirements.txt
    python tools/generar_qr.py https://USUARIO.github.io/ortix-3d/

Genera, sin servicios externos:
  - qr/qr-ortix-3d.png  (alta resolución, 24 px por módulo)
  - qr/qr-ortix-3d.svg  (vectorial)
y escribe la URL en js/config.js para activar el bloque «Compartir QR».

El código usa módulos negros, fondo blanco y un margen libre de 4 módulos.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import segno

RAIZ = Path(__file__).resolve().parent.parent
BORDE_MODULOS = 4
PX_POR_MODULO = 24
NIVEL_CORRECCION = "q"


def validar_url(url: str) -> str:
    """Exige una URL HTTPS directa, sin espacios y terminada en «/» (portada)."""
    if not re.fullmatch(r"https://[^\s/]+(/\S*)?", url):
        raise ValueError("La URL debe ser https:// y no contener espacios.")
    if "usuario" in url.lower() and "github.io" in url.lower():
        raise ValueError("Reemplaza USUARIO por el nombre de usuario de GitHub confirmado.")
    if not url.endswith("/"):
        raise ValueError("La URL debe terminar en «/» para abrir la portada (index.html).")
    return url


def matriz_a_svg(matriz: tuple[bytearray, ...], borde: int) -> str:
    """Construye un SVG con un rectángulo por tramo horizontal de módulos oscuros."""
    lado = len(matriz) + 2 * borde
    trazos: list[str] = []
    for y, fila in enumerate(matriz):
        x = 0
        while x < len(fila):
            if fila[x]:
                inicio = x
                while x < len(fila) and fila[x]:
                    x += 1
                trazos.append(f"M{inicio + borde} {y + borde}h{x - inicio}v1h-{x - inicio}z")
            else:
                x += 1
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {lado} {lado}" '
        f'width="{lado * 10}" height="{lado * 10}" shape-rendering="crispEdges" '
        'role="img" aria-label="Código QR de ORTIX 3D">'
        f'<rect width="{lado}" height="{lado}" fill="#ffffff"/>'
        f'<path fill="#000000" d="{"".join(trazos)}"/></svg>\n'
    )


def escribir_config(url: str) -> None:
    ruta = RAIZ / "js" / "config.js"
    ruta.write_text(
        "// Configuración pública del sitio. La completa tools/generar_qr.py cuando se confirma la URL.\n"
        f'window.ORTIX_CONFIG = {{ publicUrl: "{url}" }};\n',
        encoding="utf-8",
        newline="\n",
    )


def generar(url: str, destino: Path, actualizar_config: bool = True) -> tuple[Path, Path]:
    destino.mkdir(parents=True, exist_ok=True)
    codigo = segno.make(url, error=NIVEL_CORRECCION, micro=False, boost_error=False)
    ruta_png = destino / "qr-ortix-3d.png"
    ruta_svg = destino / "qr-ortix-3d.svg"
    codigo.save(str(ruta_png), kind="png", scale=PX_POR_MODULO, border=BORDE_MODULOS,
                dark="#000000", light="#ffffff")
    ruta_svg.write_text(matriz_a_svg(codigo.matrix, BORDE_MODULOS), encoding="utf-8", newline="\n")
    if actualizar_config:
        escribir_config(url)
    return ruta_png, ruta_svg


def main() -> int:
    analizador = argparse.ArgumentParser(description="Genera el QR de ORTIX 3D para una URL pública.")
    analizador.add_argument("url", help="URL pública HTTPS de la portada, p. ej. https://usuario.github.io/ortix-3d/")
    analizador.add_argument("--salida", type=Path, default=RAIZ / "qr", help="carpeta de salida (por defecto qr/)")
    analizador.add_argument("--sin-config", action="store_true", help="no modificar js/config.js")
    args = analizador.parse_args()
    try:
        url = validar_url(args.url)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    png, svg = generar(url, args.salida, actualizar_config=not args.sin_config)
    print(f"PNG: {png}\nSVG: {svg}\nURL codificada: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
