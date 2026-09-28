"""Configuración de pytest: figuras sin ventanas.

Las pruebas crean figuras. Con el backend interactivo por omisión (TkAgg en
Windows), cada figura abre Tcl/Tk: falla si esa instalación está dañada y no
existe en un CI sin pantalla. Agg dibuja en memoria y se comporta igual en
cualquier máquina. Fijarlo aquí, y no en la biblioteca, deja intacto el backend
de quien la usa.
"""

import matplotlib

matplotlib.use("Agg")
