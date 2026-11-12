"""Carrito de compras sobre Redis (base de datos NoSQL llave-valor).

Modelo de datos:
  llave : carrito:<usuario>
  valor : hash de Redis  { producto_id: cantidad }
  TTL   : el carrito se elimina solo tras TTL_SEGUNDOS sin modificaciones.
"""
import os

import redis

TTL_SEGUNDOS = 30 * 60  # 30 minutos de inactividad

# Catálogo de ejemplo: producto_id -> (nombre, precio en colones)
PRODUCTOS = {
    "laptop": ("Laptop", 450000),
    "mouse": ("Mouse inalámbrico", 12000),
    "teclado": ("Teclado mecánico", 35000),
}


def conectar() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
    )


def _llave(usuario: str) -> str:
    return f"carrito:{usuario}"


def agregar(r: redis.Redis, usuario: str, producto: str, cantidad: int = 1) -> int:
    """Suma unidades de un producto y renueva el TTL. Devuelve la cantidad resultante."""
    if producto not in PRODUCTOS:
        raise ValueError(f"Producto desconocido: {producto}")
    if cantidad < 1:
        raise ValueError("La cantidad debe ser al menos 1")
    pipe = r.pipeline()
    pipe.hincrby(_llave(usuario), producto, cantidad)  # atómico, sin leer antes
    pipe.expire(_llave(usuario), TTL_SEGUNDOS)
    total, _ = pipe.execute()
    return total


def quitar(r: redis.Redis, usuario: str, producto: str) -> bool:
    """Elimina un producto del carrito. True si estaba."""
    return r.hdel(_llave(usuario), producto) == 1


def ver(r: redis.Redis, usuario: str) -> dict[str, int]:
    """Devuelve {producto: cantidad}."""
    return {p: int(c) for p, c in r.hgetall(_llave(usuario)).items()}


def total(r: redis.Redis, usuario: str) -> int:
    """Total a pagar en colones."""
    return sum(PRODUCTOS[p][1] * c for p, c in ver(r, usuario).items())


def vaciar(r: redis.Redis, usuario: str) -> None:
    r.delete(_llave(usuario))
