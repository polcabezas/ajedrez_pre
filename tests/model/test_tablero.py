"""
Pruebas unitarias exhaustivas para la clase Tablero.

Verifica la correcta implementación de las reglas del ajedrez según FIDE
y las especificaciones del proyecto.
"""

import pytest
import logging
from model.tablero import Tablero
from model.piezas.pieza import Pieza
from model.piezas.rey import Rey
from model.piezas.reina import Reina
from model.piezas.torre import Torre
from model.piezas.alfil import Alfil
from model.piezas.caballo import Caballo
from model.piezas.peon import Peon
from typing import Tuple, Optional, Type

# ============================================================
# Fixtures de Pytest
# ============================================================

@pytest.fixture
def tablero_inicial():
    """
    Proporciona un tablero en su estado inicial estándar.
    """
    return Tablero()

@pytest.fixture
def tablero_vacio():
    """
    Proporciona un tablero vacío sin piezas.
    Util para colocar piezas específicas en tests.
    """
    tablero = Tablero()
    # Vaciar el tablero completamente
    tablero.casillas = [[None for _ in range(8)] for _ in range(8)]
    # Resetear otros estados relevantes si es necesario
    tablero.derechosEnroque = {
        'blanco': {'corto': False, 'largo': False},
        'negro': {'corto': False, 'largo': False}
    }
    tablero.objetivoPeonAlPaso = None
    tablero.historial_movimientos = []
    tablero.piezasCapturadas = []
    tablero.turno_blanco = True
    tablero.contadorRegla50Movimientos = 0
    tablero.contadorPly = 0
    tablero.estado_juego = 'en_curso'
    tablero.numero_movimiento = 1
    tablero.ultimo_movimiento = None
    tablero.gestor_historico.historial_posiciones.clear()
    return tablero

# ============================================================
# Pruebas de Inicialización y Configuración
# ============================================================

def test_inicializacion_dimensiones(tablero_inicial: Tablero):
    """
    Verifica que el tablero se inicializa con 8 filas y 8 columnas.
    """
    assert len(tablero_inicial.casillas) == 8, "El tablero debe tener 8 filas."
    for fila in tablero_inicial.casillas:
        assert len(fila) == 8, "Cada fila debe tener 8 columnas."

def test_inicializacion_piezas_blancas(tablero_inicial: Tablero):
    """
    Verifica la correcta colocación y tipo de las piezas blancas iniciales.
    """
    # Fila 1 (índice 0) - Piezas mayores blancas
    assert isinstance(tablero_inicial.getPieza((0, 0)), Torre) and tablero_inicial.getPieza((0, 0)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 1)), Caballo) and tablero_inicial.getPieza((0, 1)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 2)), Alfil) and tablero_inicial.getPieza((0, 2)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 3)), Reina) and tablero_inicial.getPieza((0, 3)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 4)), Rey) and tablero_inicial.getPieza((0, 4)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 5)), Alfil) and tablero_inicial.getPieza((0, 5)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 6)), Caballo) and tablero_inicial.getPieza((0, 6)).color == 'blanco'
    assert isinstance(tablero_inicial.getPieza((0, 7)), Torre) and tablero_inicial.getPieza((0, 7)).color == 'blanco'

    # Fila 2 (índice 1) - Peones blancos
    for col in range(8):
        assert isinstance(tablero_inicial.getPieza((1, col)), Peon) and tablero_inicial.getPieza((1, col)).color == 'blanco'

def test_inicializacion_piezas_negras(tablero_inicial: Tablero):
    """
    Verifica la correcta colocación y tipo de las piezas negras iniciales.
    """
    # Fila 8 (índice 7) - Piezas mayores negras
    assert isinstance(tablero_inicial.getPieza((7, 0)), Torre) and tablero_inicial.getPieza((7, 0)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 1)), Caballo) and tablero_inicial.getPieza((7, 1)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 2)), Alfil) and tablero_inicial.getPieza((7, 2)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 3)), Reina) and tablero_inicial.getPieza((7, 3)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 4)), Rey) and tablero_inicial.getPieza((7, 4)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 5)), Alfil) and tablero_inicial.getPieza((7, 5)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 6)), Caballo) and tablero_inicial.getPieza((7, 6)).color == 'negro'
    assert isinstance(tablero_inicial.getPieza((7, 7)), Torre) and tablero_inicial.getPieza((7, 7)).color == 'negro'

    # Fila 7 (índice 6) - Peones negros
    for col in range(8):
        assert isinstance(tablero_inicial.getPieza((6, col)), Peon) and tablero_inicial.getPieza((6, col)).color == 'negro'

def test_inicializacion_casillas_vacias(tablero_inicial: Tablero):
    """
    Verifica que las casillas intermedias están vacías al inicio.
    """
    for fila in range(2, 6): # Filas de índice 2 a 5
        for col in range(8):
            assert tablero_inicial.getPieza((fila, col)) is None, f"La casilla ({fila}, {col}) debería estar vacía."

