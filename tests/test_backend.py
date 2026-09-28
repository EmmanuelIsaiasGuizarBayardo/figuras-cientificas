"""Las pruebas dibujan en memoria, sin abrir ventanas, en cualquier máquina."""

import matplotlib


def test_pruebas_sin_ventanas() -> None:
    assert matplotlib.get_backend().lower() == "agg", "tests/conftest.py debe fijar Agg"
