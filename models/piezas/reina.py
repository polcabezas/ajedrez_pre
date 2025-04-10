"""
Define la pieza Reina y su lógica específica.
"""
import os
import logging # Importar logging
from typing import List, Tuple, TYPE_CHECKING, Literal

# Importar clase base y verificar tipos para evitar importación circular
from .pieza import Pieza
if TYPE_CHECKING:
    from models.tablero import Tablero # Para type hints

logger = logging.getLogger(__name__) # Obtener logger para este módulo

class Reina(Pieza):
    """
    Representa la pieza de ajedrez Reina.
    Hereda de la clase base Pieza.
    Combina el movimiento de la Torre y el Alfil.
    """
    def __init__(self, color: Literal['blanco', 'negro'], posicion: Tuple[int, int], tablero: 'Tablero'):
        """
        Inicializa una Reina.

        Args:
            color: El color de la pieza ('blanco' o 'negro').
            posicion: Una tupla (fila, columna) indicando la posición inicial.
            tablero: Referencia al tablero de juego.
        """
        super().__init__(color, posicion, tablero) # Llamada al constructor de la clase base

        # Establecer la imagen específica de la reina
        # Usamos minúsculas basado en los nombres de archivo proporcionados ('reina blanco.png')
        nombre_archivo = f"reina {self.color}.png"
        self.imagen = os.path.join("assets", "imagenes_piezas", nombre_archivo)

        # >>> Inicio: Verificar existencia de imagen
        try:
            # Intentar encontrar la raíz del proyecto subiendo dos niveles desde el archivo actual
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            absolute_image_path = os.path.join(project_root, self.imagen)

            if not os.path.exists(absolute_image_path):
                 logger.warning(f"Archivo de imagen no encontrado para {self}: {absolute_image_path}")
        except Exception as e:
            logger.error(f"Error al verificar ruta de imagen para {self}: {e}")
        # <<< Fin: Verificar existencia de imagen

    def obtener_simbolo(self) -> str:
        """
        Devuelve el símbolo estándar para la Reina.
        Usamos 'Q' según la notación algebraica estándar FIDE (Queen).
        """
        return 'Q'

    def obtener_movimientos_potenciales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos potenciales para la Reina (horizontales, verticales y diagonales).
        Combina la lógica de la Torre y el Alfil.
        Se extiende en cada una de las 8 direcciones hasta encontrar un borde
        o CUALQUIER pieza. La casilla de la pieza encontrada (si la hay) se incluye.
        El filtrado final se hace en `obtener_movimientos_legales` de la clase base.

        Returns:
            Lista de posiciones (fila, columna) destino potenciales.
        """
        movimientos_potenciales = []
        fila_actual, col_actual = self.posicion

        # Direcciones: 4 diagonales + 4 ortogonales
        direcciones = [
            # Diagonales (como Alfil)
            (-1, -1), (-1, 1),
            (1, -1),  (1, 1),
            # Ortogonales (como Torre)
            (-1, 0),  # Arriba
            (1, 0),   # Abajo
            (0, -1),  # Izquierda
            (0, 1)    # Derecha
        ]

        for df, dc in direcciones:
            temp_fila, temp_col = fila_actual + df, col_actual + dc

            # Explorar en la dirección actual
            while self.tablero.esPosicionValida((temp_fila, temp_col)):
                movimientos_potenciales.append((temp_fila, temp_col))
                pieza_en_camino = self.tablero.getPieza((temp_fila, temp_col))
                if pieza_en_camino is not None:
                    # Se encontró una pieza (amiga o enemiga), detener la exploración en esta dirección
                    break
                # Moverse un paso más en la misma dirección
                temp_fila += df
                temp_col += dc

        return movimientos_potenciales

    # No es necesario sobreescribir obtener_movimientos_legales por ahora,
    # ya que la Reina no tiene movimientos especiales.
    # La implementación base en Pieza se encarga del filtrado básico. 