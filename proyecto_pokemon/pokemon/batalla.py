import math
import random
from .modelos import Forcejeo
from .tipos import efectividad


class Batalla:
    def __init__(self, jugador1, jugador2, rng=None):
        self.jugadores = (jugador1, jugador2)
        self.turno_actual = 1
        self.rng = rng if rng is not None else random.Random()
        self.eventos = []
        self.animaciones = []

    def registrar_animacion(self, tipo, actor):
        self.animaciones.append(dict(tipo=tipo, actor=actor,
            activos=[dict(nombre=j.pokemon_activo.nombre, hp=j.pokemon_activo.hp_actual)
                     for j in self.jugadores], eventos=list(self.eventos)))

    def verificar_ganador(self):
        vivos = [j for j in self.jugadores if j.tiene_pokemon_disponibles()]
        return None if len(vivos) == 2 else (vivos[0].nombre if vivos else 'Empate')

    def calcular_daño(self, atacante, movimiento, objetivo, critico=False, aleatorio=1.0):
        ataque, defensa = movimiento.estadisticas(atacante, objetivo)
        base = math.floor(((2 * 50 / 5 + 2) * movimiento.potencia * ataque / defensa) / 50 + 2)
        emergencia = isinstance(movimiento, Forcejeo)
        stab = 1.5 if not emergencia and movimiento.tipo in atacante.tipos else 1
        tipo = 1 if emergencia else efectividad(movimiento.tipo, objetivo.tipos)
        daño = math.floor(base * stab * tipo * (1.5 if critico else 1) * aleatorio)
        return 0 if tipo == 0 else max(1, daño)

    def ejecutar_ataque(self, atacante, movimiento, objetivo):
        movimiento.consumir_pp()
        self.eventos.append(f'{atacante.nombre} usa {movimiento.nombre}.')
        if self.rng.uniform(1, 100) > movimiento.precision:
            self.eventos.append(f'¡El ataque de {atacante.nombre} ha fallado!')
            return
        critico = self.rng.random() <= 1 / 16
        daño = self.calcular_daño(atacante, movimiento, objetivo, critico, self.rng.uniform(.85, 1))
        recibido = objetivo.recibir_daño(daño)
        tipo = 1 if isinstance(movimiento, Forcejeo) else efectividad(movimiento.tipo, objetivo.tipos)
        if tipo == 0:
            self.eventos.append(f'No afecta a {objetivo.nombre}...')
        else:
            self.eventos.append(f'{objetivo.nombre} pierde {recibido} HP.'
                                + (' ¡Golpe crítico!' if critico else '')
                                + (' ¡Súper efectivo!' if tipo > 1 else ' Poco efectivo.' if tipo < 1 else ''))
        if isinstance(movimiento, Forcejeo):
            atacante.recibir_daño(max(1, atacante.hp_max // 4))
            self.eventos.append(f'{atacante.nombre} recibe retroceso.')

    def validar_accion(self, jugador, accion):
        if jugador.pokemon_activo.esta_debilitado():
            raise ValueError('El Pokémon activo está debilitado')
        if accion.tipo == 'cambiar' and accion.indice in jugador.reservas():
            return
        movimientos = jugador.pokemon_activo.movimientos
        if accion.tipo == 'atacar' and 0 <= accion.indice < len(movimientos) and movimientos[accion.indice].es_valido():
            return
        if accion.tipo == 'forcejeo' and not any(m.es_valido() for m in movimientos):
            return
        raise ValueError('Acción inválida o sin PP')

    def resolver_prioridad(self, accion_p1, accion_p2):
        acciones = (accion_p1, accion_p2)
        claves = [(a.tipo == 'cambiar', j.pokemon_activo.velocidad)
                  for j, a in zip(self.jugadores, acciones)]
        if claves[0] == claves[1]:
            return [0, 1] if self.rng.random() < .5 else [1, 0]
        return sorted(range(2), key=lambda i: claves[i], reverse=True)

    def procesar_turno(self, accion_p1, accion_p2):
        """Pausa ante cada reemplazo; recibe su índice mediante send()."""
        if self.verificar_ganador() is not None:
            raise ValueError('El combate ha terminado')
        acciones = (accion_p1, accion_p2)
        for jugador, accion in zip(self.jugadores, acciones):
            self.validar_accion(jugador, accion)
        actores = [j.pokemon_activo for j in self.jugadores]
        self.eventos = []
        for i in self.resolver_prioridad(*acciones):
            jugador, accion = self.jugadores[i], acciones[i]
            # Un reemplazo nunca hereda la acción del Pokémon debilitado.
            if actores[i].esta_debilitado():
                continue
            if accion.tipo == 'cambiar':
                jugador.cambiar_pokemon(accion.indice)
                self.eventos.append(f'{jugador.nombre} cambia a {jugador.pokemon_activo.nombre}.')
            else:
                movimiento = Forcejeo() if accion.tipo == 'forcejeo' else actores[i].movimientos[accion.indice]
                actores[i].atacar(movimiento, self.jugadores[1-i].pokemon_activo, self)
            self.registrar_animacion(accion.tipo, i)
            for j in self.jugadores:
                if j.pokemon_activo.esta_debilitado():
                    self.eventos.append(f'{j.pokemon_activo.nombre} se ha debilitado.')
            if self.verificar_ganador() is not None:
                break
            for j in self.jugadores:
                if j.pokemon_activo.esta_debilitado():
                    indice = yield j
                    j.cambiar_pokemon(indice)
                    self.eventos.append(f'{j.nombre} envía a {j.pokemon_activo.nombre}.')
                    self.registrar_animacion('cambiar', self.jugadores.index(j))
        self.turno_actual += 1
        return list(self.eventos)
