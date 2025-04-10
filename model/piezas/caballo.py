"""
Define la pieza Caballo y su lógica específica.
"""
import os
import logging # Importar logging
from typing import List, Tuple, TYPE_CHECKING, Literal

# Importar clase base y verificar tipos para evitar importación circular
from .pieza import Pieza
if TYPE_CHECKING:
    from model.tablero import Tablero # Para type hints

logger = logging.getLogger(__name__) # Obtener logger para este módulo

class Caballo(Pieza):
    """
    Representa la pieza de ajedrez Caballo.
    Hereda de la clase base Pieza.
    """
    def __init__(self, color: Literal['blanco', 'negro'], posicion: Tuple[int, int], tablero: 'Tablero'):
        """
        Inicializa un Caballo.

        Args:
            color: El color de la pieza ('blanco' o 'negro').
            posicion: Una tupla (fila, columna) indicando la posición inicial.
            tablero: Referencia al tablero de juego.
        """
        super().__init__(color, posicion, tablero) # Llamada al constructor de la clase base

        # Establecer la imagen específica del caballo
        nombre_archivo = f"caballo {self.color}.png"
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
        Devuelve el símbolo estándar para el Caballo.
        Usamos 'N' según la notación algebraica estándar FIDE (Knight),
        para evitar colisión con 'K' de King o 'C' si se usara en español.
        """
        return 'N'

    def obtener_movimientos_potenciales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos potenciales (saltos en 'L') para el Caballo
        desde su posición actual. Este método NO filtra por límites del tablero
        ni por casillas ocupadas, ya que el caballo salta. El filtrado
        se realiza en `obtener_movimientos_legales`.

        Returns:
            Lista de posiciones (fila, columna) destino potenciales.
        """
        movimientos_potenciales = []
        fila_actual, col_actual = self.posicion

        # Lista de los 8 posibles desplazamientos relativos en forma de 'L'
        desplazamientos_caballo = [
            (-2, -1), (-2, 1),  # 2 arriba, 1 izq/der
            (-1, -2), (-1, 2),  # 1 arriba, 2 izq/der
            (1, -2), (1, 2),   # 1 abajo, 2 izq/der
            (2, -1), (2, 1)    # 2 abajo, 1 izq/der
        ]

        for df, dc in desplazamientos_caballo:
            nueva_fila, nueva_col = fila_actual + df, col_actual + dc
            # Generamos las 8 posiciones teóricas sin filtrar aquí.
            movimientos_potenciales.append((nueva_fila, nueva_col))

        return movimientos_potenciales

    # No es necesario sobreescribir obtener_movimientos_legales por ahora,
    # ya que el Caballo no tiene movimientos especiales como enroque o al paso,
    # y la lógica base de Pieza ya filtra por:
    # 1. Estar dentro del tablero (esPosicionValida).
    # 2. No capturar piezas propias.
    # La validación de no dejar al rey en jaque se hace ahora en la base. 