"""Descarga y conserva localmente el arte oficial referenciado por PokéAPI."""
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError

BASE = Path(__file__).resolve().parent


def descargar(url):
    try:
        with urlopen(url, timeout=30) as respuesta:
            return respuesta.read()
    except HTTPError as error:
        if error.code != 403:
            raise
        # Algunos proveedores rechazan el cliente urllib; curl usa su cliente TLS.
        return subprocess.run(['curl', '--fail', '--silent', '--show-error',
                               '--location', '--max-time', '30', url],
                              check=True, capture_output=True).stdout


def main():
    destino = BASE / 'web' / 'imagenes'
    destino.mkdir(parents=True, exist_ok=True)
    manifiesto = destino / 'fuentes.json'
    fuentes = json.loads(manifiesto.read_text(encoding='utf-8')) if manifiesto.exists() else {}
    pokemones = json.loads((BASE / 'datos' / 'pokemones.json').read_text(encoding='utf-8'))
    for pokemon in pokemones:
        nombre = pokemon['nombre'].lower()
        archivo = destino / f'{nombre}.png'
        if archivo.exists() and nombre in fuentes:
            print(f'{nombre}: disponible')
            continue
        api = f'https://pokeapi.co/api/v2/pokemon/{nombre}'
        datos = json.loads(descargar(api))
        imagen = datos['sprites']['other']['official-artwork']['front_default']
        contenido = descargar(imagen)
        if not contenido.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError(f'La imagen de {nombre} no es PNG')
        archivo.write_bytes(contenido)
        fuentes[nombre] = dict(api=api, imagen=imagen, archivo=archivo.name)
        manifiesto.write_text(json.dumps(fuentes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'{nombre}: descargado ({len(contenido)} bytes)', flush=True)


if __name__ == '__main__':
    main()
