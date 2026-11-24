import argparse
import random
from .datos import Catalogo
from .modelos import Accion, Entrenador
from .batalla import Batalla


def elegir(mensaje, opciones):
    while True:
        texto = input(mensaje).strip()
        if texto.lower() in ('q', 'salir'):
            raise EOFError
        try:
            valor = int(texto)
            if valor in opciones:
                return valor
        except ValueError:
            pass
        print('Entrada inválida. Opciones: ' + ', '.join(map(str, opciones)))


def estado(p):
    porcentaje = p.hp_actual / p.hp_max
    barra = '#' * int(porcentaje * 20)
    return f'{p.nombre:12} [{barra:<20}] {p.hp_actual}/{p.hp_max} HP ({porcentaje:.0%})'


def reemplazo(jugador):
    print(f'\n{jugador.nombre}: selecciona una reserva viva.')
    for i in jugador.reservas():
        print(f'  {i+1}. {estado(jugador.equipo[i])}')
    return elegir('Reserva: ', [i+1 for i in jugador.reservas()]) - 1


def elegir_accion(jugador):
    p = jugador.pokemon_activo
    print(f'\n{jugador.nombre} — {estado(p)}')
    opcion = elegir('[1] Atacar  [2] Cambiar: ', [1, 2] if jugador.reservas() else [1])
    if opcion == 2:
        return Accion('cambiar', reemplazo(jugador))
    disponibles = [i+1 for i, m in enumerate(p.movimientos) if m.es_valido()]
    if not disponibles:
        print('Sin PP: se usará Forcejeo (con retroceso).')
        return Accion('forcejeo')
    for i, m in enumerate(p.movimientos, 1):
        print(f'  {i}. {m.nombre} | {m.tipo} / {m.categoria} | potencia {m.potencia}'
              f' | precisión {m.precision}% | PP {m.pp_actual}/{m.pp_max}')
    return Accion('atacar', elegir('Movimiento: ', disponibles) - 1)


def iniciar_combate(batalla, privado=False):
    while batalla.verificar_ganador() is None:
        print(f'\n========== TURNO {batalla.turno_actual} ==========')
        for j in batalla.jugadores:
            print(f'{j.nombre}: {estado(j.pokemon_activo)}')
        acciones = []
        for j in batalla.jugadores:
            acciones.append(elegir_accion(j))
            if privado:
                print('\n' * 60)
        for evento in batalla.procesar_turno(*acciones):
            print(evento)
    ganador = batalla.verificar_ganador()
    print('\n¡Empate!' if ganador == 'Empate' else f'\n¡Ganó {ganador}!')


def main():
    parser = argparse.ArgumentParser(description='Batallas Pokémon 3 contra 3. Escribe q para salir.')
    parser.add_argument('--semilla', type=int, help='Semilla para reproducir el azar')
    parser.add_argument('--privado', action='store_true', help='Separar comandos con líneas vacías')
    args = parser.parse_args()
    try:
        catalogo = Catalogo()
        print('SIMULADOR POKÉMON — 3 VS 3\nEscribe q para salir en cualquier selección.')
        for id, p in catalogo.pokemones.items():
            print(f"{id:2}. {p['nombre']:12} {' / '.join(t for t in (p['tipo_1'], p['tipo_2']) if t)}")
        jugadores = []
        for numero in (1, 2):
            nombre = input(f'\nNombre del jugador {numero}: ').strip() or f'Jugador {numero}'
            equipo = []
            for puesto in range(3):
                opciones = [id for id in catalogo.pokemones if id not in equipo]
                equipo.append(elegir(f'{nombre}, Pokémon {puesto+1}/3 (ID): ', opciones))
            jugadores.append(Entrenador(nombre, [catalogo.crear(id) for id in equipo]))
        batalla = Batalla(*jugadores, rng=random.Random(args.semilla), elegir_reemplazo=reemplazo)
        iniciar_combate(batalla, args.privado)
    except (EOFError, KeyboardInterrupt):
        print('\nPartida terminada por el usuario.')
