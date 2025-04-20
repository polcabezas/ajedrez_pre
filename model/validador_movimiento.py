"""
Validador de movimientos para el ajedrez.
"""
import logging
from typing import Tuple, Optional, Literal

# Importar todas las piezas para isinstance checks
from model.piezas.pieza import Pieza
from model.piezas.peon import Peon
from model.piezas.caballo import Caballo
from model.piezas.alfil import Alfil
from model.piezas.torre import Torre
from model.piezas.reina import Reina
from model.piezas.rey import Rey

# Configurar logger para este módulo si es necesario, o asumir que es configurado globalmente
logger = logging.getLogger(__name__)

class ValidadorMovimiento:
    """
    Clase que valida los movimientos en el ajedrez.
    Verifica si un movimiento es legal según las reglas del ajedrez,
    incluyendo chequeos de si una casilla está amenazada.
    """

    def __init__(self, tablero):
        """
        Inicializa el validador de movimientos.
        
        Args:
            tablero: Referencia al tablero de ajedrez.
        """
        self.tablero = tablero

    def esBlanco(self, posicion: Tuple[int, int]) -> bool:
        """
        Verifica si una pieza en una posición dada es blanca.
        
        Args:
            posicion: Una tupla (fila, columna) indicando la casilla.

        Returns:
            True si la pieza es blanca, False en caso contrario o si la casilla está vacía.
        """
        pieza = self.tablero.getPieza(posicion)
        return pieza is not None and pieza.color == 'blanco'

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
        # Usar el método del tablero para validar la posición
        if not self.tablero.esPosicionValida(posicion):
            return False

        # Iterar sobre las casillas del tablero
        for r in range(8):
            for c in range(8):
                # Usar getPieza del tablero
                pieza = self.tablero.getPieza((r, c)) 
                if pieza is None or pieza.color != color_atacante:
                    continue

                # Asumiendo que las piezas tienen un atributo 'posicion' válido
                attacker_f, attacker_c = pieza.posicion 

                # --- 1. Comprobación de Peón ---
                if isinstance(pieza, Peon):
                    direccion = 1 if pieza.color == 'blanco' else -1
                    if target_f == attacker_f + direccion:
                        if target_c == attacker_c + 1 or target_c == attacker_c - 1:
                            return True
                    continue

                # --- 2. Comprobación de Caballo ---
                if isinstance(pieza, Caballo):
                    df = abs(target_f - attacker_f)
                    dc = abs(target_c - attacker_c)
                    if (df == 1 and dc == 2) or (df == 2 and dc == 1):
                        return True
                    continue

                # --- 3. Comprobación de Rey ---
                if isinstance(pieza, Rey):
                    if abs(target_f - attacker_f) <= 1 and abs(target_c - attacker_c) <= 1:
                        if (target_f, target_c) != (attacker_f, attacker_c): 
                           return True
                    continue

                # --- 4. Comprobación de Piezas Deslizantes (Torre, Alfil, Reina) ---
                is_sliding = isinstance(pieza, (Torre, Alfil, Reina))
                if not is_sliding:
                    continue

                can_attack_rank_file = isinstance(pieza, (Torre, Reina))
                can_attack_diagonal = isinstance(pieza, (Alfil, Reina))

                df = target_f - attacker_f
                dc = target_c - attacker_c
                on_line = False
                step_f, step_c = 0, 0

                if can_attack_rank_file and (df == 0 or dc == 0) and (df != 0 or dc != 0):
                    on_line = True
                    step_f = 0 if df == 0 else (1 if df > 0 else -1)
                    step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
                elif can_attack_diagonal and abs(df) == abs(dc) and df != 0:
                    on_line = True
                    step_f = 1 if df > 0 else -1
                    step_c = 1 if dc > 0 else -1
                
                if not on_line:
                    continue
                
                path_clear = True
                check_f, check_c = attacker_f + step_f, attacker_c + step_c
                while (check_f, check_c) != posicion:
                    # Usar el método del tablero para validar
                    if not self.tablero.esPosicionValida((check_f, check_c)): 
                        logger.warning(f"[Threat Check Path] Path check went out of bounds from {(attacker_f, attacker_c)} to {posicion}")
                        path_clear = False 
                        break
                    # Usar getPieza del tablero
                    blocking_piece = self.tablero.getPieza((check_f, check_c)) 
                    if blocking_piece is not None:
                        path_clear = False
                        break
                    check_f += step_f
                    check_c += step_c
                
                if path_clear:
                    return True

        return False

    def simular_y_verificar_seguridad(self, pieza: Pieza, destino: Tuple[int, int]) -> bool:
        """
        Simula un movimiento, verifica si el rey del jugador queda en jaque y deshace la simulación.
        ¡Precaución! Este método modifica y restaura el estado del tablero temporalmente.
        Llamado por obtener_movimientos_legales de las piezas.

        Args:
            pieza: La pieza que se intenta mover.
            destino: La casilla destino del movimiento simulado.

        Returns:
            True si el rey NO queda en jaque después del movimiento simulado, False en caso contrario.
        """
        origen = pieza.posicion
        color_jugador = pieza.color
        color_oponente = 'negro' if color_jugador == 'blanco' else 'blanco'

        # --- Almacenar estado original del tablero y pieza ---     
        # Pieza en destino (puede ser None)
        pieza_capturada_temporal = self.tablero.getPieza(destino)
        # Estado 'en passant' actual
        objetivo_ep_original = self.tablero.objetivoPeonAlPaso
        # Copia profunda de los derechos de enroque para restaurar
        derechos_enroque_original = {
            'blanco': self.tablero.derechosEnroque['blanco'].copy(),
            'negro': self.tablero.derechosEnroque['negro'].copy()
        }
        # Estado 'se_ha_movido' de la pieza que se mueve
        pieza_se_ha_movido_original = getattr(pieza, 'se_ha_movido', None)
        # Estado 'se_ha_movido' de la torre capturada (si aplica)
        torre_capturada_se_ha_movido_original = None
        if pieza_capturada_temporal is not None and isinstance(pieza_capturada_temporal, Torre):
             torre_capturada_se_ha_movido_original = getattr(pieza_capturada_temporal, 'se_ha_movido', None)

        # --- Simular el movimiento --- 
        # Gestionar captura al paso simulada
        pieza_capturada_ep_real = None 
        casilla_peon_capturado_ep = None
        if isinstance(pieza, Peon) and destino == self.tablero.objetivoPeonAlPaso:
            fila_captura_ep = origen[0]
            col_captura_ep = destino[1]
            casilla_peon_capturado_ep = (fila_captura_ep, col_captura_ep)
            # Usar getPieza del tablero
            pieza_capturada_ep_real = self.tablero.getPieza(casilla_peon_capturado_ep)
            if pieza_capturada_ep_real: 
                # Usar setPieza del tablero
                self.tablero.setPieza(casilla_peon_capturado_ep, None) 
        
        # Mover la pieza en el tablero simulado
        self.tablero.setPieza(destino, pieza)
        self.tablero.setPieza(origen, None)
        # Actualizar estado interno de la pieza (temporalmente)
        pieza.posicion = destino 
        if hasattr(pieza, 'se_ha_movido'): 
            pieza.se_ha_movido = True 
        
        # --- Actualizar estado relevante (simplificado para simulación) --- 
        # Actualizar derechos de enroque (temporalmente)
        # Simular el efecto de actualizarDerechosEnroque sin llamarlo directamente
        color_movido = pieza.color
        if isinstance(pieza, Rey):
            self.tablero.derechosEnroque[color_movido]['corto'] = False
            self.tablero.derechosEnroque[color_movido]['largo'] = False
        elif isinstance(pieza, Torre):
            if color_movido == 'blanco':
                if origen == (0, 7): self.tablero.derechosEnroque['blanco']['corto'] = False
                elif origen == (0, 0): self.tablero.derechosEnroque['blanco']['largo'] = False
            elif color_movido == 'negro':
                if origen == (7, 7): self.tablero.derechosEnroque['negro']['corto'] = False
                elif origen == (7, 0): self.tablero.derechosEnroque['negro']['largo'] = False
        if pieza_capturada_temporal is not None and isinstance(pieza_capturada_temporal, Torre):
             color_capturada = pieza_capturada_temporal.color
             if color_capturada == 'blanco':
                 if destino == (0, 7): self.tablero.derechosEnroque['blanco']['corto'] = False
                 elif destino == (0, 0): self.tablero.derechosEnroque['blanco']['largo'] = False
             elif color_capturada == 'negro':
                 if destino == (7, 7): self.tablero.derechosEnroque['negro']['corto'] = False
                 elif destino == (7, 0): self.tablero.derechosEnroque['negro']['largo'] = False

        # Actualizar Peón al Paso (temporalmente)
        # Simular el efecto de actualizarPeonAlPaso
        self.tablero.objetivoPeonAlPaso = None 
        if isinstance(pieza, Peon) and abs(origen[0] - destino[0]) == 2:
            fila_objetivo = (origen[0] + destino[0]) // 2
            self.tablero.objetivoPeonAlPaso = (fila_objetivo, origen[1])

        # --- Verificar seguridad del rey --- 
        # Encontrar el rey del jugador que movió
        rey_pos = None
        for r, fila in enumerate(self.tablero.casillas):
            for c, p_actual in enumerate(fila):
                if isinstance(p_actual, Rey) and p_actual.color == color_jugador:
                    rey_pos = (r, c)
                    break
            if rey_pos: break

        es_seguro = False
        if rey_pos is None:
             logger.critical(f"SIMULACIÓN: Rey {color_jugador} no encontrado.")
        else:
             # Llamar al método esCasillaAmenazada de ESTA clase (ValidadorMovimiento)
             es_seguro = not self.esCasillaAmenazada(rey_pos, color_oponente)

        # --- Deshacer la simulación: Restaurar estado --- 
        # Restaurar estado de la pieza movida
        if hasattr(pieza, 'se_ha_movido'):
            pieza.se_ha_movido = pieza_se_ha_movido_original 
        pieza.posicion = origen 
        # Restaurar piezas en el tablero
        self.tablero.setPieza(origen, pieza)
        self.tablero.setPieza(destino, pieza_capturada_temporal)
        # Restaurar peón capturado al paso (si aplica)
        if casilla_peon_capturado_ep and pieza_capturada_ep_real:
            self.tablero.setPieza(casilla_peon_capturado_ep, pieza_capturada_ep_real) 

        # Restaurar estado del tablero
        self.tablero.objetivoPeonAlPaso = objetivo_ep_original
        self.tablero.derechosEnroque = derechos_enroque_original 
        # Restaurar estado 'se_ha_movido' de la torre capturada
        if pieza_capturada_temporal is not None and hasattr(pieza_capturada_temporal, 'se_ha_movido') and torre_capturada_se_ha_movido_original is not None:
            pieza_capturada_temporal.se_ha_movido = torre_capturada_se_ha_movido_original

        return es_seguro
