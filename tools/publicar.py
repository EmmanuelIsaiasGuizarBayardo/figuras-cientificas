"""Publica una versión en un solo paso: número, cita, requisitos, pruebas y etiqueta.

Cada paso depende del anterior y el script se detiene en el primero que falle,
siempre antes de etiquetar. Existe porque publicar a mano, con varios comandos,
dejó dos veces una etiqueta cuyo paquete declaraba otra versión.

Uso, desde la raíz del repositorio, con los cambios de la versión ya hechos:
    uv run python tools/publicar.py 0.1.3 "Qué cambia en esta versión"
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def correr(*orden: str) -> None:
    """Ejecuta un paso; si falla, detiene la publicación."""
    print(f"\n-> {' '.join(orden)}", flush=True)
    subprocess.run(orden, cwd=RAIZ, check=True)


def etiqueta_existe(etiqueta: str) -> bool:
    """True si la etiqueta ya existe en el repositorio local."""
    salida = subprocess.run(
        ["git", "tag", "--list", etiqueta], cwd=RAIZ, capture_output=True, text=True, check=True
    )
    return bool(salida.stdout.strip())


def commit(mensaje: str) -> None:
    """Commit con los hooks; si uno corrige archivos, se agregan y se reintenta una vez."""
    correr("git", "add", "-A")
    if subprocess.run(["git", "commit", "-m", mensaje], cwd=RAIZ, check=False).returncode == 0:
        return
    print("\nUn hook corrigió archivos; se agregan y se reintenta el commit.", flush=True)
    correr("git", "add", "-A")
    correr("git", "commit", "-m", mensaje)


def main(argumentos: list[str]) -> int:
    """Corre la publicación completa y devuelve 0 solo si todo se subió."""
    if len(argumentos) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", argumentos[0]):
        print(__doc__)
        return 2
    version, mensaje = argumentos
    etiqueta = f"v{version}"
    if etiqueta_existe(etiqueta):
        print(
            f"{etiqueta} ya existe. Una etiqueta publicada no se mueve: usa la versión siguiente."
        )
        return 1
    try:
        correr("uv", "version", version)
        correr("uv", "run", "python", "tools/sincronizar_cff.py")
        correr("uv", "run", "python", "tools/export_requirements.py")
        correr("uv", "run", "pytest", "-q")
        commit(mensaje)
        correr("git", "tag", "-a", etiqueta, "-m", mensaje)
        correr("git", "push", "--follow-tags")
    except subprocess.CalledProcessError as error:
        paso = " ".join(error.cmd)
        if etiqueta_existe(etiqueta):
            print(f"\nSe detuvo en: {paso}. {etiqueta} existe solo en tu máquina; al corregir,")
            print("sube con: git push --follow-tags")
        else:
            print(f"\nSe detuvo en: {paso}. No se creó {etiqueta}: corrige y vuelve a correr.")
        return 1
    print(f"\nPublicada {etiqueta}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
