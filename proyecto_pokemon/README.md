# Simulador de batallas Pokémon

Proyecto de Computación Científica 2: dos jugadores comparten una terminal y combaten con equipos de tres Pokémon. Implementación en Python 3.10 o posterior, sin dependencias externas.

## Ejecutar

### Interfaz gráfica web (HTML y CSS)

```powershell
python servidor.py
```

Abre **http://127.0.0.1:8000** en tu navegador. Selecciona tres Pokémon por jugador y confirma cada equipo. La pantalla de batalla muestra vida, PP, ataques, reservas y el registro del turno. Los dos jugadores eligen sus acciones secuencialmente en el mismo navegador. Si un Pokémon cae, la web solicita un reemplazo antes de continuar.

La interfaz está en `web/index.html`, `web/style.css` y `web/app.js`. JavaScript conecta los botones con `servidor.py`; todas las reglas se ejecutan en el mismo motor Python de la terminal. No necesita instalar paquetes ni conexión a internet. El servidor solo escucha en el equipo local; las partidas se guardan en memoria. Recargar la página inicia una nueva selección. Para otro puerto usa `python servidor.py --puerto 8080`. Detén el servidor con Ctrl+C.

### Interfaz de terminal

Las ilustraciones de los 20 Pokémon se obtienen de `sprites.other.official-artwork.front_default` de [PokéAPI](https://pokeapi.co/docs/v2#pokemon) y se guardan en `web/imagenes/`. Aparecen en el catálogo, los equipos seleccionados, el campo de batalla y las reservas. El archivo `fuentes.json` registra la URL original de cada imagen. Para recuperar imágenes faltantes ejecuta `python descargar_imagenes.py` con internet; las imágenes ya descargadas se reutilizan. El juego funciona sin conexión una vez descargadas. Pokémon y sus ilustraciones pertenecen a sus respectivos titulares; se usan aquí como material de un proyecto académico.

Desde PowerShell, en esta carpeta:

```powershell
python main.py
python main.py --semilla 42 --privado
```

Selecciona tres IDs diferentes por jugador; el primer Pokémon queda activo. Ambos jugadores pueden escoger la misma especie, pero sus HP y PP son independientes. Cada turno permite atacar o cambiar a una reserva viva. Escribe `q` en cualquier selección numérica o pulsa Ctrl+C para salir. `--privado` separa las elecciones con líneas vacías; el historial de la terminal sigue siendo accesible.

## Organización y POO

- `pokemon/modelos.py`: abstracción `Movimiento`, herencia física/especial y selección polimórfica de estadísticas; `Pokemon`, `Entrenador` y acciones. HP y PP se modifican mediante métodos y se consultan mediante propiedades.
- `pokemon/batalla.py`: prioridad, azar, daño, reemplazos y victoria. El generador aleatorio y la selección de reemplazo son inyectables para probar el motor sin terminal.
- `pokemon/tipos.py`: matriz completa de 18 × 18 y multiplicación para defensores de doble tipo.
- `pokemon/datos.py` y `datos/*.json`: carga validada de 20 Pokémon y 22 movimientos, con instancias independientes en cada equipo.
- `pokemon/cli.py`: entradas, selección de equipos, barras de HP y PP disponibles.
- `tests/test_batalla.py`: ejemplos del enunciado y casos de integración.
- `docs/uml.md`: diagrama de clases.

## Modelo matemático

Todos combaten a nivel 50. Para ataques físicos se usa ataque/defensa; para especiales, ataque especial/defensa especial.

```text
base = floor((((2 × 50 / 5 + 2) × potencia × ataque / defensa) / 50) + 2)
daño = floor(base × STAB × efectividad × crítico × aleatorio)
```

Se redondea primero la base y después el resultado para reproducir los ejemplos del documento. STAB vale 1.5 si coincide el tipo y 1 en otro caso. La efectividad multiplica ambos tipos (incluye 0.25 y 4). La inmunidad siempre produce cero; un ataque acertado no inmune hace al menos un punto. La precisión se comprueba con `uniform(1, 100) <= precisión`; el crítico con probabilidad 1/16 y factor 1.5; la dispersión usa `uniform(0.85, 1.0)`.

Los ejemplos con dispersión 1 producen 270 HP (Jolteon contra Gyarados), 0 HP (Terremoto contra Charizard) y 56 HP (Lanzallamas crítico contra Blastoise). La pérdida efectiva de HP se limita a la salud restante.

## Reglas y decisiones

Los cambios siempre ocurren antes de los ataques. Entre acciones de igual clase decide la velocidad; los empates se resuelven con probabilidad 0.5. El ataque se dirige al Pokémon actualmente activo, incluido uno que acaba de entrar. Un debilitado pierde su acción pendiente. Si quedan reservas, el jugador elige reemplazo inmediatamente antes de continuar; cuando se pierde el último Pokémon termina el combate.

Los PP se consumen incluso si el ataque falla o el objetivo es inmune. Si se agotan los cuatro movimientos se habilita Forcejeo: potencia 50, físico, neutral, sin STAB, precisión 100 y retroceso de un cuarto de HP máximo (mínimo 1). Es una extensión explícita para evitar bloqueos; puede causar empate si ambos últimos Pokémon caen.

Los datos son una configuración académica: las estadísticas se escogen para la simulación, y los valores relevantes de los ejemplos se conservan. Los movimientos solo ejecutan daño: no se modelan estados alterados, habilidades, objetos, efectos secundarios, prioridad propia de movimientos ni restricciones de aprendizaje por especie. Por ello, Ataque Rápido sigue la prioridad por velocidad exigida en el enunciado. No se requiere internet durante el juego.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Se comprueban los cuatro ejemplos, doble resistencia e inmunidad, velocidad y desempates, cambios, consumo de PP, cancelación de acciones tras debilitamiento, independencia de datos, entradas incorrectas, empate por retroceso y una partida completa automatizada.

Requisito de referencia: `proyecto final.md`, suministrado en la carpeta superior. Enlaces de consulta incluidos en ese enunciado: [Pokémon Database](https://pokemondb.net/pokedex/dragonite) y [Terremoto](https://pokemondb.net/move/earthquake).
