"""Propiedades medidas de las paletas: si una actualización las rompe, esto falla."""

import numpy as np
import pytest

from figuras_cientificas import (
    categorica,
    ciclico,
    divergente,
    estilo_serie,
    extension,
    mapa_para,
    secuencial,
)
from figuras_cientificas.verificacion import contraste, luminosidad, separacion_minima


def test_secuencial_tiene_luminosidad_monotona() -> None:
    assert np.all(np.diff(luminosidad(secuencial())) > 0)


@pytest.mark.parametrize("fondo, centro_claro", [("claro", True), ("oscuro", False)])
def test_divergente_centro_segun_fondo_y_extremos_simetricos(
    fondo: str, centro_claro: bool
) -> None:
    lum = luminosidad(divergente(fondo))
    centro, extremos = lum[len(lum) // 2], (lum[0], lum[-1])
    if centro_claro:
        assert centro > max(extremos) + 40
    else:
        assert centro < min(extremos) - 40
    assert abs(lum[0] - lum[-1]) < 3, "un lado del cero se veria mas intenso que el otro"


@pytest.mark.parametrize("fondo", ["claro", "oscuro"])
def test_divergente_positivo_es_calido(fondo: str) -> None:
    r_alto, _, b_alto, _ = divergente(fondo)(1.0)
    r_bajo, _, b_bajo, _ = divergente(fondo)(0.0)
    assert r_alto > b_alto and b_bajo > r_bajo


def test_ciclico_cierra() -> None:
    mapa = ciclico()
    assert np.allclose(mapa(0.0), mapa(1.0), atol=0.02)


@pytest.mark.parametrize("n", range(2, 11))
def test_petroff_separa_bajo_daltonismo(n: int) -> None:
    assert min(separacion_minima(categorica(n)).values()) >= 14


@pytest.mark.parametrize("n", range(2, 9))
def test_okabe_ito_separa_bajo_daltonismo(n: int) -> None:
    assert min(separacion_minima(categorica(n, paleta="okabe_ito")).values()) >= 10


def test_okabe_ito_empieza_con_colores_visibles_sobre_blanco() -> None:
    assert all(contraste(c) >= 3 for c in categorica(4, paleta="okabe_ito"))


@pytest.mark.parametrize("n, paleta", [(0, "petroff"), (11, "petroff"), (9, "okabe_ito")])
def test_categorica_rechaza_lo_que_el_color_no_distingue(n: int, paleta: str) -> None:
    with pytest.raises(ValueError):
        categorica(n, paleta=paleta)


def test_mapa_para_datos_con_signo_es_divergente_y_simetrico() -> None:
    datos = np.random.default_rng(0).normal(0.5, 1.0, 1000)
    cmap, norm = mapa_para(datos)
    assert cmap.name == divergente().name
    assert norm.vmin == pytest.approx(-norm.vmax)


def test_mapa_para_un_solo_signo_es_secuencial_en_su_rango() -> None:
    datos = np.random.default_rng(1).uniform(2.0, 9.0, 1000)
    cmap, norm = mapa_para(datos)
    assert cmap.name == secuencial().name
    assert norm.vmin == pytest.approx(datos.min())


def test_mapa_para_respeta_un_centro_explicito() -> None:
    exactitud = np.random.default_rng(2).uniform(0.55, 0.9, 200)
    _, norm = mapa_para(exactitud, centro=0.5)
    assert (norm.vmin + norm.vmax) / 2 == pytest.approx(0.5)


def test_estilo_serie_nunca_es_solo_color() -> None:
    colores = categorica(3)
    assert {"color", "linestyle", "marker"} <= set(estilo_serie(0, colores))
    assert "marker" not in estilo_serie(0, colores, marcador=False)
    assert estilo_serie(0, colores)["linestyle"] != estilo_serie(1, colores)["linestyle"]


def test_extension_marca_lo_recortado() -> None:
    datos = np.append(np.random.default_rng(4).normal(0, 1, 1000), [-50.0, 50.0])
    _, norm = mapa_para(datos)
    assert extension(datos, norm) == "both"
    assert extension(np.clip(datos, norm.vmin, norm.vmax), norm) == "neither"


def test_mapa_para_resiste_atipicos() -> None:
    datos = np.append(np.random.default_rng(3).normal(0, 1, 1000), 1e6)
    _, norm = mapa_para(datos)
    assert norm.vmax < 10
