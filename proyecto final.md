PROYECTO FINAL - SIMULADOR DE BATALLAS POKEMON

Maestría en Inteligencia Artificial, Universidad Sergio Arboleda
Asignatura: Computacion Cientifica 2
Docente: Guillermo Andres De Mendoza Corrales
Fecha de entrega: Noviembre 24 de 2026
_______________________________________________________

1. Objetivos

El proyecto consiste en desarrollar un simulador de batallas Pokémon de 3 contra 3 por turnos para dos jugadores (Jugador 1
vs  Jugador  2)  compartiendo  la  misma  terminal.  El  programa  solicitará  secuencialmente  las  acciones  de  cada  jugador,
calculará  las  prioridades  según  el  modelo  físico/mecanico  del  juego  y  procesará  las  fórmulas  matemáticas  oficiales  para
determinar el resultado del turno.
Programación Orientada a Objetos (POO): Aplicar abstracción, encapsulamiento, herencia y polimorfismo para modelar las
entidades del juego.

Modelado de sistemas y estados: Gestionar correctamente la máquina de estados de un combate por turnos (cambios de
estado de salud, turnos, prioridad de acciones).

Computación Estocástica: Implementar modelos de probabilidad para determinar precisión, golpes críticos y dispersión de
daño en cada acción.

2. Descripcion

¿Qué es un Pokémon?
En el contexto de la simulación, un Pokémon es una entidad de combate definida por un conjunto de atributos numéricos
(estadísticas)  y  un  perfil elemental (tipos). Cada Pokémon posee un estado de salud (
) y cinco estadísticas principales (
𝐴𝑡𝑘 𝐷𝑒𝑓 𝑆𝑝. 𝐴𝑡𝑘 𝑆𝑝. 𝐷𝑒𝑓 𝑆𝑝𝑒𝑒𝑑
). Su desempeño en batalla depende directamente de la relación entre su tipo elemental
,
y el tipo de los movimientos que ejecuta o recibe.

𝐻𝑃

,

,

,

Pueden buscar cada pokemon y sus estadísticas en el siguiewnte link: https://pokemondb.net/pokedex/dragonite

Las estadísticas de un pokémon se encuentran entre el valor mínimo y máximo. Para efectos de este proyecto podrán tomar
cualquier valor.

Movimientos

Ejemplo de un movimiento: https://pokemondb.net/move/earthquake

Mecánica de Tipos y Efectividad

Cada  Pokémon  y  cada  movimiento  pertenecen  a  uno  o  dos  tipos  elementales.  La  interacción  entre  tipos  determina  un
multiplicador de daño (

) en la fórmula de combate:

𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑

