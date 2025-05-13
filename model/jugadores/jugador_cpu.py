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
        self.modo_fallback = False  # Indica si se está usando el algoritmo simple de fallback

        # --- Inicialización del motor de ajedrez ---
        try:
            # Intentar inicializar el motor de ajedrez
            self.engine = chess.engine.SimpleEngine.popen_uci(self.motor_path)
            logger.info(f"Motor de ajedrez UCI inicializado desde: {self.motor_path}")
        except FileNotFoundError:
            self.modo_fallback = True
            logger.warning(f"No se encontró el motor de ajedrez en la ruta '{self.motor_path}'. "
                         f"Se usará un algoritmo simple para los movimientos del CPU.")
        except Exception as e:
            self.modo_fallback = True
            logger.warning(f"No se pudo inicializar el motor de ajedrez: {e}. "
                         f"Se usará un algoritmo simple para los movimientos del CPU.")
        # --- Fin inicialización ---

        nombre_modo = "algoritmo simple" if self.modo_fallback else f"motor UCI ({self.motor_path})"
        logger.info(f"Jugador CPU '{self.get_nombre()}' (Color: {self.get_color()}, Nivel: {self._nivel}) inicializado usando {nombre_modo}.")

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
        Si el motor no está disponible, usa un algoritmo simple para generar un movimiento aleatorio.

        Convierte el estado actual del juego al formato `python-chess`, consulta al motor
        por el mejor movimiento según el nivel de dificultad, y convierte el resultado
        de nuevo al formato interno `MoveInfo`.

        Args:
            juego (Juego): La instancia actual del juego.

        Returns:
            MoveInfo: Tupla ((fila_origen, col_origen), (fila_destino, col_destino)).
                      Devuelve ((-1,-1),(-1,-1)) si no puede encontrar un movimiento (fin de partida),
                      o si ocurre un error y no hay movimientos disponibles.
        """
        # Verificar acceso al tablero
        if not hasattr(juego, 'tablero') or juego.tablero is None:
             logger.error(f"JugadorCPU '{self.get_nombre()}' no puede acceder al tablero desde el objeto Juego.")
             # Considerar lanzar excepción o devolver movimiento inválido
             return ((-1,-1), (-1,-1)) # Devolver movimiento inválido

        tablero_interno = juego.tablero
        color_actual_str = self.get_color() # 'blanco' o 'negro'

        # Si el motor no está disponible, usar la lógica de fallback
        if self.engine is None:
            logger.warning(f"Motor de ajedrez no disponible. Usando algoritmo simple para jugador CPU '{self.get_nombre()}'.")
            return self._generar_movimiento_simple(tablero_interno)

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
             return self._generar_movimiento_simple(tablero_interno)  # Usar movimiento simple como fallback
        except Exception as e:
             logger.exception(f"Error inesperado durante la conversión del tablero para {color_actual_str}: {e}")
             return self._generar_movimiento_simple(tablero_interno)  # Usar movimiento simple como fallback

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
                return self._generar_movimiento_simple(tablero_interno)  # Intentar con movimiento simple

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
             return self._generar_movimiento_simple(tablero_interno)  # Usar movimiento simple como fallback
        except chess.engine.EngineError as e:
             logger.error(f"Error del motor de ajedrez para {color_actual_str}: {e}. FEN: {board.fen()}")
             return self._generar_movimiento_simple(tablero_interno)  # Usar movimiento simple como fallback
        except Exception as e:
             logger.exception(f"Error inesperado al solicitar movimiento del motor para {color_actual_str}: {e}")
             return self._generar_movimiento_simple(tablero_interno)  # Usar movimiento simple como fallback
             
    def _generar_movimiento_simple(self, tablero):
        """
        Algoritmo simple para generar un movimiento válido cuando el motor de ajedrez no está disponible.
        Selecciona una pieza aleatoria que pertenezca al jugador y un movimiento aleatorio válido.
        
        Args:
            tablero: El tablero actual del juego.
            
        Returns:
            MoveInfo: Tupla con las coordenadas de origen y destino del movimiento,
                    o ((-1,-1),(-1,-1)) si no hay movimiento posible.
        """
        try:
            import random
            
            # Obtener todas las piezas del color del jugador CPU
            piezas_propias = []
            for fila in range(8):
                for columna in range(8):
                    pieza = tablero.getPieza((fila, columna))
                    if pieza and pieza.get_color() == self.get_color():
                        piezas_propias.append(((fila, columna), pieza))
            
            # Barajar la lista para seleccionar aleatoriamente
            random.shuffle(piezas_propias)
            
            # Encontrar la primera pieza que tenga movimientos válidos
            for posicion, pieza in piezas_propias:
                if hasattr(pieza, 'obtener_movimientos_legales') and callable(pieza.obtener_movimientos_legales):
                    movimientos = pieza.obtener_movimientos_legales()
                    if movimientos:
                        # Seleccionar un movimiento aleatorio
                        destino = random.choice(movimientos)
                        logger.info(f"JugadorCPU '{self.get_nombre()}' ({self.get_color()}) generó movimiento simple: {posicion} -> {destino}")
                        return (posicion, destino)
            
            logger.warning(f"No se encontró ningún movimiento válido para JugadorCPU '{self.get_nombre()}' ({self.get_color()})")
            return ((-1,-1), (-1,-1))  # No hay movimiento posible
            
        except Exception as e:
            logger.exception(f"Error al generar movimiento simple: {e}")
            return ((-1,-1), (-1,-1))  # Error, devolver movimiento inválido

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