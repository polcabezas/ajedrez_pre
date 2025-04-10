"""
Gestiona el estado general del juego (turno, jaque, jaque mate, tablas).
""" 
from typing import Literal, Optional, Tuple, Dict, List
import logging
from collections import defaultdict

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Juego:
    def __init__(self, tablero):
        """
        Inicializa el juego con un tablero y un turno.
        
        Args:
            tablero: Instancia de la clase Tablero que representa el estado del tablero.
        """
        # Referencia al tablero
        self.tablero = tablero
        
        # Turno del jugador
        self.turno_blanco: bool = True # True = turno del blanco, False = turno del negro
        
        # Estado del juego
        self.estado_juego: Literal['en_curso', 'jaque', 'jaque_mate', 'tablas'] = 'en_curso'
        
        # Contador para la regla de los 50 movimientos (se resetea con captura o mov. de peón)
        self.contadorRegla50Movimientos: int = 0
        
        # Contador de plies (medio movimiento). Empieza en 0 antes del primer movimiento.
        self.contadorPly: int = 0
        
        # Número de movimiento completo (1 para el primer movimiento de blancas)
        self.numero_movimiento: int = 1
        
        # Historial de posiciones para la regla de triple repetición
        # Clave: string de representación de posición (tipo FEN), Valor: contador de ocurrencias
        self.historial_posiciones: Dict[str, int] = defaultdict(int)
        
        # Historial de movimientos
        self.historial_movimientos: List[Tuple[Literal['blanco', 'negro'], Tuple[int, int], Tuple[int, int]]] = []
        
        # Último movimiento realizado (origen, destino)
        self.ultimo_movimiento: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
        
        # Registrar la posición inicial
        self.registrarPosicionActual()
        
    def getTurnoColor(self) -> Literal['blanco', 'negro']:
        """
        Devuelve el color del jugador cuyo turno es.
        """
        return 'blanco' if self.turno_blanco else 'negro'
    
    def cambiarTurno(self):
        """
        Cambia el turno al jugador contrario.
        """
        self.turno_blanco = not self.turno_blanco
        logger.debug(f"Turno cambiado a: {'blanco' if self.turno_blanco else 'negro'}")
        
    def actualizarEstadoJuego(self):
        """
        Analiza el tablero y actualiza el estado del juego (en_curso, jaque, jaque_mate, tablas).
        """
        color_actual = self.getTurnoColor()
        color_oponente = 'negro' if color_actual == 'blanco' else 'blanco'
        
        # Encontrar el rey del jugador actual
        rey_pos = self.tablero.encontrarRey(color_actual)
        if not rey_pos:
            logger.error(f"No se encontró rey de color {color_actual}")
            return
            
        # Verificar si está en jaque
        esta_en_jaque = self.tablero.esCasillaAmenazada(rey_pos, color_oponente)
        
        # Verificar si hay movimientos legales
        movimientos_legales = self.tablero.obtener_todos_movimientos_legales(color_actual)
        hay_movimientos = len(movimientos_legales) > 0
        
        # Determinar estado
        if not hay_movimientos:
            if esta_en_jaque:
                estado = 'jaque_mate'
                logger.info(f"Jaque mate al rey {color_actual}")
            else:
                estado = 'tablas'
                logger.info(f"Tablas por ahogado del rey {color_actual}")
        elif esta_en_jaque:
            estado = 'jaque'
            logger.info(f"Jaque al rey {color_actual}")
        # Verificar tablas por repetición, regla de 50 movimientos o material insuficiente
        elif self.esTripleRepeticionActual() or self.contadorRegla50Movimientos >= 50 or self.esMaterialInsuficiente():
            estado = 'tablas'
            if self.esTripleRepeticionActual():
                logger.info("Tablas por triple repetición")
            elif self.contadorRegla50Movimientos >= 50:
                logger.info("Tablas por regla de 50 movimientos")
            else:
                logger.info("Tablas por material insuficiente")
        else:
            estado = 'en_curso'
            
        # Actualizar el estado
        self.estado_juego = estado
        logger.info(f"Estado del juego actualizado a: {estado}")
        
    def obtenerEstadoJuego(self) -> Literal['en_curso', 'jaque', 'jaque_mate', 'tablas']:
        """
        Obtiene el estado actual del juego.
        
        Returns:
            El estado actual del juego.
        """
        return self.estado_juego
        
    def actualizarContadores(self, pieza_movida, es_captura: bool):
        """
        Actualiza el contador de ply, el número de movimiento y el contador de la regla de 50 movimientos.
        
        Args:
            pieza_movida: La pieza que se acaba de mover, o None si no se dispone de ella.
            es_captura: True si el movimiento fue una captura, False en caso contrario.
        """
        self.contadorPly += 1
        
        # El número de movimiento incrementa después de que las negras muevan
        if not self.turno_blanco:  # Si turno_blanco es False, las negras ACABAN de mover
            self.numero_movimiento += 1
            
        # Determinar si es un movimiento de peón
        es_movimiento_peon = False
        if pieza_movida and hasattr(pieza_movida, '__class__'):
            es_movimiento_peon = pieza_movida.__class__.__name__ == 'Peon'
            
        # Resetear contador de 50 movimientos si fue un movimiento de peón o una captura
        if es_captura or es_movimiento_peon:
            self.contadorRegla50Movimientos = 0
        else:
            self.contadorRegla50Movimientos += 1
            
        logger.debug(f"Contadores actualizados - Ply: {self.contadorPly}, Movimiento: {self.numero_movimiento}, Regla 50: {self.contadorRegla50Movimientos}")
    
    def actualizarUltimoMovimiento(self, origen: Tuple[int, int], destino: Tuple[int, int]):
        """
        Actualiza la información sobre el último movimiento realizado.
        
        Args:
            origen (tuple): Posición de origen (fila, columna)
            destino (tuple): Posición de destino (fila, columna)
        """
        self.ultimo_movimiento = (origen, destino)
        logger.debug(f"Último movimiento: {origen} -> {destino}")
        
    def procesarMovimientoRealizado(self, pieza_movida, posOrigen: Tuple[int, int], 
                                   posDestino: Tuple[int, int], es_captura: bool):
        """
        Procesa un movimiento ya realizado en el tablero, actualizando el estado del juego.
        
        Args:
            pieza_movida: La pieza que se acaba de mover
            posOrigen: Posición original de la pieza (fila, columna)
            posDestino: Posición destino de la pieza (fila, columna)
            es_captura: Si el movimiento incluyó una captura
        """
        # 1. Actualizar último movimiento
        self.actualizarUltimoMovimiento(posOrigen, posDestino)
        
        # 2. Añadir al historial de movimientos
        color_jugador = pieza_movida.color
        self.historial_movimientos.append((color_jugador, posOrigen, posDestino))
        
        # 3. Actualizar contadores
        self.actualizarContadores(pieza_movida, es_captura)
        
        # 4. Cambiar el turno
        self.cambiarTurno()
        
        # 5. Registrar la posición actual
        self.registrarPosicionActual()
        
        # 6. Actualizar el estado del juego
        self.actualizarEstadoJuego()
        
    def procesarEnroqueRealizado(self, color: Literal['blanco', 'negro'], 
                                tipo: Literal['corto', 'largo'],
                                rey_pos_origen: Tuple[int, int], 
                                rey_pos_destino: Tuple[int, int]):
        """
        Procesa un enroque ya realizado en el tablero.
        
        Args:
            color: El color del jugador que enrocó
            tipo: El tipo de enroque ('corto' o 'largo')
            rey_pos_origen: Posición original del rey
            rey_pos_destino: Posición final del rey
        """
        # 1. Actualizar último movimiento
        self.actualizarUltimoMovimiento(rey_pos_origen, rey_pos_destino)
        
        # 2. Añadir al historial de movimientos
        self.historial_movimientos.append((color, rey_pos_origen, rey_pos_destino))
        
        # 3. Actualizar contadores (el enroque no es captura ni movimiento de peón)
        rey = self.tablero.getPieza(rey_pos_destino)
        self.actualizarContadores(rey, False)
        
        # 4. Cambiar el turno
        self.cambiarTurno()
        
        # 5. Registrar la posición actual
        self.registrarPosicionActual()
        
        # 6. Actualizar el estado del juego
        self.actualizarEstadoJuego()
        
        logger.info(f"Enroque {color} {tipo} procesado en el juego")
        
    def registrarPosicionActual(self):
        """
        Obtiene la posición actual del tablero y la registra en el historial.
        """
        posicion_fen = self.tablero.obtenerPosicionActual()
        self.registrarPosicion(posicion_fen)
        
    def registrarPosicion(self, posicion_fen: str):
        """
        Registra una posición en el historial para la regla de triple repetición.
        
        Args:
            posicion_fen: Representación FEN de la posición.
        """
        self.historial_posiciones[posicion_fen] += 1
        logger.debug(f"Posición registrada: {posicion_fen} (ocurrencias: {self.historial_posiciones[posicion_fen]})")
        
    def esTripleRepeticionActual(self) -> bool:
        """
        Verifica si la posición actual se ha repetido tres veces.
        
        Returns:
            True si la posición actual se ha repetido tres o más veces, False en caso contrario.
        """
        posicion_actual = self.tablero.obtenerPosicionActual()
        return self.esTripleRepeticion(posicion_actual)
        
    def esTripleRepeticion(self, posicion_fen: str) -> bool:
        """
        Verifica si una posición se ha repetido tres veces.
        
        Args:
            posicion_fen: Representación FEN de la posición a verificar.
            
        Returns:
            True si la posición se ha repetido tres o más veces, False en caso contrario.
        """
        ocurrencias = self.historial_posiciones[posicion_fen]
        return ocurrencias >= 3

    def esMaterialInsuficiente(self) -> bool:
        """
        Comprueba si hay material insuficiente en el tablero para forzar un jaque mate.
        Esta es una delegación al método del tablero, ya que necesita acceso directo a las piezas.
        
        Returns:
            True si el material es insuficiente para mate, False en caso contrario.
        """
        # Delegamos al tablero, que tiene acceso a las piezas
        if self.tablero:
            return self.tablero.esMaterialInsuficiente()
        return False

    def obtener_todos_movimientos_legales(self, color: Optional[Literal['blanco', 'negro']] = None) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Genera una lista de todos los movimientos legales para un color dado.
        Si no se especifica un color, se utilizará el color del jugador actual.
        
        Args:
            color: Opcional. El color para el que generar movimientos ('blanco' o 'negro').
                  Si es None, se usará el color del jugador actual.
                  
        Returns:
            Una lista de tuplas, donde cada tupla representa un movimiento legal
            en el formato ((fila_origen, col_origen), (fila_destino, col_destino)).
        """
        if color is None:
            color = self.getTurnoColor()
            
        if self.tablero:
            return self.tablero.obtener_todos_movimientos_legales(color)
        return []