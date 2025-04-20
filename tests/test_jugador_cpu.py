"""
Pruebas unitarias para la clase JugadorCPU.
"""

import pytest
import random
from unittest.mock import MagicMock, patch # Para simular el tablero y random
from typing import TYPE_CHECKING, List, Tuple # Importar List y Tuple

from model.jugadores.jugador_cpu import JugadorCPU
from model.jugadores.jugador import Jugador, MoveInfo # Importar base y tipo

# --- Mocks ---

# Mockear Tablero con el método necesario
class MockTablero:
    def obtener_todos_movimientos_legales(self, color):
        # Este método será sobreescrito por MagicMock en las pruebas
        pass

# Mockear Juego con el atributo tablero
class MockJuego:
    def __init__(self):
        self.tablero = MockTablero()

# --- Pruebas ---

def test_instanciar_jugador_cpu():
    """Verifica la instanciación correcta de JugadorCPU."""
    nombre = "CPU Easy"
    color = "negro"
    nivel = 1
    try:
        jugador = JugadorCPU(nombre, color, nivel)
        assert isinstance(jugador, JugadorCPU)
        assert isinstance(jugador, Jugador)
        assert jugador.get_nombre() == nombre
        assert jugador.get_color() == color
        assert jugador.get_nivel() == nivel
    except Exception as e:
        pytest.fail(f"No se pudo instanciar JugadorCPU: {e}")

def test_cpu_get_nivel():
    """Prueba el getter específico de nivel."""
    jugador = JugadorCPU("CPU Hard", "blanco", 3)
    assert jugador.get_nivel() == 3

@patch('model.jugadores.jugador_cpu.random.choice') # Mockear random.choice
def test_solicitar_movimiento_cpu_elige_aleatorio(mock_random_choice):
    """
    Verifica que la CPU solicita movimientos legales y elige uno al azar.
    """
    jugador = JugadorCPU("Test CPU", "blanco")
    mock_juego = MockJuego()

    # Definir los movimientos legales que el mock tablero devolverá
    movimientos_posibles: List[MoveInfo] = [((0,0),(1,0)), ((0,1),(2,2)), ((6,5),(5,5))]
    mock_juego.tablero.obtener_todos_movimientos_legales = MagicMock(return_value=movimientos_posibles)

    # Configurar el mock de random.choice para que devuelva un valor predecible
    movimiento_esperado = movimientos_posibles[1] # ((0,1),(2,2))
    mock_random_choice.return_value = movimiento_esperado

    # Llamar al método
    movimiento_devuelto = jugador.solicitarMovimiento(mock_juego)

    # Verificaciones
    mock_juego.tablero.obtener_todos_movimientos_legales.assert_called_once_with("blanco")
    mock_random_choice.assert_called_once_with(movimientos_posibles)
    assert movimiento_devuelto == movimiento_esperado

def test_solicitar_movimiento_cpu_sin_movimientos_legales():
    """
    Verifica el comportamiento cuando no hay movimientos legales.
    """
    jugador = JugadorCPU("Test CPU", "negro")
    mock_juego = MockJuego()

    # Configurar el mock para devolver lista vacía
    movimientos_vacios: List[MoveInfo] = []
    mock_juego.tablero.obtener_todos_movimientos_legales = MagicMock(return_value=movimientos_vacios)

    # Llamar al método
    movimiento_devuelto = jugador.solicitarMovimiento(mock_juego)

    # Verificar que se llamó al método del tablero
    mock_juego.tablero.obtener_todos_movimientos_legales.assert_called_once_with("negro")
    # Verificar que devuelve el valor especial indicando "sin movimiento"
    assert movimiento_devuelto == ((-1,-1), (-1,-1))

@patch('model.jugadores.jugador_cpu.logger') # Parchear la instancia logger específica
def test_solicitar_movimiento_cpu_sin_movimientos_log(mock_logger): # El argumento ahora es el logger mockeado
    """Verifica que se registra un warning si no hay movimientos."""
    jugador = JugadorCPU("Test CPU", "negro")
    mock_juego = MockJuego()
    mock_juego.tablero.obtener_todos_movimientos_legales = MagicMock(return_value=[])

    jugador.solicitarMovimiento(mock_juego)

    # Verificar que se llamó a logger.warning directamente en la instancia mockeada
    mock_logger.warning.assert_called_once()
    # Verificar parte del mensaje de warning (opcional pero útil)
    args, _ = mock_logger.warning.call_args
    assert "no tiene movimientos legales disponibles" in args[0]

def test_solicitar_movimiento_juego_sin_tablero():
    """Verifica que lanza AttributeError si el juego no tiene tablero."""
    jugador = JugadorCPU("Test CPU", "blanco")
    mock_juego_roto = MagicMock() # Un mock que no tiene 'tablero'
    # Asegurarse de que el atributo no existe en el mock para la prueba
    try:
        del mock_juego_roto.tablero
    except AttributeError:
        pass # Ya no existía, está bien

    with pytest.raises(AttributeError, match="no tiene un tablero válido"):
        jugador.solicitarMovimiento(mock_juego_roto)

def test_str_repr_jugador_cpu():
    """Prueba las representaciones __str__ y __repr__."""
    jugador = JugadorCPU("Stockfish", "negro", 8)
    assert str(jugador) == "Jugador(Nombre: Stockfish, Color: negro)"
    assert repr(jugador) == "JugadorCPU(nombre='Stockfish', color='negro')" # No incluye nivel en repr base 