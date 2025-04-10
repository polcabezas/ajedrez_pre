
# El Tablero de Ajedrez Explicado

El tablero de ajedrez (`Tablero`) es como una gran caja mágica que guarda todo lo que pasa en el juego de ajedrez.

## ¿Qué guarda el tablero?

1. `casillas` - Un cuadrado grande dividido en 64 cuadritos más pequeños donde viven las piezas
2. `historial_movimientos` - Apunta todos los movimientos que han hecho los jugadores
3. `piezasCapturadas` - Guarda las piezas que han sido "comidas"
4. `derechosEnroque` - Recuerda si los reyes pueden hacer un movimiento especial llamado enroque
5. `objetivoPeonAlPaso` - Marca si un peón puede ser capturado de una forma especial
6. `turno_blanco` - Nos dice de quién es el turno (blancas o negras)
7. `contadorRegla50Movimientos` - Cuenta movimientos para una regla especial
8. `estado_juego` - Dice si el juego sigue, hay jaque, jaque mate o tablas
9. `numero_movimiento` - El número de movimientos completos jugados
10. `ultimo_movimiento` - Recuerda el último movimiento que se hizo
11. `historial_posiciones` - Recuerda cuántas veces se ha repetido una misma posición

## ¿Qué puede hacer el tablero?

### 1. Prepararse para jugar
- `inicializarTablero` - Pone todas las piezas en sus casillas al principio

### 2. Revisar el tablero
- `esPosicionValida` - Comprueba si una casilla existe en el tablero
- `getPieza` - Mira qué pieza hay en una casilla
- `esBlanco` - Dice si una pieza es blanca o negra

### 3. Mover piezas
- `moverPieza` - Mueve una pieza de un lugar a otro
- `capturarPieza` - Guarda una pieza que ha sido "comida"
- `realizarEnroque` - Hace el movimiento especial del rey y la torre

### 4. Vigilar peligros
- `esCasillaAmenazada` - Comprueba si una casilla está en peligro
- `_simular_y_verificar_seguridad` - Prueba si un movimiento es seguro para el rey

### 5. Actualizar las reglas
- `actualizarDerechosEnroque` - Cambia si se puede hacer enroque
- `actualizarPeonAlPaso` - Actualiza la regla especial para peones
- `actualizarContadores` - Lleva la cuenta de los movimientos
- `actualizarEstadoJuego` - Dice si hay jaque, mate o tablas
- `esMaterialInsuficiente` - Mira si quedan pocas piezas para terminar

### 6. Buscar movimientos
- `obtener_todos_movimientos_legales` - Encuentra todos los movimientos que se pueden hacer

## Amigos del tablero

El tablero tiene amigos que son las piezas:
- `Pieza` - Es el papá de todas las piezas
- `Torre`, `Caballo`, `Alfil`, `Reina`, `Rey`, `Peon` - Son los diferentes tipos de piezas

### ¿Cómo se comunican?

1. El tablero le da a cada pieza una copia de sí mismo (`self`) cuando las crea
2. Cada pieza sabe:
   - Su `color` (blanco o negro)
   - Su `posicion` en el tablero
   - Si `se_ha_movido` antes
3. El tablero pregunta a las piezas:
   - `obtener_movimientos_legales()` - "¿A dónde puedes moverte?"
   - `obtenerNotacionFEN()` - "¿Cómo te escribo en el idioma del ajedrez?"

El tablero y las piezas trabajan juntos como un equipo para hacer que el juego de ajedrez funcione correctamente.
