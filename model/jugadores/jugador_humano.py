"""
Define la clase para un jugador humano.
"""

import logging
from typing import Literal, TYPE_CHECKING

from .jugador import Jugador, MoveInfo # Importar clase base y tipo

# Evitar importación circular para type hints
if TYPE_CHECKING:
    from model.juego import Juego

logger = logging.getLogger(__name__)

class JugadorHumano(Jugador):
    """
    Representa a un jugador humano en el juego de ajedrez.

    Esta clase hereda de la clase abstracta Jugador e implementa la lógica
    específica para un jugador humano. La obtención del movimiento se delega
    normalmente al controlador que gestiona la interfaz de usuario.
    """

    def __init__(self, nombre: str, color: Literal['blanco', 'negro']):
        """
        Inicializa un nuevo jugador humano.

        Args:
            nombre (str): El nombre del jugador humano.
            color (Literal['blanco', 'negro']): El color asignado ('blanco' o 'negro').
        """
        super().__init__(nombre, color)
        logger.info(f"Jugador Humano '{self.get_nombre()}' ({self.get_color()}) inicializado.")

    def solicitarMovimiento(self, juego: 'Juego') -> MoveInfo:
        """
        Solicita un movimiento al jugador humano.

        En una arquitectura MVC típica con una GUI, este método puede no ser
        llamado directamente para *obtener* el movimiento, ya que la interacción
        ocurre a través de eventos de la interfaz gráfica gestionados por el
        Controlador. El Controlador obtendrá el movimiento del usuario y
        lo pasará al modelo (Juego/Tablero).

        Este método se implementa para cumplir con la interfaz abstracta, pero
        su uso práctico puede variar. Podría usarse en un bucle de juego basado
        en consola, o simplemente lanzar un error si se espera que la lógica
        esté en el Controlador.

        Args:
            juego (Juego): La instancia actual del juego.

        Returns:
            MoveInfo: Este método, en este contexto, no debería devolver un movimiento.

        Raises:
            NotImplementedError: Indica que la lógica de obtención de movimiento
                                 para un jugador humano reside en la interacción
                                 controlador-vista, no directamente aquí.
        """
        logger.warning(f"solicitarMovimiento llamado para JugadorHumano '{self.get_nombre()}'. "
                       "La entrada de movimiento humano generalmente se maneja a través del Controlador/Vista.")
        # En un juego basado en consola, aquí se pediría input (p.ej., "e2 e4")
        # En un juego con GUI, esta función podría no hacer nada o lanzar error.
        raise NotImplementedError("La obtención del movimiento humano se gestiona externamente (Controlador/Vista).")

    # __str__ y __repr__ se heredan de Jugador y funcionan correctamente.