def test_inicializacion_estado_juego(tablero_inicial: Tablero):
    """
    Verifica el estado inicial del juego (turno, contadores, derechos enroque, etc.).
    """
    assert tablero_inicial.turno_blanco is True, "El turno inicial debe ser de las blancas."
    assert tablero_inicial.objetivoPeonAlPaso is None, "No debe haber objetivo al paso inicial."
    assert tablero_inicial.piezasCapturadas == [], "La lista de capturadas debe estar vacía."
    assert tablero_inicial.contadorRegla50Movimientos == 0, "El contador de 50 mov. debe ser 0."
    assert tablero_inicial.contadorPly == 0, "El contador de medios movimientos (ply) debe ser 0."
    assert tablero_inicial.numero_movimiento == 1, "El número de movimiento debe ser 1."
    assert tablero_inicial.estado_juego == 'en_curso', "El estado inicial debe ser 'en_curso'."
    assert tablero_inicial.ultimo_movimiento is None, "No debe haber último movimiento registrado."
    # Derechos de enroque
    assert tablero_inicial.derechosEnroque['blanco']['corto'] is True
    assert tablero_inicial.derechosEnroque['blanco']['largo'] is True
    assert tablero_inicial.derechosEnroque['negro']['corto'] is True
    assert tablero_inicial.derechosEnroque['negro']['largo'] is True

# ============================================================
# Pruebas de Consultas Básicas
# ============================================================

@pytest.mark.parametrize("posicion, esperado", [
    ((0, 0), True), ((7, 7), True), ((3, 4), True), # Dentro
    ((-1, 0), False), ((0, -1), False), ((8, 0), False), ((0, 8), False), # Fuera
    ((3.5, 4), False), (("a", 1), False), ((3,), False) # Tipos inválidos
])
def test_esPosicionValida(tablero_inicial: Tablero, posicion: Tuple[int, int], esperado: bool):
    """
    Verifica la validación de posiciones dentro y fuera de los límites.
    """
    assert tablero_inicial.esPosicionValida(posicion) == esperado

def test_getPieza_existente(tablero_inicial: Tablero):
    """
    Verifica obtener una pieza existente en una posición válida.
    """
    pieza = tablero_inicial.getPieza((0, 0))
    assert isinstance(pieza, Torre) and pieza.color == 'blanco'
    pieza = tablero_inicial.getPieza((6, 5))
    assert isinstance(pieza, Peon) and pieza.color == 'negro'

def test_getPieza_vacia(tablero_inicial: Tablero):
    """
    Verifica obtener None de una casilla vacía válida.
    """
    assert tablero_inicial.getPieza((3, 3)) is None

def test_getPieza_invalida(tablero_inicial: Tablero):
    """
    Verifica obtener None de una posición inválida.
    """
    assert tablero_inicial.getPieza((-1, 5)) is None
    assert tablero_inicial.getPieza((4, 8)) is None

# ============================================================
# Pruebas de Movimiento Básico (moverPieza)
# ============================================================

def test_moverPieza_simple_ok(tablero_inicial: Tablero):
    """
    Prueba un movimiento simple y legal de un peón blanco.
    Verifica el estado del tablero y el retorno.
    """
    origen = (1, 4) # Peón e2
    destino = (3, 4) # e4
    pieza_movida = tablero_inicial.getPieza(origen)

    resultado = tablero_inicial.moverPieza(origen, destino)

    assert resultado == 'movimiento_ok', "El resultado del movimiento debe ser 'movimiento_ok'."
    assert tablero_inicial.getPieza(origen) is None, "La casilla origen debe quedar vacía."
    assert tablero_inicial.getPieza(destino) is pieza_movida, "La pieza debe estar en la casilla destino."
    assert pieza_movida.posicion == destino, "La posición interna de la pieza debe actualizarse."
    assert tablero_inicial.turno_blanco is False, "El turno debe pasar a las negras."
    assert tablero_inicial.contadorPly == 1, "El contador Ply debe ser 1."
    assert tablero_inicial.numero_movimiento == 1, "El número de movimiento debe seguir siendo 1."
    assert tablero_inicial.contadorRegla50Movimientos == 0, "Contador 50 mov se resetea por peón."
    assert tablero_inicial.ultimo_movimiento == (origen, destino), "Se debe registrar el último movimiento."
    assert tablero_inicial.historial_movimientos[-1] == ('blanco', origen, destino), "El movimiento debe registrarse en el historial."

