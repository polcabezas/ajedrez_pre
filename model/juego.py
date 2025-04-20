"""
Gestiona el estado general del juego (turno, jaque, jaque mate, tablas).
""" 
from typing import List, Tuple, Optional, Literal
from model.tablero import Tablero
from model.temporizador import Temporizador
from model.configuracion_juego import ConfiguracionJuego

class Juego:
    """
    Clase que gestiona el estado global del juego de ajedrez.
    Coordina el tablero, los jugadores, el estado del juego y el historial.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia de juego con todas las propiedades básicas.
        """
        self.tablero = Tablero()
        self.jugadores = []
        self.jugador_actual = None
        self.estado = "JUGANDO"  # JUGANDO, JAQUE_MATE, TABLAS
        self.color_activo = "blanco"  # El color que debe jugar ahora
        self.historial_movimientos = []
        self.temporizador = None
        self.config = None
    
    def getTurnoColor(self) -> Literal['blanco', 'negro']:
        """
        Obtiene el color del jugador cuyo turno es.
        """
        return self.tablero.getTurnoColor()