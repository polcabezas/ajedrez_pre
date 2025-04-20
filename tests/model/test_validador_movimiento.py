import pytest
from model.tablero import Tablero
from model.validador_movimiento import ValidadorMovimiento
# Import necessary pieces for test setups
from model.piezas.reina import Reina
from model.piezas.peon import Peon
from model.piezas.torre import Torre
from model.piezas.alfil import Alfil
from model.piezas.rey import Rey
from model.piezas.caballo import Caballo

# Fixture to provide an empty board (can be shared or redefined)
@pytest.fixture
def tablero_vacio():
    """
    Proporciona un tablero vacío sin piezas.
    """
    tablero = Tablero()
    tablero.casillas = [[None for _ in range(8)] for _ in range(8)]
    tablero.derechosEnroque = {
        'blanco': {'corto': False, 'largo': False},
        'negro': {'corto': False, 'largo': False}
    }
    # Reset other states if needed for specific validation tests
    tablero.objetivoPeonAlPaso = None
    tablero.turno_blanco = True
    # ... potentially other resets ...
    return tablero

# Fixture to provide the validator instance based on a board
@pytest.fixture
def validador(tablero_vacio: Tablero):
    """
    Proporciona una instancia de ValidadorMovimiento asociada a un tablero vacío.
    """
    return ValidadorMovimiento(tablero_vacio)

@pytest.mark.parametrize("posicion, esperado", [
    ((0, 0), True),
    ((7, 0), False),
    ((4, 4), False)
])
def test_es_blanco(posicion, esperado):
    # Setup using initial board for parametrize compatibility
    tablero = Tablero()
    validador_inicial = ValidadorMovimiento(tablero)

    assert validador_inicial.esBlanco(posicion) == esperado
    
