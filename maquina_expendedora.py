def formato_dinero(valor):
    return "$" + format(valor, ",").replace(",", ".")


def validar_entero(valor, minimo, nombre):
    if type(valor) is not int or valor < minimo:
        raise ValueError(f"{nombre} debe ser un entero mayor o igual a {minimo}.")


class Producto:
    def __init__(self, nombre, precio, codigo):
        validar_entero(precio, 1, "El precio")
        if not nombre.strip() or not codigo.strip():
            raise ValueError("El nombre y el código del producto no pueden estar vacíos.")
        self.nombre = nombre.strip()
        self.precio = precio
        self.codigo = codigo.strip().upper()


class Ranura:
    def __init__(self, producto, cantidad, codigo):
        if not codigo.strip():
            raise ValueError("El código de ranura no puede estar vacío.")
        self.codigo = codigo.strip().upper()
        self.asignar_producto(producto, cantidad)

    def asignar_producto(self, producto, cantidad):
        validar_entero(cantidad, 0, "La cantidad")
        if producto is not None and not isinstance(producto, Producto):
            raise ValueError("Debe asignar un objeto Producto.")
        if producto is None and cantidad != 0:
            raise ValueError("Una ranura sin producto debe tener cantidad cero.")
        self.producto = producto
        self.cantidad = cantidad

    def esta_disponible(self):
        return self.producto is not None and self.cantidad > 0

    def reducir_stock(self, cantidad=1):
        validar_entero(cantidad, 1, "La cantidad que desea retirar")
        if not self.esta_disponible():
            raise ValueError("No hay unidades disponibles en esta ranura.")
        if cantidad > self.cantidad:
            raise ValueError(f"Stock insuficiente. Solo hay {self.cantidad} unidades disponibles.")
        self.cantidad -= cantidad

    def agregar_stock(self, cantidad):
        validar_entero(cantidad, 1, "La cantidad que desea agregar")
        if self.producto is None:
            raise ValueError("La ranura no tiene un producto asignado.")
        self.cantidad += cantidad


class Monedero:
    def __init__(self):
        self.saldo = 0
        self.denominaciones_aceptadas = [
            50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000
        ]

    def ingresar_dinero(self, denominacion):
        if type(denominacion) is not int or denominacion not in self.denominaciones_aceptadas:
            raise ValueError("Denominación inválida. Ingrese una moneda o billete permitido.")
        self.saldo += denominacion

    def consultar_saldo(self):
        return self.saldo

    def descontar_saldo(self, precio):
        validar_entero(precio, 1, "El precio")
        if self.saldo < precio:
            raise ValueError(
                "Saldo insuficiente. Necesita ingresar "
                f"{formato_dinero(precio - self.saldo)} adicionales."
            )
        self.saldo -= precio

    def devolver_dinero(self):
        importe = self.saldo
        self.saldo = 0
        return importe


