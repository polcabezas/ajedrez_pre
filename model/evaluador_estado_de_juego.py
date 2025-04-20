import logging
from typing import TYPE_CHECKING

# Importar piezas necesarias para chequeos de tipo
from model.piezas.alfil import Alfil

# Evitar importación circular con type hinting
if TYPE_CHECKING:
    from model.tablero import Tablero # Asumiendo que Tablero está en model/tablero.py

logger = logging.getLogger(__name__)

class EvaluadorEstadoDeJuego:
    """
    Evalúa el estado actual del juego (jaque, mate, tablas por ahogado, material insuficiente, etc.).
    """
    def __init__(self, tablero: 'Tablero'):
        """
        Inicializa el evaluador de estado del juego.

        Args:
            tablero: Referencia al objeto Tablero del juego.
        """
        if tablero is None:
             # Podríamos lanzar una excepción o loggear un error crítico
             logger.error("EvaluadorEstadoDeJuego requiere una instancia válida de Tablero.")
             raise ValueError("La instancia del tablero no puede ser None.")
        self.tablero = tablero

    def esMaterialInsuficiente(self) -> bool:
        """
        Determina si el material restante en el tablero es insuficiente para
        forzar un jaque mate.

        Condiciones de material insuficiente:
        - Rey contra rey (K vs K)
        - Rey y alfil contra rey (K+B vs K)
        - Rey y caballo contra rey (K+N vs K)
        - Rey y alfil contra rey y alfil, con ambos alfiles en casillas del mismo color.

        NOTA: Esta implementación es una simplificación común. Hay otras posiciones
        extremadamente raras que también son tablas por material insuficiente,
        pero esta cubre los casos más habituales.

        Returns:
            True si el material es insuficiente, False en caso contrario.
        """
        piezas = {'blanco': [], 'negro': []}
        alfiles_color_casilla = {'blanco': set(), 'negro': set()}

        # 1. Recolectar todas las piezas restantes y anotar color de casilla de alfiles
        for fila in range(8):
            for col in range(8):
                # Acceder a las casillas a través de la referencia al tablero
                pieza = self.tablero.casillas[fila][col]
                if pieza:
                    piezas[pieza.color].append(type(pieza).__name__)
                    # Usar isinstance para chequear el tipo de pieza
                    if isinstance(pieza, Alfil):
                        # (fila + col) % 2 == 0 para casillas "negras" (o un color)
                        # (fila + col) % 2 != 0 para casillas "blancas" (o el otro color)
                        color_casilla = 'negra' if (fila + col) % 2 == 0 else 'blanca'
                        alfiles_color_casilla[pieza.color].add(color_casilla)

        piezas_blancas = piezas['blanco']
        piezas_negras = piezas['negro']
        num_blancas = len(piezas_blancas)
        num_negras = len(piezas_negras)

        # 2. Evaluar casos de material insuficiente
        # 2.1. Rey contra Rey (K vs K)
        if num_blancas == 1 and num_negras == 1:
            # Asumiendo que las únicas piezas son Reyes si solo hay una por bando
            return True

        # 2.2. Rey y Caballo contra Rey (K+N vs K)
        # Se asume que la pieza que no es Rey es la relevante (Caballo)
        if (num_blancas == 2 and 'Caballo' in piezas_blancas and num_negras == 1) or \
           (num_negras == 2 and 'Caballo' in piezas_negras and num_blancas == 1):
            return True

        # 2.3. Rey y Alfil contra Rey (K+B vs K)
        # Se asume que la pieza que no es Rey es la relevante (Alfil)
        if (num_blancas == 2 and 'Alfil' in piezas_blancas and num_negras == 1) or \
           (num_negras == 2 and 'Alfil' in piezas_negras and num_blancas == 1):
            return True

        # 2.4. Rey y Alfil contra Rey y Alfil (mismo color de casilla) (K+B vs K+B)
        # Se asume que las piezas son Rey y Alfil si hay dos por bando
        if num_blancas == 2 and 'Alfil' in piezas_blancas and \
           num_negras == 2 and 'Alfil' in piezas_negras:
            # Si ambos sets tienen 1 elemento y son iguales, los alfiles están en el mismo color
            if len(alfiles_color_casilla['blanco']) == 1 and \
               len(alfiles_color_casilla['negro']) == 1 and \
               alfiles_color_casilla['blanco'] == alfiles_color_casilla['negro']:
                return True

        # 3. Si no es ninguno de los casos anteriores, hay material suficiente
        return False
