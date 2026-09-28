"""Comprobaciones de accesibilidad: luminosidad, contraste y daltonismo.

La simulación de deficiencias de visión de color usa el modelo de Machado et al.
(2009) con severidad completa; las distancias perceptuales se miden en CAM02-UCS.
"""

from __future__ import annotations

import io
import itertools
from collections.abc import Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from colorspacious import cspace_convert
from matplotlib.colors import Colormap
from matplotlib.figure import Figure
from numpy.typing import ArrayLike

DEFICIENCIAS: dict[str, str] = {
    "deuteranopia": "deuteranomaly",
    "protanopia": "protanomaly",
    "tritanopia": "tritanomaly",
}


def simular(rgb: ArrayLike, deficiencia: str) -> np.ndarray:
    """Cómo ve un arreglo RGB, con valores de 0 a 1, una persona con esa deficiencia."""
    if deficiencia not in DEFICIENCIAS:
        raise ValueError(f"deficiencia debe ser una de {sorted(DEFICIENCIAS)}")
    espacio = {"name": "sRGB1+CVD", "cvd_type": DEFICIENCIAS[deficiencia], "severity": 100}
    return np.clip(cspace_convert(np.asarray(rgb, dtype=float), espacio, "sRGB1"), 0, 1)


def luminosidad(cmap: Colormap) -> np.ndarray:
    """L* de CIELAB de cada entrada del mapa, sin remuestrear.

    Muestrear más puntos que entradas repite colores y produce diferencias
    exactamente cero, que parecerían mesetas del mapa.
    """
    return cspace_convert(cmap(np.arange(cmap.N))[:, :3], "sRGB1", "CIELab")[:, 0]


def _luminancia_relativa(color: object) -> float:
    lineal = np.asarray(mpl.colors.to_rgb(color))
    lineal = np.where(lineal <= 0.04045, lineal / 12.92, ((lineal + 0.055) / 1.055) ** 2.4)
    return float(lineal @ np.array([0.2126, 0.7152, 0.0722]))


def contraste(color: object, fondo: object = "white") -> float:
    """Razón de contraste de WCAG 2.1; 3:1 es el mínimo para elementos gráficos."""
    alta, baja = sorted((_luminancia_relativa(color), _luminancia_relativa(fondo)), reverse=True)
    return (alta + 0.05) / (baja + 0.05)


def separacion_minima(colores: Sequence[object]) -> dict[str, float]:
    """Distancia entre los dos colores más parecidos, por tipo de visión.

    Returns
    -------
    dict
        ΔE en CAM02-UCS para "normal" y cada deficiencia; más alto es mejor.
    """
    rgb = np.array([mpl.colors.to_rgb(c) for c in colores])
    if len(rgb) < 2:
        raise ValueError("se necesitan al menos dos colores")
    vistas = {"normal": rgb} | {d: simular(rgb, d) for d in DEFICIENCIAS}
    resultado = {}
    for nombre, vista in vistas.items():
        ucs = cspace_convert(vista, "sRGB1", "CAM02-UCS")
        resultado[nombre] = float(
            min(np.linalg.norm(a - b) for a, b in itertools.combinations(ucs, 2))
        )
    return resultado


def revisar_figura(fig: Figure, *, dpi: int = 100) -> Figure:
    """La figura como la ven personas con cada deficiencia, y su luminosidad.

    Parameters
    ----------
    fig : Figure
        Figura terminada; se renderiza sin modificarla.
    dpi : int
        Resolución del render; 100 basta para juzgar la legibilidad.

    Returns
    -------
    Figure
        Cinco vistas: típica, deuteranopia, protanopia, tritanopia y L*.
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, facecolor="white")
    buffer.seek(0)
    imagen = plt.imread(buffer)[..., :3]
    vistas = {"Visión típica": imagen} | {d.capitalize(): simular(imagen, d) for d in DEFICIENCIAS}
    alto = 2 * 4.5 * imagen.shape[0] / imagen.shape[1] + 0.8
    revision, ejes = plt.subplots(2, 3, figsize=(13.5, alto), layout="constrained")
    for eje, (titulo, vista) in zip(ejes.flat[:4], vistas.items(), strict=True):
        eje.imshow(vista)
        eje.set_title(titulo)
    ejes.flat[4].imshow(
        cspace_convert(imagen, "sRGB1", "CIELab")[..., 0], cmap="gray", vmin=0, vmax=100
    )
    ejes.flat[4].set_title("Luminosidad L*")
    for eje in ejes.flat:
        eje.axis("off")
    return revision
