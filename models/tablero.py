"""
Representa el tablero de ajedrez y las posiciones de las piezas.
""" 
import logging
from typing import Dict, List, Tuple, Optional, Literal
from collections import defaultdict # Importar defaultdict

# Importar piezas
from models.piezas.pieza import Pieza
from models.piezas.torre import Torre
from models.piezas.caballo import Caballo
from models.piezas.alfil import Alfil
from models.piezas.reina import Reina
from models.piezas.rey import Rey
from models.piezas.peon import Peon

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Tablero:
    """
    Representa el tablero de ajedrez, incluyendo posiciones de piezas, piezas capturadas,
    derechos de enroque y objetivos de captura al paso.
    """
    # ============================================================
    # 1. Inicialización y Configuración del Tablero
    # ============================================================
    
    def __init__(self):
        """
        Inicializa el tablero con casillas vacías y el estado de juego por defecto
        (derechos de enroque, sin objetivo de captura al paso, lista de capturadas vacía),
        y luego coloca las piezas en sus posiciones iniciales.
        """
        # Tablero 8x8 inicializado con None (casillas vacías)
        self.casillas: List[List[Optional[Pieza]]] = [[None for _ in range(8)] for _ in range(8)]

        # Historial de movimientos (color, posOrigen, posDestino) - Podría necesitar enriquecerse para simulación perfecta
        self.historial_movimientos: List[Tuple[Literal['blanco', 'negro'], Tuple[int, int], Tuple[int, int]]] = []

        # Lista para almacenar las piezas capturadas
        self.piezasCapturadas: List[Pieza] = []

        # Seguimiento de los derechos de enroque
        self.derechosEnroque: Dict[str, Dict[str, bool]] = {
            'blanco': {'corto': True, 'largo': True}, # corto = flanco de rey (O-O), largo = flanco de dama (O-O-O)
            'negro': {'corto': True, 'largo': True}
        }

        # Casilla objetivo para captura al paso, formato (fila, columna) o None
        self.objetivoPeonAlPaso: Optional[Tuple[int, int]] = None

        # Turno del jugador
        self.turno_blanco: bool = True # True = turno del blanco, False = turno del negro

        # Contador para la regla de los 50 movimientos (se resetea con captura o mov. de peón)
        self.contadorRegla50Movimientos: int = 0

        # Contador de plies (medio movimiento). Empieza en 0 antes del primer movimiento.
        self.contadorPly: int = 0

        # Estado del juego (en curso, jaque, jaque mate, tablas, etc.)
        self.estado_juego: Literal['en_curso', 'jaque', 'jaque_mate', 'tablas'] = 'en_curso'

        # Número de movimiento completo (1 para el primer movimiento de blancas)
        self.numero_movimiento: int = 1

        # Información del último movimiento realizado (origen, destino)
        self.ultimo_movimiento: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None

        # Historial de posiciones para la regla de triple repetición
        # Clave: string de representación de posición (tipo FEN), Valor: contador de ocurrencias
        self.historial_posiciones: Dict[str, int] = defaultdict(int)

        # Inicializar el tablero con piezas
        self.inicializarTablero()

        # Registrar la posición inicial en el historial de repeticiones
        estado_inicial = self.obtenerPosicionActual()
        self.historial_posiciones[estado_inicial] = 1

    def inicializarTablero(self):
        """
        Coloca las piezas en sus posiciones iniciales estándar.
        Pasa la instancia actual del tablero ('self') al constructor de cada pieza.
        """
        # Blancas - Pasando 'self' (el tablero) al constructor de cada Pieza
        self.casillas[0] = [
            Torre('blanco', (0, 0), self), Caballo('blanco', (0, 1), self), Alfil('blanco', (0, 2), self),
            Reina('blanco', (0, 3), self), Rey('blanco', (0, 4), self), Alfil('blanco', (0, 5), self),
            Caballo('blanco', (0, 6), self), Torre('blanco', (0, 7), self)
        ]
        self.casillas[1] = [
            Peon('blanco', (1, 0), self), Peon('blanco', (1, 1), self), Peon('blanco', (1, 2), self),
            Peon('blanco', (1, 3), self), Peon('blanco', (1, 4), self), Peon('blanco', (1, 5), self),
            Peon('blanco', (1, 6), self), Peon('blanco', (1, 7), self)
        ]

        # Negras - Pasando 'self' (el tablero) al constructor de cada Pieza
        self.casillas[6] = [
            Peon('negro', (6, 0), self), Peon('negro', (6, 1), self), Peon('negro', (6, 2), self),
            Peon('negro', (6, 3), self), Peon('negro', (6, 4), self), Peon('negro', (6, 5), self),
            Peon('negro', (6, 6), self), Peon('negro', (6, 7), self)
        ]
        self.casillas[7] = [
            Torre('negro', (7, 0), self), Caballo('negro', (7, 1), self), Alfil('negro', (7, 2), self),
            Reina('negro', (7, 3), self), Rey('negro', (7, 4), self), Alfil('negro', (7, 5), self),
            Caballo('negro', (7, 6), self), Torre('negro', (7, 7), self)
        ]

    # ============================================================
    # 2. Consulta del Tablero y Validación Básica
    # ============================================================

    def esPosicionValida(self, posicion: Tuple[int, int]) -> bool:
        """
        Verifica si una posición (tupla) es válida dentro de los límites del tablero.
        
        Args:
            posicion: Una tupla (fila, columna) indicando la casilla.
        """
        # Asegurarse de que posicion es realmente una tupla de dos enteros
        if not (isinstance(posicion, tuple) and len(posicion) == 2 and
                isinstance(posicion[0], int) and isinstance(posicion[1], int)):
            return False
        fila, columna = posicion
        return 0 <= fila <= 7 and 0 <= columna <= 7

    def getPieza(self, posicion: Tuple[int, int]) -> Optional[Pieza]:
        """
        Obtiene la pieza en una posición específica del tablero.

        Args:
            posicion: Una tupla (fila, columna) indicando la casilla.

        Returns:
            La pieza en la posición especificada o None si no hay una pieza en esa posición
            o si la posición es inválida.
        """
        if not self.esPosicionValida(posicion):
            return None
        fila, columna = posicion
        return self.casillas[fila][columna]
    
    def esBlanco(self, posicion: Tuple[int, int]) -> bool:
        """
        Verifica si una pieza en una posición dada es blanca.
        
        Args:
            posicion: Una tupla (fila, columna) indicando la casilla.

        Returns:
            True si la pieza es blanca, False en caso contrario o si la casilla está vacía.
        """
        pieza = self.getPieza(posicion)
        return pieza is not None and pieza.color == 'blanco'
    
    # ============================================================
    # 3. Ejecución Central del Movimiento
    # ============================================================

    def moverPieza(self, posOrigen: Tuple[int, int], posDestino: Tuple[int, int]) -> Literal['movimiento_ok', 'promocion_necesaria', 'error']:
        """
        Intenta mover una pieza desde una posición a otra. Realiza las siguientes acciones:
        1. Validaciones básicas (posiciones válidas, pieza en origen, no captura propia).
        2. Gestiona la captura normal o la captura especial 'al paso'.
        3. Mueve la pieza en el tablero (`self.casillas`).
        4. Añade el movimiento al historial.
        5. Actualiza la posición interna de la pieza (`pieza.posicion`).
        6. Llama a los métodos para actualizar el estado del juego (enroque, peón al paso, contadores, etc.).
        7. Detecta si se requiere una promoción de peón.
        8. Cambia el turno.
        9. Actualiza el historial de posiciones DESPUÉS de cambiar el turno
        
        NOTA: 
         - Esta función NO valida la legalidad completa del movimiento 
           (p. ej., no comprueba si el movimiento sigue las reglas de la pieza 
           o si deja al rey en jaque). Esa validación debe ocurrir ANTES de llamar a este método.
         - NO maneja el movimiento de enroque, para eso usar `realizarEnroque`.

        Args:
            posOrigen: Tupla (fila, columna) de la casilla origen.
            posDestino: Tupla (fila, columna) de la casilla destino.

        Returns:
            - 'movimiento_ok': El movimiento se realizó con éxito.
            - 'promocion_necesaria': El movimiento fue un avance de peón a la última fila y requiere promoción.
            - 'error': Hubo un problema con las validaciones básicas (p.ej., origen vacío, destino inválido).
        """
        # 1. Validar posiciones y pieza en origen
        if not self.esPosicionValida(posOrigen) or not self.esPosicionValida(posDestino):
            logger.error(f"Posición origen {posOrigen} o destino {posDestino} inválida.")
            return 'error'
        pieza_movida = self.getPieza(posOrigen)
        if pieza_movida is None:
            logger.error(f"No hay pieza en la posición origen {posOrigen}.")
            return 'error'

        # Determinar si es captura y si es en passant
        pieza_capturada = self.getPieza(posDestino)
        es_captura = False
        es_en_passant = False
        casilla_captura_ep = None # Casilla donde estaba el peón capturado al paso

        # Comprobar si es un movimiento de peón al destino objetivo de 'al paso'
        if isinstance(pieza_movida, Peon) and posDestino == self.objetivoPeonAlPaso:
            es_captura = True
            es_en_passant = True
            # El peón capturado está en la misma columna que el destino,
            # pero en la fila de origen del peón que se mueve
            fila_capturada = posOrigen[0]
            col_capturada = posDestino[1]
            casilla_captura_ep = (fila_capturada, col_capturada)
            pieza_capturada_ep = self.getPieza(casilla_captura_ep)
            if pieza_capturada_ep is None or pieza_capturada_ep.color == pieza_movida.color:
                logger.error(f"Intento de captura al paso inválida en {posDestino} (sin peón o peón propio en {casilla_captura_ep})")
                return 'error'
            self.capturarPieza(pieza_capturada_ep)
            self.setPieza(casilla_captura_ep, None)
            logger.debug(f"Captura al paso realizada. Peón capturado en {casilla_captura_ep}")

        # 2. Gestionar captura normal (si no fue al paso)
        elif pieza_capturada is not None:
            if pieza_capturada.color == pieza_movida.color:
                logger.error(f"Intento de captura de pieza propia en {posDestino}.")
                return 'error'
            self.capturarPieza(pieza_capturada)
            es_captura = True

        # 3. Mover la pieza en el tablero
        self.setPieza(posDestino, pieza_movida)
        self.setPieza(posOrigen, None)

        # 4. Añadir al historial
        # TODO: Considerar añadir información extra al historial para en passant/promoción si es necesario para FEN o PGN.
        color_jugador = pieza_movida.color
        self.historial_movimientos.append((color_jugador, posOrigen, posDestino))

        # 5. Actualizar posición interna de la pieza
        if hasattr(pieza_movida, 'posicion'):
             pieza_movida.posicion = posDestino
             if hasattr(pieza_movida, 'se_ha_movido'):
                 pieza_movida.se_ha_movido = True
        else:
             logger.warning(f"La pieza {type(pieza_movida).__name__} movida a {posDestino} no tiene atributo 'posicion' para actualizar.")

        # 6. Actualizar estado del juego post-movimiento (excepto turno)
        # Se actualizan derechos de enroque *después* de mover la pieza y registrar captura.
        self.actualizarDerechosEnroque(pieza_movida, posOrigen, pieza_capturada, posDestino)
        # El objetivo al paso se actualiza DESPUÉS de los derechos de enroque
        self.actualizarPeonAlPaso(pieza_movida, posOrigen, posDestino)
        self.actualizarContadores(pieza_movida, es_captura)
        self.actualizarUltimoMovimiento(posOrigen, posDestino)

        # 7. Detectar promoción de peón
        es_promocion = False
        if isinstance(pieza_movida, Peon):
            fila_destino = posDestino[0]
            if (pieza_movida.color == 'blanco' and fila_destino == 7) or \
               (pieza_movida.color == 'negro' and fila_destino == 0):
                es_promocion = True
                logger.debug(f"Promoción necesaria en {posDestino}")

        # 8. Cambiar turno
        self.turno_blanco = not self.turno_blanco

        # 9. Actualizar historial de posiciones DESPUÉS de cambiar el turno
        estado_actual = self.obtenerPosicionActual()
        self.historial_posiciones[estado_actual] += 1
        logger.debug(f"Historial posiciones actualizado. Estado: '{estado_actual}', Count: {self.historial_posiciones[estado_actual]}")

        # 10. Actualizar estado del juego AHORA, después del cambio de turno (NUEVO LUGAR)
        self.actualizarEstadoJuego()

        # Retornar estado
        if es_promocion:
            return 'promocion_necesaria'
        else:
            return 'movimiento_ok'

    def capturarPieza(self, pieza: Pieza) -> bool:
        """
        Añade una pieza a la lista de capturadas.
        Es llamada por `moverPieza`.

        Args:
            pieza: La pieza a capturar.
        
        Returns:
            True si la pieza se añade correctamente (no es None), False en caso contrario.
        """
        if pieza is not None:
            self.piezasCapturadas.append(pieza)
            logger.info(f"Pieza capturada: {type(pieza).__name__} {pieza.color}") # Registrar info
            return True
        return False

    def setPieza(self, posicion: Tuple[int, int], pieza: Optional[Pieza]):
        """
        Establece una pieza (o None) en una posición específica del tablero.
        Es un método auxiliar para `moverPieza` y `inicializarTablero`. No valida la posición.

        Args:
            posicion: Una tupla (fila, columna) indicando la casilla.
            pieza: La pieza a establecer, o None para vaciar la casilla.
        """
        fila, columna = posicion
        self.casillas[fila][columna] = pieza
    
    def realizarEnroque(self, color: Literal['blanco', 'negro'], tipo: Literal['corto', 'largo']) -> bool:
        """
        Realiza el movimiento de enroque (Rey y Torre) asumiendo que ya ha sido validado.
        Actualiza las posiciones en el tablero, el historial y el estado general del juego.

        Args:
            color: El color del jugador que enroca ('blanco' o 'negro').
            tipo: El tipo de enroque ('corto' para flanco de rey, 'largo' para flanco de dama).

        Returns:
            True si el enroque se realizó con éxito (según los parámetros), False si hubo un error inesperado.
        """
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
        rey = self.getPieza(rey_pos_origen)
        torre = self.getPieza(torre_pos_origen)
        
        if not isinstance(rey, Rey) or not isinstance(torre, Torre):
            logger.error(f"Piezas incorrectas en {rey_pos_origen} o {torre_pos_origen} para enroque {color} {tipo}.")
            return False
        
        # Mover las piezas en el tablero
        self.setPieza(rey_pos_destino, rey)
        self.setPieza(rey_pos_origen, None)
        self.setPieza(torre_pos_destino, torre)
        self.setPieza(torre_pos_origen, None)
        
        # Actualizar posición interna de las piezas
        if hasattr(rey, 'posicion'): rey.posicion = rey_pos_destino
        if hasattr(torre, 'posicion'): torre.posicion = torre_pos_destino
        if hasattr(rey, 'se_ha_movido'): rey.se_ha_movido = True
        if hasattr(torre, 'se_ha_movido'): torre.se_ha_movido = True
        
        # Añadir al historial (puede requerir formato especial para PGN/FEN)
        # Por ahora, añadimos un registro simple indicando enroque
        # ¿O podríamos añadir los dos movimientos individuales? Mejor uno conceptual.
        self.historial_movimientos.append((color, rey_pos_origen, rey_pos_destino)) # Registramos el mov del rey como representativo
        
        # Actualizar estado: derechos de enroque se pierden, contadores avanzan, etc.
        # El rey se movió, así que pierde ambos derechos
        self.derechosEnroque[color]['corto'] = False
        self.derechosEnroque[color]['largo'] = False
        # Actualizar Peón al Paso (se limpia porque no fue mov de peón)
        self.objetivoPeonAlPaso = None 
        # Actualizar Contadores (enroque no es captura ni mov de peón)
        self.actualizarContadores(rey, False) # Usamos el rey como pieza movida
        # Actualizar Último Movimiento (registramos el del rey)
        self.actualizarUltimoMovimiento(rey_pos_origen, rey_pos_destino)
        # Actualizar Estado del Juego
        self.actualizarEstadoJuego()
        
        # Cambiar turno
        self.turno_blanco = not self.turno_blanco
        
        # 9. Actualizar historial de posiciones DESPUÉS de cambiar el turno
        estado_actual = self.obtenerPosicionActual()
        self.historial_posiciones[estado_actual] += 1
        logger.debug(f"Historial posiciones actualizado (enroque). Estado: '{estado_actual}', Count: {self.historial_posiciones[estado_actual]}")
        
        logger.info(f"Enroque {color} {tipo} realizado.")
        return True
    
    # ============================================================
    # 4. Evaluación de Amenazas
    # ============================================================

    def esCasillaAmenazada(self, posicion: Tuple[int, int], color_atacante: Literal['blanco', 'negro']) -> bool:
        """
        Verifica si una posición es amenazada por alguna pieza del color especificado.
        Implementa la lógica de línea de visión y bloqueo para piezas deslizantes,
        y movimientos específicos para peones, caballos y reyes.
        Es crucial para la detección de jaque.

        Args:
            posicion: Tupla (fila, columna) de la casilla a verificar.
            color_atacante: El color de las piezas que podrían estar atacando.
        
        Returns:
            True si la posición es amenazada, False en caso contrario.
        """
        target_f, target_c = posicion
        if not self.esPosicionValida(posicion):
            return False

        for r in range(8):
            for c in range(8):
                pieza = self.casillas[r][c]
                if pieza is None or pieza.color != color_atacante:
                    continue

                attacker_f, attacker_c = pieza.posicion

                # --- 1. Comprobación de Peón ---
                if isinstance(pieza, Peon):
                    direccion = 1 if pieza.color == 'blanco' else -1
                    # El peón amenaza las casillas diagonales en frente
                    if target_f == attacker_f + direccion:
                        if target_c == attacker_c + 1 or target_c == attacker_c - 1:
                            return True
                    continue # Si es peón, no hace falta más chequeo

                # --- 2. Comprobación de Caballo ---
                if isinstance(pieza, Caballo):
                    # El caballo amenaza si la diferencia absoluta de filas/cols es (1,2) o (2,1)
                    df = abs(target_f - attacker_f)
                    dc = abs(target_c - attacker_c)
                    if (df == 1 and dc == 2) or (df == 2 and dc == 1):
                        return True
                    continue # Si es caballo, no hace falta más chequeo

                # --- 3. Comprobación de Rey ---
                if isinstance(pieza, Rey):
                    # El rey amenaza las casillas adyacentes
                    if abs(target_f - attacker_f) <= 1 and abs(target_c - attacker_c) <= 1:
                        # No puede ser la misma casilla (abs(df) + abs(dc) > 0)
                        if (target_f, target_c) != (attacker_f, attacker_c): 
                           return True
                    continue # Si es rey, no hace falta más chequeo

                # --- 4. Comprobación de Piezas Deslizantes (Torre, Alfil, Reina) ---
                is_sliding = isinstance(pieza, (Torre, Alfil, Reina))
                if not is_sliding:
                    continue # Si no es ninguna de las anteriores, algo raro pasa, pasar a la siguiente

                # Verificar si la pieza puede atacar en línea recta o diagonal
                can_attack_rank_file = isinstance(pieza, (Torre, Reina))
                can_attack_diagonal = isinstance(pieza, (Alfil, Reina))

                df = target_f - attacker_f
                dc = target_c - attacker_c
                on_line = False
                step_f, step_c = 0, 0

                # ¿Está en la misma fila o columna? (Ataque de Torre/Reina)
                if can_attack_rank_file and (df == 0 or dc == 0) and (df != 0 or dc != 0):
                    on_line = True
                    step_f = 0 if df == 0 else (1 if df > 0 else -1)
                    step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
                # ¿Está en la misma diagonal? (Ataque de Alfil/Reina)
                elif can_attack_diagonal and abs(df) == abs(dc) and df != 0:
                    on_line = True
                    step_f = 1 if df > 0 else -1
                    step_c = 1 if dc > 0 else -1
                
                # Si no está en una línea de ataque válida para esta pieza, continuar
                if not on_line:
                    continue
                
                # Ahora, verificar si el camino está libre HASTA la casilla objetivo
                path_clear = True
                check_f, check_c = attacker_f + step_f, attacker_c + step_c
                while (check_f, check_c) != posicion:
                    # Si salimos del tablero en el camino, algo es raro, pero el camino está 'libre' en ese sentido
                    if not self.esPosicionValida((check_f, check_c)):
                        # Esto no debería ocurrir si target_pos es válido y on_line es True
                        logger.warning(f"[Threat Check Path] Path check went out of bounds from {(attacker_f, attacker_c)} to {posicion}")
                        path_clear = False # Considerarlo bloqueado por seguridad
                        break
                    # Si encontramos CUALQUIER pieza en el camino, está bloqueado
                    blocking_piece = self.getPieza((check_f, check_c))
                    if blocking_piece is not None:
                        path_clear = False
                        break
                    # Avanzar al siguiente paso
                    check_f += step_f
                    check_c += step_c
                
                # Si el camino estaba libre, la pieza amenaza la posición
                if path_clear:
                    return True

        # Si ninguna pieza amenaza la posición tras revisar todas
        return False

    # ============================================================
    # 5. Actualización del Estado del Juego (Post-Movimiento)
    # ============================================================
    
    def getTurnoColor(self) -> Literal['blanco', 'negro']:
        """
        Devuelve el color del jugador cuyo turno es.
        """
        return 'blanco' if self.turno_blanco else 'negro'
    
    def actualizarDerechosEnroque(self, pieza_movida: Pieza, posOrigen: Tuple[int, int], pieza_capturada: Optional[Pieza] = None, posDestino: Optional[Tuple[int, int]] = None):
        """
        Actualiza los derechos de enroque si se mueve el rey o una torre desde su posición inicial,
        o si una torre es capturada en su posición inicial.
        Llamado por `moverPieza`.

        Args:
            pieza_movida: La pieza que se acaba de mover.
            posOrigen: La posición original de la pieza movida.
            pieza_capturada: La pieza capturada en el movimiento (si la hay).
            posDestino: La posición destino del movimiento (usada para detectar captura de torre).
        """
        color_movido = pieza_movida.color

        # Casillas iniciales de las torres
        torre_blanca_larga, torre_blanca_corta = (0, 0), (0, 7)
        torre_negra_larga, torre_negra_corta = (7, 0), (7, 7)

        # 1. Si el REY se mueve, pierde AMBOS derechos de enroque
        if isinstance(pieza_movida, Rey):
            if self.derechosEnroque[color_movido]['corto']:
                self.derechosEnroque[color_movido]['corto'] = False
                logger.debug(f"Enroque corto perdido para {color_movido} (movimiento de rey)")
            if self.derechosEnroque[color_movido]['largo']:
                self.derechosEnroque[color_movido]['largo'] = False
                logger.debug(f"Enroque largo perdido para {color_movido} (movimiento de rey)")
            # No necesitamos hacer más si el rey se movió
            return

        # 2. Si una TORRE se mueve DESDE su casilla inicial, pierde el derecho de ESE LADO
        if isinstance(pieza_movida, Torre):
            if color_movido == 'blanco':
                if posOrigen == torre_blanca_corta and self.derechosEnroque['blanco']['corto']:
                    self.derechosEnroque['blanco']['corto'] = False
                    logger.debug("Enroque corto perdido para blanco (movimiento torre corta)")
                elif posOrigen == torre_blanca_larga and self.derechosEnroque['blanco']['largo']:
                    self.derechosEnroque['blanco']['largo'] = False
                    logger.debug("Enroque largo perdido para blanco (movimiento torre larga)")
            elif color_movido == 'negro':
                if posOrigen == torre_negra_corta and self.derechosEnroque['negro']['corto']:
                    self.derechosEnroque['negro']['corto'] = False
                    logger.debug("Enroque corto perdido para negro (movimiento torre corta)")
                elif posOrigen == torre_negra_larga and self.derechosEnroque['negro']['largo']:
                    self.derechosEnroque['negro']['largo'] = False
                    logger.debug("Enroque largo perdido para negro (movimiento torre larga)")

        # 3. Si una TORRE es CAPTURADA EN su casilla inicial, el OPONENTE pierde el derecho de ESE LADO
        # Nota: Se usa posDestino porque es la casilla donde estaba la torre *antes* de ser capturada.
        if pieza_capturada is not None and isinstance(pieza_capturada, Torre) and posDestino is not None:
            color_capturada = pieza_capturada.color
            if color_capturada == 'blanco':
                if posDestino == torre_blanca_corta and self.derechosEnroque['blanco']['corto']: # Torre blanca corta fue capturada
                    self.derechosEnroque['blanco']['corto'] = False
                    logger.debug("Enroque corto perdido para blanco (torre corta capturada)")
                elif posDestino == torre_blanca_larga and self.derechosEnroque['blanco']['largo']: # Torre blanca larga fue capturada
                    self.derechosEnroque['blanco']['largo'] = False
                    logger.debug("Enroque largo perdido para blanco (torre larga capturada)")
            elif color_capturada == 'negro':
                if posDestino == torre_negra_corta and self.derechosEnroque['negro']['corto']: # Torre negra corta fue capturada
                    self.derechosEnroque['negro']['corto'] = False
                    logger.debug("Enroque corto perdido para negro (torre corta capturada)")
                elif posDestino == torre_negra_larga and self.derechosEnroque['negro']['largo']: # Torre negra larga fue capturada
                    self.derechosEnroque['negro']['largo'] = False
                    logger.debug("Enroque largo perdido para negro (torre larga capturada)")

    def actualizarPeonAlPaso(self, pieza_movida: Pieza, posOrigen: Tuple[int, int], posDestino: Tuple[int, int]):
        """
        Actualiza la casilla objetivo para captura al paso si un peón avanza dos casillas.
        Limpia el objetivo en cualquier otro movimiento. Llamado por `moverPieza`.

        Args:
            pieza_movida: La pieza que se acaba de mover.
            posOrigen: La posición original de la pieza movida.
            posDestino: La posición final de la pieza movida.
        """
        self.objetivoPeonAlPaso = None 

        if isinstance(pieza_movida, Peon) and abs(posOrigen[0] - posDestino[0]) == 2:
            fila_objetivo = (posOrigen[0] + posDestino[0]) // 2
            columna_objetivo = posOrigen[1]
            self.objetivoPeonAlPaso = (fila_objetivo, columna_objetivo)

    def actualizarContadores(self, pieza_movida: Pieza, es_captura: bool):
        """
        Actualiza el contador de ply, el número de movimiento y el contador de la regla de 50 movimientos.
        Llamado por `moverPieza`.

        Args:
            pieza_movida: La pieza que se acaba de mover.
            es_captura: True si el movimiento fue una captura, False en caso contrario.
        """
        self.contadorPly += 1

        # El número de movimiento incrementa después de que las negras muevan
        if not self.turno_blanco: # Si turno_blanco es False, las negras ACABAN de mover
            self.numero_movimiento += 1

        # Resetear contador de 50 movimientos si fue un movimiento de peón o una captura
        if isinstance(pieza_movida, Peon) or es_captura:
            self.contadorRegla50Movimientos = 0
        else:
            self.contadorRegla50Movimientos += 1
            
    def actualizarUltimoMovimiento(self, posOrigen: Tuple[int, int], posDestino: Tuple[int, int]):
        """
        Almacena las coordenadas del último movimiento realizado. Llamado por `moverPieza`.
        """
        self.ultimo_movimiento = (posOrigen, posDestino)

    def actualizarEstadoJuego(self):
        """
        Evalúa el estado actual del juego (en curso, jaque, jaque mate, tablas).
        Llamado por `moverPieza` y `realizarEnroque`.
        Depende de `esCasillaAmenazada` y `esTripleRepeticion`.
        
        NOTA:
         - Verifica jaque y tablas por 50 mov/repetición/material insuficiente.
         - NO implementa chequeo completo de mate/ahogado, ya que requiere la 
           generación de TODOS los movimientos legales para el jugador actual, 
           lo cual es responsabilidad de una capa superior (Controlador/Validador).
        """
        color_jugador_actual = self.getTurnoColor() # Color del jugador QUE VA A MOVER AHORA
        color_oponente = 'negro' if color_jugador_actual == 'blanco' else 'blanco'
        
        # Encontrar el rey del jugador actual
        rey_pos = None
        for r, fila in enumerate(self.casillas):
            for c, pieza in enumerate(fila):
                if isinstance(pieza, Rey) and pieza.color == color_jugador_actual:
                    rey_pos = (r, c)
                    break
            if rey_pos: break

        if rey_pos is None:
             logger.critical(f"No se encontró el rey {color_jugador_actual}. Estado del juego no actualizado.") # Usar critical para errores graves
             return

        # 1. Comprobar condiciones de Tablas (que no dependen de movimientos legales)
        if self.contadorRegla50Movimientos >= 100: # Son 50 movimientos completos, 100 plies
            self.estado_juego = 'tablas'
            logger.info("Tablas por regla de 50 movimientos.")
            return
        if self.esTripleRepeticion():
            self.estado_juego = 'tablas'
            logger.info("Tablas por triple repetición.")
            return
        # Añadir chequeo de material insuficiente para tablas
        if self.esMaterialInsuficiente():
            self.estado_juego = 'tablas'
            logger.info("Tablas por material insuficiente.")
            return

        # 2. Comprobar Jaque (evaluando si el rey actual está amenazado)
        esta_en_jaque = self.esCasillaAmenazada(rey_pos, color_oponente)

        # 3. Determinar estado final (Mate/Ahogado - REQUIERE MOVIMIENTOS LEGALES)
        movimientos_legales = self.obtener_todos_movimientos_legales(color_jugador_actual)

        if not movimientos_legales: # No hay movimientos legales
           if esta_en_jaque:
               self.estado_juego = 'jaque_mate'
               logger.info(f"Jaque Mate a {color_jugador_actual}.")
           else:
               self.estado_juego = 'tablas' # Ahogado
               logger.info(f"Tablas por ahogado a {color_jugador_actual}.")
           return

        # 4. Si hay movimientos legales (o no hemos comprobado aún), actualizar estado básico
        if esta_en_jaque:
            self.estado_juego = 'jaque'
        else:
            self.estado_juego = 'en_curso'

    def esMaterialInsuficiente(self) -> bool:
        """
        Comprueba si hay material insuficiente en el tablero para forzar un jaque mate.
        Cubre los casos más comunes definidos por la FIDE (Artículo 5.2.f / 9.6).

        Returns:
            True si el material es insuficiente para mate, False en caso contrario.
        """
        piezas_blancas = []
        piezas_negras = []
        alfiles_blancos_casilla_clara = 0
        alfiles_blancos_casilla_oscura = 0
        alfiles_negros_casilla_clara = 0
        alfiles_negros_casilla_oscura = 0

        # Contar piezas (excluyendo reyes) y características de alfiles
        for r in range(8):
            for c in range(8):
                pieza = self.casillas[r][c]
                if pieza is not None and not isinstance(pieza, Rey):
                    tipo_pieza = type(pieza)
                    # Si encontramos una Reina o una Torre o un Peón, el material SIEMPRE es suficiente
                    if tipo_pieza == Reina or tipo_pieza == Torre or tipo_pieza == Peon:
                        return False # Mate es posible

                    if pieza.color == 'blanco':
                        piezas_blancas.append(tipo_pieza)
                        if isinstance(pieza, Alfil):
                            # (0,0) es oscura en la config estándar. (r+c)%2==0 es oscura.
                            if (r + c) % 2 == 0:
                                alfiles_blancos_casilla_oscura += 1
                            else:
                                alfiles_blancos_casilla_clara += 1
                        # Guardar si hay caballos (podríamos solo contar)
                        # elif isinstance(pieza, Caballo): pass
                    else: # Negro
                        piezas_negras.append(tipo_pieza)
                        if isinstance(pieza, Alfil):
                            if (r + c) % 2 == 0:
                                alfiles_negros_casilla_oscura += 1
                            else:
                                alfiles_negros_casilla_clara += 1
                        # elif isinstance(pieza, Caballo): pass

        num_piezas_blancas = len(piezas_blancas)
        num_piezas_negras = len(piezas_negras)

        # Caso 1: Rey vs Rey (ambas listas vacías)
        if num_piezas_blancas == 0 and num_piezas_negras == 0:
            logger.debug("Material insuficiente: K vs K")
            return True

        # Caso 2: Rey + Caballo vs Rey
        if (num_piezas_blancas == 1 and piezas_blancas[0] == Caballo and num_piezas_negras == 0) or \
           (num_piezas_negras == 1 and piezas_negras[0] == Caballo and num_piezas_blancas == 0):
            logger.debug("Material insuficiente: K+N vs K")
            return True

        # Caso 3: Rey + Alfil vs Rey
        if (num_piezas_blancas == 1 and piezas_blancas[0] == Alfil and num_piezas_negras == 0) or \
           (num_piezas_negras == 1 and piezas_negras[0] == Alfil and num_piezas_blancas == 0):
            logger.debug("Material insuficiente: K+B vs K")
            return True

        # Caso 4: Rey + Alfil vs Rey + Alfil (ambos alfiles en casillas del mismo color)
        if num_piezas_blancas == 1 and piezas_blancas[0] == Alfil and \
           num_piezas_negras == 1 and piezas_negras[0] == Alfil:
            # Comprobar si ambos están en claras o ambos en oscuras
            ambos_en_claras = alfiles_blancos_casilla_clara == 1 and alfiles_negros_casilla_clara == 1
            ambos_en_oscuras = alfiles_blancos_casilla_oscura == 1 and alfiles_negros_casilla_oscura == 1
            if ambos_en_claras or ambos_en_oscuras:
                 logger.debug("Material insuficiente: K+B vs K+B (mismo color)")
                 return True

        # NOTA: K+N+N vs K NO se considera insuficiente por las reglas FIDE, aunque
        # forzar mate es extremadamente difícil y raro. Esta función correctamente devuelve False.
        # Otros casos más complejos (p.ej., finales con peones bloqueados que no pueden avanzar)
        # no se cubren aquí y generalmente se resuelven por la regla de 50 mov o triple repetición.

        return False

    # ==================================================================
    # 5.5 Simulación y Verificación de Seguridad del Rey (NUEVO)
    # ==================================================================

    def _simular_y_verificar_seguridad(self, pieza: Pieza, destino: Tuple[int, int]) -> bool:
        """
        Simula un movimiento, verifica si el rey del jugador queda en jaque y deshace la simulación.
        ¡Precaución! Este método modifica y restaura el estado del tablero temporalmente.

        Args:
            pieza: La pieza que se intenta mover.
            destino: La casilla destino del movimiento simulado.

        Returns:
            True si el rey NO queda en jaque después del movimiento simulado, False en caso contrario.
        """
        origen = pieza.posicion
        color_jugador = pieza.color
        color_oponente = 'negro' if color_jugador == 'blanco' else 'blanco'

        # --- Almacenar estado original ---        
        pieza_capturada_temporal = self.getPieza(destino)
        objetivo_ep_original = self.objetivoPeonAlPaso
        derechos_enroque_original = { 
            'blanco': self.derechosEnroque['blanco'].copy(),
            'negro': self.derechosEnroque['negro'].copy()
        }
        pieza_se_ha_movido_original = pieza.se_ha_movido
        torre_capturada_se_ha_movido_original = None
        if pieza_capturada_temporal is not None and isinstance(pieza_capturada_temporal, Torre):
             torre_capturada_se_ha_movido_original = pieza_capturada_temporal.se_ha_movido

        # --- Simular el movimiento --- 
        pieza_capturada_ep_real = None 
        casilla_peon_capturado_ep = None
        if isinstance(pieza, Peon) and destino == self.objetivoPeonAlPaso:
            fila_captura_ep = origen[0]
            col_captura_ep = destino[1]
            casilla_peon_capturado_ep = (fila_captura_ep, col_captura_ep)
            pieza_capturada_ep_real = self.getPieza(casilla_peon_capturado_ep)
            if pieza_capturada_ep_real: # Solo si realmente hay algo que capturar al paso
                self.setPieza(casilla_peon_capturado_ep, None) 
        
        self.setPieza(destino, pieza)
        self.setPieza(origen, None)
        pieza.posicion = destino 
        if hasattr(pieza, 'se_ha_movido'): # Asegurar que la pieza tiene el atributo
            pieza.se_ha_movido = True 
        
        # Actualizar derechos y EP temporalmente (simplificado)
        self.actualizarDerechosEnroque(pieza, origen, pieza_capturada_temporal, destino)
        self.actualizarPeonAlPaso(pieza, origen, destino)

        # --- Verificar seguridad del rey --- 
        rey_pos = None
        for r, fila in enumerate(self.casillas):
            for c, p_actual in enumerate(fila):
                if isinstance(p_actual, Rey) and p_actual.color == color_jugador:
                    rey_pos = (r, c)
                    break
            if rey_pos: break

        es_seguro = False
        if rey_pos is None:
             logger.critical(f"SIMULACIÓN: Rey {color_jugador} no encontrado.")
        else:
             es_seguro = not self.esCasillaAmenazada(rey_pos, color_oponente)

        # --- Deshacer la simulación ---
        if hasattr(pieza, 'se_ha_movido'):
            pieza.se_ha_movido = pieza_se_ha_movido_original 
        pieza.posicion = origen 
        self.setPieza(origen, pieza)
        self.setPieza(destino, pieza_capturada_temporal)
        if casilla_peon_capturado_ep and pieza_capturada_ep_real:
            self.setPieza(casilla_peon_capturado_ep, pieza_capturada_ep_real) 

        self.objetivoPeonAlPaso = objetivo_ep_original
        self.derechosEnroque = derechos_enroque_original 
        if pieza_capturada_temporal is not None and isinstance(pieza_capturada_temporal, Torre) and torre_capturada_se_ha_movido_original is not None:
            pieza_capturada_temporal.se_ha_movido = torre_capturada_se_ha_movido_original

        return es_seguro

    # ============================================================ 
    # 6. Representación de Posición y Chequeo de Repetición (Auxiliares)
    # ============================================================

    def obtenerPosicionActual(self) -> str:
        """
        Obtiene una representación en texto única de la posición actual del tablero,
        derechos de enroque, turno y objetivo de peón al paso.
        Necesario para el chequeo de triple repetición. Utiliza un formato FEN estándar.
        NOTA: Depende de `obtenerNotacionFEN` en las clases de Pieza para la parte de piezas.

        Returns:
            String representando unívocamente el estado relevante para repetición (Formato FEN).
        """
        posicion_piezas = []
        # Iterar desde la fila 8 (índice 7) hasta la 1 (índice 0) para FEN
        for fila_idx in range(7, -1, -1):
            fila_str = ""
            empty_count = 0
            for col_idx in range(8):
                pieza = self.casillas[fila_idx][col_idx]
                if pieza is None:
                    empty_count += 1
                else:
                    # Si había casillas vacías antes, añadir el número
                    if empty_count > 0:
                        fila_str += str(empty_count)
                        empty_count = 0
                    # Añadir la letra de la pieza
                    try:
                        letra = pieza.obtenerNotacionFEN()
                        fila_str += letra.upper() if pieza.color == 'blanco' else letra.lower()
                    except AttributeError:
                        logger.warning(f"{type(pieza).__name__} no tiene 'obtenerNotacionFEN'. Usando '?'.")
                        fila_str += "?"
            # Si la fila termina con casillas vacías, añadir el número
            if empty_count > 0:
                fila_str += str(empty_count)
            posicion_piezas.append(fila_str)
        piezas_str = "/".join(posicion_piezas) # Separador de filas estilo FEN
        
        # --- Resto del estado FEN (Turno, Enroque, Al Paso) ---
        # Turno
        turno_str = "w" if self.turno_blanco else "b"
        # Derechos de enroque
        enroque_str = ""
        if self.derechosEnroque['blanco']['corto']: enroque_str += "K"
        if self.derechosEnroque['blanco']['largo']: enroque_str += "Q"
        if self.derechosEnroque['negro']['corto']: enroque_str += "k"
        if self.derechosEnroque['negro']['largo']: enroque_str += "q"
        enroque_str = enroque_str if enroque_str else "-"
        # Objetivo peón al paso (en notación algebraica p.ej., e3)
        al_paso_str = "-"
        if self.objetivoPeonAlPaso:
            fila, col = self.objetivoPeonAlPaso
            # Convertir (fila, col) a notación algebraica (p.ej., (2, 4) -> e3)
            try:
                col_letra = chr(ord('a') + col)
                fila_num_fen = str(fila + 1) # Fila FEN es 1-indexada
                al_paso_str = col_letra + fila_num_fen
            except Exception as e: 
                al_paso_str = "?" # Error en conversión
                logger.error(f"Error convirtiendo objetivo al paso {self.objetivoPeonAlPaso} a notación algebraica: {e}")

        # Combinar todo en una cadena única (ignora contadores de 50-mov y ply por defecto FEN)
        # Formato: piezas turno enroque al_paso
        return f"{piezas_str} {turno_str} {enroque_str} {al_paso_str}"

    def esTripleRepeticion(self) -> bool:
        """
        Verifica si la posición actual (definida por piezas, turno, derechos enroque,
        y objetivo al paso) se ha repetido tres veces en la partida consultando
        el historial de posiciones mantenido por el tablero.
        Llamado por `actualizarEstadoJuego`.

        Returns:
            True si la posición actual se ha repetido tres (o más) veces, False en caso contrario.
        """
        # Obtener la representación FEN estándar de la posición actual.
        posicion_actual_str = self.obtenerPosicionActual()
        
        # Consultar el conteo en el historial mantenido por el tablero.
        ocurrencias = self.historial_posiciones[posicion_actual_str]
        
        logger.debug(f"Chequeando Repetición: Pos actual FEN: '{posicion_actual_str}'. Ocurrencias: {ocurrencias}")
        
        # La regla se cumple si la posición ha aparecido 3 o más veces.
        return ocurrencias >= 3

    # ============================================================
    # 6. Generación de Todos los Movimientos Legales (NUEVO)
    # ============================================================

    def obtener_todos_movimientos_legales(self, color: Literal['blanco', 'negro']) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Genera una lista de todos los movimientos legales para un color dado.
        Un movimiento legal es uno que sigue las reglas de la pieza y no deja
        al propio rey en jaque.

        Args:
            color: El color ('blanco' o 'negro') para el que generar movimientos.

        Returns:
            Una lista de tuplas, donde cada tupla representa un movimiento legal
            en el formato ((fila_origen, col_origen), (fila_destino, col_destino)).
            Devuelve una lista vacía si no hay movimientos legales (posible mate o ahogado).
        """
        todos_movimientos_legales = []
        for r in range(8):
            for c in range(8):
                pieza = self.casillas[r][c]
                if pieza is not None and pieza.color == color:
                    movimientos_pieza = pieza.obtener_movimientos_legales() # Ya filtra por seguridad del rey
                    origen = (r, c)
                    for destino in movimientos_pieza:
                        todos_movimientos_legales.append((origen, destino))
        
        # logger.debug(f"Movimientos legales generados para {color}: {len(todos_movimientos_legales)}") # Puede ser muy verboso
        return todos_movimientos_legales

    # --- Fin Métodos ---
   
                    
