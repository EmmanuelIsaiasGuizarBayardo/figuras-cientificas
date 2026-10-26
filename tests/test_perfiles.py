"""Los perfiles por venue viajan con el paquete y se instalan como reglas."""

import re
from importlib import resources
from pathlib import Path

import pytest

from figuras_cientificas.__main__ import guias, main, perfiles


def test_el_paquete_trae_el_perfil_cnib_lncs() -> None:
    assert "cnib_lncs" in perfiles()


def test_el_perfil_se_instala_junto_a_las_reglas(tmp_path: Path) -> None:
    destino = tmp_path / ".agents" / "rules" / "visualizacion.md"
    assert main(["regla", "--destino", str(destino), "--perfil", "cnib_lncs"]) == 0
    perfil = destino.with_name("visualizacion-cnib_lncs.md").read_text(encoding="utf-8")
    assert destino.is_file()
    assert perfil.startswith("---\ntrigger: always_on\n")
    assert len(perfil.encode()) < 24_000, "Antigravity trunca las reglas de mas de 24,000 bytes"
    assert "\u2014" not in perfil


def test_perfil_desconocido(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["regla", "--destino", str(tmp_path / "r.md"), "--perfil", "nature_2099"]) == 1
    assert "cnib_lncs" in capsys.readouterr().err


@pytest.mark.parametrize("perfil", perfiles())
def test_lo_que_cita_un_perfil_viene_con_el_paquete(perfil: str) -> None:
    """En un proyecto, el perfil solo puede remitir a archivos que el paquete trae."""
    paquete = resources.files("figuras_cientificas")
    texto = (paquete / "perfiles" / f"{perfil}.md").read_text(encoding="utf-8")
    citados = re.findall(r"`((?:guias|perfiles)/[\w./-]+\.md)`", texto)
    faltan = [ruta for ruta in citados if not (paquete / ruta).is_file()]
    assert not faltan, f"{perfil} remite a archivos que el paquete no trae: {faltan}"


def test_la_guia_de_topografias_se_consulta(capsys: pytest.CaptureFixture[str]) -> None:
    assert "topomaps_mne" in guias()
    assert main(["guia", "topomaps_mne"]) == 0
    texto = capsys.readouterr().out
    assert "plot_topomap" in texto and "fc.secuencial()" in texto


def test_guia_desconocida_y_lista(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["guia", "eeg_3d"]) == 1
    assert "topomaps_mne" in capsys.readouterr().err
    assert main(["guia"]) == 0
    assert "topomaps_mne" in capsys.readouterr().out
