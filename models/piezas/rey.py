"""
Define la pieza Rey y su lógica específica.
"""

import os
import logging
from typing import Literal, Tuple, List, TYPE_CHECKING

from .pieza import Pieza  # Importación relativa desde el mismo directorio
from .torre import Torre # Necesario para verificar la torre en el enroque

if TYPE_CHECKING:
    from models.tablero import Tablero

logger = logging.getLogger(__name__)

class Rey(Pieza):
    """
    Representa la pieza de ajedrez Rey.
    """
    def __init__(self, color: Literal['blanco', 'negro'], posicion: Tuple[int, int], tablero: 'Tablero'):
        """
        Inicializa un Rey.

        Args:
            color: El color de la pieza ('blanco' o 'negro').
            posicion: Una tupla (fila, columna) indicando la posición inicial.
            tablero: La instancia del tablero a la que pertenece la pieza.
        """
        super().__init__(color, posicion, tablero)

        # Establecer la imagen específica del rey
        nombre_archivo = f"rey {self.color}.png"
        self.imagen = os.path.join("assets", "imagenes_piezas", nombre_archivo)

        # >>> Inicio: Verificar existencia de imagen
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            absolute_image_path = os.path.join(project_root, self.imagen)
            if not os.path.exists(absolute_image_path):
                 logger.warning(f"Archivo de imagen no encontrado para {self}: {absolute_image_path}")
        except Exception as e:
            logger.error(f"Error al verificar ruta de imagen para {self}: {e}")
        # <<< Fin: Verificar existencia de imagen

    def obtener_simbolo(self) -> str:
        """
        Devuelve el símbolo estándar para el Rey.
        Usamos 'K' según la notación algebraica estándar FIDE (King).
        """
        return 'K'

    def obtener_movimientos_potenciales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos potenciales para el Rey (un paso en cualquier dirección).
        Genera las 8 casillas adyacentes.

        Returns:
            Lista de posiciones (fila, columna) destino potenciales.
        """
        movimientos_potenciales = []
        fila_actual, col_actual = self.posicion

        # Los 8 desplazamientos posibles (horizontal, vertical, diagonal)
        desplazamientos = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for df, dc in desplazamientos:
            nueva_fila, nueva_col = fila_actual + df, col_actual + dc
            movimientos_potenciales.append((nueva_fila, nueva_col))

        # El enroque se añade como movimiento legal, no potencial, porque depende de muchas condiciones
        return movimientos_potenciales

    def obtener_movimientos_legales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos legales para este Rey.
        Incluye movimientos de un paso y el enroque (si es válido).
        Filtra movimientos que van fuera del tablero, a casillas ocupadas por piezas amigas,
        o a casillas amenazadas por el oponente.

        Returns:
            Una lista de tuplas (fila, columna) representando las casillas destino legales.
        """
        movimientos_legales = []
        color_oponente = 'negro' if self.color == 'blanco' else 'blanco'

        # 1. Filtrar movimientos potenciales de un paso
        movimientos_potenciales = self.obtener_movimientos_potenciales()
        for destino in movimientos_potenciales:
            if not self.tablero.esPosicionValida(destino):
                continue # Fuera del tablero

            pieza_en_destino = self.tablero.getPieza(destino)
            if pieza_en_destino is not None and pieza_en_destino.color == self.color:
                continue # Casilla ocupada por pieza amiga

            # Verificar si la casilla destino está amenazada (Rey no puede moverse a una casilla atacada)
            if self.tablero.esCasillaAmenazada(destino, color_oponente):
                continue # No se puede mover a una casilla atacada

            # Verificar si el movimiento deja al rey en jaque (King Safety Check - ¡NUEVO!)
            # Aunque el destino no esté atacado, mover el rey podría REVELAR un ataque.
            if self.tablero._simular_y_verificar_seguridad(self, destino):
                movimientos_legales.append(destino)

        # 2. Verificar y añadir movimientos de Enroque
        # La seguridad del enroque (no pasar/aterrizar en casilla atacada) ya está en _obtener_movimientos_enroque
        movimientos_legales.extend(self._obtener_movimientos_enroque())

        return movimientos_legales

    def _obtener_movimientos_enroque(self) -> List[Tuple[int, int]]:
        """
        Verifica las condiciones y devuelve los movimientos de enroque legales.

        Returns:
            Lista con las posiciones destino del Rey para los enroques válidos (si los hay).
        """
        movimientos_enroque = []
        fila, col_rey = self.posicion
        color_oponente = 'negro' if self.color == 'blanco' else 'blanco'

        # Condiciones iniciales: El rey no debe haberse movido y no debe estar en jaque.
        if self.se_ha_movido or self.tablero.esCasillaAmenazada(self.posicion, color_oponente):
            return [] # No se puede enrocar si el rey se ha movido o está en jaque

        # Coordenadas relevantes
        col_torre_corta = 7
        col_torre_larga = 0
        casillas_intermedias_corto = [(fila, 5), (fila, 6)]
        casillas_intermedias_largo = [(fila, 1), (fila, 2), (fila, 3)]
        destino_rey_corto = (fila, 6)
        destino_rey_largo = (fila, 2)
        paso_rey_corto = (fila, 5)
        paso_rey_largo = (fila, 3)

        # Verificar Enroque Corto (O-O)
        if self.tablero.derechosEnroque[self.color]['corto']:
            torre_pos_corta = (fila, col_torre_corta)
            torre_corta = self.tablero.getPieza(torre_pos_corta)
            if isinstance(torre_corta, Torre) and not torre_corta.se_ha_movido:
                # Verificar casillas intermedias vacías
                if all(self.tablero.getPieza(pos) is None for pos in casillas_intermedias_corto):
                    # Verificar que las casillas por las que pasa/a las que llega el rey no están atacadas
                    if not self.tablero.esCasillaAmenazada(paso_rey_corto, color_oponente) and \
                       not self.tablero.esCasillaAmenazada(destino_rey_corto, color_oponente):
                        movimientos_enroque.append(destino_rey_corto)

        # Verificar Enroque Largo (O-O-O)
        if self.tablero.derechosEnroque[self.color]['largo']:
            torre_pos_larga = (fila, col_torre_larga)
            torre_larga = self.tablero.getPieza(torre_pos_larga)
            if isinstance(torre_larga, Torre) and not torre_larga.se_ha_movido:
                # Verificar casillas intermedias vacías
                if all(self.tablero.getPieza(pos) is None for pos in casillas_intermedias_largo):
                    # Verificar que las casillas por las que pasa/a las que llega el rey no están atacadas
                    # (El rey no pasa por (fila, 1)))
                    if not self.tablero.esCasillaAmenazada(destino_rey_largo, color_oponente) and \
                       not self.tablero.esCasillaAmenazada(paso_rey_largo, color_oponente):
                        movimientos_enroque.append(destino_rey_largo)

        return movimientos_enroque