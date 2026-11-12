import os

import pytest

os.environ.setdefault("REDIS_DB", "15")  # base aislada para pruebas

import carrito  # noqa: E402


@pytest.fixture
def r():
    cliente = carrito.conectar()
    cliente.flushdb()
    yield cliente
    cliente.flushdb()


def test_agregar_suma_cantidades(r):
    carrito.agregar(r, "ana", "mouse")
    assert carrito.agregar(r, "ana", "mouse", 2) == 3
    assert carrito.ver(r, "ana") == {"mouse": 3}


def test_carritos_son_independientes(r):
    carrito.agregar(r, "ana", "mouse")
    assert carrito.ver(r, "luis") == {}


def test_total(r):
    carrito.agregar(r, "ana", "laptop")
    carrito.agregar(r, "ana", "mouse", 2)
    assert carrito.total(r, "ana") == 450000 + 2 * 12000


def test_quitar_y_vaciar(r):
    carrito.agregar(r, "ana", "mouse")
    carrito.agregar(r, "ana", "teclado")
    assert carrito.quitar(r, "ana", "mouse") is True
    assert carrito.quitar(r, "ana", "mouse") is False
    carrito.vaciar(r, "ana")
    assert carrito.ver(r, "ana") == {}


def test_carrito_tiene_ttl_y_se_renueva(r):
    carrito.agregar(r, "ana", "mouse")
    r.expire("carrito:ana", 5)
    carrito.agregar(r, "ana", "mouse")
    assert r.ttl("carrito:ana") > 5


def test_producto_invalido(r):
    with pytest.raises(ValueError):
        carrito.agregar(r, "ana", "no-existe")
    with pytest.raises(ValueError):
        carrito.agregar(r, "ana", "mouse", 0)