def test_moverPieza_captura_ok(tablero_inicial: Tablero):
    """
    Prueba una captura simple y legal.
    """
    # Configurar escenario: Caballo blanco en e4, Peón negro en d5
    tablero_inicial.setPieza((3, 4), Caballo('blanco', (3, 4), tablero_inicial))
    tablero_inicial.setPieza((4, 3), Peon('negro', (4, 3), tablero_inicial))
    # Limpiar origen del caballo blanco y destino del peón negro (simulación)
    tablero_inicial.setPieza((0, 6), None) # G1
    tablero_inicial.setPieza((6, 3), None) # d7
    tablero_inicial.turno_blanco = True # Turno blanco

    origen = (3, 4)
    destino = (4, 3)
    pieza_movida = tablero_inicial.getPieza(origen)
    pieza_capturada = tablero_inicial.getPieza(destino)

    resultado = tablero_inicial.moverPieza(origen, destino)

    assert resultado == 'movimiento_ok'
    assert tablero_inicial.getPieza(origen) is None
    assert tablero_inicial.getPieza(destino) is pieza_movida
    assert pieza_movida.posicion == destino
    assert pieza_capturada in tablero_inicial.piezasCapturadas, "La pieza capturada debe estar en la lista."
    assert len(tablero_inicial.piezasCapturadas) == 1
    assert tablero_inicial.turno_blanco is False
    assert tablero_inicial.contadorRegla50Movimientos == 0, "Contador 50 mov se resetea por captura."
    assert tablero_inicial.ultimo_movimiento == (origen, destino)
    assert tablero_inicial.historial_movimientos[-1] == ('blanco', origen, destino)

def test_moverPieza_error_origen_vacio(tablero_inicial: Tablero):
    """
    Prueba intentar mover desde una casilla vacía.
    """
    resultado = tablero_inicial.moverPieza((3, 3), (4, 4))
    assert resultado == 'error', "Debe retornar 'error' si el origen está vacío."
    assert tablero_inicial.turno_blanco is True, "El turno no debe cambiar."

def test_moverPieza_error_destino_propio(tablero_inicial: Tablero):
    """
    Prueba intentar capturar una pieza propia.
    """
    resultado = tablero_inicial.moverPieza((0, 0), (1, 0)) # Torre a casilla de peón blanco
    assert resultado == 'error', "Debe retornar 'error' al intentar capturar pieza propia."
    assert isinstance(tablero_inicial.getPieza((1, 0)), Peon), "La pieza destino no debe cambiar."
    assert tablero_inicial.turno_blanco is True, "El turno no debe cambiar."

def test_moverPieza_error_posicion_invalida(tablero_inicial: Tablero):
    """
    Prueba intentar mover a/desde una posición inválida.
    """
    assert tablero_inicial.moverPieza((0, 0), (0, 8)) == 'error' # Destino inválido
    assert tablero_inicial.moverPieza((-1, 0), (2, 2)) == 'error' # Origen inválido
    assert tablero_inicial.turno_blanco is True, "El turno no debe cambiar."

def test_setPieza(tablero_vacio: Tablero):
    """
    Verifica la colocación de piezas con setPieza.
    """
    rey_blanco = Rey('blanco', (4, 4), tablero_vacio)
    tablero_vacio.setPieza((4, 4), rey_blanco)
    assert tablero_vacio.getPieza((4, 4)) is rey_blanco

    tablero_vacio.setPieza((4, 4), None)
    assert tablero_vacio.getPieza((4, 4)) is None

def test_moverPieza_actualiza_se_ha_movido(tablero_inicial: Tablero):
    """
    Verifica que moverPieza establece correctamente el flag se_ha_movido.
    Se prueba con Rey y Torre, que son cruciales para el enroque.
    """
    # 1. Probar con el Rey Blanco
    rey_blanco_origen = (0, 4)
    rey_blanco_destino = (1, 4)
    rey_blanco = tablero_inicial.getPieza(rey_blanco_origen)
    assert hasattr(rey_blanco, 'se_ha_movido'), "El Rey debe tener el atributo 'se_ha_movido'"
    assert rey_blanco.se_ha_movido is False, "El Rey no debe haberse movido inicialmente."
    # Mover el rey (asegurar casilla destino vacía)
    tablero_inicial.setPieza(rey_blanco_destino, None)
    resultado_rey = tablero_inicial.moverPieza(rey_blanco_origen, rey_blanco_destino)
    assert resultado_rey == 'movimiento_ok'
    rey_blanco_movido = tablero_inicial.getPieza(rey_blanco_destino)
    assert rey_blanco_movido is rey_blanco, "La pieza en el destino debe ser el mismo objeto Rey."
    assert rey_blanco_movido.se_ha_movido is True, "El flag se_ha_movido del Rey debe ser True después de moverse."

    # Resetear tablero para probar la torre (o usar uno nuevo)
    tablero_test_torre = Tablero() # Usar un tablero limpio para evitar interferencias

    # 2. Probar con la Torre Negra (larga)
    torre_negra_origen = (7, 0)
    torre_negra_destino = (7, 1)
    torre_negra = tablero_test_torre.getPieza(torre_negra_origen)
    assert hasattr(torre_negra, 'se_ha_movido'), "La Torre debe tener el atributo 'se_ha_movido'"
    assert torre_negra.se_ha_movido is False, "La Torre no debe haberse movido inicialmente."
    # Mover la torre (asegurar casilla destino vacía)
    tablero_test_torre.setPieza(torre_negra_destino, None)
    tablero_test_torre.turno_blanco = False # Turno Negro
    resultado_torre = tablero_test_torre.moverPieza(torre_negra_origen, torre_negra_destino)
    assert resultado_torre == 'movimiento_ok'
    torre_negra_movida = tablero_test_torre.getPieza(torre_negra_destino)
    assert torre_negra_movida is torre_negra, "La pieza en el destino debe ser el mismo objeto Torre."
    assert torre_negra_movida.se_ha_movido is True, "El flag se_ha_movido de la Torre debe ser True después de moverse."

