# Topomaps con MNE: mapa contenido en la cabeza y electrodos bien centrados

Guía técnica de `figuras-cientificas`; en un proyecto se consulta con
`uv run python -m figuras_cientificas guia topomaps_mne`. Verificada con MNE 1.13.

## El truco en una línea

Deja que **MNE haga todo**: posiciones, proyección, interpolación, contorno y marcadores, a partir de un `info` con montaje estándar. Los problemas aparecen cuando alguna pieza se calcula por fuera (coordenadas propias, `scatter` manual) o cuando la esfera de proyección no corresponde a las posiciones.

## Código mínimo (el que usamos en la Fig. 4)

```python
import matplotlib.pyplot as plt
import mne
import numpy as np

import figuras_cientificas as fc

# 1. Info con montaje estándar (nombres EXACTOS como en el montaje)
info = mne.create_info(ch_names=ALL_CHANNELS, sfreq=512, ch_types="eeg")
info.set_montage("biosemi32", on_missing="raise")  # falla si un nombre no coincide

# 2. Máscara opcional para resaltar un subconjunto (p. ej., Emotiv)
mask = np.array([ch in EMOTIV_CHANNELS for ch in ALL_CHANNELS])

fig, ax = plt.subplots(figsize=(4, 4))
im, _ = mne.viz.plot_topomap(
    importance,  # vector (n_canales,), mismo orden que info["ch_names"]
    info,  # se pasa info, NO coordenadas propias
    axes=ax,
    cmap=fc.secuencial(),  # o el que decida fc.mapa_para(importance)
    vlim=(0, 1),
    extrapolate="head",  # extrapola hasta el contorno de la cabeza, no más allá
    outlines="head",  # contorno, nariz y orejas consistentes con la esfera
    border="mean",  # valor en el borde = media de vecinos (evita artefactos)
    image_interp="cubic",
    contours=4,
    sensors=True,  # puntos de sensores dibujados por MNE
    names=ALL_CHANNELS,  # etiquetas en las posiciones proyectadas por MNE
    mask=mask,
    mask_params=dict(
        marker="o", markerfacecolor="white", markeredgecolor="black", markersize=9, linewidth=0
    ),
    show=False,
)
fig.colorbar(im, ax=ax, shrink=0.7)
```

## Causas típicas de un topomap mal formado

| Síntoma | Causa probable | Solución |
|---|---|---|
| El color se sale del círculo | `extrapolate="box"` u `outlines=None` | `extrapolate="head"` y `outlines="head"` |
| Electrodos fuera de la cabeza o el círculo no envuelve los sensores | Esfera de proyección distinta a la escala de las posiciones (frecuente al cargar `.set` de EEGLAB, que trae sus propias coordenadas) | Asignar el montaje estándar con `set_montage("biosemi32")`, o pasar `sphere="eeglab"` si conservas las posiciones del archivo |
| Puntos desplazados respecto al mapa | Electrodos dibujados con `ax.scatter` usando coordenadas 3D o una proyección propia | Usar `sensors=True`, `names=` y `mask=` de `plot_topomap`, nunca un `scatter` aparte |
| Mapa "girado" o etiquetas en lugar equivocado | El vector de datos no está en el mismo orden que `info["ch_names"]` | Reordenar: `data = data_dict` mapeado a `info["ch_names"]` |
| Pocos electrodos visibles o canales faltantes | Nombres que no coinciden con el montaje (mayúsculas, "Fpz" vs "FPz") | `on_missing="raise"` para detectarlo; `mne.rename_channels` si hace falta |
| Cabeza ovalada | Ejes con aspecto distinto | MNE fija el aspecto; no cambies `ax.set_aspect` ni el tamaño del eje después |

## Cómo validarlo antes de graficar datos

```python
# Debe verse cada sensor dentro del contorno y con su nombre correcto
mne.viz.plot_sensors(info, kind="topomap", show_names=True)

# Prueba con datos sintéticos: un "foco" en un canal conocido
test = np.zeros(len(ALL_CHANNELS))
test[ALL_CHANNELS.index("O1")] = 1
mne.viz.plot_topomap(test, info, extrapolate="head", outlines="head")
# El máximo debe aparecer sobre O1 (occipital izquierdo). Si aparece en otro lado,
# el orden de los datos o las posiciones están mal.
```

## Si necesitas posiciones propias

Si tienes coordenadas reales del registro y no quieres el montaje estándar, crea el montaje con `mne.channels.make_dig_montage(ch_pos=..., coord_frame="head")` y ajusta la esfera a esas posiciones:

```python
radius, origin, _ = mne.bem.fit_sphere_to_headshape(info, units="m")
mne.viz.plot_topomap(data, info, sphere=(*origin, radius), extrapolate="head", outlines="head")
```

## Detalles de estilo que usamos

- **Etiquetas legibles:** MNE dibuja los nombres como textos del eje; después de graficar puedes recorrer `ax.texts` para cambiar tamaño, color o peso (`txt.set_fontsize(...)`, `txt.set_fontweight("normal")`).
- **Mostrar solo un subconjunto de nombres:** pasa una lista con cadenas vacías para los canales que no quieres rotular: `[ch if ch in subset else "" for ch in ALL_CHANNELS]`.
- **Comparar mapas:** usa el mismo `vlim` en todos los mapas que se comparan. El mapa lo decide `fc.mapa_para(datos)`: divergente simétrico solo si los datos tienen ambos signos o un centro natural; una diferencia que es ≥ 0 por construcción es secuencial.

### 1. Etiquetas de canal: tamaño, peso y contraste

Con `mask`, MNE dibuja los nombres de esos canales en negritas y al tamaño base de la fuente, y el resto en peso normal y a cerca del 70% de ese tamaño; sin `mask`, todos salen normales. En mapas pequeños, los nombres en negritas desbordan los círculos. Post-procesa `ax.texts` justo después de cada `plot_topomap` (antes de añadir otros textos al eje):

```python
import matplotlib.patheffects as pe


def style_channel_labels(ax, ch_names, mask, size=5.8, whiten_unmasked=True):
    for txt in ax.texts:
        if txt.get_text() not in ch_names:
            continue
        txt.set_fontsize(size)
        txt.set_fontweight("normal")  # las negritas desbordan el círculo
        inside = mask[ch_names.index(txt.get_text())]
        if whiten_unmasked and not inside:  # texto sobre el mapa de color
            txt.set_color("white")
            txt.set_path_effects([pe.withStroke(linewidth=1.0, foreground="black")])
        else:  # texto dentro del círculo blanco
            txt.set_color("black")
            txt.set_path_effects([])
```

Balancea el círculo con la etiqueta: con figura de 7.5 in usamos `markersize=11.5` en `mask_params` y etiquetas de 5.8 pt. Si cambias el tamaño de la figura, ajusta ambos juntos. Diseñando al tamaño final, como pide el perfil `cnib_lncs`, eso equivale a ~7.4 y ~3.7 pt.

### 2. Rotula solo lo que el lector necesita

Fue la petición explícita del revisor. En las columnas del subconjunto (Emotiv y diferencia), rotula solo esos canales; el mapa completo puede conservar los 32:

```python
subset_names = [ch if ch in EMOTIV_CHANNELS else "" for ch in ALL_CHANNELS]
mne.viz.plot_topomap(..., names=subset_names, mask=emotiv_mask, ...)
```
