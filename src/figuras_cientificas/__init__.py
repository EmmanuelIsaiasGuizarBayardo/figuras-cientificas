"""Paletas, estilos y verificación de accesibilidad para figuras científicas.

Una sola fuente de verdad para las figuras de investigación: las paletas y la
regla para elegirlas (``paletas``), el tamaño y el estilo de publicación
(``diseno``), y la revisión de accesibilidad de una figura terminada
(``verificacion``). Las reglas completas, con referencias, están en
``visualizacion.md``, dentro del paquete.
"""

from importlib.metadata import version

from figuras_cientificas.diseno import ANCHOS_MM, letra_panel, tamano_figura, usar_estilo
from figuras_cientificas.paletas import (
    categorica,
    ciclico,
    divergente,
    estilo_serie,
    extension,
    mapa_para,
    secuencial,
    trama,
)
from figuras_cientificas.verificacion import (
    contraste,
    luminosidad,
    revisar_figura,
    separacion_minima,
    simular,
)

__version__ = version("figuras-cientificas")

__all__ = [
    "ANCHOS_MM",
    "categorica",
    "ciclico",
    "contraste",
    "divergente",
    "estilo_serie",
    "extension",
    "letra_panel",
    "luminosidad",
    "mapa_para",
    "revisar_figura",
    "secuencial",
    "separacion_minima",
    "simular",
    "tamano_figura",
    "trama",
    "usar_estilo",
]
