import unittest
import io
import json
from unittest.mock import Mock
from servidor import Partida, Servidor


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

    def test_formato_equipos_y_nombres(self):
        for equipos in (None, {}, [[True, 3, 6], [2, 4, 7]], [[999, 3, 6], [2, 4, 7]],
                        [[1, 3], [2, 4, 7]]):
            with self.subTest(equipos=equipos), self.assertRaises(ValueError):
                Partida(equipos, ['Ana', 'Luis'])
        with self.assertRaises(ValueError):
            Partida([[1, 3, 6], [2, 4, 7]], [None, 'Luis'])

    def test_accion_invalida_conserva_comando_del_otro_jugador(self):
        p = Partida([[1, 3, 6], [2, 4, 7]], ['Ana', 'Luis'])
        p.actuar({'tipo': 'atacar', 'indice': 0})
        for datos in (None, [], {'tipo': 'atacar', 'indice': True}, {'tipo': 'cambiar', 'indice': 0}):
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                p.actuar(datos)
            self.assertEqual(p.estado()['elige'], 1)
            self.assertEqual(p.estado()['turno'], 1)
        p.actuar({'tipo': 'atacar', 'indice': 0})
        self.assertTrue(p.estado()['reemplazo'])

    def test_http_json_no_objeto_devuelve_400(self):
        for datos in (None, [], 'texto', 42):
            contenido = json.dumps(datos).encode()
            handler = object.__new__(Servidor)
            handler.headers = {'Content-Length': str(len(contenido))}
            handler.path = '/api/iniciar'
            handler.rfile = io.BytesIO(contenido)
            handler.responder = Mock()
            handler.do_POST()
            self.assertEqual(handler.responder.call_args.args[0], 400)


if __name__ == '__main__':
    unittest.main()
