"""Verificación de accesibilidad y el comando que instala las reglas."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from figuras_cientificas import contraste, revisar_figura, simular
from figuras_cientificas.__main__ import main


def test_contraste_de_referencia() -> None:
    assert contraste("black") == pytest.approx(21.0)
    assert contraste("white") == pytest.approx(1.0)


def test_simular_conserva_la_forma_y_el_rango() -> None:
    imagen = np.random.default_rng(0).random((8, 5, 3))
    simulada = simular(imagen, "tritanopia")
    assert simulada.shape == imagen.shape
    assert simulada.min() >= 0 and simulada.max() <= 1
    with pytest.raises(ValueError):
        simular(imagen, "acromatopsia")


def test_revisar_figura_da_cinco_vistas() -> None:
    fig, ax = plt.subplots()
    ax.imshow(np.random.default_rng(1).random((10, 10)))
    revision = revisar_figura(fig)
    assert sum(1 for eje in revision.axes if eje.images) == 5
    plt.close("all")


def test_la_regla_se_instala_para_antigravity(tmp_path: Path) -> None:
    destino = tmp_path / ".agents" / "rules" / "visualizacion.md"
    assert main(["regla", "--destino", str(destino)]) == 0
    texto = destino.read_text(encoding="utf-8")
    assert texto.startswith("---\ntrigger: always_on\n")
    assert len(texto.encode()) < 24_000, "Antigravity trunca las reglas de mas de 24,000 bytes"
    assert "\u2014" not in texto
