"""Tamaño, estilo y letras de panel según la guía de figuras de Nature."""

from __future__ import annotations

from importlib import resources
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.text import Annotation

MM_POR_PULGADA = 25.4
ANCHOS_MM: dict[str, float] = {"una_columna": 89.0, "doble_columna": 183.0}
ALTURA_MAXIMA_MM = 170.0  # deja lugar a la leyenda bajo la figura


def tamano_figura(
    ancho: str | float = "una_columna",
    *,
    alto_mm: float | None = None,
    proporcion: float = 0.75,
) -> tuple[float, float]:
    """``figsize`` en pulgadas para un ancho de figura de Nature.

    Parameters
    ----------
    ancho : {"una_columna", "doble_columna"} or float
        89 mm, 183 mm, o un ancho en milímetros.
    alto_mm : float, optional
        Alto en milímetros; si se omite, ``ancho * proporcion``.
    proporcion : float
        Relación alto/ancho cuando no se da ``alto_mm``.

    Returns
    -------
    tuple of float
        (ancho, alto) en pulgadas.

    Raises
    ------
    ValueError
        Con un nombre de ancho desconocido o un alto mayor que 170 mm.
    """
    if isinstance(ancho, str):
        if ancho not in ANCHOS_MM:
            raise ValueError(f"ancho debe ser uno de {sorted(ANCHOS_MM)} o un número en mm")
        ancho_mm = ANCHOS_MM[ancho]
    else:
        ancho_mm = float(ancho)
    alto = ancho_mm * proporcion if alto_mm is None else float(alto_mm)
    if alto > ALTURA_MAXIMA_MM:
        raise ValueError(f"{alto:.0f} mm excede la altura máxima de {ALTURA_MAXIMA_MM:.0f} mm")
    return ancho_mm / MM_POR_PULGADA, alto / MM_POR_PULGADA


def usar_estilo(nombre: Literal["publicacion", "presentacion"] = "publicacion") -> None:
    """Aplica el ciclo ``petroff6`` y uno de los estilos del paquete.

    El estilo de publicación sigue la guía de Nature: texto de 5 a 7 pt, una sola
    tipografía sans-serif y texto editable en el PDF. No fija ``savefig.bbox``,
    porque "tight" cambiaría el ancho con que se diseñó la figura.
    """
    import cmcrameri  # noqa: F401  registra los mapas cmc.* que usan los estilos

    ruta = resources.files("figuras_cientificas") / "estilos" / f"{nombre}.mplstyle"
    if not ruta.is_file():
        raise ValueError(f"estilo desconocido: {nombre!r}; usa 'publicacion' o 'presentacion'")
    with resources.as_file(ruta) as archivo:
        plt.style.use(["petroff6", archivo])


def letra_panel(ax: Axes, letra: str) -> Annotation:
    """Letra de panel arriba a la izquierda: minúscula, negrita, vertical.

    Con el estilo de publicación mide 8 pt, como pide Nature; en general, un punto
    más que el texto base.
    """
    tamano = plt.rcParams["font.size"] + 1
    return ax.annotate(
        letra.lower(),
        xy=(0, 1),
        xycoords="axes fraction",
        xytext=(-2.5 * tamano, 0.5 * tamano),
        textcoords="offset points",
        fontsize=tamano,
        fontweight="bold",
        fontstyle="normal",
        ha="left",
        va="bottom",
    )
