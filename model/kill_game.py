"""
Utilidad de desarrollo para forzar el fin del juego y probar diferentes escenarios posibles, para facilitar el desarrollo y prueba del popup de fin de juego.
NO USAR EN PRODUCCIÓN - Solo para propósitos de desarrollo y pruebas.
"""

import logging
from typing import Optional, Literal, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .juego import Juego
    from .tablero import Tablero

logger = logging.getLogger(__name__)

class KillGame:
    """
    Clase de desarrollo para terminar forzadamente el juego y probar diferentes escenarios
    de fin de partida sin necesidad de jugar hasta completarla.
    
    Esta utilidad permite verificar rápidamente el funcionamiento del popup de fin de juego,
    las acciones de los botones y el reinicio del juego.
    """
    
    def __init__(self, juego: 'Juego'):
        """
        Inicializa la utilidad con una referencia al juego.
        
        Args:
            juego: Instancia del juego que se va a forzar a terminar.
        """
        self.juego = juego
        self.tablero: 'Tablero' = juego.tablero
        
    def forzar_fin_juego(self, 
                        resultado: Literal['victoria_blanco', 'victoria_negro', 'tablas'],
                        motivo: Optional[Literal['jaque_mate', 'ahogado', 'material_insuficiente', 
                                              'repeticion', 'regla_50_movimientos', 'tiempo']] = None) -> Dict[str, Any]:
        """
        Fuerza el fin del juego con el resultado y motivo especificados.
        
        Args:
            resultado: Tipo de resultado ('victoria_blanco', 'victoria_negro', 'tablas')
            motivo: Motivo del fin de juego ('jaque_mate', 'ahogado', etc.)
            
        Returns:
            Diccionario con información sobre el fin del juego forzado.
        """
        logger.warning(f"[DESARROLLO] Forzando fin de juego: {resultado} por {motivo}")
        
        # Asegurarnos de que siempre usamos la referencia más reciente al tablero
        self.tablero = self.juego.tablero
        
        # Modificar el estado del juego
        if resultado == 'victoria_blanco':
            self.juego.estado = 'jaque_mate'
            # Asegurarse de que el turno actual sea negro (para que el ganador sea blanco)
            self.juego.color_activo = 'negro'
            self.tablero.turno_blanco = False
            # Actualizar también el estado del tablero
            self.tablero.estado_juego = 'jaque_mate'
        elif resultado == 'victoria_negro':
            self.juego.estado = 'jaque_mate'
            # Asegurarse de que el turno actual sea blanco (para que el ganador sea negro)
            self.juego.color_activo = 'blanco'
            self.tablero.turno_blanco = True
            # Actualizar también el estado del tablero
            self.tablero.estado_juego = 'jaque_mate'
        elif resultado == 'tablas':
            # Establecer el estado específico de tablas según el motivo
            if motivo == 'ahogado':
                self.juego.estado = 'ahogado'
                self.tablero.estado_juego = 'tablas'  # En el tablero, ahogado se considera tablas
                self.tablero.motivo_tablas = 'ahogado'
            elif motivo in ['material_insuficiente', 'repeticion', 'regla_50_movimientos']:
                self.juego.estado = 'tablas'
                self.tablero.estado_juego = 'tablas'
                # Actualizar también el motivo en el tablero
                if hasattr(self.tablero, 'motivo_tablas'):
                    self.tablero.motivo_tablas = motivo
            else:
                self.juego.estado = 'tablas'  # Motivo genérico
                self.tablero.estado_juego = 'tablas'
                self.tablero.motivo_tablas = motivo if motivo else 'material_insuficiente'
        
        # Asegurarse de que el tablero tiene piezasCapturadas inicializado
        if not hasattr(self.tablero, 'piezasCapturadas') or self.tablero.piezasCapturadas is None:
            self.tablero.piezasCapturadas = []
        
        # Detener el temporizador si existe
        if self.juego.temporizador:
            self.juego.temporizador.detener()
            
        # Registrar información sobre el fin forzado (para debugging)
        info_fin = {
            'resultado': resultado,
            'motivo': motivo,
            'estado_juego': self.juego.estado,
            'turno_actual': self.juego.color_activo,
        }
        
        logger.info(f"[DESARROLLO] Juego terminado forzadamente: {info_fin}")
        return info_fin
    
    def simular_jaque_mate_rapido(self) -> Dict[str, Any]:
        """
        Simula un jaque mate rápido (mate del pastor) donde ganan las blancas.
        Método de conveniencia para pruebas.
        
        Returns:
            Información sobre el fin del juego.
        """
        return self.forzar_fin_juego('victoria_blanco', 'jaque_mate')
    
    def simular_tablas_ahogado(self) -> Dict[str, Any]:
        """
        Simula un final en tablas por ahogado.
        Método de conveniencia para pruebas.
        
        Returns:
            Información sobre el fin del juego.
        """
        return self.forzar_fin_juego('tablas', 'ahogado')
    
    def simular_victoria_negras(self) -> Dict[str, Any]:
        """
        Simula una victoria de las negras por jaque mate.
        Método de conveniencia para pruebas.
        
        Returns:
            Información sobre el fin del juego.
        """
        return self.forzar_fin_juego('victoria_negro', 'jaque_mate')
    
    def simular_tablas_material_insuficiente(self) -> Dict[str, Any]:
        """
        Simula tablas por material insuficiente.
        Método de conveniencia para pruebas.
        
        Returns:
            Información sobre el fin del juego.
        """
        return self.forzar_fin_juego('tablas', 'material_insuficiente')

# Ejemplo de uso (desde el controlador):
# 
# from model.kill_game import KillGame
# 
# # En algún método del controlador:
# def test_fin_de_juego(self):
#     killer = KillGame(self.modelo)
#     killer.simular_jaque_mate_rapido()  # O cualquier otro escenario
#     self._actualizar_estado_post_movimiento()  # Para que actualice la vista 