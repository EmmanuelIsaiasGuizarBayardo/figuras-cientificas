"""Las reglas escritas cumplen lo que dicen: referencias citadas y PDF reproducible."""

import io
import re
from importlib import resources

import matplotlib.pyplot as plt
import pytest


def _reglas() -> str:
    return (resources.files("figuras_cientificas") / "visualizacion.md").read_text(encoding="utf-8")


def test_toda_referencia_esta_citada_en_el_texto() -> None:
    cuerpo, referencias = _reglas().split("## Referencias")
    huerfanas = [
        bloque.strip().splitlines()[0]
        for bloque in re.split(r"\n\s*\n", referencias.strip())
        if re.split(r"[,.]", bloque.strip())[0] not in cuerpo
    ]
    assert not huerfanas, f"Referencias que el texto no cita: {huerfanas}"


def test_okabe_ito_tiene_su_cita() -> None:
    texto = _reglas()
    assert "Okabe & Ito, 2008" in texto and "Okabe, M., & Ito, K. (2008)" in texto


def test_pdf_es_identico_con_source_date_epoch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    salidas = []
    for _ in range(2):
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2], [1, 3, 2])
        buffer = io.BytesIO()
        fig.savefig(buffer, format="pdf")
        plt.close(fig)
        salidas.append(buffer.getvalue())
    assert salidas[0] == salidas[1]
    assert b"D:19700101000000" in salidas[0], "la fecha de creacion no se fijo"
