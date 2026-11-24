import random
import unittest
from unittest.mock import Mock
from pokemon.datos import Catalogo
from pokemon.modelos import Accion, Entrenador
from pokemon.batalla import Batalla
from pokemon.tipos import TIPOS, TABLA, efectividad


def resolver_turno(batalla, accion1, accion2):
    """Automatiza las reservas solo en pruebas; la web las pide al jugador."""
    pasos = batalla.procesar_turno(accion1, accion2)
    try:
        jugador = next(pasos)
        while True:
            jugador = pasos.send(jugador.reservas()[0])
    except StopIteration:
        return list(batalla.eventos)


class PruebasBatalla(unittest.TestCase):
    def setUp(self):
        self.c = Catalogo()
        self.j1 = Entrenador('Uno', [self.c.crear(i) for i in (1, 3, 6)])
        self.j2 = Entrenador('Dos', [self.c.crear(i) for i in (2, 4, 7)])
        self.b = Batalla(self.j1, self.j2, random.Random(42))

    def test_caso_1_velocidad_stab_doble_tipo(self):
        a, d = self.j1.pokemon_activo, self.j2.pokemon_activo
        self.assertEqual(self.b.resolver_prioridad(Accion('atacar'), Accion('atacar')), [0, 1])
        self.assertEqual(self.b.calcular_daño(a, a.movimientos[0], d), 270)

    def test_caso_2_inmunidad_fisica(self):
        a, d = self.c.crear(5), self.c.crear(3)
        self.assertEqual(a.movimientos[1].estadisticas(a, d), (110, 78))
        self.assertEqual(self.b.calcular_daño(a, a.movimientos[1], d), 0)

    def test_caso_3_critico_resistencia(self):
        a, d = self.c.crear(3), self.c.crear(4)
        self.assertEqual(self.b.calcular_daño(a, a.movimientos[0], d, True), 56)

    def test_caso_4_cambio_fallo_consume_pp(self):
        self.j2.cambiar_pokemon(2)
        m = self.j2.pokemon_activo.movimientos[0]
        self.b.rng = Mock()
        self.b.rng.uniform.return_value = 80
        eventos = resolver_turno(self.b, Accion('cambiar', 2), Accion('atacar'))
        self.assertIn('cambia a Gengar', eventos[0])
        self.assertTrue(any('fallado' in e for e in eventos))
        self.assertEqual(m.pp_actual, m.pp_max - 1)
        self.assertEqual(self.j1.pokemon_activo.hp_actual, self.j1.pokemon_activo.hp_max)

    def test_reemplazo_inmediato_no_hereda_accion(self):
        reserva = self.j2.equipo[1]
        resolver_turno(self.b, Accion('atacar'), Accion('atacar'))
        self.assertIs(self.j2.pokemon_activo, reserva)
        self.assertEqual(reserva.movimientos[0].pp_actual, reserva.movimientos[0].pp_max)
        self.assertEqual(self.j1.pokemon_activo.hp_actual, self.j1.pokemon_activo.hp_max)

    def test_ataque_al_objetivo_que_entro(self):
        resolver_turno(self.b, Accion('atacar'), Accion('cambiar', 1))
        self.assertEqual(self.j2.equipo[0].hp_actual, self.j2.equipo[0].hp_max)
        self.assertLess(self.j2.equipo[1].hp_actual, self.j2.equipo[1].hp_max)

    def test_empate_velocidad_ambos_resultados(self):
        self.j2.pokemon_activo.velocidad = self.j1.pokemon_activo.velocidad
        for valor, esperado in ((.49, [0, 1]), (.5, [1, 0])):
            self.b.rng = Mock()
            self.b.rng.random.return_value = valor
            self.assertEqual(self.b.resolver_prioridad(Accion('atacar'), Accion('atacar')), esperado)

    def test_catalogo_matriz_e_independencia(self):
        self.assertEqual(len(TABLA), 18)
        self.assertTrue(all(set(fila) == set(TIPOS) for fila in TABLA.values()))
        self.assertEqual(efectividad('Planta', ('Fuego', 'Volador')), .25)
        otro = self.c.crear(1)
        otro.movimientos[0].consumir_pp()
        self.assertEqual(self.j1.pokemon_activo.movimientos[0].pp_actual, 15)

    def test_accion_invalida_no_modifica_turno(self):
        with self.assertRaises(ValueError):
            resolver_turno(self.b, Accion('atacar'), Accion('cambiar', 0))
        self.assertEqual(self.j1.pokemon_activo.movimientos[0].pp_actual, 15)
        self.assertEqual(self.b.turno_actual, 1)

    def test_sin_pp_y_empate_por_retroceso(self):
        for j in self.b.jugadores:
            for p in j.equipo[1:]:
                p.recibir_daño(p.hp_max)
            p = j.pokemon_activo
            p.recibir_daño(p.hp_max - 1)
            for m in p.movimientos:
                while m.es_valido():
                    m.consumir_pp()
        resolver_turno(self.b, Accion('forcejeo'), Accion('forcejeo'))
        self.assertEqual(self.b.verificar_ganador(), 'Empate')

    def test_partida_completa(self):
        for _ in range(500):
            if self.b.verificar_ganador() is not None:
                break
            acciones = []
            for j in self.b.jugadores:
                indices = [i for i, m in enumerate(j.pokemon_activo.movimientos) if m.es_valido()]
                acciones.append(Accion('atacar', indices[0]) if indices else Accion('forcejeo'))
            resolver_turno(self.b, *acciones)
        self.assertIsNotNone(self.b.verificar_ganador())

    def test_dos_cambios_respetan_velocidad_y_no_consumen_pp(self):
        eventos = resolver_turno(self.b, Accion('cambiar', 1), Accion('cambiar', 2))
        self.assertIn('Uno cambia a Charizard', eventos[0])
        self.assertIn('Dos cambia a Machamp', eventos[1])
        for j in self.b.jugadores:
            for p in j.equipo:
                self.assertTrue(all(m.pp_actual == m.pp_max for m in p.movimientos))

    def test_limite_critico_y_dispersion(self):
        for sorteo, esperado in ((.0625, 56), (.0625001, 37)):
            with self.subTest(sorteo=sorteo):
                a, d = self.c.crear(3), self.c.crear(4)
                self.b.rng = Mock()
                self.b.rng.random.return_value = sorteo
                self.b.rng.uniform.side_effect = [100, 1]
                self.b.ejecutar_ataque(a, a.movimientos[0], d)
                self.assertEqual(d.hp_max - d.hp_actual, esperado)
                self.assertEqual(self.b.rng.uniform.call_args_list[0].args, (1, 100))
                self.assertEqual(self.b.rng.uniform.call_args_list[1].args, (.85, 1))

    def test_limite_precision(self):
        for sorteo, acierta in ((50, True), (50.001, False)):
            with self.subTest(sorteo=sorteo):
                a, d = self.c.crear(7), self.c.crear(5)
                self.b.rng = Mock()
                self.b.rng.uniform.side_effect = [sorteo, 1]
                self.b.rng.random.return_value = 1
                self.b.ejecutar_ataque(a, a.movimientos[0], d)
                self.assertEqual(d.hp_actual < d.hp_max, acierta)
                self.assertEqual(a.movimientos[0].pp_actual, 4)
                self.assertEqual(self.b.rng.random.call_count, int(acierta))

    def test_inmunidad_en_ataque_real_consume_pp(self):
        a, d = self.c.crear(5), self.c.crear(3)
        self.b.ejecutar_ataque(a, a.movimientos[1], d)
        self.assertEqual(d.hp_actual, d.hp_max)
        self.assertEqual(a.movimientos[1].pp_actual, 9)
        self.assertIn('No afecta a Charizard...', self.b.eventos)

    def test_sin_pp_no_permite_atacar(self):
        m = self.j1.pokemon_activo.movimientos[0]
        while m.es_valido():
            m.consumir_pp()
        with self.assertRaises(ValueError):
            resolver_turno(self.b, Accion('atacar'), Accion('atacar'))
        self.assertEqual(self.b.turno_actual, 1)


if __name__ == '__main__':
    unittest.main()
