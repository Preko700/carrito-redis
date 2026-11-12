"""Demo: carrito de compras de una tienda en línea usando Redis."""
import carrito


def mostrar(r, usuario: str) -> None:
    print(f"\nCarrito de {usuario}:")
    items = carrito.ver(r, usuario)
    if not items:
        print("  (vacío)")
    for producto, cantidad in items.items():
        nombre, precio = carrito.PRODUCTOS[producto]
        print(f"  {cantidad} x {nombre} = ₡{precio * cantidad:,}")
    print(f"  TOTAL: ₡{carrito.total(r, usuario):,}")
    if items:
        print(f"  Expira en: {r.ttl(f'carrito:{usuario}')} s")


def main() -> None:
    r = carrito.conectar()
    r.ping()
    for usuario in ("ana", "luis"):
        carrito.vaciar(r, usuario)

    carrito.agregar(r, "ana", "laptop")
    carrito.agregar(r, "ana", "mouse", 2)
    carrito.agregar(r, "ana", "mouse")  # suma una unidad más
    carrito.agregar(r, "luis", "teclado")
    mostrar(r, "ana")
    mostrar(r, "luis")

    print("\nAna quita el mouse...")
    carrito.quitar(r, "ana", "mouse")
    mostrar(r, "ana")

    print("\nAna paga: se vacía su carrito.")
    carrito.vaciar(r, "ana")
    mostrar(r, "ana")


if __name__ == "__main__":
    main()
