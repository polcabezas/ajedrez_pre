"""
Define la clase para gestionar el tiempo de juego de cada jugador.
"""

import time
from typing import Dict, Optional, Literal

class Temporizador:
    """
    Gestiona el tiempo de juego de cada jugador con control básico.
    """
    def __init__(self, tiempos_iniciales: Dict[Literal['blanco', 'negro'], float]):
        """
        Inicializa el temporizador con los tiempos dados para cada jugador.

        Args:
            tiempos_iniciales: Un diccionario con los segundos iniciales 
                               para 'blanco' y 'negro'. 
                               Ej: {'blanco': 600.0, 'negro': 600.0}
        """
        if not (isinstance(tiempos_iniciales, dict) and 
                'blanco' in tiempos_iniciales and 
                'negro' in tiempos_iniciales):
            raise ValueError("tiempos_iniciales debe ser un dict con claves 'blanco' y 'negro'")
            
        self.tiempos_restantes: Dict[Literal['blanco', 'negro'], float] = tiempos_iniciales.copy()
        self.turno_activo: Optional[Literal['blanco', 'negro']] = None # Qué reloj está corriendo
        self._ultimo_timestamp: Optional[float] = None # Para calcular el tiempo transcurrido
        self.corriendo: bool = False

    def iniciar_turno(self, color: Literal['blanco', 'negro']):
        """ Comienza a descontar el tiempo para el jugador especificado. """
        if not self.corriendo:
             self.corriendo = True
             
        if self.turno_activo and self.turno_activo != color:
            # Si había otro turno activo, actualiza su tiempo antes de cambiar
            self._actualizar_tiempo_restante()
        
        self.turno_activo = color
        self._ultimo_timestamp = time.monotonic() # Registra el momento de inicio

    def detener(self):
        """ Detiene el descuento de tiempo (ej. fin de partida). """
        if self.corriendo and self.turno_activo:
            self._actualizar_tiempo_restante()
        self.corriendo = False
        self.turno_activo = None
        self._ultimo_timestamp = None

    def _actualizar_tiempo_restante(self):
        """ Calcula y resta el tiempo transcurrido para el jugador activo. """
        if self.corriendo and self.turno_activo and self._ultimo_timestamp is not None:
            ahora = time.monotonic()
            transcurrido = ahora - self._ultimo_timestamp
            self.tiempos_restantes[self.turno_activo] -= transcurrido
            # Asegurarse de que el tiempo no sea negativo
            if self.tiempos_restantes[self.turno_activo] < 0:
                self.tiempos_restantes[self.turno_activo] = 0
            # Actualizar el timestamp para el próximo cálculo
            self._ultimo_timestamp = ahora

    def get_tiempo_restante(self, color: Literal['blanco', 'negro']) -> float:
        """ Devuelve el tiempo restante en segundos para un jugador. """
        # Actualizar el tiempo del jugador activo antes de devolverlo
        if self.corriendo and self.turno_activo == color:
            self._actualizar_tiempo_restante()
            
        return self.tiempos_restantes.get(color, 0.0)

    def get_tiempos_formateados(self) -> Dict[Literal['blanco', 'negro'], str]:
        """ Devuelve los tiempos restantes formateados como MM:SS. """
        # Actualizar ambos tiempos si el reloj está corriendo
        if self.corriendo and self.turno_activo:
             self._actualizar_tiempo_restante()
             
        tiempos_fmt = {}
        for color, segundos in self.tiempos_restantes.items():
            segundos_int = max(0, int(segundos))
            minutos = segundos_int // 60
            segundos_restantes = segundos_int % 60
            tiempos_fmt[color] = f"{minutos:02d}:{segundos_restantes:02d}"
        return tiempos_fmt

    def reiniciar(self, tiempos_nuevos: Dict[Literal['blanco', 'negro'], float]):
        """
        Reinicia el temporizador con nuevos valores de tiempo.
        
        Args:
            tiempos_nuevos: Un diccionario con los segundos iniciales 
                           para 'blanco' y 'negro'.
                           Ej: {'blanco': 600.0, 'negro': 600.0}
        """
        if not (isinstance(tiempos_nuevos, dict) and 
                'blanco' in tiempos_nuevos and 
                'negro' in tiempos_nuevos):
            raise ValueError("tiempos_nuevos debe ser un dict con claves 'blanco' y 'negro'")
        
        # Detener el temporizador primero
        self.detener()
        
        # Establecer los nuevos tiempos
        self.tiempos_restantes = tiempos_nuevos.copy()
        
        # Reiniciar estados
        self.turno_activo = None
        self._ultimo_timestamp = None
        self.corriendo = False

    def __str__(self) -> str:
         tiempos = self.get_tiempos_formateados()
         return f"Temporizador(Blancas: {tiempos['blanco']}, Negras: {tiempos['negro']}, Activo: {self.turno_activo}, Corriendo: {self.corriendo})"