class MaquinaExpendedora:
    def __init__(self):
        self.ranuras = []
        self.dinero = Monedero()
        self.cargar_ranura("A1", Producto("Galletas", 3000, "P001"), 10)
        self.cargar_ranura("A2", Producto("Papas", 2500, "P002"), 8)
        self.cargar_ranura("A3", Producto("Chocolate", 5000, "P003"), 5)

    def buscar_ranura(self, codigo):
        for ranura in self.ranuras:
            if ranura.codigo == codigo.strip().upper():
                return ranura
        return None

    def cargar_ranura(self, codigo, producto, cantidad, reemplazar=False):
        if not isinstance(producto, Producto):
            raise ValueError("Debe asignar un objeto Producto.")
        validar_entero(cantidad, 0, "La cantidad inicial")
        ranura = self.buscar_ranura(codigo)
        if reemplazar and ranura is None:
            raise ValueError("La ranura que desea reemplazar no existe.")
        if not reemplazar and ranura is not None:
            raise ValueError("Ya existe una ranura con ese código.")
        for existente in self.ranuras:
            if (existente is not ranura and existente.producto is not None
                    and existente.producto.codigo == producto.codigo):
                raise ValueError("El código del producto ya está en otra ranura.")
        if reemplazar:
            ranura.asignar_producto(producto, cantidad)
        else:
            self.ranuras.append(Ranura(producto, cantidad, codigo))

    def mostrar_producto(self, codigo):
        ranura = self.buscar_ranura(codigo)
        if ranura is None:
            raise ValueError("La ranura no existe.")
        if ranura.producto is None:
            print(f"\n{ranura.codigo} - Sin producto asignado")
            return
        producto = ranura.producto
        print(f"\n{ranura.codigo} - {producto.nombre}")
        print(f"Código del producto: {producto.codigo}")
        print(f"Precio: {formato_dinero(producto.precio)}")
        print(f"Disponibles: {ranura.cantidad}")
        if not ranura.esta_disponible():
            print("Agotado")

    def mostrar_inventario(self):
        for ranura in self.ranuras:
            self.mostrar_producto(ranura.codigo)

    def realizar_compra(self, codigo):
        ranura = self.buscar_ranura(codigo)
        if ranura is None:
            raise ValueError("La ranura no existe.")
        if ranura.producto is None:
            raise ValueError("La ranura no tiene un producto asignado.")
        if not ranura.esta_disponible():
            raise ValueError("El producto está agotado.")
        producto = ranura.producto
        self.dinero.descontar_saldo(producto.precio)
        ranura.reducir_stock()
        return producto


def leer_entero(mensaje, minimo):
    while True:
        try:
            valor = int(input(mensaje))
            validar_entero(valor, minimo, "El valor")
            return valor
        except ValueError:
            print(f"Ingrese un número entero mayor o igual a {minimo}, sin puntos ni comas.")


def leer_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("Este campo no puede estar vacío.")


def menu_ingresar_dinero(monedero):
    print("\n===== INGRESAR DINERO =====")
    print("Denominaciones aceptadas:")
    print(", ".join(formato_dinero(valor) for valor in monedero.denominaciones_aceptadas))
    while True:
        print(f"\nSaldo actual: {formato_dinero(monedero.consultar_saldo())}")
        denominacion = leer_entero("Ingrese una denominación (0 para volver): ", 0)
        if denominacion == 0:
            return
        try:
            monedero.ingresar_dinero(denominacion)
            print(f"Dinero recibido: {formato_dinero(denominacion)}")
            print(f"Saldo disponible: {formato_dinero(monedero.consultar_saldo())}")
            return
        except ValueError as error:
            print(error)


def retirar_dinero(monedero):
    saldo = monedero.consultar_saldo()
    if saldo == 0:
        print("No existe dinero pendiente por devolver.")
        return
    print(f"Saldo pendiente: {formato_dinero(saldo)}")
    print(f"Dinero devuelto: {formato_dinero(monedero.devolver_dinero())}")
    print(f"Saldo actual: {formato_dinero(monedero.consultar_saldo())}")


def administrar_stock(maquina, reducir=False):
    codigo = leer_texto("Código de ranura: ")
    ranura = maquina.buscar_ranura(codigo)
    if ranura is None:
        raise ValueError("La ranura no existe.")
    if ranura.producto is None:
        raise ValueError("La ranura no tiene un producto asignado.")
    maquina.mostrar_producto(codigo)
    accion = "retirar" if reducir else "agregar"
    cantidad = leer_entero(f"Unidades que desea {accion}: ", 1)
    anterior = ranura.cantidad
    if reducir:
        ranura.reducir_stock(cantidad)
    else:
        ranura.agregar_stock(cantidad)
    print("Inventario actualizado.")
    print(f"Cantidad anterior: {anterior}")
    cambio = "retirada" if reducir else "agregada"
    print(f"Cantidad {cambio}: {cantidad}")
    print(f"Cantidad actual: {ranura.cantidad}")


