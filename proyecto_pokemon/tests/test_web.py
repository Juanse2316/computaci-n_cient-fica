import unittest
from servidor import Partida


class PruebasWeb(unittest.TestCase):
    def test_animaciones_conservan_dano_antes_del_reemplazo(self):
        p = Partida([[1, 3, 6], [2, 4, 7]], ['Ana', 'Luis'])
        p.actuar({'tipo': 'atacar', 'indice': 0})
        p.actuar({'tipo': 'atacar', 'indice': 0})
        golpe = p.batalla.animaciones[0]
        self.assertEqual(golpe['actor'], 0)
        self.assertEqual(golpe['activos'][1], {'nombre': 'Gyarados', 'hp': 0})
        p.actuar({'tipo': 'reemplazar', 'indice': 1})
        self.assertEqual(p.batalla.animaciones[-1]['tipo'], 'cambiar')
        self.assertEqual(p.batalla.animaciones[-1]['activos'][1]['nombre'], 'Blastoise')
        self.assertEqual(golpe['activos'][1]['nombre'], 'Gyarados')

    def test_comandos_reemplazo_y_continuacion(self):
        p = Partida([[1, 3, 6], [2, 4, 7]], ['Ana', 'Luis'])
        p.actuar({'tipo': 'atacar', 'indice': 0})
        self.assertEqual(p.estado()['elige'], 1)
        p.actuar({'tipo': 'atacar', 'indice': 0})
        self.assertTrue(p.estado()['reemplazo'])
        self.assertEqual(p.estado()['elige'], 1)
        with self.assertRaises(ValueError):
            p.actuar({'tipo': 'reemplazar', 'indice': 0})
        p.actuar({'tipo': 'reemplazar', 'indice': 1})
        self.assertFalse(p.estado()['reemplazo'])
        self.assertEqual(p.estado()['turno'], 2)
        self.assertEqual(p.batalla.jugadores[1].pokemon_activo.nombre, 'Blastoise')
        self.assertEqual(p.batalla.jugadores[0].pokemon_activo.hp_actual, 140)

    def test_partida_completa_web(self):
        p = Partida([[1, 3, 6], [2, 4, 7]], ['Ana', 'Luis'])
        for _ in range(1000):
            estado = p.estado()
            if estado['ganador'] is not None:
                break
            jugador = p.batalla.jugadores[estado['elige']]
            if estado['reemplazo']:
                p.actuar({'tipo': 'reemplazar', 'indice': jugador.reservas()[0]})
            else:
                indices = [i for i, m in enumerate(jugador.pokemon_activo.movimientos) if m.es_valido()]
                p.actuar({'tipo': 'atacar', 'indice': indices[0]} if indices else {'tipo': 'forcejeo'})
        self.assertIsNotNone(p.estado()['ganador'])

    def test_equipos_invalidos(self):
        with self.assertRaises(ValueError):
            Partida([[1, 1, 3], [2, 4, 7]], ['Ana', 'Luis'])


if __name__ == '__main__':
    unittest.main()
