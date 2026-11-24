import json
from pathlib import Path
from .modelos import Pokemon, MovimientoFisico, MovimientoEspecial
from .tipos import TIPOS


class Catalogo:
    def __init__(self, directorio=None):
        ruta = Path(directorio) if directorio else Path(__file__).resolve().parent.parent / 'datos'
        registros = json.loads((ruta / 'pokemones.json').read_text(encoding='utf-8'))
        movimientos = json.loads((ruta / 'movimientos.json').read_text(encoding='utf-8'))
        self.pokemones = {p['id']: p for p in registros}
        self.movimientos = {m['id']: m for m in movimientos}
        if len(self.pokemones) != len(registros) or len(self.movimientos) != len(movimientos):
            raise ValueError('IDs duplicados en los datos')
        cobertura = {t for p in registros for t in (p['tipo_1'], p['tipo_2']) if t}
        if len(registros) < 20 or cobertura != set(TIPOS):
            raise ValueError('Se requieren 20 Pokémon y cobertura de los 18 tipos')
        for id in self.pokemones:
            self.crear(id)

    def crear(self, id):
        registro = dict(self.pokemones[id])
        instancias = []
        for mid in registro['movimientos']:
            datos = dict(self.movimientos[mid])
            datos.pop('id')
            categoria = datos.pop('categoria')
            clase = {'Físico': MovimientoFisico, 'Especial': MovimientoEspecial}[categoria]
            instancias.append(clase(**datos))
        registro['movimientos'] = instancias
        return Pokemon(**registro)