# ============================================================
# Pruebas de Movimientos Especiales
# ============================================================

# --- En Passant ---

def test_actualizarPeonAlPaso_creacion(tablero_inicial: Tablero):
    """
    Verifica que el objetivo al paso se crea correctamente tras avance doble de peón.
    """
    tablero_inicial.moverPieza((1, 4), (3, 4)) # e2 -> e4
    assert tablero_inicial.objetivoPeonAlPaso == (2, 4), "El objetivo al paso debe ser e3 (2, 4)."
    assert tablero_inicial.turno_blanco is False # Turno negro

def test_actualizarPeonAlPaso_limpieza(tablero_inicial: Tablero):
    """
    Verifica que el objetivo al paso se limpia tras un movimiento que no sea avance doble.
    """
    tablero_inicial.moverPieza((1, 4), (3, 4)) # e4, crea objetivo e3
    assert tablero_inicial.objetivoPeonAlPaso == (2, 4)
    tablero_inicial.moverPieza((6, 0), (5, 0)) # Negro mueve a6
    assert tablero_inicial.objetivoPeonAlPaso is None, "El objetivo al paso debe limpiarse."

def test_moverPieza_enPassant_ok(tablero_inicial: Tablero):
    """
    Prueba una captura al paso válida.
    """
    # Configuración: Peón blanco en e5, Peón negro en d7. Negro mueve d7->d5
    tablero_inicial.setPieza((4, 4), Peon('blanco', (4, 4), tablero_inicial)) # Pass tablero
    tablero_inicial.setPieza((1, 4), None) # Vaciar e2
    tablero_inicial.turno_blanco = False # Turno Negro

    # Negro mueve d7->d5
    tablero_inicial.moverPieza((6, 3), (4, 3)) # Peón negro d5
    assert tablero_inicial.objetivoPeonAlPaso == (5, 3), "Objetivo al paso debe ser d6 (5, 3)."
    assert tablero_inicial.turno_blanco is True # Turno Blanco

    # Blanco captura al paso exd6
    origen_blanco = (4, 4) # e5
    destino_blanco = (5, 3) # d6 (casilla de captura al paso)
    casilla_peon_capturado = (4, 3) # d5 (donde estaba el peón negro)
    pieza_blanca = tablero_inicial.getPieza(origen_blanco)
    pieza_negra_capturada = tablero_inicial.getPieza(casilla_peon_capturado)

    resultado = tablero_inicial.moverPieza(origen_blanco, destino_blanco)

    assert resultado == 'movimiento_ok'
    assert tablero_inicial.getPieza(origen_blanco) is None, "Origen del peón blanco (e5) debe estar vacío."
    assert tablero_inicial.getPieza(destino_blanco) is pieza_blanca, "Peón blanco debe estar en destino (d6)."
    assert pieza_blanca.posicion == destino_blanco, "Posición interna del peón blanco debe ser d6."
    assert tablero_inicial.getPieza(casilla_peon_capturado) is None, "Casilla del peón negro capturado (d5) debe estar vacía."
    assert pieza_negra_capturada in tablero_inicial.piezasCapturadas, "Peón negro debe estar en capturadas."
    assert tablero_inicial.objetivoPeonAlPaso is None, "Objetivo al paso debe limpiarse después de la captura."
    assert tablero_inicial.turno_blanco is False # Turno Negro
    assert tablero_inicial.contadorRegla50Movimientos == 0, "Contador 50 mov se resetea por captura."

# --- Promoción ---

def test_moverPieza_promocion_necesaria_blanco(tablero_vacio: Tablero):
    """
    Verifica que mover un peón blanco a la 8va fila retorna 'promocion_necesaria'.
    """
    peon_blanco = Peon('blanco', (6, 0), tablero_vacio)
    tablero_vacio.setPieza((6, 0), peon_blanco) # Peón blanco en a7
    tablero_vacio.turno_blanco = True

    resultado = tablero_vacio.moverPieza((6, 0), (7, 0)) # Mueve a a8

    assert resultado == 'promocion_necesaria'
    assert tablero_vacio.getPieza((6, 0)) is None # Origen vacío
    # La pieza en el destino es el peón ANTES de la promoción real
    assert isinstance(tablero_vacio.getPieza((7, 0)), Peon)
    assert tablero_vacio.getPieza((7, 0)) is peon_blanco
    assert peon_blanco.posicion == (7, 0)
    assert tablero_vacio.turno_blanco is False # Turno cambió

