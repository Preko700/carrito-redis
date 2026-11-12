# Carrito de compras con Redis

Programa en **Python** que usa **Redis**, una base de datos NoSQL de tipo **llave-valor**, para manejar el carrito de compras de una tienda en línea.

## Escenario

Una tienda en línea necesita guardar el carrito de cada cliente mientras navega. El carrito se consulta y se modifica constantemente (agregar un producto, quitarlo, ver el total), así que necesita respuestas muy rápidas. Además, si el cliente abandona la tienda, su carrito no debe quedar ocupando espacio para siempre.

Siempre se accede al carrito por el identificador del cliente. No hacen falta consultas complejas ni relaciones con otras tablas, por eso una base llave-valor encaja bien.

## Cómo se resolvió con llave-valor

Cada cliente tiene **una llave** y su valor es un **hash** de Redis, es decir, un pequeño diccionario de producto y cantidad:

```
carrito:ana  ->  { "laptop": 1, "mouse": 3 }
carrito:luis ->  { "teclado": 1 }
```

| Operación del carrito | Comando de Redis | Función en `carrito.py` |
|---|---|---|
| Agregar unidades de un producto | `HINCRBY carrito:<usuario> <producto> <n>` | `agregar` |
| Quitar un producto | `HDEL carrito:<usuario> <producto>` | `quitar` |
| Ver el carrito | `HGETALL carrito:<usuario>` | `ver` |
| Vaciar el carrito (al pagar) | `DEL carrito:<usuario>` | `vaciar` |
| Expirar el carrito abandonado | `EXPIRE carrito:<usuario> 1800` | `agregar` |

Detalles de diseño:

- `HINCRBY` suma de forma **atómica** sin leer antes el valor, así que dos pestañas del mismo cliente no se pisan.
- Cada vez que se agrega algo se renueva `EXPIRE` a 30 minutos. Un carrito abandonado desaparece solo, sin tareas de limpieza.
- Los precios están en un diccionario dentro del código, y el total se calcula al consultarlo. Redis solo guarda las cantidades.

## Archivos

```
carrito.py        lógica del carrito (todas las operaciones con Redis)
main.py           demo ejecutable
test_carrito.py   6 pruebas con pytest
docker-compose.yml, requirements.txt
```

## Cómo ejecutarlo

Requisitos: Python 3.10+ y un servidor Redis (cualquier versión reciente).

```bash
docker compose up -d          # o: redis-server
pip install -r requirements.txt
python main.py                # demo
pytest -q                     # pruebas (usan la base 15, no tocan la 0)
```

La conexión se configura con `REDIS_HOST`, `REDIS_PORT` y `REDIS_DB`.

## Salida de la demo

```
Carrito de ana:
  1 x Laptop = ₡450,000
  3 x Mouse inalámbrico = ₡36,000
  TOTAL: ₡486,000
  Expira en: 1800 s

Ana quita el mouse...

Carrito de ana:
  1 x Laptop = ₡450,000
  TOTAL: ₡450,000
  Expira en: 1800 s

Ana paga: se vacía su carrito.

Carrito de ana:
  (vacío)
  TOTAL: ₡0
```
