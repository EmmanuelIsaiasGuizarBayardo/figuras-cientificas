"""Figura de ejemplo que aplica todas las reglas, y su revisión de accesibilidad.

Datos sintéticos de neuroingeniería en una figura a doble columna de Nature:
(a) ERSP relativo a la línea base, (b) conectividad ordenada por región, (c) ERPs
con IC 95% y (d) exactitud de decodificación por sujeto con el umbral de azar.

Uso, desde la raíz del repositorio:
    uv run python ejemplos/demo.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import NullLocator

import figuras_cientificas as fc

SALIDA = Path("results") / "ejemplos"
SEMILLA = 42
CONDICIONES = ("Estándar", "Desviante", "Novedoso")


def ic95(muestras: np.ndarray, rng: np.random.Generator, n_boot: int = 2000) -> np.ndarray:
    """IC 95% de la media sobre el eje 0 (sujetos), por bootstrap de percentiles.

    Returns
    -------
    np.ndarray
        Arreglo (2, ...) con los límites inferior y superior.
    """
    indices = rng.integers(0, muestras.shape[0], size=(n_boot, muestras.shape[0]))
    return np.percentile(muestras[indices].mean(axis=1), [2.5, 97.5], axis=0)


def panel_ersp(ax: Axes, rng: np.random.Generator) -> None:
    """ERSP en dB: tiene signo, así que mapa_para elige un divergente simétrico."""
    tiempos = np.linspace(-0.5, 1.5, 200)
    frecuencias = np.geomspace(3, 40, 40)
    t, f = np.meshgrid(tiempos, frecuencias)
    ers_theta = 2.0 * np.exp(-((t - 0.25) ** 2) / 0.02 - np.log(f / 5.5) ** 2 / 0.05)
    erd_alfa_beta = -3.0 * np.exp(-((t - 0.6) ** 2) / 0.08 - np.log(f / 12) ** 2 / 0.15)
    ersp = ers_theta + erd_alfa_beta + 0.3 * rng.standard_normal(t.shape)
    cmap, norm = fc.mapa_para(ersp)
    malla = ax.pcolormesh(tiempos, frecuencias, ersp, cmap=cmap, norm=norm, rasterized=True)
    ax.set_yscale("log")
    ax.set_yticks([4, 8, 13, 30], labels=["4", "8", "13", "30"])
    ax.yaxis.set_minor_locator(NullLocator())
    ax.axvline(0, color="0.2", linewidth=0.5, linestyle="--")
    ax.set(xlabel="Tiempo (s)", ylabel="Frecuencia (Hz)")
    ax.figure.colorbar(
        malla, ax=ax, label="ERSP (dB respecto a la línea base)", extend=fc.extension(ersp, norm)
    )


def panel_conectividad(ax: Axes, rng: np.random.Generator) -> None:
    """Diferencia de conectividad, ordenada por región y con escala simétrica."""
    regiones, por_region = ("Frontal", "Central", "Parietal", "Occipital"), 4
    n = len(regiones) * por_region
    delta = 0.08 * rng.standard_normal((n, n))
    delta = (delta + delta.T) / 2
    delta[:4, :4] += 0.35
    delta[8:, 8:] -= 0.25
    np.fill_diagonal(delta, np.nan)
    cmap, norm = fc.mapa_para(delta)
    imagen = ax.imshow(delta, cmap=cmap, norm=norm)
    centros = np.arange(len(regiones)) * por_region + (por_region - 1) / 2
    ax.set_xticks(centros, labels=regiones)
    ax.set_yticks(centros, labels=regiones)
    ax.tick_params(length=0)
    for borde in np.arange(1, len(regiones)) * por_region - 0.5:
        ax.axhline(borde, color="white", linewidth=0.6)
        ax.axvline(borde, color="white", linewidth=0.6)
    ax.figure.colorbar(
        imagen, ax=ax, label="ΔPLV (desviante − estándar)", extend=fc.extension(delta, norm)
    )


def panel_erp(ax: Axes, rng: np.random.Generator) -> None:
    """ERP promedio de 20 sujetos con IC 95%; color, línea y leyenda por forma."""
    tiempos = np.linspace(-100, 600, 351)
    colores = fc.categorica(len(CONDICIONES))
    for i, nombre in enumerate(CONDICIONES):
        n100 = -(2.5 + 0.5 * i) * np.exp(-((tiempos - 100) ** 2) / 600)
        p300 = (2.0 + 2.2 * i) * np.exp(-((tiempos - (320 + 20 * i)) ** 2) / 4500)
        sujetos = (n100 + p300) * rng.normal(1, 0.25, (20, 1)) + rng.standard_normal((20, 351))
        estilo = fc.estilo_serie(i, colores, marcador=False)
        bajo, alto = ic95(sujetos, rng)
        ax.fill_between(tiempos, bajo, alto, color=estilo["color"], alpha=0.2, linewidth=0)
        ax.plot(tiempos, sujetos.mean(axis=0), **estilo, label=nombre)
    ax.axhline(0, color="0.5", linewidth=0.5)
    ax.axvline(0, color="0.5", linewidth=0.5, linestyle="--")
    ax.set(xlabel="Tiempo (ms)", ylabel="Amplitud (µV), positivo arriba")
    ax.legend(loc="upper left")


def panel_decodificacion(ax: Axes, rng: np.random.Generator) -> None:
    """Exactitud por sujeto, media con IC 95% y umbral de azar por permutación."""
    n_sujetos, n_ensayos = 20, 120
    colores = fc.categorica(len(CONDICIONES))
    for i, media_real in enumerate((0.58, 0.67, 0.74)):
        exactitud = np.clip(rng.normal(media_real, 0.05, n_sujetos), 0, 1)
        estilo = fc.estilo_serie(i, colores)
        ax.scatter(
            i + rng.uniform(-0.12, 0.12, n_sujetos),
            exactitud,
            s=6,
            alpha=0.7,
            color=estilo["color"],
            marker=estilo["marker"],
            linewidths=0,
        )
        bajo, alto = ic95(exactitud, rng)
        media = exactitud.mean()
        ax.errorbar(
            i + 0.3,
            media,
            yerr=[[media - bajo], [alto - media]],
            color=estilo["color"],
            marker=estilo["marker"],
            markersize=4,
        )
    # Con 120 ensayos, el azar no es 0.5: es el percentil 95 de la distribución nula.
    azar = np.percentile(rng.binomial(n_ensayos, 0.5, 10_000) / n_ensayos, 95)
    ax.axhline(azar, color="0.25", linewidth=0.6, linestyle="--")
    ax.text(2.45, azar - 0.008, f"azar por sujeto, p < 0.05 ({azar:.3f})", ha="right", va="top")
    ax.set_xticks(range(len(CONDICIONES)), labels=CONDICIONES)
    ax.set(ylabel="Exactitud de decodificación", ylim=(0.4, 0.9))


def figura_demo() -> Figure:
    """Los cuatro paneles, con letras y tamaño de doble columna."""
    fc.usar_estilo("publicacion")
    rng = np.random.default_rng(SEMILLA)
    fig, ejes = plt.subplots(2, 2, figsize=fc.tamano_figura("doble_columna", alto_mm=120))
    for eje, panel in zip(
        ejes.flat, (panel_ersp, panel_conectividad, panel_erp, panel_decodificacion), strict=True
    ):
        panel(eje, rng)
    for eje, letra in zip(ejes.flat, "abcd", strict=True):
        fc.letra_panel(eje, letra)
    return fig


def main() -> None:
    """Guarda la figura en PDF y PNG, y su revisión de accesibilidad."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    fig = figura_demo()
    fig.savefig(SALIDA / "figura_demo.pdf")
    fig.savefig(SALIDA / "figura_demo.png", dpi=300)
    fc.revisar_figura(fig).savefig(SALIDA / "revision_accesibilidad.png", dpi=150)
    print(f"Figuras en {SALIDA}/: figura_demo.pdf, figura_demo.png, revision_accesibilidad.png")


if __name__ == "__main__":
    main()
