import logging
from typing import Dict, Tuple, Optional, Literal, TYPE_CHECKING
from collections import defaultdict

# Evitar importación circular con type hinting
if TYPE_CHECKING:
    from model.tablero import Tablero

logger = logging.getLogger(__name__)

class GestorDelHistorico:
    """
    Gestiona el historial de posiciones y movimientos, y detecta condiciones de tablas relacionadas.
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
        
        # Podríamos añadir aquí también el historial_movimientos si queremos que este gestor
        # maneje todo el historial, pero por ahora solo movemos la repetición.
        # self.historial_movimientos = [] # Ejemplo

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
