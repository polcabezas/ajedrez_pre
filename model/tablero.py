"""
Representa el tablero de ajedrez y las posiciones de las piezas.
""" 
import logging
from typing import Dict, List, Tuple, Optional, Literal
from collections import defaultdict # Importar defaultdict

# Importar piezas
from model.piezas import Torre, Caballo, Alfil, Reina, Rey, Peon
from model.piezas.pieza import Pieza
# Importar evaluador de estado
from .evaluador_estado_de_juego import EvaluadorEstadoDeJuego
# Importar validador de movimiento
from .validador_movimiento import ValidadorMovimiento
# Importar gestor del histórico
from .gestor_del_historico import GestorDelHistorico
# Importar EjecutorMovimiento
from .ejecutor_movimiento import EjecutorMovimiento

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
        
        # Motivo específico de tablas (material_insuficiente, repeticion, regla_50_movimientos, ahogado)
        self.motivo_tablas: Optional[str] = None

        # Número de movimiento completo (1 para el primer movimiento de blancas)
        self.numero_movimiento: int = 1

        # Información del último movimiento realizado (origen, destino)
        self.ultimo_movimiento: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None

        # Historial de posiciones se mueve a GestorDelHistorico
        # self.historial_posiciones: Dict[str, int] = defaultdict(int)

        # Inicializar el tablero con piezas
        self.inicializarTablero()

        # --- Instanciar componentes auxiliares ---
        # Crear instancia del evaluador de estado del juego
        self.evaluador_estado = EvaluadorEstadoDeJuego(self)
        # Crear instancia del validador de movimiento
        self.validador_movimiento = ValidadorMovimiento(self)
        # Crear instancia del gestor del histórico
        self.gestor_historico = GestorDelHistorico(self)
        # TODO: Instanciar EjecutorMovimiento cuando se refactorice
        # >>> Instanciar EjecutorMovimiento
        self.ejecutor_movimiento = EjecutorMovimiento(self)
        # <<< Fin Instanciar EjecutorMovimiento

        # Registrar la posición inicial en el historial de repeticiones (ahora via gestor)
        estado_inicial = self.gestor_historico.obtenerPosicionActual()
        self.gestor_historico.historial_posiciones[estado_inicial] = 1

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
        # --- Delegar la ejecución al EjecutorMovimiento ---
        return self.ejecutor_movimiento.ejecutar_movimiento_normal(posOrigen, posDestino)

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
        # --- Delegar la ejecución al EjecutorMovimiento ---
        return self.ejecutor_movimiento.ejecutar_enroque(color, tipo)
    
    # ============================================================
    # 4. Evaluación de Amenazas (MOVIDO A ValidadorMovimiento)
    # ============================================================

    # ============================================================
    # 5. Actualización del Estado del Juego (Post-Movimiento)
    # ============================================================
    
    def getTurnoColor(self) -> Literal['blanco', 'negro']:
        """
        Devuelve el color del jugador cuyo turno es.
        """
        return 'blanco' if self.turno_blanco else 'negro'
    
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
            self.motivo_tablas = 'regla_50_movimientos'
            logger.info("Tablas por regla de 50 movimientos.")
            return
        # Usar la instancia del gestor del histórico
        if self.gestor_historico.esTripleRepeticion():
            self.estado_juego = 'tablas'
            self.motivo_tablas = 'repeticion'
            logger.info("Tablas por triple repetición.")
            return
        # Comprobar tablas por material insuficiente
        # Usar la instancia del evaluador de estado
        if self.evaluador_estado.esMaterialInsuficiente():
            self.estado_juego = 'tablas'
            self.motivo_tablas = 'material_insuficiente'
            logger.info("Estado del juego actualizado a: tablas (material insuficiente)")
            return

        # 2. Comprobar Jaque (evaluando si el rey actual está amenazado)
        # Usar la instancia del validador de movimiento
        esta_en_jaque = self.validador_movimiento.esCasillaAmenazada(rey_pos, color_oponente)

        # 3. Determinar estado final (Mate/Ahogado - REQUIERE MOVIMIENTOS LEGALES)
        movimientos_legales = self.obtener_todos_movimientos_legales(color_jugador_actual)

        if not movimientos_legales: # No hay movimientos legales
           if esta_en_jaque:
               self.estado_juego = 'jaque_mate'
               logger.info(f"Jaque Mate a {color_jugador_actual}.")
           else:
               # Comprobar si hay tablas por ahogado
               if not self.obtener_todos_movimientos_legales(color_jugador_actual):
                   self.estado_juego = 'tablas' # Ahogado
                   self.motivo_tablas = 'ahogado'
                   logger.info(f"Estado del juego actualizado a: tablas (ahogado para {color_jugador_actual})")
           return

        # Si no es mate, ni ahogado, ni tablas por reglas, el juego sigue en curso (o en jaque)
        self.estado_juego = 'jaque' if esta_en_jaque else 'en_curso'
        self.motivo_tablas = None  # Restablecer el motivo si el estado no es tablas
        logger.debug(f"Estado del juego actualizado a: {self.estado_juego}")

    # ==================================================================
    # 5.5 Simulación y Verificación de Seguridad del Rey (MOVIDO a ValidadorMovimiento)
    # ==================================================================

    # ============================================================ 
    # 6. Representación de Posición y Chequeo de Repetición (MOVIMOS A GestorDelHistorico)
    # ============================================================

    # ============================================================
    # 7. Generación de Todos los Movimientos Legales
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
   
                    
