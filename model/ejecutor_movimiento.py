"""
Módulo que contiene la clase EjecutorMovimiento, responsable de
ejecutar movimientos validados y actualizar el estado del tablero.
"""

import logging
from typing import Tuple, Optional, Literal, TYPE_CHECKING

# Importar piezas para type hints y chequeos
from model.piezas.pieza import Pieza
from model.piezas.peon import Peon
from model.piezas.rey import Rey
from model.piezas.torre import Torre

if TYPE_CHECKING:
    from model.tablero import Tablero # Evitar importación circular

logger = logging.getLogger(__name__)

class EjecutorMovimiento:
    """
    Clase responsable de la ejecución de movimientos de ajedrez y
    la actualización del estado del juego resultante en el tablero.
    Asume que los movimientos que recibe ya han sido validados como legales.
    """

    def __init__(self, tablero: 'Tablero'):
        """
        Inicializa el ejecutor de movimientos.

        Args:
            tablero: La instancia del tablero sobre la que operará el ejecutor.
        """
        self.tablero = tablero

    def ejecutar_movimiento_normal(self, posOrigen: Tuple[int, int], posDestino: Tuple[int, int]) -> Literal['movimiento_ok', 'promocion_necesaria', 'error']:
        """
        Ejecuta un movimiento normal (no enroque) en el tablero.
        Gestiona capturas (normal y al paso), mueve la pieza, actualiza
        el estado del juego (enroque, al paso, contadores, etc.) y cambia el turno.

        Args:
            posOrigen: Tupla (fila, columna) de la casilla origen.
            posDestino: Tupla (fila, columna) de la casilla destino.

        Returns:
            - 'movimiento_ok': El movimiento se realizó con éxito.
            - 'promocion_necesaria': El movimiento fue un avance de peón a la última fila y requiere promoción.
            - 'error': Hubo un problema con las validaciones básicas internas (esto no debería ocurrir si el movimiento fue pre-validado).
        """
        # --- Logic moved from Tablero.moverPieza --- 
        
        # 1. Validar posiciones y pieza en origen
        # Basic validation assumed to be done before calling executor, but good practice to keep checks
        if not self.tablero.esPosicionValida(posOrigen) or not self.tablero.esPosicionValida(posDestino):
            logger.error(f"[Ejecutor] Posición origen {posOrigen} o destino {posDestino} inválida.")
            return 'error'
        pieza_movida = self.tablero.getPieza(posOrigen)
        if pieza_movida is None:
            logger.error(f"[Ejecutor] No hay pieza en la posición origen {posOrigen}.")
            return 'error'

        # Determinar si es captura y si es en passant
        pieza_capturada = self.tablero.getPieza(posDestino)
        es_captura = False
        # es_en_passant = False # Not explicitly needed here, determined by condition
        casilla_captura_ep = None # Casilla donde estaba el peón capturado al paso

        # Comprobar si es un movimiento de peón al destino objetivo de 'al paso'
        if isinstance(pieza_movida, Peon) and posDestino == self.tablero.objetivoPeonAlPaso:
            es_captura = True
            # es_en_passant = True
            # El peón capturado está en la misma columna que el destino,
            # pero en la fila de origen del peón que se mueve
            fila_capturada = posOrigen[0]
            col_capturada = posDestino[1]
            casilla_captura_ep = (fila_capturada, col_capturada)
            pieza_capturada_ep = self.tablero.getPieza(casilla_captura_ep)
            if pieza_capturada_ep is None or pieza_capturada_ep.color == pieza_movida.color:
                logger.error(f"[Ejecutor] Intento de captura al paso inválida en {posDestino} (sin peón o peón propio en {casilla_captura_ep})")
                return 'error' # Should have been caught by validation, but defensive check
            self._capturarPieza(pieza_capturada_ep)
            self.tablero.setPieza(casilla_captura_ep, None)
            logger.debug(f"[Ejecutor] Captura al paso realizada. Peón capturado en {casilla_captura_ep}")

        # 2. Gestionar captura normal (si no fue al paso)
        elif pieza_capturada is not None:
            if pieza_capturada.color == pieza_movida.color:
                logger.error(f"[Ejecutor] Intento de captura de pieza propia en {posDestino}.")
                return 'error' # Should have been caught by validation
            self._capturarPieza(pieza_capturada)
            es_captura = True

        # 3. Mover la pieza en el tablero
        self.tablero.setPieza(posDestino, pieza_movida)
        self.tablero.setPieza(posOrigen, None)

        # 4. Añadir al historial
        # TODO: Considerar añadir información extra al historial para en passant/promoción si es necesario para FEN o PGN.
        color_jugador = pieza_movida.color
        self.tablero.historial_movimientos.append((color_jugador, posOrigen, posDestino))

        # 5. Actualizar posición interna de la pieza
        if hasattr(pieza_movida, 'posicion'):
             pieza_movida.posicion = posDestino
             if hasattr(pieza_movida, 'se_ha_movido'):
                 pieza_movida.se_ha_movido = True
        else:
             # This case should ideally not happen with well-defined pieces
             logger.warning(f"[Ejecutor] La pieza {type(pieza_movida).__name__} movida a {posDestino} no tiene atributo 'posicion' para actualizar.")

        # 6. Actualizar estado del juego post-movimiento (excepto turno)
        # Calls methods directly on the Tablero instance
        self._actualizarDerechosEnroque(pieza_movida, posOrigen, pieza_capturada, posDestino)
        self._actualizarPeonAlPaso(pieza_movida, posOrigen, posDestino)
        self._actualizarContadores(pieza_movida, es_captura)
        self._actualizarUltimoMovimiento(posOrigen, posDestino)

        # 7. Detectar promoción de peón
        es_promocion = False
        if isinstance(pieza_movida, Peon):
            fila_destino = posDestino[0]
            if (pieza_movida.color == 'blanco' and fila_destino == 7) or \
               (pieza_movida.color == 'negro' and fila_destino == 0):
                es_promocion = True
                logger.debug(f"[Ejecutor] Promoción necesaria en {posDestino}")

        # 8. Cambiar turno
        self.tablero.turno_blanco = not self.tablero.turno_blanco

        # 9. Actualizar historial de posiciones DESPUÉS de cambiar el turno
        self.tablero.gestor_historico.registrar_posicion()

        # 10. Actualizar estado del juego AHORA, después del cambio de turno
        self.tablero.actualizarEstadoJuego()

        # Retornar estado
        if es_promocion:
            return 'promocion_necesaria'
        else:
            return 'movimiento_ok'

    def ejecutar_enroque(self, color: Literal['blanco', 'negro'], tipo: Literal['corto', 'largo']) -> bool:
        """
        Ejecuta el movimiento de enroque en el tablero.
        Mueve el Rey y la Torre, actualiza sus estados, actualiza los derechos
        de enroque, contadores, historial y cambia el turno.

        Args:
            color: El color del jugador que enroca ('blanco' o 'negro').
            tipo: El tipo de enroque ('corto' para flanco de rey, 'largo' para flanco de dama).

        Returns:
            True si el enroque se realizó con éxito, False si hubo un error inesperado.
        """
        # --- Logic moved from Tablero.realizarEnroque --- 

        # Determinar filas y columnas según el color y tipo
        fila = 0 if color == 'blanco' else 7
        
        # Posiciones iniciales y finales del Rey
        rey_col_origen = 4
        rey_pos_origen = (fila, rey_col_origen)
        rey_col_destino = 6 if tipo == 'corto' else 2
        rey_pos_destino = (fila, rey_col_destino)
        
        # Posiciones iniciales y finales de la Torre
        torre_col_origen = 7 if tipo == 'corto' else 0
        torre_pos_origen = (fila, torre_col_origen)
        torre_col_destino = 5 if tipo == 'corto' else 3
        torre_pos_destino = (fila, torre_col_destino)
        
        # Obtener las piezas (deberían ser Rey y Torre)
        rey = self.tablero.getPieza(rey_pos_origen)
        torre = self.tablero.getPieza(torre_pos_origen)
        
        if not isinstance(rey, Rey) or not isinstance(torre, Torre):
            logger.error(f"[Ejecutor] Piezas incorrectas en {rey_pos_origen} o {torre_pos_origen} para enroque {color} {tipo}.")
            return False
        
        # Mover las piezas en el tablero
        self.tablero.setPieza(rey_pos_destino, rey)
        self.tablero.setPieza(rey_pos_origen, None)
        self.tablero.setPieza(torre_pos_destino, torre)
        self.tablero.setPieza(torre_pos_origen, None)
        
        # Actualizar posición interna de las piezas
        if hasattr(rey, 'posicion'): rey.posicion = rey_pos_destino
        if hasattr(torre, 'posicion'): torre.posicion = torre_pos_destino
        if hasattr(rey, 'se_ha_movido'): rey.se_ha_movido = True
        if hasattr(torre, 'se_ha_movido'): torre.se_ha_movido = True
        
        # Añadir al historial (puede requerir formato especial para PGN/FEN)
        self.tablero.historial_movimientos.append((color, rey_pos_origen, rey_pos_destino)) # Registramos el mov del rey como representativo
        
        # Actualizar estado: derechos de enroque se pierden, contadores avanzan, etc.
        # El rey se movió, así que pierde ambos derechos
        self.tablero.derechosEnroque[color]['corto'] = False
        self.tablero.derechosEnroque[color]['largo'] = False
        # Actualizar Peón al Paso (se limpia porque no fue mov de peón)
        self.tablero.objetivoPeonAlPaso = None 
        # Actualizar Contadores (enroque no es captura ni mov de peón)
        self._actualizarContadores(rey, False) # Usamos el rey como pieza movida
        # Actualizar Último Movimiento (registramos el del rey)
        self._actualizarUltimoMovimiento(rey_pos_origen, rey_pos_destino)
        
        # Cambiar turno
        self.tablero.turno_blanco = not self.tablero.turno_blanco
        
        # Actualizar historial de posiciones DESPUÉS de cambiar el turno (ahora via gestor)
        self.tablero.gestor_historico.registrar_posicion()

        # Actualizar Estado del Juego AHORA, después del cambio de turno
        self.tablero.actualizarEstadoJuego()
        
        logger.info(f"[Ejecutor] Enroque {color} {tipo} realizado.")
        return True

    # --- Moved Helper Methods (now private) ---

    def _capturarPieza(self, pieza: Pieza) -> bool:
        """
        Añade una pieza a la lista de capturadas del tablero.
        (Formerly Tablero.capturarPieza)

        Args:
            pieza: La pieza a capturar.
        
        Returns:
            True si la pieza se añade correctamente (no es None), False en caso contrario.
        """
        if pieza is not None:
            self.tablero.piezasCapturadas.append(pieza)
            logger.info(f"[Ejecutor] Pieza capturada: {type(pieza).__name__} {pieza.color}")
            return True
        return False

    def _actualizarDerechosEnroque(self, pieza_movida: Pieza, posOrigen: Tuple[int, int], pieza_capturada: Optional[Pieza] = None, posDestino: Optional[Tuple[int, int]] = None):
        """
        Actualiza los derechos de enroque en el tablero.
        (Formerly Tablero.actualizarDerechosEnroque)
        """
        color_movido = pieza_movida.color

        # Casillas iniciales de las torres
        torre_blanca_larga, torre_blanca_corta = (0, 0), (0, 7)
        torre_negra_larga, torre_negra_corta = (7, 0), (7, 7)

        # 1. Si el REY se mueve, pierde AMBOS derechos de enroque
        if isinstance(pieza_movida, Rey):
            if self.tablero.derechosEnroque[color_movido]['corto']:
                self.tablero.derechosEnroque[color_movido]['corto'] = False
                logger.debug(f"[Ejecutor] Enroque corto perdido para {color_movido} (movimiento de rey)")
            if self.tablero.derechosEnroque[color_movido]['largo']:
                self.tablero.derechosEnroque[color_movido]['largo'] = False
                logger.debug(f"[Ejecutor] Enroque largo perdido para {color_movido} (movimiento de rey)")
            return

        # 2. Si una TORRE se mueve DESDE su casilla inicial, pierde el derecho de ESE LADO
        if isinstance(pieza_movida, Torre):
            if color_movido == 'blanco':
                if posOrigen == torre_blanca_corta and self.tablero.derechosEnroque['blanco']['corto']:
                    self.tablero.derechosEnroque['blanco']['corto'] = False
                    logger.debug("[Ejecutor] Enroque corto perdido para blanco (movimiento torre corta)")
                elif posOrigen == torre_blanca_larga and self.tablero.derechosEnroque['blanco']['largo']:
                    self.tablero.derechosEnroque['blanco']['largo'] = False
                    logger.debug("[Ejecutor] Enroque largo perdido para blanco (movimiento torre larga)")
            elif color_movido == 'negro':
                if posOrigen == torre_negra_corta and self.tablero.derechosEnroque['negro']['corto']:
                    self.tablero.derechosEnroque['negro']['corto'] = False
                    logger.debug("[Ejecutor] Enroque corto perdido para negro (movimiento torre corta)")
                elif posOrigen == torre_negra_larga and self.tablero.derechosEnroque['negro']['largo']:
                    self.tablero.derechosEnroque['negro']['largo'] = False
                    logger.debug("[Ejecutor] Enroque largo perdido para negro (movimiento torre larga)")

        # 3. Si una TORRE es CAPTURADA EN su casilla inicial, el OPONENTE pierde el derecho de ESE LADO
        if pieza_capturada is not None and isinstance(pieza_capturada, Torre) and posDestino is not None:
            color_capturada = pieza_capturada.color
            # Use self.tablero.derechosEnroque here
            if color_capturada == 'blanco':
                if posDestino == torre_blanca_corta and self.tablero.derechosEnroque['blanco']['corto']:
                    self.tablero.derechosEnroque['blanco']['corto'] = False
                    logger.debug("[Ejecutor] Enroque corto perdido para blanco (torre corta capturada)")
                elif posDestino == torre_blanca_larga and self.tablero.derechosEnroque['blanco']['largo']:
                    self.tablero.derechosEnroque['blanco']['largo'] = False
                    logger.debug("[Ejecutor] Enroque largo perdido para blanco (torre larga capturada)")
            elif color_capturada == 'negro':
                if posDestino == torre_negra_corta and self.tablero.derechosEnroque['negro']['corto']:
                    self.tablero.derechosEnroque['negro']['corto'] = False
                    logger.debug("[Ejecutor] Enroque corto perdido para negro (torre corta capturada)")
                elif posDestino == torre_negra_larga and self.tablero.derechosEnroque['negro']['largo']:
                    self.tablero.derechosEnroque['negro']['largo'] = False
                    logger.debug("[Ejecutor] Enroque largo perdido para negro (torre larga capturada)")

    def _actualizarPeonAlPaso(self, pieza_movida: Pieza, posOrigen: Tuple[int, int], posDestino: Tuple[int, int]):
        """
        Actualiza la casilla objetivo para captura al paso en el tablero.
        (Formerly Tablero.actualizarPeonAlPaso)
        """
        # Use self.tablero.objetivoPeonAlPaso
        self.tablero.objetivoPeonAlPaso = None 

        if isinstance(pieza_movida, Peon) and abs(posOrigen[0] - posDestino[0]) == 2:
            fila_objetivo = (posOrigen[0] + posDestino[0]) // 2
            columna_objetivo = posOrigen[1]
            self.tablero.objetivoPeonAlPaso = (fila_objetivo, columna_objetivo)
            logger.debug(f"[Ejecutor] Objetivo al paso actualizado a: {self.tablero.objetivoPeonAlPaso}")

    def _actualizarContadores(self, pieza_movida: Pieza, es_captura: bool):
        """
        Actualiza los contadores de ply, número de movimiento y regla de 50 movimientos en el tablero.
        (Formerly Tablero.actualizarContadores)
        """
        # Use self.tablero.* for counters
        self.tablero.contadorPly += 1

        # El número de movimiento incrementa después de que las negras muevan
        # This method is called BEFORE the turn is flipped in ejecutar_movimiento_normal
        # So, we increment if it was Black's turn (meaning Black just finished their move part)
        if not self.tablero.turno_blanco: 
            self.tablero.numero_movimiento += 1
            logger.debug(f"[Ejecutor] Número de movimiento incrementado a: {self.tablero.numero_movimiento}")

        # Resetear contador de 50 movimientos si fue un movimiento de peón o una captura
        if isinstance(pieza_movida, Peon) or es_captura:
            self.tablero.contadorRegla50Movimientos = 0
            logger.debug("[Ejecutor] Contador 50 movimientos reseteado.")
        else:
            self.tablero.contadorRegla50Movimientos += 1
            logger.debug(f"[Ejecutor] Contador 50 movimientos incrementado a: {self.tablero.contadorRegla50Movimientos}")
            
    def _actualizarUltimoMovimiento(self, posOrigen: Tuple[int, int], posDestino: Tuple[int, int]):
        """
        Almacena las coordenadas del último movimiento realizado en el tablero.
        (Formerly Tablero.actualizarUltimoMovimiento)
        """
        self.tablero.ultimo_movimiento = (posOrigen, posDestino)
        logger.debug(f"[Ejecutor] Último movimiento actualizado a: {posOrigen} -> {posDestino}")
