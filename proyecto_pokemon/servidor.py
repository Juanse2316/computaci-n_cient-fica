"""Servidor local de la interfaz web, sin dependencias externas."""
import argparse
import json
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from pokemon.datos import Catalogo
from pokemon.modelos import Accion, Entrenador
from pokemon.batalla import Batalla

WEB = Path(__file__).resolve().parent / 'web'


class Partida:
    def __init__(self, equipos, nombres):
        catalogo = Catalogo()
        if len(equipos) != 2 or len(nombres) != 2:
            raise ValueError('Se necesitan dos jugadores')
        jugadores = [Entrenador(str(n)[:30] or f'Jugador {i+1}', [catalogo.crear(id) for id in e])
                     for i, (n, e) in enumerate(zip(nombres, equipos))]
        self.batalla = Batalla(*jugadores)
        self.acciones = []
        self.pasos = None
        self.reemplazo = None

    def avanzar(self, indice=None):
        try:
            self.reemplazo = next(self.pasos) if indice is None else self.pasos.send(indice)
        except StopIteration:
            self.pasos = self.reemplazo = None
            self.acciones = []

    def actuar(self, datos):
        if self.batalla.verificar_ganador() is not None:
            raise ValueError('La partida terminó')
        if self.reemplazo is not None:
            indice = datos.get('indice')
            if datos.get('tipo') != 'reemplazar' or type(indice) is not int or indice not in self.reemplazo.reservas():
                raise ValueError('Selecciona una reserva disponible')
            self.avanzar(indice)
        else:
            indice = datos.get('indice', 0)
            if type(indice) is not int:
                raise ValueError('Índice inválido')
            accion = Accion(datos.get('tipo'), indice)
            self.batalla.validar_accion(self.batalla.jugadores[len(self.acciones)], accion)
            self.acciones.append(accion)
            if len(self.acciones) == 2:
                self.pasos = self.batalla.procesar_turno_interactivo(*self.acciones)
                self.avanzar()

    def estado(self):
        b = self.batalla
        jugadores = []
        for j in b.jugadores:
            equipo = []
            for p in j.equipo:
                equipo.append(dict(nombre=p.nombre, tipos=p.tipos, hp=p.hp_actual, max=p.hp_max,
                                   activo=p is j.pokemon_activo,
                                   movimientos=[dict(nombre=m.nombre, tipo=m.tipo, categoria=m.categoria,
                                                      potencia=m.potencia, precision=m.precision,
                                                      pp=m.pp_actual, max=m.pp_max) for m in p.movimientos]))
            jugadores.append(dict(nombre=j.nombre, equipo=equipo))
        return dict(turno=b.turno_actual, jugadores=jugadores, ganador=b.verificar_ganador(),
                    elige=b.jugadores.index(self.reemplazo) if self.reemplazo else len(self.acciones),
                    reemplazo=self.reemplazo is not None, eventos=b.eventos)


class Servidor(BaseHTTPRequestHandler):
    partidas = {}

    def responder(self, codigo, datos, tipo='application/json; charset=utf-8'):
        contenido = json.dumps(datos, ensure_ascii=False).encode() if isinstance(datos, (dict, list)) else datos
        self.send_response(codigo)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(contenido)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(contenido)

    def do_GET(self):
        if self.path == '/api/catalogo':
            return self.responder(200, list(Catalogo().pokemones.values()))
        archivos = {'/': ('index.html', 'text/html'), '/style.css': ('style.css', 'text/css'),
                    '/app.js': ('app.js', 'text/javascript')}
        # Lista explícita: no se aceptan rutas arbitrarias del cliente.
        for p in Catalogo().pokemones.values():
            nombre = p['nombre'].lower() + '.png'
            archivos['/imagenes/' + nombre] = ('imagenes/' + nombre, 'image/png')
        if self.path not in archivos:
            return self.responder(404, {'error': 'Ruta no encontrada'})
        nombre, tipo = archivos[self.path]
        archivo = WEB / nombre
        if not archivo.is_file():
            return self.responder(404, {'error': 'Archivo no disponible'})
        self.responder(200, archivo.read_bytes(), tipo if tipo == 'image/png' else tipo + '; charset=utf-8')

    def do_POST(self):
        try:
            # Solo se aceptan peticiones del navegador en este mismo servidor.
            origen = self.headers.get('Origin')
            if origen and origen != 'http://' + self.headers.get('Host', ''):
                return self.responder(403, {'error': 'Origen no permitido'})
            longitud = int(self.headers.get('Content-Length', '0'))
            if not 0 < longitud <= 10000:
                raise ValueError('Petición inválida')
            datos = json.loads(self.rfile.read(longitud))
            if self.path == '/api/iniciar':
                partida = Partida(datos['equipos'], datos['nombres'])
                anterior = datos.get('sesion')
                self.partidas.pop(anterior, None)
                if len(self.partidas) >= 100:
                    self.partidas.pop(next(iter(self.partidas)))
                sesion = secrets.token_urlsafe(24)
                self.partidas[sesion] = partida
                return self.responder(200, dict(sesion=sesion, estado=partida.estado()))
            if self.path != '/api/accion':
                return self.responder(404, {'error': 'Ruta no encontrada'})
            partida = self.partidas[datos['sesion']]
            partida.batalla.animaciones = []
            partida.actuar(datos)
            self.responder(200, {'estado': partida.estado(), 'animaciones': partida.batalla.animaciones})
        except (ValueError, KeyError, TypeError, IndexError) as error:
            self.responder(400, {'error': 'Datos inválidos o partida no disponible. ' + str(error)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interfaz web local del simulador Pokémon')
    parser.add_argument('--puerto', type=int, default=8000)
    args = parser.parse_args()
    servidor = HTTPServer(('127.0.0.1', args.puerto), Servidor)
    print(f'Abre http://127.0.0.1:{args.puerto} en tu navegador. Ctrl+C para detener.', flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
