# -*- coding: utf-8 -*-

"""
Tests para la clase base abstracta Pieza.
Estos tests verifican la funcionalidad común heredada por todas las piezas.
"""

import pytest
from model.tablero import Tablero
from model.piezas.pieza import Pieza
from model.piezas.peon import Peon # Usamos Peon como ejemplo concreto
from model.piezas.torre import Torre # Usamos Torre para variedad
import os # Importar os para normalizar rutas

# --- Fixtures ---
@pytest.fixture
def tablero_vacio():
    """
    Proporciona una instancia limpia del tablero para cada test.
    """
    return Tablero()

@pytest.fixture
def peon_blanco(tablero_vacio):
    """
    Proporciona una instancia de Peon blanco para tests.
    """
    # Asegurarse de pasar el tablero a la fixture también
    return Peon('blanco', (1, 0), tablero_vacio)

@pytest.fixture
def torre_negra(tablero_vacio):
    """
    Proporciona una instancia de Torre negra para tests.
    """
     # Asegurarse de pasar el tablero a la fixture también
    return Torre('negro', (7, 7), tablero_vacio)

# --- Tests para Pieza ---

def test_inicializacion_pieza(peon_blanco, torre_negra, tablero_vacio):
    """
    Verifica que los atributos básicos se inicialicen correctamente
    a través del constructor de Pieza.
    """
    # Test con Peon
    assert peon_blanco.color == 'blanco'
    assert peon_blanco.posicion == (1, 0)
    assert peon_blanco.tablero is tablero_vacio
    # La comprobación de se_ha_movido/primer_movimiento puede variar por pieza, mejor en tests específicos
    # assert not peon_blanco.se_ha_movido
    assert isinstance(peon_blanco.imagen, str) # Verificar que se asigna una ruta de imagen
    # Comprobación case-insensitive del nombre del archivo
    assert "peon blanco.png".lower() in peon_blanco.imagen.lower() # <- Comprobación case-insensitive

    # Test con Torre
    assert torre_negra.color == 'negro'
    assert torre_negra.posicion == (7, 7)
    assert torre_negra.tablero is tablero_vacio
    # La comprobación de se_ha_movido/movida puede variar, mejor en test_torre.py
    # assert not torre_negra.se_ha_movido
    assert isinstance(torre_negra.imagen, str)
    # Comprobación case-insensitive del nombre del archivo
    assert "torre negro.png".lower() in torre_negra.imagen.lower() # <- Comprobación case-insensitive


def test_representacion_str_repr(peon_blanco, torre_negra):
    """
    Verifica las representaciones en string (__str__ y __repr__) de la pieza.
    """
    assert str(peon_blanco) == "Peon blanco en (1, 0)"
    # __repr__ usa el símbolo y formato específico
    # Asegúrate que el símbolo 'P' es correcto según tu implementación de Peon.obtener_simbolo()
    assert repr(peon_blanco) == "P(b, 10)"

    assert str(torre_negra) == "Torre negro en (7, 7)"
    # Corregido: Usar 'R' para Torre en repr
    assert repr(torre_negra) == "R(n, 77)" # <- Corregido a 'R'


def test_obtener_notacion_fen(peon_blanco, torre_negra):
    """
    Verifica que la notación FEN/Algebraica se obtenga correctamente.
    Por defecto llama a obtener_simbolo().
    """
    # Asegúrate que el símbolo 'P' es correcto según tu implementación de Peon.obtener_simbolo()
    assert peon_blanco.obtenerNotacionFEN() == 'P'
    # Corregido: Usar 'R' para Torre en FEN
    assert torre_negra.obtenerNotacionFEN() == 'R' # <- Corregido a 'R'

def test_metodos_abstractos_requieren_implementacion():
    """
    Verifica que intentar llamar a los métodos abstractos directamente
    (si fuera posible crear una instancia de Pieza pura o una subclase incompleta)
    lanzaría NotImplementedError.
    NOTA: En la práctica, testeamos que las subclases *sí* los implementan.
    Este test es más conceptual. Una forma sería crear una subclase ad-hoc:
    """
    class PiezaIncompleta(Pieza):
        # No implementa obtener_simbolo ni obtener_movimientos_potenciales
        def __init__(self, color, posicion, tablero):
             # Llama al init base, pero no define imagen ni símbolo específico
            super().__init__(color, posicion, tablero)
            # Necesitamos definir imagen aquí o _construir_ruta_imagen fallará si se llama
            # El __init__ base llama a _construir_ruta_imagen si self.imagen es None
            # Pero _construir_ruta_imagen depende del nombre de la clase, que aquí es 'PiezaIncompleta'
            # Para evitar fallos aquí, asignamos una ruta dummy explícita.
            self.imagen = "dummy.png"


    tablero = Tablero()
    pieza_test = PiezaIncompleta('blanco', (0,0), tablero)

    with pytest.raises(NotImplementedError):
        pieza_test.obtener_simbolo()

    with pytest.raises(NotImplementedError):
        pieza_test.obtener_movimientos_potenciales()

def test_construir_ruta_imagen(peon_blanco, torre_negra):
    """
    Verifica la lógica interna (si se considera necesario testearla)
    de construcción de la ruta de imagen.
    """
    # _construir_ruta_imagen es llamado indirectamente por el __init__
    # de las subclases generalmente. Podemos llamarlo explícitamente para test.
    # Asegurarse de que la comparación sea robusta a separadores de path (\ vs /) y case.
    ruta_esperada_peon = os.path.join("assets", "imagenes_piezas", "Peon blanco.png").lower()
    ruta_actual_peon = peon_blanco._construir_ruta_imagen().lower()
    assert os.path.normpath(ruta_actual_peon) == os.path.normpath(ruta_esperada_peon)

    ruta_esperada_torre = os.path.join("assets", "imagenes_piezas", "Torre negro.png").lower()
    ruta_actual_torre = torre_negra._construir_ruta_imagen().lower()
    assert os.path.normpath(ruta_actual_torre) == os.path.normpath(ruta_esperada_torre)


# NOTA: Testear obtener_movimientos_legales de la clase base Pieza es complejo
# porque depende fuertemente de obtener_movimientos_potenciales (abstracto)
# y de la lógica de simulación del tablero (_simular_y_verificar_seguridad).
# Es más efectivo testear obtener_movimientos_legales en cada subclase concreta
# (test_peon.py, test_torre.py, etc.) donde los movimientos potenciales están definidos. 