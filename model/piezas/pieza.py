"""
Clase base para todas las piezas de ajedrez.
""" 

import logging
from typing import Literal, Tuple, TYPE_CHECKING, List, Optional
import os # Importar os para manejo de rutas

# Evitar importación circular para type hints con referencias adelantadas
if TYPE_CHECKING:
    from model.tablero import Tablero

# Configuración básica del logging (puedes ajustar el nivel y formato según necesites)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pieza:
    """
    Clase base para todas las piezas de ajedrez.
    """
    def __init__(self, color: Literal['blanco', 'negro'], posicion: Tuple[int, int], tablero: 'Tablero'):
        """
        Inicializa una pieza.

        Args:
            color: El color de la pieza ('blanco' o 'negro').
            posicion: Una tupla (fila, columna) indicando la posición inicial.
            tablero: La instancia del tablero en la que se encuentra la pieza.
        """
        self.color: Literal['blanco', 'negro'] = color
        self.posicion: Tuple[int, int] = posicion
        self.tablero: 'Tablero' = tablero
        self.se_ha_movido: bool = False
        self.imagen: Optional[str] = None # Atributo para la ruta de la imagen, inicializado a None
        # Las subclases deben establecer la ruta correcta en sus __init__
        # Ejemplo en subclase: self.imagen = self._construir_ruta_imagen()

    def obtener_simbolo(self) -> str:
        """
        Método abstracto para obtener el símbolo de la pieza (p.ej., 'K', 'q', 'P').
        Las subclases DEBEN implementar este método.
        """
        raise NotImplementedError("Las subclases deben implementar obtener_simbolo()")

    def obtener_movimientos_potenciales(self) -> List[Tuple[int, int]]:
        """
        Método abstracto para obtener todos los movimientos 'brutos' (potenciales)
        que la pieza podría hacer desde su posición actual, sin considerar
        jaques, obstrucciones complejas o reglas especiales como el enroque.
        Las subclases DEBEN implementar este método.

        Returns:
            Una lista de tuplas (fila, columna) representando las casillas destino potenciales.
        """
        raise NotImplementedError("Las subclases deben implementar obtener_movimientos_potenciales()")

    def obtener_movimientos_legales(self) -> List[Tuple[int, int]]:
        """
        Calcula todos los movimientos legales para esta pieza en la posición actual del tablero.
        Este método considera:
        1. Movimientos base/potenciales de la pieza.
        2. Obstrucciones por piezas del mismo color.
        3. Capturas de piezas del color opuesto.
        4. Que el movimiento no deje al propio rey en jaque.
        5. Reglas especiales (enroque, al paso) - gestionadas aquí o en métodos específicos llamados desde aquí.

        Returns:
            Una lista de tuplas (fila, columna) representando las casillas destino legales.
        """
        movimientos_legales = []
        # 1. Obtener movimientos potenciales (definidos en subclase)
        # ¡Importante! Obtener potenciales primero para no recalcular en cada simulación
        movimientos_potenciales = self.obtener_movimientos_potenciales()

        # 2. Filtrar movimientos potenciales
        for destino in movimientos_potenciales:
            # 2a. Verificar si está dentro del tablero 
            if not self.tablero.esPosicionValida(destino):
                continue

            # 2b. Verificar si la casilla destino está ocupada por pieza propia
            pieza_en_destino = self.tablero.getPieza(destino)
            if pieza_en_destino is not None and pieza_en_destino.color == self.color:
                continue # No se puede mover a casilla ocupada por pieza propia

            # 2c. Simular el movimiento y verificar si deja al rey en jaque (¡NUEVO!)
            if self.tablero._simular_y_verificar_seguridad(self, destino):
                # Solo añadir el movimiento si el rey está seguro después de él
                movimientos_legales.append(destino)

        # 3. Considerar movimientos especiales (Enroque, Al Paso)
        # Estos deben manejarse en las clases Rey y Peón, quienes sobreescribirán este método
        # o añadirán su lógica específica aquí si no lo sobreescriben completamente.

        return movimientos_legales

    def obtenerNotacionFEN(self) -> str:
        """
        Devuelve la notación FEN/Algebraica estándar para la pieza.
        Llama a obtener_simbolo() por defecto.
        """
        # Por defecto, la notación FEN usa el mismo símbolo que definimos
        # Peones ('P') usan mayúscula, las otras piezas también. El color
        # se determina en Tablero.obtenerPosicionActual con upper/lower case.
        return self.obtener_simbolo()

    def __str__(self) -> str:
        """ Representación informal de la pieza. """
        return f"{type(self).__name__} {self.color} en {self.posicion}"

    def __repr__(self) -> str:
        """ Representación más técnica de la pieza. """
        try:
            simbolo = self.obtener_simbolo()
        except NotImplementedError:
            simbolo = "?" # Símbolo por defecto si la subclase aún no lo implementa
        return f"{simbolo}({self.color[0]}, {self.posicion[0]}{self.posicion[1]})"

    def _construir_ruta_imagen(self) -> str:
        """
        Construye la ruta relativa a la imagen de la pieza.
        Este método espera que las subclases definan self.nombre_archivo_imagen.
        ¡Atención! Este método es un EJEMPLO y las subclases deben adaptarlo
        o implementar su propia lógica para definir la ruta.
        """
        # Obtener el nombre base de la clase (p. ej., 'Peon', 'Torre')
        nombre_clase = type(self).__name__

        # Asumiremos 'NombreClase color.png' como convención aquí.
        nombre_archivo = f"{nombre_clase} {self.color}.png"

        # Construir ruta relativa desde la raíz del proyecto
        ruta_base = os.path.join("assets", "imagenes_piezas")
        ruta_imagen = os.path.join(ruta_base, nombre_archivo)

        # Opcional: Verificar si el archivo existe
        # ruta_absoluta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) # Ir 3 niveles arriba desde piezas/pieza.py
        # ruta_absoluta_imagen = os.path.join(ruta_absoluta_proyecto, ruta_imagen)
        # if not os.path.exists(ruta_absoluta_imagen):
        #     logger.warning(f"Archivo de imagen no encontrado en la ruta esperada: {ruta_absoluta_imagen}. Buscando variaciones...")
            # Aquí se podría intentar buscar con las `posibles_nombres`
            # Por simplicidad, devolvemos la ruta esperada directamente.

        return ruta_imagen



