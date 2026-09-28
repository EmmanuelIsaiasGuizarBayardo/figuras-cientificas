"""Instala las reglas de visualización como regla de Antigravity en un proyecto.

Uso, desde la raíz del proyecto que depende de figuras-cientificas:
    uv run python -m figuras_cientificas regla
"""

from __future__ import annotations

import argparse
import sys
from importlib import resources
from pathlib import Path

from figuras_cientificas import __version__

ENCABEZADO = """---
trigger: always_on
description: "Reglas de visualización científica (figuras-cientificas {version})."
---

<!-- Generado por figuras-cientificas {version}. No se edita aquí: se regenera con
     'uv run python -m figuras_cientificas regla' tras actualizar la biblioteca. -->

"""


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada del comando."""
    analizador = argparse.ArgumentParser(prog="python -m figuras_cientificas")
    ordenes = analizador.add_subparsers(dest="orden", required=True)
    regla = ordenes.add_parser("regla", help="escribe las reglas como regla de Antigravity")
    regla.add_argument("--destino", type=Path, default=Path(".agents/rules/visualizacion.md"))
    argumentos = analizador.parse_args(argv)

    reglas = (resources.files("figuras_cientificas") / "visualizacion.md").read_text(
        encoding="utf-8"
    )
    texto = ENCABEZADO.format(version=__version__) + reglas
    argumentos.destino.parent.mkdir(parents=True, exist_ok=True)
    argumentos.destino.write_text(texto, encoding="utf-8", newline="\n")
    print(f"Regla escrita en {argumentos.destino} ({len(texto.encode())} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