× 2. 0 × 4. 0
 o

): El ataque inflige el doble de daño (o cuádruple si el objetivo tiene doble tipo

●  Súper Efectivo (
vulnerable).
●  Daño Normal (
●  Poco Efectivo (
●  Inmune (
× 0. 0

× 1. 0

): El ataque inflige el daño estándar.

× 0. 5 × 0. 25
 o
): El ataque no inflige daño.

): El ataque inflige la mitad de daño (o la cuarta parte).

3. Requerimientos para el pool de pokemones

Para garantizar la variedad estratégica y la correcta prueba de la matriz de tipos en el proyecto, el sistema debe tener
configurados un pool mínimo de 20 Pokémon predefinidos.

3.1 Cobertura Total de Tipos: Entre los 20 Pokémon del archivo, deben estar representados los 18 tipos
oficiales de la franquicia (Fuego, Agua, Planta, Eléctrico, Hielo, Lucha, Veneno, Tierra, Volador, Psíquico, Bicho,
Roca, Fantasma, Dragón, Acero, Siniestro, Hada y Normal).

3.2Atributos Completos: Cada registro en el archivo de datos debe incluir obligatoriamente:

id: Identificador único.

○
○  nombre: Nombre del Pokémon.
○
○  estadisticas: Objetos o valores numéricos para
○  movimientos: Lista con los IDs o nombres de 4 movimientos asignados.

tipo_1 y tipo_2: Cadena de texto (ej. "Fuego", "Volador" o null si es monotipo).
 y

,

,

,

,

𝐻𝑃 𝐴𝑡𝑘 𝐷𝑒𝑓 𝑆𝑝. 𝐴𝑡𝑘 𝑆𝑝. 𝐷𝑒𝑓 𝑆𝑝𝑒𝑒𝑑

.

4. Clases propuestas

Clase Movimiento:

●  Atributos: nombre, tipo, categoria (Físico o Especial), potencia, precision (0-100), pp_max,

pp_actual.

●  Métodos: consumir_pp(), es_valido().

Clase Pokemon:

●  Atributos: nombre, tipo_1, tipo_2 (opcional), hp_max, hp_actual, ataque, defensa, at_especial,

def_especial, velocidad, movimientos (lista/array de hasta 4 instancias de Movimiento).

●  Métodos: recibir_daño(cantidad), esta_debilitado(), atacar(movimiento, objetivo),

obtener_estadistica().

Clase Entrenador (o Jugador):

●  Atributos: nombre, equipo (lista de 3 Pokemon), pokemon_activo.
●  Métodos: elegir_accion(), cambiar_pokemon(nuevo_indice),

tiene_pokemon_disponibles().

Clase Batalla (Motor principal):

●  Atributos: jugador1, jugador2, turno_actual.
●  Métodos: iniciar_combate(), procesar_turno(accion_p1, accion_p2),

resolver_prioridad(), calcular_daño(), verificar_ganador().

5. Mecanica de combate por turnos

Fase de Comandos:
En la terminal, se presentan las opciones al Jugador 1 (ocultando o limpiando pantalla opcionalmente para
mantener privacidad) y luego al Jugador 2.

●  Opciones por turno: [1] Atacar (seleccionar movimiento) o [2] Cambiar Pokémon (seleccionar reserva

vivo).

Prioridad de Ejecución:

●  El cambio de Pokémon tiene prioridad absoluta sobre cualquier ataque.
●  Si ambos eligen cambiar, se ejecutan en orden aleatorio o según la velocidad de sus Pokémon activos.
●  Si ambos eligen atacar, ataca primero el Pokémon con mayor estadística de velocidad. En caso de

empate, la prioridad se decide mediante un sorteo aleatorio de probabilidad

𝑝 = 0. 5

.

Cálculo Numérico del Daño:

(Asumir Nivel = 50 para todos los Pokémon).

●  Reglas para Ataque / Defensa:

○  Si el movimiento es Físico, se usa Ataque del atacante y Defensa del objetivo.
○  Si el movimiento es Especial, se usa At_Especial del atacante y Def_Especial del objetivo.

●  Modificador:

𝑀𝑜𝑑𝑖𝑓𝑖𝑐𝑎𝑑𝑜𝑟 = 𝑆𝑇𝐴𝐵 × 𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑 × 𝐶𝑟í𝑡𝑖𝑐𝑜 × 𝐴𝑙𝑒𝑎𝑡𝑜𝑟𝑖𝑜

●  STAB (Same Type Attack Bonus):
 si no.

atacante;

1. 0

1. 5

 si el tipo del movimiento coincide con algún tipo del Pokémon

●  Efectividad: Multiplicador obtenido de la tabla de tipos (
 si ocurre un golpe crítico;
●  Crítico:
●  Aleatorio: Valor continuo uniformemente distribuido

,
 en caso contrario.

1. 0

1. 5

𝑈(0. 85, 1. 00)

.

0. 0 0. 5 1. 0 2. 0 4. 0

,

,

,

).

Cuando un Pokémon tiene dos tipos (por ejemplo, Gyarados, que es de tipo Agua / Volador), la efectividad total
del ataque se calcula multiplicando individualmente la efectividad del tipo del ataque contra cada uno de los
dos tipos del Pokémon defensor.

La fórmula es:

𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑𝑇𝑜𝑡𝑎𝑙 = 𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑(𝑇𝑖𝑝𝑜𝐴𝑡𝑎𝑞𝑢𝑒 → 𝑇𝑖𝑝𝑜1) × 𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑(𝑇𝑖𝑝𝑜𝐴𝑡𝑎𝑞𝑢𝑒 → 𝑇𝑖𝑝𝑜2)

Simulación Estocástica

.
●  Precisión: Un ataque acierta solo si un valor aleatorio
●  Probabilidad de Crítico: Cada ataque exitoso tiene un $6.25\%$ de probabilidad (

𝑟 ∼ 𝑈(1, 100) ≤ 𝑃𝑟𝑒𝑐𝑖𝑠𝑖ó𝑛

1/16

) de asestar un

golpe crítico.

Interfaz en Terminal (CLI)

●  Presentación clara del estado actual al inicio de cada turno:

○  Nombres de los Pokémon activos y sus barras/porcentajes de HP actual vs. HP máximo.
○  Puntos de Poder (PP) restantes para cada movimiento al seleccionar un ataque.

Reglas adicionales

Cuando un Pokémon cae a
inmediatamente antes de continuar

0𝐻𝑃

: El jugador que perdió al Pokémon debe seleccionar un reemplazo

6. Ejemplos de interacciones (Casos de prueba)

Caso 1: Validación de Prioridad por Velocidad y Ventaja de Tipo Básica

●  Propósito: Validar que el Pokémon más rápido ataca primero y que el modificador de tipo súper efectivo (

× 2. 0

× 1. 5
●  Atacante: Jolteon (Eléctrico) — Velocidad: 130

) se aplique correctamente.

) con STAB (

1.  Ataque usado: Rayo (Especial, Tipo: Eléctrico, Potencia: 90, Precisión: 100%)
2.  Estadística

𝑆𝑝. 𝐴𝑡𝑘

: 110

●  Defensor: Gyarados (Agua / Volador) — Velocidad: 81

1.  Estadística

𝑆𝑝. 𝐷𝑒𝑓

: 100

●  Cálculo Esperado:

1.  Orden: Jolteon actúa primero por tener mayor velocidad (
2.  Categoría: Especial
 de Jolteon (110) y
𝑆𝑝. 𝐴𝑡𝑘
 (Rayo es Eléctrico y Jolteon es Eléctrico).
3.  STAB:
1. 5
4.  Efectividad: Eléctrico es súper efectivo contra Agua (

 Usa

→

130 > 81

).

𝑆𝑝. 𝐷𝑒𝑓

 de Gyarados (100).

× 2. 0

) y Volador (

× 2. 0 →

)

 Multiplicador

total de tipo
5.  Daño final:

= 4. 0

.

𝐷𝑎ñ𝑜𝐵𝑎𝑠𝑒 =

22×90× 110
100

50

(

+ 2

) = 2178
(

50 + 2

) = 45. 56 → 45

6.

𝐷𝑎ñ𝑜𝑇𝑜𝑡𝑎𝑙 = 45 × 1. 5(𝑆𝑇𝐴𝐵) × 4. 0(𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑) = 270 𝑝𝑢𝑛𝑡𝑜𝑠𝑑𝑒𝑑𝑎ñ𝑜.

Caso 2: Validación de Ataque Físico vs Especial e Inmunidad

●  Propósito: Comprobar la diferencia entre estadísticas físicas/especiales y el manejo estricto del

multiplicador de inmunidad (

× 0. 0

).

●  Atacante: Snorlax (Normal) — Velocidad: 30

1.  Ataque usado: Terremoto (Físico, Tipo: Tierra, Potencia: 100, Precisión: 100%)
2.  Estadística

: 110

𝐴𝑡𝑘

●  Defensor: Charizard (Fuego / Volador) — Velocidad: 100

1.  Estadística

𝐷𝑒𝑓

: 78

●  Cálculo Esperado:

1.  Orden: Charizard actúa primero por velocidad (
2.  Efectividad: Los ataques de tipo Tierra no afectan a los tipos Volador (
3.  Daño final:   puntos de daño (Mensaje en consola: "No afecta a Charizard...").

100 > 30

).

0

𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑 = 0. 0

).

Caso 3: Validación de Golpe Crítico y Resistencia (Poco Efectivo)

●  Propósito: Verificar el cálculo cuando ocurre un golpe crítico (probabilidad del $6.25\%$, multiplicador

× 1. 5

) combinado con resistencia tipo (
●  Atacante: Charizard (Fuego / Volador)

× 0. 5

).

1.  Ataque usado: Lanzallamas (Especial, Tipo: Fuego, Potencia: 90, Precisión: 100%)
2.  Estadística
●  Defensor: Blastoise (Agua)

𝑆𝑝. 𝐴𝑡𝑘

: 129

1.  Estadística

𝑆𝑝. 𝐷𝑒𝑓

: 105

1. 5

●  Cálculo Esperado:
1.  STAB:
2.  Efectividad: Fuego es poco efectivo contra Agua (
3.  Crítico: Si el motor genera
4.  Daño final:

 (Lanzallamas es Fuego y Charizard es Fuego).
).
, se aplica multiplicador por Crítico

𝑟 ≤ 0. 0625

× 0. 5

= 1. 5

.

𝐷𝑎ñ𝑜𝐵𝑎𝑠𝑒 =

22×90× 129
105

50

(

+ 2

) = 2432.57
(

50 + 2

) = 50. 65 → 50

𝐷𝑎ñ𝑜𝑇𝑜𝑡𝑎𝑙 = 50 × 1. 5(𝑆𝑇𝐴𝐵) × 0. 5(𝐸𝑓𝑒𝑐𝑡𝑖𝑣𝑖𝑑𝑎𝑑) × 1. 5(𝐶𝑟í𝑡𝑖𝑐𝑜) = 56. 25 → 56𝑝𝑢𝑛𝑡𝑜𝑠.

Caso 4: Validación de Prioridad por Cambio de Pokémon y Fallo por Precisión

●  Propósito: Confirmar que la acción "Cambiar Pokémon" interrumpe el orden por velocidad y validar el

fallo de un movimiento por precisión.

●  Jugador 1: Elige la acción Cambiar Pokémon (cambia a Gengar).
●  Jugador 2: Elige la acción Atacar con Machamp usando Puño Dinámico (Físico, Tipo: Lucha, Potencia:

100, Precisión: 50%).

●  Cálculo Esperado:

1.  Prioridad: El cambio de Pokémon del Jugador 1 se procesa antes de que el Jugador 2 ejecute su

ataque, sin importar las velocidades.

2.  Verificación de Precisión: El sistema genera un número aleatorio

𝑟 ∼ 𝑈(1, 100)

.

■  Si
𝑟 > 50
■  No se deduce
fallado!".

, el ataque falla automáticamente.

𝐻𝑃

 del objetivo y se muestra el mensaje: "¡El ataque de Machamp ha

3.  Consumo de PP: Los Puntos de Poder (
1 unidad aunque el ataque haya fallado.

𝑃𝑃

) del movimiento Puño Dinámico deben reducirse en

7. Criterio de evaluación

Criterio

Descripcion

Diseño y
Estructura POO

Correcto modelado de clases, responsabilidades bien
delimitadas, encapsulamiento y UML.

Valor

35%

Lógica de
Combate y
Reglas

Modelo
Matemático y
Estocástico

Interfaz CLI

Correcta implementación de prioridades de velocidad,
cambios de Pokémon, debilidad/resistencia y flujo de turnos

30%

Precisión en la fórmula de daño, cálculo de STAB, generación
de aleatorios para precisión/críticos.

25%

Manejo de errores de entrada del usuario, flujo amigable.
Pueden hacer esta capa apoyándose con IA

10%

