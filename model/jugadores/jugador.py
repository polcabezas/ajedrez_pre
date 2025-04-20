"""
Define la clase base abstracta para los jugadores del juego de ajedrez.
"""

import logging
from abc import ABC, abstractmethod
from typing import Literal, Tuple, TYPE_CHECKING

# Evitar importación circular para type hints
# Comentar o eliminar este bloque
# if TYPE_CHECKING:
#     from model.juego import Juego # Asumiendo que Juego está en model/juego.py

# Definir un tipo para la información del movimiento (provisional)
# Representa (fila_origen, col_origen), (fila_destino, col_destino)
MoveInfo = Tuple[Tuple[int, int], Tuple[int, int]]

# Configuración básica del logging
# TODO: Considerar mover la configuración de logging a un punto central (main.py o un módulo de config)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Jugador(ABC):
    """
    Clase base abstracta para representar un jugador en el juego de ajedrez.

    Esta clase no debe ser instanciada directamente. Las clases concretas
    (como JugadorHumano o JugadorCPU) deben heredar de esta y implementar
    el método abstracto `solicitarMovimiento`.

    Attributes:
        nombre (str): El nombre del jugador.
        color (Literal['blanco', 'negro']): El color de las piezas asignadas al jugador.
    """

    def __init__(self, nombre: str, color: Literal['blanco', 'negro']):
        """
        Inicializa un nuevo jugador.

        Args:
            nombre (str): El nombre del jugador. Debe ser una cadena no vacía.
            color (Literal['blanco', 'negro']): El color asignado al jugador.
                                                Debe ser 'blanco' o 'negro'.

        Raises:
            ValueError: Si el nombre está vacío o el color no es válido.
        """
        if not nombre:
            logger.error("El nombre del jugador no puede estar vacío.")
            raise ValueError("El nombre del jugador no puede estar vacío.")
        if color not in ['blanco', 'negro']:
            logger.error(f"Color inválido '{color}' proporcionado para el jugador '{nombre}'.")
            raise ValueError("El color debe ser 'blanco' o 'negro'.")

        self._nombre: str = nombre
        self._color: Literal['blanco', 'negro'] = color
        logger.info(f"Jugador '{self._nombre}' creado con color '{self._color}'.")

    def get_nombre(self) -> str:
        """
        Devuelve el nombre del jugador.

        Returns:
            str: El nombre del jugador.
        """
        return self._nombre

    def get_color(self) -> Literal['blanco', 'negro']:
        """
        Devuelve el color asignado al jugador.

        Returns:
            Literal['blanco', 'negro']: El color del jugador ('blanco' o 'negro').
        """
        return self._color

    @abstractmethod
    def solicitarMovimiento(self, juego: 'Juego') -> MoveInfo:
        """
        Método abstracto para que el jugador determine y devuelva su próximo movimiento.

        Las subclases deben implementar este método para definir cómo un jugador
        (humano o IA) decide su movimiento basándose en el estado actual del juego.

        Args:
            juego (Juego): La instancia actual del juego, proporcionando acceso
                           al estado del tablero y otras informaciones relevantes.

        Returns:
            MoveInfo: Una tupla que representa el movimiento seleccionado,
                      en el formato ((fila_origen, col_origen), (fila_destino, col_destino)).

        Raises:
            NotImplementedError: Si la subclase no implementa este método.
        """
        raise NotImplementedError("Las subclases deben implementar solicitarMovimiento()")

    def __str__(self) -> str:
        """
        Representación informal de la instancia del jugador.

        Returns:
            str: Cadena formateada con el nombre y color del jugador.
        """
        return f"Jugador(Nombre: {self._nombre}, Color: {self._color})"

    def __repr__(self) -> str:
        """
        Representación técnica de la instancia del jugador.

        Returns:
            str: Cadena que podría usarse para recrear el objeto (aproximadamente).
        """
        return f"{type(self).__name__}(nombre='{self._nombre}', color='{self._color}')"
