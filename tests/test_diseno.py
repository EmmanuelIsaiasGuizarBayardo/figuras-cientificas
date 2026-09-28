"""Tamaños y estilo según la guía de Nature, verificados sobre el archivo guardado."""

import re
from collections.abc import Iterator
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

from figuras_cientificas import letra_panel, tamano_figura, usar_estilo
from figuras_cientificas.diseno import MM_POR_PULGADA


@pytest.fixture(autouse=True)
def _estilo_aislado() -> Iterator[None]:
    with mpl.rc_context():
        yield
    plt.close("all")


@pytest.mark.parametrize("ancho, mm", [("una_columna", 89.0), ("doble_columna", 183.0)])
def test_anchos_de_nature(ancho: str, mm: float) -> None:
    assert tamano_figura(ancho)[0] * MM_POR_PULGADA == pytest.approx(mm)


def test_altura_maxima_y_nombre_desconocido() -> None:
    with pytest.raises(ValueError):
        tamano_figura("una_columna", alto_mm=171)
    with pytest.raises(ValueError):
        tamano_figura("tres_columnas")


def test_estilo_de_publicacion() -> None:
    usar_estilo("publicacion")
    assert 5 <= plt.rcParams["xtick.labelsize"] <= plt.rcParams["font.size"] <= 7
    assert plt.rcParams["pdf.fonttype"] == 42, "el texto del PDF debe quedar editable"
    assert plt.rcParams["savefig.bbox"] is None, "'tight' cambiaria el ancho de la figura"
    assert plt.rcParams["axes.prop_cycle"].by_key()["color"][0] == "#5790fc"


def test_pdf_guardado_conserva_el_ancho_de_columna(tmp_path: Path) -> None:
    usar_estilo("publicacion")
    fig, ax = plt.subplots(figsize=tamano_figura("una_columna"))
    ax.plot([0, 1], [0, 1])
    ax.set_ylabel("una etiqueta larga que tight recortaria o expandiria")
    fig.savefig(tmp_path / "f.pdf")
    caja = re.search(
        rb"/MediaBox \[\s*0 0 ([\d.]+) ([\d.]+)\s*\]", (tmp_path / "f.pdf").read_bytes()
    )
    assert caja is not None
    assert float(caja.group(1)) / 72 * MM_POR_PULGADA == pytest.approx(89.0, abs=0.1)


def test_letra_de_panel_segun_nature() -> None:
    usar_estilo("publicacion")
    _, ax = plt.subplots()
    letra = letra_panel(ax, "A")
    assert letra.get_text() == "a"
    assert letra.get_fontsize() == 8 and letra.get_fontweight() == "bold"


def test_estilo_desconocido() -> None:
    with pytest.raises(ValueError):
        usar_estilo("poster")  # type: ignore[arg-type]
