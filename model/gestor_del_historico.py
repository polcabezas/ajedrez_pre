import logging
from typing import Dict, Tuple, Optional, Literal, TYPE_CHECKING, List
from collections import defaultdict

# Evitar importación circular con type hinting
if TYPE_CHECKING:
    from model.tablero import Tablero
    from model.piezas.pieza import Pieza

logger = logging.getLogger(__name__)

class GestorDelHistorico:
    """
    Gestiona el historial de posiciones y movimientos, y detecta condiciones de tablas relacionadas.
    También registra el historial de movimientos en notación algebraica estándar (SAN).
    """

    def __init__(self, tablero: 'Tablero'):
        """
        Inicializa el gestor del histórico.

        Args:
            tablero: Referencia al objeto Tablero del juego.
        """
        if tablero is None:
             logger.error("GestorDelHistorico requiere una instancia válida de Tablero.")
             raise ValueError("La instancia del tablero no puede ser None.")
        self.tablero = tablero
        
        # Historial de posiciones para la regla de triple repetición
        # Clave: string de representación de posición (tipo FEN), Valor: contador de ocurrencias
        self.historial_posiciones: Dict[str, int] = defaultdict(int)
        
        # Historial de movimientos en notación algebraica
        self.historial_san: List[str] = []
        # Historial de movimientos con información completa (para usar en la interfaz de usuario)
        self.historial_completo: List[Dict] = []
        # Número del movimiento actual (incrementa después de cada par de movimientos)
        self.numero_movimiento: int = 1

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
                # Acceder a casillas a través de la referencia al tablero
                pieza = self.tablero.casillas[fila_idx][col_idx]
                if pieza is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fila_str += str(empty_count)
                        empty_count = 0
                    try:
                        # Assume piece has this method
                        letra = pieza.obtenerNotacionFEN()
                        fila_str += letra.upper() if pieza.color == 'blanco' else letra.lower()
                    except AttributeError:
                        logger.warning(f"{type(pieza).__name__} no tiene 'obtenerNotacionFEN'. Usando '?'.")
                        fila_str += "?"
            if empty_count > 0:
                fila_str += str(empty_count)
            posicion_piezas.append(fila_str)
        piezas_str = "/".join(posicion_piezas)

        # --- Resto del estado FEN (Turno, Enroque, Al Paso) --- 
        # Acceder a través de la referencia al tablero
        turno_str = "w" if self.tablero.turno_blanco else "b"
        
        # Acceder a través de la referencia al tablero
        enroque_str = ""
        if self.tablero.derechosEnroque['blanco']['corto']: enroque_str += "K"
        if self.tablero.derechosEnroque['blanco']['largo']: enroque_str += "Q"
        if self.tablero.derechosEnroque['negro']['corto']: enroque_str += "k"
        if self.tablero.derechosEnroque['negro']['largo']: enroque_str += "q"
        enroque_str = enroque_str if enroque_str else "-"
        
        # Acceder a través de la referencia al tablero
        al_paso_str = "-"
        if self.tablero.objetivoPeonAlPaso:
            fila, col = self.tablero.objetivoPeonAlPaso
            try:
                col_letra = chr(ord('a') + col)
                fila_num_fen = str(fila + 1)
                al_paso_str = col_letra + fila_num_fen
            except Exception as e:
                al_paso_str = "?"
                logger.error(f"Error convirtiendo objetivo al paso {self.tablero.objetivoPeonAlPaso} a notación algebraica: {e}")

        return f"{piezas_str} {turno_str} {enroque_str} {al_paso_str}"

    def reiniciar(self):
        """
        Reinicia el historial completo, limpiando todas las estructuras de datos.
        Debe llamarse cuando se reinicia una partida.
        """
        # Limpiar el historial de posiciones
        self.historial_posiciones.clear()
        
        # Limpiar historial de notación
        self.historial_san = []
        
        # Limpiar historial completo
        self.historial_completo = []
        
        # Reiniciar contador de movimientos
        self.numero_movimiento = 1
        
        logger.info("Historial reiniciado completamente")

    def esTripleRepeticion(self) -> bool:
        """
        Verifica si la posición actual se ha repetido tres veces en la partida.
        Consulta el historial de posiciones mantenido por este gestor.

        Returns:
            True si la posición actual se ha repetido tres (o más) veces, False en caso contrario.
        """
        # Obtener la representación FEN usando el método de esta clase.
        posicion_actual_str = self.obtenerPosicionActual()
        
        # Consultar el conteo en el historial de esta clase.
        ocurrencias = self.historial_posiciones[posicion_actual_str]
        
        logger.debug(f"Chequeando Repetición (Gestor): Pos FEN: '{posicion_actual_str}'. Ocurrencias: {ocurrencias}")
        
        return ocurrencias >= 3
    
    def registrar_posicion(self):
        """
        Registra la posición actual en el historial de repeticiones.
        Debe llamarse DESPUÉS de que un movimiento se complete y el turno cambie.
        """
        estado_actual = self.obtenerPosicionActual()
        self.historial_posiciones[estado_actual] += 1
        logger.debug(f"Historial posiciones actualizado (Gestor). Estado: '{estado_actual}', Count: {self.historial_posiciones[estado_actual]}")
        
    def registrar_movimiento(self, pieza: 'Pieza', origen: Tuple[int, int], destino: Tuple[int, int], 
                           es_captura: bool = False, pieza_capturada: Optional['Pieza'] = None,
                           es_jaque: bool = False, es_mate: bool = False, 
                           es_enroque: bool = False, tipo_enroque: Optional[str] = None,
                           es_promocion: bool = False, pieza_promocion: Optional[str] = None,
                           es_al_paso: bool = False):
        """
        Registra un movimiento en notación algebraica estándar (SAN) en el historial.
        
        Args:
            pieza: La pieza que se movió.
            origen: Casilla de origen (fila, columna).
            destino: Casilla de destino (fila, columna).
            es_captura: True si el movimiento capturó una pieza.
            pieza_capturada: La pieza capturada (si aplica).
            es_jaque: True si el movimiento puso al rey rival en jaque.
            es_mate: True si el movimiento resultó en jaque mate.
            es_enroque: True si el movimiento fue un enroque.
            tipo_enroque: "corto" o "largo" si es enroque.
            es_promocion: True si un peón fue promovido.
            pieza_promocion: El tipo de pieza a la que se promovió el peón.
            es_al_paso: True si fue una captura al paso.
        """
        # Convertir a notación SAN
        notacion_san = self._convertir_a_san(pieza, origen, destino, 
                                           es_captura, pieza_capturada,
                                           es_jaque, es_mate, 
                                           es_enroque, tipo_enroque,
                                           es_promocion, pieza_promocion,
                                           es_al_paso)
        
        # Registrar en el historial SAN
        self.historial_san.append(notacion_san)
        
        # Crear entrada para el historial completo
        entrada_historial = {
            'notacion_san': notacion_san,
            'numero': self.numero_movimiento,
            'color': pieza.color,
            'pieza': type(pieza).__name__,
            'origen': origen,
            'destino': destino,
            'es_captura': es_captura,
            'es_jaque': es_jaque,
            'es_mate': es_mate,
            'es_enroque': es_enroque,
            'es_promocion': es_promocion,
        }
        
        # Registrar en el historial completo
        self.historial_completo.append(entrada_historial)
        
        # Actualizar número de movimiento (después de que las negras juegan)
        if pieza.color == 'negro':
            self.numero_movimiento += 1
            
        logger.debug(f"Movimiento registrado: {notacion_san}")
        
        return notacion_san
    
    def _convertir_a_san(self, pieza: 'Pieza', origen: Tuple[int, int], destino: Tuple[int, int], 
                        es_captura: bool = False, pieza_capturada: Optional['Pieza'] = None,
                        es_jaque: bool = False, es_mate: bool = False, 
                        es_enroque: bool = False, tipo_enroque: Optional[str] = None,
                        es_promocion: bool = False, pieza_promocion: Optional[str] = None,
                        es_al_paso: bool = False) -> str:
        """
        Convierte un movimiento a notación algebraica estándar (SAN).
        
        Args:
            (Los mismos que registrar_movimiento)
            
        Returns:
            str: El movimiento en notación SAN.
        """
        # Manejar enroque
        if es_enroque:
            if tipo_enroque == "corto":
                return "O-O"
            else:  # enroque largo
                return "O-O-O"
        
        # Obtener símbolo de la pieza (vacío para peones)
        tipo_pieza = type(pieza).__name__.lower()
        simbolo_pieza = ""
        if tipo_pieza != "peon":
            # Usar primera letra en español (excepto caballo que usa N)
            simbolos = {
                "torre": "T",
                "caballo": "C",
                "alfil": "A",
                "reina": "D",
                "rey": "R"
            }
            simbolo_pieza = simbolos.get(tipo_pieza, "?")
        
        # Convertir coordenadas a notación algebraica
        col_origen, fila_origen = origen[1], origen[0]
        col_destino, fila_destino = destino[1], destino[0]
        
        # Convertir columna a letra (a-h)
        col_letra_origen = chr(ord('a') + col_origen)
        col_letra_destino = chr(ord('a') + col_destino)
        
        # Convertir fila a número (1-8)
        fila_num_origen = str(fila_origen + 1)
        fila_num_destino = str(fila_destino + 1)
        
        # Determinar ambigüedad (si otra pieza del mismo tipo podía moverse a la misma casilla)
        es_ambiguo = False
        necesita_fila = False
        necesita_columna = False
        
        if tipo_pieza != "peon":  # Los peones se diferencian por columna siempre
            # Buscar otras piezas del mismo tipo y color que podrían mover a la misma casilla
            for fila in range(8):
                for columna in range(8):
                    if (fila, columna) == origen:
                        continue  # Saltar la pieza actual
                    
                    pieza_otra = self.tablero.getPieza((fila, columna))
                    if pieza_otra and type(pieza_otra).__name__.lower() == tipo_pieza and pieza_otra.color == pieza.color:
                        # Verificar si esta otra pieza podría mover al mismo destino
                        if destino in pieza_otra.obtener_movimientos_legales():
                            es_ambiguo = True
                            if columna == col_origen:
                                necesita_fila = True
                            else:
                                necesita_columna = True
        
        # Construir notación para origen (desambiguación)
        origen_notacion = ""
        if es_ambiguo:
            if necesita_columna:
                origen_notacion += col_letra_origen
            if necesita_fila:
                origen_notacion += fila_num_origen
        
        # Para peones que capturan, siempre incluir la columna de origen
        if tipo_pieza == "peon" and es_captura:
            origen_notacion = col_letra_origen
        
        # Agregar símbolo de captura
        captura_notacion = "x" if es_captura else ""
        
        # Construir notación para destino (siempre incluido)
        destino_notacion = col_letra_destino + fila_num_destino
        
        # Notación de promoción (si aplica)
        promocion_notacion = ""
        if es_promocion and pieza_promocion:
            simbolos_promocion = {
                "reina": "D",
                "torre": "T",
                "alfil": "A",
                "caballo": "C"
            }
            promocion_notacion = "=" + simbolos_promocion.get(pieza_promocion.lower(), "?")
        
        # Jaque o jaque mate
        jaque_notacion = ""
        if es_mate:
            jaque_notacion = "#"
        elif es_jaque:
            jaque_notacion = "+"
        
        # Al paso (opcional, se puede incluir como e.p. después de la notación)
        al_paso_notacion = " e.p." if es_al_paso else ""
        
        # Juntar todas las partes
        notacion_san = f"{simbolo_pieza}{origen_notacion}{captura_notacion}{destino_notacion}{promocion_notacion}{jaque_notacion}{al_paso_notacion}"
        
        return notacion_san
    
    def obtener_historial_completo_formato(self) -> List[str]:
        """
        Genera un listado del historial completo en formato:
        "1. e4 e5" (un número, movimiento blanco, movimiento negro)
        
        Returns:
            Lista de strings con los movimientos numerados. El último movimiento 
            puede tener solo el movimiento blanco si el historial tiene un número impar de movimientos.
        """
        resultado = []
        movimiento_actual = ""
        
        for i, mov in enumerate(self.historial_completo):
            if i % 2 == 0:  # Movimiento de blancas
                movimiento_actual = f"{mov['numero']}. {mov['notacion_san']}"
                if i == len(self.historial_completo) - 1:  # Si es el último y es blanco
                    resultado.append(movimiento_actual)
            else:  # Movimiento de negras
                movimiento_actual += f" {mov['notacion_san']}"
                resultado.append(movimiento_actual)
                movimiento_actual = ""
                
        return resultado
    
    def exportar_a_pgn(self) -> str:
        """
        Exporta el historial de movimientos al formato PGN (Portable Game Notation).
        Incluye información básica como la fecha y resultado.
        
        Returns:
            str: Representación PGN del juego.
        """
        import datetime
        
        # Encabezados PGN
        encabezados = [
            f'[Event "Partida de Ajedrez"]',
            f'[Site "?"]',
            f'[Date "{datetime.datetime.now().strftime("%Y.%m.%d")}"]',
            f'[Round "?"]',
            f'[White "Jugador Blanco"]',
            f'[Black "Jugador Negro"]',
            f'[Result "*"]'  # * indica resultado desconocido o partida en progreso
        ]
        
        # Convertir el historial a formato PGN (movimientos numerados)
        movimientos_pgn = self.obtener_historial_completo_formato()
        
        # Unir encabezados y movimientos
        pgn = "\n".join(encabezados) + "\n\n" + " ".join(movimientos_pgn) + " *"
        
        return pgn
