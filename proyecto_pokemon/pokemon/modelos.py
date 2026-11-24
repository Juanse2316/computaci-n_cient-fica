from abc import ABC, abstractmethod
from dataclasses import dataclass
from .tipos import TIPOS


class Movimiento(ABC):
    """La categoría elige polimórficamente las estadísticas del daño."""
    categoria = ''

    def __init__(self, nombre, tipo, potencia, precision, pp_max):
        if tipo not in TIPOS or potencia <= 0 or not 0 <= precision <= 100 or pp_max <= 0:
            raise ValueError('Movimiento inválido')
        self.nombre, self.tipo = nombre, tipo
        self.potencia, self.precision, self.pp_max = potencia, precision, pp_max
        self._pp_actual = pp_max

    @property
    def pp_actual(self):
        return self._pp_actual

    def es_valido(self):
        return self.pp_actual > 0

    def consumir_pp(self):
        if not self.es_valido():
            raise ValueError('No quedan PP')
        self._pp_actual -= 1

    @abstractmethod
    def estadisticas(self, atacante, objetivo):
        pass


class MovimientoFisico(Movimiento):
    categoria = 'Físico'

    def estadisticas(self, atacante, objetivo):
        return atacante.ataque, objetivo.defensa


class MovimientoEspecial(Movimiento):
    categoria = 'Especial'

    def estadisticas(self, atacante, objetivo):
        return atacante.at_especial, objetivo.def_especial


class Forcejeo(MovimientoFisico):
    """Emergencia sin PP: daño neutral, sin STAB y retroceso de 1/4 HP."""
    def __init__(self):
        super().__init__('Forcejeo', 'Normal', 50, 100, 1)


class Pokemon:
    def __init__(self, id, nombre, tipo_1, tipo_2, estadisticas, movimientos):
        if tipo_1 not in TIPOS or (tipo_2 is not None and tipo_2 not in TIPOS):
            raise ValueError('Tipo inválido')
        claves = ('hp', 'ataque', 'defensa', 'at_especial', 'def_especial', 'velocidad')
        if any(not isinstance(estadisticas[k], int) or estadisticas[k] <= 0 for k in claves):
            raise ValueError('Las estadísticas deben ser enteros positivos')
        if len(movimientos) != 4:
            raise ValueError('Cada Pokémon debe tener cuatro movimientos')
        self.id, self.nombre = id, nombre
        self.tipo_1, self.tipo_2 = tipo_1, tipo_2
        self.hp_max = estadisticas['hp']
        self._hp_actual = self.hp_max
        for clave in claves[1:]:
            setattr(self, clave, estadisticas[clave])
        self.movimientos = movimientos

    @property
    def tipos(self):
        return tuple(t for t in (self.tipo_1, self.tipo_2) if t is not None)

    @property
    def hp_actual(self):
        return self._hp_actual

    def recibir_daño(self, cantidad):
        if cantidad < 0:
            raise ValueError('El daño no puede ser negativo')
        recibido = min(self.hp_actual, int(cantidad))
        self._hp_actual -= recibido
        return recibido

    def esta_debilitado(self):
        return self.hp_actual == 0

    def obtener_estadistica(self, nombre):
        if nombre not in ('ataque', 'defensa', 'at_especial', 'def_especial', 'velocidad'):
            raise ValueError('Estadística desconocida')
        return getattr(self, nombre)

    def atacar(self, movimiento, objetivo, batalla):
        return batalla.ejecutar_ataque(self, movimiento, objetivo)


@dataclass(frozen=True)
class Accion:
    tipo: str
    indice: int = 0


class Entrenador:
    def __init__(self, nombre, equipo):
        if len(equipo) != 3 or len({p.id for p in equipo}) != 3:
            raise ValueError('Selecciona tres Pokémon diferentes')
        self.nombre, self.equipo = nombre, equipo
        self._indice_activo = 0

    @property
    def pokemon_activo(self):
        return self.equipo[self._indice_activo]

    def reservas(self):
        return [i for i, p in enumerate(self.equipo)
                if i != self._indice_activo and not p.esta_debilitado()]

    def cambiar_pokemon(self, nuevo_indice):
        if nuevo_indice not in self.reservas():
            raise ValueError('Reserva inválida')
        self._indice_activo = nuevo_indice

    def tiene_pokemon_disponibles(self):
        return any(not p.esta_debilitado() for p in self.equipo)