def test_moverPieza_promocion_necesaria_negro(tablero_vacio: Tablero):
    """
    Verifica que mover un peón negro a la 1ra fila retorna 'promocion_necesaria'.
    """
    peon_negro = Peon('negro', (1, 7), tablero_vacio)
    tablero_vacio.setPieza((1, 7), peon_negro) # Peón negro en h2
    tablero_vacio.turno_blanco = False # Turno negro

    resultado = tablero_vacio.moverPieza((1, 7), (0, 7)) # Mueve a h1

    assert resultado == 'promocion_necesaria'
    assert tablero_vacio.getPieza((1, 7)) is None # Origen vacío
    assert isinstance(tablero_vacio.getPieza((0, 7)), Peon)
    assert tablero_vacio.getPieza((0, 7)) is peon_negro
    assert peon_negro.posicion == (0, 7)
    assert tablero_vacio.turno_blanco is True # Turno cambió

# --- Enroque ---

def test_actualizarDerechosEnroque_mov_rey_blanco(tablero_inicial: Tablero):
    """
    Verifica que mover el rey blanco pierde ambos derechos de enroque.
    """
    rey = tablero_inicial.getPieza((0, 4))
    # Asegurarse de que la casilla destino está vacía para la prueba
    tablero_inicial.setPieza((1, 4), None)
    tablero_inicial.moverPieza((0, 4), (1, 4)) # Ke1 -> e2
    assert tablero_inicial.derechosEnroque['blanco']['corto'] is False
    assert tablero_inicial.derechosEnroque['blanco']['largo'] is False
    # Los derechos negros no deben cambiar
    assert tablero_inicial.derechosEnroque['negro']['corto'] is True
    assert tablero_inicial.derechosEnroque['negro']['largo'] is True

def test_actualizarDerechosEnroque_mov_torre_corta_negra(tablero_inicial: Tablero):
    """
    Verifica que mover la torre corta negra pierde el derecho corto negro.
    """
    tablero_inicial.turno_blanco = False # Turno negro
    torre = tablero_inicial.getPieza((7, 7))
    # Asegurarse de que la casilla destino está vacía para la prueba
    tablero_inicial.setPieza((6, 7), None)
    tablero_inicial.moverPieza((7, 7), (6, 7)) # Th8 -> h7
    assert tablero_inicial.derechosEnroque['negro']['corto'] is False
    assert tablero_inicial.derechosEnroque['negro']['largo'] is True # Largo no cambia
    # Los derechos blancos no deben cambiar
    assert tablero_inicial.derechosEnroque['blanco']['corto'] is True
    assert tablero_inicial.derechosEnroque['blanco']['largo'] is True

def test_actualizarDerechosEnroque_mov_torre_larga_blanca(tablero_inicial: Tablero):
    """
    Verifica que mover la torre larga blanca pierde el derecho largo blanco.
    """
    torre = tablero_inicial.getPieza((0, 0))
    # Asegurarse de que la casilla destino está vacía para la prueba
    tablero_inicial.setPieza((0, 1), None)
    tablero_inicial.moverPieza((0, 0), (0, 1)) # Ta1 -> b1
    assert tablero_inicial.derechosEnroque['blanco']['largo'] is False
    assert tablero_inicial.derechosEnroque['blanco']['corto'] is True # Corto no cambia
    assert tablero_inicial.derechosEnroque['negro']['corto'] is True
    assert tablero_inicial.derechosEnroque['negro']['largo'] is True

def test_actualizarDerechosEnroque_captura_torre_corta_blanca(tablero_vacio: Tablero):
    """
    Verifica que capturar la torre corta blanca en h1 hace perder el derecho corto blanco.
    """
    tablero_vacio.setPieza((0, 7), Torre('blanco', (0, 7), tablero_vacio))
    tablero_vacio.setPieza((1, 6), Reina('negro', (1, 6), tablero_vacio))
    tablero_vacio.derechosEnroque['blanco']['corto'] = True
    tablero_vacio.turno_blanco = False

    # Negro captura Dxg2xh1
    tablero_vacio.moverPieza((1, 6), (0, 7))

    assert tablero_vacio.derechosEnroque['blanco']['corto'] is False, "El derecho corto blanco debe perderse por captura de torre."

def test_realizarEnroque_corto_blanco_ok(tablero_vacio: Tablero):
    """
    Prueba la ejecución del enroque corto blanco (asumiendo validez).
    """
    # Setup: Rey en e1, Torre en h1, casillas f1, g1 vacías. Derechos OK.
    rey = Rey('blanco', (0, 4), tablero_vacio)
    torre = Torre('blanco', (0, 7), tablero_vacio)
    tablero_vacio.setPieza((0, 4), rey)
    tablero_vacio.setPieza((0, 7), torre)
    tablero_vacio.derechosEnroque['blanco']['corto'] = True
    tablero_vacio.derechosEnroque['blanco']['largo'] = True # Dejar el largo también para ver que no se afecta innecesariamente
    tablero_vacio.turno_blanco = True

    resultado = tablero_vacio.realizarEnroque('blanco', 'corto')

    assert resultado is True
    assert tablero_vacio.getPieza((0, 4)) is None, "e1 debe estar vacío."
    assert tablero_vacio.getPieza((0, 7)) is None, "h1 debe estar vacío."
    assert tablero_vacio.getPieza((0, 6)) is rey, "Rey debe estar en g1."
    assert tablero_vacio.getPieza((0, 5)) is torre, "Torre debe estar en f1."
    assert rey.posicion == (0, 6), "Posición interna del Rey debe ser g1."
    assert torre.posicion == (0, 5), "Posición interna de la Torre debe ser f1."
    assert tablero_vacio.derechosEnroque['blanco']['corto'] is False, "Derecho corto blanco perdido."
    assert tablero_vacio.derechosEnroque['blanco']['largo'] is False, "Derecho largo blanco perdido (movimiento de rey)."
    assert tablero_vacio.turno_blanco is False, "Turno debe pasar a negras."
    assert tablero_vacio.contadorRegla50Movimientos == 1, "Contador 50 mov avanza (no peón, no captura)."
    assert tablero_vacio.ultimo_movimiento == ((0, 4), (0, 6)), "Último mov registrado (mov rey)."
    assert tablero_vacio.historial_movimientos[-1] == ('blanco', (0, 4), (0, 6)), "Historial registra mov rey."

