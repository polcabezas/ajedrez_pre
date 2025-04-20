"""
Define la clase para un jugador CPU (controlado por la IA).
"""

import logging
import random
from typing import Literal, TYPE_CHECKING, List, Tuple, Optional

# +++ Imports for python-chess and engine +++
import chess
import chess.engine
# --- End imports ---

from .jugador import Jugador, MoveInfo # Importar clase base y tipo

# Evitar importación circular para type hints
if TYPE_CHECKING:
    from model.juego import Juego
    # Necesitaremos acceso al tablero para obtener movimientos legales
    from model.tablero import Tablero
    from model.piezas.pieza import Pieza # Import Pieza for type hint

logger = logging.getLogger(__name__)

class JugadorCPU(Jugador):
    """
    Representa a un jugador controlado por la computadora (CPU) usando un motor de ajedrez externo.

    Esta clase hereda de Jugador e implementa `solicitarMovimiento`
    utilizando la librería `python-chess` y un motor UCI como Stockfish.
    """

    # Mapa de símbolos propios a tipos de pieza de python-chess
    _SIMBOLO_A_TIPO_PIEZA = {
        'P': chess.PAWN,
        'N': chess.KNIGHT, # Caballo
        'B': chess.BISHOP, # Alfil
        'R': chess.ROOK,   # Torre
        'Q': chess.QUEEN,  # Reina
        'K': chess.KING    # Rey
    }

    def __init__(self, nombre: str, color: Literal['blanco', 'negro'], nivel: int = 1, motor_path: Optional[str] = "stockfish"):
        """
        Inicializa un nuevo jugador CPU.

        Args:
            nombre (str): El nombre del jugador CPU (p.ej., "CPU Nivel 1").
            color (Literal['blanco', 'negro']): El color asignado ('blanco' o 'negro').
            nivel (int, optional): Nivel de dificultad de la CPU (aproximadamente correlacionado con tiempo de pensamiento). Por defecto es 1.
            motor_path (Optional[str], optional): Ruta al ejecutable del motor UCI (p.ej., Stockfish).
                                                  Por defecto es "stockfish", asumiendo que está en el PATH.
        """
        super().__init__(nombre, color)
        self._nivel = nivel
        self.engine: Optional[chess.engine.SimpleEngine] = None # Inicializar como None
        self.motor_path = motor_path

        # --- Inicialización del motor de ajedrez ---
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.motor_path)
            logger.info(f"Motor de ajedrez UCI inicializado desde: {self.motor_path}")
        except FileNotFoundError:
            logger.error(f"Error: No se encontró el motor de ajedrez en la ruta especificada: '{self.motor_path}'. "
                         f"Asegúrate de que Stockfish (u otro motor UCI) esté instalado y en el PATH, "
                         f"o proporciona la ruta correcta al inicializar JugadorCPU.")
            # El motor seguirá siendo None, solicitarMovimiento fallará elegantemente.
        except Exception as e:
            logger.exception(f"Se produjo un error inesperado al inicializar el motor de ajedrez desde '{self.motor_path}': {e}")
            # Dejar el motor como None.
        # --- Fin inicialización ---

        logger.info(f"Jugador CPU '{self.get_nombre()}' (Color: {self.get_color()}, Nivel: {self._nivel}) inicializado.")

    def get_nivel(self) -> int:
        """
        Devuelve el nivel de dificultad de la CPU.

        Returns:
            int: El nivel de la CPU.
        """
        return self._nivel

    # --- Métodos de conversión ---
    def _convertir_coordenada_a_indice(self, pos: Tuple[int, int]) -> int:
        """Convierte coordenadas (fila, col) 0-7 a índice de casilla chess (0-63)."""
        fila, col = pos
        # Nuestra fila 0 es la fila 1 de chess, fila 7 es la 8. Col 0 es a, Col 7 es h.
        # Indice = columna + fila * 8
        return col + fila * 8

    def _convertir_indice_a_coordenada(self, indice: int) -> Tuple[int, int]:
        """Convierte índice de casilla chess (0-63) a coordenadas (fila, col) 0-7."""
        # fila = indice // 8, columna = indice % 8
        return indice // 8, indice % 8

    def _convertir_a_chess_board(self, tablero: 'Tablero') -> chess.Board:
        """
        Convierte el estado interno del Tablero a un objeto chess.Board.

        Args:
            tablero (Tablero): La instancia del tablero del juego.

        Returns:
            chess.Board: El tablero convertido al formato de python-chess.

        Raises:
            ValueError: Si se encuentra un tipo de pieza desconocido.
        """
        board = chess.Board()
        board.clear_board() # Empezar con un tablero vacío

        # 1. Colocar piezas
        for fila_idx, fila in enumerate(tablero.casillas):
            for col_idx, pieza in enumerate(fila):
                if pieza:
                    indice_casilla = self._convertir_coordenada_a_indice((fila_idx, col_idx))
                    simbolo = pieza.obtener_simbolo() # e.g., 'P', 'R', 'k'
                    tipo_pieza = self._SIMBOLO_A_TIPO_PIEZA.get(simbolo.upper())

                    if tipo_pieza is None:
                         logger.error(f"Símbolo de pieza desconocido '{simbolo}' en ({fila_idx}, {col_idx}) durante la conversión.")
                         raise ValueError(f"Símbolo de pieza desconocido: {simbolo}")

                    color_pieza = chess.WHITE if pieza.get_color() == 'blanco' else chess.BLACK
                    chess_piece = chess.Piece(tipo_pieza, color_pieza)
                    board.set_piece_at(indice_casilla, chess_piece)

        # 2. Establecer turno
        board.turn = chess.WHITE if tablero.getTurnoColor() == 'blanco' else chess.BLACK

        # 3. Establecer derechos de enroque
        mask_enroque = 0
        if tablero.derechosEnroque['blanco']['corto']: mask_enroque |= chess.BB_H1 # K
        if tablero.derechosEnroque['blanco']['largo']: mask_enroque |= chess.BB_A1 # Q
        if tablero.derechosEnroque['negro']['corto']: mask_enroque |= chess.BB_H8 # k
        if tablero.derechosEnroque['negro']['largo']: mask_enroque |= chess.BB_A8 # q
        board.castling_rights = mask_enroque

        # 4. Establecer casilla de captura al paso (en passant)
        if tablero.objetivoPeonAlPaso:
            try:
                board.ep_square = self._convertir_coordenada_a_indice(tablero.objetivoPeonAlPaso)
            except IndexError:
                 logger.warning(f"Coordenada de en passant inválida {tablero.objetivoPeonAlPaso} recibida del tablero, ignorando.")
                 board.ep_square = None # Asegurarse de que sea None si la conversión falla
        else:
            board.ep_square = None

        # 5. Establecer contadores
        board.halfmove_clock = tablero.contadorRegla50Movimientos
        board.fullmove_number = tablero.numero_movimiento # Asumiendo que empieza en 1

        return board
    # --- Fin Métodos de conversión ---

    def solicitarMovimiento(self, juego: 'Juego') -> MoveInfo:
        """
        Determina y devuelve el próximo movimiento de la CPU utilizando el motor de ajedrez.

        Convierte el estado actual del juego al formato `python-chess`, consulta al motor
        por el mejor movimiento según el nivel de dificultad, y convierte el resultado
        de nuevo al formato interno `MoveInfo`.

        Args:
            juego (Juego): La instancia actual del juego.

        Returns:
            MoveInfo: Tupla ((fila_origen, col_origen), (fila_destino, col_destino)).
                      Devuelve ((-1,-1),(-1,-1)) si el motor no está disponible,
                      no puede encontrar un movimiento (fin de partida), o si ocurre un error.
        """
        # Verificar si el motor está disponible
        if self.engine is None:
            logger.error(f"JugadorCPU '{self.get_nombre()}' no puede solicitar movimiento: el motor de ajedrez no está inicializado.")
            return ((-1,-1), (-1,-1)) # Indicar error o incapacidad de mover

        # Verificar acceso al tablero
        if not hasattr(juego, 'tablero') or juego.tablero is None:
             logger.error(f"JugadorCPU '{self.get_nombre()}' no puede acceder al tablero desde el objeto Juego.")
             # Considerar lanzar excepción o devolver movimiento inválido
             return ((-1,-1), (-1,-1)) # Devolver movimiento inválido

        tablero_interno: 'Tablero' = juego.tablero
        color_actual_str = self.get_color() # 'blanco' o 'negro'

        # Convertir el tablero interno a formato python-chess
        try:
            board = self._convertir_a_chess_board(tablero_interno)
            # Validar si la posición es legal según python-chess (puede detectar inconsistencias)
            if not board.is_valid():
                 logger.warning(f"La posición del tablero convertida para {color_actual_str} es inválida según python-chess. FEN: {board.fen()}")
                 # Podría haber un problema en la conversión o estado ilegal en tablero_interno
                 # Intentar continuar, pero el motor podría fallar.

        except ValueError as e:
             logger.error(f"Error al convertir el tablero para {color_actual_str}: {e}")
             return ((-1,-1), (-1,-1))
        except Exception as e:
             logger.exception(f"Error inesperado durante la conversión del tablero para {color_actual_str}: {e}")
             return ((-1,-1), (-1,-1))

        # Calcular el mejor movimiento con el motor
        tiempo_limite = 0.1 * self._nivel # Tiempo en segundos (ajustar según sea necesario)
        try:
            # Asegurarse de que el turno en el board coincide con el color del jugador CPU
            color_esperado = chess.WHITE if color_actual_str == 'blanco' else chess.BLACK
            if board.turn != color_esperado:
                logger.warning(f"El turno en el tablero convertido ({'Blanco' if board.turn == chess.WHITE else 'Negro'}) "
                               f"no coincide con el color esperado del jugador CPU ({color_actual_str}). "
                               f"FEN: {board.fen()}. Se intentará jugar de todas formas.")
                # Esto podría indicar un error en _convertir_a_chess_board o en la lógica del juego.

            resultado = self.engine.play(board, chess.engine.Limit(time=tiempo_limite))

            if resultado.move is None:
                # Esto puede ocurrir en jaque mate o tablas.
                logger.warning(f"El motor no devolvió ningún movimiento para {color_actual_str} (Posible fin de partida). FEN: {board.fen()}")
                return ((-1,-1), (-1,-1)) # Indicar que no hay movimiento legal

            # Convertir el movimiento resultante de vuelta a nuestro formato
            movimiento_motor: chess.Move = resultado.move
            origen_idx = movimiento_motor.from_square
            destino_idx = movimiento_motor.to_square

            origen_coord = self._convertir_indice_a_coordenada(origen_idx)
            destino_coord = self._convertir_indice_a_coordenada(destino_idx)

            # TODO: Considerar la promoción. El motor puede devolver un movimiento con promoción (e.g., e7e8q).
            # Necesitamos manejar `movimiento_motor.promotion` si no es None.
            # Por ahora, simplemente devolvemos origen/destino. La lógica de promoción
            # debería manejarse en `tablero.moverPieza` o similar al recibir este movimiento.
            if movimiento_motor.promotion:
                simbolo_promo = chess.piece_symbol(movimiento_motor.promotion).upper() # P.ej., 'Q'
                logger.info(f"Movimiento del motor incluye promoción a: {simbolo_promo}")
                # La implementación actual de MoveInfo solo tiene origen/destino.
                # Se necesita una forma de pasar la información de promoción al tablero/juego.

            logger.info(f"JugadorCPU '{self.get_nombre()}' ({color_actual_str}) elige mover de {origen_coord} a {destino_coord} (Motor UCI: {movimiento_motor.uci()}).")
            return (origen_coord, destino_coord)

        except chess.engine.EngineTerminatedError:
             logger.error(f"El motor de ajedrez terminó inesperadamente para {color_actual_str}.")
             self.engine = None # Marcar el motor como no disponible
             return ((-1,-1), (-1,-1))
        except chess.engine.EngineError as e:
             logger.error(f"Error del motor de ajedrez para {color_actual_str}: {e}. FEN: {board.fen()}")
             return ((-1,-1), (-1,-1))
        except Exception as e:
             logger.exception(f"Error inesperado al solicitar movimiento del motor para {color_actual_str}: {e}")
             return ((-1,-1), (-1,-1))

    # --- Limpieza ---
    def __del__(self):
        """
        Asegura que el proceso del motor de ajedrez se cierre correctamente
        cuando la instancia de JugadorCPU es eliminada.
        """
        if self.engine:
            try:
                self.engine.quit()
                logger.info(f"Motor de ajedrez para JugadorCPU '{self.get_nombre()}' cerrado.")
            except chess.engine.EngineTerminatedError:
                 logger.warning(f"Intento de cerrar un motor ya terminado para JugadorCPU '{self.get_nombre()}'.")
            except Exception as e:
                 logger.exception(f"Error al intentar cerrar el motor de ajedrez para JugadorCPU '{self.get_nombre()}': {e}")
        # else:
            # logger.debug(f"No se requiere cierre del motor para JugadorCPU '{self.get_nombre()}' (ya estaba cerrado o nunca se inició).")

    # __str__ y __repr__ se heredan de Jugador. __repr__ mostrará JugadorCPU. 