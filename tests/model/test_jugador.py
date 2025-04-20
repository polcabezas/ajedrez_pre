# tests/test_jugador.py
"""
Pruebas unitarias para la clase base abstracta Jugador.
"""

import pytest
from model.jugadores.jugador import Jugador, MoveInfo
from abc import ABC
from typing import TYPE_CHECKING

# Evitar importación circular para type hints
if TYPE_CHECKING:
    from model.juego import Juego

# Crear una subclase concreta mínima SOLO para propósitos de prueba
class JugadorConcreto(Jugador):
    """Implementación concreta mínima de Jugador para pruebas."""
    def solicitarMovimiento(self, juego: 'Juego') -> MoveInfo:
        # Implementación mínima, no se probará su lógica aquí
        print(f"{self.get_nombre()} simulando solicitud de movimiento.")
        return ((0,0), (1,1)) # Devuelve un movimiento dummy

# --- Pruebas ---

def test_jugador_es_abstracta():
    """Verifica que la clase Jugador no se puede instanciar directamente."""
    assert issubclass(Jugador, ABC), "Jugador debería ser una subclase de ABC"
    with pytest.raises(TypeError, match="Can\'t instantiate abstract class Jugador"):
        Jugador("Test Abstracto", "blanco")

def test_instanciar_subclase_concreta():
    """Verifica que una subclase concreta SÍ se puede instanciar."""
    try:
        jugador = JugadorConcreto("Jugador Test", "negro")
        assert isinstance(jugador, JugadorConcreto)
        assert isinstance(jugador, Jugador)
    except Exception as e:
        pytest.fail(f"No se pudo instanciar JugadorConcreto: {e}")

def test_getters_jugador():
    """Prueba los métodos get_nombre() y get_color()."""
    nombre_test = "Alice"
    color_test = "blanco"
    jugador = JugadorConcreto(nombre_test, color_test)
    assert jugador.get_nombre() == nombre_test
    assert jugador.get_color() == color_test

def test_inicializacion_parametros_invalidos():
    """Prueba la inicialización con parámetros inválidos."""
    # Nombre vacío
    with pytest.raises(ValueError, match="El nombre del jugador no puede estar vacío"):
        JugadorConcreto("", "blanco")

    # Color inválido
    with pytest.raises(ValueError, match="El color debe ser 'blanco' o 'negro'"):
        JugadorConcreto("Bob", "azul")

    # Color con mayúsculas (debería fallar según la definición actual)
    with pytest.raises(ValueError, match="El color debe ser 'blanco' o 'negro'"):
        JugadorConcreto("Charlie", "Blanco")

def test_str_repr_jugador():
    """Prueba las representaciones __str__ y __repr__."""
    jugador = JugadorConcreto("Deep Blue", "negro")
    assert str(jugador) == "Jugador(Nombre: Deep Blue, Color: negro)"
    assert repr(jugador) == "JugadorConcreto(nombre='Deep Blue', color='negro')"

# Nota: No podemos probar directamente llamar a solicitarMovimiento en Jugador
# porque es abstracto. Las pruebas de esta lógica se harán en las subclases. 