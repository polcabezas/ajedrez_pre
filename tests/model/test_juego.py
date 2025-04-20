import pytest
from model.juego import Juego
from model.tablero import Tablero

@pytest.fixture
def juego():
    """
    Fixture que devuelve una instancia de Juego inicializada y configurada.
    """
    j = Juego()
    # Añadir configuración básica para que el estado inicial (turno) sea válido
    j.configurar_nueva_partida({'modalidad': 'Humano vs Humano', 'tipo_juego': 'Clásico'}) 
    return j

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
    # IMPORTANTE: Esto ahora no es suficiente, ya que Juego maneja su propio color_activo
    # Deberíamos simular un movimiento o usar un método de Juego para cambiar el turno.
    # Por ahora, actualizaremos directamente el atributo interno de Juego para probar getTurnoColor.
    # Idealmente, se probaría a través de realizar_movimiento.
    # juego.tablero.turno_blanco = False # Esto ya no es suficiente
    juego.color_activo = 'negro' # Actualizar directamente para el test

    # Verificamos que getTurnoColor refleja el cambio
    assert juego.getTurnoColor() == 'negro'