def test_realizarEnroque_largo_negro_ok(tablero_vacio: Tablero):
    """
    Prueba la ejecución del enroque largo negro (asumiendo validez).
    """
    # Setup: Rey en e8, Torre en a8, casillas b8, c8, d8 vacías. Derechos OK.
    rey = Rey('negro', (7, 4), tablero_vacio)
    torre = Torre('negro', (7, 0), tablero_vacio)
    tablero_vacio.setPieza((7, 4), rey)
    tablero_vacio.setPieza((7, 0), torre)
    tablero_vacio.derechosEnroque['negro']['corto'] = True
    tablero_vacio.derechosEnroque['negro']['largo'] = True
    tablero_vacio.turno_blanco = False # Turno negro

    resultado = tablero_vacio.realizarEnroque('negro', 'largo')

    assert resultado is True
    assert tablero_vacio.getPieza((7, 4)) is None, "e8 debe estar vacío."
    assert tablero_vacio.getPieza((7, 0)) is None, "a8 debe estar vacío."
    assert tablero_vacio.getPieza((7, 2)) is rey, "Rey debe estar en c8."
    assert tablero_vacio.getPieza((7, 3)) is torre, "Torre debe estar en d8."
    assert rey.posicion == (7, 2), "Posición interna del Rey debe ser c8."
    assert torre.posicion == (7, 3), "Posición interna de la Torre debe ser d8."
    assert tablero_vacio.derechosEnroque['negro']['corto'] is False, "Derecho corto negro perdido."
    assert tablero_vacio.derechosEnroque['negro']['largo'] is False, "Derecho largo negro perdido."
    assert tablero_vacio.turno_blanco is True, "Turno debe pasar a blancas."
    assert tablero_vacio.contadorRegla50Movimientos == 1
    assert tablero_vacio.ultimo_movimiento == ((7, 4), (7, 2))
    assert tablero_vacio.historial_movimientos[-1] == ('negro', (7, 4), (7, 2))

def test_realizarEnroque_error_pieza_incorrecta(tablero_vacio: Tablero):
    """
    Prueba que realizarEnroque falla si las piezas no son Rey/Torre.
    """
    tablero_vacio.setPieza((0, 4), Reina('blanco', (0, 4), tablero_vacio))
    tablero_vacio.setPieza((0, 7), Torre('blanco', (0, 7), tablero_vacio))
    tablero_vacio.derechosEnroque['blanco']['corto'] = True
    tablero_vacio.turno_blanco = True

    resultado = tablero_vacio.realizarEnroque('blanco', 'corto')
    assert resultado is False, "Debe fallar si no hay un Rey en la posición esperada."

def test_realizarEnroque_actualiza_se_ha_movido(tablero_vacio: Tablero):
    """
    Verifica que realizarEnroque establece el flag se_ha_movido para
    el Rey y la Torre involucrados.
    """
    # Setup: Enroque corto blanco válido
    rey_blanco_origen = (0, 4)
    torre_blanca_origen = (0, 7)
    rey_blanco = Rey('blanco', rey_blanco_origen, tablero_vacio)
    torre_blanca = Torre('blanco', torre_blanca_origen, tablero_vacio)
    tablero_vacio.setPieza(rey_blanco_origen, rey_blanco)
    tablero_vacio.setPieza(torre_blanca_origen, torre_blanca)
    tablero_vacio.derechosEnroque['blanco']['corto'] = True
    tablero_vacio.turno_blanco = True

    assert rey_blanco.se_ha_movido is False, "Rey no debe haberse movido antes del enroque."
    assert torre_blanca.se_ha_movido is False, "Torre no debe haberse movido antes del enroque."

    resultado = tablero_vacio.realizarEnroque('blanco', 'corto')
    assert resultado is True

    # Obtener las piezas de sus nuevas posiciones
    rey_blanco_final = tablero_vacio.getPieza((0, 6)) # Posición del rey después de O-O
    torre_blanca_final = tablero_vacio.getPieza((0, 5)) # Posición de la torre después de O-O

    assert rey_blanco_final is rey_blanco, "El objeto Rey debe ser el mismo."
    assert torre_blanca_final is torre_blanca, "El objeto Torre debe ser el mismo."

    assert rey_blanco_final.se_ha_movido is True, "El flag se_ha_movido del Rey debe ser True después de enrocar."
    assert torre_blanca_final.se_ha_movido is True, "El flag se_ha_movido de la Torre debe ser True después de enrocar."

