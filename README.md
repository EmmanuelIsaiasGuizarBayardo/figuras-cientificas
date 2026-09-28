# figuras-cientificas

Paletas, estilos y verificación de accesibilidad para figuras científicas. Es una
sola fuente de verdad para las figuras de investigación: el color se elige según
los datos, el tamaño sigue la guía de Nature y cada figura se puede revisar como
la ve una persona con daltonismo. Las reglas completas, con referencias, están en
[`src/figuras_cientificas/visualizacion.md`](src/figuras_cientificas/visualizacion.md).

## Usar en una investigación

```
uv add git+https://github.com/EmmanuelIsaiasGuizarBayardo/figuras-cientificas --tag v0.1.1
uv run python -m figuras_cientificas regla
```

La primera línea la agrega como dependencia, y `uv.lock` fija la versión exacta
que usó cada investigación. La segunda escribe `.agents/rules/visualizacion.md`,
para que Antigravity aplique las reglas en ese proyecto. Para actualizar, cambia
la etiqueta en `uv add` y vuelve a correr `regla`.

```python
import matplotlib.pyplot as plt
import figuras_cientificas as fc

fc.usar_estilo("publicacion")  # guía de Nature: texto de 5 a 7 pt, editable
fig, (a, b) = plt.subplots(1, 2, figsize=fc.tamano_figura("doble_columna", alto_mm=70))

cmap, norm = fc.mapa_para(ersp)  # divergente simétrico o secuencial, según los datos
malla = a.pcolormesh(tiempos, frecuencias, ersp, cmap=cmap, norm=norm)
fig.colorbar(malla, ax=a, extend=fc.extension(ersp, norm))  # marca lo recortado

colores = fc.categorica(len(erps))  # petroff6 hasta seis series
for i, erp in enumerate(erps):
    b.plot(tiempos, erp, **fc.estilo_serie(i, colores, marcador=False))

for eje, letra in zip((a, b), "ab", strict=True):
    fc.letra_panel(eje, letra)
fig.savefig("figura.pdf")  # sin bbox_inches="tight": conserva los 183 mm
fc.revisar_figura(fig).savefig("revision.png")  # daltonismo simulado y luminosidad
```

`ejemplos/demo.py` aplica todas las reglas en una figura completa:
`uv run python ejemplos/demo.py` la guarda en `results/ejemplos/`.

## Qué verifican las pruebas

Cada elección de la biblioteca es una propiedad medida, y `uv run pytest` falla si
una actualización de matplotlib o de cmcrameri la rompe:

- El mapa secuencial tiene luminosidad estrictamente creciente.
- El divergente para fondo claro tiene el centro claro; el de fondo oscuro, oscuro;
  en ambos los extremos difieren menos de 3 unidades de L* y el positivo es cálido.
- Toda paleta categórica de 2 a 10 colores separa sus colores bajo deuteranopia,
  protanopia y tritanopia simuladas; los cuatro primeros de Okabe-Ito tienen
  contraste de al menos 3:1 contra blanco.
- Un PDF de una columna mide 89 mm, y el texto queda editable.

## Estructura

```
src/figuras_cientificas/   paletas.py, diseno.py, verificacion.py, estilos/ y las reglas.
tests/                     Pruebas de las propiedades medidas.
ejemplos/                  Figura de demostración.
tools/                     Utilidades del repositorio.
```

## Puesta en marcha

Requisitos: Git y [uv](https://docs.astral.sh/uv/). Funciona igual en Windows, Mac y Linux.

```
uv sync
uv run pre-commit install
```

`uv sync` crea `.venv`, instala desde `uv.lock` e instala el paquete en modo editable.

## Dependencias

`pyproject.toml` → `uv.lock` (fuente de verdad) → `requirements.txt` (export).
Requiere matplotlib 3.11 o posterior, que incluye `petroff6`, `petroff10` y
`okabe_ito`; cmcrameri aporta los mapas de Crameri y colorspacious la simulación
de daltonismo.

## Licencia

El código se distribuye bajo la licencia MIT (`LICENSE`). Los mapas de color son de
Crameri (2018) y las secuencias categóricas de Petroff (2024); al publicar, se citan
como indica la sección "Cómo citar" de las reglas.

## Créditos

Los roles de cada persona, en taxonomía CRediT, están en `CREDITS.md`. Para citar
el proyecto, GitHub genera la referencia desde `CITATION.cff` con el botón
**Cite this repository**. Para contribuir, ver `CONTRIBUTING.md`.

## Estándar DUNNE

Este proyecto nació de la plantilla DUNNE. Las reglas que le aplican están en
`docs/estandar/` y los comandos de uso frecuente en `docs/comandos.md`.
`AGENTS.md` le entrega ese contexto a Claude Code y a la mayoría de los
asistentes de código.

Para traer las mejoras más recientes del estándar, con el árbol de trabajo limpio:

```
uvx copier update --trust
```
