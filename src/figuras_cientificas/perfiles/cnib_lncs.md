# Perfil de visualización: congreso CNIB / Springer LNCS

Complementa a `visualizacion.md`. Se aplica a figuras para el CNIB (proceedings de
Springer, plantilla LNCS) o para cualquier venue con requisitos equivalentes. Sus
reglas salen de las instrucciones de autor del CNIB 2026, de los comentarios de los
revisores del manuscrito 151 y de los ajustes que llevaron a sus cuatro figuras
finales (`Figure1.tif` a `Figure4.tif`).

Requiere `figuras-cientificas` 0.2.0 o posterior. Las funciones marcadas con
**(v0.2.0)** no existen en versiones anteriores; para esos casos se incluye el
código equivalente. En un proyecto, el perfil se instala junto a las reglas con
`uv run python -m figuras_cientificas regla --perfil cnib_lncs`.

## Precedencia

1. Instrucciones de autor del venue (obligatorias; motivo de rechazo).
2. Este perfil.
3. `visualizacion.md` (reglas generales).

Todo lo que este perfil no menciona se rige por `visualizacion.md`.

## Qué sobrescribe y por qué

| Regla general | En este perfil | Motivo |
|---|---|---|
| Ancho de 89 o 183 mm (Nature) | 122 mm, el ancho de texto LNCS: `fc.tamano_figura("lncs", alto_mm=...)` **(v0.2.0)** o `fc.tamano_figura(122, alto_mm=...)` | Plantilla LNCS de una columna |
| Letra de panel minúscula, `a` | `A)` arriba a la izquierda: `fc.letra_panel(ax, "a", estilo="parentesis")` **(v0.2.0)** | Requisito del CNIB (Apéndice A) |
| PDF vectorial | TIFF a 300 dpi, RGB sin alfa, LZW, nombre `FigureN.tif`: `fc.exportar_tiff(fig, "Figure1.tif")` **(v0.2.0)** | Requisito del CNIB |
| Pie libre | `Figure N. Título. A) ... B) ...`; nunca "Fig. N" en el pie (en el texto sí) | Requisito del CNIB |
| Sin texto alternativo | *Alt-Text* en cada figura dentro del Word | *Checklist* del CNIB |

Se mantiene la regla general de **no usar `bbox_inches="tight"`**: con la figura
diseñada a su tamaño final, recortar cambiaría ese tamaño.

## Tamaño y tipografía

Diseña al tamaño final con el estilo de publicación (texto de 7 pt), igual que en la
regla general; solo cambia el ancho:

```python
import matplotlib.pyplot as plt
import figuras_cientificas as fc

fc.usar_estilo("publicacion")
fig, axes = plt.subplots(1, 3, figsize=fc.tamano_figura(122, alto_mm=50))
```

Tamaños de referencia de las figuras del 151, ya convertidos a tamaño final:

| Figura | Tamaño final |
|---|---|
| Barras o matrices de 3 paneles | 122 × 50 mm |
| ROC de un panel | 90 × 90 mm |
| Topografías 3 × 3 | 122 × 133 mm |

Nota histórica: el script del 151 (`generate_paper_figures.py`) no usa el paquete.
Diseñó a 7.5 in con texto de 10 pt y Word lo redujo ×0.64 al insertarlo; el
resultado impreso (~6.4 pt) es equivalente, pero ese atajo ya no se recomienda.

Sin título incrustado: el título vive en el pie.

## Letras de panel

```python
fc.letra_panel(ax, "a", estilo="parentesis")  # dibuja "A)"   (v0.2.0)
```

Equivalente para versiones anteriores, usando la ranura de título izquierda (el
*layout* la respeta y coexiste con el título centrado):

```python
ax.set_title("A)", loc="left", fontweight="bold")
```

En paneles angostos donde el título centrado choca con la letra, colócala sobre la
zona de la etiqueta del eje y, alineada con la línea base del título:

```python
ax.annotate(
    "A)",
    xy=(-0.24, 1.0),
    xycoords="axes fraction",
    xytext=(0, plt.rcParams["axes.titlepad"]),
    textcoords="offset points",
    ha="left",
    va="baseline",
    fontweight="bold",
)
```

## Recetas por tipo de figura

### Comparación de exactitud entre esquemas (Fig. 1)

- Color por grupo y segunda codificación por **trama** (`fc.trama(i)`), de modo que
  la figura se lea sin color.
- **Una sola leyenda** (`fig.legend`) con parches neutros, debajo de la figura.
- Anotación directa sobre cada barra con la configuración ganadora; abreviaturas
  inequívocas (`SVM-lin`, `SVM-quad`, `k-NN`).
