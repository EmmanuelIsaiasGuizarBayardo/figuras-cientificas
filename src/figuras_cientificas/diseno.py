"""Tamaño, estilo, letras de panel y exportación de figuras.

Por omisión sigue la guía de figuras de Nature. Los venues con requisitos propios, como
Springer LNCS, tienen su ancho, su estilo de letra de panel y su formato de archivo.
"""

from __future__ import annotations

import io
from importlib import resources
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Annotation
from PIL import Image

MM_POR_PULGADA = 25.4
ANCHOS_MM: dict[str, float] = {
    "una_columna": 89.0,  # Nature
    "doble_columna": 183.0,  # Nature
    "lncs": 122.0,  # ancho de texto de Springer LNCS: \textwidth de llncs.cls, 12.2 cm
}
ALTURA_MAXIMA_MM = 170.0  # deja lugar a la leyenda bajo la figura


def tamano_figura(
    ancho: str | float = "una_columna",
    *,
    alto_mm: float | None = None,
    proporcion: float = 0.75,
) -> tuple[float, float]:
    """``figsize`` en pulgadas para un ancho de figura con nombre o en milímetros.

    Parameters
    ----------
    ancho : {"una_columna", "doble_columna", "lncs"} or float
        89 o 183 mm (Nature), 122 mm (ancho de texto de Springer LNCS), o un ancho
        en milímetros.
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


EstiloLetra = Literal["nature", "parentesis"]


def letra_panel(ax: Axes, letra: str, estilo: EstiloLetra = "nature") -> Annotation:
    """Letra de panel arriba a la izquierda, en negrita y vertical.

    Parameters
    ----------
    ax : Axes
        Panel que recibe la letra.
    letra : str
        Letra del panel, en cualquier caja.
    estilo : {"nature", "parentesis"}
        ``"nature"`` escribe la minúscula (``a``); ``"parentesis"``, la mayúscula con
        paréntesis (``A)``), como piden el CNIB y otros venues. La posición, el tamaño
        y el peso son los mismos en ambos.

    Returns
    -------
    Annotation

    Raises
    ------
    ValueError
        Con un estilo desconocido.

    Notes
    -----
    Con el estilo de publicación mide 8 pt, como pide Nature; en general, un punto más
    que el texto base.
    """
    textos = {"nature": letra.lower(), "parentesis": f"{letra.upper()})"}
    if estilo not in textos:
        raise ValueError(f"estilo debe ser uno de {sorted(textos)}, no {estilo!r}")
    tamano = plt.rcParams["font.size"] + 1
    return ax.annotate(
        textos[estilo],
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


def exportar_tiff(fig: Figure, ruta: str | Path, dpi: int = 300) -> Path:
    """Guarda la figura como TIFF RGB sin canal alfa, con compresión LZW.

    Algunas editoriales rechazan un TIFF con canal alfa, así que la figura se compone
    sobre blanco. Conserva el tamaño diseñado: no usa ``bbox_inches="tight"``.

    Parameters
    ----------
    fig : Figure
        Figura terminada.
    ruta : str or Path
        Destino, con extensión ``.tif`` o ``.tiff``.
    dpi : int
        Resolución; 300 es la que piden la mayoría de los venues.

    Returns
    -------
    Path
        La ruta escrita.

    Raises
    ------
    ValueError
        Si la extensión no es ``.tif`` ni ``.tiff``.
    """
    ruta = Path(ruta)
    if ruta.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError(f"la extensión debe ser .tif o .tiff, no {ruta.suffix!r}")
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, facecolor="white")
    buffer.seek(0)
    with Image.open(buffer) as imagen:
        rgba = imagen.convert("RGBA")
    rgb = Image.new("RGB", rgba.size, "white")
    rgb.paste(rgba, mask=rgba.getchannel("A"))
    rgb.save(ruta, format="TIFF", dpi=(dpi, dpi), compression="tiff_lzw")
    return ruta
