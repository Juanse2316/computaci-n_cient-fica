# Diagrama de clases

```mermaid
classDiagram
    class Movimiento {
        <<abstract>>
        +nombre
        +tipo
        +potencia
        +precision
        +pp_max
        -pp_actual
        +consumir_pp()
        +es_valido()
        +estadisticas(atacante, objetivo)*
    }
    Movimiento <|-- MovimientoFisico
    Movimiento <|-- MovimientoEspecial
    MovimientoFisico <|-- Forcejeo
    class Pokemon {
        +nombre
        +tipos
        +hp_max
        -hp_actual
        +recibir_daño(cantidad)
        +esta_debilitado()
        +atacar(movimiento, objetivo, batalla)
        +obtener_estadistica(nombre)
    }
    class Entrenador {
        +nombre
        +pokemon_activo
        +reservas()
        +cambiar_pokemon(indice)
        +tiene_pokemon_disponibles()
    }
    class Batalla {
        +turno_actual
        +procesar_turno(accion_p1, accion_p2)
        +resolver_prioridad(accion_p1, accion_p2)
        +calcular_daño(atacante, movimiento, objetivo)
        +verificar_ganador()
    }
    class Accion {
        +tipo
        +indice
    }
    class Catalogo {
        +crear(id)
    }
    Pokemon "1" *-- "4" Movimiento
    Entrenador "1" *-- "3" Pokemon
    Batalla "1" o-- "2" Entrenador
    Batalla ..> Accion
    Catalogo ..> Pokemon
    CLI ..> Catalogo
    CLI ..> Batalla
    CLI ..> Accion
```

La interfaz CLI gestiona `elegir_accion` e `iniciar_combate`, separando las entradas de usuario del motor. El motor solicita los reemplazos mediante una función inyectada. El flujo es: comandos → validación → prioridad → ejecución → debilitamientos/reemplazos → victoria o siguiente turno.