- El criterio de selección debe ser **idéntico** al de la tabla del texto (en el
  151: mejor exactitud *subject-wise* excluyendo la métrica `all`).

### Matrices de confusión (Fig. 2)

- Celdas con conteo y porcentaje de la clase real; `vmin=0, vmax=100` en todas.
- **Una barra de color compartida** (`fig.colorbar(..., ax=list(axes))`).
- El nombre del modelo va en el pie, no en el título del panel.
- `fc.secuencial()`: porcentaje sin centro natural.

### Curvas ROC (Fig. 3)

- Una curva por contraste con `fc.estilo_serie(i, colores)` (color, línea y
  marcador); `markevery` para no saturar; diagonal de azar punteada en gris.
- Si la leyenda reporta AUC de predicciones agrupadas y la tabla el AUC por
  partición, el pie lo aclara: son resúmenes distintos.
- Aspecto `equal`.

### Topografías comparativas (Fig. 4)

Técnica de MNE en la guía `guias/topomaps_mne.md`, que viene con el paquete y se consulta
con `uv run python -m figuras_cientificas guia topomaps_mne`. Reglas de publicación:

- Etiquetas de canal en peso normal (MNE usa negritas que desbordan los círculos),
  en blanco con trazo negro sobre el mapa y en negro dentro de los círculos.
- Círculo y etiqueta proporcionales: el 151 usó `markersize=11.5` y 5.8 pt a
  7.5 in de diseño; a tamaño final equivale a ~7.4 y ~3.7 pt.
- En las columnas de un subconjunto (por ejemplo, Emotiv), rotular solo esos
  canales: fue la petición explícita de un revisor.
- Letra de panel por fila; por mapa solo si el venue lo pide.
- Con dos escalas (importancia y diferencia), barras de color **horizontales bajo
  las columnas que describen**.
- El mapa de cada columna lo decide `fc.mapa_para(datos)`, no el tipo de panel: una
  diferencia que es ≥ 0 por construcción es secuencial.

## Exportación

```python
fc.exportar_tiff(fig, "Figure1.tif")  # RGB, 300 dpi, LZW, sin alfa   (v0.2.0)
```

Equivalente para versiones anteriores:

```python
import io
from PIL import Image


def exportar_tiff(fig, ruta, dpi=300):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    buf.seek(0)
    im = Image.open(buf).convert("RGBA")
    rgb = Image.new("RGB", im.size, "white")
    rgb.paste(im, mask=im.split()[3])
    rgb.save(ruta, format="TIFF", dpi=(dpi, dpi), compression="tiff_lzw")
```

En Word: desactivar la compresión de imágenes (*Opciones → Avanzadas → No comprimir
las imágenes*, resolución "Alta fidelidad"), reemplazar con *Cambiar imagen → Desde
un archivo* e insertar al tamaño de diseño (122 mm para ancho completo).

## Verificación contra el manuscrito

Cada script imprime los valores que su figura muestra y los compara con los del
texto (configuraciones, conteos, AUC, retenciones). Un solo `[DIF]` bloquea la
entrega. Fue lo que detectó que la Fig. 1 entregada usaba una lógica de selección
distinta a la de la Tabla 1.

## Desviaciones conocidas en las figuras del 151

Cumplen las instrucciones del CNIB, pero no tres reglas generales; corregirlas en
trabajos futuros:

1. El mapa de diferencias usa `managua` (centro oscuro) sobre fondo claro; además,
   la diferencia 32 − 14 es ≥ 0, así que corresponde un secuencial.
2. La Fig. 1 resume 50 evaluaciones con media ± DE en barras; la regla general pide
   mostrar la distribución y preferir IC 95%.
3. El texto y la presentación usan azar = 0.50; la regla general pide el nivel de
   azar empírico por permutación (Combrisson & Jerbi, 2015).

Compromiso conocido: las etiquetas de canal quedan en ~3.7 pt impresas, por debajo
del mínimo de 5 pt. Para la tesina, usar menos mapas por figura o doble página.

## Antes de enviar

- [ ] Letras `A)`, `B)`, `C)` en toda figura multipanel.
- [ ] Pies en formato `Figure N. Título. A) ...`, dentro del límite de palabras.
- [ ] `FigureN.tif`: RGB, 300 dpi, LZW.
- [ ] *Alt-Text* en cada figura del Word.
- [ ] Reporte de verificación sin `[DIF]`.
- [ ] `fc.revisar_figura(fig)` sin pérdida de información en deuteranopia,
      protanopia, tritanopia ni en luminosidad.
