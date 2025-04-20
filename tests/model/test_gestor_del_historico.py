import pytest
import logging
from collections import defaultdict
from model.tablero import Tablero
from model.gestor_del_historico import GestorDelHistorico
from model.piezas.rey import Rey
from model.piezas.peon import Peon # Needed for test_obtenerPosicionActual_post_movimiento

# Fixtures (similar to test_tablero, adjust if necessary)
@pytest.fixture
def tablero_inicial():
    return Tablero()

@pytest.fixture
def tablero_vacio():
    tablero = Tablero()
    tablero.casillas = [[None for _ in range(8)] for _ in range(8)]
    tablero.derechosEnroque = {
        'blanco': {'corto': False, 'largo': False},
        'negro': {'corto': False, 'largo': False}
    }
    tablero.objetivoPeonAlPaso = None
    tablero.turno_blanco = True
    # Need to create the gestor here too, but it will be empty
    tablero.gestor_historico = GestorDelHistorico(tablero)
    tablero.gestor_historico.historial_posiciones.clear()
    return tablero

@pytest.fixture
def gestor_inicial(tablero_inicial: Tablero):
    """Provides a history manager linked to an initial board state."""
    # Tablero.__init__ already creates and registers the initial state
    return tablero_inicial.gestor_historico

@pytest.fixture
def gestor_vacio(tablero_vacio: Tablero):
    """Provides a history manager linked to an empty board."""
    # The tablero_vacio fixture already created the gestor
    return tablero_vacio.gestor_historico

# --- Tests for obtenerPosicionActual --- 

def test_obtenerPosicionActual_inicial(gestor_inicial: GestorDelHistorico):
    """
    Verifica la representación FEN estándar de la posición inicial vía Gestor.
    """
    piezas_esperadas = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    turno_esperado = "w"
    enroque_esperado = "KQkq"
    alpaso_esperado = "-"
    esperado_fen_parcial = f"{piezas_esperadas} {turno_esperado} {enroque_esperado} {alpaso_esperado}"

    assert gestor_inicial.obtenerPosicionActual() == esperado_fen_parcial

def test_obtenerPosicionActual_post_movimiento(tablero_inicial: Tablero, gestor_inicial: GestorDelHistorico):
    """
    Verifica la representación FEN estándar tras un movimiento (e4) vía Gestor.
    """
    # Perform the move on the associated tablero
    tablero_inicial.moverPieza((1, 4), (3, 4)) # e4

    piezas_esperadas = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
    turno_esperado = "b" # Turno negro
    enroque_esperado = "KQkq" # No cambia
    alpaso_esperado = "e3" # Objetivo al paso creado

    esperado_fen_parcial = f"{piezas_esperadas} {turno_esperado} {enroque_esperado} {alpaso_esperado}"
    assert gestor_inicial.obtenerPosicionActual() == esperado_fen_parcial

def test_obtenerPosicionActual_sin_enroque(tablero_inicial: Tablero, gestor_inicial: GestorDelHistorico):
    """
    Verifica la representación FEN cuando se pierden derechos de enroque vía Gestor.
    """
    # Modify the associated tablero
    tablero_inicial.derechosEnroque['blanco']['corto'] = False
    tablero_inicial.derechosEnroque['negro']['largo'] = False
    enroque_esperado = "Qk" # Solo quedan Largo Blanco y Corto Negro

    pos_str = gestor_inicial.obtenerPosicionActual()
    partes = pos_str.split(' ')
    assert len(partes) == 4
    assert partes[2] == enroque_esperado

# --- Tests for esTripleRepeticion --- 

def test_esTripleRepeticion_simple(tablero_vacio: Tablero, gestor_vacio: GestorDelHistorico):
    """
    Verifica la detección básica de triple repetición vía Gestor.
    """
    # Setup on the associated tablero
    rey_b = Rey('blanco', (0, 0), tablero_vacio)
    rey_n = Rey('negro', (7, 7), tablero_vacio)
    tablero_vacio.setPieza((0, 0), rey_b)
    tablero_vacio.setPieza((7, 7), rey_n)
    tablero_vacio.turno_blanco = True
    
    # Clear history in the gestor and register initial state
    gestor_vacio.historial_posiciones.clear()
    gestor_vacio.registrar_posicion() # Initial S0, Count = 1

    # Perform moves on the tablero, the gestor's registrar_posicion will be called inside
    # Mov 1: Kb1 (W) -> Turn B
    tablero_vacio.moverPieza((0, 0), (0, 1)) # S1, Count = 1
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 2: Kh7 (B) -> Turn W
    tablero_vacio.moverPieza((7, 7), (7, 6)) # S2, Count = 1
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 3: Ka1 (W) -> Turn B
    tablero_vacio.moverPieza((0, 1), (0, 0)) # S3, Count = 1
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 4: Kh8 (B) -> Turn W
    tablero_vacio.moverPieza((7, 6), (7, 7)) # S0, Count = 2 
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 5: Kb1 (W) -> Turn B
    tablero_vacio.moverPieza((0, 0), (0, 1)) # S1, Count = 2
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 6: Kh7 (B) -> Turn W
    tablero_vacio.moverPieza((7, 7), (7, 6)) # S2, Count = 2
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 7: Ka1 (W) -> Turn B
    tablero_vacio.moverPieza((0, 1), (0, 0)) # S3, Count = 2
    assert not gestor_vacio.esTripleRepeticion()
    # Mov 8: Kh8 (B) -> Turn W
    tablero_vacio.moverPieza((7, 6), (7, 7)) # S0, Count = 3

    # Check repetition using the gestor method
    assert gestor_vacio.esTripleRepeticion() is True

# Add more tests if needed, e.g., repetition with castling rights changes 