def test_esCasillaAmenazada_positiva(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """
    Verifica que una casilla es identificada como amenazada por el validador.
    """
    # Colocar una reina negra en d4 (3,3)
    reina_negra = Reina('negro', (3, 3), tablero_vacio)
    tablero_vacio.setPieza((3, 3), reina_negra)

    casillas_amenazadas_esperadas = [
        # Horizontales/Verticales
        (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7),
        (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3),
        # Diagonales
        (0, 0), (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7),
        (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)
    ]
    for casilla in casillas_amenazadas_esperadas:
        assert validador.esCasillaAmenazada(casilla, 'negro') is True, f"Casilla {casilla} debería estar amenazada por la reina negra en d4"

    # Test con un peón
    tablero_vacio.setPieza((3,3), None) # Limpiar reina
    peon_blanco = Peon('blanco', (1, 4), tablero_vacio) # Peón e2
    tablero_vacio.setPieza((1, 4), peon_blanco)
    assert validador.esCasillaAmenazada((2, 3), 'blanco') is True, "Peón blanco en e2 debería amenazar d3"
    assert validador.esCasillaAmenazada((2, 5), 'blanco') is True, "Peón blanco en e2 debería amenazar f3"
    assert validador.esCasillaAmenazada((2, 4), 'blanco') is False, "Peón blanco en e2 NO debería amenazar e3"
    assert validador.esCasillaAmenazada((1, 3), 'blanco') is False, "Peón blanco en e2 NO debería amenazar d2"

def test_esCasillaAmenazada_negativa_color(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """
    Verifica que una casilla no es amenazada por el color incorrecto.
    """
    reina_negra = Reina('negro', (3, 3), tablero_vacio)
    tablero_vacio.setPieza((3, 3), reina_negra)
    assert validador.esCasillaAmenazada((3, 4), 'blanco') is False

def test_esCasillaAmenazada_negativa_no_amenaza(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """
    Verifica que una casilla no es amenazada si ninguna pieza la ataca.
    """
    reina_negra = Reina('negro', (0, 0), tablero_vacio)
    tablero_vacio.setPieza((0, 0), reina_negra)
    assert validador.esCasillaAmenazada((7, 7), 'negro') is True # Reina a1 SI amenaza h8
    assert validador.esCasillaAmenazada((5, 5), 'negro') is True # Reina a1 SI amenaza f6
    assert validador.esCasillaAmenazada((2, 3), 'negro') is False # Reina a1 NO amenaza d3

def test_esCasillaAmenazada_posicion_invalida(validador: ValidadorMovimiento):
    """
    Verifica que una posición inválida nunca está amenazada.
    """
    # No necesita tablero_vacio, solo el validador
    assert validador.esCasillaAmenazada((-1, 0), 'blanco') is False
    assert validador.esCasillaAmenazada((8, 8), 'negro') is False

def test_esCasillaAmenazada_camino_bloqueado(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """
    Verifica que una casilla no está amenazada si el camino está bloqueado.
    """
    # 1. Torre bloqueada
    torre_blanca = Torre('blanco', (0, 0), tablero_vacio)
    bloqueador_negro = Peon('negro', (0, 2), tablero_vacio)
    tablero_vacio.setPieza((0, 0), torre_blanca)
    tablero_vacio.setPieza((0, 2), bloqueador_negro)
    assert validador.esCasillaAmenazada((0, 3), 'blanco') is False, "Torre a1 no debería amenazar d1"
    assert validador.esCasillaAmenazada((0, 1), 'blanco') is True, "Torre a1 sí debería amenazar b1"

    # Limpiar
    tablero_vacio.setPieza((0, 0), None)
    tablero_vacio.setPieza((0, 2), None)

    # 2. Alfil bloqueado
    alfil_negro = Alfil('negro', (7, 2), tablero_vacio)
    bloqueador_blanco = Peon('blanco', (5, 4), tablero_vacio)
    tablero_vacio.setPieza((7, 2), alfil_negro)
    tablero_vacio.setPieza((5, 4), bloqueador_blanco)
    assert validador.esCasillaAmenazada((2, 5), 'negro') is False, "Alfil c8 no debería amenazar f3"
    assert validador.esCasillaAmenazada((6, 3), 'negro') is True, "Alfil c8 sí debería amenazar d7"

    # Limpiar
    tablero_vacio.setPieza((7, 2), None)
    tablero_vacio.setPieza((5, 4), None)

    # 3. Reina bloqueada (diagonal)
    reina_blanca = Reina('blanco', (3, 3), tablero_vacio)
    bloqueador_blanco = Torre('blanco', (5, 5), tablero_vacio)
    tablero_vacio.setPieza((3, 3), reina_blanca)
    tablero_vacio.setPieza((5, 5), bloqueador_blanco)
    assert validador.esCasillaAmenazada((6, 6), 'blanco') is False, "Reina d4 no debería amenazar g7"
    assert validador.esCasillaAmenazada((4, 4), 'blanco') is True, "Reina d4 sí debería amenazar e5"

# --- Tests for simular_y_verificar_seguridad (Moved) --- 

def test_simular_y_verificar_seguridad_mov_seguro(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """Verifica que un movimiento que no expone al rey es seguro."""
    rey_b = Rey('blanco', (0, 4), tablero_vacio)
    torre_b = Torre('blanco', (0, 0), tablero_vacio)
    rey_n = Rey('negro', (7, 7), tablero_vacio) # Add opponent king
    tablero_vacio.setPieza((0, 4), rey_b)
    tablero_vacio.setPieza((0, 0), torre_b)
    tablero_vacio.setPieza((7, 7), rey_n)
    # Capture original state *string* for comparison after restoration
    # Note: Need the gestor to get the FEN string
    estado_original_str = tablero_vacio.gestor_historico.obtenerPosicionActual()

    # Mover la torre a1->a2 (seguro)
    # Call the method on the validator instance
    es_seguro = validador.simular_y_verificar_seguridad(torre_b, (1, 0))
    assert es_seguro is True, "Mover torre a2 debería ser seguro."
    # Verificar que el tablero se restauró
    assert tablero_vacio.gestor_historico.obtenerPosicionActual() == estado_original_str, "El tablero no se restauró tras simulación segura."
    assert tablero_vacio.getPieza((0, 0)) is torre_b
    assert tablero_vacio.getPieza((1, 0)) is None

def test_simular_y_verificar_seguridad_mov_ilegal_jaque(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """Verifica que un movimiento que deja al rey en jaque es inseguro."""
    rey_b = Rey('blanco', (0, 4), tablero_vacio) # Ke1
    alfil_b = Alfil('blanco', (1, 4), tablero_vacio) # Be2 (clavado)
    reina_n = Reina('negro', (3, 4), tablero_vacio) # Qe4 (ataca alfil y rey)
    rey_n = Rey('negro', (7, 7), tablero_vacio) # Add opponent king
    tablero_vacio.setPieza((0, 4), rey_b)
    tablero_vacio.setPieza((1, 4), alfil_b)
    tablero_vacio.setPieza((3, 4), reina_n)
    tablero_vacio.setPieza((7, 7), rey_n)
    estado_original_str = tablero_vacio.gestor_historico.obtenerPosicionActual()

    # Mover el alfil clavado (ilegal)
    es_seguro = validador.simular_y_verificar_seguridad(alfil_b, (2, 3)) # Be2->d3?
    assert es_seguro is False, "Mover alfil clavado debería ser inseguro."
    # Verificar que el tablero se restauró
    assert tablero_vacio.gestor_historico.obtenerPosicionActual() == estado_original_str, "El tablero no se restauró tras simulación ilegal (jaque)."
    assert tablero_vacio.getPieza((1, 4)) is alfil_b
    assert tablero_vacio.getPieza((2, 3)) is None

def test_simular_y_verificar_seguridad_bloqueo_jaque(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """Verifica que un movimiento que bloquea un jaque es seguro."""
    rey_b = Rey('blanco', (0, 0), tablero_vacio) # Ka1
    alfil_b = Alfil('blanco', (2, 2), tablero_vacio) # Bc3
    torre_n = Torre('negro', (0, 7), tablero_vacio) # Th1 (jaque)
    rey_n = Rey('negro', (7, 7), tablero_vacio) # Add opponent king
    tablero_vacio.setPieza((0, 0), rey_b)
    tablero_vacio.setPieza((2, 2), alfil_b)
    tablero_vacio.setPieza((0, 7), torre_n)
    tablero_vacio.setPieza((7, 7), rey_n)
    tablero_vacio.turno_blanco = True # Turno blanco (en jaque)
    estado_original_str = tablero_vacio.gestor_historico.obtenerPosicionActual()

    # Mover el alfil para bloquear (c3->c1)
    es_seguro = validador.simular_y_verificar_seguridad(alfil_b, (0, 2))
    assert es_seguro is True, "Bloquear jaque con alfil debería ser seguro."
    # Verificar restauración
    assert tablero_vacio.gestor_historico.obtenerPosicionActual() == estado_original_str, "El tablero no se restauró tras simulación de bloqueo."

def test_simular_y_verificar_seguridad_mov_rey_a_jaque(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """Verifica que mover el rey a una casilla atacada es inseguro."""
    rey_b = Rey('blanco', (0, 0), tablero_vacio) # Ka1
    torre_n = Torre('negro', (0, 7), tablero_vacio) # Th1 (ataca b1)
    rey_n = Rey('negro', (7, 7), tablero_vacio) # Add opponent king
    tablero_vacio.setPieza((0, 0), rey_b)
    tablero_vacio.setPieza((0, 7), torre_n)
    tablero_vacio.setPieza((7, 7), rey_n)
    estado_original_str = tablero_vacio.gestor_historico.obtenerPosicionActual()

    # Mover rey a casilla atacada (a1->b1)
    es_seguro = validador.simular_y_verificar_seguridad(rey_b, (0, 1))
    assert es_seguro is False, "Mover rey a casilla atacada (b1) debería ser inseguro."
    # Verificar restauración
    assert tablero_vacio.gestor_historico.obtenerPosicionActual() == estado_original_str, "El tablero no se restauró tras simulación de rey a jaque."

def test_simular_y_verificar_seguridad_en_passant_expone_rey(tablero_vacio: Tablero, validador: ValidadorMovimiento):
    """Verifica si una captura al paso que expondría al rey es insegura."""
    rey_b = Rey('blanco', (0, 4), tablero_vacio) # Ke1
    peon_b = Peon('blanco', (4, 4), tablero_vacio) # Pe5
    peon_n = Peon('negro', (6, 3), tablero_vacio) # Pd7
    torre_n = Torre('negro', (7, 4), tablero_vacio) # Te8
    rey_n = Rey('negro', (7, 0), tablero_vacio) # Ka8
    tablero_vacio.setPieza((0, 4), rey_b)
    tablero_vacio.setPieza((4, 4), peon_b)
    tablero_vacio.setPieza((6, 3), peon_n)
    tablero_vacio.setPieza((7, 4), torre_n)
    tablero_vacio.setPieza((7, 0), rey_n)
    tablero_vacio.turno_blanco = False # Turno Negro

    # Negro mueve d7->d5
    tablero_vacio.moverPieza((6, 3), (4, 3))
    assert tablero_vacio.objetivoPeonAlPaso == (5, 3) # Objetivo d6
    assert tablero_vacio.turno_blanco is True # Turno Blanco
    estado_original_str = tablero_vacio.gestor_historico.obtenerPosicionActual()
    peon_b_a_mover = tablero_vacio.getPieza((4,4))
    assert isinstance(peon_b_a_mover, Peon)

    # Simular captura al paso e5xd6
    es_seguro = validador.simular_y_verificar_seguridad(peon_b_a_mover, (5, 3))
    assert es_seguro is False, "Captura al paso exd6 que expone rey debería ser insegura."
    # Verificar restauración
    assert tablero_vacio.gestor_historico.obtenerPosicionActual() == estado_original_str, "El tablero no se restauró tras simulación de e.p. ilegal."
    assert tablero_vacio.getPieza((4,4)) is peon_b_a_mover, "Peón blanco no restaurado en e5"
    assert isinstance(tablero_vacio.getPieza((4,3)), Peon), "Peón negro no restaurado en d5"
    assert tablero_vacio.getPieza((5,3)) is None, "Casilla d6 no restaurada a vacía"
    assert tablero_vacio.objetivoPeonAlPaso == (5,3), "Objetivo al paso no restaurado"
