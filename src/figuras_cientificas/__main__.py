"""Instala las reglas de visualización, y los perfiles por venue, como reglas de Antigravity.

Uso, desde la raíz del proyecto que depende de figuras-cientificas:
    uv run python -m figuras_cientificas regla
    uv run python -m figuras_cientificas regla --perfil cnib_lncs
    uv run python -m figuras_cientificas guia topomaps_mne
"""

from __future__ import annotations

import argparse
import sys
from importlib import resources
from pathlib import Path

from figuras_cientificas import __version__

ENCABEZADO = """---
trigger: always_on
description: "{descripcion} (figuras-cientificas {version})."
---

<!-- Generado por figuras-cientificas {version}. No se edita aquí: se regenera con
     'uv run python -m figuras_cientificas regla{opcion}' tras actualizar la biblioteca. -->

"""


def _documentos(carpeta: str) -> list[str]:
    """Nombres de los documentos Markdown de una carpeta del paquete."""
    ruta = resources.files("figuras_cientificas") / carpeta
    return sorted(p.name.removesuffix(".md") for p in ruta.iterdir() if p.name.endswith(".md"))


def perfiles() -> list[str]:
    """Nombres de los perfiles por venue que trae el paquete."""
    return _documentos("perfiles")


def guias() -> list[str]:
    """Nombres de las guías técnicas que trae el paquete."""
    return _documentos("guias")


def _escribir(destino: Path, cuerpo: str, descripcion: str, opcion: str) -> None:
    """Escribe una regla con su encabezado de Antigravity."""
    texto = ENCABEZADO.format(version=__version__, descripcion=descripcion, opcion=opcion) + cuerpo
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8", newline="\n")
    print(f"Regla escrita en {destino} ({len(texto.encode())} bytes).")


def _mostrar_guia(nombre: str | None) -> int:
    """Imprime una guía, o la lista de guías disponibles."""
    if nombre is None:
        print(f"Guías disponibles: {', '.join(guias())}.")
        return 0
    if nombre not in guias():
        print(f"Guía desconocida: {nombre!r}. Disponibles: {', '.join(guias())}.", file=sys.stderr)
        return 1
    # En Windows, una salida redirigida usa la codificación local, que no tiene
    # caracteres como "≥"; un agente que lee la guía por una tubería fallaría.
    sys.stdout.reconfigure(encoding="utf-8")
    texto = (resources.files("figuras_cientificas") / "guias" / f"{nombre}.md").read_text(
        encoding="utf-8"
    )
    print(texto, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada del comando."""
    analizador = argparse.ArgumentParser(prog="python -m figuras_cientificas")
    ordenes = analizador.add_subparsers(dest="orden", required=True)
    regla = ordenes.add_parser("regla", help="escribe las reglas como regla de Antigravity")
    regla.add_argument("--destino", type=Path, default=Path(".agents/rules/visualizacion.md"))
    regla.add_argument("--perfil", help=f"agrega un perfil por venue: {', '.join(perfiles())}")
    guia = ordenes.add_parser("guia", help="muestra una guía técnica; sin nombre, las lista")
    guia.add_argument("nombre", nargs="?", help=f"una de: {', '.join(guias())}")
    argumentos = analizador.parse_args(argv)

    if argumentos.orden == "guia":
        return _mostrar_guia(argumentos.nombre)
    if argumentos.perfil is not None and argumentos.perfil not in perfiles():
        disponibles = ", ".join(perfiles())
        print(
            f"Perfil desconocido: {argumentos.perfil!r}. Disponibles: {disponibles}.",
            file=sys.stderr,
        )
        return 1
    paquete = resources.files("figuras_cientificas")
    reglas = (paquete / "visualizacion.md").read_text(encoding="utf-8")
    _escribir(argumentos.destino, reglas, "Reglas de visualización científica", "")
    if argumentos.perfil:
        perfil = (paquete / "perfiles" / f"{argumentos.perfil}.md").read_text(encoding="utf-8")
        _escribir(
            argumentos.destino.with_name(f"visualizacion-{argumentos.perfil}.md"),
            perfil,
            f"Perfil de visualización {argumentos.perfil}",
            f" --perfil {argumentos.perfil}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