def administrar_producto(maquina):
    accion = input("1. Crear ranura\n2. Reemplazar producto\n3. Volver\nSeleccione una opción: ").strip()
    if accion == "3":
        return
    if accion not in ["1", "2"]:
        raise ValueError("Opción inválida.")
    codigo_ranura = leer_texto("Código de ranura: ").upper()
    ranura = maquina.buscar_ranura(codigo_ranura)
    reemplazar = accion == "2"
    if reemplazar and ranura is None:
        raise ValueError("La ranura que desea reemplazar no existe.")
    if not reemplazar and ranura is not None:
        raise ValueError("Ya existe una ranura con ese código.")
    nombre = leer_texto("Nombre del producto: ")
    precio = leer_entero("Precio en pesos (sin puntos ni comas): ", 1)
    codigo_producto = leer_texto("Código del producto: ")
    cantidad = leer_entero("Cantidad inicial: ", 0)
    producto = Producto(nombre, precio, codigo_producto)
    if reemplazar:
        maquina.mostrar_producto(codigo_ranura)
        print(f"Nuevo producto: {producto.nombre} - {formato_dinero(precio)}")
        print(f"Código: {producto.codigo} | Nueva cantidad: {cantidad}")
        confirmacion = input("¿Confirma el reemplazo del producto y su cantidad? (s/n): ")
        if confirmacion.strip().lower() != "s":
            print("Reemplazo cancelado.")
            return
    maquina.cargar_ranura(codigo_ranura, producto, cantidad, reemplazar)
    print("Producto registrado correctamente.")


def menu_admin(maquina):
    while True:
        print("\n===== ADMINISTRADOR =====")
        print("1. Mostrar inventario\n2. Agregar stock\n3. Agregar o cambiar producto")
        print("4. Reducir stock\n5. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()
        try:
            if opcion == "1":
                maquina.mostrar_inventario()
            elif opcion == "2":
                administrar_stock(maquina)
            elif opcion == "3":
                administrar_producto(maquina)
            elif opcion == "4":
                administrar_stock(maquina, reducir=True)
            elif opcion == "5":
                return
            else:
                print("Opción inválida.")
        except ValueError as error:
            print(error)


def main():
    maquina = MaquinaExpendedora()
    try:
        while True:
            print("\n===== MÁQUINA EXPENDEDORA =====")
            print(f"\nSaldo disponible: {formato_dinero(maquina.dinero.consultar_saldo())}")
            print("\n1. Catálogo\n2. Ingresar dinero\n3. Comprar producto")
            print("4. Cancelar y retirar dinero\n5. Admin\n6. Salir")
            opcion = input("\nSeleccione una opción: ").strip()
            try:
                if opcion == "1":
                    print("\n===== CATÁLOGO =====")
                    maquina.mostrar_inventario()
                elif opcion == "2":
                    menu_ingresar_dinero(maquina.dinero)
                elif opcion == "3":
                    print("\n===== COMPRAR PRODUCTO =====")
                    maquina.mostrar_inventario()
                    codigo = leer_texto("\nSeleccione una ranura: ")
                    ranura = maquina.buscar_ranura(codigo)
                    if ranura is not None and ranura.producto is not None:
                        print(f"Precio: {formato_dinero(ranura.producto.precio)}")
                    print(f"Saldo disponible: {formato_dinero(maquina.dinero.consultar_saldo())}")
                    producto = maquina.realizar_compra(codigo)
                    print(f"Producto entregado: {producto.nombre}")
                    print("Compra realizada correctamente.")
                    print(f"Saldo restante: {formato_dinero(maquina.dinero.consultar_saldo())}")
                elif opcion == "4":
                    print("\n===== RETIRAR DINERO =====")
                    retirar_dinero(maquina.dinero)
                elif opcion == "5":
                    menu_admin(maquina)
                elif opcion == "6":
                    break
                else:
                    print("Opción inválida.")
            except ValueError as error:
                print(error)
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada interrumpida. Finalizando la sesión.")
    print("\n===== FINALIZAR =====")
    retirar_dinero(maquina.dinero)
    print("Gracias por utilizar la máquina expendedora.")


if __name__ == "__main__":
    main()
