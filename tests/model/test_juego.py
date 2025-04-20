import pytest
from model.juego import Juego
from model.tablero import Tablero

@pytest.fixture
def juego():
    """
    Fixture que devuelve una instancia de Juego inicializada.
    """
    return Juego()

def test_getTurnoColor_inicial(juego):
    """
    Verifica que el color del turno inicial es blanco.
    """
    assert juego.getTurnoColor() == 'blanco'

def test_getTurnoColor_despues_de_cambiar_turno(juego):
    """
    Verifica que getTurnoColor refleja correctamente los cambios en el tablero.
    """
    # El turno inicial es blanco
    assert juego.getTurnoColor() == 'blanco'
    
    # Cambiamos manualmente el turno en el tablero
    juego.tablero.turno_blanco = False
    
    # Verificamos que getTurnoColor refleja el cambio
    assert juego.getTurnoColor() == 'negro'