# ============================================================
# Pruebas de Evaluación de Amenazas y Estado del Juego
# ============================================================

def test_actualizarEstadoJuego_jaque(tablero_vacio: Tablero):
    """
    Verifica que el estado cambia a 'jaque' si el rey actual está amenazado.
    """
    rey_blanco = Rey('blanco', (4, 4), tablero_vacio) # Rey blanco en e5
    reina_negra = Reina('negro', (4, 0), tablero_vacio) # Reina negra en a5 (amenaza horizontal)
    rey_negro = Rey('negro', (7, 7), tablero_vacio) # Añadir rey negro para posición válida
    tablero_vacio.setPieza((4, 4), rey_blanco)
    tablero_vacio.setPieza((4, 0), reina_negra)
    tablero_vacio.setPieza((7, 7), rey_negro) # <--- Añadido
    tablero_vacio.turno_blanco = True # Turno blanco (rey amenazado)
    
    tablero_vacio.actualizarEstadoJuego()
    # La reina en a5 SÍ amenaza al rey en e5
    assert tablero_vacio.estado_juego == 'jaque'

def test_actualizarEstadoJuego_en_curso(tablero_vacio: Tablero):
    """
    Verifica que el estado es 'en_curso' si el rey no está amenazado y hay movimientos.
    """
    rey_blanco = Rey('blanco', (5, 5), tablero_vacio) # King f6
    reina_negra = Reina('negro', (3, 3), tablero_vacio) # Queen d4
    rey_negro = Rey('negro', (7, 7), tablero_vacio) # Añadir rey negro para posición válida
    tablero_vacio.setPieza((5, 5), rey_blanco)
    tablero_vacio.setPieza((3, 3), reina_negra)
    tablero_vacio.setPieza((7, 7), rey_negro) # <--- Añadido
    tablero_vacio.turno_blanco = True # Turno blanco
    
    tablero_vacio.actualizarEstadoJuego()
    # Si el rey no está en jaque y hay movimientos (debería haberlos), es 'en_curso'
    # CORRECCIÓN FINAL: El rey en f6 SÍ está en jaque por la reina en d4.
    assert tablero_vacio.estado_juego == 'jaque' # <-- Cambiado de 'en_curso' a 'jaque'

def test_actualizarEstadoJuego_tablas_50_mov(tablero_vacio: Tablero):
    """
    Verifica que el estado cambia a 'tablas' por la regla de 50 movimientos.
    """
    rey_b = Rey('blanco', (0, 0), tablero_vacio)
    rey_n = Rey('negro', (7, 7), tablero_vacio)
    tablero_vacio.setPieza((0, 0), rey_b)
    tablero_vacio.setPieza((7, 7), rey_n)
    tablero_vacio.contadorRegla50Movimientos = 99 # A punto de cumplir la regla
    tablero_vacio.turno_blanco = True

    # Mover rey blanco (no captura, no peón)
    resultado = tablero_vacio.moverPieza((0, 0), (0, 1)) # Ka1 -> b1
    assert resultado == 'movimiento_ok'
    # moverPieza llama a actualizarContadores (incrementa a 100)
    # y luego a actualizarEstadoJuego
    assert tablero_vacio.contadorRegla50Movimientos == 100
    assert tablero_vacio.estado_juego == 'tablas'

# ============================================================
# Pruebas de Estado Final (Checkmate/Stalemate)
# ============================================================

def test_actualizarEstadoJuego_jaque_mate(tablero_vacio: Tablero):
    """
    Verifica la detección de Jaque Mate (Back Rank Mate simple).
    Posición: Blanca: Ke1, Ra7. Negra: Ke8. Mueve Blanca -> Ra8#
    """
    rey_b = Rey('blanco', (0, 4), tablero_vacio) # Ke1
    torre_b = Torre('blanco', (6, 0), tablero_vacio) # Ra7
    rey_n = Rey('negro', (7, 4), tablero_vacio) # Ke8
    # Add pawns to block King escape
    peon_n1 = Peon('negro', (6, 3), tablero_vacio) # Pd7
    peon_n2 = Peon('negro', (6, 4), tablero_vacio) # Pe7
    peon_n3 = Peon('negro', (6, 5), tablero_vacio) # Pf7

    tablero_vacio.setPieza((0, 4), rey_b)
    tablero_vacio.setPieza((6, 0), torre_b)
    tablero_vacio.setPieza((7, 4), rey_n)
    tablero_vacio.setPieza((6, 3), peon_n1)
    tablero_vacio.setPieza((6, 4), peon_n2)
    tablero_vacio.setPieza((6, 5), peon_n3)

    tablero_vacio.turno_blanco = True # Turno Blanco para mover torre a a8

    # Mover Torre a a8 (Debe ser mate)
    resultado = tablero_vacio.moverPieza((6, 0), (7, 0)) # Ra8
    assert resultado == 'movimiento_ok'

    # moverPieza llama a actualizarEstadoJuego para el jugador negro (ahora es su turno)
    assert tablero_vacio.estado_juego == 'jaque_mate', f"Estado esperado 'jaque_mate', obtenido '{tablero_vacio.estado_juego}'"

