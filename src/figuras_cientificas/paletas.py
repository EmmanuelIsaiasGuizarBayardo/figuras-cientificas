"""Paletas accesibles y la regla para elegir el mapa de color de unos datos.

Mapas continuos de Scientific colour maps (Crameri, 2018) y secuencias
categóricas de Petroff (2024), con Okabe-Ito como alternativa citable. Cada
elección está medida, y las pruebas lo verifican: luminosidad CIELAB en los
mapas y separación mínima bajo daltonismo simulado en las categorías.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import matplotlib as mpl
import numpy as np
from cmcrameri import cm as cmc
from matplotlib import style
from matplotlib.colors import Colormap, Normalize
from numpy.typing import ArrayLike

Fondo = Literal["claro", "oscuro"]
Extension = Literal["neither", "min", "max", "both"]
Paleta = Literal["petroff", "okabe_ito"]

LINEAS: tuple[str | tuple[int, tuple[int, ...]], ...] = (
    "-",
    "--",
    "-.",
    ":",
    (0, (3, 1, 1, 1)),
    (0, (5, 1)),
)
MARCADORES: tuple[str, ...] = ("o", "s", "^", "D", "v", "P", "X", "*")
TRAMAS: tuple[str, ...] = ("", "//", "\\\\", "xx", "..", "oo", "++", "||")

# Okabe-Ito para fondo claro: primero los cuatro colores con contraste de al
# menos 3:1 contra blanco; al final el amarillo (1.3:1, solo para rellenos con
# borde oscuro) y el negro (reservado para referencias). Son índices del
# colormap "okabe_ito" de matplotlib: 0 negro, 1 naranja, 2 azul cielo,
# 3 verde azulado, 4 amarillo, 5 azul, 6 bermellón, 7 púrpura rojizo.
_ORDEN_OKABE_ITO = (5, 6, 3, 7, 1, 2, 4, 0)
_TOPE = {"petroff": 10, "okabe_ito": 8}


def secuencial() -> Colormap:
    """Mapa para datos ordenados sin centro: potencia, amplitud, SNR, exactitud."""
    return cmc.batlow


def divergente(fondo: Fondo = "claro") -> Colormap:
    """Mapa para datos con centro natural o con ambos signos.

    Parameters
    ----------
    fondo : {"claro", "oscuro"}
        Sobre fondo claro el centro debe ser claro, para que "sin efecto" se
        confunda con el fondo y los efectos resalten (``roma``). Sobre fondo
        oscuro, lo contrario (``managua``). En ambos, positivo es cálido.

    Returns
    -------
    Colormap
    """
    if fondo == "claro":
        return cmc.roma_r
    if fondo == "oscuro":
        return mpl.colormaps["managua"].reversed()
    raise ValueError(f"fondo debe ser 'claro' u 'oscuro', no {fondo!r}")


def ciclico() -> Colormap:
    """Mapa para datos angulares: fase, dirección."""
    return cmc.romaO


def categorica(n: int, *, paleta: Paleta = "petroff") -> list[str]:
    """Colores para n categorías, en el orden en que deben usarse.

    Parameters
    ----------
    n : int
        Número de categorías: de 1 a 10 con Petroff, de 1 a 8 con Okabe-Ito.
    paleta : {"petroff", "okabe_ito"}
        Petroff por omisión: ``petroff6`` hasta seis categorías y los primeros n
        colores de ``petroff10`` de siete a diez. ``petroff8`` no se usa porque
        sus prefijos separan peor bajo daltonismo que los de ``petroff10``.
        Okabe-Ito, cuando se requiera esa paleta por nombre.

    Returns
    -------
    list of str
        Colores en hexadecimal.

    Raises
    ------
    ValueError
        Con más categorías de las que el color distingue. En ese caso conviene
        facetar, agrupar, o resaltar unas pocas y dejar el resto en gris.
    """
    if paleta not in _TOPE:
        raise ValueError(f"paleta debe ser 'petroff' u 'okabe_ito', no {paleta!r}")
    if not 1 <= n <= _TOPE[paleta]:
        raise ValueError(
            f"{n} categorías no se distinguen solo por color (máximo {_TOPE[paleta]} con "
            f"{paleta}); facetea, agrupa o resalta unas pocas y deja el resto en gris"
        )
    if paleta == "okabe_ito":
        base = mpl.colormaps["okabe_ito"].colors
        return [mpl.colors.to_hex(base[i]) for i in _ORDEN_OKABE_ITO[:n]]
    ciclo = style.library["petroff6" if n <= 6 else "petroff10"]["axes.prop_cycle"]
    return list(ciclo.by_key()["color"][:n])


def estilo_serie(i: int, colores: Sequence[str], *, marcador: bool = True) -> dict[str, object]:
    """Color, tipo de línea y marcador de la serie i: nunca solo el color.

    Parameters
    ----------
    i : int
        Índice de la serie.
    colores : sequence of str
        Normalmente ``categorica(n)``.
    marcador : bool
        Falso en series densas, como un ERP o una señal: un marcador por muestra
        es tinta sin información, y el tipo de línea basta como redundancia.

    Returns
    -------
    dict
        Argumentos para ``ax.plot(..., **estilo)``.
    """
    estilo: dict[str, object] = {
        "color": colores[i % len(colores)],
        "linestyle": LINEAS[i % len(LINEAS)],
    }
    if marcador:
        estilo["marker"] = MARCADORES[i % len(MARCADORES)]
    return estilo


def trama(i: int) -> str:
    """Trama de relleno de la categoría i, para barras y áreas."""
    return TRAMAS[i % len(TRAMAS)]


def extension(datos: ArrayLike, norm: Normalize) -> Extension:
    """Qué extremos de la barra de color deben marcar datos recortados por la escala.

    Una escala fijada por percentil recorta valores; sin la marca, el lector no
    puede saber que existen. Se usa como ``fig.colorbar(..., extend=extension(...))``.
    """
    valores = np.asarray(datos, dtype=float)
    valores = valores[np.isfinite(valores)]
    abajo, arriba = bool(valores.min() < norm.vmin), bool(valores.max() > norm.vmax)
    return {(False, False): "neither", (True, False): "min", (False, True): "max"}.get(
        (abajo, arriba), "both"
    )


def mapa_para(
    datos: ArrayLike,
    *,
    centro: float | None = None,
    percentil: float = 98.0,
    fondo: Fondo = "claro",
) -> tuple[Colormap, Normalize]:
    """Elige mapa y escala: la regla de divergente contra secuencial, como código.

    Datos con un centro natural, o con ambos signos, van en un mapa divergente
    con escala simétrica. Datos de un solo signo van en uno secuencial sobre su
    rango real, aunque la métrica pudiera tener otro signo en teoría.

    Parameters
    ----------
    datos : array_like
        Valores a representar; se ignoran los no finitos.
    centro : float, optional
        Referencia natural: 0, la línea base o el nivel de azar. Si se omite y los
        datos tienen ambos signos, el centro es 0.
    percentil : float
        Percentil que fija el extremo de la escala, para que un valor atípico no
        la comprima.
    fondo : {"claro", "oscuro"}
        Fondo de la figura; decide el mapa divergente.

    Returns
    -------
    cmap : Colormap
    norm : Normalize
        Simétrica alrededor del centro en el caso divergente.
    """
    valores = np.asarray(datos, dtype=float)
    valores = valores[np.isfinite(valores)]
    if valores.size == 0:
        raise ValueError("no hay datos finitos")
    if centro is None and valores.min() < 0 < valores.max():
        centro = 0.0
    if centro is not None:
        radio = float(np.percentile(np.abs(valores - centro), percentil))
        if radio == 0:
            raise ValueError("los datos no se alejan del centro")
        return divergente(fondo), Normalize(vmin=centro - radio, vmax=centro + radio)
    bajo, alto = float(valores.min()), float(np.percentile(valores, percentil))
    if alto <= bajo:
        raise ValueError("los datos no varían")
    return secuencial(), Normalize(vmin=bajo, vmax=alto)
