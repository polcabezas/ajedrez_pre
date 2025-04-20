# tests/test_jugador_humano.py
"""
Pruebas unitarias para la clase JugadorHumano.
"""

import pytest
from model.jugadores.jugador_humano import JugadorHumano
from model.jugadores.jugador import Jugador # Importar base para isinstance
from typing import TYPE_CHECKING

# Mockear Juego si es necesario para type hints o llamadas
if TYPE_CHECKING:
    from model.juego import Juego
else:
    # Crear un Mock simple si se necesitara pasar a solicitarMovimiento
    class MockJuego:
        pass
    Juego = MockJuego

# --- Pruebas ---

def test_instanciar_jugador_humano():
    """Verifica que se puede instanciar JugadorHumano correctamente."""
    nombre = "Player 1"
    color = "blanco"
    try:
        jugador = JugadorHumano(nombre, color)
        assert isinstance(jugador, JugadorHumano)
        assert isinstance(jugador, Jugador) # Verificar herencia
        assert jugador.get_nombre() == nombre
        assert jugador.get_color() == color
    except Exception as e:
        pytest.fail(f"No se pudo instanciar JugadorHumano: {e}")

def test_herencia_y_getters():
    """Prueba los getters heredados de la clase base."""
    jugador = JugadorHumano("Player 2", "negro")
    assert jugador.get_nombre() == "Player 2"
    assert jugador.get_color() == "negro"

def test_solicitar_movimiento_raises_notimplemented():
    """
    Verifica que solicitarMovimiento lanza NotImplementedError,
    ya que la entrada real viene de la GUI/Controlador.
    """
    jugador = JugadorHumano("Test", "blanco")
    mock_juego = Juego() # Usar el Mock o un None si la función no lo usa

    with pytest.raises(NotImplementedError, match="La obtención del movimiento humano se gestiona externamente"):
        jugador.solicitarMovimiento(mock_juego)

def test_inicializacion_humano_parametros_invalidos():
    """Prueba la inicialización con parámetros inválidos (a través de super)."""
    # Nombre vacío
    with pytest.raises(ValueError, match="El nombre del jugador no puede estar vacío"):
        JugadorHumano("", "negro")

    # Color inválido
    with pytest.raises(ValueError, match="El color debe ser 'blanco' o 'negro'"):
        JugadorHumano("Garry", "verde")

def test_str_repr_jugador_humano():
    """Prueba las representaciones __str__ y __repr__ heredadas."""
    jugador = JugadorHumano("Magnus", "blanco")
    # __str__ usa el método de la clase base
    assert str(jugador) == "Jugador(Nombre: Magnus, Color: blanco)"
    # __repr__ usa el nombre de la clase actual (JugadorHumano)
    assert repr(jugador) == "JugadorHumano(nombre='Magnus', color='blanco')" 