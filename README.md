# figuras-cientificas

Paletas, estilos y verificación de accesibilidad para figuras científicas.

## Estructura

```
src/figuras_cientificas/   Código fuente. Paquete instalable.
tests/             Pruebas.
tools/             Utilidades del repositorio.
```

## Puesta en marcha

Requisitos: Git y [uv](https://docs.astral.sh/uv/). Funciona igual en Windows, Mac y Linux.

```
uv sync
uv run pre-commit install
```

`uv sync` crea `.venv`, instala desde `uv.lock` e instala el paquete en modo editable.

**Sin uv, solo con pip:**

```
python -m venv .venv
# Windows:    .venv\Scripts\activate
# Mac/Linux:  source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
```

## Dependencias

`pyproject.toml` → `uv.lock` (fuente de verdad) → `requirements.txt` (export).

Para agregar una dependencia: `uv add <paquete>`. Al hacer commit, un hook regenera
`uv.lock` y `requirements.txt`; si los modifica, el commit se detiene a propósito y
basta con volver a agregar los archivos.

## Licencia

El código se distribuye bajo la licencia MIT (`LICENSE`).

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
