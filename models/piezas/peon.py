"""
Define la pieza Peón y su lógica específica.
"""

import os
import logging # Importar logging
from typing import Literal, Tuple, List, TYPE_CHECKING

from .pieza import Pieza  # Importación relativa desde el mismo directorio

if TYPE_CHECKING:
    from models.tablero import Tablero # Para type hints

logger = logging.getLogger(__name__) # Obtener logger para este módulo

class Peon(Pieza):
    """
    Representa la pieza de ajedrez Peón.
    """
    def __init__(self, color: Literal['blanco', 'negro'], posicion: Tuple[int, int], tablero: 'Tablero'):
        """
        Inicializa un Peón.

        Args:
            color: El color de la pieza ('blanco' o 'negro').
            posicion: Una tupla (fila, columna) indicando la posición inicial.
            tablero: La instancia del tablero a la que pertenece la pieza.
        """
        super().__init__(color, posicion, tablero)

        # Establecer la imagen específica del peón
        nombre_archivo = f"peon {self.color}.png"
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
        Devuelve el símbolo estándar para el Peón.
        Usamos 'P' según la notación algebraica estándar FIDE.
        """
        return 'P'

    def obtener_movimientos_potenciales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos potenciales para el Peón.
        Incluye avance simple, avance doble (si aplica) y las dos diagonales de captura.
        NO valida si las casillas están ocupadas, si la captura es válida,
        si es en passant, o si el movimiento deja al rey en jaque.
        Esa lógica pertenece a `obtener_movimientos_legales`.

        Returns:
            Lista de posiciones (fila, columna) destino potenciales.
        """
        movimientos_potenciales = []
        fila_actual, col_actual = self.posicion

        # Determinar la dirección del movimiento y la fila inicial según el color
        if self.color == 'blanco':
            direccion = 1  # Blancas avanzan incrementando la fila (de 1 a 7)
            fila_inicial = 1
        else: # Negro
            direccion = -1 # Negras avanzan decrementando la fila (de 6 a 0)
            fila_inicial = 6

        # 1. Avance simple
        fila_destino_simple = fila_actual + direccion
        movimientos_potenciales.append((fila_destino_simple, col_actual))

        # 2. Avance doble (solo desde la fila inicial)
        if fila_actual == fila_inicial:
            fila_destino_doble = fila_actual + 2 * direccion
            movimientos_potenciales.append((fila_destino_doble, col_actual))

        # 3. Capturas diagonales
        col_izquierda = col_actual - 1
        col_derecha = col_actual + 1
        movimientos_potenciales.append((fila_destino_simple, col_izquierda))
        movimientos_potenciales.append((fila_destino_simple, col_derecha))

        # Nota: La validez real de estos movimientos (p.ej., si hay pieza para capturar,
        # si el avance es a casilla vacía, si está dentro del tablero) se verificará
        # en `obtener_movimientos_legales`.

        return movimientos_potenciales 

    def obtener_movimientos_legales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos legales para este Peón.
        Considera: avance simple, avance doble, capturas diagonales y captura al paso.
        Filtra los movimientos potenciales según las reglas específicas del Peón.
        NOTA: La validación de seguridad del rey (no dejarlo en jaque) se hace llamando
        a `tablero._simular_y_verificar_seguridad` para cada movimiento candidato.

        Returns:
            Una lista de tuplas (fila, columna) representando las casillas destino legales.
        """
        movimientos_legales = []
        fila_actual, col_actual = self.posicion
        color_oponente = 'negro' if self.color == 'blanco' else 'blanco'

        # Determinar la dirección del movimiento y las filas relevantes
        if self.color == 'blanco':
            direccion = 1
            fila_inicial = 1
            fila_en_passant = 4 # Fila 5 para el peón blanco (índice 4)
        else: # Negro
            direccion = -1
            fila_inicial = 6
            fila_en_passant = 3 # Fila 4 para el peón negro (índice 3)

        # 1. Avance simple
        destino_simple = (fila_actual + direccion, col_actual)
        if self.tablero.esPosicionValida(destino_simple) and self.tablero.getPieza(destino_simple) is None:
            # Comprobar seguridad
            if self.tablero._simular_y_verificar_seguridad(self, destino_simple):
                movimientos_legales.append(destino_simple)

                # 2. Avance doble (solo si el avance simple es seguro y posible)
                if fila_actual == fila_inicial:
                    destino_doble = (fila_actual + 2 * direccion, col_actual)
                    # Comprobar camino libre y destino válido/vacío
                    if self.tablero.esPosicionValida(destino_doble) and self.tablero.getPieza(destino_doble) is None:
                        # Comprobar seguridad para avance doble
                        if self.tablero._simular_y_verificar_seguridad(self, destino_doble):
                            movimientos_legales.append(destino_doble)

        # 3. Capturas diagonales estándar
        destinos_diagonales = [
            (fila_actual + direccion, col_actual - 1), # Diagonal izquierda
            (fila_actual + direccion, col_actual + 1)  # Diagonal derecha
        ]
        for destino_diag in destinos_diagonales:
            if self.tablero.esPosicionValida(destino_diag):
                pieza_en_destino = self.tablero.getPieza(destino_diag)
                if pieza_en_destino is not None and pieza_en_destino.color == color_oponente:
                    # Comprobar seguridad para captura diagonal
                    if self.tablero._simular_y_verificar_seguridad(self, destino_diag):
                        movimientos_legales.append(destino_diag)

        # 4. Captura al paso (En Passant)
        if fila_actual == fila_en_passant and self.tablero.objetivoPeonAlPaso is not None:
            objetivo_ep = self.tablero.objetivoPeonAlPaso
            # Comprobar si el objetivo EP coincide con un movimiento diagonal potencial
            if objetivo_ep in [(fila_actual + direccion, col_actual - 1), (fila_actual + direccion, col_actual + 1)]:
                 # Comprobar seguridad para captura al paso
                 # La simulación se encarga de quitar el peón capturado correcto
                 if self.tablero._simular_y_verificar_seguridad(self, objetivo_ep):
                    movimientos_legales.append(objetivo_ep)

        return movimientos_legales 