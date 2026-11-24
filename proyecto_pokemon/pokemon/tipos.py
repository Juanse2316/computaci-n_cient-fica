"""Matriz completa: las interacciones omitidas son neutrales."""
TIPOS = ('Normal', 'Fuego', 'Agua', 'Eléctrico', 'Planta', 'Hielo', 'Lucha',
         'Veneno', 'Tierra', 'Volador', 'Psíquico', 'Bicho', 'Roca',
         'Fantasma', 'Dragón', 'Siniestro', 'Acero', 'Hada')
# Por fila: vulnerables, resistentes, inmunes al tipo atacante.
FILAS = {
    'Normal': ('', 'Roca Acero', 'Fantasma'),
    'Fuego': ('Planta Hielo Bicho Acero', 'Fuego Agua Roca Dragón', ''),
    'Agua': ('Fuego Tierra Roca', 'Agua Planta Dragón', ''),
    'Eléctrico': ('Agua Volador', 'Eléctrico Planta Dragón', 'Tierra'),
    'Planta': ('Agua Tierra Roca', 'Fuego Planta Veneno Volador Bicho Dragón Acero', ''),
    'Hielo': ('Planta Tierra Volador Dragón', 'Fuego Agua Hielo Acero', ''),
    'Lucha': ('Normal Hielo Roca Siniestro Acero', 'Veneno Volador Psíquico Bicho Hada', 'Fantasma'),
    'Veneno': ('Planta Hada', 'Veneno Tierra Roca Fantasma', 'Acero'),
    'Tierra': ('Fuego Eléctrico Veneno Roca Acero', 'Planta Bicho', 'Volador'),
    'Volador': ('Planta Lucha Bicho', 'Eléctrico Roca Acero', ''),
    'Psíquico': ('Lucha Veneno', 'Psíquico Acero', 'Siniestro'),
    'Bicho': ('Planta Psíquico Siniestro', 'Fuego Lucha Veneno Volador Fantasma Acero Hada', ''),
    'Roca': ('Fuego Hielo Volador Bicho', 'Lucha Tierra Acero', ''),
    'Fantasma': ('Psíquico Fantasma', 'Siniestro', 'Normal'),
    'Dragón': ('Dragón', 'Acero', 'Hada'),
    'Siniestro': ('Psíquico Fantasma', 'Lucha Siniestro Hada', ''),
    'Acero': ('Hielo Roca Hada', 'Fuego Agua Eléctrico Acero', ''),
    'Hada': ('Lucha Dragón Siniestro', 'Fuego Veneno Acero', ''),
}
TABLA = {ataque: {defensa: next((valor for grupo, valor in zip(FILAS[ataque], (2, .5, 0))
                                      if defensa in grupo.split()), 1)
                  for defensa in TIPOS} for ataque in TIPOS}


def efectividad(tipo, tipos_objetivo):
    resultado = 1
    for defensa in tipos_objetivo:
        resultado *= TABLA[tipo][defensa]
    return resultado
