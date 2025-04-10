"""
Inicializador del paquete para la lógica específica de las piezas.
"""

from .pieza import Pieza
from .alfil import Alfil
from .caballo import Caballo
from .peon import Peon
from .reina import Reina
from .rey import Rey
from .torre import Torre

__all__ = ['Pieza', 'Alfil', 'Caballo', 'Peon', 'Reina', 'Rey', 'Torre'] 