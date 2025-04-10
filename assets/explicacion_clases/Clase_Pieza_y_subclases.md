# Explicación de las Clases de Piezas

Vamos a ver qué hacen todas las piezas del ajedrez que viven en la carpeta `piezas`. ¡Es como conocer a todos los personajes de un cuento!

Primero, tenemos a la mamá y papá de todas las piezas:

### `Pieza` (en `pieza.py`) - El Papá/Mamá de Todas las Piezas

Esta es la clase **base**, como el molde general para todas las piezas.

**¿Qué guarda?**
*   `color`: Si es blanca o negra.
*   `posicion`: Dónde está en el tablero (su casita).
*   `tablero`: Una copia del tablero entero, para poder mirar dónde están las otras piezas.
*   `se_ha_movido`: Si ya se movió alguna vez (importante para reglas especiales).
*   `imagen`: El dibujito de la pieza.

**¿Qué sabe hacer?**
*   `obtener_simbolo()`: Dice qué letra la representa (¡pero ella no sabe cuál, sus hijos sí!).
*   `obtener_movimientos_potenciales()`: Imagina a dónde *podría* moverse, sin pensar mucho en las reglas (¡sus hijos saben cómo moverse de verdad!).
*   `obtener_movimientos_legales()`: Piensa bien y dice a dónde se puede mover *de verdad*, siguiendo las reglas y asegurándose de que el rey no quede en peligro. Usa la función secreta del tablero `_simular_y_verificar_seguridad` para esto.
*   `obtenerNotacionFEN()`: Dice cómo se escribe la pieza en el idioma secreto del ajedrez (FEN).
*   `_construir_ruta_imagen()`: Busca el dibujito correcto para la pieza.

---

Ahora, ¡vamos a conocer a los hijos! Todos ellos son "hijos" de `Pieza`, así que saben hacer todo lo que sabe hacer `Pieza`, pero cada uno tiene sus trucos especiales.

### `Peon` (en `peon.py`) - El Soldadito Valiente

**¿Qué guarda?**
*   Todo lo de `Pieza`.

**¿Qué sabe hacer (además de lo de Pieza)?**
*   `obtener_simbolo()`: Sabe que su símbolo es 'P'.
*   `obtener_movimientos_potenciales()`: Sabe moverse para adelante:
    *   Un pasito.
    *   ¡Dos pasitos si es su primer movimiento!
    *   Puede comer en diagonal hacia adelante.
*   `obtener_movimientos_legales()`: Es más listo y también sabe hacer la "captura al paso" (una regla especial) y avisa si llega al otro lado para convertirse en otra pieza (¡promoción!).

### `Caballo` (en `caballo.py`) - El Saltador Loco

**¿Qué guarda?**
*   Todo lo de `Pieza`.

**¿Qué sabe hacer (además de lo de Pieza)?**
*   `obtener_simbolo()`: Sabe que su símbolo es 'N' (¡viene de *Knight* en inglés!).
*   `obtener_movimientos_potenciales()`: Sabe moverse en forma de "L": dos casillas en una dirección (recta) y luego una a un lado. ¡Es el único que puede saltar por encima de otras piezas!

### `Torre` (en `torre.py`) - La Fuerte y Recta

**¿Qué guarda?**
*   Todo lo de `Pieza`.

**¿Qué sabe hacer (además de lo de Pieza)?**
*   `obtener_simbolo()`: Sabe que su símbolo es 'R' (¡de *Rook*!).
*   `obtener_movimientos_potenciales()`: Sabe moverse en línea recta (horizontal o vertical) todas las casillas que quiera, hasta que se choca con otra pieza o el borde del tablero.
*   ¡También ayuda al Rey a hacer el movimiento especial del enroque!

### `Alfil` (en `alfil.py`) - El Diagonal Elegante

**¿Qué guarda?**
*   Todo lo de `Pieza`.

**¿Qué sabe hacer (además de lo de Pieza)?**
*   `obtener_simbolo()`: Sabe que su símbolo es 'B' (¡de *Bishop*!).
*   `obtener_movimientos_potenciales()`: Sabe moverse en diagonal todas las casillas que quiera, siempre por casillas del mismo color, hasta que se choca con otra pieza o el borde.

### `Reina` (en `reina.py`) - La Más Poderosa

**¿Qué guarda?**
*   Todo lo de `Pieza`.

**¿Qué sabe hacer (además de lo de Pieza)?**
*   `obtener_simbolo()`: Sabe que su símbolo es 'Q' (¡de *Queen*!).
*   `obtener_movimientos_potenciales()`: ¡Es súper poderosa! Sabe moverse como la `Torre` (recto) Y como el `Alfil` (diagonal), todas las casillas que quiera.

### `Rey` (en `rey.py`) - El Más Importante (¡y un poco lento!)

**¿Qué guarda?**
*   Todo lo de `Pieza`.

**¿Qué sabe hacer (además de lo de Pieza)?**
*   `obtener_simbolo()`: Sabe que su símbolo es 'K' (¡de *King*!).
*   `obtener_movimientos_potenciales()`: Solo puede moverse un pasito en cualquier dirección (recto o diagonal).
*   `obtener_movimientos_legales()`: Es muy cuidadoso. Antes de decir a dónde puede ir, mira si puede hacer el "enroque" (un movimiento especial con la `Torre`). Para eso, pregunta al `tablero` si todavía tiene `derechosEnroque`, si las casillas entre él y la torre están vacías y si no están amenazadas por el enemigo.

**En resumen:**

Todas las piezas saben su color, dónde están y cómo es el tablero. La `Pieza` base les enseña a pensar si un movimiento es seguro. Luego, cada pieza (`Peon`, `Caballo`, etc.) sabe exactamente *cómo* se mueve (recto, diagonal, en L, saltando...) y si tiene alguna regla especial como el enroque o la captura al paso. ¡Trabajan junto al `Tablero` para que el juego sea divertido y justo!
