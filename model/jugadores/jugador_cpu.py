"""
Define la clase para un jugador CPU (controlado por la IA).
"""

import logging
import random
from typing import Literal, TYPE_CHECKING, List, Tuple

from .jugador import Jugador, MoveInfo # Importar clase base y tipo

# Evitar importación circular para type hints
if TYPE_CHECKING:
    from model.juego import Juego
    # Necesitaremos acceso al tablero para obtener movimientos legales
    from model.tablero import Tablero

logger = logging.getLogger(__name__)

class JugadorCPU(Jugador):
    """
    Representa a un jugador controlado por la computadora (CPU).

    Esta clase hereda de Jugador e implementa `solicitarMovimiento`
    con una lógica simple de selección de movimiento (actualmente, aleatoria).
    """

    def __init__(self, nombre: str, color: Literal['blanco', 'negro'], nivel: int = 1):
        """
        Inicializa un nuevo jugador CPU.

        Args:
            nombre (str): El nombre del jugador CPU (p.ej., "CPU Nivel 1").
            color (Literal['blanco', 'negro']): El color asignado ('blanco' o 'negro').
            nivel (int, optional): Nivel de dificultad de la CPU. Por defecto es 1.
                                   Actualmente no se utiliza, pero se prevé para futuras mejoras.
        """
        super().__init__(nombre, color)
        self._nivel = nivel
        logger.info(f"Jugador CPU '{self.get_nombre()}' (Color: {self.get_color()}, Nivel: {self._nivel}) inicializado.")

    def get_nivel(self) -> int:
        """
        Devuelve el nivel de dificultad de la CPU.

        Returns:
            int: El nivel de la CPU.
        """
        return self._nivel

    def solicitarMovimiento(self, juego: 'Juego') -> MoveInfo:
        """
        Determina y devuelve el próximo movimiento de la CPU.

        La lógica actual elige un movimiento legal al azar.

        Args:
            juego (Juego): La instancia actual del juego, proporcionando acceso
                           al estado del tablero.

        Returns:
            MoveInfo: Una tupla que representa el movimiento seleccionado,
                      en el formato ((fila_origen, col_origen), (fila_destino, col_destino)).
                      Devuelve ((-1,-1),(-1,-1)) si no hay movimientos legales disponibles
                      (situación de fin de partida o error).

        Raises:
            AttributeError: Si el objeto `juego` no tiene un atributo `tablero` válido.
        """
        if not hasattr(juego, 'tablero') or juego.tablero is None:
             logger.error(f"JugadorCPU '{self.get_nombre()}' no puede acceder al tablero desde el objeto Juego.")
             raise AttributeError("El objeto Juego proporcionado no tiene un tablero válido.")

        tablero: 'Tablero' = juego.tablero
        color_actual = self.get_color()

        # Obtener todos los movimientos legales para el color de la CPU
        try:
            movimientos_legales: List[Tuple[Tuple[int, int], Tuple[int, int]]] = tablero.obtener_todos_movimientos_legales(color_actual)
        except Exception as e:
            logger.exception(f"Error al obtener movimientos legales para {color_actual}: {e}")
            # Considerar qué hacer aquí. ¿Lanzar excepción o devolver no-movimiento?
            # Devolver no-movimiento puede ser más seguro en un bucle de juego.
            return ((-1,-1), (-1,-1))


        if not movimientos_legales:
            logger.warning(f"JugadorCPU '{self.get_nombre()}' ({color_actual}) no tiene movimientos legales disponibles (¿Fin de partida?).")
            # Devolver un valor indicativo de que no hay movimiento
            return ((-1,-1), (-1,-1))

        # Elegir un movimiento al azar
        movimiento_elegido = random.choice(movimientos_legales)
        origen, destino = movimiento_elegido

        logger.info(f"JugadorCPU '{self.get_nombre()}' ({color_actual}) elige mover de {origen} a {destino}.")

        return movimiento_elegido

    # __str__ y __repr__ se heredan de Jugador. __repr__ mostrará JugadorCPU. 