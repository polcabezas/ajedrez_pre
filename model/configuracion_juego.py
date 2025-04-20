"""
Define la clase para gestionar la configuración específica de una partida de ajedrez.
"""

import logging
from typing import Dict, Literal, Optional

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

class ConfiguracionJuego:
    """
    Gestiona y proporciona la configuración específica para una partida de ajedrez,
    basándose en el tipo de juego seleccionado (Clásico, Rápido, Blitz).
    
    Esta clase almacena los parámetros clave como el tiempo inicial, el incremento
    por movimiento y si se requiere anotación, facilitando el acceso a esta
    información por otras partes del sistema como la clase Juego o Temporizador.
    """

    # Parámetros base para cada tipo de juego según FIDE/Solicitud
    # (Tiempo base en segundos, Incremento en segundos, Requiere anotación)
    PARAMETROS_POR_TIPO: Dict[str, Dict[str, any]] = {
        'Clásico': {'tiempo_base': 90 * 60, 'incremento': 30, 'anotacion': True},
        'Rápido':  {'tiempo_base': 25 * 60, 'incremento': 10, 'anotacion': False},
        'Blitz':   {'tiempo_base': 3 * 60,  'incremento': 2,  'anotacion': False}
        # Añadir aquí otros modos si es necesario
    }
    DEFAULT_TIPO = 'Rápido' # Tipo a usar si el proporcionado no es válido

    def __init__(self, config_inicial: dict):
        """
        Inicializa la configuración de la partida basada en un diccionario de opciones.

        Args:
            config_inicial (dict): Un diccionario que debe contener al menos 'tipo_juego'
                                   y opcionalmente 'modalidad'. Ejemplo:
                                   {'tipo_juego': 'Rápido', 'modalidad': 'Humano vs CPU'}
        """
        if not isinstance(config_inicial, dict):
             logger.error("Error: config_inicial debe ser un diccionario. Usando configuración por defecto.")
             config_inicial = {} # Usar diccionario vacío para proceder con defaults

        # --- 1. Determinar Tipo de Juego y Modalidad ---
        self._tipo_juego: str = config_inicial.get('tipo_juego', self.DEFAULT_TIPO)
        # Extraer solo el nombre base del tipo de juego si viene con descripción
        # Ej: 'Clásico (90 minutos + 30 segundos/movimiento)' -> 'Clásico'
        if '(' in self._tipo_juego:
            self._tipo_juego = self._tipo_juego.split('(')[0].strip()
            
        self._modalidad: str = config_inicial.get('modalidad', 'Humano vs Humano') # Default si no se provee

        # Validar que el tipo de juego sea conocido, si no, usar el default
        if self._tipo_juego not in self.PARAMETROS_POR_TIPO:
            logger.warning(f"Tipo de juego '{self._tipo_juego}' no reconocido. "
                           f"Usando configuración por defecto: '{self.DEFAULT_TIPO}'.")
            self._tipo_juego = self.DEFAULT_TIPO

        # --- 2. Cargar Parámetros Específicos del Tipo de Juego ---
        parametros = self.PARAMETROS_POR_TIPO[self._tipo_juego]
        
        self._tiempo_base_segundos: int = parametros['tiempo_base']
        self._incremento_segundos: int = parametros['incremento']
        self._requiere_anotacion: bool = parametros['anotacion']

        logger.info(f"ConfiguracionJuego inicializada: Tipo='{self._tipo_juego}', "
                    f"Modalidad='{self._modalidad}', "
                    f"TiempoBase={self._tiempo_base_segundos}s, "
                    f"Incremento={self._incremento_segundos}s, "
                    f"Anotación={self._requiere_anotacion}")

    # --- Propiedades para Acceder a la Configuración ---

    @property
    def tipo_partida(self) -> str:
        """
        Devuelve el tipo de partida configurado (ej. 'Clásico', 'Rápido', 'Blitz').
        """
        return self._tipo_juego

    @property
    def modalidad_juego(self) -> str:
        """
        Devuelve la modalidad de juego configurada (ej. 'Humano vs Humano').
        """
        return self._modalidad

    @property
    def tiempo_inicial_segundos(self) -> int:
        """
        Devuelve el tiempo base inicial asignado a cada jugador en segundos.
        Este valor debe ser usado para inicializar el temporizador.
        """
        return self._tiempo_base_segundos

    @property
    def incremento_por_movimiento_segundos(self) -> int:
        """
        Devuelve el tiempo en segundos que se añade al reloj de un jugador
        después de completar cada movimiento. Puede ser 0 si no hay incremento.
        """
        return self._incremento_segundos

    @property
    def necesita_anotacion(self) -> bool:
        """
        Indica si este modo de juego requiere que los movimientos sean anotados
        según las reglas estándar (principalmente para 'Clásico').
        La lógica de la anotación en sí residiría en la Vista/Controlador.
        """
        return self._requiere_anotacion

    # --- Consideraciones Adicionales (No implementadas aquí directamente) ---
    # La gestión del paso del tiempo y la aplicación de incrementos es responsabilidad
    # de la clase 'Temporizador'. Esta clase 'ConfiguracionJuego' sólo *provee* los
    # parámetros iniciales (tiempo base e incremento) que el 'Temporizador' debe usar.
    
    # La determinación del final de la partida por tiempo agotado también recae en
    # la clase 'Juego' o 'Controlador', quienes consultarían el estado del 'Temporizador'.
    # El final por jaque mate, ahogado, tablas, etc., es determinado por la lógica
    # del juego (probablemente en 'Juego' o 'EvaluadorEstadoDeJuego'), no por esta
    # clase de configuración.
    
    # La lógica específica para las reglas de Blitz (ej. manejo de jugadas ilegales)
    # tendría que implementarse en las clases que gestionan la validación y ejecución
    # de movimientos ('ValidadorMovimiento', 'EjecutorMovimiento', 'Juego'), quienes
    # podrían consultar `self.tipo_partida` de esta configuración si fuera necesario
    # para aplicar reglas diferentes.