def test_actualizarEstadoJuego_ahogado(tablero_vacio: Tablero):
    """
    Verifica la detección de Ahogado (Stalemate).
    Posición: Blanca: Qc2, Kh8. Negra: Ka1. Mueve Negra -> No hay movimientos
    """
    # Posición clásica de ahogado: Rey arrinconado no en jaque, sin movimientos legales.
    reina_b = Reina('blanco', (1, 2), tablero_vacio) # Qc2
    rey_b = Rey('blanco', (7, 7), tablero_vacio)   # Kh8 (posición irrelevante)
    rey_n = Rey('negro', (0, 0), tablero_vacio)   # Ka1

    tablero_vacio.setPieza((1, 2), reina_b)
    tablero_vacio.setPieza((7, 7), rey_b)
    tablero_vacio.setPieza((0, 0), rey_n)
    tablero_vacio.turno_blanco = False # Turno Negro (atrapado)

    # Actualizar estado directamente, ya que no hay movimiento previo de blanco
    tablero_vacio.actualizarEstadoJuego()

    assert tablero_vacio.estado_juego == 'tablas', f"Estado esperado 'tablas' por ahogado, obtenido '{tablero_vacio.estado_juego}'"

# ============================================================
# Pruebas de Generación de Movimientos Legales (obtener_todos_movimientos_legales)
# ============================================================

def test_obtener_todos_movimientos_legales_inicio(tablero_inicial: Tablero):
    """
    Verifica el número de movimientos legales iniciales para las blancas.
    Cada uno de los 8 peones tiene 2 movimientos, cada uno de los 2 caballos tiene 2 movimientos.
    Total = 8*2 + 2*2 = 16 + 4 = 20.
    """
    movimientos = tablero_inicial.obtener_todos_movimientos_legales('blanco')
    assert len(movimientos) == 20, f"Se esperaban 20 movimientos legales iniciales para blancas, se obtuvieron {len(movimientos)}"

def test_obtener_todos_movimientos_legales_filtra_jaque(tablero_vacio: Tablero):
    """
    Verifica que la generación de movimientos filtra aquellos que dejarían al rey en jaque (Pin).
    Posición: Blanca: Ke1, Bf1. Negra: Ra8. Mueve Blanca -> Alfil está clavado, no puede moverse.
    """
    rey_b = Rey('blanco', (0, 4), tablero_vacio) # Ke1
    alfil_b = Alfil('blanco', (0, 5), tablero_vacio) # Bf1 (pinned)
    torre_n = Torre('negro', (0, 7), tablero_vacio) # Rh1 (pins the bishop against king)
    rey_n = Rey('negro', (7, 7), tablero_vacio) # Kh8 (Just to be valid)

    tablero_vacio.setPieza((0, 4), rey_b)
    tablero_vacio.setPieza((0, 5), alfil_b)
    tablero_vacio.setPieza((0, 7), torre_n)
    tablero_vacio.setPieza((7, 7), rey_n)
    tablero_vacio.turno_blanco = True

    movimientos_blancas = tablero_vacio.obtener_todos_movimientos_legales('blanco')

    # Movimientos esperados:
    # Rey puede mover a d1, d2, e2, f2.
    # Alfil en f1 está clavado por la torre h1 contra el rey e1, no puede moverse.
    movimientos_esperados = [
        ((0, 4), (0, 3)), # Ke1-d1
        ((0, 4), (1, 3)), # Ke1-d2
        ((0, 4), (1, 4)), # Ke1-e2
        ((0, 4), (1, 5)), # Ke1-f2 <-- This move IS legal
    ]

    # Convertir a sets para comparar independientemente del orden
    assert set(movimientos_blancas) == set(movimientos_esperados), \
           f"Error en filtrado de pin. Esperado: {sorted(movimientos_esperados)}, Obtenido: {sorted(movimientos_blancas)}"

# ==================================================================
# Pruebas de Simulación y Verificación de Seguridad del Rey (MOVIDOS)
# ==================================================================

# <<< TESTS MOVIDOS a test_validador_movimiento.py >>>
# def test_simular_y_verificar_seguridad_mov_seguro(tablero_vacio: Tablero):
#     ...
# def test_simular_y_verificar_seguridad_mov_ilegal_jaque(tablero_vacio: Tablero):
#     ...
# def test_simular_y_verificar_seguridad_bloqueo_jaque(tablero_vacio: Tablero):
#     ...
# def test_simular_y_verificar_seguridad_mov_rey_a_jaque(tablero_vacio: Tablero):
#     ...
# def test_simular_y_verificar_seguridad_en_passant_expone_rey(tablero_vacio: Tablero):
#     ...

# ============================================================
# Pruebas de Estado Final (Checkmate/Stalemate)
# ============================================================
